import os
import sys
import json
from collections import Counter

# Garante que o diretório raiz do projeto esteja no sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Caminho para o arquivo de editais
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))
#DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
EDITAIS_PATH = os.path.join(DATA_DIR, 'editais.json')

def main():
    try:
        with open(EDITAIS_PATH, 'r', encoding='utf-8') as f:
            editais = json.load(f)
    except Exception as e:
        print(f'Erro ao ler editais.json: {e}')
        return

    numeros = [e.get('numeroControlePNCP') for e in editais if e.get('numeroControlePNCP')]
    counter = Counter(numeros)
    unicos = sum(1 for v in counter.values() if v == 1)
    repetidos = sum(1 for v in counter.values() if v > 1)
    print(f'numeroControlePNCP únicos: {unicos}')
    print(f'numeroControlePNCP que aparecem mais de uma vez: {repetidos}')

if __name__ == '__main__':
    main()
