"""
Script manual para buscar editais e itens da API PNCP conforme padrão e lógica do sistema.

Este script permite buscar manualmente editais e itens da API PNCP, seguindo a lógica do sistema, com opções de padronização e logging detalhado.
Pode ser utilizado para testes, manutenção ou coleta específica de dados.
"""
import logging
import os
import sys
# Garante que o diretório raiz do projeto esteja no sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
import signal
import argparse
from datetime import datetime, timedelta

# Adiciona a pasta raiz ao PATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.config import LOG_LEVEL, LOG_FORMAT, LOGS_DIR, request_cancel

if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(LOGS_DIR, "manual_fetch_editais.log"))
    ]
)

logger = logging.getLogger(__name__)

from backend.services.editais_service import EditaisService
from backend.storage.data_manager import DataManager


def generate_edital_id(edital):
    """
    Gera um identificador único para o edital, preferencialmente usando numeroControlePNCP ou ID_C_PNCP.
    """
    if edital.get("numeroControlePNCP"):
        return edital["numeroControlePNCP"]
    if edital.get("ID_C_PNCP"):
        return edital["ID_C_PNCP"]
    cnpj = edital.get("orgaoEntidade", {}).get("cnpj") or edital.get("cnpjOrgao", "")
    ano = edital.get("anoCompra") or edital.get("ano", "")
    numero = edital.get("numeroCompra") or edital.get("numero", "")
    return f"{str(cnpj)}_{str(ano)}_{str(numero)}"


def padroniza_edital(edital):
    """
    Padroniza os campos de identificação do edital e adiciona o campo _edital_id.
    """
    cnpj = edital.get("orgaoEntidade", {}).get("cnpj") or edital.get("cnpjOrgao", "")
    ano = edital.get("anoCompra") or edital.get("ano", "")
    numero = edital.get("numeroCompra") or edital.get("numero", "")
    edital_id = generate_edital_id(edital)
    edital["_edital_id"] = edital_id
    edital["cnpj"] = str(cnpj)
    edital["ano"] = str(ano)
    edital["numero"] = str(numero)
    if edital.get("numeroControlePNCP"):
        edital["numeroControlePNCP"] = edital["numeroControlePNCP"]
    if edital.get("ID_C_PNCP"):
        edital["ID_C_PNCP"] = edital["ID_C_PNCP"]
    return edital


def padroniza_item(item):
    """
    Padroniza os campos de identificação do item e adiciona o campo _edital_id.
    """
    edital_id = (
        item.get("edital_numeroControlePNCP")
        or item.get("edital_ID_C_PNCP")
        or f"{item.get('edital_cnpj', '')}_{item.get('edital_ano', '')}_{item.get('edital_numero', '')}"
    )
    item["_edital_id"] = edital_id
    if item.get("edital_numeroControlePNCP"):
        item["edital_numeroControlePNCP"] = item["edital_numeroControlePNCP"]
    if item.get("edital_ID_C_PNCP"):
        item["edital_ID_C_PNCP"] = item["edital_ID_C_PNCP"]
    item["edital_cnpj"] = str(item.get("edital_cnpj", ""))
    item["edital_ano"] = str(item.get("edital_ano", ""))
    item["edital_numero"] = str(item.get("edital_numero", ""))
    return item

