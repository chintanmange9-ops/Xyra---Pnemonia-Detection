import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request
from PIL import Image

import config

app = Flask(__name__)
# Single file: 16 MB; batch folder: allow up to 100 MB total (e.g., 20 images × 5 MB)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

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
        "endpoints": ["/api/status", "/api/analyze", "/api/analyze-batch", "/api/download-report", "/api/stats"],
    })


@app.route("/api/status", methods=["GET"])
def check_status():
    p = get_pipeline()
    return jsonify({
        "running": True,
        "model_loaded": p.diagnosis.model_loaded if p else False,
        "model_version": p.diagnosis.model_version if p else "not_loaded",
        "model_classes": config.MODEL_CLASSES,
        "provider": config.LLM_PROVIDER,
        "llm_model": config.OPENROUTER_MODEL,
        "llm_configured": bool(config.OPENROUTER_API_KEY),
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
        filename = file.filename or "unknown"
        print(f"[Single] {filename} — pipeline start", flush=True)
        image_data = file.read()
        p = get_pipeline()
        result = p.run(image_data)
        if "error" in result:
            print(f"[Single] {filename} — ERROR {result['error']}", flush=True)
            return jsonify({"error": result["error"]}), 500
        print(f"[Single] {filename} — OK {result.get('prediction')} {result.get('confidence')}% ({result.get('processingTime')}s)", flush=True)
        return jsonify({"success": True, "result": result})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/analyze-batch", methods=["POST"])
def api_analyze_batch():
    """
    Batch folder upload: accepts multiple files under field 'xrays' (or repeated 'xray').
    Returns: {success: true, results: [{filename, result} or {filename, error}]}
    Each file is validated like /api/analyze; pipeline runs sequentially (RAG/LLM per image).
    """
    # Collect files: support both 'xrays' and repeated 'xray'
    files = request.files.getlist("xrays")
    if not files or files == [None] or (len(files) == 1 and files[0].filename == ""):
        files = request.files.getlist("xray")
    # Fallback: any file field
    if not files or (len(files) == 1 and files[0].filename == ""):
        # collect all uploaded files
        files = list(request.files.values())
    if not files:
        return jsonify({"error": "No files uploaded. Use field 'xrays' with multiple files."}), 400

    # Flatten in case a single FileStorage with no filename
    files = [f for f in files if f and f.filename]

    if not files:
        return jsonify({"error": "No valid files"}), 400

    # Limit safety: max 50 files per batch
    if len(files) > 50:
        return jsonify({"error": f"Too many files ({len(files)}). Max 50 per batch."}), 400

    p = get_pipeline()
    results = []
    total = len(files)
    print(f"[Batch] Received {total} files: {[f.filename for f in files[:5]]}{' ...' if total>5 else ''}", flush=True)
    for idx, f in enumerate(files, 1):
        filename = f.filename or "unknown"
        print(f"[Batch {idx}/{total}] {filename} — validating...", flush=True)
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            print(f"[Batch {idx}/{total}] {filename} — SKIP unsupported type '{ext}'", flush=True)
            results.append({"filename": filename, "error": f"Unsupported type '{ext}'"})
            continue
        try:
            image_data = f.read()
            if not image_data:
                print(f"[Batch {idx}/{total}] {filename} — SKIP empty file", flush=True)
                results.append({"filename": filename, "error": "Empty file"})
                continue
            print(f"[Batch {idx}/{total}] {filename} — pipeline start ({len(image_data)} bytes)", flush=True)
            result = p.run(image_data)
            if "error" in result:
                print(f"[Batch {idx}/{total}] {filename} — ERROR {result['error']}", flush=True)
                results.append({"filename": filename, "error": result["error"]})
            else:
                print(f"[Batch {idx}/{total}] {filename} — OK {result.get('prediction')} {result.get('confidence')}% ({result.get('processingTime')}s)", flush=True)
                result["_source_filename"] = filename
                results.append({"filename": filename, "result": result})
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[Batch {idx}/{total}] {filename} — EXCEPTION {e}", flush=True)
            results.append({"filename": filename, "error": str(e)})
    print(f"[Batch] Done {len(results)} files — ok {sum(1 for r in results if 'result' in r)} failed {sum(1 for r in results if 'error' in r)}", flush=True)

    # Summary counts
    ok = sum(1 for r in results if "result" in r)
    return jsonify({"success": True, "count": len(files), "ok": ok, "failed": len(files) - ok, "results": results})


@app.route("/api/stats", methods=["GET"])
def api_stats():
    p = get_pipeline()
    stats = p.learner.get_stats()
    return jsonify(stats)


@app.route("/api/download-report", methods=["POST", "OPTIONS"])
def api_download_report():
    if request.method == "OPTIONS":
        return "", 204

    data = request.get_json(silent=True)
    if not data or "result" not in data:
        return jsonify({"error": "No analysis result provided"}), 400

    try:
        from report_generator import generate_report
        pdf_bytes = generate_report(data["result"])
        from flask import send_file
        import io
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"Xyra_Report_{data['result'].get('case_id', 'report')}.pdf",
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("=" * 50)
    print("  LungAI Backend — Multi-Agent Pneumonia CDSS")
    print("=" * 50)
    print(f"  LLM Provider: {config.LLM_PROVIDER}  Model: {config.OPENROUTER_MODEL}")
    print(f"  LLM Configured: {bool(config.OPENROUTER_API_KEY)}")
    print(f"  Confidence Threshold: {config.CONFIDENCE_THRESHOLD}")
    print(f"  API: http://localhost:5000/api/analyze  (batch: /api/analyze-batch)")
    print("=" * 50)
    p = get_pipeline()
    import threading

    def warm_rag():
        print("[Startup] Eagerly loading RAG index...")
        ready = p.rag.warmup()
        print("[Startup] RAG index loaded" if ready else "[Startup] RAG warmup completed without local index")

    threading.Thread(target=warm_rag, name="rag-warmup", daemon=True).start()
    app.run(debug=False, host="0.0.0.0", port=5000)
