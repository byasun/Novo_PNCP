"""
Script para gerar um ID_C_PNCP único para cada edital (UUID independente dos campos) e propagar para os itens correspondentes.
O campo edital_ID_C_PNCP dos itens será preenchido com o ID_C_PNCP do edital correspondente pelo vínculo tradicional (CNPJ, ano, número).

Este script deve ser utilizado para garantir que cada edital possua um identificador único absoluto, facilitando o rastreamento e a integridade dos dados entre editais e itens.
"""
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )

from backend.storage.data_manager import DataManager

def generate_edital_key(edital):
    """
    Gera uma chave única baseada em CNPJ, ano e número do edital.
    Utilizada para mapear e relacionar editais e itens.
    """
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
        id_c_pncp = str(uuid.uuid4())
        edital["ID_C_PNCP"] = id_c_pncp
        # Reordena para ser o primeiro campo
        editais[i] = {"ID_C_PNCP": id_c_pncp, **{k: v for k, v in edital.items() if k != "ID_C_PNCP"}}

    # Cria um índice auxiliar para mapear (CNPJ, ano, numero) para todos os editais
    key_to_ids = {}
    for edital in editais:
        key = generate_edital_key(edital)
        key_to_ids.setdefault(key, []).append(edital["ID_C_PNCP"])

    # Propaga o ID_C_PNCP para os itens
    for i, item in enumerate(itens):
        cnpj = item.get("edital_cnpj") or item.get("cnpjOrgao") or item.get("cnpj")
        ano = item.get("edital_ano") or item.get("anoCompra") or item.get("ano")
        numero = item.get("edital_numero") or item.get("numeroCompra") or item.get("numero")
        key = f"{str(cnpj)}_{str(ano)}_{str(numero)}"
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
