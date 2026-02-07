"""Aplicação web Flask (API + SPA React)."""

from flask import Flask, jsonify, send_file, request, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
import os
import logging
from datetime import datetime, timedelta
import re
from backend.services.editais_service import EditaisService
from backend.storage.data_manager import DataManager
from backend.storage.auth_db import (
    init_db,
    get_user_by_id,
    get_user_by_username,
    get_user_by_email,
    verify_user,
    create_user,
    has_any_user,
)
from backend.config import (
    DATA_DIR,
    SECRET_KEY,
    SESSION_LIFETIME_MINUTES,
    SESSION_COOKIE_SECURE,
    SESSION_COOKIE_HTTPONLY,
    SESSION_COOKIE_SAMESITE,
    DATABASE_URL,
)
from backend.export.exporter import Exporter

logger = logging.getLogger(__name__)

WEB_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(WEB_DIR, "..", ".."))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
REACT_DIST_DIR = os.path.join(FRONTEND_DIR, "react", "dist")

app = Flask(__name__, static_folder=REACT_DIST_DIR, static_url_path="/assets")
# CORS para frontend separado (React)
allowed_origins_env = os.getenv("PNCP_FRONTEND_ORIGINS", "")
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
CORS(
    app,
    resources={
        r"/api/*": {"origins": allowed_origins},
        r"/login": {"origins": allowed_origins},
        r"/logout": {"origins": allowed_origins},
        r"/users/*": {"origins": allowed_origins},
        r"/download/*": {"origins": allowed_origins},
    },
    supports_credentials=True,
)
# Permite URLs com e sem "/" no final
app.url_map.strict_slashes = False
app.config["SECRET_KEY"] = SECRET_KEY
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=SESSION_LIFETIME_MINUTES)
app.config["SESSION_COOKIE_SECURE"] = SESSION_COOKIE_SECURE
app.config["SESSION_COOKIE_HTTPONLY"] = SESSION_COOKIE_HTTPONLY
app.config["SESSION_COOKIE_SAMESITE"] = SESSION_COOKIE_SAMESITE

csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = "spa"
login_manager.login_message = "Faça login para acessar os editais."

os.makedirs(DATA_DIR, exist_ok=True)
# Inicializa o banco de usuários
init_db(DATABASE_URL)

editais_service = EditaisService()
data_manager = DataManager()
exporter = Exporter()

daily_job = None


def validate_password_policy(password: str, confirm: str) -> str | None:
    """Valida a política de senha e retorna mensagem de erro, se houver."""
    if password != confirm:
        return "As senhas não conferem."
    if len(password) < 6:
        return "A senha deve ter no mínimo 6 caracteres."
    if not re.search(r"[A-Z]", password):
        return "A senha deve conter pelo menos uma letra maiúscula."
    if not re.search(r"[a-z]", password):
        return "A senha deve conter pelo menos uma letra minúscula."
    if not re.search(r"\d", password):
        return "A senha deve conter pelo menos um número."
    if not re.search(r"[^A-Za-z0-9]", password):
        return "A senha deve conter pelo menos um caractere especial."
    return None


def _get_request_data() -> dict:
    if request.is_json:
        return request.get_json(silent=True) or {}
    return request.form.to_dict(flat=True)


