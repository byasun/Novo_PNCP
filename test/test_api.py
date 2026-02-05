"""Teste de integração para validar modalidades na API PNCP."""

#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "backend", ".env"))

API_BASE_URL = os.getenv("API_BASE_URL")
if not API_BASE_URL:
    raise RuntimeError("Missing API_BASE_URL in backend/.env")

# Testa diferentes códigos de modalidade
for codigo in range(1, 10):
    r = requests.get(
        f'{API_BASE_URL}/contratacoes/publicacao',
        params={
            'dataInicial': '20260101',
            'dataFinal': '20260202',
            'codigoModalidadeContratacao': str(codigo),
            'pagina': '1'
        }
    )
    
    if r.status_code == 200:
        data = r.json()
        if data.get('data'):
            modalidades = set(x.get('modalidadeNome') for x in data['data'][:5])
            print(f"Código {codigo}: {list(modalidades)[0] if modalidades else 'Sem dados'} - Total: {len(data['data'])}")
        else:
            print(f"Código {codigo}: Sem dados")
    else:
        print(f"Código {codigo}: Erro {r.status_code}")
