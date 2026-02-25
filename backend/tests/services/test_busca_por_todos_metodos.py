from backend.storage.data_manager import DataManager
from backend.services.editais_service import EditaisService
import pytest

def test_busca_por_todos_metodos():
    dm = DataManager()
    service = EditaisService()
    editais = dm.load_editais()
    for edital in editais:
        cnpj = edital.get('orgaoEntidade', {}).get('cnpj') or edital.get('cnpjOrgao')
        ano = edital.get('anoCompra') or edital.get('ano')
        numero = edital.get('numeroCompra') or edital.get('numero')
        numeroControlePNCP = edital.get('numeroControlePNCP')
        id_c_pncp = edital.get('ID_C_PNCP')
        # Busca por todos os métodos
        found1 = service.get_edital_by_key(numeroControlePNCP) if numeroControlePNCP else None
        found2 = service.get_edital_by_key(id_c_pncp) if id_c_pncp else None
        found3 = service.get_edital_by_key(f"{cnpj}_{ano}_{numero}")
        assert any([found1, found2, found3]), f"Edital não encontrado por nenhum método: {edital}"
