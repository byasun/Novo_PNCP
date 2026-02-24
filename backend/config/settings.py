"""
Configurações globais do sistema PNCP.

Este módulo centraliza todas as configurações do sistema, incluindo:
- URLs de APIs externas
- Parâmetros de coleta de dados
- Agendamento de tarefas
- Configurações de logging
- Segurança e variáveis de ambiente

As variáveis são carregadas do arquivo .env e expostas para uso em todo o backend.
"""

import os
import threading
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

load_dotenv(os.path.join(BASE_DIR, ".env"))


def _get_env(name: str, default: str | None = None, required: bool = False) -> str | None:
	"""
	Recupera o valor de uma variável de ambiente.
	Se não existir, retorna o valor padrão ou lança erro se for obrigatória.
	"""
	value = os.getenv(name, default)
	if required and not value:
		raise RuntimeError(f"Variável de ambiente obrigatória não encontrada: {name}")
	return value


# =============================================================================
# FLAG DE CANCELAMENTO GLOBAL (para interrupção via Ctrl+C)
# Utilizada para sinalizar cancelamento de operações longas (ex: coleta de dados)
# =============================================================================
_cancel_flag = threading.Event()

def request_cancel():
	"""
	Sinaliza para cancelar operações em andamento (uso: handler de Ctrl+C).
	"""
	_cancel_flag.set()

def reset_cancel():
	"""
	Reseta a flag de cancelamento (chamar no início de operações longas).
	"""
	_cancel_flag.clear()

def is_cancelled():
	"""
	Verifica se foi solicitado cancelamento global (Ctrl+C).
	"""
	return _cancel_flag.is_set()


# =============================================================================
# CONFIGURAÇÕES DE API
# =============================================================================

# URL base para buscar editais (contratações/publicação)
API_BASE_URL = _get_env("API_BASE_URL", required=True)

# URL base para buscar itens (itens por órgão/compras)
API_ITEMS_BASE_URL = _get_env("API_ITEMS_BASE_URL", required=True)

# Paginação e tentativas (configuráveis via .env)
PAGE_SIZE = 50
MAX_RETRIES = int(_get_env("MAX_RETRIES", "5"))  # Número de tentativas antes de desistir
RETRY_DELAY = float(_get_env("RETRY_DELAY", "5"))  # Delay inicial entre tentativas (segundos)
RETRY_BACKOFF_MULTIPLIER = float(_get_env("RETRY_BACKOFF_MULTIPLIER", "2.0"))  # Multiplicador exponencial para backoff

# Configuração de busca paralela de itens (configuráveis via .env)
ITEMS_FETCH_THREADS = int(_get_env("ITEMS_FETCH_THREADS", "3"))  # Número de threads paralelas (reduza se tiver muitos 429)
ITEMS_FETCH_DELAY_PER_THREAD = float(_get_env("ITEMS_FETCH_DELAY", "0.5"))  # Delay por thread para evitar rate limit
ITEMS_FETCH_CHECKPOINT = 100  # Salvar progresso a cada N editais
ITEMS_SKIP_EXISTING = _get_env("ITEMS_SKIP_EXISTING", "true").lower() in ("true", "1", "yes")  # Pular editais com itens já salvos

# Pastas padrão (paths absolutos)
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
EXPORT_DIR = DATA_DIR

# Arquivo de checkpoint (metadados de progresso)
EDITAIS_CHECKPOINT_FILE = os.path.join(DATA_DIR, ".editais_checkpoint.json")

# Horário padrão do agendador
SCHEDULER_HOUR = 3
SCHEDULER_MINUTE = 0

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Segurança / Auth
SECRET_KEY = _get_env("PNCP_SECRET_KEY", "change-me-in-production")
SESSION_LIFETIME_MINUTES = int(os.getenv("PNCP_SESSION_LIFETIME_MINUTES", "720"))

# Cookies de sessão
# Em produção, use HTTPS e SESSION_COOKIE_SECURE=True
SESSION_COOKIE_SECURE = os.getenv("PNCP_SESSION_COOKIE_SECURE", "false").lower() == "true"
SESSION_COOKIE_HTTPONLY = os.getenv("PNCP_SESSION_COOKIE_HTTPONLY", "true").lower() == "true"
SESSION_COOKIE_SAMESITE = os.getenv("PNCP_SESSION_COOKIE_SAMESITE", "Lax")

# Banco de dados (usuários)
# Padrão: SQLite em data/users.db
DATABASE_URL = _get_env("PNCP_DATABASE_URL", required=True)

def _normalize_sqlite_url(url: str) -> str:
	# Se for SQLite com caminho relativo, resolve para BASE_DIR
	if not url.startswith("sqlite:///"):
		return url
	path = url.replace("sqlite:///", "", 1)
	# Windows: caminho absoluto tem letra de drive, ex: C:/...
	if os.path.isabs(path) or (len(path) >= 2 and path[1] == ":"):
		return url
	abs_path = os.path.join(BASE_DIR, path)
	# Normaliza para barras '/' exigidas pelo SQLAlchemy
	return f"sqlite:///{abs_path.replace(os.sep, '/')}"

DATABASE_URL = _normalize_sqlite_url(DATABASE_URL)
