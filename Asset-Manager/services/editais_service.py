import logging
from api_client.pncp_client import PNCPClient
from storage.data_manager import DataManager

logger = logging.getLogger(__name__)

class EditaisService:
    def __init__(self):
        self.client = PNCPClient()
        self.data_manager = DataManager()
    
    def fetch_all_editais(self, data_inicial=None, data_final=None, modalidade="Pregão - Eletrônico"):
        logger.info(f"Starting editais fetch with modalidade: {modalidade}...")
        editais = self.client.get_all_editais(data_inicial, data_final, modalidade)
        logger.info(f"Fetched {len(editais)} editais from API")
        return editais
    
    def get_all_editais_local(self):
        return self.data_manager.load_editais()
    
    def get_edital_by_key(self, edital_key):
        editais = self.data_manager.load_editais()
        for edital in editais:
            key = self._generate_edital_key(edital)
            if key == edital_key:
                return edital
        return None
    
    def _generate_edital_key(self, edital):
        cnpj = edital.get("orgaoEntidade", {}).get("cnpj", "") or edital.get("cnpjOrgao", "")
        ano = edital.get("ano", "")
        seq = edital.get("numero", "")
        return f"{cnpj}_{ano}_{seq}"
    
    def save_editais(self, editais):
        self.data_manager.save_editais(editais)
        logger.info(f"Saved {len(editais)} editais to local storage")
    
    def update_editais(self, data_inicial=None, data_final=None, modalidade="Pregão - Eletrônico"):
        editais = self.fetch_all_editais(data_inicial, data_final, modalidade)
        if editais:
            self.save_editais(editais)
        return editais
