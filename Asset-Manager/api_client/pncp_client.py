import requests
import time
import logging
from config import API_BASE_URL, PAGE_SIZE, MAX_RETRIES, RETRY_DELAY

logger = logging.getLogger(__name__)

class PNCPClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "PNCP-Collector/1.0"
        })
    
    def _make_request(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1}/{MAX_RETRIES} failed for {url}: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"All retries failed for {url}")
                    raise
        return None
    
    def get_contratos(self, page=1, size=PAGE_SIZE, data_inicial=None, data_final=None):
        params = {"pagina": page, "tamanhoPagina": size}
        if data_inicial:
            params["dataInicial"] = data_inicial
        if data_final:
            params["dataFinal"] = data_final
        
        try:
            return self._make_request("/contratos", params)
        except Exception as e:
            logger.error(f"Error fetching contratos page {page}: {e}")
            return None
    
    def get_contrato_by_id(self, cnpj, ano, sequencial):
        endpoint = f"/orgaos/{cnpj}/contratos/{ano}/{sequencial}"
        try:
            return self._make_request(endpoint)
        except Exception as e:
            logger.error(f"Error fetching contrato {cnpj}/{ano}/{sequencial}: {e}")
            return None
    
    def get_itens_contrato(self, cnpj, ano, sequencial):
        endpoint = f"/orgaos/{cnpj}/contratos/{ano}/{sequencial}/itens"
        try:
            result = self._make_request(endpoint)
            return result if result else []
        except Exception as e:
            logger.error(f"Error fetching itens for contrato {cnpj}/{ano}/{sequencial}: {e}")
            return []
    
    def get_editais(self, page=1, size=PAGE_SIZE, data_inicial=None, data_final=None, codigo_modalidade=None):
        params = {"pagina": page, "tamanhoPagina": size}
        if data_inicial:
            params["dataInicial"] = data_inicial
        if data_final:
            params["dataFinal"] = data_final
        if codigo_modalidade:
            params["codigoModalidadeContratacao"] = codigo_modalidade
        
        try:
            # Editais/Contratações are obtained from /contratacoes/publicacao endpoint
            return self._make_request("/contratacoes/publicacao", params)
        except Exception as e:
            logger.error(f"Error fetching editais page {page}: {e}")
            return None
    
    def get_all_contratos(self, data_inicial=None, data_final=None):
        all_contratos = []
        page = 1
        errors_count = 0
        max_errors = 3
        
        while True:
            logger.info(f"Fetching contratos page {page}...")
            result = self.get_contratos(page=page, data_inicial=data_inicial, data_final=data_final)
            
            if result is None:
                errors_count += 1
                logger.warning(f"Failed to fetch page {page}. Error count: {errors_count}/{max_errors}")
                if errors_count >= max_errors:
                    logger.error(f"Too many consecutive errors, stopping at page {page}")
                    break
                page += 1
                time.sleep(1)
                continue
            
            errors_count = 0
            
            if isinstance(result, list):
                data = result
                total_pages = 1
            elif isinstance(result, dict):
                data = result.get("data", result.get("contratos", []))
                if not isinstance(data, list):
                    logger.warning(f"Unexpected data format on page {page}: {type(data)}")
                    data = []
                total_pages = result.get("totalPaginas", result.get("totalPages", 1))
            else:
                logger.warning(f"Unexpected result type on page {page}: {type(result)}")
                break
            
            if not data:
                logger.info(f"No more data on page {page}, stopping pagination")
                break
            
            all_contratos.extend(data)
            logger.info(f"Fetched {len(data)} contratos from page {page}. Total: {len(all_contratos)}")
            
            if page >= total_pages or len(data) < PAGE_SIZE:
                break
            
            page += 1
            time.sleep(0.5)
        
        logger.info(f"Finished fetching contratos. Total collected: {len(all_contratos)}")
        return all_contratos
    
    def get_all_editais(self, data_inicial=None, data_final=None, codigo_modalidade=None):
        all_editais = []
        page = 1
        errors_count = 0
        max_errors = 3
        
        while True:
            logger.info(f"Fetching editais page {page}...")
            result = self.get_editais(page=page, data_inicial=data_inicial, data_final=data_final, codigo_modalidade=codigo_modalidade)
            
            if result is None:
                errors_count += 1
                logger.warning(f"Failed to fetch page {page}. Error count: {errors_count}/{max_errors}")
                if errors_count >= max_errors:
                    logger.error(f"Too many consecutive errors, stopping at page {page}")
                    break
                page += 1
                time.sleep(1)
                continue
            
            errors_count = 0
            
            if isinstance(result, list):
                data = result
            elif isinstance(result, dict):
                data = result.get("data", result.get("contratacoes", []))
                if not isinstance(data, list):
                    logger.warning(f"Unexpected data format on page {page}: {type(data)}")
                    data = []
            else:
                logger.warning(f"Unexpected result type on page {page}: {type(result)}")
                break
            
            if not data:
                logger.info(f"No more data on page {page}, stopping pagination")
                break
            
            all_editais.extend(data)
            logger.info(f"Fetched {len(data)} editais from page {page}. Total: {len(all_editais)}")
            
            # Continue to next page if we got data
            page += 1
            time.sleep(0.5)
        
        logger.info(f"Finished fetching editais. Total collected: {len(all_editais)}")
        return all_editais
