import requests
import time
import logging
import json
import os
from config import API_BASE_URL, API_ITEMS_BASE_URL, PAGE_SIZE, MAX_RETRIES, RETRY_DELAY, EDITAIS_CHECKPOINT_FILE

logger = logging.getLogger(__name__)

class PNCPClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.items_base_url = API_ITEMS_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "PNCP-Collector/1.0"
        })
    
    def _get_last_checkpoint_page(self):
        """Load the last successfully checkpointed page for editais"""
        if os.path.exists(EDITAIS_CHECKPOINT_FILE):
            try:
                with open(EDITAIS_CHECKPOINT_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get('last_checkpoint_page', 1)
            except Exception as e:
                logger.warning(f"Error reading checkpoint file: {e}")
        return 1
    
    def _save_checkpoint_page(self, page):
        """Save the current checkpoint page"""
        try:
            os.makedirs(os.path.dirname(EDITAIS_CHECKPOINT_FILE) or '.', exist_ok=True)
            with open(EDITAIS_CHECKPOINT_FILE, 'w') as f:
                json.dump({'last_checkpoint_page': page}, f)
        except Exception as e:
            logger.error(f"Error saving checkpoint file: {e}")
    
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
    
    def get_itens_edital(self, cnpj, ano, numero):
        """Fetch items for a given edital/contratação"""
        endpoint = f"/orgaos/{cnpj}/compras/{ano}/{numero}"
        try:
            result = self._make_request(endpoint)
            if result and isinstance(result, dict):
                # Try to get itens from the response
                itens = result.get("itens", result.get("items", []))
                return itens if isinstance(itens, list) else []
            return []
        except Exception as e:
            logger.error(f"Error fetching itens for edital {cnpj}/{ano}/{numero}: {e}")
            return []

    def get_itens_edital_count(self, cnpj, ano, mes):
        """Return integer count from /api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{mes}/itens/quantidade"""
        endpoint = f"/orgaos/{cnpj}/compras/{ano}/{mes}/itens/quantidade"
        url = f"{self.items_base_url}{endpoint}"
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(url, timeout=30)
                # If endpoint doesn't exist for this orgao/period, return 0 without retrying
                if response.status_code == 404:
                    logger.debug(f"Items count endpoint not found for {cnpj}/{ano}/{mes} (404)")
                    return 0
                response.raise_for_status()
                # Response body is a plain number
                return int(response.json()) if response.text else 0
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt+1}/{MAX_RETRIES} failed for {url}: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"All retries failed for {url}")
                    return 0

    def get_itens_edital_paginated(self, cnpj, ano, mes, page=1, size=PAGE_SIZE):
        """Fetch items for a given edital/period with pagination: /api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{mes}/itens"""
        endpoint = f"/orgaos/{cnpj}/compras/{ano}/{mes}/itens"
        url = f"{self.items_base_url}{endpoint}"
        params = {"pagina": page, "tamanhoPagina": size}
        
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(url, params=params, timeout=30)
                # If the items endpoint doesn't exist for this orgao/period, treat as no items
                if response.status_code == 404:
                    logger.debug(f"Items endpoint not found for {cnpj}/{ano}/{mes} (404)")
                    return []
                
                response.raise_for_status()
                result = response.json()
                
                if result is None:
                    return []
                if isinstance(result, list):
                    return result
                if isinstance(result, dict):
                    data = result.get("data", result.get("itens", result.get("items", [])))
                    return data if isinstance(data, list) else []
                return []
            
            except requests.exceptions.RequestException as e:
                # For non-404 errors, log and retry
                logger.warning(f"Attempt {attempt+1}/{MAX_RETRIES} failed for {url}: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                logger.error(f"All retries failed for {url}")
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

            # Track previous total to detect when the last page returned fewer
            # records than a full page. If the difference between the new total
            # and the previous total is less than PAGE_SIZE, stop to avoid
            # making extra requests that often return errors or empty responses.
            prev_total = len(all_contratos)
            all_contratos.extend(data)
            fetched_now = len(all_contratos) - prev_total
            logger.info(f"Fetched {len(data)} contratos from page {page}. Total: {len(all_contratos)}")

            if fetched_now < PAGE_SIZE:
                logger.info(f"Fetched fewer than PAGE_SIZE ({fetched_now} < {PAGE_SIZE}) on page {page}, stopping pagination")
                break

            if page >= total_pages:
                break

            page += 1
            time.sleep(0.5)
        
        logger.info(f"Finished fetching contratos. Total collected: {len(all_contratos)}")
        return all_contratos
    
    def get_all_editais(self, data_inicial=None, data_final=None, codigo_modalidade=None, on_checkpoint=None):
        """
        Fetch all editais with incremental saving via checkpoint callback.
        
        Args:
            data_inicial: Start date (YYYYMMDD format)
            data_final: End date (YYYYMMDD format)
            codigo_modalidade: Modality code (e.g., 6 for Pregão Eletrônico)
            on_checkpoint: Optional callback function(editais_list, current_page) called every N pages to save progress
        """
        from config import PAGE_SIZE
        
        # Get starting page from checkpoint (go back 1 page for safety)
        last_checkpoint_page = self._get_last_checkpoint_page()
        start_page = max(1, last_checkpoint_page - 1) if last_checkpoint_page > 1 else 1
        
        if start_page < last_checkpoint_page:
            logger.info(f"Resuming from page {start_page} (checkpoint was at page {last_checkpoint_page}, going back 1 page for safety)")
        
        all_editais = []
        page = start_page
        errors_count = 0
        max_errors = 3
        checkpoint_interval = 10  # Save checkpoint every 10 pages
        pages_since_checkpoint = 0
        
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

            prev_total = len(all_editais)
            all_editais.extend(data)
            fetched_now = len(all_editais) - prev_total
            logger.info(f"Fetched {len(data)} editais from page {page}. Total: {len(all_editais)}")
            
            pages_since_checkpoint += 1
            
            # Save checkpoint every N pages
            if pages_since_checkpoint >= checkpoint_interval:
                logger.info(f"Checkpoint: {len(all_editais)} editais fetched on page {page}, saving...")
                self._save_checkpoint_page(page)
                if on_checkpoint:
                    try:
                        on_checkpoint(all_editais, page)
                    except Exception as e:
                        logger.error(f"Error in checkpoint callback: {e}")
                pages_since_checkpoint = 0

            if fetched_now < PAGE_SIZE:
                logger.info(f"Fetched fewer than PAGE_SIZE ({fetched_now} < {PAGE_SIZE}) on page {page}, stopping pagination")
                break

            page += 1
            time.sleep(0.5)
        
        logger.info(f"Finished fetching editais. Total collected: {len(all_editais)}")
        return all_editais
