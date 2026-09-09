"""
app.py — CVTeX Bulk Generator Flask Application
"""

import csv
import io
import json
import threading
import uuid
from pathlib import Path

from flask import (
    Flask, render_template, request, jsonify,
    Response, send_file, stream_with_context
)

from kb_parser   import load_kb
from rule_engine import build_cv_data
from llm_adapter import generate_profil, generate_lettre, current_french_date
from tex_generator import render_cv, render_lettre
from compiler    import compile_offer

app = Flask(__name__)
app.secret_key = "cvtex-bulk-generator"

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# ---------------------------------------------------------------------------
# In-memory job store  { job_id: { offer, status, cv_data, texts, result } }
# ---------------------------------------------------------------------------
_jobs: dict[str, dict] = {}
_kb = None  # loaded once on first request


def get_kb():
    global _kb
    if _kb is None:
        _kb = load_kb()
    return _kb


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload-csv", methods=["POST"])
def upload_csv():
    """Parse uploaded CSV and return list of offers."""
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    content = file.read().decode("utf-8-sig")  # handle BOM
    reader  = csv.DictReader(io.StringIO(content))

    offers = []
    for row in reader:
        offer = {
            "company":         row.get("company", "").strip(),
            "job_title":       row.get("job_title", "").strip(),
            "job_description": row.get("job_description", "").strip(),
            "keywords":        row.get("keywords", "").strip(),
        }
        if offer["company"] and offer["job_title"]:
            offers.append(offer)

    return jsonify({"offers": offers})


@app.route("/generate", methods=["POST"])
def generate():
    """
    Accept a list of offers (from CSV or manual table).
    Spawn a background thread per offer to run KB + rules + LLM.
    Return job_ids immediately; client polls /stage1/<job_id>.
    """
    body   = request.get_json(force=True)
    offers = body.get("offers", [])
    kb     = get_kb()

    job_ids = []
    for offer in offers:
        job_id = str(uuid.uuid4())[:8]
        _jobs[job_id] = {
            "offer":   offer,
            "status":  "pending",
            "cv_data": None,
            "profil":  None,
            "lettre":  None,
            "result":  None,
            "error":   None,
        }
        job_ids.append(job_id)
        t = threading.Thread(target=_generate_job, args=(job_id, offer, kb), daemon=True)
        t.start()

    return jsonify({"job_ids": job_ids})


def _generate_job(job_id: str, offer: dict, kb: dict):
    """Background worker: rule engine + LLM generation for one offer."""
    job = _jobs[job_id]
    try:
        job["status"] = "generating"
        cv_data = build_cv_data(offer, kb)
        profil  = generate_profil(offer, cv_data)
        lettre  = generate_lettre(offer, cv_data)
        job["cv_data"] = cv_data
        job["profil"]  = profil
        job["lettre"]  = lettre
        job["status"]  = "ready"
    except Exception as e:
        job["status"] = "error"
        job["error"]  = str(e)


@app.route("/status/<job_id>")
def job_status(job_id: str):
    """Return current status of a job."""
    job = _jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify({
        "status":  job["status"],
        "company": job["offer"].get("company", ""),
        "error":   job.get("error", ""),
    })


@app.route("/stage1/<job_id>")
def stage1_get(job_id: str):
    """Return generated texts for Stage 1 review."""
    job = _jobs.get(job_id)
    if not job or job["status"] not in ("ready", "compiled"):
        return jsonify({"error": "Not ready"}), 404

    cv_data = job["cv_data"]
    return jsonify({
        "job_id":    job_id,
        "company":   job["offer"].get("company", ""),
        "job_title": job["offer"].get("job_title", ""),
        "profil":    job["profil"],
        "lettre":    job["lettre"],
        "projects":  [{"title": p["title"], "selected": True} for p in cv_data["projects"]],
        "certifs":   [{"title": c["title"], "selected": True} for c in cv_data["certifs"]],
    })


