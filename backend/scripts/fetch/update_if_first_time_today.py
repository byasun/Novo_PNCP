"""
Script utilitário para atualizar editais e itens se for o primeiro uso do dia.
Pode ser chamado no início do main.py.

Este script verifica se já houve atualização diária dos editais e itens. Caso não tenha ocorrido, executa a atualização e marca o dia como atualizado, evitando execuções duplicadas no mesmo dia.
"""
import os
import json
from datetime import datetime
from backend.scheduler.job import DailyJob
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
    A merge incremental é feita automaticamente pelo DataManager.
    """
    if already_updated_today():
        print("Já foi feita atualização hoje. Pulando...")
        return
    print("Primeira execução do dia, atualizando editais e itens...")
    daily_job = DailyJob()
    daily_job.run_now()
    mark_updated_today()
    print("Atualização diária concluída.")

if __name__ == "__main__":
    # Permite execução direta do script
    update_if_first_time_today()
