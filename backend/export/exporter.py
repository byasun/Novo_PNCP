"""Módulo de exportação para CSV/XLSX."""

import pandas as pd
import os
import logging
from backend.config import EXPORT_DIR
import re
from openpyxl.utils.exceptions import IllegalCharacterError
from backend.storage.data_manager import DataManager

logger = logging.getLogger(__name__)

class Exporter:
    def __init__(self):
        # Diretório de exportação configurável
        self.export_dir = EXPORT_DIR
        self._ensure_export_dir()
    
    def _ensure_export_dir(self):
        # Garante que a pasta de exportação exista
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)
            logger.info(f"Created export directory: {self.export_dir}")
    
    def export_contratos(self, contratos):
        # Exporta contratos para CSV e XLSX
        if not contratos:
            logger.warning("No contratos to export")
            return
        
        try:
            df = pd.json_normalize(contratos)
            
            csv_path = os.path.join(self.export_dir, "contratos.csv")
            df.to_csv(csv_path, index=False, encoding="utf-8-sig")
            logger.info(f"Exported contratos to {csv_path}")
            
            xlsx_path = os.path.join(self.export_dir, "contratos.xlsx")
            df.to_excel(xlsx_path, index=False, engine="openpyxl")
            logger.info(f"Exported contratos to {xlsx_path}")
            
        except Exception as e:
            logger.error(f"Error exporting contratos: {e}")
            raise
    
    def export_editais(self, editais):
        # Exporta editais para CSV e XLSX (com aba de itens)
        if not editais:
            logger.warning("No editais to export")
            return
        
        try:
            df = pd.json_normalize(editais)
            # Sanitize string fields to remove control/illegal characters for Excel
            def clean_str(s):
                if not isinstance(s, str):
                    return s
                # remove control characters (0x00-0x1F and 0x7F-0x9F)
                return re.sub(r'[\x00-\x1F\x7F-\x9F]', '', s)

            df = df.applymap(lambda v: clean_str(v) if isinstance(v, str) else v)

            csv_path = os.path.join(self.export_dir, "editais.csv")
            df.to_csv(csv_path, index=False, encoding="utf-8-sig")
            logger.info(f"Exported editais to {csv_path}")

            # Prepare items sheet from DataManager
            try:
                dm = DataManager()
                itens = dm.load_itens()
                df_itens = pd.json_normalize(itens) if itens else pd.DataFrame()
            except Exception as e:
                logger.warning(f"Could not load itens for export: {e}")
                df_itens = pd.DataFrame()

            xlsx_path = os.path.join(self.export_dir, "editais.xlsx")
            def _write_xlsx(df_main, df_items, path):
                # Escreve XLSX com múltiplas abas
                with pd.ExcelWriter(path, engine="openpyxl") as writer:
                    df_main.to_excel(writer, sheet_name="Editais", index=False)
                    df_items.to_excel(writer, sheet_name="Itens Editais", index=False)

            try:
                _write_xlsx(df, df_itens, xlsx_path)
                logger.info(f"Exported editais and itens to {xlsx_path}")
            except IllegalCharacterError as e:
                logger.warning(f"Illegal characters prevented XLSX export on first attempt: {e}. Attempting aggressive cleanup and retry...")
                try:
                    # Aggressive cleanup: coerce to str and strip non-printable characters again
                    def aggressive_clean(v):
                        try:
                            s = str(v)
                        except Exception:
                            return ''
                        return re.sub(r'[\x00-\x1F\x7F-\x9F]', '', s)

                    # Coerce all values to strings and aggressively clean control chars
                    df = df.astype(str).applymap(lambda v: aggressive_clean(v))
                    df_itens = df_itens.astype(str).applymap(lambda v: aggressive_clean(v))
                    _write_xlsx(df, df_itens, xlsx_path)
                    logger.info(f"Exported editais and itens to {xlsx_path} after aggressive cleanup")
                except Exception as e2:
                    logger.error(f"Failed to export XLSX after aggressive cleanup: {e2}. CSV available at {csv_path}")
            except Exception as e:
                logger.error(f"Unexpected error exporting XLSX: {e}")
            
        except Exception as e:
            logger.error(f"Error exporting editais: {e}")
            raise
    
    def export_itens(self, itens):
        # Exporta itens (contratos) para CSV e XLSX
        if not itens:
            logger.warning("No itens to export")
            return
        
        try:
            df = pd.json_normalize(itens)
            
            csv_path = os.path.join(self.export_dir, "itens_contratos.csv")
            df.to_csv(csv_path, index=False, encoding="utf-8-sig")
            logger.info(f"Exported itens to {csv_path}")
            
            xlsx_path = os.path.join(self.export_dir, "itens_contratos.xlsx")
            df.to_excel(xlsx_path, index=False, engine="openpyxl")
            logger.info(f"Exported itens to {xlsx_path}")
            
        except Exception as e:
            logger.error(f"Error exporting itens: {e}")
            raise
    
    def export_all(self, contratos, itens):
        # Exportação completa (contratos + itens)
        logger.info("Starting full export...")
        self.export_contratos(contratos)
        self.export_itens(itens)
        logger.info("Full export completed")
