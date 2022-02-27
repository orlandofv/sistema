# -*- coding: utf-8 -*-

import sys
import os
from decimal import Decimal

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import (QMessageBox, QTableView, QPushButton, QApplication, QAbstractItemView,
                             QHBoxLayout, QVBoxLayout, QWidget, QSizePolicy, QLabel, QComboBox, QDateEdit,
                             QCalendarWidget)

from maindialog import Dialog
from sortmodel import MyTableModel

LISTA_DE_CODIGOS = []


class Pesquisa(Dialog):
    def __init__(self, parent=None, titulo="Pesquisa", imagem="./icons/search.ico"):
        super(Pesquisa, self).__init__(parent, titulo, imagem)

        self.current_id = 0
        self.codfacturacao = None

        if self.parent() is not None:
            self.conn = self.parent().conn
            self.cur = self.parent().cur
        else:
            self.conn = ""
            self.cur = ""

        self.ui()
        self.fill_users()
        self.fill_documentos()
        self.fill_caixa_combo()

    def clickedslot(self, index):
        row = int(index.row())
        indice = self.tm.index(row, 0)
        self.current_id = indice.data()

        cod= self.tm.index(row, 1)
        self.codfacturacao = cod.data()

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

        self.data_inicial = QDateEdit()
        self.data_inicial.setCalendarPopup(True)
        self.data_inicial.setCalendarWidget(QCalendarWidget(self))
        self.data_inicial.setDate(QDate.currentDate().addDays(-30))
        self.data_final = QDateEdit()
        self.data_final.setCalendarPopup(True)
        self.data_final.setCalendarWidget(QCalendarWidget(self))
        self.data_final.setDate(QDate.currentDate())
        self.data_inicial.dateChanged.connect(self.fill_caixa_combo)
        self.data_final.dateChanged.connect(self.fill_caixa_combo)
        self.combo_caixa = QComboBox()
        self.combo_caixa.currentIndexChanged.connect(self.get_caixa_cod)
        self.combo_usuario = QComboBox()
        self.combo_documento = QComboBox()
        gravar_btn = QPushButton(QIcon("./icons/delete.ico"), "Eliminar", self)
        fechar_btn = QPushButton(QIcon("./icons/close.ico"), "Fechar", self)
        fechar_btn.clicked.connect(self.close)

        v_box = QVBoxLayout()
        v_box.addWidget(QLabel("Data Inicial"))
        v_box.addWidget(self.data_inicial)
        v_box.addWidget(QLabel("Data Final"))
        v_box.addWidget(self.data_final)
        v_box.addWidget(QLabel("Caixa"))
        v_box.addWidget(self.combo_caixa)
        v_box.addWidget(QLabel("Usuário"))
        v_box.addWidget(self.combo_usuario)
        v_box.addWidget(QLabel("Documento"))
        v_box.addWidget(self.combo_documento)
        v_box.addWidget(self.tabela)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(spacer)
        btn_layout.addWidget(gravar_btn)
        btn_layout.addWidget(fechar_btn)

        v_layout = QVBoxLayout()
        v_layout.setContentsMargins(10, 0, 10, 10)

        v_layout.addLayout(v_box)
        v_layout.addLayout(btn_layout)

        self.layout().addLayout(v_layout)

    def get_cod_documento(self, nome_do_documento):
        """
        :return: Nome do documento baseado no nome
        """
        sql =  """SELECT cod from documentos where nome="{}" """.format(nome_do_documento)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            return None

        return data[0][0]


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

    def get_caixa_cod(self, index):
        return LISTA_DE_CODIGOS[index]

    def fill_caixa_combo(self):

        self.combo_caixa.clear()

        datainicial = QDate(self.data_inicial.date()).toString('yyyy-MM-dd')
        datafinal = QDate(self.data_final.date()).toString('yyyy-MM-dd')

        sql = """SELECT cod, created, modified from caixa WHERE created BETWEEN "{}" AND "{}" order by created DESC
        """.format(datainicial, datafinal)

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

    def fill_users(self):

        sql = "SELECT cod FROM users"
        self.cur.execute(sql)
        data = self.cur.fetchall()

        self.combo_usuario.addItem("Todos")

        if len(data) > 0:
            for item in data:
                self.combo_usuario.addItem(item[0])

            self.combo_usuario.setCurrentText(self.parent().user)
            return True

        return False

    def fill_documentos(self):

        sql = "SELECT nome FROM documentos"
        self.cur.execute(sql)
        data = self.cur.fetchall()

        self.combo_documento.addItem("Todos")

        if len(data) > 0:
            for item in data:
                self.combo_documento.addItem(item[0])

            return True

        return False

    def get_cod_documento(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)

    helloPythonWidget = Pesquisa()
    helloPythonWidget.show()

    sys.exit(app.exec_())

