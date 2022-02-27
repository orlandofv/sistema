# -*- coding: utf-8 -*-
"""
Created on Fri Mar 02 23:18:43 2012

@author: lims
"""
import datetime
from decimal import Decimal

from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QCalendarWidget, QFormLayout, QVBoxLayout, QToolBar, QMessageBox,\
    QDateEdit, QAction, QApplication, QComboBox, QPlainTextEdit

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon
import sys
from time import localtime, strftime

from pricespinbox import price

import sqlite3 as lite

DB_FILENAME = "dados.tsdb"
DATA_HORA_FORMATADA = strftime("%Y-%m-%d %H:%M:%S", localtime())
DATA_ACTUAL = datetime.date.today()
ANO_ACTUAL = DATA_ACTUAL.year
DIA = DATA_ACTUAL.day
MES = DATA_ACTUAL.month


class CC_Fornecedor(QDialog):
    cod_cc_fornecedor = 0
    cod_documento = 0

    def __init__(self, parent=None):
        super(CC_Fornecedor, self).__init__(parent)

        if self.parent() is None:
            self.db = self.connect_db()
        else:
            self.cur = self.parent().cur
            self.conn = self.parent().conn

        self.accoes()
        self.ui()

        self.enche_fornecedores()

    def calcula_valor_total(self, iva):
        vt = iva * 117 / 17
        self.valor_a_pagar.setValue(vt)

        return vt

    def calcula_saldo(self, valor_1, valor_2):
        print("A Calcular Saldo.....", "Valor a Pagar: ", valor_1, "Valor Pago: ", valor_2, valor_1 < valor_2)
        if valor_1 < valor_2:
            self.valor_pago.setValue(valor_1)

        saldo = valor_1 - valor_2
        self.saldo.setValue(saldo)

        return saldo

    def ui(self):
        html = """<center style= "background-image: './images/control.png'" > <h2 > Conta Corrente de Fornecedores </h2> </center> """

        titulo = QLabel(html)

        self.fornecedor = QComboBox()
        self.documento = QLineEdit()
        self.documento.setMaxLength(20)
        calendario = QCalendarWidget()
        self.data = QDateEdit()
        self.data.setCalendarPopup(True)
        self.data.setCalendarWidget(calendario)
        self.data.setDate(QDate.currentDate())
        self.iva = price()
        self.iva.valueChanged.connect(lambda: self.calcula_valor_total(self.iva.value()))
        self.valor_a_pagar = price()
        self.valor_a_pagar.valueChanged.connect(lambda: self.calcula_saldo(self.valor_a_pagar.value(),
                                                                        self.valor_pago.value()))
        self.valor_pago = price()
        self.valor_pago.setVisible(False)
        self.valor_pago.valueChanged.connect(lambda: self.calcula_saldo(self.valor_a_pagar.value(),
                                                                        self.valor_pago.value()))
        self.saldo = price()
        self.saldo.setVisible(False)
        self.obs = QPlainTextEdit()

        grid = QFormLayout()

        grid.addRow(QLabel("Fornecedor"), self.fornecedor)
        grid.addRow(QLabel("Nº do Documento"), self.documento)
        grid.addRow(QLabel("Data do Documento"), self.data)
        grid.addRow(QLabel("IVA do Documento"), self.iva)
        grid.addRow(QLabel("Valor do Documento"), self.valor_a_pagar)
        # grid.addRow(QLabel("Valor pago ao Fornecedor"), self.valor_pago)
        # grid.addRow(QLabel("Saldo do Fornecedor"), self.saldo)
        grid.addRow(QLabel("Observações"), self.obs)

        vLay = QVBoxLayout(self)
        vLay.setContentsMargins(0, 0, 0, 0)

        cLay = QVBoxLayout()
        cLay.setContentsMargins(10, 10, 10, 10)

        cLay.addLayout(grid)

        vLay.addWidget(titulo)
        vLay.addLayout(cLay)
        vLay.addWidget(self.tool)
        self.setLayout(vLay)

        self.setWindowTitle("Cadastro de Conta Corrente de Fornecedores")

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

    def enche_fornecedores(self):
        from utilities import enche_combobox
        dados = enche_combobox(self.cur, "fornecedores", "nome")

        if len(dados) > 0:
            self.fornecedor.addItems(dados)
            return True

        return False

    def enche_usuarios(self):
        sql = "SELECT cod FROM USERS"
        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        self.usuario.clear()

        if len(data) > 0:
            for x in data:
                self.usuario.addItem(x[0])
            return True

        return False

    def accoes(self):
        self.tool = QToolBar()
        self.tool.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.tool.setContextMenuPolicy(Qt.PreventContextMenu)

        gravar = QAction(QIcon("./images/ok.png"), "Gravar\nDados", self)
        eliminar = QAction(QIcon("./icons/new.ico"), "Limpar\nCampos", self)

        fechar = QAction(QIcon("./images/filequit.png"), "&Fechar", self)

        self.tool.addAction(gravar)
        self.tool.addAction(eliminar)

        self.tool.addSeparator()
        self.tool.addAction(fechar)

        gravar.triggered.connect(self.add_record)
        fechar.triggered.connect(self.fechar)

    def closeEvent(self, evt):
        parent = self.parent()
        try:
            if parent is not None:
                parent.fill_table()
                parent.enchecc_fornecedores()
        except Exception as e:
            return

    def fechar(self):
        self.close()

    def validacao(self):

        if self.valor_a_pagar.value() == 0:
            QMessageBox.warning(self, "Erro", "Valor a pagar Inválido")
            self.valor_a_pagar.setFocus()
            return False
        elif self.documento.text() == "":
            QMessageBox.warning(self, "Erro", "Entre o documento (Ex: Factura 1150/2020)")
            self.documento.setFocus()
            return False
        else:
            return True

    def mostrar_registo(self, codigo):

        sql = """SELECT * FROM cc_fornecedores WHERE cod={} """.format(codigo)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for x in data:
                self.fornecedor.setCurrentText(x[1])
                self.documento.setText(x[2])
                self.data.setDate(x[3])
                self.iva.setValue(x[4])
                self.valor_a_pagar.setValue(x[5])
                self.valor_pago.setValue(x[6])
                self.saldo.setValue(x[7])
                self.obs.setPlainText(x[9])

    def existe(self, codigo):

        sql = """SELECT cod from cc_fornecedores WHERE cod = "{codigo}" """.format(codigo=str(codigo))

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            self.cod_cc_fornecedor = codigo
            return False
        else:
            codigo = int(data[0][0])
            self.cod_cc_fornecedor = codigo
            return True

    def add_record(self):

        if self.validacao() is False:
            return False

        if self.parent() is not None:
            created_by = self.parent().user
            modified_by = self.parent().user
        else:
            created_by = "User"
            modified_by = "User"

        created = DATA_HORA_FORMATADA
        modified = DATA_HORA_FORMATADA

        cod = self.cod_cc_fornecedor
        fornecedor = self.fornecedor.currentText()
        documento = self.documento.text()
        data = QDate(self.data.date()).toString("yyyy-MM-dd")
        iva = self.iva.value()
        valor_a_pagar = self.valor_a_pagar.value()
        valor_pago = self.valor_pago.value()
        saldo = self.saldo.value()
        estado = 1
        obs = self.obs.toPlainText()

        if self.existe(cod) is True:

            sql = """UPDATE cc_fornecedores set fornecedor="{fornecedor}", documento="{documento}", data="{data}", iva={iva},
                        valor_a_pagar={valor_a_pagar}, valor_pago={valor_pago}, saldo={saldo}, estado={estado}, 
                        modified="{modified}", modified_by="{modified_by}", obs="{obs}" WHERE cod="{cod}" 
                        """.format(cod=cod, fornecedor=fornecedor, documento=documento, data=data, iva=iva,
                                   valor_a_pagar=valor_a_pagar, valor_pago=valor_pago, saldo=saldo,
                                   estado=estado, modified=modified, modified_by=modified_by,
                                   obs=obs)

        else:
            values = """ "{fornecedor}", "{documento}", "{data}", "{iva}", {valor_a_pagar}, {valor_pago}, {saldo}, 
                                                {estado}, "{obs}", "{created}", "{modified}", "{modified_by}", 
                                                "{created_by}" 
                                                            """.format(fornecedor=fornecedor, documento=documento, data=data,
                                                                       iva=iva,
                                                                       valor_a_pagar=valor_a_pagar,
                                                                       valor_pago=valor_pago,
                                                                       saldo=saldo,
                                                                       estado=estado, created=created,
                                                                       created_by=created_by,
                                                                       modified=modified, modified_by=modified_by,
                                                                       obs=obs)

            sql = """INSERT INTO cc_fornecedores (fornecedor, documento, data, iva, valor_a_pagar, valor_pago, saldo, estado, 
            obs, created, modified, modified_by, created_by) values({value})""".format(value=values)

        print(sql)

        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            QMessageBox.critical(self, "Erro", "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
            return

        if QMessageBox.question(self, "Pergunta", "Registo Gravado com sucesso!\nDeseja Cadastrar outro Item?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            pass
        else:
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


if __name__ == '__main__':
    app = QApplication(sys.argv)

    helloPythonWidget = CC_Fornecedor()
    helloPythonWidget.show()

    sys.exit(app.exec_())