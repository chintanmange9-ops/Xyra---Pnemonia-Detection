import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request
from PIL import Image

import config

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB upload limit

pipeline = None


def get_pipeline():
    global pipeline
    if pipeline is None:
        from pipeline.orchestrator import PipelineOrchestrator
        pipeline = PipelineOrchestrator()
    return pipeline


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/")
def index():
    return jsonify({
        "service": "LungAI Backend",
        "status": "running",
        "frontend": "http://localhost:5173",
        "endpoints": ["/api/status", "/api/analyze", "/api/stats"],
    })


@app.route("/api/status", methods=["GET"])
def check_status():
    p = get_pipeline()
    return jsonify({
        "running": True,
        "model_loaded": p.diagnosis.model_loaded if p else False,
        "model_version": p.diagnosis.model_version if p else "not_loaded",
        "model_classes": config.MODEL_CLASSES,
        "provider": config.LLM_MODEL,
        "confidence_threshold": config.CONFIDENCE_THRESHOLD,
    })


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    if "xray" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["xray"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

    try:
        image_data = file.read()
        p = get_pipeline()
        result = p.run(image_data)

        if "error" in result:
            return jsonify({"error": result["error"]}), 500

        return jsonify({"success": True, "result": result})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/stats", methods=["GET"])
def api_stats():
    p = get_pipeline()
    stats = p.learner.get_stats()
    return jsonify(stats)


if __name__ == "__main__":
    print("=" * 50)
    print("  LungAI Backend — Multi-Agent Pneumonia CDSS")
    print("=" * 50)
    print(f"  LLM Model: {config.LLM_MODEL}")
    print(f"  Confidence Threshold: {config.CONFIDENCE_THRESHOLD}")
    print(f"  API: http://localhost:5000/api/analyze")
    print("=" * 50)
    p = get_pipeline()
    import threading
    threading.Thread(target=lambda: (print("[Startup] Eagerly loading RAG index..."), p.rag._load_or_build_index(), setattr(p.rag, '_initialized', True), print("[Startup] RAG index loaded")), daemon=True).start()
    app.run(debug=False, host="0.0.0.0", port=5000)
