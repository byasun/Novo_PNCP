import os
import shutil
import glob


BACKUP_DIR = os.path.join(os.path.dirname(__file__), '../../data/backup_itens')
RESTORE_DIR = os.path.join(os.path.dirname(__file__), '../../data')

# Listar arquivos de backup disponíveis
backup_files = sorted(glob.glob(os.path.join(BACKUP_DIR, 'itens.json_*')))

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
dest_file = os.path.join(RESTORE_DIR, 'itens.json')

print(f'Restaurando backup: {backup_file} -> {dest_file}')
shutil.copy2(backup_file, dest_file)
print('Restauração concluída.')
