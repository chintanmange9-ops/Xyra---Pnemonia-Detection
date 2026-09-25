# Xyra — Explainable Pneumonia Detection

Xyra is an explainable, multi-agent Clinical Decision Support System (CDSS) for chest X-ray classification. It predicts one of three classes:

- `NORMAL`
- `BACTERIAL` pneumonia
- `VIRAL` pneumonia

The repository contains the EfficientNet-B2 training notebook, the packaged classifier and U-Net lung-mask weights, a Flask API, a React/Vite frontend, hybrid FAISS RAG, and OpenRouter-powered structured report synthesis.

> **Research prototype:** Xyra is intended for academic research and evaluation. It is not a medical device and must not be used as the sole basis for diagnosis or treatment. A qualified radiologist must review all clinical images and reports.

## Repository Contents

```text
semifinal/
├── backend/
│   ├── agents/
│   │   ├── preprocessor.py       Image loading and ImageNet preprocessing
│   │   ├── diagnosis.py          EfficientNet-B2 three-class inference
│   │   ├── explainability.py     Integrated Gradients and lung masking
│   │   ├── rag_agent.py          FAISS/PDF RAG with PubMed fallback
│   │   ├── synthesizer.py        OpenRouter report synthesis and fallback
│   │   ├── validator.py          Guardrail validation gate
│   │   └── learner.py            Local case logging and hard-case flagging
│   ├── pipeline/orchestrator.py  Sequential agent orchestration
│   ├── models/
│   │   ├── chest_xray_3class.pth EfficientNet-B2 classifier weights
│   │   └── best_unet_model.pth   Auxiliary U-Net lung-mask weights
│   ├── knowledge/
│   │   ├── guidelines/           Clinical guideline source documents
│   │   ├── pdf_store/            FAISS PDF index and chunks
│   │   ├── clinical_guidelines.faiss
│   │   └── metadata.json
│   ├── chat_via_openrouter.py    OpenRouter strict-schema client
│   ├── app.py                    Flask API
│   ├── config.py                 Runtime configuration
│   └── requirements.txt
├── frontend/                     React 19 + Vite dashboard
├── notebook9e5ff259c3.ipynb     Classifier training notebook
├── run.bat                       Windows development launcher
└── .env.example                 Safe configuration template
```

Runtime-generated case logs, attribution images, caches, `.env`, and generated reports are intentionally excluded from Git. They remain local and are regenerated at runtime.

## Model and Training Notebook

The training notebook is [`notebook9e5ff259c3.ipynb`](notebook9e5ff259c3.ipynb). It was designed for Kaggle GPU execution and contains five sequential cells.

### 1. Reproducible environment

The notebook sets:

- Python and PyTorch device selection with CUDA when available
- `BATCH_SIZE = 16`
- `IMG_SIZE = 384`
- NumPy, PyTorch, and Python random seeds set to `42`
- ImageNet mean and standard deviation

### 2. Anti-shortcut raw-image dataset

The classifier is trained on raw radiographs, not lung-segmented crops. The notebook uses:

```text
Resize(416, 416)
RandomCrop(384, 384)
RandomHorizontalFlip(p=0.5)
RandomRotation(15)
ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2, hue=0.05)
RandomAffine(translate=(0.1, 0.1), scale=(0.9, 1.1))
RandomAdjustSharpness(sharpness_factor=1.5, p=0.3)
ToTensor()
Normalize(ImageNet mean, ImageNet std)
```

The validation transform resizes directly to `384 x 384`. Mixup is enabled with `MIXUP_ALPHA = 0.4` and a probability of `0.4`.

The `AntiShortcutDataset` returns two labels and a mixup coefficient so the training loop can blend samples and apply the corresponding mixed loss.

### 3. Data sources and labels

The notebook combines raw images from the following Kaggle datasets:

1. **paultimothymooney/chest-xray-pneumonia**
   - `NORMAL` images are mapped to `NORMAL`.
   - `PNEUMONIA` filenames containing `bacteria` are mapped to `BACTERIAL`.
   - `PNEUMONIA` filenames containing `virus` are mapped to `VIRAL`.

2. **kostasdiamantaras/chest-xrays-bacterial-viral-pneumonia-normal**
   - Images are resolved through `labels_train.csv`.
   - Class IDs `0`, `1`, and `2` map to `NORMAL`, `BACTERIAL`, and `VIRAL`.

The notebook searches the Kaggle input mount dynamically, including the `/kaggle/input/datasets/<owner>/<dataset>` layout. It shuffles each class pool, combines the pools, and creates a stratified split.

