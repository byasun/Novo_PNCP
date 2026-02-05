"""Gerenciamento de dados locais em JSON."""

import json
import os
import logging
from backend.config import DATA_DIR

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self):
        # Diretório base de dados
        self.data_dir = DATA_DIR
        self.contratos_file = os.path.join(self.data_dir, "contratos.json")
        self.editais_file = os.path.join(self.data_dir, "editais.json")
        self.itens_file = os.path.join(self.data_dir, "itens.json")
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        # Cria diretório se não existir
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.info(f"Created data directory: {self.data_dir}")
    
    def save_contratos(self, contratos):
        # Salva contratos em disco
        try:
            with open(self.contratos_file, "w", encoding="utf-8") as f:
                json.dump(contratos, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(contratos)} contratos to {self.contratos_file}")
        except Exception as e:
            logger.error(f"Error saving contratos: {e}")
            raise
    
    def load_contratos(self):
        # Carrega contratos do disco
        if not os.path.exists(self.contratos_file):
            logger.info("No contratos file found, returning empty list")
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
        # Salva editais em disco
        try:
            with open(self.editais_file, "w", encoding="utf-8") as f:
                json.dump(editais, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(editais)} editais to {self.editais_file}")
        except Exception as e:
            logger.error(f"Error saving editais: {e}")
            raise
    
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
    
    def save_itens(self, itens):
        # Salva itens em disco
        try:
            with open(self.itens_file, "w", encoding="utf-8") as f:
                json.dump(itens, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(itens)} itens to {self.itens_file}")
        except Exception as e:
            logger.error(f"Error saving itens: {e}")
            raise
    
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
