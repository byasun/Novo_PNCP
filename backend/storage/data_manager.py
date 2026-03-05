"""
Gerenciamento de dados locais em JSON.

Este módulo implementa a classe DataManager, responsável por salvar e carregar
editais, contratos e itens em arquivos JSON no disco, garantindo persistência local.
"""

import json
import os
import logging
from backend.config import DATA_DIR

logger = logging.getLogger(__name__)

class DataManager:
    """
    Classe responsável por gerenciar a persistência local de dados em arquivos JSON.
    Permite salvar e carregar contratos, editais e itens do sistema PNCP.
    """
    def __init__(self):
        # Diretório base de dados
        self.data_dir = DATA_DIR
        self.contratos_file = os.path.join(self.data_dir, "contratos.json")
        self.editais_file = os.path.join(self.data_dir, "editais.json")
        self.itens_file = os.path.join(self.data_dir, "itens.json")
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """
        Garante que o diretório de dados exista, criando-o se necessário.
        """
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.info(f"Diretório de dados criado: {self.data_dir}")
    
    def save_contratos(self, contratos):
        """
        Salva a lista de contratos em disco no formato JSON.
        """
        try:
            with open(self.contratos_file, "w", encoding="utf-8") as f:
                json.dump(contratos, f, ensure_ascii=False, indent=2)
            logger.info(f"{len(contratos)} contratos salvos em {self.contratos_file}")
        except Exception as e:
            logger.error(f"Erro ao salvar contratos: {e}")
            raise
    
    def load_contratos(self):
        """
        Carrega a lista de contratos do disco.
        Retorna uma lista vazia se o arquivo não existir.
        """
        if not os.path.exists(self.contratos_file):
            logger.info("Arquivo de contratos não encontrado, retornando lista vazia")
            return []
        
        try:
            with open(self.contratos_file, "r", encoding="utf-8") as f:
                contratos = json.load(f)
            logger.info(f"Loaded {len(contratos)} contratos from storage")
            return contratos
        except Exception as e:
            logger.error(f"Error loading contratos: {e}")
            return []
    
    def save_editais(self, editais):
        # Salva editais em disco com merge incremental
        # Se arquivo já existe, faz merge ao invés de sobrescrever
        existing_editais = []
        if os.path.exists(self.editais_file):
            try:
                with open(self.editais_file, "r", encoding="utf-8") as f:
                    existing_editais = json.load(f)
            except Exception:
                pass
        
        # Mescla editais por ID_C_PNCP
        # Mantém todos os antigos e só adiciona/atualiza os novos
        edital_map = {e.get("ID_C_PNCP"): e for e in existing_editais if e.get("ID_C_PNCP")}
        for edital in editais:
            if edital.get("ID_C_PNCP"):
                edital_map[edital["ID_C_PNCP"]] = edital
        
        all_editais = list(edital_map.values())
        # Nunca sobrescreve com lista vazia - mantém dados existentes se nenhum novo foi adicionado
        if all_editais:
            try:
                with open(self.editais_file, "w", encoding="utf-8") as f:
                    json.dump(all_editais, f, ensure_ascii=False, indent=2)
                logger.info(f"Saved {len(all_editais)} editais to {self.editais_file} (merge incremental: {len(existing_editais)} existing + {len(editais)} new/updated)")
            except Exception as e:
                logger.error(f"Error saving editais: {e}")
                raise
        else:
            logger.info(f"No editais to save. Keeping {len(existing_editais)} existing editais (merge incremental: {len(existing_editais)} existing + {len(editais)} new/updated)")
    
    def load_editais(self):
        # Carrega editais do disco
        if not os.path.exists(self.editais_file):
            logger.info("No editais file found, returning empty list")
            return []
        
        try:
            with open(self.editais_file, "r", encoding="utf-8") as f:
                editais = json.load(f)
            logger.info(f"Loaded {len(editais)} editais from storage")
            return editais
        except Exception as e:
            logger.error(f"Error loading editais: {e}")
            return []
    
    def save_itens(self, itens, append=False):
        # Salva itens em disco
        # Se append=True, acrescenta aos existentes. Se False, sobrescreve com a lista fornecida.
        if append:
            existing_itens = []
            if os.path.exists(self.itens_file):
                try:
                    with open(self.itens_file, "r", encoding="utf-8") as f:
                        existing_itens = json.load(f)
                except Exception:
                    pass
            all_itens = existing_itens + itens
        else:
            all_itens = itens
        
        if all_itens:
            try:
                with open(self.itens_file, "w", encoding="utf-8") as f:
                    json.dump(all_itens, f, ensure_ascii=False)
                logger.info(f"Saved {len(all_itens)} itens to {self.itens_file}")
            except Exception as e:
                logger.error(f"Error saving itens: {e}")
                raise
        else:
            logger.info(f"No itens to save.")
    
    def load_itens(self):
        # Carrega itens do disco
        if not os.path.exists(self.itens_file):
            logger.info("No itens file found, returning empty list")
            return []
        
        try:
            with open(self.itens_file, "r", encoding="utf-8") as f:
                itens = json.load(f)
            logger.info(f"Loaded {len(itens)} itens from storage")
            return itens
        except Exception as e:
            logger.error(f"Error loading itens: {e}")
            return []
    
    def get_last_update(self):
        # Retorna timestamp da última atualização de editais
        if os.path.exists(self.editais_file):
            return os.path.getmtime(self.editais_file)
        return None
