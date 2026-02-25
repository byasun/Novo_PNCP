from backend.storage.data_manager import DataManager
import uuid
import pytest

def test_atualizacao_identificadores():
    dm = DataManager()
    editais = dm.load_editais()
    itens = dm.load_itens()
    # Atualiza o identificador de um edital
    for edital in editais:
        old_id = edital.get('ID_C_PNCP')
        if old_id:
            novo_id = str(uuid.uuid4())
            edital['ID_C_PNCP'] = novo_id
            break
    dm.save_editais(editais)
    # Atualiza todos os itens vinculados
    for item in itens:
        if item.get('edital_ID_C_PNCP') == old_id:
            item['edital_ID_C_PNCP'] = novo_id
    dm.save_itens(itens)
    # Valida integridade
    ids_editais = set(e.get('ID_C_PNCP') for e in editais)
    for item in itens:
        if item.get('edital_ID_C_PNCP'):
            assert item['edital_ID_C_PNCP'] in ids_editais, f"Item órfão após atualização de identificador: {item}"
