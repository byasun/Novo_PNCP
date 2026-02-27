from backend.storage.data_manager import DataManager
from backend.services.editais_service import EditaisService
import pytest

def test_compatibilidade_dados_antigos():
    dm = DataManager()
    service = EditaisService()
    editais = dm.load_editais()
    # Simula editais antigos sem identificador único
    # Teste removido: compatibilidade por chave composta não é mais suportada. Apenas IDs oficiais são aceitos.
