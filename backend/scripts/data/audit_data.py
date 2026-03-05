"""
Script unificado para auditoria e estatísticas dos dados (editais e itens).

Fornece estatísticas e contagens de dados armazenados em editais.json e itens.json.

Uso:
    python backend/scripts/data/audit_data.py                      # Menu interativo
    python backend/scripts/data/audit_data.py --count              # Conta editais e itens
    python backend/scripts/data/audit_data.py --numerocontrol      # Analisa numeroControlePNCP
    python backend/scripts/data/audit_data.py --all                # Todas as estatísticas
"""

import os
import sys
import json
import argparse
from collections import Counter

# Adiciona a pasta raiz ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))
EDITAIS_PATH = os.path.join(DATA_DIR, 'editais.json')
ITENS_PATH = os.path.join(DATA_DIR, 'itens.json')


# ===== AUDITORIA 1: Contagem de Editais e Itens =====
def audit_count():
    """Conta e exibe total de editais e itens."""
    n_editais = 0
    n_itens = 0
    
    # Conta editais
    try:
        with open(EDITAIS_PATH, 'r', encoding='utf-8') as f:
            editais = json.load(f)
        n_editais = len(editais)
    except Exception as e:
        print(f'✗ Erro ao ler editais.json: {e}')
    
    # Conta itens
    try:
        with open(ITENS_PATH, 'r', encoding='utf-8') as f:
            itens = json.load(f)
        n_itens = len(itens)
    except Exception as e:
        print(f'✗ Erro ao ler itens.json: {e}')
    
    print("\n" + "="*60)
    print("AUDITORIA 1: Contagem de Editais e Itens")
    print("="*60)
    print(f"✓ Editais encontrados: {n_editais}")
    print(f"✓ Itens encontrados: {n_itens}")
    
    if n_editais > 0 and n_itens > 0:
        razao = n_itens / n_editais
        print(f"  Média de itens por edital: {razao:.2f}")


# ===== AUDITORIA 2: Análise de numeroControlePNCP =====
def audit_numerocontrol():
    """Analisa e exibe estatísticas sobre numeroControlePNCP."""
    try:
        with open(EDITAIS_PATH, 'r', encoding='utf-8') as f:
            editais = json.load(f)
    except Exception as e:
        print(f'✗ Erro ao ler editais.json: {e}')
        return
    
    numeros = [e.get('numeroControlePNCP') for e in editais if e.get('numeroControlePNCP')]
    
    print("\n" + "="*60)
    print("AUDITORIA 2: Análise de numeroControlePNCP")
    print("="*60)
    print(f"Total de editais: {len(editais)}")
    print(f"Editais com numeroControlePNCP: {len(numeros)}")
    
    if numeros:
        counter = Counter(numeros)
        unicos = sum(1 for v in counter.values() if v == 1)
        repetidos = sum(1 for v in counter.values() if v > 1)
        
        print(f"\n✓ numeroControlePNCP únicos: {unicos}")
        print(f"⚠ numeroControlePNCP que aparecem mais de uma vez: {repetidos}")
        
        if repetidos > 0:
            print("\n⚠ Exemplos de numeroControlePNCP duplicados:")
            dup_items = [(k, v) for k, v in counter.items() if v > 1]
            for numero, count in dup_items[:5]:
                print(f"  {numero}: {count} vezes")
    else:
        print("✗ Nenhum numero de controle PNCP encontrado")


