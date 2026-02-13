"""Busca editais "A Receber/Recebendo Proposta" publicados ou atualizados nos últimos 15 dias."""

import logging
import os
import sys
import signal
from datetime import datetime, timedelta
import argparse

# Adiciona a pasta raiz (Novo_PNCP) ao PATH para permitir imports do projeto
# __file__ = scripts/fetch/fetch_recent_editais.py -> dirname = fetch -> dirname = scripts -> dirname = backend -> dirname = Novo_PNCP
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.config import LOG_LEVEL, LOG_FORMAT, LOGS_DIR, request_cancel

if not os.path.exists(LOGS_DIR):
    # Garante a pasta de logs
    os.makedirs(LOGS_DIR)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(LOGS_DIR, "fetch_recent_editais.log"))
    ]
)

logger = logging.getLogger(__name__)

from backend.services.editais_service import EditaisService
from backend.storage.data_manager import DataManager


def main(days=15, fetch_items=True):
    """
    Busca editais dos últimos N dias que estão A Receber/Recebendo Proposta.
    
    Args:
        days (int): Número de dias para retrospecção (padrão: 15)
        fetch_items (bool): Se True, também busca itens para os editais (padrão: True)
    
    Returns:
        int: Código de saída (0 = sucesso, 1 = erro)
    """
    
    # Cabeçalho de execução
    logger.info("=" * 70)
    logger.info("FETCHING RECENT EDITAIS (A Receber/Recebendo Proposta)")
    logger.info("=" * 70)
    
    logger.info(f"Filter: Only editais published in last {days} days (client-side filter)")
    logger.info(f"Endpoint: /contratacoes/proposta (recebimento de propostas aberto)")
    logger.info(f"Fetching: ALL editais from API (no dataInicial limit)")
    
    # IMPORTANT: dataFinal for /contratacoes/proposta endpoint means the MAX date
    # for proposal reception period, NOT the search date. Use end of 2026
    # to get ALL editais that are currently open for receiving proposals.
    data_final_str = "20261231"  # December 31, 2026 - includes all open editais
    
    logger.info(f"API dataFinal: {data_final_str} (end of 2026 to include all open proposals)")
    
    editais_service = EditaisService()
    data_manager = DataManager()
    
    # Busca editais recentes
    start_time = datetime.now()
    logger.info(f"Starting edital fetch at {start_time}...")
    
    try:
        # Busca editais da API com modalidade 6 (Pregão Eletrônico)
        # O filtro por dataPublicacaoPncp é aplicado automaticamente no cliente
        recent_editais = editais_service.fetch_all_editais(
            data_inicial=None,          # No initial date limit
            data_final=data_final_str,  # End of 2026 (required parameter)
            codigo_modalidade=6,        # 6 = Pregão Eletrônico
            filter_by_publication_date=True,  # ✅ Filtra por dataPublicacaoPncp no cliente
            days_publication=days  # Client-side filter: last N days
        )
        
        logger.info(f"Fetched {len(recent_editais)} editais after publication date filter (client-side)")
        
        if not recent_editais:
            logger.warning(f"No editais found with publication date in last {days} days")
            logger.info("=" * 70)
            return 0
        
        # Salva editais
        try:
            editais_service.save_editais(recent_editais)
            logger.info(f"Saved {len(recent_editais)} editais to local storage")
        except Exception as e:
            logger.error(f"Error saving editais: {e}")
            return 1
        
        # Estatísticas
        logger.info("")
        logger.info(f"Recent editais summary:")
        logger.info(f"  Total fetchad: {len(recent_editais)}")
        
        # Conta por modalidade (se disponível)
        modalidades = {}
        for edital in recent_editais:
            modalidade = edital.get("modalidade", {})
            if isinstance(modalidade, dict):
                mod_nome = modalidade.get("label", "Unknown")
            else:
                mod_nome = str(modalidade)
            
            if mod_nome not in modalidades:
                modalidades[mod_nome] = 0
            modalidades[mod_nome] += 1
        
        for mod_nome, count in sorted(modalidades.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  - {mod_nome}: {count}")
        
        # Mostra amostra
        logger.info(f"\nSample editais (first 5):")
        for i, edital in enumerate(recent_editais[:5], start=1):
            cnpj = edital.get("orgaoEntidade", {}).get("cnpj") or edital.get("cnpjOrgao", "N/A")
            numero = edital.get("numeroCompra") or edital.get("numero", "N/A")
            ano = edital.get("anoCompra") or edital.get("ano", "N/A")
            descricao = edital.get("descricao", "N/A")[:60]
            logger.info(f"  {i}. {descricao}... (CNPJ: {cnpj}, {ano}/{numero})")
        
        # Opcionalmente busca itens para os editais
        if fetch_items:
            logger.info("")
            logger.info("=" * 70)
            logger.info("FETCHING ITEMS FOR RECENT EDITAIS")
            logger.info("=" * 70)
            
            items_start_time = datetime.now()
            logger.info(f"Starting item fetch at {items_start_time}...")
            
            try:
                all_itens = editais_service.fetch_itens_for_all_editais(recent_editais)
                items_end_time = datetime.now()
                items_duration = (items_end_time - items_start_time).total_seconds()
                
                logger.info(f"Item fetch completed in {items_duration:.2f} seconds")
                logger.info(f"Total items fetched: {len(all_itens)}")
                
                if all_itens:
                    logger.info(f"Sample items (first 5):")
                    for i, item in enumerate(all_itens[:5], start=1):
                        desc = item.get('descricao', 'N/A')[:60]
                        logger.info(f"  {i}. {desc}... (edital: {item.get('edital_cnpj')}/{item.get('edital_ano')}/{item.get('edital_numero')})")
                
            except Exception as e:
                logger.error(f"Error during item fetch: {e}")
                # Não retorna erro (itens são opcionais neste script)
        
        # Finalização
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("")
        logger.info("=" * 70)
        logger.info(f"FETCH COMPLETED SUCCESSFULLY")
        logger.info(f"Total duration: {duration:.2f} seconds")
        logger.info("=" * 70)
        
        return 0
        
    except Exception as e:
        logger.exception(f"Error during fetch: {e}")
        logger.info("=" * 70)
        return 1


def signal_handler(signum, frame):
    """Handler para Ctrl+C - sinaliza cancelamento e sai graciosamente."""
    print("\n\n⚠️  Interrupção solicitada (Ctrl+C). Finalizando...")
    request_cancel()
    sys.exit(0)


if __name__ == "__main__":
    # Registra handler para Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    parser = argparse.ArgumentParser(
        description='Busca editais "A Receber/Recebendo Proposta" dos últimos N dias'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=15,
        help='Número de dias para retrospecção (padrão: 15)'
    )
    parser.add_argument(
        '--no-items',
        action='store_true',
        help='Não busca itens para os editais (apenas busca editais)'
    )
    
    args = parser.parse_args()
    
    fetch_items = not args.no_items
    exit_code = main(days=args.days, fetch_items=fetch_items)
    sys.exit(exit_code)
