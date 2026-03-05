"""
Script para forçar busca de itens para todos os editais sem itens.

Identifica editais que não têm itens salvos e tenta buscá-los de novo,
com logging detalhado de erros e falhas.

Uso:
    python scripts/data/fetch_missing_items.py              # Modo interativo
    python scripts/data/fetch_missing_items.py --force      # Força busca sem confirmação
    python scripts/data/fetch_missing_items.py --dry-run    # Simula sem salvar
"""

import os
import sys
import logging

# Ajusta sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.storage.data_manager import DataManager
from backend.services.editais_service import EditaisService
from backend.config import LOGS_DIR

# Configura logging detalhado
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(LOGS_DIR, 'fetch_missing_items.log'))
    ]
)
logger = logging.getLogger(__name__)


def find_missing_editais():
    """Identifica editais sem itens salvos."""
    dm = DataManager()
    editais = dm.load_editais()
    itens = dm.load_itens()
    
    # Cria mapa de editais com itens
    editais_com_itens = set()
    for item in itens:
        chave = (
            item.get('edital_numeroControlePNCP')
            or item.get('edital_ID_C_PNCP')
        )
        if chave:
            editais_com_itens.add(chave)
    
    # Identifica editais faltando
    editais_faltando = []
    for edital in editais:
        chave = (
            edital.get('numeroControlePNCP')
            or edital.get('ID_C_PNCP')
        )
        if chave not in editais_com_itens:
            editais_faltando.append(edital)
    
    return editais_faltando, len(editais), len(itens)


def fetch_missing(editais_faltando, dry_run=False):
    """Busca itens para editais faltando."""
    if not editais_faltando:
        print("✓ Todos os editais já têm itens!")
        return
    
    print(f"\n{'='*70}")
    print(f"BUSCA DE ITENS FALTANDO")
    print(f"{'='*70}\n")
    print(f"Editais sem itens: {len(editais_faltando)}")
    
    if dry_run:
        print("\n⚠ MODO SIMULAÇÃO (--dry-run): Mostrando editais faltando sem buscar\n")
        for i, edital in enumerate(editais_faltando[:10], 1):
            numero = edital.get('numeroControlePNCP', 'N/A')
            cnpj = edital.get('cnpjOrgao', 'None')
            ano = edital.get('anoCompra', 'N/A')
            numero_ed = edital.get('numeroCompra', 'N/A')
            print(f"  {i}. {numero} | CNPJ={cnpj} | {ano}/{numero_ed}")
        
        if len(editais_faltando) > 10:
            print(f"  ... e mais {len(editais_faltando) - 10} editais")
        return
    
    # Busca itens
    service = EditaisService()
    
    print("Iniciando busca de itens (isso pode levar alguns minutos)...\n")
    
    try:
        all_itens = service.fetch_itens_for_all_editais(
            editais_faltando,
            skip_existing=False  # ← FORÇA busca mesmo que haja erro anterior
        )
        
        print(f"\n✓ Busca concluída!")
        print(f"  Itens buscados: {len(all_itens)}")
        
        # Verifica resultado
        dm = DataManager()
        itens_salvos = dm.load_itens()
        
        print(f"  Itens totais salvos: {len(itens_salvos)}")
        
        # Reidentifica faltando após busca
        editais_com_itens = set()
        for item in itens_salvos:
            chave = (
                item.get('edital_numeroControlePNCP')
                or item.get('edital_ID_C_PNCP')
            )
            if chave:
                editais_com_itens.add(chave)
        
        ainda_faltando = sum(
            1 for e in editais_faltando
            if (e.get('numeroControlePNCP') or e.get('ID_C_PNCP')) not in editais_com_itens
        )
        
        print(f"  Editais ainda sem itens: {ainda_faltando}")
        
        if ainda_faltando > 0:
            print(f"\n⚠ Ainda há {ainda_faltando} editais sem itens!")
            print(f"  Verifique os logs: {os.path.join(LOGS_DIR, 'fetch_missing_items.log')}")
        else:
            print(f"\n✓ Sucesso! Todos os editais têm itens salvos!")
    
    except KeyboardInterrupt:
        print("\n⚠ Busca interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Erro durante busca: {e}")
        logger.exception("Erro completo:")
        sys.exit(1)


def main():
    """Função principal."""
    dry_run = '--dry-run' in sys.argv
    force = '--force' in sys.argv
    
    logger.info("="*70)
    logger.info("Iniciando script de busca de itens faltando")
    logger.info("="*70)
    
    # Identifica faltando
    editais_faltando, total_editais, total_itens = find_missing_editais()
    
    print(f"\n{'='*70}")
    print(f"DIAGNÓSTICO RÁPIDO")
    print(f"{'='*70}")
    print(f"Total de editais: {total_editais}")
    print(f"Total de itens salvos: {total_itens}")
    print(f"Editais SEM itens: {len(editais_faltando)} ({len(editais_faltando)/total_editais*100:.1f}%)")
    
    if not editais_faltando:
        print("\n✓ Nenhum edital faltando!")
        return
    
    # Modo simulação
    if dry_run:
        print("\n📋 Modo simulação ativado...")
        fetch_missing(editais_faltando, dry_run=True)
        return
    
    # Confirmação se não forçado
    if not force:
        print(f"\nVocê deseja buscar itens para {len(editais_faltando)} editais faltando?")
        confirm = input("Continuar? (s/N): ").strip().lower()
        if confirm != 's':
            print("Abortado.")
            return
    
    # Busca
    fetch_missing(editais_faltando, dry_run=False)


if __name__ == '__main__':
    main()
