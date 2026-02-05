"""Testes unitários do EditaisService."""

from backend.services.editais_service import EditaisService


def test_generate_edital_key_prefers_orgao_cnpj():
    # Deve preferir cnpj do órgão quando disponível
    service = EditaisService()
    edital = {
        "orgaoEntidade": {"cnpj": "123"},
        "cnpjOrgao": "999",
        "anoCompra": 2026,
        "numeroCompra": 10,
    }
    key = service._generate_edital_key(edital)
    assert key == "123_2026_10"


def test_generate_edital_key_fallbacks():
    # Deve usar cnpjOrgao quando orgaoEntidade não existir
    service = EditaisService()
    edital = {
        "cnpjOrgao": "555",
        "anoCompra": 2025,
        "numeroCompra": 7,
    }
    key = service._generate_edital_key(edital)
    assert key == "555_2025_7"


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
