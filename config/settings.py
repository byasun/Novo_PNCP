import os

# Base URL for fetching editais (contratações/publicação)
API_BASE_URL = "https://pncp.gov.br/api/consulta/v1"

# Base URL for fetching items (itens by orgao/compras)
API_ITEMS_BASE_URL = "https://pncp.gov.br/api/pncp/v1"

PAGE_SIZE = 50
MAX_RETRIES = 3
RETRY_DELAY = 5

# Parallel fetching configuration
ITEMS_FETCH_THREADS = 5  # Number of parallel threads for item fetching
ITEMS_FETCH_DELAY_PER_THREAD = 0.1  # Delay (seconds) between requests per thread to avoid rate limiting
ITEMS_FETCH_CHECKPOINT = 100  # Save progress every N editais processed

DATA_DIR = "data"
LOGS_DIR = "logs"
EXPORT_DIR = "data"

# Checkpoint metadata files
EDITAIS_CHECKPOINT_FILE = "data/.editais_checkpoint.json"  # Stores last successful checkpoint info for editais

SCHEDULER_HOUR = 3
SCHEDULER_MINUTE = 0

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
