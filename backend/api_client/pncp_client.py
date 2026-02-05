import requests
import time
import logging
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from backend.config import (
    API_BASE_URL, API_ITEMS_BASE_URL, PAGE_SIZE, MAX_RETRIES, RETRY_DELAY, 
    EDITAIS_CHECKPOINT_FILE, request_cancel, reset_cancel, is_cancelled
)

logger = logging.getLogger(__name__)


class PNCPClient:
    """Cliente HTTP para a API do PNCP.

    Centraliza requisições, tratamento de erros, retry e checkpoint de paginação.
    """
    def __init__(self):
        # URLs base para endpoints de editais/contratações e itens
        self.base_url = API_BASE_URL
        self.items_base_url = API_ITEMS_BASE_URL
        # Sessão HTTP reutilizável para melhor performance
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "PNCP-Collector/1.0"
        })
    
    def _get_last_checkpoint_page(self):
        """Carrega a última página salva no checkpoint de editais."""
        if os.path.exists(EDITAIS_CHECKPOINT_FILE):
            try:
                with open(EDITAIS_CHECKPOINT_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get('last_checkpoint_page', 1)
            except Exception as e:
                logger.warning(f"Error reading checkpoint file: {e}")
        return 1
    
    def _save_checkpoint_page(self, page):
        """Salva a página atual no checkpoint de editais."""
        try:
            os.makedirs(os.path.dirname(EDITAIS_CHECKPOINT_FILE) or '.', exist_ok=True)
            with open(EDITAIS_CHECKPOINT_FILE, 'w') as f:
                json.dump({'last_checkpoint_page': page}, f)
        except Exception as e:
            logger.error(f"Error saving checkpoint file: {e}")
    
    def _make_request(self, endpoint, params=None):
        # Requisição GET com retry e timeout padrão
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
        # Lista contratos com paginação e filtro por datas
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
        # Obtém um contrato específico por identificadores
        endpoint = f"/orgaos/{cnpj}/contratos/{ano}/{sequencial}"
        try:
            return self._make_request(endpoint)
        except Exception as e:
            logger.error(f"Error fetching contrato {cnpj}/{ano}/{sequencial}: {e}")
            return None
    
    def get_itens_contrato(self, cnpj, ano, sequencial):
        # Obtém itens de um contrato
        endpoint = f"/orgaos/{cnpj}/contratos/{ano}/{sequencial}/itens"
        try:
            result = self._make_request(endpoint)
            return result if result else []
        except Exception as e:
            logger.error(f"Error fetching itens for contrato {cnpj}/{ano}/{sequencial}: {e}")
            return []
    
    def get_itens_edital(self, cnpj, ano, numero):
        """Obtém itens de um edital/contratação (endpoint não paginado)."""
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
        """Retorna a quantidade de itens para um edital em um mês específico."""
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
        """Obtém itens paginados de um edital por período (mês)."""
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
        """Lista editais (contratações A RECEBER/RECEBENDO PROPOSTAS) com filtros.
        
        IMPORTANT: For /contratacoes/proposta endpoint, 'dataFinal' represents the
        MAXIMUM date for proposal reception period, NOT a search date filter.
        Use a far future date (e.g., 20501231) to include all editais currently
        open for receiving proposals.
        """
        params = {"pagina": page, "tamanhoPagina": size}
        if data_inicial:
            params["dataInicial"] = data_inicial
        if data_final:
            params["dataFinal"] = data_final
        if codigo_modalidade:
            params["codigoModalidadeContratacao"] = codigo_modalidade
        
        try:
            # Editais/Contratações com recebimento de propostas aberto
            return self._make_request("/contratacoes/proposta", params)
        except Exception as e:
            logger.error(f"Error fetching editais page {page}: {e}")
            return None
    
    def get_all_contratos(self, data_inicial=None, data_final=None):
        """Obtém todos os contratos com paginação e tolerância a falhas."""
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
    
    def get_all_editais(self, data_inicial=None, data_final=None, codigo_modalidade=None, on_checkpoint=None, max_workers=5):
        """
        Busca todos os editais com paralelização e checkpoint periódico.
        
        Args:
            data_inicial: Data inicial (formato YYYYMMDD)
            data_final: Data final (formato YYYYMMDD)
            codigo_modalidade: Código da modalidade (ex.: 6 para Pregão Eletrônico)
            on_checkpoint: Callback opcional (editais_list, current_page) para salvar progresso
            max_workers: Número de threads paralelas (padrão: 5)
        """
        from backend.config import PAGE_SIZE
        
        # Primeira requisição para descobrir o total de páginas
        logger.info("Fetching first page to determine total pages...")
        first_result = self.get_editais(page=1, data_inicial=data_inicial, data_final=data_final, codigo_modalidade=codigo_modalidade)
        
        if first_result is None:
            logger.error("Failed to fetch first page")
            return []
        
        total_pages = first_result.get("totalPaginas", 1)
        total_records = first_result.get("totalRegistros", 0)
        first_page_data = first_result.get("data", first_result.get("contratacoes", []))
        
        logger.info(f"Total pages: {total_pages}, Total records: {total_records}")
        
        if total_pages <= 1:
            return first_page_data if isinstance(first_page_data, list) else []
        
        # Inicializa com dados da primeira página
        all_editais = list(first_page_data) if isinstance(first_page_data, list) else []
        
        # Get starting page from checkpoint
        last_checkpoint_page = self._get_last_checkpoint_page()
        start_page = max(2, last_checkpoint_page) if last_checkpoint_page > 1 else 2
        
        if start_page > 2:
            logger.info(f"Resuming from page {start_page} (checkpoint was at page {last_checkpoint_page})")
        
        # Define função para buscar uma página
        def fetch_page(page_num):
            if is_cancelled():
                return page_num, []
            result = self.get_editais(page=page_num, data_inicial=data_inicial, data_final=data_final, codigo_modalidade=codigo_modalidade)
            if result is None:
                return page_num, []
            if isinstance(result, list):
                return page_num, result
            elif isinstance(result, dict):
                data = result.get("data", result.get("contratacoes", []))
                return page_num, data if isinstance(data, list) else []
            return page_num, []
        
        # Busca páginas em paralelo em batches
        remaining_pages = list(range(start_page, total_pages + 1))
        batch_size = max_workers * 2  # Processa em batches maiores para manter threads ocupadas
        checkpoint_interval = 50  # Salva checkpoint a cada 50 páginas
        pages_fetched = 0
        cancelled = False
        
        logger.info(f"Fetching {len(remaining_pages)} remaining pages with {max_workers} parallel workers...")
        logger.info("Press Ctrl+C to interrupt...")
        
        try:
            reset_cancel()  # Garante que a flag está limpa no início
            
            while remaining_pages and not is_cancelled():
                batch = remaining_pages[:batch_size]
                remaining_pages = remaining_pages[batch_size:]
                
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = {executor.submit(fetch_page, page): page for page in batch}
                    
                    try:
                        for future in as_completed(futures, timeout=60):
                            if is_cancelled():
                                break
                            page_num = futures[future]
                            try:
                                _, page_data = future.result(timeout=5)
                                if page_data:
                                    all_editais.extend(page_data)
                                pages_fetched += 1
                                
                                if pages_fetched % 10 == 0:
                                    logger.info(f"Progress: {pages_fetched + 1}/{total_pages} pages, {len(all_editais)} editais collected")
                            except Exception as e:
                                logger.error(f"Error fetching page {page_num}: {e}")
                    except KeyboardInterrupt:
                        logger.warning("\nInterrupção solicitada! Cancelando operações...")
                        request_cancel()
                        # Cancela futures pendentes
                        for future in futures:
                            future.cancel()
                        cancelled = True
                        break
                
                if cancelled or is_cancelled():
                    break
                
                # Checkpoint após cada batch
                if pages_fetched % checkpoint_interval == 0 or not remaining_pages:
                    current_page = batch[-1] if batch else start_page
                    self._save_checkpoint_page(current_page)
                    if on_checkpoint:
                        try:
                            on_checkpoint(all_editais, current_page)
                        except Exception as e:
                            logger.error(f"Error in checkpoint callback: {e}")
                
                # Pequena pausa entre batches para não sobrecarregar a API
                if remaining_pages:
                    time.sleep(0.2)
                    
        except KeyboardInterrupt:
            logger.warning("\nInterrupção solicitada (Ctrl+C)! Salvando progresso...")
            request_cancel()
            cancelled = True
        
        if cancelled:
            logger.info(f"Operação interrompida. Salvando {len(all_editais)} editais coletados até agora...")
            # Salva checkpoint final
            if all_editais:
                self._save_checkpoint_page(pages_fetched + start_page)
                if on_checkpoint:
                    try:
                        on_checkpoint(all_editais, pages_fetched + start_page)
                    except Exception as e:
                        logger.error(f"Error in final checkpoint callback: {e}")
        
        logger.info(f"Finished fetching editais. Total collected: {len(all_editais)}")
        return all_editais
