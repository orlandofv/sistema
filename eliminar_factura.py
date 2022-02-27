# -*- coding: utf-8 -*-

import sys
import os
from decimal import Decimal

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMessageBox, QTableView, QPushButton, QApplication, QAbstractItemView,
                             QHBoxLayout, QVBoxLayout, QWidget, QSizePolicy, QLabel, QComboBox)

from maindialog import Dialog
from sortmodel import MyTableModel

LISTA_DE_CODIGOS = []


class EliminarFacturas(Dialog):
    def __init__(self, parent=None, titulo="Gestão de Facturas", imagem=""):
        super(EliminarFacturas, self).__init__(parent, titulo, imagem)

        self.current_id = 0
        self.codfacturacao = None

        if self.parent() is not None:
            self.conn = self.parent().conn
            self.cur = self.parent().cur
        else:
            self.conn = ""
            self.cur = ""

        self.ui()

        self.fill_caixa_combo()

    def ui(self):
        self.tabela = QTableView(self)

        self.tabela.clicked.connect(self.clickedslot)

        self.tabela.setAlternatingRowColors(True)

        # hide grid
        self.tabela.setShowGrid(False)

        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        # set the font

        # hide vertical header
        vh = self.tabela.verticalHeader()
        vh.setVisible(False)

        # set horizontal header properties and stretch last column
        hh = self.tabela.horizontalHeader()
        hh.setStretchLastSection(True)

        # set column width to fit contents
        self.tabela.resizeColumnsToContents()

        # enable sorting
        self.tabela.setSortingEnabled(True)

        self.combo_caixa = QComboBox()
        self.combo_caixa.currentIndexChanged.connect(self.fill_table)
        gravar_btn = QPushButton(QIcon("./icons/delete.ico"), "Eliminar", self)
        # gravar_btn.clicked.connect(self.selecionado)
        gravar_btn.clicked.connect(self.elimina_dados)
        fechar_btn = QPushButton(QIcon("./icons/close.ico"), "Fechar", self)
        fechar_btn.clicked.connect(self.close)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(spacer)
        btn_layout.addWidget(gravar_btn)
        btn_layout.addWidget(fechar_btn)

        v_layout = QVBoxLayout()
        v_layout.setContentsMargins(10, 0, 10, 10)

        v_layout.addWidget(QLabel("Escolha a caixa"))
        v_layout.addWidget(self.combo_caixa)
        v_layout.addWidget(self.tabela)
        v_layout.addLayout(btn_layout)

        self.layout().addLayout(v_layout)

    def get_caixa_cod(self, index):
        return LISTA_DE_CODIGOS[index]

    def fill_caixa_combo(self):
        sql = """SELECT cod, created, modified from caixa order by created DESC"""
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                LISTA_DE_CODIGOS.append(item[0])

                if item[2] != None:
                    self.combo_caixa.addItem("{}, {} - {}".format(item[0], item[1], item[2]))
                else:
                    self.combo_caixa.addItem("{}, {} - {}".format(item[0], item[1], "Aberta"))
            return True
        else:
            return False

    def fill_table(self):

        if len(LISTA_DE_CODIGOS) == 0:
            return False

        cod_caixa = self.get_caixa_cod(self.combo_caixa.currentIndex())

        header = ["DOC", "codfactura", "Factura", "Descrição", "Qty", "Total", "Cliente"]

        sql = """SELECT facturacaodetalhe.cod, facturacao.cod, facturacao.numero, produtos.nome, 
        facturacaodetalhe.quantidade, facturacaodetalhe.total, clientes.nome FROM produtos 
        INNER JOIN facturacaodetalhe ON produtos.cod=facturacaodetalhe.codproduto
        INNER JOIN facturacao  ON facturacao.cod=facturacaodetalhe.codfacturacao 
        INNER JOIN clientes ON clientes.cod=facturacao.codcliente
        WHERE facturacao.caixa="{caixacod}" AND facturacao.coddocumento="DC20181111111"
        AND (facturacao.codcliente="CL20181111111" OR clientes.nome="Cliente Padrão") 
        ORDER BY facturacao.numero""".format(caixacod=cod_caixa)

        print(sql)

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        if len(data) == 0:
            print("Não há nada")
            tabledata = ["", "", "", "", "", "", ""]
        else:
            tabledata = data

        try:
            # set the table model
            self.tm = MyTableModel(tabledata, header, self)
            self.totalItems = self.tm.rowCount(self)
            self.tabela.setModel(self.tm)
            self.tabela.setColumnHidden(0, True)
            self.tabela.setColumnHidden(1, True)
            self.tabela.setColumnWidth(2, self.tabela.width() * .1)
            self.tabela.setColumnWidth(3, self.tabela.width() * .5)
            self.tabela.setColumnWidth(4, self.tabela.width() * .1)
            self.tabela.setColumnWidth(5, self.tabela.width() * .1)
            self.tabela.setColumnWidth(6, self.tabela.width() * .2)

            # # set row height
            nrows = len(tabledata)
            for row in range(nrows):
                self.tabela.setRowHeight(row, 25)

            return True

        except Exception as e:
            print(e)
            return False

    # Verifica se a tabela está vazia ou não
    def tabelavazia(self):

        if self.codfacturacao == "":
            return

        sql = """ SELECT * from facturacaodetalhe WHERE codfacturacao="{cod}" """.format(cod=self.codfacturacao)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            return True
        else:
            return False

    def calcula_total_geral(self):

        if self.tabelavazia() is True:
            sql = """ delete from facturacao WHERE cod= '{}' """.format(self.codfacturacao)
            self.alterar_de_preco = False

            self.cur.execute(sql)
            self.conn.commit()
            return

        sql = """ SELECT sum(custo), sum(desconto), sum(taxa), sum(subtotal), sum(lucro), sum(total) from 
        facturacaodetalhe WHERE codfacturacao="{codfacturacao}" """.format(codfacturacao=self.codfacturacao)

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        custo = Decimal(data[0][0])
        desconto = Decimal(data[0][1])
        taxa = Decimal(data[0][2])
        subtotal = Decimal(data[0][3])
        lucro = Decimal(data[0][4])
        total = Decimal(data[0][5])

        facturacaosql = """ UPDATE facturacao set custo={custo}, desconto={desconto}, taxa={taxa}, 
        subtotal={subtotal}, lucro={lucro},
        total={total} WHERE cod="{cod}" """.format(custo=custo, desconto=desconto, taxa=taxa, subtotal=subtotal,
                                                   lucro=lucro, total=total, cod=self.codfacturacao)
        try:
            self.cur.execute(facturacaosql)
            self.conn.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def elimina_dados(self):

        if self.current_id == "":
            QMessageBox.information(self, "Info", "Selecione o registo a apagar na tabela")
            return

        sql = """delete from facturacaodetalhe WHERE cod={codigo}""".format(codigo=self.current_id)

        try:
            self.cur.execute(sql)
            self.conn.commit()
            self.fill_table()
            self.calcula_total_geral()
            # QMessageBox.information(self, "Sucesso", "Registo: Eliminado com sucesso")

        except Exception as e:
            QMessageBox.warning(self, "Erro", "Erro ao eliminar o registo: {}".format(e.args))

    def clickedslot(self, index):
        row = int(index.row())
        indice = self.tm.index(row, 0)
        self.current_id = indice.data()

        cod= self.tm.index(row, 1)
        self.codfacturacao = cod.data()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    facturas = EliminarFacturas()
    facturas.show()
    sys.exit(app.exec_())


