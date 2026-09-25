import config
from chat_via_openrouter import OpenRouterError, run_via_openrouter


class SynthesizerAgent:
    SYSTEM_PROMPT = """You are an expert radiologist AI assistant specializing in chest X-ray interpretation.
You receive diagnostic data from a pneumonia detection model, explainability status, and relevant clinical guidelines.

Return only the primary finding detected by the model. Do not add differential diagnoses, alternative conditions, or speculative findings.

Return JSON with this exact structure:
{
  "overall_status": "Normal, Abnormal, or Requires Attention",
  "confidence": 0,
  "findings": [
    {
      "name": "Primary finding name",
      "region": "Anatomical region",
      "severity": "Normal, Mild, Moderate, or Severe",
      "confidence": 0,
      "description": "Description of the primary finding only"
    }
  ],
  "recommendations": ["General recommendation"],
  "summary": "Concise clinical summary"
}"""

    def __init__(self):
        self.model = config.OPENROUTER_MODEL
        self.provider = config.LLM_PROVIDER

    def _expected_status(self, label):
        if label == "NORMAL":
            return "Normal"
        if label in {"BACTERIAL", "VIRAL"}:
            return "Abnormal"
        return "Requires Attention"

    def _apply_diagnosis_constraints(self, report, diagnosis):
        label = diagnosis.get("label")
        expected_status = self._expected_status(label)
        finding = report["findings"][0]
        finding_name = finding["name"].strip().lower()
        if report["overall_status"] != expected_status:
            raise ValueError("overall status does not match diagnosis")
        if label == "NORMAL":
            matches = "normal" in finding_name and not any(
                term in finding_name for term in ("bacterial", "viral")
            )
        elif label in {"BACTERIAL", "VIRAL"}:
            other_label = "viral" if label == "BACTERIAL" else "bacterial"
            matches = label.lower() in finding_name and other_label not in finding_name
        else:
            matches = False
        if not matches:
            raise ValueError("primary finding does not match diagnosis")
        model_confidence = float(diagnosis.get("confidence_score", 0.0))
        model_confidence = min(max(model_confidence, 0.0), 1.0)
        report["confidence"] = model_confidence
        finding["confidence"] = model_confidence
        return report

    def run(self, diagnosis, explainability, rag_context):
        if diagnosis.get("label") not in {"NORMAL", "BACTERIAL", "VIRAL"}:
            return self.fallback_synthesis(diagnosis, explainability)
        prompt = self._build_prompt(diagnosis, explainability, rag_context)
        try:
            report = run_via_openrouter(
                system_prompt=self.SYSTEM_PROMPT,
                user_prompt=prompt,
            )
            report = self._apply_diagnosis_constraints(report, diagnosis)
            report["synthesis_status"] = "openrouter"
            return report
        except (OpenRouterError, ValueError, TypeError, KeyError) as exc:
            print(f"[Synthesizer] OpenRouter synthesis unavailable: {exc}")
            return self.fallback_synthesis(diagnosis, explainability)

    def _build_prompt(self, diagnosis, explainability, rag_context):
        parts = [
            "## Diagnostic Model Output",
            f"- Label: {diagnosis.get('label', 'Unknown')}",
            f"- Confidence: {diagnosis.get('confidence_score', 0):.1%}",
            f"- Model: {diagnosis.get('model_version', 'N/A')}",
            "",
            "## Explainability Data",
        ]
        if explainability.get("shap_url"):
            parts.append("- Pixel-level attribution generated and constrained to the lung mask")
        if rag_context:
            parts.extend(["", "## Relevant Clinical Guidelines"])
            for index, context in enumerate(rag_context[:5], 1):
                truncated = context[:500] + "..." if len(context) > 500 else context
                parts.append(f"{index}. {truncated}")
        parts.extend(
            [
                "",
                "Synthesize one report consistent with the diagnostic model label. Return the required JSON only.",
            ]
        )
        return "\n".join(parts)

    def fallback_synthesis(self, diagnosis, explainability):
        label = diagnosis.get("label", "Unknown")
        confidence = diagnosis.get("confidence_score", 0.0)
        if label in {"BACTERIAL", "VIRAL"}:
            status = "Abnormal"
            severity = "Moderate" if confidence > 0.7 else "Mild"
        elif label == "NORMAL":
            status = "Normal"
            severity = "Normal"
        else:
            status = "Requires Attention"
            severity = "Mild"
        return {
            "synthesis_status": "fallback",
            "overall_status": status,
            "confidence": confidence,
            "findings": [
                {
                    "name": f"Model Prediction: {label}",
                    "region": "Lungs",
                    "severity": severity,
                    "confidence": confidence,
                    "description": (
                        f"The CNN model predicted '{label}' with {confidence:.1%} confidence. "
                        "LLM synthesis was unavailable; this fallback is based only on model output."
                    ),
                }
            ],
            "recommendations": [
                "Consult with a qualified radiologist for clinical interpretation",
                "LLM synthesis service was unavailable; manual review is recommended",
            ],
            "summary": (
                f"Fallback analysis: CNN model predicted {label} with {confidence:.1%} confidence. "
                "The LLM synthesis step was unavailable. Review the model output manually."
            ),
        }
