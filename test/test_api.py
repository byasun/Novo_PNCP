#!/usr/bin/env python3
import requests
import json

# Test different modalidade codes
for codigo in range(1, 10):
    r = requests.get(
        'https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao',
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
