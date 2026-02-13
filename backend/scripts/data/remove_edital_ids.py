"""
Script para remover os campos 'ID_C_PNCP', 'edital_ID_C_PNCP' e '_edital_id' de todos os editais e itens dos arquivos JSON.
"""
import sys
import os
import json

# Adiciona a pasta raiz ao sys.path para permitir imports absolutos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.storage.data_manager import DataManager

CAMPOS_REMOVER = ["ID_C_PNCP", "edital_ID_C_PNCP", "_edital_id"]

def remove_campos(obj):
    for campo in CAMPOS_REMOVER:
        if campo in obj:
            del obj[campo]
    return obj

def main():
    data_manager = DataManager()
    editais = data_manager.load_editais()
    itens = data_manager.load_itens()

    editais_limpos = [remove_campos(dict(e)) for e in editais]
    itens_limpos = [remove_campos(dict(i)) for i in itens]

    data_manager.save_editais(editais_limpos)
    data_manager.save_itens(itens_limpos)
    print(f"Campos removidos de {len(editais_limpos)} editais e {len(itens_limpos)} itens.")

if __name__ == "__main__":
    main()
