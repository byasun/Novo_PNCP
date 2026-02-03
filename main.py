import logging
import os
import sys
from config import LOG_LEVEL, LOG_FORMAT, LOGS_DIR

if not os.path.exists(LOGS_DIR):
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

from scheduler.job import DailyJob
from web.app import app, set_job
from storage.data_manager import DataManager

def main():
    logger.info("=" * 60)
    logger.info("Starting PNCP Editais System")
    logger.info("=" * 60)
    
    data_manager = DataManager()
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