# ===== AUDITORIA 3: Resumo Geral =====
def audit_general_summary():
    """Exibe resumo geral de todas as estatísticas."""
    n_editais = 0
    n_itens = 0
    
    # Carrega editais
    try:
        with open(EDITAIS_PATH, 'r', encoding='utf-8') as f:
            editais = json.load(f)
        n_editais = len(editais)
    except Exception as e:
        print(f'✗ Erro ao ler editais.json: {e}')
        editais = []
    
    # Carrega itens
    try:
        with open(ITENS_PATH, 'r', encoding='utf-8') as f:
            itens = json.load(f)
        n_itens = len(itens)
    except Exception as e:
        print(f'✗ Erro ao ler itens.json: {e}')
        itens = []
    
    # Analisa numeroControlePNCP
    numeros = [e.get('numeroControlePNCP') for e in editais if e.get('numeroControlePNCP')]
    counter = Counter(numeros) if numeros else {}
    unicos_numero = sum(1 for v in counter.values() if v == 1) if counter else 0
    repetidos_numero = sum(1 for v in counter.values() if v > 1) if counter else 0
    
    print("\n" + "="*60)
    print("AUDITORIA GERAL: Resumo de Dados")
    print("="*60)
    print(f"\n📊 Contagem:")
    print(f"  Editais: {n_editais}")
    print(f"  Itens: {n_itens}")
    if n_editais > 0 and n_itens > 0:
        razao = n_itens / n_editais
        print(f"  Média de itens/edital: {razao:.2f}")
    
    print(f"\n🔢 numeroControlePNCP:")
    print(f"  Editais com numeroControlePNCP: {len(numeros)}")
    print(f"  Únicos: {unicos_numero}")
    print(f"  Duplicados: {repetidos_numero}")
    
    # Análise de IDs
    id_c_pncp_editais = sum(1 for e in editais if e.get('ID_C_PNCP'))
    id_c_pncp_itens = sum(1 for i in itens if i.get('edital_ID_C_PNCP'))
    
    print(f"\n🔗 ID_C_PNCP:")
    print(f"  Editais com ID_C_PNCP: {id_c_pncp_editais}")
    print(f"  Itens com edital_ID_C_PNCP: {id_c_pncp_itens}")
    
    # Análise de dados principais
    editais_com_campo = {
        'numeroCompra': sum(1 for e in editais if e.get('numeroCompra')),
        'anoCompra': sum(1 for e in editais if e.get('anoCompra')),
        'cnpjOrgao': sum(1 for e in editais if e.get('cnpjOrgao')),
    }
    
    print(f"\n📝 Campos em Editais:")
    for campo, count in editais_com_campo.items():
        print(f"  {campo}: {count}")
    
    print("\n" + "="*60)


# ===== MENU INTERATIVO =====
def main_interactive():
    """Menu principal interativo."""
    print("\n" + "="*60)
    print("AUDITORIA DE DADOS - PNCP")
    print("="*60)
    print("\nEscolha uma auditoria:")
    print("1: Contagem de editais e itens")
    print("2: Análise de numeroControlePNCP")
    print("3: Resumo geral (todas as estatísticas)")
    print("4: Sair")
    
    while True:
        try:
            opcao = int(input("\nEscolha uma opção (1-4): "))
            if 1 <= opcao <= 4:
                break
            else:
                print("✗ Opção inválida. Tente novamente.")
        except ValueError:
            print("✗ Entrada inválida. Digite um número.")
    
    if opcao == 1:
        audit_count()
    elif opcao == 2:
        audit_numerocontrol()
    elif opcao == 3:
        audit_count()
        audit_numerocontrol()
        audit_general_summary()
    else:
        print("Saindo...")
        return


# ===== CLI COM ARGUMENTOS =====
def main():
    """Função principal com suporte a argumentos CLI."""
    parser = argparse.ArgumentParser(
        description='Auditoria e estatísticas de dados (editais e itens)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Menu interativo
  python backend/scripts/data/audit_data.py
  
  # Contar editais e itens
  python backend/scripts/data/audit_data.py --count
  
  # Analisar numeroControlePNCP
  python backend/scripts/data/audit_data.py --numerocontrol
  
  # Resumo geral
  python backend/scripts/data/audit_data.py --all
        """
    )
    
    parser.add_argument(
        '--count',
        action='store_true',
        help='Exibe contagem de editais e itens'
    )
    parser.add_argument(
        '--numerocontrol',
        action='store_true',
        help='Analisa estatísticas de numeroControlePNCP'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Exibe resumo geral com todas as estatísticas'
    )
    
    args = parser.parse_args()
    
    # Se alguma flag foi passada
    if args.count or args.numerocontrol or args.all:
        if args.count or args.all:
            audit_count()
        if args.numerocontrol or args.all:
            audit_numerocontrol()
        
        if args.all:
            audit_general_summary()
        
        return
    
    # Caso padrão: menu interativo
    main_interactive()


if __name__ == '__main__':
    main()
