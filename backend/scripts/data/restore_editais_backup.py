import os
import shutil
import glob


BACKUP_DIR = os.path.join(os.path.dirname(__file__), '../../data/backup_editais')
RESTORE_DIR = os.path.join(os.path.dirname(__file__), '../../data')

# Listar arquivos de backup disponíveis
backup_files = sorted(glob.glob(os.path.join(BACKUP_DIR, 'editais.json_*')))

if not backup_files:
    print('Nenhum arquivo de backup encontrado.')
    exit(1)

print('Backups disponíveis:')
for idx, file in enumerate(backup_files):
    print(f'{idx + 1}: {os.path.basename(file)}')

while True:
    try:
        escolha = int(input(f'Escolha o número do backup para restaurar (1-{len(backup_files)}): '))
        if 1 <= escolha <= len(backup_files):
            break
        else:
            print('Opção inválida. Tente novamente.')
    except ValueError:
        print('Entrada inválida. Digite um número.')

backup_file = backup_files[escolha - 1]
dest_file = os.path.join(RESTORE_DIR, 'editais.json')

print(f'Restaurando backup: {backup_file} -> {dest_file}')
shutil.copy2(backup_file, dest_file)

print('Restauração concluída.')

# Pergunta se deseja restaurar também os itens
resp = input('Deseja restaurar também o backup dos itens? (s/N): ').strip().lower()
if resp == 's':
    BACKUP_DIR_ITENS = os.path.join(os.path.dirname(__file__), '../../data/backup_itens')
    RESTORE_DIR_ITENS = os.path.join(os.path.dirname(__file__), '../../data')
    backup_files_itens = sorted(glob.glob(os.path.join(BACKUP_DIR_ITENS, 'itens.json_*')))
    if not backup_files_itens:
        print('Nenhum arquivo de backup de itens encontrado.')
    else:
        print('Backups de itens disponíveis:')
        for idx, file in enumerate(backup_files_itens):
            print(f'{idx + 1}: {os.path.basename(file)}')
        while True:
            try:
                escolha = int(input(f'Escolha o número do backup de itens para restaurar (1-{len(backup_files_itens)}): '))
                if 1 <= escolha <= len(backup_files_itens):
                    break
                else:
                    print('Opção inválida. Tente novamente.')
            except ValueError:
                print('Entrada inválida. Digite um número.')
        backup_file_itens = backup_files_itens[escolha - 1]
        dest_file_itens = os.path.join(RESTORE_DIR_ITENS, 'itens.json')
        print(f'Restaurando backup: {backup_file_itens} -> {dest_file_itens}')
        shutil.copy2(backup_file_itens, dest_file_itens)
        print('Restauração de itens concluída.')
