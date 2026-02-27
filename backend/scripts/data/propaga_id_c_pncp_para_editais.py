import os
import json

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))
EDITAIS_PATH = os.path.join(DATA_DIR, 'editais.json')
ITENS_PATH = os.path.join(DATA_DIR, 'itens.json')


def main():
    # Carrega editais
    with open(EDITAIS_PATH, 'r', encoding='utf-8') as f:
        editais = json.load(f)
    # Carrega itens
    with open(ITENS_PATH, 'r', encoding='utf-8') as f:
        itens = json.load(f)

    # Cria um mapa: edital_numeroControlePNCP -> edital_ID_C_PNCP (usando os itens)
    numero_to_id_c_pncp = {}
    for item in itens:
        numero = item.get('edital_numeroControlePNCP')
        id_c_pncp = item.get('edital_ID_C_PNCP')
        if numero and id_c_pncp:
            numero_to_id_c_pncp[str(numero)] = id_c_pncp

    # Atualiza os editais com o ID_C_PNCP correspondente
    atualizados = 0
    for edital in editais:
        numero = edital.get('numeroControlePNCP')
        if numero and (not edital.get('ID_C_PNCP') or not isinstance(edital.get('ID_C_PNCP'), str) or not edital['ID_C_PNCP'].strip()):
            id_c_pncp = numero_to_id_c_pncp.get(str(numero))
            if id_c_pncp:
                edital['ID_C_PNCP'] = id_c_pncp
                atualizados += 1

    # Salva editais atualizados
    with open(EDITAIS_PATH, 'w', encoding='utf-8') as f:
        json.dump(editais, f, ensure_ascii=False, indent=2)
    print(f'Editais atualizados com ID_C_PNCP: {atualizados}')

if __name__ == '__main__':
    main()
