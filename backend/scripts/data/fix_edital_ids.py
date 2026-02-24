"""
Script para atualizar editais.json e itens.json adicionando o campo _edital_id no início de cada edital e item.
O campo _edital_id é usado para vincular itens ao edital correspondente.

Este script padroniza o campo de vínculo entre editais e itens, facilitando a integridade referencial e buscas rápidas.
"""
import os
import sys
import json

# Adiciona a pasta raiz ao sys.path para permitir imports absolutos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.storage.data_manager import DataManager

def generate_edital_id(cnpj, ano, numero):
    """
    Gera uma string única para identificar um edital a partir de CNPJ, ano e número.
    """
    return f"{str(cnpj)}_{str(ano)}_{str(numero)}"

def padroniza_edital_id(edital):
    """
    Adiciona o campo _edital_id ao edital, garantindo que seja o primeiro campo.
    """
    cnpj = edital.get("orgaoEntidade", {}).get("cnpj") or edital.get("cnpjOrgao") or edital.get("cnpj")
    ano = edital.get("anoCompra") or edital.get("ano")
    numero = edital.get("numeroCompra") or edital.get("numero")
    edital_id = generate_edital_id(cnpj, ano, numero)
    # Garante que _edital_id é o primeiro campo
    new_edital = {"_edital_id": edital_id}
    new_edital.update(edital)
    return new_edital

def padroniza_item_id(item):
    """
    Adiciona o campo _edital_id ao item, garantindo que seja o primeiro campo.
    """
    cnpj = item.get("edital_cnpj") or item.get("cnpjOrgao") or item.get("cnpj")
    ano = item.get("edital_ano") or item.get("anoCompra") or item.get("ano")
    numero = item.get("edital_numero") or item.get("numeroCompra") or item.get("numero")
    edital_id = generate_edital_id(cnpj, ano, numero)
    # Garante que _edital_id é o primeiro campo
    new_item = {"_edital_id": edital_id}
    new_item.update(item)
    return new_item

def main():
    """
    Função principal que atualiza os arquivos de editais e itens, adicionando o campo _edital_id padronizado.
    """
    data_manager = DataManager()
    editais = data_manager.load_editais()
    itens = data_manager.load_itens()
    # Atualiza todos os editais e itens com o campo _edital_id padronizado
    editais_atualizados = [padroniza_edital_id(e) for e in editais]
    itens_atualizados = [padroniza_item_id(i) for i in itens]

    data_manager.save_editais(editais_atualizados)
    data_manager.save_itens(itens_atualizados)
    print(f"Atualização concluída: {len(editais_atualizados)} editais e {len(itens_atualizados)} itens atualizados.")

if __name__ == "__main__":
    # Permite execução direta do script
    main()
