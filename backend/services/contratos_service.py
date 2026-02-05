"""Serviço de contratos (camada de negócio)."""

import logging
from backend.api_client.pncp_client import PNCPClient
from backend.storage.data_manager import DataManager

logger = logging.getLogger(__name__)

class ContratosService:
    def __init__(self):
        # Cliente da API e gerenciador de dados locais
        self.client = PNCPClient()
        self.data_manager = DataManager()
    
    def fetch_all_contratos(self, data_inicial=None, data_final=None):
        # Busca contratos na API
        logger.info("Starting contratos fetch...")
        contratos = self.client.get_all_contratos(data_inicial, data_final)
        logger.info(f"Fetched {len(contratos)} contratos from API")
        return contratos
    
    def get_contrato_details(self, cnpj, ano, sequencial):
        # Detalhes de um contrato específico
        return self.client.get_contrato_by_id(cnpj, ano, sequencial)
    
    def get_all_contratos_local(self):
        # Retorna contratos salvos localmente
        return self.data_manager.load_contratos()
    
    def get_contrato_by_key(self, contrato_key):
        # Busca contrato por chave composta (cnpj_ano_sequencial)
        contratos = self.data_manager.load_contratos()
        for contrato in contratos:
            key = self._generate_contrato_key(contrato)
            if key == contrato_key:
                return contrato
        return None
    
    def _generate_contrato_key(self, contrato):
        # Gera chave única para lookup
        cnpj = contrato.get("orgaoEntidade", {}).get("cnpj", "") or contrato.get("cnpjOrgao", "")
        ano = contrato.get("anoContrato", "")
        seq = contrato.get("sequencialContrato", "")
        return f"{cnpj}_{ano}_{seq}"
    
    def save_contratos(self, contratos):
        # Persiste contratos em disco
        self.data_manager.save_contratos(contratos)
        logger.info(f"Saved {len(contratos)} contratos to local storage")
    
    def update_contratos(self, data_inicial=None, data_final=None):
        # Atualiza contratos: busca na API e salva localmente
        contratos = self.fetch_all_contratos(data_inicial, data_final)
        if contratos:
            self.save_contratos(contratos)
        return contratos