def _serve_spa():
    index_path = os.path.join(REACT_DIST_DIR, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(REACT_DIST_DIR, "index.html")
    return jsonify({
        "status": "error",
        "message": "React build not found. Execute npm run build in frontend/react."
    }), 404

def set_job(job):
    # Injeta job do scheduler para uso nas rotas
    global daily_job
    daily_job = job


@login_manager.user_loader
def load_user(user_id):
    # Carrega usuário para a sessão (Flask-Login)
    try:
        return get_user_by_id(int(user_id))
    except Exception:
        return None


@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith("/api") or request.is_json or request.accept_mimetypes.accept_json:
        return jsonify({"error": "unauthorized"}), 401
    return _serve_spa()

@app.after_request
def add_header(response):
    # Evita cache no navegador
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route("/")
def spa():
    return _serve_spa()

@app.route("/api/editais")
@login_required
def api_editais():
    # Retorna editais em JSON
    editais = editais_service.get_all_editais_local()
    return jsonify({"total": len(editais), "data": editais})


@app.route("/api/editais/<path:edital_key>")
@login_required
def api_edital_detail(edital_key):
    parts = edital_key.split("_")
    if len(parts) != 3:
        return jsonify({"error": "Edital não encontrado"}), 404
    edital = editais_service.get_edital_by_key(edital_key)
    if not edital:
        return jsonify({"error": "Edital não encontrado"}), 404
    return jsonify({"data": edital})


@app.route("/api/editais/<path:edital_key>/itens")
@login_required
def api_edital_itens(edital_key):
    parts = edital_key.split("_")
    if len(parts) != 3:
        return jsonify({"error": "Edital não encontrado"}), 404
    cnpj, ano, numero = parts
    itens = editais_service.get_itens_by_edital(cnpj, ano, numero)
    return jsonify({"total": len(itens), "data": itens})

@app.route("/api/editais/count")
@login_required
def api_editais_count():
    """Retorna apenas a contagem de editais (tempo real)."""
    editais = editais_service.get_all_editais_local()
    return jsonify({"total": len(editais)})

@app.route("/api/status")
@login_required
def api_status():
    # Status da aplicação e do scheduler
    editais = editais_service.get_all_editais_local()
    last_update = data_manager.get_last_update()
    
    user_info = {}
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
        user_info = {
            "name": getattr(current_user, 'name', None),
            "username": getattr(current_user, 'username', None),
            "email": getattr(current_user, 'email', None),
        }
    status = {
        "total_editais": len(editais),
        "last_update": datetime.fromtimestamp(last_update).isoformat() if last_update else None,
        "scheduler": daily_job.get_status() if daily_job else None,
        **user_info
    }
    return jsonify(status)

@app.route("/api/trigger-update", methods=["POST"])
@csrf.exempt
@login_required
def trigger_update():
    # Dispara atualização manual (incremental)
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
            return jsonify({
                "status": "success",
                "message": "Update started in background",
                "update_id": daily_job.current_update_id
            })
        else:
            return jsonify({"status": "error", "message": "Could not start update"}), 500
    return jsonify({"status": "error", "message": "Scheduler not available"}), 500

@app.route("/download/<filename>")
@login_required
def download_file(filename):
    # Download de arquivos CSV/XLSX exportados
    allowed_files = ["editais.csv", "editais.xlsx"]
    if filename not in allowed_files:
        return jsonify({"error": "File not found"}), 404
    # Build absolute path to data directory
    file_path = os.path.join(DATA_DIR, filename)
    try:
        # Sempre exporta/atualiza os arquivos antes de servir
        editais = data_manager.load_editais()
        exporter.export_editais(editais)
    except Exception as e:
        logger.error(f"Error generating export file {filename}: {e}")
        return jsonify({"error": "File not available yet"}), 404
    if not os.path.exists(file_path):
        return jsonify({"error": "File not available yet"}), 404
    return send_file(file_path, as_attachment=True)


@app.route("/login", methods=["GET", "POST"])
@csrf.exempt
def login():
    if request.method == "GET":
        return _serve_spa()

    if current_user.is_authenticated:
        return jsonify({"status": "success", "message": "Already authenticated"})

    if not has_any_user():
        return jsonify({"status": "error", "message": "Nenhum usuário cadastrado. Crie um usuário primeiro."}), 409

    data = _get_request_data()
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    user = verify_user(username, password)
    if user:
        from flask import session
        session.permanent = True
        login_user(user, remember=True)
        resp = jsonify({"status": "success", "message": "Login successful"})
        return resp
    return jsonify({"status": "error", "message": "Usuário ou senha inválidos."}), 401


@app.route("/logout", methods=["POST", "GET"])
@login_required
@csrf.exempt
def logout():
    logout_user()
    return jsonify({"status": "success", "message": "Logged out"})


# Rota /setup removida do frontend - criar primeiro usuário via terminal:
# python scripts/create_user.py "Admin" admin admin@email.com SenhaForte123!


@app.route("/users/new", methods=["GET", "POST"])
@csrf.exempt
def create_user_view():
    if request.method == "GET":
        return _serve_spa()

    data = _get_request_data()
    name = (data.get("name") or "").strip()
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    confirm = data.get("confirm_password") or data.get("confirm") or ""

    # Validações de campos obrigatórios
    if not name:
        return jsonify({"status": "error", "message": "Preencha o nome."}), 400
    if not username:
        return jsonify({"status": "error", "message": "Preencha o usuário."}), 400
    if not email:
        return jsonify({"status": "error", "message": "Preencha o email."}), 400
    if not password:
        return jsonify({"status": "error", "message": "Preencha a senha."}), 400

    # Validação de formato de email
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return jsonify({"status": "error", "message": "Email inválido."}), 400

    # Validação de política de senha
    policy_error = validate_password_policy(password, confirm)
    if policy_error:
        return jsonify({"status": "error", "message": policy_error}), 400

    # Verifica duplicidade de usuário e email
    if get_user_by_username(username):
        return jsonify({"status": "error", "message": "Usuário já existe."}), 409
    if get_user_by_email(email):
        return jsonify({"status": "error", "message": "Email já cadastrado."}), 409

    create_user(username=username, password=password, name=name, email=email)
    return jsonify({"status": "success", "message": "Usuário criado com sucesso."})


@app.route("/editais")
@app.route("/edital/<path:edital_key>")
def spa_routes(edital_key=None):
    return _serve_spa()


@app.route("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory(os.path.join(REACT_DIST_DIR, "assets"), filename)


@app.route("/<path:path>")
def serve_spa_fallback(path):
    full_path = os.path.join(REACT_DIST_DIR, path)
    if os.path.exists(full_path) and os.path.isfile(full_path):
        return send_from_directory(REACT_DIST_DIR, path)
    return _serve_spa()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