The notebook does not contain a fixed reported score because it is committed without executed outputs. The validation metrics are printed when the notebook is run.

### 4. Model and optimizer

The classifier is built from torchvision EfficientNet-B2 with ImageNet initialization:

```python
model = models.efficientnet_b2(weights="IMAGENET1K_V1")
model.classifier = nn.Sequential(
    nn.Dropout(0.3),
    nn.Linear(model.classifier[1].in_features, 3),
)
```

Training configuration:

- Three classes: `NORMAL`, `BACTERIAL`, `VIRAL`
- Weighted random sampling using inverse training-class frequencies
- `CrossEntropyLoss(label_smoothing=0.1)`
- AdamW with backbone learning rate `1e-4`
- Head learning rate `1e-3`
- Weight decay `1e-4`
- `CosineAnnealingLR(T_max=60)`
- Up to 60 epochs
- Early stopping patience of 15 epochs
- Best validation accuracy checkpoint saved to:

```text
/kaggle/working/chest_xray_3class.pth
```

### 5. Test-time augmentation evaluation

The final notebook cell reloads the best checkpoint and evaluates the validation split with horizontal-flip TTA:

```text
prediction = argmax(logits(original) + logits(horizontal_flip(original)))
```

It prints:

- Classification report
- Confusion matrix
- Macro one-vs-rest ROC AUC when supported by the installed scikit-learn version
- Per-class recall

### Running the notebook

1. Open the notebook in Kaggle or Jupyter.
2. Attach the two chest X-ray datasets as Kaggle inputs.
3. Select a GPU accelerator.
4. Run the cells from top to bottom.
5. Download `chest_xray_3class.pth` from `/kaggle/working`.
6. Place the downloaded checkpoint at:

```text
backend/models/chest_xray_3class.pth
```

The notebook trains the classifier only. The auxiliary U-Net lung-mask model is packaged separately as `backend/models/best_unet_model.pth` and is used only to constrain the explainability map.

## Runtime System Architecture

The Flask entry point is `backend/app.py`. Requests pass through the following sequence:

```text
Upload
  → PreprocessingAgent
  → DiagnosisAgent
  → ExplainabilityAgent
  → RAGAgent
  → SynthesizerAgent
  → ValidatorAgent
  → LearnerAgent
  → JSON response
```

### 1. Preprocessing

`backend/agents/preprocessor.py`:

- Applies EXIF orientation
- Converts to RGB
- Resizes to `384 x 384` with Lanczos interpolation
- Applies ImageNet normalization
- Returns a `3 x 384 x 384` float tensor

### 2. Diagnosis

`backend/agents/diagnosis.py`:

- Loads `backend/models/chest_xray_3class.pth`
- Builds torchvision EfficientNet-B2
- Replaces the classifier head with `Dropout(0.3) + Linear(1408, 3)`
- Runs softmax inference
- Returns the label, probability distribution, model version, and confidence

The deployed checkpoint is the raw-image classifier described in the notebook. The U-Net is not part of classification.

### 3. Explainability

`backend/agents/explainability.py` uses Captum Integrated Gradients:

- Attribution resolution: `256 x 256`, upscaled for display
- 25 integration steps
- Zero baseline
- Channel averaging
- Gaussian smoothing
- Percentile clipping
- Power-curve contrast enhancement
- Lung-mask constraint

The UI historically calls this map “SHAP” because the API field is named `shapAnalysis`/`shapUrl`, but the implementation is Integrated Gradients, not a Shapley-value decomposition.

The lung mask is loaded from:

```text
backend/models/best_unet_model.pth
```

If the U-Net cannot be loaded, the agent falls back to an OpenCV heuristic mask. The current packaged repository includes the U-Net weights.

### 4. Hybrid RAG

`backend/agents/rag_agent.py` searches in this order:

1. Packaged PDF FAISS store under `backend/knowledge/pdf_store/`
2. PubMed-seeded FAISS index
3. Online PubMed E-utilities as a last resort

The packaged PDF store contains 968 chunks embedded with `all-MiniLM-L6-v2`. The first run requires the embedding model to be available locally or downloadable from the model provider.

RAG warmup and request-time search share one initialization lock. The index is loaded once even when startup warmup and the first request overlap.

### 5. OpenRouter synthesis

`backend/chat_via_openrouter.py` calls:

```text
https://openrouter.ai/api/v1/chat/completions
```

The default model is:

```text
liquid/lfm-2.5-2.6b:free
```

The request uses a strict JSON Schema containing:

- `overall_status`
- `confidence`
- Exactly one primary `finding`
- Up to three `recommendations`
- `summary`

