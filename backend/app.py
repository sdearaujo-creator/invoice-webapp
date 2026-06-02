"""
Invoice Upload Web App — Flask backend.

Routes:
  GET  /              -> the upload page (served from ../frontend)
  POST /api/process   -> accept a PDF, return extracted invoice data as JSON
  POST /api/save      -> accept (edited) invoice data, save it to Airtable
"""

import os
import sys
import tempfile

# Make this file's own folder importable. Locally we run from backend/, so the
# sibling modules are found automatically; on Vercel the function runs from the
# project root, so we add backend/ to the path explicitly.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

# Load .env BEFORE importing airtable_client (it reads env vars at import time).
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import pdf_processor
import airtable_client

FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")
)

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)  # harmless here; useful if the frontend is ever hosted separately
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # reject uploads over 5 MB


# --- Error handlers -------------------------------------------------------
@app.errorhandler(413)
def file_too_large(e):
    # Flask blocks oversized uploads with a 413 (HTML by default). Return JSON
    # so the frontend shows a clear message instead of "Could not reach the server."
    return jsonify({"error": "File too large. Please upload a PDF under 5 MB."}), 413


# --- Frontend -------------------------------------------------------------
@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


# --- API: extract data from an uploaded PDF -------------------------------
@app.route("/api/process", methods=["POST"])
def process():
    if "file" not in request.files:
        return jsonify({"error": "No file was uploaded."}), 400

    upload = request.files["file"]
    if upload.filename == "":
        return jsonify({"error": "No file selected."}), 400
    if not upload.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Please upload a PDF file."}), 400

    # Save to a temp file, extract, then always clean up.
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    try:
        upload.save(tmp.name)
        tmp.close()
        data = pdf_processor.process_pdf(tmp.name)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"Could not read this PDF: {e}"}), 500
    finally:
        if os.path.exists(tmp.name):
            os.remove(tmp.name)


# --- API: save (possibly edited) data to Airtable -------------------------
@app.route("/api/save", methods=["POST"])
def save():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No invoice data received."}), 400

    ok, result = airtable_client.save_invoice(data)
    if ok:
        return jsonify({"success": True, "airtable_record_id": result})
    return jsonify({"success": False, "error": result}), 502


if __name__ == "__main__":
    # Local development server.
    app.run(host="127.0.0.1", port=5000, debug=True)
