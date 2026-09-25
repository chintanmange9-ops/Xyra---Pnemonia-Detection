"""Xyra System Report - Comprehensive PDF documentation of the entire CDSS."""

import re
from fpdf import FPDF


def _safe(text: str) -> str:
    replacements = {
        "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-", "\u2026": "...", "\u2022": "-",
        "\u00a0": " ", "\u00b0": " deg", "\u00d7": "x", "\u00f7": "/",
        "\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2015": "-",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"[^\x00-\xff]", "?", text)
    return text


class SystemReport(FPDF):
    def __init__(self):
        super().__init__()
        self._in_toc = False

    def header(self):
        if self._in_toc:
            return
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, "Xyra - Pneumonia CDSS | System Report", 0, 0, "L")
        self.cell(0, 6, f"Page {self.page_no()}", 0, 1, "R")
        self.set_draw_color(200, 200, 200)
        self.line(10, 12, 200, 12)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, "Xyra - Inter-Project Design 2026 | IPD Group 2", 0, 0, "C")

    def title_page(self):
        self.add_page()
        self.ln(50)
        self.set_font("Helvetica", "B", 32)
        self.set_text_color(10, 22, 40)
        self.cell(0, 15, "Xyra", 0, 1, "C")
        self.set_font("Helvetica", "", 16)
        self.set_text_color(60, 60, 60)
        self.cell(0, 10, "Pneumonia Clinical Decision Support System", 0, 1, "C")
        self.ln(5)
        self.set_font("Helvetica", "", 12)
        self.cell(0, 8, "Comprehensive System Report", 0, 1, "C")
        self.ln(20)
        self.set_font("Helvetica", "", 11)
        self.set_text_color(80, 80, 80)
        self.cell(0, 7, "Inter-Project Design (IPD 2026)", 0, 1, "C")
        self.cell(0, 7, "IPD Group 2", 0, 1, "C")
        self.ln(5)
        self.cell(0, 7, "Date: August 2026", 0, 1, "C")
        self.ln(30)
        self.set_draw_color(10, 22, 40)
        self.line(60, self.get_y(), 150, self.get_y())
        self.ln(5)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(120, 120, 120)
        self.multi_cell(0, 5, _safe(
            "This report documents the complete technical architecture, "
            "model implementations, pipeline design, and frontend system "
            "of the Xyra Pneumonia CDSS."
        ))

    def toc_page(self):
        self._in_toc = True
        self.add_page()
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(10, 22, 40)
        self.cell(0, 10, "Table of Contents", 0, 1)
        self.ln(5)
        self._in_toc = False

        sections = [
            ("1.", "System Overview"),
            ("2.", "Model Architecture: EfficientNet-B2"),
            ("3.", "Pipeline Architecture"),
            ("3.1", "Module 1: Preprocessing"),
            ("3.2", "Module 2: Diagnosis"),
            ("3.3", "Module 3: Explainability"),
            ("3.4", "Module 4a: RAG Agent"),
            ("3.5", "Module 4b: LLM Synthesizer"),
            ("3.6", "Module 4c: Validator"),
            ("3.7", "Module 6: Active Learning"),
            ("4.", "RAG Knowledge Base"),
            ("5.", "LLM Integration"),
            ("6.", "Explainability Methods"),
            ("6.1", "Grad-CAM++"),
            ("6.2", "Integrated Gradients"),
            ("6.3", "Regional Importance"),
            ("7.", "Frontend Architecture"),
            ("7.1", "Technology Stack"),
            ("7.2", "Component Hierarchy"),
            ("7.3", "UI Sub-components"),
            ("8.", "Flask API Endpoints"),
            ("9.", "PDF Report Generator"),
            ("10.", "Training Details"),
            ("11.", "Configuration Reference"),
            ("12.", "Dependencies"),
            ("13.", "File Structure"),
        ]
        for num, title in sections:
            is_sub = "." in num and not num.endswith(".")
            self.set_font("Helvetica", "" if is_sub else "B", 11)
            self.set_text_color(40, 40, 40)
            indent = "    " if is_sub else ""
            self.cell(0, 7, _safe(f"{indent}{num}  {title}"), 0, 1)

    def section(self, num, title):
        self.add_page()
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(10, 22, 40)
        self.cell(0, 10, _safe(f"{num}  {title}"), 0, 1)
        self.set_draw_color(10, 22, 40)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def subsection(self, num, title):
        self.ln(3)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(30, 50, 80)
        self.cell(0, 8, _safe(f"{num}  {title}"), 0, 1)
        self.ln(2)

    def body(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5, _safe(text))
        self.ln(2)

    def kv(self, key, value):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(40, 40, 40)
        self.cell(55, 6, _safe(key) + ":")
        self.set_font("Helvetica", "", 10)
        self.cell(0, 6, _safe(value), 0, 1)

    def table_header(self, cols, widths):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(10, 22, 40)
        for i, col in enumerate(cols):
            self.cell(widths[i], 7, _safe(col), 1, 0, "C", True)
        self.ln()

    def table_row(self, cols, widths):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(40, 40, 40)
        max_h = 7
        for i, col in enumerate(cols):
            self.cell(widths[i], max_h, _safe(col), 1, 0, "L")
        self.ln()

    def table_row_wrap(self, cols, widths):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(40, 40, 40)
        x = self.get_x()
        y = self.get_y()
        max_h = 7
        lines = []
        for i, col in enumerate(cols):
            n_lines = max(1, len(col) // (widths[i] // 2))
            lines.append(n_lines)
        max_h = max(lines) * 5 + 2
        max_h = max(max_h, 7)
        if self.get_y() + max_h > 270:
            self.add_page()
            y = self.get_y()
        for i, col in enumerate(cols):
            self.set_xy(x + sum(widths[:i]), y)
            self.multi_cell(widths[i], 5, _safe(col), 1, "L")
        self.set_y(y + max_h)

    def bullet(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        x = self.get_x()
        self.cell(5, 5, "-")
        self.multi_cell(0, 5, _safe(f" {text}"))
        self.ln(1)

    def code_block(self, text):
        self.set_font("Courier", "", 8)
        self.set_text_color(50, 50, 50)
        self.set_fill_color(245, 245, 245)
        self.multi_cell(0, 4, _safe(text), 1, "L", True)
        self.ln(2)


def generate_system_report() -> bytes:
    pdf = SystemReport()
    pdf.set_auto_page_break(auto=True, margin=20)

    # Title + TOC
    pdf.title_page()
    pdf.toc_page()

    # === Section 1: System Overview ===
    pdf.section("1", "System Overview")
    pdf.body(
        "Xyra is a multi-agent AI Clinical Decision Support System (CDSS) for pneumonia "
        "detection from chest X-rays. It combines deep learning classification, explainable "
        "AI, retrieval-augmented generation (RAG), and large language model (LLM) synthesis "
        "to produce transparent, evidence-based diagnostic reports."
    )
    pdf.body(
        "The system follows a modular pipeline architecture with 7 agents orchestrated in "
        "sequence. A chest X-ray image is uploaded, preprocessed, classified into one of three "
        "classes (Normal, Bacterial Pneumonia, Viral Pneumonia), explained via Grad-CAM and "
        "Integrated Gradients, enriched with clinical guidelines from a RAG knowledge base, "
        "and synthesized into a structured clinical report by an LLM."
    )

    pdf.subsection("1.1", "Key Capabilities")
    pdf.bullet("3-class pneumonia classification: Normal, Bacterial, Viral")
    pdf.bullet("Grad-CAM++ heatmap visualization for model attention")
    pdf.bullet("Integrated Gradients pixel-level attribution (labeled SHAP in UI)")
    pdf.bullet("6-zone lung region importance scoring")
    pdf.bullet("RAG-augmented clinical guidelines from 7 medical sources (968 chunks)")
    pdf.bullet("LLM-generated clinical summary, findings, and recommendations")
    pdf.bullet("PDF report download with full analysis details")
    pdf.bullet("Active learning loop with hard case flagging")

    pdf.subsection("1.2", "Architecture at a Glance")
    pdf.body(
        "Frontend: React 19 + Vite 8 (port 5173)\n"
        "Backend: Flask 3.1 (port 5000)\n"
        "Model: EfficientNet-B2 @ 384px (PyTorch 2.12)\n"
        "LLM: OpenRouter Free Model Router\n"
        "Vector DB: FAISS (968 vectors, all-MiniLM-L6-v2 embeddings)\n"
        "Pipeline: 7 agents in sequential orchestration"
    )

    # === Section 2: Model Architecture ===
    pdf.section("2", "Model Architecture: EfficientNet-B2")

    w = [50, 140]
    pdf.table_header(["Attribute", "Value"], w)
    pdf.table_row(["Architecture", "torchvision.models.efficientnet_b2"], w)
    pdf.table_row(["Input Size", "384 x 384 pixels (RGB)"], w)
    pdf.table_row(["Output Classes", "3: NORMAL, BACTERIAL, VIRAL"], w)
    pdf.table_row(["Classifier Head", "Dropout(0.3) + Linear(1408, 3)"], w)
    pdf.table_row(["in_features", "1408"], w)
    pdf.table_row(["Normalization", "ImageNet mean=[0.485, 0.456, 0.406]"], w)
    pdf.table_row(["", "std=[0.229, 0.224, 0.225]"], w)
    pdf.table_row(["Version", "EfficientNet-B2_384px_3class_v1.0"], w)
    pdf.table_row(["Weights File", "models/chest_xray_3class.pth"], w)
    pdf.table_row(["Inference Device", "CUDA (if available), else CPU"], w)
    pdf.ln(3)
    pdf.body(
        "The classifier head replaces the original ImageNet 1000-class fc layer with a "
        "2-layer sequential: Dropout(p=0.3) followed by Linear(1408, 3). At inference, "
        "softmax produces 3-class probabilities. The predicted class is argmax, and "
        "confidence is the corresponding softmax probability."
    )

    pdf.subsection("2.1", "Embedding Model (RAG)")
    pdf.table_header(["Attribute", "Value"], w)
    pdf.table_row(["Model", "all-MiniLM-L6-v2 (Sentence Transformers)"], w)
    pdf.table_row(["Dimension", "384"], w)
    pdf.table_row(["Normalization", "L2 (cosine similarity via FAISS IndexFlatIP)"], w)
    pdf.table_row(["Batch Size", "64"], w)
    pdf.ln(3)

    # === Section 3: Pipeline Architecture ===
    pdf.section("3", "Pipeline Architecture")
    pdf.body(
        "The pipeline is orchestrated by PipelineOrchestrator (backend/pipeline/orchestrator.py). "
        "It chains 7 agents in sequence with error handling and fallback at each stage."
    )

    pdf.subsection("3.1", "Module 1: Preprocessing (PreprocessingAgent)")
    pdf.body(
        "File: backend/agents/preprocessor.py\n\n"
        "Steps performed:\n"
        "1. EXIF transpose (auto-rotate based on orientation tag)\n"
        "2. Convert to RGB mode\n"
        "3. Resize to 384x384 using cv2.INTER_LANCZOS4\n"
        "4. Normalize: (pixel/255 - mean) / std (ImageNet values)\n"
        "5. Transpose to (C, H, W) format: channels-first for PyTorch\n\n"
        "Input: PIL Image (original upload)\n"
        "Output: numpy array (3, 384, 384) float32"
    )

    pdf.subsection("3.2", "Module 2: Diagnosis (DiagnosisAgent)")
    pdf.body(
        "File: backend/agents/diagnosis.py\n\n"
        "Steps performed:\n"
        "1. Convert numpy array to torch tensor, add batch dimension\n"
        "2. Forward pass through EfficientNet-B2\n"
        "3. Apply softmax to get probabilities\n"
        "4. Extract argmax (predicted class) and confidence\n\n"
        "Output dict:\n"
        "  - label: 'NORMAL', 'BACTERIAL', or 'VIRAL'\n"
        "  - confidence_score: float (0-1)\n"
        "  - model_version: 'EfficientNet-B2_384px_3class_v1.0'\n"
        "  - logits: raw model output\n"
        "  - probabilities: dict with class probabilities"
    )

    pdf.subsection("3.3", "Module 3: Explainability (ExplainabilityAgent)")
    pdf.body(
        "File: backend/agents/explainability.py\n\n"
        "Produces two explainability outputs:\n\n"
        "A) Grad-CAM++ Heatmap:\n"
        "   - Library: pytorch_grad_cam (GradCAMPlusPlus)\n"
        "   - Target layer: model.features[7] (last MBConv block)\n"
        "   - Target class: predicted class\n"
        "   - Output: RGB overlay on original X-ray\n\n"
        "B) Integrated Gradients (labeled 'SHAP' in UI):\n"
        "   - Library: captum (IntegratedGradients)\n"
        "   - Runs at 256x256 (upscaled to 384x384 for display)\n"
        "   - n_steps=25, baseline=zeros\n"
        "   - Post-processing: channel mean, Gaussian blur, 99th percentile clip\n"
        "   - Power-boosted (sqrt curve) for visible heatmap\n\n"
        "Also produces 6-zone regional importance scores."
    )

    pdf.subsection("3.4", "Module 4a: RAG Agent (RAGAgent)")
    pdf.body(
        "File: backend/agents/rag_agent.py\n\n"
        "Hybrid RAG with 3-tier fallback:\n\n"
        "1. PDF Vector Store (preferred):\n"
        "   - FAISS IndexFlatIP with 968 vectors\n"
        "   - 7 source files: 6 PDFs + 1 text\n"
        "   - Chunks: 800 chars, 150 overlap, min 40 chars\n"
        "   - Returns top-5 results with source metadata\n\n"
        "2. PubMed-Seeded Index (fallback):\n"
        "   - FAISS IndexFlatL2 with 50 vectors\n"
        "   - Seeded from 5 pneumonia-related queries\n"
        "   - Distance threshold: 1.5\n\n"
        "3. Online PubMed (last resort):\n"
        "   - NCBI EUtils API (esearch + efetch)\n"
        "   - Returns title + abstract from XML\n\n"
        "Output: list of {text, source, page} dicts"
    )

    pdf.subsection("3.5", "Module 4b: LLM Synthesizer (SynthesizerAgent)")
    pdf.body(
        "File: backend/agents/synthesizer.py\n\n"
        "Provider: OpenRouter\n"
        "Model: liquid/lfm-2.5-2.6b:free\n"
        "URL: https://openrouter.ai/api/v1/chat/completions\n"
        "Max tokens: 1200 | Timeout: 45s\n\n"
        "Prompt includes:\n"
        "- Model output (label, confidence, version)\n"
        "- Explainability status\n"
        "- Top 5 RAG clinical guidelines (truncated to 500 chars)\n\n"
        "System prompt: Expert radiologist AI with strict JSON Schema output\n\n"
        "Response structure:\n"
        "  overall_status: 'Normal' | 'Abnormal' | 'Requires Attention'\n"
        "  confidence: float\n"
        "  findings: [{name, region, severity, confidence, description}]\n"
        "  recommendations: [string]\n"
        "  summary: string\n\n"
        "Fallback: fallback_synthesis() when LLM unavailable"
    )

    pdf.subsection("3.6", "Module 4c: Validator (ValidatorAgent)")
    pdf.body(
        "File: backend/agents/validator.py\n\n"
        "Three guardrail checks:\n\n"
        "1. Confidence Gate: confidence_score >= CONFIDENCE_THRESHOLD (0.30)\n\n"
        "2. Narrative Check: combined summary+findings text must contain\n"
        "   at least one expected clinical term\n\n"
        "3. Synthesis Gate: structured OpenRouter synthesis must have completed\n\n"
        "Pipeline status: 'APPROVED' if all checks pass, 'FALLBACK' when\n"
        "OpenRouter synthesis is unavailable, otherwise 'RETRY'.\n"
        "Fallback results are never marked as validated."
    )

    pdf.subsection("3.7", "Module 6: Active Learning (LearnerAgent)")
    pdf.body(
        "File: backend/agents/learner.py\n\n"
        "Async logging via daemon thread to knowledge/case_log.jsonl\n\n"
        "Hard case criteria:\n"
        "- Confidence between 0.50 and 0.75\n"
        "- OR retry_count > 0\n"
        "- OR status == 'RETRY'\n\n"
        "Hard cases also flagged to knowledge/hard_cases.jsonl\n"
        "Stats available via GET /api/stats endpoint"
    )

    # === Section 4: RAG Knowledge Base ===
    pdf.section("4", "RAG Knowledge Base")
    pdf.body(
        "The RAG knowledge base consists of curated clinical guidelines for pneumonia "
        "diagnosis, stored as vector embeddings for semantic search."
    )
    pdf.subsection("4.1", "Source Files (knowledge/guidelines/)")
    w2 = [100, 90]
    pdf.table_header(["File", "Type"], w2)
    pdf.table_row(["ATS_IDSA_CAP_Guidelines_2019.pdf", "Clinical Guideline"], w2)
    pdf.table_row(["IDSA_ATS_CAP_2007.pdf", "Clinical Guideline"], w2)
    pdf.table_row(["2503.02906v1.pdf", "Research Paper"], w2)
    pdf.table_row(["executive_summary.pdf", "Summary Document"], w2)
    pdf.table_row(["koo-et-al-2020-...viral-pneumonia.pdf", "Radiology Update"], w2)
    pdf.table_row(["main.pdf", "Research Paper"], w2)
    pdf.table_row(["Pneumonia_Imaging_Bacterial_Viral_PMC6717952.txt", "PMC Article"], w2)
    pdf.ln(3)

    pdf.subsection("4.2", "Vector Store Configuration")
    pdf.kv("Index type", "FAISS IndexFlatIP (cosine similarity)")
    pdf.kv("Total vectors", "968")
    pdf.kv("Embedding model", "all-MiniLM-L6-v2 (384-dim)")
    pdf.kv("Chunk size", "800 characters")
    pdf.kv("Chunk overlap", "150 characters")
    pdf.kv("Min chunk size", "40 characters")
    pdf.kv("Ingestion script", "backend/ingest_vector_db.py")
    pdf.ln(3)

    pdf.subsection("4.3", "Ingestion Process")
    pdf.body(
        "1. Read PDFs via pypdf.PdfReader (page-by-page)\n"
        "2. Read plain text files directly\n"
        "3. Chunk text: 800 chars with 150 overlap\n"
        "4. Embed all chunks with SentenceTransformer (batch_size=64)\n"
        "5. Build FAISS IndexFlatIP with normalized embeddings\n"
        "6. Save to knowledge/pdf_store/ (faiss.index + chunks.json)\n"
        "7. Metadata includes: source filename, page number, chunk_id"
    )

    # === Section 5: LLM Integration ===
    pdf.section("5", "LLM Integration")
    w3 = [55, 135]
    pdf.table_header(["Attribute", "Value"], w3)
    pdf.table_row(["Provider", "OpenRouter"], w3)
    pdf.table_row(["API URL", "https://openrouter.ai/api/v1/chat/completions"], w3)
    pdf.table_row(["Model", "liquid/lfm-2.5-2.6b:free"], w3)
    pdf.table_row(["Max Tokens", "1200"], w3)
    pdf.table_row(["Timeout", "45 seconds"], w3)
    pdf.table_row(["Authentication", "OPENROUTER_API_KEY environment variable"], w3)
    pdf.table_row(["Output Mode", "Strict JSON Schema"], w3)
    pdf.ln(3)
    pdf.body(
        "The LLM receives a structured prompt containing the model prediction, "
        "explainability status, and top-five RAG clinical guidelines. OpenRouter "
        "structured outputs enforce the report schema before local validation. "
        "API keys and raw prompt/response content are never logged."
    )

    # === Section 6: Explainability Methods ===
    pdf.section("6", "Explainability Methods")

    pdf.subsection("6.1", "Grad-CAM++")
    pdf.kv("Library", "pytorch_grad_cam v1.5.5")
    pdf.kv("Variant", "GradCAMPlusPlus (cleaner than vanilla Grad-CAM)")
    pdf.kv("Target layer", "model.features[7] (last MBConv block)")
    pdf.kv("Target", "ClassifierOutputTarget(predicted_class)")
    pdf.kv("Output", "RGB overlay on original X-ray (384x384)")
    pdf.ln(3)
    pdf.body(
        "Grad-CAM++ produces a class-discriminative localization map highlighting "
        "regions important for the predicted class. The target layer is the last "
        "MBConv block (features[7]) of EfficientNet-B2, which provides good spatial "
        "resolution for localization. The grayscale CAM is overlaid on the original "
        "X-ray using show_cam_on_image() with alpha blending."
    )

    pdf.subsection("6.2", "Integrated Gradients (SHAP)")
    pdf.kv("Library", "captum v0.9.0")
    pdf.kv("Resolution", "256x256 (upscaled to 384x384 for display)")
    pdf.kv("Steps", "25")
    pdf.kv("Baseline", "All-zeros tensor")
    pdf.kv("Post-processing", "Gaussian blur (11x11, sigma=3)")
    pdf.kv("Clipping", "99th percentile")
    pdf.kv("Boost", "Power curve: sign(sv) * |sv|^0.4")
    pdf.kv("Colormap", "RdBu_r (red=positive, blue=negative)")
    pdf.ln(3)
    pdf.body(
        "Integrated Gradients computes pixel-level attributions by accumulating "
        "gradients along a straight-line path from baseline (all zeros) to input. "
        "The attribution is averaged across RGB channels, Gaussian-blurred, clipped "
        "at the 99th percentile, and boosted with a sqrt-like power curve for "
        "visibility. Attribution is displayed only within the lung fields."
    )

    pdf.subsection("6.3", "Regional Importance")
    pdf.body(
        "The 384x384 attribution map is divided into 6 lung zones:\n"
        "- Upper Left, Upper Right\n"
        "- Middle Left, Middle Right\n"
        "- Lower Left, Lower Right\n\n"
        "For each zone, the mean absolute attribution within the lung-masked "
        "area is computed. All zone scores are normalized to percentages "
        "(sum = 100%). These are displayed as horizontal bar charts in the UI."
    )

    # === Section 7: Frontend Architecture ===
    pdf.section("7", "Frontend Architecture")

    pdf.subsection("7.1", "Technology Stack")
    w4 = [60, 130]
    pdf.table_header(["Technology", "Version / Details"], w4)
    pdf.table_row(["React", "^19.1.0"], w4)
    pdf.table_row(["Vite", "^8.2.0 (build tool)"], w4)
    pdf.table_row(["@vitejs/plugin-react", "^4.5.2"], w4)
    pdf.table_row(["Package Name", "lungai-frontend"], w4)
    pdf.table_row(["Dev Server Port", "5173"], w4)
    pdf.table_row(["Proxy /api", "http://localhost:5000"], w4)
    pdf.table_row(["Fonts", "DM Sans + Inter (Google Fonts)"], w4)
    pdf.ln(3)

    pdf.subsection("7.2", "Component Hierarchy")
    pdf.body(
        "App.jsx (root)\n"
        "  |- Navbar.jsx (sticky nav, scroll-spy, mobile drawer)\n"
        "  |- Hero.jsx (particle background, glowing orbs, CTA)\n"
        "  |- About.jsx (4 feature cards: Preprocessing, EfficientNet-B2,\n"
        "  |       Grad-CAM/SHAP, RAG+LLM)\n"
        "  |- HowItWorks.jsx (6-step timeline)\n"
        "  |- DiseaseAwareness.jsx (tabbed: Overview, Types, Symptoms, Prevention)\n"
        "  |- Upload.jsx (drag-drop, scanning animation, progress ring)\n"
        "  |- Dashboard.jsx (results: ImageSlider, ConfidenceGauge, BarChart,\n"
        "  |       SHAP zones, AI report, recommendations, evidence sources,\n"
        "  |       regions, Download Report, Share Results)\n"
        "  |- Team.jsx (team cards + tech stack badges)\n"
        "  |- Footer.jsx (brand, links, project info)"
    )

    pdf.subsection("7.3", "UI Sub-components")
    w5 = [45, 145]
    pdf.table_header(["Component", "Description"], w5)
    pdf.table_row(["ConfidenceGauge", "SVG circular gauge with color coding"], w5)
    pdf.table_row(["BarChart", "Horizontal bars for 3-class probabilities"], w5)
    pdf.table_row(["ImageSlider", "Before/after comparison with draggable handle"], w5)
    pdf.table_row(["TypewriterText", "Character-by-character reveal at 20ms/char"], w5)
    pdf.table_row(["ScrollReveal", "IntersectionObserver fade+slide animation"], w5)
    pdf.table_row(["Tilt3D", "Mouse-tracking 3D perspective tilt effect"], w5)
    pdf.table_row(["ParticleBackground", "25 floating particles (blue/white)"], w5)
    pdf.table_row(["ProgressSteps", "Linear step indicators with checkmarks"], w5)
    pdf.ln(3)

    pdf.subsection("7.4", "Custom Hooks")
    pdf.bullet("useInView: IntersectionObserver wrapper, returns [ref, isInView]")
    pdf.bullet("useScrollSpy: Tracks active section via rootMargin -70%")

    # === Section 8: Flask API ===
    pdf.section("8", "Flask API Endpoints")
    w6 = [20, 50, 120]
    pdf.table_header(["Method", "Route", "Purpose"], w6)
    pdf.table_row(["GET", "/", "Service info + endpoints list"], w6)
    pdf.table_row(["GET", "/api/status", "Model status, version, provider"], w6)
    pdf.table_row(["POST", "/api/analyze", "Main analysis (accepts xray file)"], w6)
    pdf.table_row(["GET", "/api/stats", "Learner stats (total/hard cases)"], w6)
    pdf.table_row(["POST", "/api/download-report", "PDF report generation"], w6)
    pdf.table_row(["OPTIONS", "/api/download-report", "CORS preflight (204)"], w6)
    pdf.ln(3)
    pdf.body(
        "Accepted image formats: .jpg, .jpeg, .png, .webp, .bmp, .tiff\n"
        "Max upload size: 16 MB\n"
        "CORS: Access-Control-Allow-Origin: * (all responses)\n"
        "Startup: Lazy-loads PipelineOrchestrator on first request;\n"
        "eagerly loads RAG index in background daemon thread."
    )

    # === Section 9: PDF Report Generator ===
    pdf.section("9", "PDF Report Generator")
    pdf.kv("File", "backend/report_generator.py")
    pdf.kv("Library", "fpdf2 (FPDF class)")
    pdf.kv("Output", "PDF bytes via pdf.output(dest='S')")
    pdf.ln(3)
    pdf.body("PDF Sections:")
    pdf.bullet("Header: 'Xyra - Chest X-Ray Analysis Report'")
    pdf.bullet("Case Information: case ID, image quality, processing time, validation")
    pdf.bullet("Diagnosis: prediction, confidence, class probabilities")
    pdf.bullet("Detected Regions: name, severity, description")
    pdf.bullet("Clinical Summary: LLM-generated narrative")
    pdf.bullet("Recommendations: numbered list")
    pdf.bullet("Evidence Sources: title, journal, year, text excerpt")
    pdf.bullet("Disclaimer: academic prototype notice")
    pdf.ln(2)
    pdf.body(
        "Character safety: _safe() function replaces Unicode punctuation "
        "(curly quotes, em dashes, bullets) with latin-1 compatible ASCII "
        "equivalents to prevent encoding errors."
    )

    # === Section 10: Training Details ===
    pdf.section("10", "Training Details")
    pdf.subsection("10.1", "3-Class Model (chest_xray_3class.pth)")
    pdf.kv("Notebook", "train-3class-shortcut-free-b2-384 (Kaggle)")
    pdf.kv("GPU", "NVIDIA T4 x2")
    pdf.kv("Architecture", "EfficientNet-B2 @ 384px")
    pdf.kv("Training Data", "paultimothymooney (5,232) + kostas (4,672) = ~9,904 images")
    pdf.kv("Class Balance", "Balanced 3-class (Normal, Bacterial, Viral)")
    pdf.kv("Validation", "12% stratified split, seed=42")
    pdf.ln(2)
    pdf.body("Training Recipe:")
    pdf.bullet("Batch size: 16")
    pdf.bullet("Optimizer: AdamW (lr=1e-4, weight_decay=1e-4)")
    pdf.bullet("Label smoothing: 0.1")
    pdf.bullet("Scheduler: CosineAnnealingLR (T_max=60)")
    pdf.bullet("Early stopping: patience=15")
    pdf.bullet("Augmentation: Resize(416) + RandomCrop(384) + HFlip + Rot15 + ColorJitter + Affine + Sharpness")
    pdf.bullet("Evaluation: TTA (Test-Time Augmentation)")
    pdf.bullet("Test set: kostas TEST split (618 unique images, md5-recovered labels)")

    # === Section 11: Configuration ===
    pdf.section("11", "Configuration Reference")
    pdf.body("All configuration constants from backend/config.py:")
    pdf.ln(2)
    config_items = [
        ("MODEL_WEIGHTS", "models/chest_xray_3class.pth"),
        ("MODEL_CLASSES", '["NORMAL", "BACTERIAL", "VIRAL"]'),
        ("MODEL_INPUT_SIZE", "(384, 384)"),
        ("IMAGENET_MEAN", "[0.485, 0.456, 0.406]"),
        ("IMAGENET_STD", "[0.229, 0.224, 0.225]"),
        ("OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions"),
        ("OPENROUTER_API_KEY", "Loaded from backend/.env; never logged"),
        ("OPENROUTER_MODEL", "liquid/lfm-2.5-2.6b:free"),
        ("LLM_MAX_TOKENS", "1200"),
        ("LLM_TIMEOUT_SECONDS", "45"),
        ("FAISS_DIMENSION", "384"),
        ("FAISS_EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        ("CONFIDENCE_THRESHOLD", "0.30"),
        ("MAX_RETRY_COUNT", "1"),
        ("OUTPUT_DIR", "static/outputs"),
    ]
    w7 = [55, 135]
    pdf.table_header(["Variable", "Value"], w7)
    for k, v in config_items:
        pdf.table_row([k, v], w7)

    # === Section 12: Dependencies ===
    pdf.section("12", "Dependencies")
    deps = [
        ("Flask", "3.1.3"),
        ("gunicorn", "latest"),
        ("Pillow", "11.2.1"),
        ("python-dotenv", "latest"),
        ("torch", "2.12.1"),
        ("torchvision", "0.27.1"),
        ("grad-cam", "1.5.5"),
        ("captum", "0.9.0"),
        ("opencv-python", "4.13.0.92"),
        ("numpy", "2.2.6"),
        ("matplotlib", "3.10.6"),
        ("faiss-cpu", "1.14.3"),
        ("sentence-transformers", "5.6.0"),
        ("requests", "2.34.2"),
        ("pypdf", ">=4.2.0"),
        ("fpdf2", ">=2.8.0"),
    ]
    w8 = [70, 120]
    pdf.table_header(["Package", "Version"], w8)
    for name, ver in deps:
        pdf.table_row([name, ver], w8)

    # === Section 13: File Structure ===
    pdf.section("13", "File Structure")
    tree = """semifinal/
  run.bat
  backend/
    app.py                    Flask server (port 5000)
    config.py                 All configuration constants
    requirements.txt          18 Python dependencies
    ingest_vector_db.py       PDF/Text -> FAISS index builder
    report_generator.py       PDF report via fpdf2
    chat_via_openrouter.py    OpenRouter structured-output client
    models/
      chest_xray_3class.pth   EfficientNet-B2 weights
    agents/
      preprocessor.py         Module 1: Image preprocessing
      diagnosis.py            Module 2: 3-class classification
      explainability.py       Module 3: Grad-CAM++ + Integrated Gradients
      rag_agent.py            Module 4a: Hybrid RAG
      synthesizer.py          Module 4b: LLM report synthesis
      validator.py            Module 4c: Guardrail validation
      learner.py              Module 6: Active learning logger
    pipeline/
      orchestrator.py         Pipeline orchestrator
    knowledge/
      guidelines/             7 source PDFs/txt files
      pdf_store/              FAISS index + chunks
      clinical_guidelines.faiss
      metadata.json
      case_log.jsonl
      hard_cases.jsonl
    static/
      outputs/                Generated images
  frontend/
    index.html
    package.json              React 19, Vite 8
    vite.config.js
    src/
      main.jsx
      App.jsx
      services/api.js
      hooks/
        useInView.js
        useScrollSpy.js
      data/
        teamMembers.js
        pipelineSteps.js
        diseaseInfo.js
      components/
        Navbar.jsx            Navigation bar
        Hero.jsx              Hero section
        About.jsx             Feature cards
        HowItWorks.jsx        6-step timeline
        DiseaseAwareness.jsx  Tabbed info
        Upload.jsx            File upload
        Dashboard.jsx         Results display
        Team.jsx              Team cards
        Footer.jsx            Footer
        ui/                   8 UI sub-components"""
    pdf.code_block(tree)

    output = pdf.output(dest="S")
    if isinstance(output, str):
        return output.encode("latin-1")
    return bytes(output)


if __name__ == "__main__":
    pdf_bytes = generate_system_report()
    out_path = "Xyra_System_Report.pdf"
    with open(out_path, "wb") as f:
        f.write(pdf_bytes)
    print(f"Report saved to {out_path} ({len(pdf_bytes)} bytes)")
