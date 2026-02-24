"""
Script para validar se os itens estão corretamente vinculados aos editais pelo campo ID_C_PNCP.
Percorre todos os editais e verifica se existe pelo menos um item com edital_ID_C_PNCP igual ao ID_C_PNCP do edital.
"""

import os
import sys
import json


# Ajusta o PYTHONPATH e o import para rodar de dentro da pasta backend ou backend/scripts
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
cwd = os.getcwd()
if os.path.basename(cwd) == "backend":
    # Rodando de dentro de backend: importa storage.data_manager direto
    if cwd not in sys.path:
        sys.path.insert(0, cwd)
    from storage.data_manager import DataManager
else:
    # Rodando de outro lugar: importa backend.storage.data_manager
    PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    from backend.storage.data_manager import DataManager

def main():
    dm = DataManager()
    editais = dm.load_editais()
    itens = dm.load_itens()


    # Sets de IDs
    edital_ids = set(str(edital.get("ID_C_PNCP", "")) for edital in editais if str(edital.get("ID_C_PNCP", "")))
    item_edital_ids = set(str(item.get("edital_ID_C_PNCP", "")) for item in itens if str(item.get("edital_ID_C_PNCP", "")))

    # 1. Quantos ID_C_PNCP não têm nenhum item vinculado
    idc_sem_item = edital_ids - item_edital_ids
    # 2. Quantos edital_ID_C_PNCP não estão vinculados a nenhum edital
    item_sem_edital = item_edital_ids - edital_ids
    # 3. Quantos ID_C_PNCP têm pelo menos um item vinculado
    idc_com_item = edital_ids & item_edital_ids
    # 4. Quantos edital_ID_C_PNCP estão vinculados a um edital
    item_vinculado_edital = item_edital_ids & edital_ids

    print(f"Total de editais (ID_C_PNCP): {len(edital_ids)}")
    print(f"Total de itens (edital_ID_C_PNCP únicos): {len(item_edital_ids)}\n")
    print(f"1. Quantos ID_C_PNCP não têm nenhum item vinculado: {len(idc_sem_item)}")
    print(f"2. Quantos edital_ID_C_PNCP não estão vinculados a nenhum edital: {len(item_sem_edital)}")
    print(f"3. Quantos ID_C_PNCP têm pelo menos um item vinculado: {len(idc_com_item)}")
    print(f"4. Quantos edital_ID_C_PNCP estão vinculados a um edital: {len(item_vinculado_edital)}")

if __name__ == "__main__":
    main()