The synthesizer then checks that the generated finding agrees with the CNN label and uses the CNN confidence rather than allowing the LLM to replace it.

If OpenRouter is unavailable, malformed, rate-limited, or returns a contradictory report, the system produces a deterministic fallback response. Fallback responses are never marked as validated.

### 6. Validation

`backend/agents/validator.py` requires:

1. Confidence threshold
2. Expected clinical terminology in the narrative
3. Completed OpenRouter synthesis

Result statuses:

| Status | Meaning |
|---|---|
| `APPROVED` | All guardrail checks pass and OpenRouter synthesis completed |
| `FALLBACK` | LLM synthesis was unavailable or degraded |
| `RETRY` | Synthesis completed but another guardrail check failed |

The frontend displays fallback results as degraded and requiring clinical review.

### 7. Local learning log

`backend/agents/learner.py` writes local case records and hard-case flags under `backend/knowledge/`. These files are ignored by Git because they are runtime data, not source code.

## Requirements

### Backend

- Python 3.10+
- PyTorch and torchvision
- Flask
- Captum
- FAISS CPU
- Sentence Transformers
- OpenCV
- Pillow
- Requests
- fpdf2

Install from the repository root:

```bash
cd backend
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On Linux/macOS, activate with `source .venv/bin/activate`.

### Frontend

Use Node.js `20.19+` or `22.12+`:

```bash
cd frontend
npm install
npm run dev
```

## Configuration

Copy the safe template and create a local environment file:

```bash
cd backend
copy .env.example .env       # Windows
# cp .env.example .env       # Linux/macOS
```

Set:

```text
OPENROUTER_API_KEY=your-new-key
OPENROUTER_MODEL=liquid/lfm-2.5-2.6b:free
```

Never commit `.env`. The root `.gitignore` excludes it and the template `.env.example` is safe to commit.

The current free model is zero-cost but rate-limited and may be slow. For a stable deployment, configure a paid low-latency model that supports OpenRouter structured outputs.

> OpenRouter free-model providers may log prompts or use them for service operations. Do not send identifiable patient information or protected health information through the free route.

## Running Locally

From the repository root on Windows:

```bash
run.bat
```

Or start the services separately:

```bash
cd backend
python app.py
```

```bash
cd frontend
npm run dev
```

Default URLs:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:5000`
- Backend status: `http://localhost:5000/api/status`

## API

### Analyze one image

```bash
curl -X POST http://localhost:5000/api/analyze \
  -F "xray=@sample.jpg"
```

### Analyze a batch

```bash
curl -X POST http://localhost:5000/api/analyze-batch \
  -F "xrays=@sample1.jpg" \
  -F "xrays=@sample2.jpg"
```

### Check service status

```bash
curl http://localhost:5000/api/status
```

### Generate a PDF report

```bash
curl -X POST http://localhost:5000/api/download-report \
  -H "Content-Type: application/json" \
  -d "{\"result\": {}}"
```

The report endpoint expects a result object shaped like the frontend analysis response.

## Validation and Tests

Run backend regression tests:

```bash
cd backend
python -m unittest -v
python -m compileall -q .
```

Run the frontend production build:

```bash
cd frontend
npm run build
```

The backend tests cover:

- OpenRouter success and malformed responses
- Missing API key
- HTTP errors and timeouts
- CNN/LLM confidence consistency
- Rejection of contradictory findings
- RAG single initialization under concurrent warmup
- Fallback status and validation behavior

## GitHub Notes

The repository includes model artifacts below GitHub's 100 MB per-file limit:

- `backend/models/chest_xray_3class.pth`
- `backend/models/best_unet_model.pth`

The following are intentionally not uploaded:

- `.env` and API keys
- `case_log.jsonl` and `hard_cases.jsonl`
- `static/outputs/`
- `frontend/node_modules/`
- `frontend/dist/`
- generated system-report PDF
- local memory/session traces

The current development configuration binds Flask to `0.0.0.0:5000` and uses Flask's development server. Add authentication, restricted CORS, TLS, a production WSGI server, rate limiting, and a formal clinical validation process before exposing Xyra outside a trusted development network.

## Limitations

- The classifier is a research model, not a clinically validated diagnostic device.
- DICOM support is not implemented; the API accepts common image formats such as JPEG, PNG, WEBP, BMP, and TIFF.
- Image-quality assessment is informational and does not establish that an input is a valid frontal chest radiograph.
- The system does not provide a formal patient-identity, consent, retention, or de-identification workflow.
- OpenRouter availability, rate limits, model behavior, and provider data policies are external dependencies.
- The packaged PDF RAG store improves retrieval but is not a substitute for clinician review.
