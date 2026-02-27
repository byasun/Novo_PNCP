"""
Ponto de entrada principal da aplicação PNCP (editais).

Este arquivo inicializa o backend, configura logging, executa rotinas de limpeza e atualização de dados, e inicia o servidor web Flask.
Também garante a invalidação de sessões antigas e o controle de jobs agendados.
"""

import atexit
import logging
import os
import signal
import sys
import uuid

# Ajusta sys.path para garantir importação do pacote backend ao rodar diretamente
import sys
import os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


# Importa configurações antes de configurar o logger
from backend.config import LOG_LEVEL, LOG_FORMAT, LOGS_DIR

# Configura logger global
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# Importa objetos essenciais do backend
from backend.web.app import app, set_job
from backend.storage.data_manager import DataManager
from backend.scheduler.job import DailyJob

# Handler para sinais de encerramento (Ctrl+C, SIGTERM)

def _shutdown_handler(signum, frame):
    """Handler para sinais de encerramento (Ctrl+C, SIGTERM)."""
    from backend.config import request_cancel
    logger.warning(f"Recebido sinal {signum}. Encerrando aplicação...")
    request_cancel()
    sys.exit(0)

# Função para invalidar todas as sessões (executada ao sair)

def _invalidate_all_sessions():
    """Função para invalidar todas as sessões (executada ao sair)."""
    logger.info("Invalidando todas as sessões (logout global).")
    # Aqui você pode adicionar lógica extra se necessário

# Permite executar como script dentro de backend/ (python main.py)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


# Garante a pasta de logs
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

def main():
    """
    Função principal que inicializa o backend, executa rotinas de limpeza, atualização e inicia o servidor web.
    """
    # Registra handlers de encerramento para garantir limpeza de sessões
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

    # 1. (Removido) Limpeza automática de editais/itens expirados
    # (A remoção automática foi desativada para evitar perda de dados)

    # 2. Verifica se é a primeira inicialização do dia
    try:
        from backend.scripts.fetch.update_if_first_time_today import already_updated_today, update_if_first_time_today
        if not already_updated_today():
            # 3. Se for a primeira inicialização, atualiza editais/itens
            update_if_first_time_today()
        else:
            # 4. Se não for, pula atualização
            logger.info("Atualização de editais/itens já foi feita hoje. Pulando...")
    except Exception as e:
        logger.warning(f"Falha ao verificar/atualizar editais e itens: {e}")

    data_manager = DataManager()
    # Carrega editais locais (se existirem)
    editais = data_manager.load_editais()
    logger.info(f"Loaded {len(editais)} editais from local storage")

    # Garante que todos os itens dos editais estejam salvos
    from backend.services.editais_service import EditaisService
    editais_service = EditaisService()
    logger.info("Buscando e salvando itens para todos os editais...")
    editais_service.fetch_itens_for_all_editais(editais, skip_existing=False)
    logger.info("Itens de todos os editais garantidos no armazenamento local.")

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
