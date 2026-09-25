import io
import os
import re
import time
import uuid
import traceback
from PIL import Image, ImageOps

import config
from agents.preprocessor import PreprocessingAgent
from agents.diagnosis import DiagnosisAgent
from agents.explainability import ExplainabilityAgent
from agents.rag_agent import RAGAgent
from agents.synthesizer import SynthesizerAgent
from agents.validator import ValidatorAgent
from agents.learner import LearnerAgent


class PipelineOrchestrator:
    """Chains all 6 modules into a sequential pipeline."""

    LABEL_TO_PREDICTION = {
        "NORMAL": "Normal",
        "BACTERIAL": "Bacterial Pneumonia",
        "VIRAL": "Viral Pneumonia",
    }

    def __init__(self):
        print("[Pipeline] Initializing agents...")
        self.preprocessor = PreprocessingAgent(config.MODEL_INPUT_SIZE)
        self.diagnosis = DiagnosisAgent()
        self.explainability = ExplainabilityAgent(diagnosis_model=self.diagnosis)
        self.rag = RAGAgent()
        self.synthesizer = SynthesizerAgent()
        self.validator = ValidatorAgent()
        self.learner = LearnerAgent()
        print("[Pipeline] All agents initialized")

    def run(self, image_bytes: bytes) -> dict:
        start_time = time.time()

        try:
            original_image = Image.open(io.BytesIO(image_bytes))
            original_image = ImageOps.exif_transpose(original_image)
            original_image = original_image.convert("RGB")
        except Exception as e:
            return {"error": f"Failed to open image: {e}"}

        case_id = f"PX-{uuid.uuid4().hex[:5].upper()}"

        # Module 1: Preprocessing (ImageNet normalization — matches training)
        t0 = time.time()
        try:
            print("[Pipeline] Module 1: Preprocessing...")
            preprocessed = self.preprocessor.run(original_image)
        except Exception as e:
            print(f"[Pipeline] Module 1 failed: {e}")
            traceback.print_exc()
            return {"error": f"Preprocessing failed: {e}"}
        print(f"[Pipeline] Module 1 done in {time.time()-t0:.1f}s")

        # Module 2: 3-class classification (Normal / Bacterial / Viral)
        t0 = time.time()
        try:
            print("[Pipeline] Module 2: 3-class classification...")
            diagnosis_result = self.diagnosis.run(preprocessed)
            print(f"[Pipeline] Prediction: {diagnosis_result['label']} ({diagnosis_result['confidence_score']:.1%})")
        except Exception as e:
            print(f"[Pipeline] Module 2 failed: {e}")
            traceback.print_exc()
            diagnosis_result = {
                "label": "Unknown",
                "confidence_score": 0.0,
                "model_version": "error",
                "logits": [0.0, 0.0, 0.0],
                "probabilities": {},
            }
        print(f"[Pipeline] Module 2 done in {time.time()-t0:.1f}s")

        # Module 3: Explainability (SHAP Attribution only — Grad-CAM removed)
        t0 = time.time()
        try:
            print("[Pipeline] Module 3: Explainability...")
            predicted_class_idx = config.MODEL_CLASSES.index(diagnosis_result["label"]) if diagnosis_result["label"] in config.MODEL_CLASSES else 0
            explainability_result = self.explainability.run_fast(
                original_image,
                case_id=case_id,
                predicted_class=predicted_class_idx,
            )
            case_id = explainability_result.get("case_id", case_id)
        except Exception as e:
            print(f"[Pipeline] Module 3 failed: {e}")
            traceback.print_exc()
            explainability_result = {
                "case_id": case_id,
                "grad_cam_url": None,
                "shap_url": None,
            }
        print(f"[Pipeline] Module 3 done in {time.time()-t0:.1f}s")

        # Module 4: Reasoning & Validation
        rag_context: list[dict] = [{"text": "No clinical guidelines available.", "source": "N/A", "page": 0}]
        t0 = time.time()
        try:
            print("[Pipeline] Module 4: Reasoning & Validation...")
            t_rag = time.time()
            try:
                rag_context = self.rag.run(
                    f"{diagnosis_result['label']} chest X-ray findings"
                )
            except Exception as e:
                print(f"[Pipeline] RAG failed (continuing without): {e}")
            print(f"[Pipeline] RAG done in {time.time()-t_rag:.1f}s")

            # Extract plain text for synthesizer and validator
            rag_texts = [item["text"] if isinstance(item, dict) else item for item in rag_context]

            t_llm = time.time()
            llm_result = {}
            try:
                llm_result = self.synthesizer.run(diagnosis_result, explainability_result, rag_texts)
            except Exception as e:
                print(f"[Pipeline] LLM synthesis failed: {e}")
                llm_result = self.synthesizer.fallback_synthesis(diagnosis_result, explainability_result)
            print(f"[Pipeline] LLM done in {time.time()-t_llm:.1f}s")

            full_result = self._merge_results(
                diagnosis_result, explainability_result, llm_result
            )
            full_result = self.validator.run(full_result, rag_texts)

        except Exception as e:
            print(f"[Pipeline] Module 4 failed: {e}")
            traceback.print_exc()
            full_result = self._fallback_result(diagnosis_result, explainability_result, case_id)

        # Finalize
        elapsed = time.time() - start_time
        full_result["case_id"] = case_id
        full_result["processing_time"] = round(elapsed, 2)
        full_result["image_quality"] = self._assess_quality(original_image)
        full_result["confidence"] = int(diagnosis_result["confidence_score"] * 100)
        if full_result.get("overall_status") not in ("Normal", "Abnormal", "Requires Attention"):
            full_result["overall_status"] = "Normal" if diagnosis_result["label"] == "NORMAL" else "Requires Attention"

        frontend_result = self._map_to_frontend(full_result, rag_context)

        # Module 6: Learning loop (async)
        try:
            print("[Pipeline] Module 6: Logging case...")
            self.learner.log_async(full_result)
        except Exception as e:
            print(f"[Pipeline] Learner failed (non-critical): {e}")

        print(f"[Pipeline] Complete in {elapsed:.2f}s | Status: {full_result.get('pipeline_status')}")
        return frontend_result

    def _fallback_result(self, diagnosis: dict, explainability: dict, case_id: str) -> dict:
        label = diagnosis.get("label", "Unknown")
        conf = diagnosis.get("confidence_score", 0.0)
        conf_pct = int(conf * 100)
        is_normal = label == "NORMAL"
        return {
            "overall_status": "Normal" if is_normal else "Requires Attention",
            "confidence": conf_pct,
            "findings": [{
                "name": f"Model Prediction: {label}",
                "region": "Lungs",
                "severity": "Normal" if is_normal else "Moderate",
                "confidence": conf_pct,
                "description": f"CNN model predicted {label} with {conf:.1%} confidence.",
            }],
            "recommendations": ["Consult with a qualified radiologist"],
            "summary": f"Analysis: {label} predicted with {conf:.1%} confidence.",
            "diagnosis": diagnosis,
            "explainability": explainability,
            "pipeline_status": "FALLBACK",
        }

    def _merge_results(self, diagnosis: dict, explainability: dict, llm_result: dict) -> dict:
        merged = dict(llm_result)
        merged["diagnosis"] = diagnosis
        merged["explainability"] = explainability
        return merged

    def _assess_quality(self, image: Image.Image) -> str:
        w, h = image.size
        if w < 200 or h < 200:
            return "Poor"
        if w < 500 or h < 500:
            return "Fair"
        return "Good"

    def _map_to_frontend(self, full_result: dict, rag_context: list[dict] | None = None) -> dict:
        diagnosis = full_result.get("diagnosis", {})
        label = diagnosis.get("label", "Unknown")
        probs = diagnosis.get("probabilities", {})
        validation = full_result.get("validation", {})
        explainability = full_result.get("explainability", {})
        pipeline_status = full_result.get("pipeline_status", "UNKNOWN")
        is_validated = pipeline_status == "APPROVED" and validation.get("overall_pass") is True

        frontend = {
            "case_id": full_result.get("case_id", ""),
            "prediction": self.LABEL_TO_PREDICTION.get(label, label.title()),
            "probabilities": {
                "normal": round(probs.get("NORMAL", 0.0), 4),
                "bacterial": round(probs.get("BACTERIAL", 0.0), 4),
                "viral": round(probs.get("VIRAL", 0.0), 4),
            },
            "confidence": full_result.get("confidence", 0),
            "isValidated": is_validated,
            "status": pipeline_status,
            "overallStatus": full_result.get("overall_status", "Requires Attention"),
            "imageQuality": full_result.get("image_quality", "Good"),
            "processingTime": full_result.get("processing_time", 0),
            "summary": full_result.get("summary", ""),
            "recommendations": full_result.get("recommendations", []),
            "report": {
                "text": full_result.get("summary", ""),
                "sources": self._build_sources(rag_context or []),
            },
            "regions": [
                {
                    "name": f.get("name", "Finding"),
                    "severity": f.get("severity", "Moderate"),
                    "description": f.get("description", ""),
                }
                for f in full_result.get("findings", [])
            ],
            "shapAnalysis": explainability.get("shap_analysis", []),
            "gradcamUrl": explainability.get("grad_cam_url"),
            "shapUrl": explainability.get("shap_url"),
        }
        return frontend

    def _build_sources(self, rag_context: list[dict]) -> list[dict]:
        sources = []
        for item in rag_context[:4]:
            if isinstance(item, str):
                text = item.strip()
                source_name = "PubMed"
            elif isinstance(item, dict):
                text = (item.get("text") or "").strip()
                raw_source = item.get("source", "pubmed")
                source_name = self._format_source_name(raw_source)
            else:
                continue
            if not text:
                continue
            # year: try text, then fallback to source filename (e.g., koo-et-al-2020-..., ATS_IDSA_2019)
            year_match = re.search(r"\b(19|20)\d{2}\b", text)
            if not year_match and isinstance(item, dict):
                raw_src = item.get("source", "")
                year_match = re.search(r"\b(19|20)\d{2}\b", raw_src)
            # also include page for PDF chunks
            page = item.get("page", 0) if isinstance(item, dict) else 0
            journal_display = source_name
            if page and page != 0 and source_name != "PubMed":
                journal_display = f"{source_name} · p. {page}"
            sources.append({
                "title": text[:110] + ("..." if len(text) > 110 else ""),
                "text": text,
                "journal": journal_display,
                "year": year_match.group(0) if year_match else "N/A",
            })
        return sources

    @staticmethod
    def _format_source_name(raw: str) -> str:
        """Convert a source filename/path into a human-readable label."""
        if not raw or raw in ("pubmed", "N/A", "unknown"):
            return "PubMed"
        basename = os.path.basename(raw)
        name = os.path.splitext(basename)[0]
        name = name.replace("_", " ").replace("-", " ")
        name = re.sub(r"\s+", " ", name).strip()
        if len(name) > 60:
            name = name[:60].rsplit(" ", 1)[0]
        return name or "PubMed"
