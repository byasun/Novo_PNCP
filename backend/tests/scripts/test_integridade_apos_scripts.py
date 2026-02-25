import os
import sys
import importlib.util
from backend.storage.data_manager import DataManager

def test_integridade_apos_scripts():
    # Executa scripts de fix e geração
    scripts = [
        '../scripts/data/fix_edital_ids.py',
        '../scripts/data/generate_edital_unique_ids_absolute.py'
    ]
    for script in scripts:
        script_path = os.path.join(os.path.dirname(__file__), script)
        spec = importlib.util.spec_from_file_location('script', script_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    # Após execução, valida integridade
    dm = DataManager()
    editais = dm.load_editais()
    itens = dm.load_itens()
    ids_editais = set(e.get('numeroControlePNCP') or e.get('ID_C_PNCP') for e in editais)
    for item in itens:
        id_item = item.get('edital_numeroControlePNCP') or item.get('edital_ID_C_PNCP')
        assert id_item in ids_editais, f"Item órfão após scripts: {id_item}"
