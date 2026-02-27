"""
Script para identificar chaves compostas duplicadas em editais.json.
A chave composta é formada por CNPJ, ano e número do edital.
"""
import os
import sys
import json
from collections import Counter

# Garante que o diretório raiz do projeto esteja no sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.config import DATA_DIR

EDITAIS_PATH = os.path.join(DATA_DIR, "editais.json")

def chave_composta(edital):
    cnpj = (edital.get("orgaoEntidade", {}) or {}).get("cnpj") or edital.get("cnpjOrgao")
    ano = edital.get("anoCompra") or edital.get("ano")
    numero = edital.get("numeroCompra") or edital.get("numero")
    return f"{cnpj}_{ano}_{numero}"

def main():
    if not os.path.exists(EDITAIS_PATH):
        print(f"Arquivo não encontrado: {EDITAIS_PATH}")
        return
    with open(EDITAIS_PATH, "r", encoding="utf-8") as f:
        editais = json.load(f)
    chaves = [chave_composta(e) for e in editais]
    counter = Counter(chaves)
    duplicadas = {k: v for k, v in counter.items() if v > 1}
    print(f"Total de editais: {len(editais)}")
    print(f"Chaves compostas únicas: {len(counter)}")
    print(f"Chaves compostas duplicadas: {len(duplicadas)}")
    if duplicadas:
        print("Exemplos de chaves duplicadas:")
        for chave, count in list(duplicadas.items())[:10]:
            print(f"  {chave}: {count} vezes")
    else:
        print("Nenhuma chave composta duplicada encontrada.")

if __name__ == "__main__":
    main()
