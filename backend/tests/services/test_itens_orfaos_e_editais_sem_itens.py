from backend.storage.data_manager import DataManager
import pytest

def test_itens_orfaos():
    dm = DataManager()
    editais = dm.load_editais()
    itens = dm.load_itens()
    ids_editais = set(e.get('numeroControlePNCP') or e.get('ID_C_PNCP') for e in editais)
    orfaos = [i for i in itens if (i.get('edital_numeroControlePNCP') or i.get('edital_ID_C_PNCP')) not in ids_editais]
    assert not orfaos, f"Itens órfãos encontrados: {orfaos}"

def test_editais_sem_itens():
    dm = DataManager()
    editais = dm.load_editais()
    itens = dm.load_itens()
    ids_com_itens = set(i.get('edital_numeroControlePNCP') or i.get('edital_ID_C_PNCP') for i in itens)
    sem_itens = [e for e in editais if (e.get('numeroControlePNCP') or e.get('ID_C_PNCP')) not in ids_com_itens]
    # Não falha, mas reporta
    print(f"Editais sem itens: {len(sem_itens)}")
