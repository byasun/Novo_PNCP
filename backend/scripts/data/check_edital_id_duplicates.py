"""
Script para verificar duplicidade de ID_C_PNCP em editais.json e itens.json.
Mostra os IDs duplicados e a quantidade de ocorrências em cada arquivo.

Este script é útil para identificar inconsistências de integridade, garantindo que cada edital e item possua um identificador único.
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
    """
    Verifica e retorna um dicionário com os IDs duplicados e suas quantidades em um arquivo JSON.
    """
    with open(path, encoding="utf-8") as f:
        dados = json.load(f)
    ids = [obj.get(campo) for obj in dados if campo in obj]
    contagem = Counter(ids)
    duplicados = {k: v for k, v in contagem.items() if v > 1}
    return duplicados

def main():
    """
    Função principal que verifica e exibe a quantidade de IDs duplicados em cada arquivo.
    """
    for arquivo in ARQUIVOS:
        duplicados = verifica_duplicados(arquivo)
        print(f"Arquivo: {arquivo}")
        print(f"  Quantidade de ID_C_PNCP duplicados: {len(duplicados)}")

if __name__ == "__main__":
    # Permite execução direta do script
    main()
