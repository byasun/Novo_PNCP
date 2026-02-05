"""Ponto de entrada da aplicação PNCP (editais)."""

import logging
import os
import sys

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

def main():
    # Log de inicialização
    logger.info("=" * 60)
    logger.info("Starting PNCP Editais System")
    logger.info("=" * 60)
    
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
