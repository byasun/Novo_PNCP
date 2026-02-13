"""Ponto de entrada da aplicação PNCP (editais)."""

import atexit
import logging
import os
import signal
import sys
import uuid

# Permite executar como script dentro de backend/ (python main.py)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.config import LOG_LEVEL, LOG_FORMAT, LOGS_DIR

if not os.path.exists(LOGS_DIR):
    # Garante a pasta de logs
    os.makedirs(LOGS_DIR)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(LOGS_DIR, "app.log"))
    ]
)

logger = logging.getLogger(__name__)

from backend.scheduler.job import DailyJob
from backend.web.app import app, set_job
from backend.storage.data_manager import DataManager


def _invalidate_all_sessions():
    """Invalida todas as sessões ativas ao encerrar o sistema.
    
    Isso é feito alterando a SECRET_KEY, o que torna todos os cookies
    de sessão existentes inválidos quando o servidor reiniciar.
    """
    logger.info("Invalidating all active sessions (server shutdown)...")
    # Gera nova SECRET_KEY para invalidar sessões existentes
    app.config["SECRET_KEY"] = str(uuid.uuid4())
    logger.info("All sessions invalidated.")


def _shutdown_handler(signum, frame):
    """Handler para sinais de encerramento (SIGINT, SIGTERM)."""
    logger.info("=" * 60)
    logger.info("Received shutdown signal. Cleaning up...")
    logger.info("=" * 60)
    _invalidate_all_sessions()
    sys.exit(0)


def main():
    # Registra handlers de encerramento
    signal.signal(signal.SIGINT, _shutdown_handler)
    signal.signal(signal.SIGTERM, _shutdown_handler)
    atexit.register(_invalidate_all_sessions)
    
    # Log de inicialização
    logger.info("=" * 60)
    logger.info("Starting PNCP Editais System")
    logger.info("=" * 60)
    
    # Gera SECRET_KEY única para esta instância (invalida sessões anteriores)
    runtime_secret = f"{app.config['SECRET_KEY']}_{uuid.uuid4()}"
    app.config["SECRET_KEY"] = runtime_secret
    logger.info("New session secret generated (previous sessions invalidated)")
    
    # Atualização automática se for a primeira execução do dia
    try:
        from backend.scripts.update_if_first_time_today import update_if_first_time_today
        update_if_first_time_today()
    except Exception as e:
        logger.warning(f"Falha ao executar atualização automática diária: {e}")

    data_manager = DataManager()
    # Carrega editais locais (se existirem)
    editais = data_manager.load_editais()
    logger.info(f"Loaded {len(editais)} editais from local storage")
    
    daily_job = DailyJob()
    set_job(daily_job)
    
    # Dispara atualização ao iniciar se não houver dados
    if len(editais) == 0:
        logger.info("No editais found. Triggering initial update...")
        daily_job.run_now()
    
    daily_job.start()
    
    logger.info("Starting Flask web server on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    main()
