"""
Script utilitário para atualizar editais e itens se for o primeiro uso do dia.
Pode ser chamado no início do main.py.
"""
import os
import json
from datetime import datetime
from backend.scheduler.job import DailyJob
from backend.storage.data_manager import DataManager

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CHECKPOINT_FILE = os.path.join(DATA_DIR, ".first_update_check.json")

def already_updated_today():
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
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_update_date": datetime.now().strftime("%Y-%m-%d")}, f)

def update_if_first_time_today():
    if already_updated_today():
        print("Já foi feita atualização hoje. Pulando...")
        return
    print("Primeira execução do dia, atualizando editais e itens...")
    daily_job = DailyJob()
    daily_job.run_now()
    mark_updated_today()
    print("Atualização diária concluída.")

if __name__ == "__main__":
    update_if_first_time_today()
