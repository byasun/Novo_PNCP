import os
import sys
import json

# Adiciona a pasta raiz ao sys.path para garantir imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
EDITAIS_PATH = os.path.join(DATA_DIR, 'editais.json')
ITENS_PATH = os.path.join(DATA_DIR, 'itens.json')

def main():
    # Conta editais
    try:
        with open(EDITAIS_PATH, 'r', encoding='utf-8') as f:
            editais = json.load(f)
        n_editais = len(editais)
    except Exception as e:
        print(f'Erro ao ler editais.json: {e}')
        n_editais = 0
    # Conta itens
    try:
        with open(ITENS_PATH, 'r', encoding='utf-8') as f:
            itens = json.load(f)
        n_itens = len(itens)
    except Exception as e:
        print(f'Erro ao ler itens.json: {e}')
        n_itens = 0
    # Exibe resultado
    print(f'Editais encontrados: {n_editais}')
    print(f'Itens encontrados: {n_itens}')

if __name__ == '__main__':
    main()
