"""
Script utilitário para atualizar editais e itens se for o primeiro uso do dia.
Pode ser chamado no início do main.py.

Este script verifica se já houve atualização diária dos editais e itens. Caso não tenha ocorrido, executa a atualização e marca o dia como atualizado, evitando execuções duplicadas no mesmo dia.
"""
import os
import json
from datetime import datetime
from backend.scheduler.job import DailyJob
from backend.storage.data_manager import DataManager
from backend.config import DATA_DIR

CHECKPOINT_FILE = os.path.join(DATA_DIR, ".first_update_check.json")

def already_updated_today():
    """
    Verifica se já foi feita atualização hoje, consultando o arquivo de checkpoint.
    """
    if not os.path.exists(CHECKPOINT_FILE):
        return False
    try:
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        last = data.get("last_update_date")
        return last == datetime.now().strftime("%Y-%m-%d")
    except Exception:
        return False

def mark_updated_today():
    """
    Marca a data de hoje como já atualizada no arquivo de checkpoint.
    """
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_update_date": datetime.now().strftime("%Y-%m-%d")}, f)

def update_if_first_time_today():
    """
    Executa a atualização de editais e itens apenas se ainda não foi feita no dia.
    """
    if already_updated_today():
        print("Já foi feita atualização hoje. Pulando...")
        return
    print("Primeira execução do dia, atualizando editais e itens...")
    daily_job = DailyJob()
    daily_job.run_now()

    # Mesclar dados se arquivos já existirem
    dm = DataManager()
    editais_path = os.path.join(DATA_DIR, "editais.json")
    itens_path = os.path.join(DATA_DIR, "itens.json")
    # Mesclar editais
    if os.path.exists(editais_path):
        try:
            with open(editais_path, "r", encoding="utf-8") as f:
                antigos = json.load(f)
        except Exception:
            antigos = []
        novos = dm.load_editais()
        # Mescla por ID_C_PNCP: sempre mantém todos os antigos e só adiciona/atualiza os novos
        editais_dict = {e.get("ID_C_PNCP"): e for e in antigos if e.get("ID_C_PNCP")}
        for e in novos:
            if e.get("ID_C_PNCP"):
                editais_dict[e["ID_C_PNCP"]] = e
        # Só salva se houver pelo menos 1 edital (antigo ou novo)
        if editais_dict:
            dm.save_editais(list(editais_dict.values()))
        else:
            print("Nenhum edital encontrado (nem antigo nem novo). Mantendo arquivo antigo.")
    # Mesclar itens
    if os.path.exists(itens_path):
        try:
            with open(itens_path, "r", encoding="utf-8") as f:
                antigos = json.load(f)
        except Exception:
            antigos = []
        novos = dm.load_itens()
        # Mescla por edital_ID_C_PNCP + id/numero: sempre mantém todos os antigos e só adiciona/atualiza os novos
        key = lambda i: (str(i.get("edital_ID_C_PNCP")), str(i.get("id") or i.get("numero") or i.get("item")))
        item_map = {key(i): i for i in antigos if i.get("edital_ID_C_PNCP")}
        for item in novos:
            item_map[key(item)] = item
        # Só salva se houver pelo menos 1 item (antigo ou novo)
        if item_map:
            with open(itens_path, "w", encoding="utf-8") as f:
                json.dump(list(item_map.values()), f, ensure_ascii=False, indent=2)
        else:
            print("Nenhum item encontrado (nem antigo nem novo). Mantendo arquivo antigo.")

    mark_updated_today()
    print("Atualização diária concluída.")

if __name__ == "__main__":
    # Permite execução direta do script
    update_if_first_time_today()
