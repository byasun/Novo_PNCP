from backend.storage.data_manager import DataManager
from backend.services.editais_service import EditaisService
import pytest

def test_busca_por_todos_metodos():
    dm = DataManager()
    service = EditaisService()
    editais = dm.load_editais()
    for edital in editais:
        numeroControlePNCP = edital.get('numeroControlePNCP')
        id_c_pncp = edital.get('ID_C_PNCP')
        # Busca apenas por métodos oficiais
        found1 = service.get_edital_by_key(numeroControlePNCP) if numeroControlePNCP else None
        found2 = service.get_edital_by_key(id_c_pncp) if id_c_pncp else None
        assert any([found1, found2]), f"Edital não encontrado por identificadores oficiais: {edital}"
