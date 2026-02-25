import pytest
from backend.storage.data_manager import DataManager
from backend.services.editais_service import EditaisService

def test_editais_possuem_identificador_unico():
    dm = DataManager()
    editais = dm.load_editais()
    assert all(
        e.get('numeroControlePNCP') or e.get('ID_C_PNCP') for e in editais
    ), "Todos os editais devem ter numeroControlePNCP ou ID_C_PNCP"

def test_itens_possuem_vinculo_unico():
    dm = DataManager()
    itens = dm.load_itens()
    assert all(
        i.get('edital_numeroControlePNCP') or i.get('edital_ID_C_PNCP') for i in itens
    ), "Todos os itens devem ter edital_numeroControlePNCP ou edital_ID_C_PNCP"

def test_vinculo_item_edital():
    dm = DataManager()
    editais = dm.load_editais()
    itens = dm.load_itens()
    ids_editais = set(
        str(e.get('numeroControlePNCP') or e.get('ID_C_PNCP')) for e in editais
    )
    for item in itens:
        id_item = str(item.get('edital_numeroControlePNCP') or item.get('edital_ID_C_PNCP'))
        assert id_item in ids_editais, f"Item órfão: {id_item} não encontrado em editais"

def test_busca_por_identificador():
    service = EditaisService()
    dm = DataManager()
    editais = dm.load_editais()
    for edital in editais:
        ident = edital.get('numeroControlePNCP') or edital.get('ID_C_PNCP')
        if not ident:
            continue
        # Busca pelo identificador
        found = service.get_edital_by_key(ident)
        assert found is not None, f"Edital não encontrado por identificador: {ident}"
        # Busca itens pelo identificador
        itens = service.get_itens_by_edital(numeroControlePNCP=edital.get('numeroControlePNCP'), id_c_pncp=edital.get('ID_C_PNCP'))
        # Não falha se não houver itens, mas deve rodar sem erro
        assert isinstance(itens, list)
