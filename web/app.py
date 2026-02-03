from flask import Flask, render_template, jsonify, send_file, request
import os
import logging
from datetime import datetime
from services.editais_service import EditaisService
from services.itens_service import ItensService
from storage.data_manager import DataManager
from config import DATA_DIR
from export.exporter import Exporter

logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates", static_folder="static")

editais_service = EditaisService()
itens_service = ItensService()
data_manager = DataManager()
exporter = Exporter()

daily_job = None

def set_job(job):
    global daily_job
    daily_job = job

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route("/")
def index():
    editais = editais_service.get_all_editais_local()
    last_update = data_manager.get_last_update()
    last_update_str = datetime.fromtimestamp(last_update).strftime("%d/%m/%Y %H:%M") if last_update else "Nunca"
    
    return render_template(
        "index.html",
        editais=editais,
        total_editais=len(editais),
        last_update=last_update_str
    )

@app.route("/edital/<path:edital_key>")
def edital_detail(edital_key):
    parts = edital_key.split("_")
    if len(parts) != 3:
        return render_template("error.html", message="Edital não encontrado"), 404
    
    cnpj, ano, numero = parts
    edital = editais_service.get_edital_by_key(edital_key)
    
    if not edital:
        return render_template("error.html", message="Edital não encontrado"), 404
    
    itens = editais_service.get_itens_by_edital(cnpj, ano, numero)
    
    return render_template(
        "edital_detail.html",
        edital=edital,
        itens=itens,
        total_itens=len(itens)
    )

@app.route("/api/editais")
def api_editais():
    editais = editais_service.get_all_editais_local()
    return jsonify({"total": len(editais), "data": editais})

@app.route("/api/editais/count")
def api_editais_count():
    """Return just the count of editais for real-time updates"""
    editais = editais_service.get_all_editais_local()
    return jsonify({"total": len(editais)})

@app.route("/api/status")
def api_status():
    editais = editais_service.get_all_editais_local()
    last_update = data_manager.get_last_update()
    
    status = {
        "total_editais": len(editais),
        "last_update": datetime.fromtimestamp(last_update).isoformat() if last_update else None,
        "scheduler": daily_job.get_status() if daily_job else None
    }
    return jsonify(status)

@app.route("/api/trigger-update", methods=["POST"])
def trigger_update():
    if daily_job:
        if daily_job.is_running:
            return jsonify({"status": "error", "message": "Update already in progress"}), 409
        # Start incremental sync by default when triggered manually
        started = False
        if hasattr(daily_job, 'run_incremental_async'):
            started = daily_job.run_incremental_async()
        else:
            started = daily_job.run_now_async()
        if started:
            return jsonify({"status": "success", "message": "Update started in background"})
        else:
            return jsonify({"status": "error", "message": "Could not start update"}), 500
    return jsonify({"status": "error", "message": "Scheduler not available"}), 500

@app.route("/download/<filename>")
def download_file(filename):
    allowed_files = ["editais.csv", "editais.xlsx"]
    if filename not in allowed_files:
        return jsonify({"error": "File not found"}), 404
    # Build absolute path to data directory (project root / DATA_DIR)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    file_path = os.path.join(project_root, DATA_DIR, filename)
    # If file does not exist, try to generate it from current data
    if not os.path.exists(file_path):
        try:
            # Export editais to requested format
            editais = data_manager.load_editais()
            exporter.export_editais(editais)
        except Exception as e:
            logger.error(f"Error generating export file {filename}: {e}")
    if not os.path.exists(file_path):
        return jsonify({"error": "File not available yet"}), 404
    
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
