# -*- coding: utf-8 -*-

import datetime
from decimal import Decimal
from time import localtime, strftime
from utilities import ANO_ACTUAL, DATA_ACTUAL, DATA_HORA_FORMATADA, DATA_HORA_FORMATADA_MYSQL, DIA, HORA, MES

class Facturacao(object):

    # facturacao table fields
    numero = 1
    coddocumento = "DC20181111111"
    codcliente = "CL20181111111"
    data = DATA_HORA_FORMATADA_MYSQL
    custo = 0
    subtotal = 0
    desconto = 0
    taxa = 0
    total = 0
    lucro = 0
    debito = 0
    credito = 0
    saldo = 0
    troco = 0
    banco = 0
    cash = 0
    transferencia = 0
    estado = 1
    extenso = ""
    ano = ANO_ACTUAL
    mes = MES
    obs = ""
    created = DATA_HORA_FORMATADA_MYSQL
    modified = DATA_HORA_FORMATADA_MYSQL
    modified_by = "administrador"
    created_by = "administrador"
    finalizado = 0
    caixa = ""
    pago = 0
    comissao = 0
    pagamento = 0

    # facturacaodetalhe table fields
    codfacturacao = ""
    codproduto = ""
    custo_produto = 0
    preco = 0
    quantidade = 0
    subtotal_produto = 0
    desconto_produto = 0
    taxa_produto = 0
    total_produto = 0
    lucro_produto = 0
    codarmazem = "AR201875cNP1"

    #MySQL DB Connection
    conn = ""
    cur = ""
    actualizar_detalhes = False
    incluir_detalhes = True
    
    def __init__(self, connection=None, cursor=None):

        self.conn = connection
        self.cur = cursor

        self.connect_db()

    def create_invoice(self, cod_facturacao, cod_caixa, cod_documento, cod_cliente, cod_user):
        """Creates a Invoice """

        erros = ["", False, None]

        if (cod_caixa , cod_facturacao, cod_documento, cod_cliente, cod_user) in erros:
            print("codfacturacao, codcaixa, coddocuento, codcliente e user nao podem estar vazios")
            return False

        self.codfacturacao = cod_facturacao
        self.caixa = cod_caixa
        self.coddocumento = cod_documento
        self.codcliente = cod_cliente
        self.created_by = self.modified_by = cod_user

        values = (self.codfacturacao, self.numero, self.coddocumento, self.codcliente, self.data, self.custo, self.subtotal,
                  self.desconto, self.taxa, self.total, self.lucro, self.debito, self.credito, self.saldo, self.troco,
                  self.banco, self.cash, self.transferencia, self.estado, self.extenso, self.ano, self.mes, self.obs,
                  self.created, self.modified, self.modified_by, self.created_by, self.finalizado, self.caixa,
                  self.pago, self.comissao, self.pagamento)

        detalhes_values = (self.codfacturacao, self.codproduto, self.custo_produto, self.preco, self.quantidade,
                           self.subtotal_produto, self.desconto_produto, self.taxa_produto, self.total_produto,
                           self.lucro_produto, self.codarmazem)

        # se for novo dado
        if self.existe_codfacturacao(self.codfacturacao) is False:
            sql = """INSERT INTO facturacao (cod, numero, coddocumento, codcliente, data, custo, subtotal, desconto, 
            taxa, total, lucro, debito, credito, saldo, troco, banco, cash, tranferencia, estado, extenso, ano, mes, 
            obs, created, modified, modified_by, created_by, finalizado, caixa, pago, comissao, pagamento) 
            VALUES {} """.format(values)

            detalhe_sql = """INSERT INTO facturacaodetalhe (codfacturacao, codproduto, custo, preco, quantidade, 
            subtotal, desconto, taxa, total, lucro, codarmazem) VALUES {} """.format(detalhes_values)

        # Se estivermos a actualizar
        else:
            sql = """ UPDATE facturacao SET custo=custo+{}, subtotal=subtotal+{}, desconto=desconto+{}, taxa=taxa+{},
                        total=total+{}, lucro=lucro+{}, debito=debito+{} WHERE cod="{}" """.format(self.custo,
                                                                                                   self.subtotal,
                                                                                                   self.desconto,
                                                                                                   self.taxa,
                                                                                                   self.total,
                                                                                                   self.lucro,
                                                                                                   self.total,
                                                                                                   self.codfacturacao)

            if self.existe_produto(self.codfacturacao, self.codproduto):
                # Se for so para actualizar as linhas de facturacaodetalhe
                if self.actualizar_detalhes is True:
                    detalhe_sql = """UPDATE facturacaodetalhe SET preco={}, quantidade={}, custo={}, desconto={},subtotal={}, taxa={}, 
                    total={}, lucro={} WHERE codfacturacao="{}" AND codproduto="{}" """.format(self.preco, self.quantidade,
                                                                                             self.custo_produto,
                                                                                               self.desconto_produto,
                                                                                             self.subtotal_produto,
                                                                                             self.taxa_produto,
                                                                                             self.total_produto,
                                                                                             self.lucro_produto,
                                                                                             self.codfacturacao,
                                                                                             self.codproduto)

                # Se for so para incrementar as linhas de facturacaodetalhe
                else:
                    detalhe_sql = """UPDATE facturacaodetalhe SET preco={}, quantidade=quantidade+{}, custo=custo+{}, 
                    subtotal=subtotal+{}, taxa=taxa+{}, total=total+{}, lucro=lucro+{} WHERE codfacturacao="{}" 
                    AND codproduto="{}" """.format(self.preco, self.quantidade, self.custo_produto, self.subtotal_produto,
                                                 self.taxa_produto, self.total_produto, self.lucro_produto,
                                                 self.codfacturacao, self.codproduto)
            else:
                detalhe_sql = """INSERT INTO facturacaodetalhe (codfacturacao, codproduto, custo, preco, quantidade, 
                            subtotal, desconto, taxa, total, lucro, codarmazem) VALUES {} """.format(detalhes_values)
        try:
            print(sql)
            print("Detalhes", detalhe_sql)
            self.cur.execute(sql)
            
            if self.incluir_detalhes is True:
                self.cur.execute(detalhe_sql)

            self.conn.commit()
            self.calcula_total_geral(cod_facturacao)

            return True
        except Exception as e:
            self.conn.rollback()
            print("Erro na criação ou actualização da Factura {}".format(e))
            return False

    def get_produto_detalhe(self, produto, cod_armazem):
        """
        :param produto: codigo do produto
        :param cod_armazem: armazem onde em uso pela aplicacao
        :return: cod, preco, custo, foto, nome, quantidade, codtaxa
        """
        sql = """select produtos.cod, produtos.preco, produtos.custo, produtos.foto, produtos.nome, 
        produtosdetalhe.quantidade, produtos.codtaxa from produtos INNER JOIN produtosdetalhe ON
        produtos.cod=produtosdetalhe.codproduto WHERE produtos.cod= "{nome}"
        or produtos.cod_barras = "{cod}" and produtosdetalhe.codarmazem="{armazem}" 
        GROUP BY produtos.cod """.format(nome=produto, cod=produto, armazem=cod_armazem)

        self.cur.execute(sql)
        # lista = self.cur.fetchall()
        data = self.cur.fetchall()

        if len(data) > 0:
            return data[0]
        else:
            return []

    def update_data(self, cod_facturacao, cod_produto, preco, quantidade, taxa, custo):
        """Updates data records"""

        subtotal_linha = Decimal(quantidade) * Decimal(preco)
        taxa_linha = Decimal(taxa)
        total_linha = subtotal_linha * taxa_linha + subtotal_linha
        custo_linha = Decimal(custo) * Decimal(quantidade)
        lucro_linha = subtotal_linha - custo_linha

        facturacao_detalhe_sql = """UPDATE facturacaodetalhe SET preco={}, quantidade={}, custo={},
        subtotal={}, taxa={}, total={}, lucro={} 
        WHERE codfacturacao="{}" and codproduto="{}" """.format(preco, quantidade, custo_linha, subtotal_linha,
                                                              taxa_linha, total_linha, lucro_linha, cod_facturacao,
                                                              cod_produto)

        print(facturacao_detalhe_sql)

        try:
            self.cur.execute(facturacao_detalhe_sql)
            self.conn.commit()
            return True
        except Exception as e:
            print("Erro:\n'{}' ".format(e))
            return False

    def update_data_cod(self, cod_facturacao, cod_facturacao_1, cod_produto, preco, quantidade, taxa, custo):
        """Updates data records"""

        subtotal_linha = Decimal(quantidade) * Decimal(preco)
        taxa_linha = Decimal(taxa)
        total_linha = subtotal_linha * taxa_linha + subtotal_linha
        custo_linha = Decimal(custo) * Decimal(quantidade)
        lucro_linha = subtotal_linha - custo_linha

        facturacao_detalhe_sql = """UPDATE facturacaodetalhe SET codfacturacao="{}", preco={}, quantidade={}, custo={},
        subtotal={}, taxa={}, total={}, lucro={} 
        WHERE codfacturacao="{}" and codproduto="{}" """.format(cod_facturacao_1, preco, quantidade, custo_linha,
                                                              subtotal_linha, taxa_linha, total_linha, lucro_linha,
                                                              cod_facturacao, cod_produto)

        print(facturacao_detalhe_sql)

        try:
            self.cur.execute(facturacao_detalhe_sql)
            self.conn.commit()
            return True
        except Exception as e:
            print("Erro:\n'{}' ".format(e))
            return False


    def calcula_total_geral(self, cod_facturacao):
        """calculates the sum of pro"""

        sql = """SELECT SUM(custo) as custo, SUM(subtotal) as subtotal, SUM(taxa) as taxa, 
        SUM(total) as total, SUM(lucro) as lucro FROM facturacaodetalhe WHERE codfacturacao="{}" 
        GROUP BY codfacturacao """.format(cod_facturacao)

        try:
            self.cur.execute(sql)
            lista = self.cur.fetchall()

            data = [tuple(str(item) for item in t) for t in lista]

            if len(data) > 0:
                return data

        except Exception as e:
            print("Erro:\n'{}' ".format(e))

        return []

    def delete_data(self, cod_facturacao):
        """deletes records from database"""

        facturacao_detalhe_sql = """DELETE FROM facturacaodetalhe WHERE codfacturacao="{}" """.format(cod_facturacao)
        facturacao_sql = """DELETE FROM facturacao WHERE cod="{}" """.format(cod_facturacao)

        self.cur.execute(facturacao_detalhe_sql)
        self.cur.execute(facturacao_sql)

        try:
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print("Erro:\n'{}' ".format(e))
            return False

    def get_data(self, cod_facturacao):
        """Retrivies a List of data is not empty from database, otherwise returns empty List"""

        sql = """SELECT codproduto, preco, taxa, custo, quantidade FROM facturacaodetalhe 
        WHERE codfacturacao="{}" """.format(cod_facturacao)

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        if len(data) > 0:
            return data

        return []

    def get_nome_produto(self, cod_produto):
        """Gets the primary key of a product given the name"""
        sql = """SELECT nome FROM produtos WHERE cod="{}" """.format(cod_produto)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data[0]:
                return item

        return None

    def get_codproduto(self, nome_produto):
        """Gets the primary key of a product given the name"""
        sql = """SELECT cod FROM produtos WHERE nome="{}" """.format(nome_produto)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data[0]:
                return item

        return None

    def get_coddocumento(self, nome_documento):
        """Gets the primary key of a doc given the name"""
        sql = """SELECT cod FROM documentos WHERE nome="{}" """.format(nome_documento)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data[0]:
                return item

        return None

    def get_codtaxa(self, nome_taxa):
        """Gets the primary key of a tax given the name"""
        sql = """SELECT cod FROM taxas WHERE nome="{}" """.format(nome_taxa)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data[0]:
                return item

        return None

    def get_valor_taxa(self, codtaxa):
        """Gets value of a tax given the name"""
        sql = """SELECT valor FROM taxas WHERE cod="{}" """.format(codtaxa)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data[0]:
                return item

        return 0

    def get_codcliente(self, nome_cliente):
        """Gets the primary key of a costumer given the name"""
        sql = """SELECT cod FROM clientes WHERE nome="{}" """.format(nome_cliente)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data[0]:
                return item

        return None

    def get_codarmazem(self, nome_armazem):
        """Gets the primary key of a store given the name"""
        sql = """SELECT cod FROM armazem WHERE nome="{}" """.format(nome_armazem)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data[0]:
                return item

        return None

    def get_codfornecedor(self, nome_fornecedor):
        """Gets the primary key of a supplier given the name"""
        sql = """SELECT cod FROM fornecedores WHERE nome="{}" """.format(nome_fornecedor)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data[0]:
                return item

        return None

    def get_coduser(self, nome_user):
        """Gets the primary key of a user given the name"""
        sql = """SELECT cod FROM users WHERE nome="{}" """.format(nome_user)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data[0]:
                return item

        return None

    def existe_codfacturacao(self, cod_documento):

        sql = """SELECT cod from facturacao WHERE cod="{}" """.format(cod_documento)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return True
        else:
            return False

    def existe_produto(self,cod_facturacao, cod_produto):

        sql = """SELECT codproduto from facturacaodetalhe WHERE codfacturacao="{}" 
        AND codproduto="{}" """.format(cod_facturacao, cod_produto)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return True
        else:
            return False

    def connect_db(self):

        import mysql.connector as mc

        try:
            self.conn = mc.connect(host="127.0.0.1",
                                   user="root",
                                   passwd="abc123@123",
                                   db="agencia_boa",
                                   port="3306")

            self.cur = self.conn.cursor()
            print("Sucesso")
            return True

        except Exception as e:
            print("Falha de conexao: ", e)
            return False

    def addNumers(self, *args):

        if len(args) == 0:
            return 0

        return sum(args)


if __name__ == '__main__':
    app = Facturacao()