"""
Normalizador de texto para exportação.

Remove ou substitui caracteres ilegais/problemáticos que causam erros
ao gerar arquivos XLSX (openpyxl) e CSV. Deve ser chamado ANTES da
exportação para garantir dados limpos.

Caracteres tratados:
- Control chars ilegais para openpyxl (0x00-0x08, 0x0B, 0x0C, 0x0E-0x1F)
- DEL e faixa Latin-1 Supplement control (0x7F-0x9F)
- Surrogates Unicode (0xD800-0xDFFF)
- Unicode noncharacters (0xFFFE, 0xFFFF)
- Quebras de linha (\r\n, \r, \n) → substituídas por espaço
- Espaços múltiplos consecutivos → um único espaço
- Espaços em branco no início/fim → removidos (trim)
"""

import re
import logging

logger = logging.getLogger(__name__)

# Regex que captura todos os caracteres ilegais para openpyxl/Excel
_ILLEGAL_CHARS_RE = re.compile(
    r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f'
    r'\ud800-\udfff\ufffe\uffff]'
)

# Regex para múltiplos espaços consecutivos
_MULTI_SPACES_RE = re.compile(r' {2,}')


def normalize_str(value):
    """
    Normaliza uma string individual:
    1. Remove caracteres ilegais para Excel/openpyxl
    2. Substitui quebras de linha por espaço
    3. Colapsa espaços múltiplos em um só
    4. Remove espaços no início/fim
    """
    if not isinstance(value, str):
        return value
    # 1. Remove caracteres ilegais
    s = _ILLEGAL_CHARS_RE.sub('', value)
    # 2. Quebras de linha → espaço
    s = s.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')
    # 3. Colapsa espaços múltiplos
    s = _MULTI_SPACES_RE.sub(' ', s)
    # 4. Trim
    s = s.strip()
    return s


def normalize_dict(record):
    """
    Normaliza todos os valores string de um dicionário (um registro/edital/item).
    Percorre recursivamente dicionários aninhados.
    """
    if not isinstance(record, dict):
        return record
    normalized = {}
    for key, value in record.items():
        if isinstance(value, str):
            normalized[key] = normalize_str(value)
        elif isinstance(value, dict):
            normalized[key] = normalize_dict(value)
        elif isinstance(value, list):
            normalized[key] = [
                normalize_dict(item) if isinstance(item, dict)
                else normalize_str(item) if isinstance(item, str)
                else item
                for item in value
            ]
        else:
            normalized[key] = value
    return normalized


def normalize_records(records):
    """
    Normaliza uma lista de registros (editais ou itens).
    Retorna a lista com todos os textos limpos para exportação.

    Args:
        records: Lista de dicionários a normalizar.

    Returns:
        Lista normalizada (nova lista, sem alterar a original).
    """
    if not records:
        return records
    count = len(records)
    normalized = [normalize_dict(r) for r in records]
    logger.info(f"Normalized {count} records (text cleanup for export)")
    return normalized
