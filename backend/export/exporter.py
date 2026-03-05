"""
Módulo de exportação para CSV/XLSX.

Fornece a classe Exporter, responsável por exportar dados de contratos, editais e itens
em formatos CSV e Excel, utilizando pandas e openpyxl.

Antes da exportação, os dados são normalizados pelo módulo normalizer para remover
caracteres ilegais que causam erros no openpyxl.
"""

import pandas as pd
import os
import logging
from backend.config import EXPORT_DIR
import re
from openpyxl.utils.exceptions import IllegalCharacterError
from backend.storage.data_manager import DataManager
from backend.export.normalizer import normalize_records

logger = logging.getLogger(__name__)

class Exporter:
    """
    Classe responsável por exportar dados do sistema PNCP em formatos CSV e XLSX.
    Utiliza pandas para manipulação e exportação dos dados.
    """
    def __init__(self):
        # Diretório de exportação configurável
        self.export_dir = EXPORT_DIR
        self._ensure_export_dir()

    def _ensure_export_dir(self):
        """
        Garante que a pasta de exportação exista.
        Cria o diretório caso não exista.
        """
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)
            logger.info(f"Diretório de exportação criado: {self.export_dir}")

    def export_contratos(self, contratos):
        """
        Exporta a lista de contratos para arquivos CSV e XLSX.
        Os arquivos são salvos no diretório de exportação configurado.
        """
        if not contratos:
            logger.warning("Nenhum contrato para exportar")
            return

        try:
            df = pd.json_normalize(contratos)

            csv_path = os.path.join(self.export_dir, "contratos.csv")
            df.to_csv(csv_path, index=False, encoding="utf-8-sig")
            logger.info(f"Contratos exportados para {csv_path}")

            xlsx_path = os.path.join(self.export_dir, "contratos.xlsx")
            df.to_excel(xlsx_path, index=False, engine="openpyxl")
            logger.info(f"Contratos exportados para {xlsx_path}")
            
        except Exception as e:
            logger.error(f"Error exporting contratos: {e}")
            raise
    
    def export_editais(self, editais):
        # Exporta editais + itens para um único CSV e um XLSX (com abas separadas)
        if not editais:
            logger.warning("No editais to export")
            return
        
        try:
            # Normaliza editais
            logger.info("Normalizing editais data for export...")
            editais_clean = normalize_records(editais)
            df = pd.json_normalize(editais_clean)
            df.insert(0, 'tipo', 'edital')

            # Carrega e normaliza itens
            df_itens = pd.DataFrame()
            try:
                dm = DataManager()
                itens = dm.load_itens()
                if itens:
                    logger.info("Normalizing itens data for export...")
                    itens_clean = normalize_records(itens)
                    df_itens = pd.json_normalize(itens_clean)
                    df_itens.insert(0, 'tipo', 'item')
            except Exception as e:
                logger.warning(f"Could not load/export itens: {e}")

            # CSV único: editais + itens concatenados (com coluna 'tipo' distinguindo)
            csv_path = os.path.join(self.export_dir, "editais.csv")
            df_combined = pd.concat([df, df_itens], ignore_index=True, sort=False)
            df_combined.to_csv(csv_path, index=False, encoding="utf-8-sig")
            logger.info(f"Exported {len(df)} editais + {len(df_itens)} itens to {csv_path}")

            # Exporta XLSX com ambas as abas
            xlsx_path = os.path.join(self.export_dir, "editais.xlsx")
            def _write_xlsx(df_main, df_items, path):
                with pd.ExcelWriter(path, engine="openpyxl") as writer:
                    df_main.to_excel(writer, sheet_name="Editais", index=False)
                    df_items.to_excel(writer, sheet_name="Itens Editais", index=False)

            try:
                _write_xlsx(df, df_itens, xlsx_path)
                logger.info(f"Exported editais and itens to {xlsx_path}")
            except IllegalCharacterError as e:
                logger.warning(f"Illegal characters after normalization: {e}. Attempting printable-only fallback...")
                try:
                    def printable_only(v):
                        try:
                            s = str(v)
                        except Exception:
                            return ''
                        return ''.join(c for c in s if c.isprintable() or c in (' ', '\t'))

                    for dframe in [df, df_itens]:
                        for col in dframe.columns:
                            if dframe[col].dtype == "object":
                                dframe[col] = dframe[col].map(printable_only)
                    _write_xlsx(df, df_itens, xlsx_path)
                    logger.info(f"Exported editais and itens to {xlsx_path} after printable-only fallback")
                except Exception as e2:
                    logger.error(f"Failed to export XLSX even after fallback: {e2}. CSV available at {csv_path}")
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
