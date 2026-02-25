from backend.storage.data_manager import DataManager
from backend.services.editais_service import EditaisService
import pytest

def test_fallback_chave_composta():
    dm = DataManager()
    service = EditaisService()
    editais = dm.load_editais()
    # Simula busca por chave composta para editais sem identificador único
    for edital in editais:
        if not (edital.get('numeroControlePNCP') or edital.get('ID_C_PNCP')):
            cnpj = edital.get('orgaoEntidade', {}).get('cnpj') or edital.get('cnpjOrgao')
            ano = edital.get('anoCompra') or edital.get('ano')
            numero = edital.get('numeroCompra') or edital.get('numero')
            key = f"{cnpj}_{ano}_{numero}"
            found = service.get_edital_by_key(key)
            assert found is not None, f"Edital sem identificador único não encontrado pela chave composta: {key}"
