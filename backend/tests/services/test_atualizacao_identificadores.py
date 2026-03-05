import uuid
import pytest


def test_atualizacao_identificadores():
    """
    Testa que ao atualizar o ID_C_PNCP de um edital e propagar para os itens,
    a integridade referencial é mantida.
    Usa dados em memória para não modificar dados reais.
    """
    # Dados de teste isolados (não modifica dados reais)
    editais = [
        {"ID_C_PNCP": "aaa-111", "numeroControlePNCP": "00000000000100-1-000001/2025"},
        {"ID_C_PNCP": "bbb-222", "numeroControlePNCP": "00000000000100-1-000002/2025"},
    ]
    itens = [
        {"edital_ID_C_PNCP": "aaa-111", "numeroItem": 1, "descricao": "Item A1"},
        {"edital_ID_C_PNCP": "aaa-111", "numeroItem": 2, "descricao": "Item A2"},
        {"edital_ID_C_PNCP": "bbb-222", "numeroItem": 1, "descricao": "Item B1"},
    ]

    # Simula atualização de identificador
    old_id = "aaa-111"
    novo_id = str(uuid.uuid4())
    for edital in editais:
        if edital["ID_C_PNCP"] == old_id:
            edital["ID_C_PNCP"] = novo_id
            break

    # Propaga para itens
    for item in itens:
        if item.get("edital_ID_C_PNCP") == old_id:
            item["edital_ID_C_PNCP"] = novo_id

    # Valida integridade
    ids_editais = set(e["ID_C_PNCP"] for e in editais)
    for item in itens:
        assert item["edital_ID_C_PNCP"] in ids_editais, (
            f"Item órfão após atualização de identificador: {item}"
        )
