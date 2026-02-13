"""
Script para verificar duplicidade de ID_C_PNCP em editais.json e itens.json.
Mostra os IDs duplicados e a quantidade de ocorrências em cada arquivo.
"""
import json
from collections import Counter

import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVOS = [
    os.path.join(SCRIPT_DIR, "..", "data", "editais.json"),
    os.path.join(SCRIPT_DIR, "..", "data", "itens.json")
]

def verifica_duplicados(path, campo="ID_C_PNCP"):
    with open(path, encoding="utf-8") as f:
        dados = json.load(f)
    ids = [obj.get(campo) for obj in dados if campo in obj]
    contagem = Counter(ids)
    duplicados = {k: v for k, v in contagem.items() if v > 1}
    return duplicados

def main():
    for arquivo in ARQUIVOS:
        duplicados = verifica_duplicados(arquivo)
        print(f"Arquivo: {arquivo}")
        print(f"  Quantidade de ID_C_PNCP duplicados: {len(duplicados)}")

if __name__ == "__main__":
    main()
