"""
Script para atualizar editais.json e itens.json adicionando o campo _edital_id no início de cada edital e item.
O campo _edital_id é usado para vincular itens ao edital correspondente.

Este script padroniza o campo de vínculo entre editais e itens, facilitando a integridade referencial e buscas rápidas.
"""
import os
import sys
import json

# Garante que o diretório raiz do projeto esteja no sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Adiciona a pasta raiz ao sys.path para permitir imports absolutos
#sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.storage.data_manager import DataManager


def generate_edital_id(edital):
    """
    Gera um identificador único para o edital, usando apenas numeroControlePNCP ou ID_C_PNCP.
    """
    if edital.get("numeroControlePNCP"):
        return edital["numeroControlePNCP"]
    if edital.get("ID_C_PNCP"):
        return edital["ID_C_PNCP"]
    return None


def padroniza_edital_id(edital):
    """
    Adiciona o campo _edital_id ao edital, garantindo que seja o primeiro campo.
    """
    edital_id = generate_edital_id(edital)
    new_edital = {"_edital_id": edital_id}
    new_edital.update(edital)
    return new_edital


def padroniza_item_id(item):
    """
    Adiciona o campo _edital_id ao item, garantindo que seja o primeiro campo.
    """
    edital_id = (
        item.get("edital_numeroControlePNCP")
        or item.get("edital_ID_C_PNCP")
        or f"{item.get('edital_cnpj')}_{item.get('edital_ano')}_{item.get('edital_numero')}"
    )
    new_item = {"_edital_id": edital_id}
    new_item.update(item)
    return new_item

def main():
    """
    Função principal que atualiza os arquivos de editais e itens, adicionando o campo _edital_id padronizado.
    """
    data_manager = DataManager()
    editais = data_manager.load_editais()
    itens = data_manager.load_itens()
    # Atualiza todos os editais e itens com o campo _edital_id padronizado
    editais_atualizados = [padroniza_edital_id(e) for e in editais]
    itens_atualizados = [padroniza_item_id(i) for i in itens]

    data_manager.save_editais(editais_atualizados)
    data_manager.save_itens(itens_atualizados)
    print(f"Atualização concluída: {len(editais_atualizados)} editais e {len(itens_atualizados)} itens atualizados.")

if __name__ == "__main__":
    # Permite execução direta do script
    main()
