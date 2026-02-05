"""Serviço de itens de contratos (camada de negócio)."""

import logging
from backend.api_client.pncp_client import PNCPClient
from backend.storage.data_manager import DataManager

logger = logging.getLogger(__name__)

class ItensService:
    def __init__(self):
        # Cliente da API e gerenciador de dados locais
        self.client = PNCPClient()
        self.data_manager = DataManager()
    
    def fetch_itens_for_contrato(self, cnpj, ano, sequencial):
        # Busca itens de um contrato específico
        logger.info(f"Fetching itens for contrato {cnpj}/{ano}/{sequencial}...")
        itens = self.client.get_itens_contrato(cnpj, ano, sequencial)
        return itens if itens else []
    
    def fetch_itens_for_all_contratos(self, contratos):
        # Busca itens de todos os contratos
        all_itens = []
        total = len(contratos)
        
        for idx, contrato in enumerate(contratos):
            cnpj = contrato.get("orgaoEntidade", {}).get("cnpj", "") or contrato.get("cnpjOrgao", "")
            ano = contrato.get("anoContrato", "")
            sequencial = contrato.get("sequencialContrato", "")
            
            if cnpj and ano and sequencial:
                itens = self.fetch_itens_for_contrato(cnpj, ano, sequencial)
                for item in itens:
                    # Anota vínculo do item com o contrato
                    item["contrato_cnpj"] = cnpj
                    item["contrato_ano"] = ano
                    item["contrato_sequencial"] = sequencial
                all_itens.extend(itens)
                
                if (idx + 1) % 10 == 0:
                    logger.info(f"Processed {idx + 1}/{total} contratos for itens")
        
        logger.info(f"Fetched {len(all_itens)} itens total")
        return all_itens
    
    def get_all_itens_local(self):
        # Retorna itens salvos localmente
        return self.data_manager.load_itens()
    
    def get_itens_by_contrato(self, cnpj, ano, sequencial):
        # Filtra itens por contrato
        all_itens = self.data_manager.load_itens()
        return [
            item for item in all_itens
            if (item.get("contrato_cnpj") == cnpj and
                str(item.get("contrato_ano")) == str(ano) and
                str(item.get("contrato_sequencial")) == str(sequencial))
        ]
    
    def save_itens(self, itens):
        # Persiste itens em disco
        self.data_manager.save_itens(itens)
        logger.info(f"Saved {len(itens)} itens to local storage")
