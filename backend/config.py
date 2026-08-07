import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Model paths — 3-class classifier: Normal / Bacterial / Viral (EfficientNet-B2 @384px)
MODEL_WEIGHTS = os.path.join(BASE_DIR, "models", "chest_xray_3class.pth")
MODEL_CLASSES = ["NORMAL", "BACTERIAL", "VIRAL"]
MODEL_INPUT_SIZE = (384, 384)

# ImageNet normalization (matches EfficientNet training)
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# LLM API config (DeepSeek V4 Flash via OpenCode Zen)
LLM_API_URL = "https://opencode.ai/zen/v1/chat/completions"
LLM_API_KEY = os.environ.get("RADIANTAI_LLM_KEY", "public")
LLM_MODEL = "deepseek-v4-flash-free"
LLM_MAX_TOKENS = 6000

# FAISS
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "knowledge", "clinical_guidelines.faiss")
FAISS_METADATA_PATH = os.path.join(BASE_DIR, "knowledge", "metadata.json")
FAISS_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
FAISS_DIMENSION = 384

# Output
OUTPUT_DIR = os.path.join(BASE_DIR, "static", "outputs")

# Validation
CONFIDENCE_THRESHOLD = 0.30  # 30% minimum to pass
MAX_RETRY_COUNT = 1

# Learning loop
CASE_LOG_PATH = os.path.join(BASE_DIR, "knowledge", "case_log.jsonl")
