"""
Testes unitários do EditaisService.

Este módulo contém testes para as funções internas do serviço de editais,
verificando geração de chaves, fallback de campos e extração de mês.
"""

from backend.services.editais_service import EditaisService


"""
Testes removidos: geração e fallback de chave composta não são mais suportados. Apenas IDs oficiais são aceitos.
"""


def test_extract_month_from_edital():
    # Extração de mês a partir de campos diferentes
    service = EditaisService()
    edital = {"mesCompra": "04"}
    assert service._extract_month_from_edital(edital) == 4

    edital = {"dataPublicacao": "2026-12-31"}
    assert service._extract_month_from_edital(edital) == 12


def test_get_itens_by_edital_filters():
    # Filtrar itens por edital
    service = EditaisService()

    itens = [
        {"edital_cnpj": "1", "edital_ano": "2026", "edital_numero": "10"},
        {"edital_cnpj": "2", "edital_ano": "2026", "edital_numero": "10"},
        {"edital_cnpj": "1", "edital_ano": "2025", "edital_numero": "10"},
    ]

    service.data_manager.load_itens = lambda: itens
    result = service.get_itens_by_edital("1", "2026", "10")
    assert result == [itens[0]]
