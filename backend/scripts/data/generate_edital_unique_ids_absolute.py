"""
Script para gerar um ID_C_PNCP único para cada edital (UUID independente dos campos) e propagar para os itens correspondentes.
O campo edital_ID_C_PNCP dos itens será preenchido com o ID_C_PNCP do edital correspondente pelo vínculo tradicional (CNPJ, ano, número).

Este script deve ser utilizado para garantir que cada edital possua um identificador único absoluto, facilitando o rastreamento e a integridade dos dados entre editais e itens.
"""
import os
import sys
import uuid


# Garante que o diretório raiz do projeto esteja no sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

#sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )

from backend.storage.data_manager import DataManager


def generate_edital_key(edital):
    """
    Gera uma chave única baseada em numeroControlePNCP, ID_C_PNCP ou (CNPJ, ano, numero).
    """
    if edital.get("numeroControlePNCP"):
        return edital["numeroControlePNCP"]
    if edital.get("ID_C_PNCP"):
        return edital["ID_C_PNCP"]
    cnpj = edital.get("orgaoEntidade", {}).get("cnpj") or edital.get("cnpjOrgao") or edital.get("cnpj")
    ano = edital.get("anoCompra") or edital.get("ano")
    numero = edital.get("numeroCompra") or edital.get("numero")
    return f"{str(cnpj)}_{str(ano)}_{str(numero)}"


def main():
    """
    Função principal que executa a geração dos UUIDs únicos para editais e propaga para os itens relacionados.
    """
    data_manager = DataManager()
    editais = data_manager.load_editais()
    itens = data_manager.load_itens()



    # Gera um UUID único para cada edital, independente dos campos
    for i, edital in enumerate(editais):
        if not edital.get("ID_C_PNCP"):
            id_c_pncp = str(uuid.uuid4())
            edital["ID_C_PNCP"] = id_c_pncp
        # Reordena para ser o primeiro campo
        editais[i] = {"ID_C_PNCP": edital["ID_C_PNCP"], **{k: v for k, v in edital.items() if k != "ID_C_PNCP"}}


    # Cria um índice auxiliar para mapear identificadores para todos os editais
    key_to_ids = {}
    for edital in editais:
        key = generate_edital_key(edital)
        key_to_ids.setdefault(key, []).append(edital["ID_C_PNCP"])


    # Propaga o ID_C_PNCP para os itens
    for i, item in enumerate(itens):
        # Tenta identificar o edital correspondente por todos os identificadores possíveis
        key = (
            item.get("edital_numeroControlePNCP")
            or item.get("edital_ID_C_PNCP")
            or f"{item.get('edital_cnpj')}_{item.get('edital_ano')}_{item.get('edital_numero')}"
        )
        id_list = key_to_ids.get(key)
        edital_id_c_pncp = id_list[0] if id_list else None
        item["edital_ID_C_PNCP"] = edital_id_c_pncp
        # Reordena para ser o primeiro campo
        itens[i] = {"edital_ID_C_PNCP": edital_id_c_pncp, **{k: v for k, v in item.items() if k != "edital_ID_C_PNCP"}}

    # Salva as alterações nos arquivos de editais e itens
    data_manager.save_editais(editais)
    data_manager.save_itens(itens)
    print(f"UUIDs únicos gerados para {len(editais)} editais e propagados para {len(itens)} itens.")

if __name__ == "__main__":
    # Permite execução direta do script
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )
    main()
