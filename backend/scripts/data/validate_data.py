"""
Script unificado para validação e verificação de integridade de dados (editais e itens).

Realiza múltiplas verificações de integridade referencial, duplicidade de IDs e consistência de dados.

Uso:
    python backend/scripts/data/validate_data.py                          # Menu interativo
    python backend/scripts/data/validate_data.py --composite-keys         # Verifica chaves compostas duplicadas
    python backend/scripts/data/validate_data.py --duplicate-ids          # Verifica ID_C_PNCP duplicados
    python backend/scripts/data/validate_data.py --consistency            # Valida vínculo editais-itens
    python backend/scripts/data/validate_data.py --link-integrity         # Valida campo edital_ID_C_PNCP
    python backend/scripts/data/validate_data.py --all                    # Executa todas as validações
"""

import os
import sys
import json
import argparse
from collections import Counter

# Garante que o diretório raiz do projeto esteja no sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.config import DATA_DIR
from backend.storage.data_manager import DataManager


# ===== VALIDAÇÃO 1: Chaves Compostas Duplicadas =====
def validate_composite_keys():
    """Identifica chaves compostas duplicadas em editais.json."""
    editais_path = os.path.join(DATA_DIR, "editais.json")
    
    if not os.path.exists(editais_path):
        print(f"✗ Arquivo não encontrado: {editais_path}")
        return
    
    with open(editais_path, "r", encoding="utf-8") as f:
        editais = json.load(f)
    
    def chave_composta(edital):
        cnpj = (edital.get("orgaoEntidade", {}) or {}).get("cnpj") or edital.get("cnpjOrgao")
        ano = edital.get("anoCompra") or edital.get("ano")
        numero = edital.get("numeroCompra") or edital.get("numero")
        return f"{cnpj}_{ano}_{numero}"
    
    chaves = [chave_composta(e) for e in editais]
    counter = Counter(chaves)
    duplicadas = {k: v for k, v in counter.items() if v > 1}
    
    print("\n" + "="*60)
    print("VALIDAÇÃO 1: Chaves Compostas Duplicadas (CNPJ_Ano_Número)")
    print("="*60)
    print(f"Total de editais: {len(editais)}")
    print(f"Chaves compostas únicas: {len(counter)}")
    print(f"Chaves compostas duplicadas: {len(duplicadas)}")
    
    if duplicadas:
        print("⚠ Exemplos de chaves duplicadas:")
        for chave, count in list(duplicadas.items())[:10]:
            print(f"  {chave}: {count} vezes")
    else:
        print("✓ Nenhuma chave composta duplicada encontrada.")


# ===== VALIDAÇÃO 2: ID_C_PNCP Duplicados =====
def validate_duplicate_ids():
    """Verifica duplicidade de ID_C_PNCP em editais.json e itens.json."""
    editais_path = os.path.join(DATA_DIR, "editais.json")
    itens_path = os.path.join(DATA_DIR, "itens.json")
    
    def verifica_duplicados(path, campo="ID_C_PNCP"):
        """Verifica e retorna dicionário com IDs duplicados."""
        if not os.path.exists(path):
            return {}
        with open(path, encoding="utf-8") as f:
            dados = json.load(f)
        ids = [obj.get(campo) for obj in dados if campo in obj]
        contagem = Counter(ids)
        duplicados = {k: v for k, v in contagem.items() if v > 1}
        return duplicados
    
    print("\n" + "="*60)
    print("VALIDAÇÃO 2: ID_C_PNCP Duplicados")
    print("="*60)
    
    for arquivo, nome in [(editais_path, "Editais"), (itens_path, "Itens")]:
        duplicados = verifica_duplicados(arquivo)
        print(f"\n{nome}: {arquivo}")
        if duplicados:
            print(f"  ⚠ Quantidade de ID_C_PNCP duplicados: {len(duplicados)}")
            for id_dup, count in list(duplicados.items())[:5]:
                print(f"    {id_dup}: {count} vezes")
        else:
            print(f"  ✓ Nenhum ID_C_PNCP duplicado encontrado")


# ===== VALIDAÇÃO 3: Consistency Editais <-> Itens =====
def validate_consistency():
    """Valida vínculo entre editais e itens pelo ID_C_PNCP."""
    data_manager = DataManager()
    editais = data_manager.load_editais()
    itens = data_manager.load_itens()
    
    # Sets de IDs
    edital_ids = set(str(edital.get("ID_C_PNCP", "")) 
                     for edital in editais if str(edital.get("ID_C_PNCP", "")))
    item_edital_ids = set(str(item.get("edital_ID_C_PNCP", "")) 
                          for item in itens if str(item.get("edital_ID_C_PNCP", "")))
    
    # Análises
    idc_sem_item = edital_ids - item_edital_ids
    item_sem_edital = item_edital_ids - edital_ids
    idc_com_item = edital_ids & item_edital_ids
    item_vinculado_edital = item_edital_ids & edital_ids
    
    print("\n" + "="*60)
    print("VALIDAÇÃO 3: Vínculo Editais <-> Itens (ID_C_PNCP)")
    print("="*60)
    print(f"\nTotal de editais (ID_C_PNCP): {len(edital_ids)}")
    print(f"Total de itens (edital_ID_C_PNCP únicos): {len(item_edital_ids)}\n")
    print(f"✓ ID_C_PNCP com itens vinculados: {len(idc_com_item)}")
    print(f"⚠ ID_C_PNCP sem itens vinculados: {len(idc_sem_item)}")
    print(f"⚠ edital_ID_C_PNCP sem edital correspondente: {len(item_sem_edital)}")
    
    if idc_sem_item:
        print(f"\n⚠ Exemplos de editais sem itens:")
        for id_val in list(idc_sem_item)[:5]:
            print(f"  {id_val}")


