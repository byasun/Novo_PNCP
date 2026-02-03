import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from services.editais_service import EditaisService
from services.itens_service import ItensService
from export.exporter import Exporter
from config import SCHEDULER_HOUR, SCHEDULER_MINUTE

logger = logging.getLogger(__name__)

class DailyJob:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.editais_service = EditaisService()
        self.itens_service = ItensService()
        self.exporter = Exporter()
        self.last_run = None
        self.is_running = False
    
    def run_daily_update(self):
        if self.is_running:
            logger.warning("Job already running, skipping...")
            return
        
        self.is_running = True
        logger.info("=" * 50)
        logger.info("Starting daily update job...")
        logger.info("=" * 50)
        
        try:
            today = datetime.now()
            data_final = today.strftime("%Y%m%d")
            data_inicial = (today - timedelta(days=15)).strftime("%Y%m%d")
            
            logger.info(f"Fetching editais from {data_inicial} to {data_final} with codigo_modalidade 6 (Pregão - Eletrônico)")
            self.editais_service.update_editais(
                data_inicial=data_inicial,
                data_final=data_final,
                codigo_modalidade=6
            )
            
            self.last_run = datetime.now()
            logger.info(f"Daily update completed at {self.last_run}")
            
        except Exception as e:
            logger.error(f"Error in daily update job: {e}")
        finally:
            self.is_running = False
    
    def start(self):
        trigger = CronTrigger(hour=SCHEDULER_HOUR, minute=SCHEDULER_MINUTE)
        self.scheduler.add_job(
            self.run_daily_update,
            trigger=trigger,
            id="daily_update",
            name="Daily PNCP Update",
            replace_existing=True
        )
        self.scheduler.start()
        logger.info(f"Scheduler started. Daily job scheduled at {SCHEDULER_HOUR:02d}:{SCHEDULER_MINUTE:02d}")
    
    def stop(self):
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
    
    def run_now_async(self):
        import threading
        if self.is_running:
            logger.warning("Job already running, cannot start another")
            return False
        thread = threading.Thread(target=self.run_daily_update, daemon=True)
        thread.start()
        logger.info("Manual trigger: update started in background thread")
        return True

    def run_incremental_update(self):
        """
        Run an incremental sync: compare remote editais (last 15 days) with local storage,
        update existing records and fetch items only for newly added editais.
        """
        if self.is_running:
            logger.warning("Job already running, skipping incremental update...")
            return

        self.is_running = True
        logger.info("Starting incremental update job...")
        try:
            today = datetime.now()
            data_final = today.strftime("%Y%m%d")
            data_inicial = (today - timedelta(days=15)).strftime("%Y%m%d")

            logger.info(f"Incremental sync: fetching editais from {data_inicial} to {data_final}")
            summary = self.editais_service.sync_editais(
                data_inicial=data_inicial,
                data_final=data_final,
                codigo_modalidade=6
            )
            logger.info(f"Incremental sync completed: {summary}")
            self.last_run = datetime.now()
        except Exception as e:
            logger.error(f"Error in incremental update job: {e}")
        finally:
            self.is_running = False

    def run_incremental_async(self):
        import threading
        if self.is_running:
            logger.warning("Job already running, cannot start incremental update")
            return False
        thread = threading.Thread(target=self.run_incremental_update, daemon=True)
        thread.start()
        logger.info("Manual trigger: incremental update started in background thread")
        return True
    
    def run_now(self):
        logger.info("Manual trigger: running update now...")
        self.run_daily_update()
    
    def get_next_run(self):
        job = self.scheduler.get_job("daily_update")
        if job:
            return job.next_run_time
        return None
    
    def get_status(self):
        next_run = self.get_next_run()
        return {
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": next_run.isoformat() if next_run else None,
            "is_running": self.is_running
        }
