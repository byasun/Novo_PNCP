"""
Script unificado para restaurar backups de editais e itens.

Este script permite restaurar backups de editais, itens ou ambos de forma interativa.
Oferece menu para selecionar quais dados restaurar e qual backup escolher.

Uso:
    python backend/scripts/data/restore_backup.py                    # Menu interativo completo
    python backend/scripts/data/restore_backup.py --editais          # Restaurar apenas editais
    python backend/scripts/data/restore_backup.py --itens            # Restaurar apenas itens
    python backend/scripts/data/restore_backup.py --all              # Restaurar ambos automaticamente
"""

import os
import shutil
import glob
import sys
import argparse


def list_backups(backup_dir, data_type):
    """
    Lista os arquivos de backup disponíveis em um diretório.
    
    Args:
        backup_dir: Caminho do diretório de backup
        data_type: Tipo de dado ('editais' ou 'itens') para pattern matching
    
    Returns:
        Lista de arquivos de backup ordenados
    """
    if not os.path.exists(backup_dir):
        return []
    
    pattern_file = f"{data_type}.json_*"
    backup_files = sorted(glob.glob(os.path.join(backup_dir, pattern_file)))
    return backup_files


def restore_backup(backup_file, dest_file, data_type):
    """
    Restaura um arquivo de backup para o destino.
    
    Args:
        backup_file: Caminho do arquivo de backup
        dest_file: Caminho de destino
        data_type: Tipo de dado ('editais' ou 'itens') para mensagens
    
    Returns:
        Tupla (sucesso: bool, mensagem: str)
    """
    try:
        print(f'Restaurando backup de {data_type}: {os.path.basename(backup_file)} -> {os.path.basename(dest_file)}')
        shutil.copy2(backup_file, dest_file)
        print(f'✓ Restauração de {data_type} concluída com sucesso.')
        return True, f"Backup de {data_type} restaurado"
    except Exception as e:
        print(f'✗ Erro ao restaurar {data_type}: {e}')
        return False, f"Erro ao restaurar {data_type}: {e}"


def restore_editais_interactive():
    """Restaura editais de forma interativa."""
    BACKUP_DIR = os.path.join(os.path.dirname(__file__), '../../data/backup_editais')
    RESTORE_DIR = os.path.join(os.path.dirname(__file__), '../../data')
    
    backup_files = list_backups(BACKUP_DIR, 'editais')
    
    if not backup_files:
        print('✗ Nenhum arquivo de backup de editais encontrado.')
        return False
    
    print(f'\nBackups de editais disponíveis ({len(backup_files)}):')
    for idx, file in enumerate(backup_files):
        print(f'{idx + 1}: {os.path.basename(file)}')
    
    while True:
        try:
            escolha = int(input(f'Escolha o número do backup para restaurar (1-{len(backup_files)}): '))
            if 1 <= escolha <= len(backup_files):
                break
            else:
                print('✗ Opção inválida. Tente novamente.')
        except ValueError:
            print('✗ Entrada inválida. Digite um número.')
    
    backup_file = backup_files[escolha - 1]
    dest_file = os.path.join(RESTORE_DIR, 'editais.json')
    
    sucesso, msg = restore_backup(backup_file, dest_file, 'editais')
    return sucesso


def restore_itens_interactive():
    """Restaura itens de forma interativa."""
    BACKUP_DIR = os.path.join(os.path.dirname(__file__), '../../data/backup_itens')
    RESTORE_DIR = os.path.join(os.path.dirname(__file__), '../../data')
    
    backup_files = list_backups(BACKUP_DIR, 'itens')
    
    if not backup_files:
        print('✗ Nenhum arquivo de backup de itens encontrado.')
        return False
    
    print(f'\nBackups de itens disponíveis ({len(backup_files)}):')
    for idx, file in enumerate(backup_files):
        print(f'{idx + 1}: {os.path.basename(file)}')
    
    while True:
        try:
            escolha = int(input(f'Escolha o número do backup para restaurar (1-{len(backup_files)}): '))
            if 1 <= escolha <= len(backup_files):
                break
            else:
                print('✗ Opção inválida. Tente novamente.')
        except ValueError:
            print('✗ Entrada inválida. Digite um número.')
    
    backup_file = backup_files[escolha - 1]
    dest_file = os.path.join(RESTORE_DIR, 'itens.json')
    
    sucesso, msg = restore_backup(backup_file, dest_file, 'itens')
    return sucesso


def main_interactive():
    """Menu principal interativo."""
    print('\n' + '='*60)
    print('RESTAURAÇÃO DE BACKUPS - PNCP')
    print('='*60)
    print('\nO que você deseja restaurar?')
    print('1: Apenas editais')
    print('2: Apenas itens')
    print('3: Editais e itens')
    print('4: Sair')
    
    while True:
        try:
            opcao = int(input('\nEscolha uma opção (1-4): '))
            if 1 <= opcao <= 4:
                break
            else:
                print('✗ Opção inválida. Tente novamente.')
        except ValueError:
            print('✗ Entrada inválida. Digite um número.')
    
    if opcao == 1:
        restore_editais_interactive()
    elif opcao == 2:
        restore_itens_interactive()
    elif opcao == 3:
        restore_editais_interactive()
        print()
        restore_itens_interactive()
    else:
        print('Saindo...')
        return


def main():
    """Função principal com suporte a argumentos CLI."""
    parser = argparse.ArgumentParser(
        description='Restaura backups de editais e itens do PNCP',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Menu interativo completo
  python backend/scripts/data/restore_backup.py
  
  # Restaurar apenas editais (interativo)
  python backend/scripts/data/restore_backup.py --editais
  
  # Restaurar apenas itens (interativo)
  python backend/scripts/data/restore_backup.py --itens
        """
    )
    
    parser.add_argument(
        '--editais',
        action='store_true',
        help='Restaurar apenas editais'
    )
    parser.add_argument(
        '--itens',
        action='store_true',
        help='Restaurar apenas itens'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Restaurar editais e itens automaticamente (último backup de cada)'
    )
    
    args = parser.parse_args()
    
    # Se --all, restaura automaticamente os últimos backups
    if args.all:
        BACKUP_DIR_EDITAIS = os.path.join(os.path.dirname(__file__), '../../data/backup_editais')
        BACKUP_DIR_ITENS = os.path.join(os.path.dirname(__file__), '../../data/backup_itens')
        RESTORE_DIR = os.path.join(os.path.dirname(__file__), '../../data')
        
        editais_backups = list_backups(BACKUP_DIR_EDITAIS, 'editais')
        itens_backups = list_backups(BACKUP_DIR_ITENS, 'itens')
        
        if editais_backups:
            restore_backup(editais_backups[-1], os.path.join(RESTORE_DIR, 'editais.json'), 'editais')
        
        if itens_backups:
            restore_backup(itens_backups[-1], os.path.join(RESTORE_DIR, 'itens.json'), 'itens')
        
        return
    
    # Se apenas --editais
    if args.editais:
        restore_editais_interactive()
        return
    
    # Se apenas --itens
    if args.itens:
        restore_itens_interactive()
        return
    
    # Caso padrão: menu interativo completo
    main_interactive()


if __name__ == "__main__":
    main()