# ===== VALIDAÇÃO 4: Link Integrity (edital_ID_C_PNCP) =====
def validate_link_integrity():
    """Verifica se todos os itens têm edital_ID_C_PNCP válido."""
    data_manager = DataManager()
    editais = data_manager.load_editais()
    itens = data_manager.load_itens()
    
    ids_editais = set(e.get("ID_C_PNCP") for e in editais if e.get("ID_C_PNCP"))
    total_itens = len(itens)
    sem_id = 0
    id_inexistente = 0
    exemplos_sem_id = []
    exemplos_id_inexistente = []
    
    for item in itens:
        eid = item.get("edital_ID_C_PNCP")
        if not eid:
            sem_id += 1
            if len(exemplos_sem_id) < 3:
                exemplos_sem_id.append(item)
        elif eid not in ids_editais:
            id_inexistente += 1
            if len(exemplos_id_inexistente) < 3:
                exemplos_id_inexistente.append(item)
    
    print("\n" + "="*60)
    print("VALIDAÇÃO 4: Integridade de Vínculo (edital_ID_C_PNCP)")
    print("="*60)
    print(f"\nTotal de itens: {total_itens}")
    print(f"✓ Itens com edital_ID_C_PNCP válido: {total_itens - sem_id - id_inexistente}")
    print(f"⚠ Itens sem campo edital_ID_C_PNCP: {sem_id}")
    print(f"⚠ Itens com edital_ID_C_PNCP inválido: {id_inexistente}")
    
    if exemplos_sem_id:
        print("\n⚠ Exemplos de itens sem edital_ID_C_PNCP:")
        for ex in exemplos_sem_id:
            print(f"  {ex.get('numeroItem', 'N/A')}")
    if exemplos_id_inexistente:
        print("\n⚠ Exemplos de itens com edital_ID_C_PNCP inexistente:")
        for ex in exemplos_id_inexistente:
            print(f"  Item: {ex.get('numeroItem', 'N/A')}, edital_ID_C_PNCP: {ex.get('edital_ID_C_PNCP')}")


# ===== MENU INTERATIVO =====
def main_interactive():
    """Menu principal interativo."""
    print("\n" + "="*60)
    print("VALIDAÇÃO DE INTEGRIDADE DE DADOS - PNCP")
    print("="*60)
    print("\nEscolha uma validação:")
    print("1: Chaves compostas duplicadas")
    print("2: ID_C_PNCP duplicados")
    print("3: Vínculo Editais <-> Itens")
    print("4: Integridade de Vínculo (edital_ID_C_PNCP)")
    print("5: Executar todas as validações")
    print("6: Sair")
    
    while True:
        try:
            opcao = int(input("\nEscolha uma opção (1-6): "))
            if 1 <= opcao <= 6:
                break
            else:
                print("✗ Opção inválida. Tente novamente.")
        except ValueError:
            print("✗ Entrada inválida. Digite um número.")
    
    if opcao == 1:
        validate_composite_keys()
    elif opcao == 2:
        validate_duplicate_ids()
    elif opcao == 3:
        validate_consistency()
    elif opcao == 4:
        validate_link_integrity()
    elif opcao == 5:
        validate_composite_keys()
        validate_duplicate_ids()
        validate_consistency()
        validate_link_integrity()
        print("\n" + "="*60)
        print("✓ Todas as validações concluídas!")
        print("="*60)
    else:
        print("Saindo...")
        return


# ===== CLI COM ARGUMENTOS =====
def main():
    """Função principal com suporte a argumentos CLI."""
    parser = argparse.ArgumentParser(
        description='Valida e verifica integridade dos dados (editais e itens)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Menu interativo
  python backend/scripts/data/validate_data.py
  
  # Verificar chaves compostas duplicadas
  python backend/scripts/data/validate_data.py --composite-keys
  
  # Executar todas as validações
  python backend/scripts/data/validate_data.py --all
        """
    )
    
    parser.add_argument(
        '--composite-keys',
        action='store_true',
        help='Verifica chaves compostas duplicadas (CNPJ_Ano_Número)'
    )
    parser.add_argument(
        '--duplicate-ids',
        action='store_true',
        help='Verifica ID_C_PNCP duplicados em editais e itens'
    )
    parser.add_argument(
        '--consistency',
        action='store_true',
        help='Valida vínculo entre editais e itens'
    )
    parser.add_argument(
        '--link-integrity',
        action='store_true',
        help='Valida integridade do campo edital_ID_C_PNCP em itens'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Executa todas as validações'
    )
    
    args = parser.parse_args()
    
    # Se alguma flag foi passada
    if args.composite_keys or args.duplicate_ids or args.consistency or args.link_integrity or args.all:
        if args.composite_keys or args.all:
            validate_composite_keys()
        if args.duplicate_ids or args.all:
            validate_duplicate_ids()
        if args.consistency or args.all:
            validate_consistency()
        if args.link_integrity or args.all:
            validate_link_integrity()
        
        if args.all:
            print("\n" + "="*60)
            print("✓ Todas as validações concluídas!")
            print("="*60)
        return
    
    # Caso padrão: menu interativo
    main_interactive()


if __name__ == "__main__":
    main()
