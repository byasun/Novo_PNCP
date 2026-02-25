import os
import sys
import importlib.util
from backend.storage.data_manager import DataManager

def test_remocao_expirados():
    # Executa o script de remoção
    script_path = os.path.join(os.path.dirname(__file__), '../scripts/data/remove_expired_editais.py')
    spec = importlib.util.spec_from_file_location('remove_expired_editais', script_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # Após execução, valida se não há editais/itens expirados
    dm = DataManager()
    editais = dm.load_editais()
    itens = dm.load_itens()
    # Todos os editais devem estar ativos
    for edital in editais:
        data_enc = edital.get('dataEncerramentoProposta')
        if data_enc:
            from datetime import datetime
            try:
                dt = datetime.fromisoformat(data_enc)
            except Exception:
                continue
            assert dt >= datetime.now(), f"Edital expirado não removido: {edital}"
    # Todos os itens devem estar vinculados a editais ativos
    ids_ativos = set(e.get('numeroControlePNCP') or e.get('ID_C_PNCP') for e in editais)
    for item in itens:
        id_item = item.get('edital_numeroControlePNCP') or item.get('edital_ID_C_PNCP')
        assert id_item in ids_ativos, f"Item de edital expirado não removido: {id_item}"
