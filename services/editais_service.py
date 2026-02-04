import logging
from api_client.pncp_client import PNCPClient
from storage.data_manager import DataManager
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class EditaisService:
    def __init__(self):
        self.client = PNCPClient()
        self.data_manager = DataManager()
    
    def fetch_all_editais(self, data_inicial=None, data_final=None, codigo_modalidade=6):
        logger.info(f"Starting editais fetch with codigo_modalidade: {codigo_modalidade}...")
        
        # Callback to save checkpoints
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
        return editais
    
    def fetch_itens_for_edital(self, cnpj, ano, numero):
        logger.info(f"Fetching itens for edital {cnpj}/{ano}/{numero}...")
        itens = self.client.get_itens_edital(cnpj, ano, numero)
        return itens if itens else []

    def _extract_month_from_edital(self, edital):
        # Try explicit field
        mes = edital.get("mesCompra") or edital.get("mes")
        if mes:
            try:
                return int(mes)
            except:
                pass

        # Try to parse common date fields
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
    
    def fetch_itens_for_all_editais(self, editais):
        """
        Fetch items for all editais using parallel threads with incremental saving.
        This will iterate each edital, try to determine the year/month and orgao CNPJ
        and use the PNCP endpoints to fetch all items (paginated). Each item will be
        annotated with editorial linkage fields and returned as a flat list.
        
        Saves progress incrementally to allow resuming if interrupted.
        """
        from config import ITEMS_FETCH_THREADS, ITEMS_FETCH_DELAY_PER_THREAD, ITEMS_FETCH_CHECKPOINT
        
        if not editais:
            logger.info("No editais provided for item fetching")
            return []

        # Load existing items to avoid duplicates and enable resuming
        existing_itens = self.data_manager.load_itens()
        existing_keys = set()
        for item in existing_itens:
            # Create key from edital identifiers + item number
            key = f"{item.get('edital_cnpj')}_{item.get('edital_ano')}_{item.get('edital_numero')}_{item.get('numeroItem')}"
            existing_keys.add(key)
        
        logger.info(f"Loaded {len(existing_itens)} existing items from storage")
        logger.info(f"Fetching items for {len(editais)} editais using {ITEMS_FETCH_THREADS} parallel threads...")
        
        all_itens = existing_itens.copy()  # Start with existing items
        processed_count = 0
        
        # Use ThreadPoolExecutor for parallel fetching
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
                    
                    # Filter out duplicates (items we already have)
                    for item in itens:
                        key = f"{item.get('edital_cnpj')}_{item.get('edital_ano')}_{item.get('edital_numero')}_{item.get('numeroItem')}"
                        if key not in existing_keys:
                            all_itens.append(item)
                            existing_keys.add(key)
                    
                    processed_count += 1
                    
                    # Save checkpoint every N editais
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

        # Final save
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
        Fetch items for a single edital. This runs in a thread.
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
                # First, check if there are any items for this edital/period
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

            # Annotate items with linkage to the edital
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
        return self.data_manager.load_editais()
    
    def get_edital_by_key(self, edital_key):
        editais = self.data_manager.load_editais()
        for edital in editais:
            key = self._generate_edital_key(edital)
            if key == edital_key:
                return edital
        return None
    
    def get_itens_by_edital(self, cnpj, ano, numero):
        all_itens = self.data_manager.load_itens()
        return [
            item for item in all_itens
            if (item.get("edital_cnpj") == cnpj and
                str(item.get("edital_ano")) == str(ano) and
                str(item.get("edital_numero")) == str(numero))
        ]
    
    def _generate_edital_key(self, edital):
        cnpj = edital.get("orgaoEntidade", {}).get("cnpj", "") or edital.get("cnpjOrgao", "")
        ano = edital.get("anoCompra", "")
        numero = edital.get("numeroCompra", "")
        return f"{cnpj}_{ano}_{numero}"
    
    def save_editais(self, editais):
        self.data_manager.save_editais(editais)
        logger.info(f"Saved {len(editais)} editais to local storage")
    
    def save_itens(self, itens):
        self.data_manager.save_itens(itens)
        logger.info(f"Saved {len(itens)} itens to local storage")
    
    def update_editais(self, data_inicial=None, data_final=None, codigo_modalidade=6):
        logger.info("Updating editais (preserving existing + adding/updating new)")

        local_editais = self.data_manager.load_editais()

        # If there is existing data, perform incremental sync to preserve all editais
        if local_editais:
            self.sync_editais(data_inicial, data_final, codigo_modalidade)
            return self.data_manager.load_editais()

        # First-time load (no local data): full fetch + save
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

    def sync_editais(self, data_inicial=None, data_final=None, codigo_modalidade=6):
        """
        Incremental sync: fetch remote editais for the given period, compare with local
        stored editais by key and timestamp, update existing records when remote is
        newer, add new editais, and fetch items only for the newly added editais.

        Returns a summary dict: {added: int, updated: int}
        """
        logger.info(f"Starting incremental sync for editais ({data_inicial} to {data_final})")
        # Fetch remote editais for period (this uses existing checkpointed fetch)
        remote_editais = self.fetch_all_editais(data_inicial, data_final, codigo_modalidade)
        if not remote_editais:
            logger.info("No remote editais fetched for incremental sync")
            return {"added": 0, "updated": 0}

        # Load local editais
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
                # New edital: add and schedule items fetch
                logger.info(f"Adding new edital {key}")
                local_editais.append(remote)
                new_editais.append(remote)
                added += 1

        # Save merged editais
        if added or updated:
            try:
                self.save_editais(local_editais)
                logger.info(f"Incremental sync saved: {added} added, {updated} updated")
            except Exception:
                logger.exception("Failed to save editais after incremental sync")

        # Fetch items only for the newly added editais
        if new_editais:
            try:
                logger.info(f"Fetching items for {len(new_editais)} new editais")
                self.fetch_itens_for_all_editais(new_editais)
            except Exception:
                logger.exception("Error while fetching itens for newly added editais")

        return {"added": added, "updated": updated}
