"""
Script para remover editais e itens publicados há mais de N dias.

Este script mantém apenas editais publicados nos últimos N dias (padrão: 15),
removendo os antigos e seus itens correspondentes. Realiza backup automático dos arquivos antes de modificá-los.

Uso:
    python backend/scripts/data/filter_editais_by_publication_date.py               # Últimos 15 dias
    python backend/scripts/data/filter_editais_by_publication_date.py 30           # Últimos 30 dias
    python backend/scripts/data/filter_editais_by_publication_date.py --dry-run    # Simula sem salvar
"""

import os
import sys
import json
import shutil
from datetime import datetime

# Ajusta sys.path para permitir importação do backend
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.services.editais_service import EditaisService
from backend.config import DATA_DIR
from backend.storage.data_manager import DataManager


def backup_file(file_path):
    """
    Cria backup de um arquivo com timestamp.
    
    Returns:
        Caminho do arquivo de backup ou None se arquivo não existe
    """
    if not os.path.exists(file_path):
        return None
    
    backup_dir = os.path.join(os.path.dirname(file_path), 'backup_' + os.path.basename(file_path).replace('.json', ''))
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f"{os.path.basename(file_path)}_{timestamp}")
    
    try:
        shutil.copy2(file_path, backup_path)
        print(f"✓ Backup criado: {os.path.basename(backup_path)}")
        return backup_path
    except Exception as e:
        print(f"✗ Erro ao criar backup: {e}")
        return None


def main(days=15, dry_run=False):
    """
    Remove editais publicados há mais de N dias e seus itens correspondentes.
    
    Args:
        days: Últimos N dias para manter (padrão: 15)
        dry_run: Se True, simula sem salvar os arquivos
    """
    data_manager = DataManager()
    
    print("\n" + "="*60)
    print(f"FILTRO POR DATA DE PUBLICAÇÃO (últimos {days} dias)")
    print("="*60)
    
    # Carrega editais
    editais = data_manager.load_editais()
    itens = data_manager.load_itens()
    
    if not editais:
        print("✗ Nenhum edital encontrado.")
        return
    
    print(f"\nEDITAIS ANTES: {len(editais)}")
    print(f"ITENS ANTES: {len(itens)}")
    
    # Filtra editais: mantém apenas os últimos N dias
    service = EditaisService()
    editais_recentes = service._filter_editais_by_publication_date(editais, days=days)
    
    removed_count = len(editais) - len(editais_recentes)
    print(f"\n✓ Editais a remover (publicados há mais de {days} dias): {removed_count}")
    print(f"✓ Editais a manter (publicados nos últimos {days} dias): {len(editais_recentes)}")
    
    # Cria set de IDs dos editais que serão mantidos
    edital_ids_to_keep = set(
        e.get('numeroControlePNCP') or e.get('ID_C_PNCP')
        for e in editais_recentes
        if e.get('numeroControlePNCP') or e.get('ID_C_PNCP')
    )
    
    # Filtra itens: mantém apenas itens dos editais que ficarão
    itens_recentes = [
        item for item in itens
        if (
            item.get('edital_numeroControlePNCP') in edital_ids_to_keep
            or item.get('edital_ID_C_PNCP') in edital_ids_to_keep
        )
    ]
    
    removed_items = len(itens) - len(itens_recentes)
    print(f"✓ Itens a remover (dos editais antigos): {removed_items}")
    print(f"✓ Itens a manter: {len(itens_recentes)}")
    
    if dry_run:
        print("\n⚠ MODO SIMULAÇÃO: Nenhum arquivo foi modificado.")
        return
    
    # Faz backup dos arquivos
    print("\n" + "-"*60)
    print("Realizando backups...")
    backup_file(os.path.join(DATA_DIR, "editais.json"))
    backup_file(os.path.join(DATA_DIR, "itens.json"))
    
    # Salva arquivos modificados
    print("\nSalvando arquivos modificados...")
    try:
        data_manager.save_editais(editais_recentes)
        print(f"✓ editais.json atualizado: {len(editais_recentes)} editais")
        
        data_manager.save_itens(itens_recentes)
        print(f"✓ itens.json atualizado: {len(itens_recentes)} itens")
        
        print("\n" + "="*60)
        print("✓ Operação concluída com sucesso!")
        print("="*60)
    except Exception as e:
        print(f"✗ Erro ao salvar arquivos: {e}")
        sys.exit(1)


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    sys.argv = [s for s in sys.argv if s != "--dry-run"]
    
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    
    if dry_run:
        print("⚠ Modo simulação ativado (--dry-run)")
    
    main(days=days, dry_run=dry_run)
