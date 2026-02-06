"""Serviço de editais (camada de negócio e sincronização)."""

import logging
from backend.api_client.pncp_client import PNCPClient
from backend.storage.data_manager import DataManager
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class EditaisService:
    def __init__(self):
        # Cliente da API e gerenciador de dados locais
        self.client = PNCPClient()
        self.data_manager = DataManager()
    
    def fetch_all_editais(self, data_inicial=None, data_final=None, codigo_modalidade=6, filter_by_publication_date=True, days_publication=15):
        """
        Busca editais com checkpoint incremental e filtro opcional de data de publicação.
        
        Args:
            data_inicial: Data inicial para busca na API (não é usado para filtro final)
            data_final: Data final para busca na API (não é usado para filtro final)
            codigo_modalidade: Código da modalidade
            filter_by_publication_date: Se True, filtra por dataPublicacaoPncp dos últimos N dias
            days_publication: Número de dias para filtro de publicação (padrão: 15)
        """
        logger.info(f"Starting editais fetch with codigo_modalidade: {codigo_modalidade}...")
        
        # Callback para salvar checkpoint periódico
        def save_editais_checkpoint(editais, page):
            logger.info(f"Saving editais checkpoint at page {page}: {len(editais)} editais total")
            self.save_editais(editais)
        
        editais = self.client.get_all_editais(
            data_inicial, 
            data_final, 
            codigo_modalidade,
            on_checkpoint=save_editais_checkpoint
        )
        logger.info(f"Fetched {len(editais)} editais from API")
        
        # Aplica filtro de data de publicação se solicitado
        if filter_by_publication_date:
            logger.info(f"Applying publication date filter (last {days_publication} days)...")
            editais = self._filter_editais_by_publication_date(editais, days=days_publication)
            logger.info(f"After publication date filter: {len(editais)} editais remaining")
        
        return editais
    
    def fetch_itens_for_edital(self, cnpj, ano, numero):
        # Busca itens de um edital específico
        logger.info(f"Fetching itens for edital {cnpj}/{ano}/{numero}...")
        itens = self.client.get_itens_edital(cnpj, ano, numero)
        return itens if itens else []

    def _extract_month_from_edital(self, edital):
        # Tenta campos explícitos de mês
        mes = edital.get("mesCompra") or edital.get("mes")
        if mes:
            try:
                return int(mes)
            except:
                pass

        # Tenta parsear datas comuns
        for field in ("dataPublicacao", "dataInclusao", "dataAtualizacao", "dataInicio", "data"):
            val = edital.get(field)
            if val and isinstance(val, str) and len(val) >= 7:
                # Expecting ISO-like date: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS
                try:
                    parts = val.split("T")[0].split("-")
                    if len(parts) >= 2:
                        return int(parts[1])
                except:
                    continue
        return None
    
    def _parse_date_field(self, date_str):
        """
        Parse data em vários formatos para timestamp.
        Suporta: ISO (2026-02-05), ISO com tempo, timestamp Unix, etc.
        """
        if not date_str:
            return None
        
        try:
            # Se for número, trata como timestamp
            if isinstance(date_str, (int, float)):
                return datetime.fromtimestamp(date_str)
            
            # Converte string para datetime
            date_str = str(date_str).strip()
            
            # Remove 'Z' de final se presente
            if date_str.endswith('Z'):
                date_str = date_str[:-1]
            
            # Tenta ISO format com tempo
            if 'T' in date_str:
                return datetime.fromisoformat(date_str)
            
            # Tenta ISO format já data
            if len(date_str) == 10 and date_str.count('-') == 2:
                return datetime.fromisoformat(date_str)
            
            # Tenta outros formatos comuns
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d']:
                try:
                    return datetime.strptime(date_str, fmt)
                except:
                    pass
        
        except Exception as e:
            logger.debug(f"Could not parse date '{date_str}': {e}")
        
        return None
    
    def _filter_editais_by_publication_date(self, editais, days=15):
        """
        Filtra editais mantendo apenas os publicados nos últimos N dias.
        
        Procura pelos campos:
        - dataPublicacaoPncp (prioritário)
        - dataPublicacao
        - dataInclusao
        
        Args:
            editais (list): Lista de editais da API
            days (int): Número de dias para retrospecção
        
        Returns:
            list: Editais filtrados por data de publicação
        """
        if not editais:
            return []
        
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered = []
        rejected = []
        
        for edital in editais:
            # Tenta encontrar a data de publicação em ordem de preferência
            pub_date_str = None
            for field in ['dataPublicacaoPncp', 'dataPublicacao', 'dataInclusao']:
                pub_date_str = edital.get(field)
                if pub_date_str:
                    break
            
            if not pub_date_str:
                logger.debug(f"Could not find publication date for edital {edital.get('numeroCompra')}, keeping it (no date = recent)")
                filtered.append(edital)
                continue
            
            # Converte string de data para datetime
            pub_date = self._parse_date_field(pub_date_str)
            
            if not pub_date:
                logger.debug(f"Could not parse publication date '{pub_date_str}' for edital {edital.get('numeroCompra')}, keeping it")
                filtered.append(edital)
                continue
            
            # Verifica se está dentro da janela de tempo
            if pub_date >= cutoff_date:
                filtered.append(edital)
            else:
                rejected.append({
                    'numero': edital.get('numeroCompra'),
                    'pub_date': pub_date.strftime('%Y-%m-%d'),
                    'type': 'old_publication'
                })
        
        # Log de resumo
        logger.info(f"Filtered editais by publication date (last {days} days):")
        logger.info(f"  - Kept: {len(filtered)} editais")
        logger.info(f"  - Rejected (too old): {len(rejected)} editais")
        
        if rejected and len(rejected) <= 10:
            for item in rejected[:10]:
                logger.debug(f"    Rejected: {item['numero']} (published: {item['pub_date']})")
        
        return filtered

    def fetch_itens_for_all_editais(self, editais, skip_existing=None):
        """
        Busca itens de todos os editais com threads e salvamento incremental.
        
        - Usa endpoints paginados quando possível
        - Anota cada item com chaves do edital
        - Salva checkpoints para permitir retomada
        
        Args:
            editais: Lista de editais para buscar itens
            skip_existing: Se True, pula editais que já têm itens salvos.
                          Se None, usa valor de ITEMS_SKIP_EXISTING do .env (padrão: True)
        """
        from backend.config import ITEMS_FETCH_THREADS, ITEMS_FETCH_DELAY_PER_THREAD, ITEMS_FETCH_CHECKPOINT, ITEMS_SKIP_EXISTING
        
        # Usa configuração do .env se não especificado
        if skip_existing is None:
            skip_existing = ITEMS_SKIP_EXISTING
        
        if not editais:
            logger.info("No editais provided for item fetching")
            return []

        # Carrega itens existentes para evitar duplicidades
        existing_itens = self.data_manager.load_itens()
        existing_keys = set()
        existing_edital_keys = set()  # Chaves de editais que já têm itens
        
        for item in existing_itens:
            # Cria chave única para deduplicação de itens
            key = f"{item.get('edital_cnpj')}_{item.get('edital_ano')}_{item.get('edital_numero')}_{item.get('numeroItem')}"
            existing_keys.add(key)
            # Cria chave do edital para verificar quais já foram processados
            edital_key = f"{item.get('edital_cnpj')}_{item.get('edital_ano')}_{item.get('edital_numero')}"
            existing_edital_keys.add(edital_key)
        
        logger.info(f"Loaded {len(existing_itens)} existing items from storage")
        logger.info(f"Found {len(existing_edital_keys)} editais with items already saved")
        
        # Filtra editais que já têm itens salvos (se skip_existing=True)
        if skip_existing and existing_edital_keys:
            editais_to_process = []
            skipped_count = 0
            for edital in editais:
                cnpj = (edital.get("orgaoEntidade", {}) or {}).get("cnpj") or edital.get("cnpjOrgao")
                ano = edital.get("anoCompra") or edital.get("ano")
                numero = edital.get("numeroCompra") or edital.get("numero")
                edital_key = f"{cnpj}_{ano}_{numero}"
                
                if edital_key in existing_edital_keys:
                    skipped_count += 1
                else:
                    editais_to_process.append(edital)
            
            logger.info(f"Skipping {skipped_count} editais that already have items saved")
            logger.info(f"Will process {len(editais_to_process)} editais without items")
            editais = editais_to_process
            
            if not editais:
                logger.info("All editais already have items saved. Nothing to fetch.")
                return existing_itens
        
        logger.info(f"Fetching items for {len(editais)} editais using {ITEMS_FETCH_THREADS} parallel threads...")
        
        all_itens = existing_itens.copy()  # Start with existing items
        processed_count = 0
        
        # Usa ThreadPoolExecutor para paralelizar a coleta
        executor = None
        try:
            executor = ThreadPoolExecutor(max_workers=ITEMS_FETCH_THREADS)
            # Submit all tasks
            futures = {}
            for idx, edital in enumerate(editais, start=1):
                future = executor.submit(self._fetch_items_for_single_edital, idx, len(editais), edital, ITEMS_FETCH_DELAY_PER_THREAD)
                futures[future] = idx
            
            # Collect results as they complete and save incrementally
            for future in as_completed(futures):
                try:
                    itens = future.result()
                    
                    # Remove duplicados (itens já conhecidos)
                    for item in itens:
                        key = f"{item.get('edital_cnpj')}_{item.get('edital_ano')}_{item.get('edital_numero')}_{item.get('numeroItem')}"
                        if key not in existing_keys:
                            all_itens.append(item)
                            existing_keys.add(key)
                    
                    processed_count += 1
                    
                    # Salva checkpoint a cada N editais
                    if processed_count % ITEMS_FETCH_CHECKPOINT == 0:
                        logger.info(f"Checkpoint: {processed_count}/{len(editais)} editais processed, {len(all_itens)} total items, saving...")
                        try:
                            self.data_manager.save_itens(all_itens)
                            logger.info(f"Checkpoint saved successfully")
                        except Exception:
                            logger.exception("Failed to save checkpoint")
                            
                except Exception as e:
                    idx = futures[future]
                    logger.error(f"Error in parallel fetch for edital {idx}: {e}")
                    processed_count += 1

        except KeyboardInterrupt:
            # Interrupção manual: salvar progresso parcial
            logger.warning(f"Fetch interrupted by user at {processed_count}/{len(editais)} editais processed")
            # Wait for all threads to complete before saving
            if executor:
                logger.info("Waiting for all threads to complete...")
                executor.shutdown(wait=True)
            # Save all collected items before exiting
            if all_itens:
                try:
                    self.data_manager.save_itens(all_itens)
                    logger.info(f"Interrupted: saved {len(all_itens)} items collected so far")
                except Exception:
                    logger.exception("Failed to save items on interruption")
            raise
        finally:
            # Ensure executor is shut down
            if executor:
                try:
                    executor.shutdown(wait=True)
                except Exception:
                    pass

        # Salvamento final
        if all_itens:
            try:
                self.data_manager.save_itens(all_itens)
                logger.info(f"Final save: {len(all_itens)} total items saved to storage")
            except Exception:
                logger.exception("Failed to final save itens to local storage")

        logger.info(f"Finished fetching items for all editais. Total itens collected: {len(all_itens)}")
        return all_itens
    
    def _fetch_items_for_single_edital(self, idx, total, edital, delay_per_request):
        """
        Busca itens de um edital específico (executa em thread).
        """
        try:
            cnpj = (edital.get("orgaoEntidade", {}) or {}).get("cnpj") or edital.get("cnpjOrgao")
            ano = edital.get("anoCompra") or edital.get("ano")
            numero = edital.get("numeroCompra") or edital.get("numero")

            if not cnpj or not ano or not numero:
                logger.debug(f"Skipping edital {idx}/{total} with missing identifiers: cnpj={cnpj}, ano={ano}, numero={numero}")
                return []

            mes = self._extract_month_from_edital(edital)
            itens = []
            
            if not mes:
                logger.debug(f"Could not determine month for edital {idx}/{total}: {cnpj}/{ano}/{numero}")
                itens = self.client.get_itens_edital(cnpj, ano, numero)
                itens = itens or []
            else:
                # Primeiro, checa quantidade para evitar chamadas desnecessárias
                item_count = self.client.get_itens_edital_count(cnpj, ano, mes)
                time.sleep(delay_per_request)
                
                if item_count == 0:
                    logger.debug(f"No items for edital {idx}/{total}: {cnpj}/{ano}/{mes} (count=0)")
                    itens = []
                else:
                    logger.info(f"Found {item_count} items for edital {idx}/{total}: {cnpj}/{ano}/{mes}")
                    # Use paginated items endpoint
                    page = 1
                    while True:
                        page_items = self.client.get_itens_edital_paginated(cnpj, ano, mes, page=page)
                        time.sleep(delay_per_request)
                        
                        if not page_items:
                            break
                        itens.extend(page_items)
                        logger.debug(f"  Edital {idx}/{total}: Page {page}: {len(page_items)} items, total: {len(itens)}")
                        page += 1

            # Anota itens com chaves do edital
            for item in itens:
                item["edital_cnpj"] = cnpj
                item["edital_ano"] = ano
                item["edital_numero"] = numero

            if itens:
                logger.info(f"Completed edital {idx}/{total}: fetched {len(itens)} itens")
            
            return itens

        except Exception as e:
            logger.error(f"Error fetching itens for edital {idx}/{total}: {e}")
            return []
    
    def get_all_editais_local(self):
        # Retorna editais salvos localmente
        return self.data_manager.load_editais()
    
    def get_edital_by_key(self, edital_key):
        # Busca edital por chave composta
        editais = self.data_manager.load_editais()
        for edital in editais:
            key = self._generate_edital_key(edital)
            if key == edital_key:
                return edital
        return None
    
    def get_itens_by_edital(self, cnpj, ano, numero):
        # Filtra itens vinculados a um edital
        all_itens = self.data_manager.load_itens()
        return [
            item for item in all_itens
            if (item.get("edital_cnpj") == cnpj and
                str(item.get("edital_ano")) == str(ano) and
                str(item.get("edital_numero")) == str(numero))
        ]
    
    def _generate_edital_key(self, edital):
        # Gera chave única para lookup
        cnpj = edital.get("orgaoEntidade", {}).get("cnpj", "") or edital.get("cnpjOrgao", "")
        ano = edital.get("anoCompra", "")
        numero = edital.get("numeroCompra", "")
        return f"{cnpj}_{ano}_{numero}"
    
    def save_editais(self, editais):
        # Persiste editais em disco
        self.data_manager.save_editais(editais)
        logger.info(f"Saved {len(editais)} editais to local storage")
    
    def save_itens(self, itens):
        # Persiste itens em disco
        self.data_manager.save_itens(itens)
        logger.info(f"Saved {len(itens)} itens to local storage")
    
    def update_editais(self, data_inicial=None, data_final=None, codigo_modalidade=6):
        # Atualiza editais preservando histórico local
        logger.info("Updating editais (preserving existing + adding/updating new)")

        local_editais = self.data_manager.load_editais()

        # Se já há dados, usa sync incremental
        if local_editais:
            self.sync_editais(data_inicial, data_final, codigo_modalidade)
            return self.data_manager.load_editais()

        # Primeira carga (sem dados locais): fetch completo
        logger.info("No local editais found. Performing full fetch...")
        editais = self.fetch_all_editais(data_inicial, data_final, codigo_modalidade)
        if editais:
            self.save_editais(editais)
            logger.info(f"Successfully saved {len(editais)} editais")
            try:
                self.fetch_itens_for_all_editais(editais)
            except Exception:
                logger.exception("Error while fetching itens for editais")
        else:
            logger.warning("No editais were fetched from API")
        return editais

    def sync_editais(self, data_inicial=None, data_final=None, codigo_modalidade=6, filter_by_publication_date=False, days_publication=15):
        """
        Sincronização incremental: compara editais remotos e locais.

        - Atualiza registros mais novos
        - Adiciona novos editais
        - Busca itens apenas para editais novos
        
        Args:
            filter_by_publication_date: Se True, filtra por dataPublicacaoPncp após buscar da API
            days_publication: Número de dias para filtro de publicação
        
        Retorna: {added: int, updated: int}
        """
        logger.info(f"Starting incremental sync for editais ({data_inicial} to {data_final})")
        # Busca editais remotos (com checkpoint)
        remote_editais = self.fetch_all_editais(
            data_inicial, 
            data_final, 
            codigo_modalidade,
            filter_by_publication_date=filter_by_publication_date,
            days_publication=days_publication
        )
        if not remote_editais:
            logger.info("No remote editais fetched for incremental sync")
            return {"added": 0, "updated": 0}

        # Carrega editais locais
        local_editais = self.data_manager.load_editais()
        local_map = {}
        for idx, e in enumerate(local_editais):
            key = self._generate_edital_key(e)
            local_map[key] = (idx, e)

        added = 0
        updated = 0
        new_editais = []

        from datetime import datetime

        def to_ts(val):
            # Converte timestamp/datas diversas para epoch
            if not val:
                return None
            try:
                # Try ISO parsing
                if isinstance(val, (int, float)):
                    return float(val)
                # remove timezone Z if present
                s = val.split("Z")[0]
                # If only date part
                if len(s) == 10:
                    return datetime.fromisoformat(s + "T00:00:00").timestamp()
                return datetime.fromisoformat(s).timestamp()
            except Exception:
                try:
                    return float(val)
                except Exception:
                    return None

        for remote in remote_editais:
            key = self._generate_edital_key(remote)
            remote_ts = to_ts(remote.get("dataPublicacaoPncp") or remote.get("dataAtualizacao") or remote.get("dataPublicacao") or remote.get("dataInclusao"))

            if key in local_map:
                idx, local = local_map[key]
                local_ts = to_ts(local.get("dataPublicacaoPncp") or local.get("dataAtualizacao") or local.get("dataPublicacao") or local.get("dataInclusao"))
                # If remote has newer timestamp, replace local
                if remote_ts and (not local_ts or remote_ts > local_ts):
                    logger.info(f"Updating local edital {key}: remote is newer ({remote_ts} > {local_ts})")
                    local_editais[idx] = remote
                    updated += 1
                else:
                    # no action needed
                    continue
            else:
                # Novo edital: adicionar e coletar itens
                logger.info(f"Adding new edital {key}")
                local_editais.append(remote)
                new_editais.append(remote)
                added += 1

        # Salva editais mesclados
        if added or updated:
            try:
                self.save_editais(local_editais)
                logger.info(f"Incremental sync saved: {added} added, {updated} updated")
            except Exception:
                logger.exception("Failed to save editais after incremental sync")

        # Busca itens apenas para novos editais
        if new_editais:
            try:
                logger.info(f"Fetching items for {len(new_editais)} new editais")
                self.fetch_itens_for_all_editais(new_editais)
            except Exception:
                logger.exception("Error while fetching itens for newly added editais")

        return {"added": added, "updated": updated}
