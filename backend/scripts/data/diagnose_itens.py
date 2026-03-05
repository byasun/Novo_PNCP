"""
Script de diagnóstico para analisar a relação entre editais e itens.

Este script verifica quais editais têm itens, quais não têm, e identifica possíveis problemas.
"""

import os
import sys
import json

# Ajusta sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.storage.data_manager import DataManager


def diagnose():
    """Realiza diagnóstico da relação editais <-> itens."""
    dm = DataManager()
    
    editais = dm.load_editais()
    itens = dm.load_itens()
    
    print("\n" + "="*70)
    print("DIAGNÓSTICO: EDITAIS x ITENS")
    print("="*70)
    
    print(f"\n📊 CONTAGEM GERAL:")
    print(f"  Total de editais: {len(editais)}")
    print(f"  Total de itens: {len(itens)}")
    
    if len(editais) > 0:
        media = len(itens) / len(editais)
        print(f"  Média de itens/edital: {media:.2f}")
    
    # Mapa de itens por edital
    itens_por_edital = {}
    for item in itens:
        chave = (
            item.get('edital_numeroControlePNCP')
            or item.get('edital_ID_C_PNCP')
        )
        if chave:
            if chave not in itens_por_edital:
                itens_por_edital[chave] = 0
            itens_por_edital[chave] += 1
    
    print(f"\n🔍 EDITAIS COM ITENS:")
    print(f"  Editais que têm itens salvos: {len(itens_por_edital)}")
    print(f"  Editais SEM itens: {len(editais) - len(itens_por_edital)}")
    
    # Editais sem itens
    editais_sem_itens = []
    for edital in editais:
        chave = (
            edital.get('numeroControlePNCP')
            or edital.get('ID_C_PNCP')
        )
        if chave not in itens_por_edital:
            editais_sem_itens.append(edital)
    
    print(f"\n⚠️ ANÁLISE DETALHADA:")
    print(f"  Editais com pelo menos 1 item: {len(itens_por_edital)}")
    print(f"  Editais com 0 itens: {len(editais_sem_itens)}")
    
    # Estatísticas de itens por edital
    if itens_por_edital:
        counts = list(itens_por_edital.values())
        min_itens = min(counts)
        max_itens = max(counts)
        media_itens = sum(counts) / len(counts)
        
        print(f"\n📈 DISTRIBUIÇÃO DE ITENS:")
        print(f"  Mínimo de itens em um edital: {min_itens}")
        print(f"  Máximo de itens em um edital: {max_itens}")
        print(f"  Média de itens (entre os com itens): {media_itens:.2f}")
        
        # Quantos editais têm exatamente 1 item
        com_1_item = sum(1 for c in counts if c == 1)
        com_0_item = len(editais_sem_itens)
        
        print(f"\n  Editais com exatamente 1 item: {com_1_item}")
        print(f"  Editais com 0 itens: {com_0_item}")
    
    # Se há muitos editais sem itens, mostra exemplos
    if len(editais_sem_itens) > 0:
        print(f"\n❌ EXEMPLOS DE EDITAIS SEM ITENS (mostrando até 5):")
        for edital in editais_sem_itens[:5]:
            numero = edital.get('numeroControlePNCP')
            cnpj = edital.get('cnpjOrgao')
            ano = edital.get('anoCompra')
            numero_ed = edital.get('numeroCompra')
            print(f"  - {numero} | {cnpj}/{ano}/{numero_ed}")
    
    # Verifica IDs
    print(f"\n🔑 VERIFICAÇÃO DE IDs:")
    editais_sem_id_pncp = sum(1 for e in editais if not e.get('ID_C_PNCP'))
    itens_sem_edital_id = sum(1 for i in itens if not i.get('edital_ID_C_PNCP'))
    
    print(f"  Editais sem ID_C_PNCP: {editais_sem_id_pncp}")
    print(f"  Itens sem edital_ID_C_PNCP: {itens_sem_edital_id}")
    
    # Recomendações
    print(f"\n💡 RECOMENDAÇÕES:")
    if len(editais_sem_itens) > len(editais) * 0.3:
        print(f"  ⚠️ Mais de 30% dos editais não têm itens!")
        print(f"     Próximos passos:")
        print(f"     1. Execute: python scripts/fetch/force_fetch_items.py")
        print(f"     2. Verifique os logs em: /backend/logs/")
        print(f"     3. Verifique a conectividade com a API PNCP")
    else:
        print(f"  ✓ Proporção de itens está aceitável")
    
    print("\n" + "="*70)


if __name__ == '__main__':
    diagnose()
