"""Script para limpar dados antigos do sistema PNCP."""

import os
import sys
import json
import logging
import signal
from pathlib import Path
from datetime import datetime

# Permite executar como script dentro de backend/ 
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PARENT_DIR = os.path.abspath(os.path.join(ROOT_DIR, ".."))

# Add parent to sys.path se ao executar de scripts/
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from backend.config import DATA_DIR, EDITAIS_CHECKPOINT_FILE
except ImportError:
    # Fallback: usar valores padrão
    DATA_DIR = os.path.join(ROOT_DIR, "data")
    EDITAIS_CHECKPOINT_FILE = os.path.join(DATA_DIR, ".editais_checkpoint.json")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def clean_editais_data(backup=True):
    """
    Remove arquivo de editais local.
    
    Args:
        backup (bool): Se True, renomeia arquivo com timestamp ao invés de deletar
    
    Returns:
        dict: {'success': bool, 'file_path': str, 'message': str}
    """
    editais_file = os.path.join(DATA_DIR, 'editais.json')
    
    if not os.path.exists(editais_file):
        msg = f"Arquivo de editais não encontrado: {editais_file}"
        logger.info(msg)
        return {'success': True, 'file_path': editais_file, 'message': msg}
    
    try:
        if backup:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(DATA_DIR, f'editais_backup_{timestamp}.json')
            os.rename(editais_file, backup_file)
            msg = f"Arquivo de editais movido para backup: {backup_file}"
            logger.info(msg)
            return {'success': True, 'file_path': backup_file, 'message': msg}
        else:
            os.remove(editais_file)
            msg = f"Arquivo de editais deletado: {editais_file}"
            logger.info(msg)
            return {'success': True, 'file_path': editais_file, 'message': msg}
    
    except Exception as e:
        msg = f"Erro ao limpar editais: {e}"
        logger.error(msg)
        return {'success': False, 'file_path': editais_file, 'message': msg}


def clean_itens_data(backup=True):
    """
    Remove arquivo de itens local.
    
    Args:
        backup (bool): Se True, renomeia arquivo com timestamp ao invés de deletar
    
    Returns:
        dict: {'success': bool, 'file_path': str, 'message': str}
    """
    itens_file = os.path.join(DATA_DIR, 'itens.json')
    
    if not os.path.exists(itens_file):
        msg = f"Arquivo de itens não encontrado: {itens_file}"
        logger.info(msg)
        return {'success': True, 'file_path': itens_file, 'message': msg}
    
    try:
        if backup:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(DATA_DIR, f'itens_backup_{timestamp}.json')
            os.rename(itens_file, backup_file)
            msg = f"Arquivo de itens movido para backup: {backup_file}"
            logger.info(msg)
            return {'success': True, 'file_path': backup_file, 'message': msg}
        else:
            os.remove(itens_file)
            msg = f"Arquivo de itens deletado: {itens_file}"
            logger.info(msg)
            return {'success': True, 'file_path': itens_file, 'message': msg}
    
    except Exception as e:
        msg = f"Erro ao limpar itens: {e}"
        logger.error(msg)
        return {'success': False, 'file_path': itens_file, 'message': msg}


def clean_checkpoint(backup=True):
    """
    Remove arquivo de checkpoint de paginação.
    
    Args:
        backup (bool): Se True, renomeia arquivo com timestamp ao invés de deletar
    
    Returns:
        dict: {'success': bool, 'file_path': str, 'message': str}
    """
    checkpoint_file = EDITAIS_CHECKPOINT_FILE
    
    if not os.path.exists(checkpoint_file):
        msg = f"Arquivo de checkpoint não encontrado: {checkpoint_file}"
        logger.info(msg)
        return {'success': True, 'file_path': checkpoint_file, 'message': msg}
    
    try:
        if backup:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = checkpoint_file.replace('.json', f'_backup_{timestamp}.json')
            os.rename(checkpoint_file, backup_file)
            msg = f"Arquivo de checkpoint movido para backup: {backup_file}"
            logger.info(msg)
            return {'success': True, 'file_path': backup_file, 'message': msg}
        else:
            os.remove(checkpoint_file)
            msg = f"Arquivo de checkpoint deletado: {checkpoint_file}"
            logger.info(msg)
            return {'success': True, 'file_path': checkpoint_file, 'message': msg}
    
    except Exception as e:
        msg = f"Erro ao limpar checkpoint: {e}"
        logger.error(msg)
        return {'success': False, 'file_path': checkpoint_file, 'message': msg}


def clean_all_data(backup=True):
    """
    Remove todos os dados del sistema (editais, itens e checkpoint).
    
    Args:
        backup (bool): Se True, cria backups ao invés de deletar
    
    Returns:
        dict: Resultados de cada limpeza
    """
    logger.info("=" * 60)
    logger.info("Iniciando limpeza de dados antigos")
    logger.info("=" * 60)
    
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    
    results = {
        'editais': clean_editais_data(backup=backup),
        'itens': clean_itens_data(backup=backup),
        'checkpoint': clean_checkpoint(backup=backup),
        'backup_enabled': backup,
        'timestamp': datetime.now().isoformat()
    }
    
    # Summary
    success_count = sum(1 for r in [results['editais'], results['itens'], results['checkpoint']] if r['success'])
    logger.info("=" * 60)
    logger.info(f"Limpeza concluída: {success_count}/3 operações bem-sucedidas")
    logger.info(f"Dados com backup: {backup}")
    logger.info("=" * 60)
    
    return results


def print_summary(results):
    """Exibe resumo da limpeza de forma legível."""
    print("\n" + "=" * 70)
    print("RESUMO DA LIMPEZA DE DADOS")
    print("=" * 70)
    print(f"Timestamp: {results['timestamp']}")
    print(f"Backup Ativado: {'Sim' if results['backup_enabled'] else 'Não'}")
    print("-" * 70)
    
    for data_type, result in [('Editais', results['editais']), 
                               ('Itens', results['itens']), 
                               ('Checkpoint', results['checkpoint'])]:
        status = "✓ OK" if result['success'] else "✗ ERRO"
        print(f"{data_type:15} {status:8} - {result['message']}")
    
    print("=" * 70 + "\n")


def signal_handler(signum, frame):
    """Handler para Ctrl+C - sai graciosamente."""
    print("\n\n⚠️  Interrupção solicitada (Ctrl+C). Finalizando...")
    sys.exit(0)


if __name__ == "__main__":
    # Registra handler para Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Limpa dados antigos do sistema PNCP'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Deleta arquivos ao invés de criar backups (cuidado!)'
    )
    parser.add_argument(
        '--type',
        choices=['all', 'editais', 'itens', 'checkpoint'],
        default='all',
        help='Tipo de dados a limpar (padrão: all)'
    )
    
    args = parser.parse_args()
    backup = not args.no_backup
    
    if args.type == 'all':
        results = clean_all_data(backup=backup)
        print_summary(results)
    elif args.type == 'editais':
        result = clean_editais_data(backup=backup)
        logger.info(f"Editais: {result['message']}")
    elif args.type == 'itens':
        result = clean_itens_data(backup=backup)
        logger.info(f"Itens: {result['message']}")
    elif args.type == 'checkpoint':
        result = clean_checkpoint(backup=backup)
        logger.info(f"Checkpoint: {result['message']}")
