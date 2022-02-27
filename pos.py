# -*- coding: utf-8 -*-
"""
Created on Fri Mar 02 23:18:43 2012

@author: lims
"""

class POS:

    def __init__(self):
        self.conn = ""
        self.database = ""
        self.cur = ""

    def connectar_db(self):
        """Estabelece coneccao com a Base de Dados"""
        pass

    def lista_produtos(self):
        """Lista todos produtos existentes na Base de Dados"""
        sql = """select cod, nome, preco, preco1, preco2, preco3, preco4 from produtos"""

    def obter_nomeProduto(self):
        """ Obtem o nome do produto apartir da """
        pass

    def atribuir_nomeProduto(self):
        pass

    def obter_codproduto(self, nomeproduto):
        pass

    def atribir_codProduto(self):
        pass

    def gravar_novoproduto(self, codproduto, preco):
        pass

    def actualizar_Produto(self):
        pass

    def calcular_total(self, codfacturacao):
        """Calcula total geral da transacao"""

        sql = """SELECT SUM(subtotal) as sub, SUM(taxa) as tx, SUM(desconto) as ds, 
        SUM(total) as tt FROM facturacaodetalhe WHERE codfacturacao="{}" """.format(codfacturacao)

