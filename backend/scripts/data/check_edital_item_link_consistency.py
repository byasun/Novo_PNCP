"""
Script para verificar se todos os itens possuem o campo edital_ID_C_PNCP e se esse campo corresponde a algum ID_C_PNCP presente em editais.json.
Mostra estatísticas e exemplos de inconsistências, se houver.
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.storage.data_manager import DataManager

def main():
    data_manager = DataManager()
    editais = data_manager.load_editais()
    itens = data_manager.load_itens()

    ids_editais = set(e.get("ID_C_PNCP") for e in editais if e.get("ID_C_PNCP"))
    total_itens = len(itens)
    sem_id = 0
    id_inexistente = 0
    exemplos_sem_id = []
    exemplos_id_inexistente = []

    for item in itens:
        eid = item.get("edital_ID_C_PNCP")
        if not eid:
            sem_id += 1
            if len(exemplos_sem_id) < 5:
                exemplos_sem_id.append(item)
        elif eid not in ids_editais:
            id_inexistente += 1
            if len(exemplos_id_inexistente) < 5:
                exemplos_id_inexistente.append(item)

    print(f"Total de itens: {total_itens}")
    print(f"Itens sem campo edital_ID_C_PNCP: {sem_id}")
    print(f"Itens com edital_ID_C_PNCP não encontrado em editais: {id_inexistente}")
    if exemplos_sem_id:
        print("Exemplos de itens sem edital_ID_C_PNCP:")
        for ex in exemplos_sem_id:
            print(f"  {ex}")
    if exemplos_id_inexistente:
        print("Exemplos de itens com edital_ID_C_PNCP inexistente:")
        for ex in exemplos_id_inexistente:
            print(f"  {ex}")

if __name__ == "__main__":
    main()
