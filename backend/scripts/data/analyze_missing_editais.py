"""
Script para analisar estrutura de editais faltando.

Identifica quais campos estão faltando em editais que não têm itens.
Mostra a estrutura JSON para diagnóstico.
"""

import os
import sys
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.storage.data_manager import DataManager


def analyze_missing_editais():
    """Analisa a estrutura de editais sem itens."""
    dm = DataManager()
    editais = dm.load_editais()
    itens = dm.load_itens()
    
    # Editais com itens
    editais_com_itens = set()
    for item in itens:
        chave = (
            item.get('edital_numeroControlePNCP')
            or item.get('edital_ID_C_PNCP')
        )
        if chave:
            editais_com_itens.add(chave)
    
    # Editais sem itens
    editais_faltando = [
        e for e in editais
        if (e.get('numeroControlePNCP') or e.get('ID_C_PNCP')) not in editais_com_itens
    ]
    
    print("\n" + "="*70)
    print(f"ANÁLISE DE EDITAIS SEM ITENS ({len(editais_faltando)} editais)")
    print("="*70)
    
    # Analisa campos ausentes
    campos_faltando = {
        'cnpjOrgao': 0,
        'anoCompra': 0,
        'numeroCompra': 0,
        'orgaoEntidade': 0,
        'dataPublicacaoPncp': 0,
    }
    
    print("\n🔍 CAMPOS AUSENTES NOS EDITAIS:")
    for edital in editais_faltando:
        if not edital.get('cnpjOrgao'):
            campos_faltando['cnpjOrgao'] += 1
        if not edital.get('anoCompra'):
            campos_faltando['anoCompra'] += 1
        if not edital.get('numeroCompra'):
            campos_faltando['numeroCompra'] += 1
        if not edital.get('orgaoEntidade'):
            campos_faltando['orgaoEntidade'] += 1
        if not edital.get('dataPublicacaoPncp'):
            campos_faltando['dataPublicacaoPncp'] += 1
    
    for campo, count in campos_faltando.items():
        porcentagem = (count / len(editais_faltando)) * 100 if editais_faltando else 0
        print(f"  {campo}: {count} ({porcentagem:.1f}%)")
    
    # Mostra exemplos
    print(f"\n📋 EXEMPLOS DE EDITAIS SEM ITENS (primeiros 3):")
    for i, edital in enumerate(editais_faltando[:3], 1):
        print(f"\n  Edital {i}:")
        print(f"    numeroControlePNCP: {edital.get('numeroControlePNCP')}")
        print(f"    ID_C_PNCP: {edital.get('ID_C_PNCP')}")
        print(f"    cnpjOrgao: {edital.get('cnpjOrgao')}")
        print(f"    anoCompra: {edital.get('anoCompra')}")
        print(f"    numeroCompra: {edital.get('numeroCompra')}")
        print(f"    orgaoEntidade: {edital.get('orgaoEntidade', {}).get('cnpj') if edital.get('orgaoEntidade') else 'N/A'}")
        print(f"    dataPublicacaoPncp: {edital.get('dataPublicacaoPncp')}")
        print(f"\n    JSON completo:")
        print(f"    {json.dumps(edital, indent=6, ensure_ascii=False)[:500]}...")
    
    print("\n" + "="*70)


if __name__ == '__main__':
    analyze_missing_editais()
