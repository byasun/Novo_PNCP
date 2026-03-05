import os
import sys
import importlib.util
from datetime import datetime, timedelta
from backend.storage.data_manager import DataManager


def test_remocao_expirados():
    """
    Executa o script de remoção de expirados e valida que não restam
    editais cujo encerramento de propostas é anterior ao momento da execução
    (com margem de 30 segundos para tempo de execução do teste).
    """
    # Marca o momento antes de executar o script
    before_run = datetime.now() - timedelta(seconds=30)

    # Executa o script de remoção
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
    script_path = os.path.join(PROJECT_ROOT, 'backend/scripts/data/remove_expired_editais.py')
    spec = importlib.util.spec_from_file_location('remove_expired_editais', script_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # O script tem if __name__ == "__main__", então chamamos main() explicitamente
    mod.main()

    # Após execução, valida se não há editais expirados
    dm = DataManager()
    editais = dm.load_editais()
    itens = dm.load_itens()

    # Todos os editais restantes devem ter encerramento >= momento da execução do script
    for edital in editais:
        data_enc = edital.get('dataEncerramentoProposta')
        if data_enc:
            try:
                dt = datetime.fromisoformat(data_enc)
            except Exception:
                continue
            assert dt >= before_run, (
                f"Edital expirado não removido (encerramento={data_enc}): "
                f"ID_C_PNCP={edital.get('ID_C_PNCP')}"
            )

    # Todos os itens devem estar vinculados a editais ativos
    ids_ativos = set(e.get('numeroControlePNCP') or e.get('ID_C_PNCP') for e in editais)
    for item in itens:
        id_item = item.get('edital_numeroControlePNCP') or item.get('edital_ID_C_PNCP')
        assert id_item in ids_ativos, f"Item de edital expirado não removido: {id_item}"
