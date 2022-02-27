# -*- coding: utf-8 -*-
"""
Created on Fri Mar 02 23:18:43 2012

@author: lims
"""

from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QDoubleSpinBox, QFormLayout, QVBoxLayout, QToolBar, QMessageBox, \
    QTextEdit, QAction, QApplication, QComboBox, QTableView, QAbstractItemView, QPushButton, QHBoxLayout, QSpacerItem

from sortmodel import MyTableModel
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon
import sys

from utilities import codigo as cd
from pricespinbox import price

class Pagamentos(QDialog):

    def __init__(self, parent=None):
        super(Pagamentos, self).__init__(parent)

        self.current_id = ""
        self.empresa_host = "127.0.0.1"
        self.empresa_user = "root"
        self.empresa_passw = "abc123@123"
        self.empresa_db = "copia"
        self.empresa_port = 3306
        self.cod_fornecedor = ""

        # Connect the Database
        if self.parent() is None:
            self.db = self.connect_db()
            self.user = ""
        else:
            self.conn = self.parent().conn
            self.cur = self.parent().cur
            self.user = self.parent().user

        self.ui()

    def ui(self):

        self.stock_numero = QLineEdit()
        self.stock_numero.setEnabled(False)
        self.factura_numero = QLineEdit()
        self.factura_numero.setEnabled(False)
        self.combo_fornecedor = QLineEdit(self)
        self.spin_pago = price()
        self.spin_pago.setEnabled(False)
        self.spin_saldo = price()
        self.spin_saldo.setEnabled(False)
        self.spin_valor_a_papar = price()
        self.spin_valor_a_papar.valueChanged.connect(self.calcula_novo_saldo)
        self.spin_novo_saldo = price()
        self.spin_novo_saldo.setEnabled(False)

        self.butao_gravar = QPushButton("Gravar")
        self.butao_cancelar = QPushButton("Fechar")
        self.butao_cancelar.clicked.connect(self.close)

        butonlayout = QHBoxLayout()
        butonlayout.addWidget(self.butao_gravar)
        butonlayout.addWidget(self.butao_cancelar)

        # create the view
        self.tv = QTableView(self)

        # set the minimum size
        self.tv.setMinimumSize(400, 300)

        # hide grid
        self.tv.setShowGrid(False)

        self.tv.setSelectionBehavior(QAbstractItemView.SelectRows)
        # set the font

        # hide vertical header
        vh = self.tv.verticalHeader()
        vh.setVisible(False)

        # set horizontal header properties and stretch last column
        hh = self.tv.horizontalHeader()
        hh.setStretchLastSection(True)

        # set column width to fit contents
        self.tv.resizeColumnsToContents()

        # enable sorting
        self.tv.setSortingEnabled(True)

        self.tv.clicked.connect(self.clickedslot)
        self.tv.setAlternatingRowColors(True)

        formalyout = QFormLayout()

        formalyout.addRow(QLabel("Cod. Stock"), self.stock_numero)
        formalyout.addRow(QLabel("Documento"), self.factura_numero)
        formalyout.addRow(QLabel("Fornecedor"), self.combo_fornecedor)
        formalyout.addRow(QLabel("Valor em Dívida"), self.spin_pago)
        formalyout.addRow(QLabel("Saldo"), self.spin_saldo)
        formalyout.addRow(QLabel("Valor a pagar"), self.spin_valor_a_papar)
        formalyout.addRow(QLabel("Novo Saldo"), self.spin_novo_saldo)
        formalyout.addRow(self.tv)
        formalyout.addRow("", butonlayout)

        self.setLayout(formalyout)
        self.setWindowTitle("Pagamentos à Fornecedores")

    def clickedslot(self, index):
        self.row = int(index.row())

        indice = self.tm.index(self.row, 0)
        self.current_id = indice.data()

    def calcula_novo_saldo(self):

        print("calculando")

        try:
            if self.spin_valor_a_papar.value() >= self.spin_saldo.value():

                self.spin_valor_a_papar.setValue(self.spin_saldo.value())

            self.spin_novo_saldo.setValue(self.spin_saldo.value()-
                                          self.spin_valor_a_papar.value())
        except Exception as e:
            print(e)

    def gravar(self):
        if self.spin_valor_a_papar.value() <= 0:
            QMessageBox.warning(self, "Valor a Pagar errado","Valor a pagar deve ser maior que zero (0).")
            self.spin_valor_a_papar.setFocus()
            return

        valor =  self.spin_valor_a_papar.value()

        sql = """UPDATE stock SET saldo={saldo}, pago=pago+{pago} """.format(pago=valor, saldo=valor)

        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(e)

    def total_de_divida(self,codfornecedor):
        sql = """SELECT SUM(valor) as divida, (SUM(valor) - SUM(pago)) as saldo, SUM(saldo) as debito from stock 
        WHERE fornecedor="{}" GROUP BY fornecedor """.format(codfornecedor)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                self.spin_pago.setValue(item[0])
                self.spin_saldo.setValue(item[1])

    def get_cod_stock(self, codctock):
        sql = """select stock.cod, stock.numero, stock.total, stock.pago, stock.saldo, fornecedores.nome FROM stock 
        INNER JOIN forncedores on fornecedores.cod=stock.fornecedor 
        WHERE cod = "{cod}" """.format(cod=codctock)

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        if len(data) > 0:
            self.codfornecedor = "".join(data[0])
            self.total_de_divida(self.codfornecedor)

    def connect_db(self):
        import mysql.connector as mc

        self.conn = mc.connect(host=self.empresa_host,
                               user=self.empresa_user,
                               passwd=self.empresa_passw,
                               db=self.empresa_db,
                               port=self.empresa_port)

        self.cur = self.conn.cursor()

        return

if __name__ == '__main__':

    app = QApplication(sys.argv)

    helloPythonWidget = Pagamentos()
    helloPythonWidget.show()

    sys.exit(app.exec_())