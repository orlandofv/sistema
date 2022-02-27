# -*- coding: utf-8 -*-
"""
Created on Fri Mar 02 23:18:43 2012

@author: lims
"""

from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QVBoxLayout, QToolBar, QMessageBox, \
    QTextEdit, QAction, QApplication, QTableView, QAbstractItemView, QComboBox, QFormLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sys

from sortmodel import MyTableModel

import sqlite3 as lite

DB_FILENAME = "dados.tsdb"


class Cliente(QDialog):
    def __init__(self, parent=None):
        super(Cliente, self).__init__(parent)

        self.list_de_documentos = []
        self.accoes()
        self.ui()

        if self.parent() is None:
            self.db = self.connect_db()
        else:
            self.cur = self.parent().cur
            self.conn = self.parent().conn

        self.enchedocumentos()
        self.fill_table()

    def ui(self):
        html = """<center style= "background-image: './images/control.png'" > <h2 > Documentos não Finalizados </h2> </center> """

        titulo = QLabel(html)

        vLay = QVBoxLayout()
        self.tabela = QTableView(self)

        # self.tabela.clicked.connect(self.clickedslot)
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

        label = QLabel("Selecione o documento")
        self.documentos_box = QComboBox()
        self.documentos_box.currentIndexChanged.connect(self.fill_table)
        self.documentos_box.setFocus()

        formlay = QFormLayout()

        formlay.addRow(label, self.documentos_box)

        vLay.addWidget(titulo)
        vLay.addLayout(formlay)
        vLay.addWidget(self.tabela)
        vLay.addWidget(self.tool)
        self.setLayout(vLay)

        self.setWindowTitle("Documentos não Finalizados")

        style = """
            margin: 0;
            padding: 0;
            border-image:url(./images/transferir.jpg) 30 30 stretch;
            background:#303030;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 12px;
            color: #FFFFFF;
        """
        titulo.setStyleSheet(style)

    def accoes(self):
        self.tool = QToolBar()
        self.tool.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        gravar = QAction(QIcon("./images/ok.png"), "Gravar\nDados", self)
        fechar = QAction(QIcon("./images/filequit.png"), "&Fechar", self)

        self.tool.addAction(gravar)

        self.tool.addSeparator()
        self.tool.addAction(fechar)

        gravar.triggered.connect(self.activardocumento)
        fechar.triggered.connect(self.fechar)

    def enchedocumentos(self):
        """
            Enche documentos na Combobox e a lista com o respectivo códido de cada documento
        :return: Lista de códigos de documentos
        """

        self.documentos_box.clear()
        self.list_de_documentos.clear()

        sql = """select data, facturacao.nome, facturacao.cod from facturacao INNER JOIN facturacaodetalhe 
        ON facturacao.cod=facturacaodetalhe.codfacturacao
        WHERE finalizado=0 and facturacaodetalhe.codarmazem="{}" GROUP BY facturacao.cod ORDER BY 
        facturacao.data DESC""".format(self.parent().codarmazem)
        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        if len(data) > 0:
            for item in data:
                self.documentos_box.addItem(str(item[1]))
                self.list_de_documentos.append(item[2])
        else:
            self.close()

        return self.list_de_documentos

    def fill_table(self):

        header = ["Artigo", "Descrição", "Preço", "Qty" ,"Total"]

        if len(self.list_de_documentos) == 0:
            return False

        indice = self.list_de_documentos[self.documentos_box.currentIndex()]
        sql = """ select codproduto, produtos.nome, facturacaodetalhe.preco, facturacaodetalhe.quantidade,
        facturacaodetalhe.total from produtos INNER JOIN facturacaodetalhe ON 
        produtos.cod=facturacaodetalhe.codproduto WHERE codfacturacao="{}" """.format(indice)

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]
        self.tabledata = data

        if len(data) == 0:
            self.tabledata = [('', '', '', '', '')]
        try:

            # set the table model
            self.tm = MyTableModel(self.tabledata, header, self)
            self.totalItems = self.tm.rowCount(self)
            self.tabela.setModel(self.tm)
        except Exception as e:
            return False
        # # set row height
        nrows = len(self.tabledata)
        for row in range(nrows):
            self.tabela.setRowHeight(row, 25)

        return True

    def closeEvent(self, evt):
        parent = self.parent()
        try:
            if parent is not None:
                parent.fill_table()
        except Exception as e:
            return

    def fechar(self):
        self.close()

    def connect_db(self):
        # Connect to database and retrieves data
        try:
            self.conn = lite.connect(DB_FILENAME)
            self.cur = self.conn.cursor()

        except Exception as e:
            QMessageBox.critical(self, "Erro ao conectar a Base de Dados",
                                 "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
            sys.exit(True)

    def activardocumento(self):
        if self.parent() is None: return

        parente = self.parent()

        indice = self.list_de_documentos[self.documentos_box.currentIndex()]
        parente.codigogeral = indice
        parente.calcula_total_geral()
        parente.butao_apagarTudo.setEnabled(True)
        parente.butao_apagarItem.setEnabled(True)

        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    helloPythonWidget = Cliente()
    helloPythonWidget.show()

    sys.exit(app.exec_())