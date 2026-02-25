from backend.storage.data_manager import DataManager
from backend.services.editais_service import EditaisService
import pytest

def test_compatibilidade_dados_antigos():
    dm = DataManager()
    service = EditaisService()
    editais = dm.load_editais()
    # Simula editais antigos sem identificador único
    antigos = [e for e in editais if not (e.get('numeroControlePNCP') or e.get('ID_C_PNCP'))]
    for edital in antigos:
        cnpj = edital.get('orgaoEntidade', {}).get('cnpj') or edital.get('cnpjOrgao')
        ano = edital.get('anoCompra') or edital.get('ano')
        numero = edital.get('numeroCompra') or edital.get('numero')
        key = f"{cnpj}_{ano}_{numero}"
        found = service.get_edital_by_key(key)
        assert found is not None, f"Edital antigo não encontrado por chave composta: {key}"
