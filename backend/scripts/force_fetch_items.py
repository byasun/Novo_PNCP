"""Força a coleta de itens para todos os editais salvos localmente."""
import logging
import os
import sys
from datetime import datetime

# Adiciona a pasta raiz ao PATH para permitir imports do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import LOG_LEVEL, LOG_FORMAT, LOGS_DIR

if not os.path.exists(LOGS_DIR):
    # Garante a pasta de logs
    os.makedirs(LOGS_DIR)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(LOGS_DIR, "fetch_items.log"))
    ]
)

logger = logging.getLogger(__name__)

from backend.services.editais_service import EditaisService
from backend.storage.data_manager import DataManager
import time


def main():
    # Cabeçalho de execução
    logger.info("=" * 70)
    logger.info("FORCING ITEM FETCH FOR ALL EDITAIS")
    logger.info("=" * 70)
    
    data_manager = DataManager()
    editais_service = EditaisService()
    
    # Load all editais from storage
    editais = data_manager.load_editais()
    logger.info(f"Loaded {len(editais)} editais from local storage")
    
    if not editais:
        logger.warning("No editais found in storage. Run main.py first to fetch editais.")
        return
    
    # Force fetch items for all editais
    start_time = datetime.now()
    logger.info(f"Starting item fetch at {start_time}...")
    
    try:
        all_itens = editais_service.fetch_itens_for_all_editais(editais)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 70)
        logger.info(f"ITEM FETCH COMPLETED")
        logger.info(f"Total editais processed: {len(editais)}")
        logger.info(f"Total items fetched: {len(all_itens)}")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info("=" * 70)
        
        # Show sample
        if all_itens:
            logger.info(f"\nSample items (first 5):")
            for i, item in enumerate(all_itens[:5], start=1):
                logger.info(f"  {i}. {item.get('descricao', 'N/A')[:60]}... (edital: {item.get('edital_cnpj')}/{item.get('edital_ano')}/{item.get('edital_numero')})")
        
    except Exception as e:
        logger.exception(f"Error during item fetch: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
