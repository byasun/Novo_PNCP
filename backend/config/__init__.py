"""
Módulo de configuração do sistema PNCP.

Este arquivo reexporta variáveis e funções de configuração do settings.py para manter compatibilidade retroativa e facilitar o acesso centralizado às configurações globais do sistema.
"""

# Reexporta variáveis de configuração para outros módulos
from .settings import (
    API_BASE_URL,
    API_ITEMS_BASE_URL,
    PAGE_SIZE,
    MAX_RETRIES,
    RETRY_DELAY,
    RETRY_BACKOFF_MULTIPLIER,
    ITEMS_FETCH_THREADS,
    ITEMS_FETCH_DELAY_PER_THREAD,
    ITEMS_FETCH_CHECKPOINT,
    ITEMS_SKIP_EXISTING,
    DATA_DIR,
    LOGS_DIR,
    EXPORT_DIR,
    EDITAIS_CHECKPOINT_FILE,
    SCHEDULER_HOUR,
    SCHEDULER_MINUTE,
    LOG_LEVEL,
    LOG_FORMAT,
    SECRET_KEY,
    SESSION_LIFETIME_MINUTES,
    SESSION_COOKIE_SECURE,
    SESSION_COOKIE_HTTPONLY,
    SESSION_COOKIE_SAMESITE,
    DATABASE_URL,
    # Funções de controle de cancelamento (Ctrl+C)
    request_cancel,
    reset_cancel,
    is_cancelled,
)

__all__ = [
    "API_BASE_URL",
    "API_ITEMS_BASE_URL",
    "PAGE_SIZE",
    "MAX_RETRIES",
    "RETRY_DELAY",
    "RETRY_BACKOFF_MULTIPLIER",
    "ITEMS_FETCH_THREADS",
    "ITEMS_FETCH_DELAY_PER_THREAD",
    "ITEMS_FETCH_CHECKPOINT",
    "ITEMS_SKIP_EXISTING",
    "DATA_DIR",
    "LOGS_DIR",
    "EXPORT_DIR",
    "EDITAIS_CHECKPOINT_FILE",
    "SCHEDULER_HOUR",
    "SCHEDULER_MINUTE",
    "LOG_LEVEL",
    "LOG_FORMAT",
    "SECRET_KEY",
    "SESSION_LIFETIME_MINUTES",
    "SESSION_COOKIE_SECURE",
    "SESSION_COOKIE_HTTPONLY",
    "SESSION_COOKIE_SAMESITE",
    "DATABASE_URL",
    # Funções de controle de cancelamento
    "request_cancel",
    "reset_cancel",
    "is_cancelled",
]
