from backend.storage.data_manager import DataManager
import pytest

def test_editais_identificador_unico():
    dm = DataManager()
    editais = dm.load_editais()
    ids = [e.get('numeroControlePNCP') or e.get('ID_C_PNCP') for e in editais]
    ids = [i for i in ids if i]
    assert len(ids) == len(set(ids)), 'Existem editais com identificador duplicado.'

def test_itens_identificador_unico():
    dm = DataManager()
    itens = dm.load_itens()
    chaves = [(i.get('edital_numeroControlePNCP') or i.get('edital_ID_C_PNCP'), i.get('numeroItem')) for i in itens]
    chaves = [c for c in chaves if c[0] and c[1]]
    assert len(chaves) == len(set(chaves)), 'Existem itens com identificador duplicado.'
