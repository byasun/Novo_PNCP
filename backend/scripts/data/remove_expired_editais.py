"""
Script para remover editais e itens cujos editais já encerraram o recebimento de propostas.

Este script identifica editais cujo prazo de recebimento de propostas já expirou e remove tanto os editais quanto os itens correspondentes dos arquivos JSON.
Também realiza backup dos arquivos antes de sobrescrever.
"""
import os
import json
import sys
from datetime import datetime

# Garante que o diretório raiz do projeto esteja no sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.config import DATA_DIR
EDITAIS_PATH = os.path.join(DATA_DIR, "editais.json")
ITENS_PATH = os.path.join(DATA_DIR, "itens.json")
BACKUP_SUFFIX = datetime.now().strftime("_%Y%m%d_%H%M%S")


def load_json(path):
    """
    Carrega um arquivo JSON e retorna seu conteúdo como lista de dicionários.
    Retorna lista vazia se o arquivo não existir.
    """
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    """
    Salva uma lista de dicionários em um arquivo JSON formatado.
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def backup_file(path, backup_dir):
    """
    Realiza backup do arquivo em um diretório específico, adicionando sufixo com data/hora.
    """
    if os.path.exists(path):
        os.makedirs(backup_dir, exist_ok=True)
        base = os.path.basename(path)
        backup_path = os.path.join(backup_dir, f"{base}{BACKUP_SUFFIX}")
        os.rename(path, backup_path)

def main():
    """
    Função principal que remove editais e itens expirados.
    Editais sem data de encerramento são mantidos por segurança.
    Realiza backup dos arquivos antes de sobrescrever.
    """
    now = datetime.now()
    editais = load_json(EDITAIS_PATH)
    itens = load_json(ITENS_PATH)

    # Filtra editais que ainda não encerraram

    editais_ativos = []
    chaves_ativos = set()
    for edital in editais:
        data_enc = edital.get("dataEncerramentoProposta")
        # Identificador único preferencial
        chave = (
            edital.get("numeroControlePNCP")
            or edital.get("ID_C_PNCP")
            or f"{edital.get('orgaoEntidade', {}).get('cnpj') or edital.get('cnpjOrgao')}_{edital.get('anoCompra') or edital.get('ano')}_{edital.get('numeroCompra') or edital.get('numero')}"
        )
        if not data_enc:
            # Se não tem data, mantém por segurança
            editais_ativos.append(edital)
            chaves_ativos.add(chave)
            continue
        try:
            dt = datetime.fromisoformat(data_enc)
        except Exception:
            # Tenta formato sem T
            try:
                dt = datetime.strptime(data_enc, "%Y-%m-%d %H:%M:%S")
            except Exception:
                # Se não conseguir converter, mantém edital por segurança
                editais_ativos.append(edital)
                chaves_ativos.add(chave)
                continue
        if dt >= now:
            # Edital ainda está ativo
            editais_ativos.append(edital)
            chaves_ativos.add(chave)

    # Filtra itens dos editais ativos
    def item_chave(item):
        return (
            item.get("edital_numeroControlePNCP")
            or item.get("edital_ID_C_PNCP")
            or f"{item.get('edital_cnpj')}_{item.get('edital_ano')}_{item.get('edital_numero')}"
        )
    itens_ativos = [item for item in itens if item_chave(item) in chaves_ativos]

    # Backup antes de sobrescrever
    backup_file(EDITAIS_PATH, os.path.join(DATA_DIR, 'backup_editais'))
    backup_file(ITENS_PATH, os.path.join(DATA_DIR, 'backup_itens'))
    save_json(EDITAIS_PATH, editais_ativos)
    save_json(ITENS_PATH, itens_ativos)
    print(f"Editais e itens expirados removidos. {len(editais_ativos)} editais e {len(itens_ativos)} itens restantes.")

if __name__ == "__main__":
    # Permite execução direta do script
    main()
