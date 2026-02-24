
"""
Script para padronizar os campos de identificação dos itens de edital como string.
Uso: python backend/scripts/data/fix_itens_keys.py

Este script garante que os campos edital_cnpj, edital_ano e edital_numero dos itens estejam sempre no formato string, evitando problemas de consistência e comparação.
"""
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.config import DATA_DIR
ITENS_PATH = os.path.join(DATA_DIR, "itens.json")


def main():
    """
    Função principal que padroniza os campos de identificação dos itens para string.
    """
    if not os.path.exists(ITENS_PATH):
        print(f"Arquivo não encontrado: {ITENS_PATH}")
        return

    with open(ITENS_PATH, "r", encoding="utf-8") as f:
        try:
            itens = json.load(f)
        except Exception as e:
            print(f"Erro ao ler itens.json: {e}")
            return

    changed = False
    for item in itens:
        for key in ("edital_cnpj", "edital_ano", "edital_numero"):
            # Garante que o campo está no formato string
            if key in item and not isinstance(item[key], str):
                item[key] = str(item[key])
                changed = True

    if changed:
        with open(ITENS_PATH, "w", encoding="utf-8") as f:
            json.dump(itens, f, ensure_ascii=False, indent=2)
        print(f"Campos padronizados e arquivo salvo: {ITENS_PATH}")
    else:
        print("Nenhuma alteração necessária. Todos os campos já estavam como string.")
if __name__ == "__main__":
    # Permite execução direta do script
    main()

if __name__ == "__main__":
    main()
