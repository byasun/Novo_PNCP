"""Testes unitários do DataManager (persistência JSON)."""

import json
from backend.storage import data_manager as dm_module
from backend.storage.data_manager import DataManager


def test_save_and_load_editais(tmp_path):
    # Salvar e carregar editais
    dm_module.DATA_DIR = str(tmp_path)
    manager = DataManager()

    editais = [{"id": 1}, {"id": 2}]
    manager.save_editais(editais)

    loaded = manager.load_editais()
    assert loaded == editais


def test_save_and_load_itens(tmp_path):
    # Salvar e carregar itens
    dm_module.DATA_DIR = str(tmp_path)
    manager = DataManager()

    itens = [{"id": "a"}, {"id": "b"}]
    manager.save_itens(itens)

    loaded = manager.load_itens()
    assert loaded == itens


def test_load_when_missing(tmp_path):
    # Carregar quando arquivos não existem
    dm_module.DATA_DIR = str(tmp_path)
    manager = DataManager()

    assert manager.load_editais() == []
    assert manager.load_itens() == []


def test_get_last_update(tmp_path):
    # Timestamp de última atualização
    dm_module.DATA_DIR = str(tmp_path)
    manager = DataManager()

    manager.save_editais([{"id": 1}])
    assert manager.get_last_update() is not None


def test_save_contratos_roundtrip(tmp_path):
    # Salvar/ler contratos e validar JSON
    dm_module.DATA_DIR = str(tmp_path)
    manager = DataManager()

    contratos = [{"id": "c1"}]
    manager.save_contratos(contratos)
    assert manager.load_contratos() == contratos

    # Validate JSON file format
    with open(manager.contratos_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == contratos
