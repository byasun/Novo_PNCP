Script para padronizar os campos de identificação dos itens de edital como string.
Uso: python backend/scripts/fix_itens_keys.py
"""
import json
import os

"""
Script para padronizar os campos de identificação dos itens de edital como string.
Uso: python backend/scripts/data/fix_itens_keys.py
"""
import json
import os
ITENS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "itens.json")


def main():
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
    main()
