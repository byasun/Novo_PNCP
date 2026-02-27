import os
import json
from backend.services.editais_service import EditaisService
from backend.config.settings import DATA_DIR, EDITAIS_FILE

def main(days=15):
    # Caminho do arquivo de editais
    editais_path = os.path.join(DATA_DIR, EDITAIS_FILE)
    if not os.path.exists(editais_path):
        print(f"Arquivo de editais não encontrado: {editais_path}")
        return
    with open(editais_path, 'r', encoding='utf-8') as f:
        editais = json.load(f)
    service = EditaisService()
    filtered = service._filter_editais_by_publication_date(editais, days=days)
    print(f"Editais filtrados (últimos {days} dias): {len(filtered)} de {len(editais)}")

    # Garante que os campos ID_C_PNCP e numeroControlePNCP estejam presentes em cada edital filtrado
    for edital in filtered:
        original = next((e for e in editais if e.get('ID_C_PNCP') == edital.get('ID_C_PNCP')), None)
        if original:
            edital['ID_C_PNCP'] = original.get('ID_C_PNCP')
            edital['numeroControlePNCP'] = original.get('numeroControlePNCP')

    # Salva o resultado filtrado em um novo arquivo
    out_path = os.path.join(DATA_DIR, f"editais_filtrados_{days}d.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)
    print(f"Arquivo salvo: {out_path}")

if __name__ == "__main__":
    import sys
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    main(days)