@app.route("/stage1/approve/<job_id>", methods=["POST"])
def stage1_approve(job_id: str):
    """
    Accept (possibly edited) texts from Stage 1.
    Trigger pdflatex compilation in background.
    """
    job = _jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    body = request.get_json(force=True)
    job["profil"]  = body.get("profil",  job["profil"])
    job["lettre"]  = body.get("lettre",  job["lettre"])

    # Apply user selection of projects / certifs
    selected_projects = set(body.get("selected_projects", []))
    selected_certifs  = set(body.get("selected_certifs",  []))

    cv_data = job["cv_data"]
    if selected_projects:
        cv_data["projects"] = [p for p in cv_data["projects"] if p["title"] in selected_projects]
    if selected_certifs:
        cv_data["certifs"]  = [c for c in cv_data["certifs"]  if c["title"] in selected_certifs]

    job["status"] = "compiling"
    t = threading.Thread(target=_compile_job, args=(job_id,), daemon=True)
    t.start()

    return jsonify({"status": "compiling"})


def _compile_job(job_id: str):
    """Background worker: render LaTeX and compile to PDF."""
    job    = _jobs[job_id]
    cv_data = job["cv_data"]
    offer   = job["offer"]
    try:
        issue_date = current_french_date()
        cv_tex     = render_cv(cv_data, job["profil"])
        lettre_tex = render_lettre(cv_data, job["lettre"], issue_date)
        result     = compile_offer(job_id, offer["company"], cv_tex, lettre_tex)
        job["result"] = result
        job["status"] = "compiled" if result["success"] else "error"
        if not result["success"]:
            job["error"] = result.get("error", "Compilation failed")
    except Exception as e:
        job["status"] = "error"
        job["error"]  = str(e)


@app.route("/stage1/reject/<job_id>", methods=["POST"])
def stage1_reject(job_id: str):
    job = _jobs.get(job_id)
    if job:
        job["status"] = "rejected"
    return jsonify({"status": "rejected"})


@app.route("/stage2/<job_id>")
def stage2_get(job_id: str):
    """Return compiled PDF paths and 1-page check results for Stage 2."""
    job = _jobs.get(job_id)
    if not job or job["status"] != "compiled":
        return jsonify({"error": "Not compiled yet"}), 404

    result = job["result"]
    folder = Path(result["folder"])

    return jsonify({
        "job_id":    job_id,
        "company":   job["offer"].get("company", ""),
        "folder":    result["folder"],
        "cv_pages":  result.get("cv_pages", -1),
        "overflow":  result.get("overflow", False),
        "cv_url":    f"/pdf/{job_id}/cv",
        "lettre_url": f"/pdf/{job_id}/lettre",
    })


@app.route("/pdf/<job_id>/<doc_type>")
def serve_pdf(job_id: str, doc_type: str):
    """Serve compiled PDF for inline preview."""
    job = _jobs.get(job_id)
    if not job or not job.get("result"):
        return "Not found", 404

    folder = Path(job["result"]["folder"])
    if doc_type == "cv":
        path = folder / "CV_Achraf_Izelmadene.pdf"
    else:
        path = folder / "Lettre_Achraf_Izelmadene.pdf"

    if not path.exists():
        return "PDF not found", 404

    return send_file(str(path), mimetype="application/pdf")


@app.route("/stage2/save/<job_id>", methods=["POST"])
def stage2_save(job_id: str):
    """Files already live in offres/ — mark job as saved."""
    job = _jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    job["status"] = "saved"
    return jsonify({"status": "saved", "folder": job["result"]["folder"]})


@app.route("/stage2/save-all", methods=["POST"])
def stage2_save_all():
    """Mark all compiled jobs as saved."""
    saved = []
    for job_id, job in _jobs.items():
        if job["status"] == "compiled":
            job["status"] = "saved"
            saved.append(job_id)
    return jsonify({"saved": saved})


@app.route("/stage1/regenerate/<job_id>", methods=["POST"])
def stage1_regenerate(job_id: str):
    """Re-run LLM generation for a single job."""
    job = _jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    kb = get_kb()
    job["status"] = "pending"
    t = threading.Thread(target=_generate_job, args=(job_id, job["offer"], kb), daemon=True)
    t.start()
    return jsonify({"status": "pending"})


@app.route("/jobs")
def list_jobs():
    """Return summary of all current jobs."""
    return jsonify({
        jid: {
            "company":  j["offer"].get("company", ""),
            "status":   j["status"],
            "overflow": j.get("result", {}).get("overflow", False) if j.get("result") else False,
        }
        for jid, j in _jobs.items()
    })


@app.route("/jobs/clear", methods=["POST"])
def clear_jobs():
    """Clear all job state (start fresh)."""
    _jobs.clear()
    return jsonify({"cleared": True})


if __name__ == "__main__":
    app.run(debug=True, port=5000, threaded=True)