def main(days=15, fetch_items=True):
    logger.info("=" * 70)
    logger.info("MANUAL FETCH DE EDITAIS (API PNCP) - PADRÃO SISTEMA")
    logger.info("=" * 70)

    # 1. Busca todos os editais recebendo propostas na modalidade 6
    ano_atual = datetime.now().year
    data_final = f"{ano_atual}1231"
    data_inicial = None
    codigo_modalidade = 6
    filtro_publicacao = True

    logger.info(f"Parâmetros: days={days}, data_inicial={data_inicial}, data_final={data_final}, codigo_modalidade={codigo_modalidade}, filtro_publicacao={filtro_publicacao}")

    editais_service = EditaisService()
    data_manager = DataManager()

    start_time = datetime.now()
    logger.info(f"Iniciando busca de editais em {start_time}...")

    try:
        # Busca todos os editais
        editais = editais_service.fetch_all_editais(
            data_inicial=data_inicial,
            data_final=data_final,
            codigo_modalidade=codigo_modalidade,
            filter_by_publication_date=False
        )
        logger.info(f"{len(editais)} editais recebidos da API.")

        # 2. NÃO filtra por dataInclusao, salva todos os editais recebidos da API
        logger.info(f"{len(editais)} editais recebidos da API (sem filtro de dataInclusao)")

        # 3. Padroniza campos e 4. Cria campo de ID
        editais_padronizados = [padroniza_edital(e.copy()) for e in editais]

        # 5. Carrega editais existentes e adiciona apenas os novos
        editais_existentes = {e.get("_edital_id"): e for e in data_manager.load_editais()}
        novos_editais = []
        for edital in editais_padronizados:
            if edital["_edital_id"] not in editais_existentes:
                novos_editais.append(edital)
                editais_existentes[edital["_edital_id"]] = edital
        todos_editais = list(editais_existentes.values())
        data_manager.save_editais(todos_editais)
        logger.info(f"Editais salvos em {data_manager.editais_file} (adicionados {len(novos_editais)} novos)")

        all_itens = []
        if fetch_items:
            logger.info("\nFETCHING ITEMS FOR EDITAIS")
            items_start_time = datetime.now()
            logger.info(f"Iniciando busca de itens em {items_start_time}...")
            try:
                # 6. Busca itens apenas para novos editais
                all_itens = data_manager.load_itens()
                itens_existentes = {(i.get("_edital_id"), i.get("itemSequencial")): i for i in all_itens}
                novos_itens = []
                for edital in novos_editais:
                    cnpj = edital["cnpj"]
                    ano = edital["ano"]
                    numero = edital["numero"]
                    numeroControlePNCP = edital.get("numeroControlePNCP")
                    id_c_pncp = edital.get("ID_C_PNCP")
                    itens = editais_service.fetch_itens_for_edital(
                        cnpj, ano, numero, numeroControlePNCP=numeroControlePNCP, id_c_pncp=id_c_pncp
                    )
                    itens_padronizados = [padroniza_item(i.copy()) for i in itens]
                    for item in itens_padronizados:
                        chave = (item["_edital_id"], item.get("itemSequencial"))
                        if chave not in itens_existentes:
                            novos_itens.append(item)
                            itens_existentes[chave] = item
                todos_itens = list(itens_existentes.values())
                data_manager.save_itens(todos_itens)
                items_end_time = datetime.now()
                items_duration = (items_end_time - items_start_time).total_seconds()
                logger.info(f"Busca de itens concluída em {items_duration:.2f} segundos")
                logger.info(f"Total de itens buscados: {len(novos_itens)} novos, {len(todos_itens)} no total")
            except Exception as e:
                logger.error(f"Erro ao buscar itens: {e}")

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Busca manual concluída em {duration:.2f} segundos")
        logger.info("=" * 70)
        return 0
    except Exception as e:
        logger.exception(f"Erro durante busca manual: {e}")
        logger.info("=" * 70)
        return 1

def signal_handler(signum, frame):
    print("\n\n⚠️  Interrupção solicitada (Ctrl+C). Finalizando...")
    request_cancel()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    parser = argparse.ArgumentParser(
        description='Busca manual de editais da API PNCP conforme padrão do sistema.'
    )
    parser.add_argument('--days', type=int, default=15, help='Dias para filtro de publicação (padrão: 15)')
    parser.add_argument('--no-items', action='store_true', help='Não busca itens para os editais (apenas busca editais)')
    args = parser.parse_args()

    fetch_items = not args.no_items
    exit_code = main(
        days=args.days,
        fetch_items=fetch_items
    )
    sys.exit(exit_code)
