import os

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Model paths — 3-class classifier: Normal / Bacterial / Viral (EfficientNet-B2 @384px, raw — no UNet segmentation)
# Production: c5_b2_3class_384_31MB.pth (b8d79ffa, 31.27MB, 7.77M params) — shortcut-free raw training (c5nonseg)
# Segmented alternatives (c4_b2_* , checkpoint3/2/1) kept in ipd/test_models/ for reference only
MODEL_WEIGHTS = os.path.join(BASE_DIR, "models", "chest_xray_3class.pth")
UNET_WEIGHTS = os.path.join(BASE_DIR, "models", "best_unet_model.pth")
MODEL_CLASSES = ["NORMAL", "BACTERIAL", "VIRAL"]
MODEL_INPUT_SIZE = (384, 384)

# ImageNet normalization (matches EfficientNet training)
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# LLM — OpenRouter
LLM_PROVIDER = "openrouter"
OPENROUTER_API_URL = os.environ.get(
    "OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions"
)
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "liquid/lfm-2.5-2.6b:free")
OPENROUTER_SITE_URL = os.environ.get("OPENROUTER_SITE_URL", "http://localhost:5000")
OPENROUTER_APP_NAME = os.environ.get("OPENROUTER_APP_NAME", "Xyra")
LLM_MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", "1200"))
LLM_CONNECT_TIMEOUT_SECONDS = int(os.environ.get("LLM_CONNECT_TIMEOUT_SECONDS", "10"))
LLM_TIMEOUT_SECONDS = int(os.environ.get("LLM_TIMEOUT_SECONDS", "45"))

# FAISS
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "knowledge", "clinical_guidelines.faiss")
FAISS_METADATA_PATH = os.path.join(BASE_DIR, "knowledge", "metadata.json")
FAISS_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
FAISS_DIMENSION = 384

# PDF vector store (preferred over the PubMed-seeded index when present)
PDF_VECTOR_STORE_DIR = os.path.join(BASE_DIR, "knowledge", "pdf_store")
PDF_INDEX_PATH = os.path.join(PDF_VECTOR_STORE_DIR, "faiss.index")
PDF_CHUNKS_PATH = os.path.join(PDF_VECTOR_STORE_DIR, "chunks.json")

# Output
OUTPUT_DIR = os.path.join(BASE_DIR, "static", "outputs")

# Validation
CONFIDENCE_THRESHOLD = 0.30  # 30% minimum to pass
MAX_RETRY_COUNT = 1

# Learning loop
CASE_LOG_PATH = os.path.join(BASE_DIR, "knowledge", "case_log.jsonl")
