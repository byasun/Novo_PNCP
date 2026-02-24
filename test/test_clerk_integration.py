
"""
Testes de integração para endpoints protegidos por Clerk.
Valida acesso autorizado e tratamento de token inválido.
"""

import requests
import os
import pytest

# Define a URL base e o JWT de teste a partir das variáveis de ambiente
BASE_URL = os.getenv('CLERK_TEST_API_URL', 'http://localhost:5000')
CLERK_JWT = os.getenv('CLERK_TEST_JWT', '')

# Testa acesso autorizado ao endpoint protegido pelo Clerk
@pytest.mark.skipif(not CLERK_JWT, reason="JWT Clerk não definido para teste")
def test_clerk_protected_endpoint():
    url = f"{BASE_URL}/api/secure-clerk"
    headers = {"Authorization": f"Bearer {CLERK_JWT}"}
    resp = requests.get(url, headers=headers)
    assert resp.status_code == 200, f"Status inesperado: {resp.status_code}"
    data = resp.json()
    assert "user" in data, "Resposta não contém dados do usuário Clerk"
    assert data["message"] == "Acesso autorizado via Clerk!"

# Testa resposta ao uso de token inválido
@pytest.mark.skipif(not CLERK_JWT, reason="JWT Clerk não definido para teste")
def test_clerk_invalid_token():
    url = f"{BASE_URL}/api/secure-clerk"
    headers = {"Authorization": "Bearer invalid.jwt.token"}
    resp = requests.get(url, headers=headers)
    assert resp.status_code == 401, f"Status esperado 401, obtido: {resp.status_code}"
    data = resp.json()
    assert "error" in data
