import os
import sys
import json
from backend.services.editais_service import load_editais, fetch_and_save_items_for_edital
from backend.config.settings import DATA_DIR, EDITAIS_FILE, ITENS_FILE


def load_itens():
    itens_path = os.path.join(DATA_DIR, ITENS_FILE)
    if not os.path.exists(itens_path):
        return []
    with open(itens_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_editais_without_items(editais, itens):
    edital_ids_with_items = set(item.get('ID_C_PNCP') for item in itens if item.get('ID_C_PNCP'))
    return [edital for edital in editais if edital.get('ID_C_PNCP') not in edital_ids_with_items]

def main():
    print("Carregando editais e itens...")
    editais = load_editais()
    itens = load_itens()
    editais_sem_itens = get_editais_without_items(editais, itens)
    print(f"Encontrados {len(editais_sem_itens)} editais sem itens.")
    for edital in editais_sem_itens:
        id_c_pncp = edital.get('ID_C_PNCP')
        if not id_c_pncp:
            print(f"Edital sem ID_C_PNCP: {edital}")
            continue
        print(f"Buscando itens para edital ID_C_PNCP={id_c_pncp} ...")
        try:
            fetch_and_save_items_for_edital(edital)
        except Exception as e:
            print(f"Erro ao buscar itens para edital {id_c_pncp}: {e}")

if __name__ == "__main__":
    main()
