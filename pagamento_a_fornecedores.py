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
from utilities import enche_combobox
from utilities import enche_combobox_com_clausula

DB_FILENAME = "dados.tsdb"
DATA_HORA_FORMATADA = strftime("%Y-%m-%d %H:%M:%S", localtime())
DATA_ACTUAL = datetime.date.today()
ANO_ACTUAL = DATA_ACTUAL.year
DIA = DATA_ACTUAL.day
MES = DATA_ACTUAL.month


class Pagamento_a_Fornecedor(QDialog):
    cod_pagamento_a_fornecedor = 0
    cod_documento = 0
    cod_cc_fornecedor = 0

    valor_aterior = 0

    def __init__(self, parent=None):
        super(Pagamento_a_Fornecedor, self).__init__(parent)

        if self.parent() is None:
            self.db = self.connect_db()
        else:
            self.cur = self.parent().cur
            self.conn = self.parent().conn

        self.accoes()
        self.ui()

        self.enche_fornecedores()

    def calcula_saldo(self, valor_1, valor_2):
        print("A Calcular Saldo.....", "Valor a Pagar: ", valor_1, "Valor Pago: ", valor_2, valor_1 < valor_2)
        if valor_1 < valor_2:
            self.valor_pago.setValue(valor_1)

        saldo = valor_1 - valor_2
        self.saldo_actual.setValue(saldo)

        return saldo

    def ui(self):
        html = """<center style= "background-image: './images/control.png'" > <h2 > Pagamento de Fornecedors </h2> </center> """

        titulo = QLabel(html)

        self.fornecedor = QComboBox()
        self.fornecedor.currentIndexChanged.connect(lambda: self.enche_documentos(self.fornecedor.currentText()))
        self.documento = QComboBox()
        self.documento.currentIndexChanged.connect(lambda: self.get_valor_documento(self.documento.currentText()))
        calendario = QCalendarWidget()
        self.data = QDateEdit()
        self.data.setCalendarPopup(True)
        self.data.setCalendarWidget(calendario)
        self.data.setDate(QDate.currentDate())
        self.saldo_anterior = price()
        self.saldo_anterior.setEnabled(False)
        self.valor_pago = price()
        self.valor_pago.valueChanged.connect(lambda: self.calcula_saldo(self.saldo_anterior.value(),
                                                                        self.valor_pago.value()))

        self.saldo_actual = price()
        self.saldo_actual.setEnabled(False)
        self.obs = QPlainTextEdit()

        grid = QFormLayout()

        grid.addRow(QLabel("Fornecedor"), self.fornecedor)
        grid.addRow(QLabel("Nº do Documento"), self.documento)
        grid.addRow(QLabel("Data de Pagamento"), self.data)
        grid.addRow(QLabel("Saldo Anterior"), self.saldo_anterior)
        grid.addRow(QLabel("Valor a Receber"), self.valor_pago)
        grid.addRow(QLabel("Saldo Actual"), self.saldo_actual)
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

        self.setWindowTitle("Cadastro de Pagamento de Fornecedors")

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

    def get_codcc(self, nome_fornecedor, documento):
        sql = """SELECT cod from cc_fornecedores WHERE fornecedor="{}" and documento="{}" """.format(nome_fornecedor, documento)
        self.cur.execute(sql)
        dados = self.cur.fetchall()

        if len(dados) > 0:
            self.cod_cc_fornecedor = dados[0][0]

        return self.cod_cc_fornecedor

    def enche_fornecedores(self):
        dados = enche_combobox(self.cur, "fornecedores", "nome")

        self.fornecedor.clear()

        if len(dados) > 0:
            self.fornecedor.addItems(dados)
            return True

        return False

    def enche_documentos(self, nome_documento):
        dados = enche_combobox_com_clausula(self.cur, "cc_fornecedores", "documento", """fornecedor="{}" 
        """.format(nome_documento))

        self.documento.clear()

        if len(dados) > 0:
            self.documento.addItems(dados)
            return True

        return False

    def get_valor_documento(self, documento):
        dados = enche_combobox_com_clausula(self.cur, "cc_fornecedores", "saldo", """documento="{}" """.format(documento))

        print(dados)

        if len(dados) > 0:
            self.saldo_anterior.setValue(dados[0])
            return True
        else:
            self.saldo_anterior.setValue(0)
            return False

    def accoes(self):
        self.tool = QToolBar()
        self.tool.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

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
                parent.enchepagamento_a_fornecedores()
        except Exception as e:
            return

    def fechar(self):
        self.close()

    def validacao(self):

        if self.valor_pago.value() == 0:
            QMessageBox.warning(self, "Erro", "Valor a pagar Inválido")
            self.valor_pago.setFocus()
            return False
        elif self.fornecedor.currentText() == "" or self.documento.currentText() == "":
            QMessageBox.warning(self, "Erro", "Documento não existe")
            self.valor_pago.setFocus()
            return False
        else:
            return True

    def mostrar_registo(self, codigo):

        sql = """select c.fornecedor, c.documento, p.saldo_anterior, p.valor_pago, p.saldo_actual, p.obs 
        FROM pagamento_a_fornecedores p INNER JOIN cc_fornecedores c ON c.cod=p.codcc WHERE p.cod={} """.format(codigo)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for x in data:
                self.fornecedor.setCurrentText(x[0])
                self.documento.setCurrentText(x[1])
                self.saldo_anterior.setValue(x[2])
                self.valor_pago.setValue(x[3])
                self.saldo_actual.setValue(x[4])
                self.obs.setPlainText(x[5])

    def existe(self, codigo):

        sql = """SELECT cod from pagamento_a_fornecedores WHERE cod = "{codigo}" """.format(codigo=str(codigo))

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            self.cod_pagamento_a_fornecedor = codigo
            return False
        else:
            codigo = int(data[0][0])
            self.cod_pagamento_a_fornecedor = codigo
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

        cod = self.cod_pagamento_a_fornecedor
        codcc = self.get_codcc(self.fornecedor.currentText(), self.documento.currentText())
        saldo_anterior = self.saldo_anterior.value()
        valor_pago = self.valor_pago.value()
        saldo_actual = self.saldo_actual.value()
        data = QDate(self.data.date()).toString("yyyy-MM-dd")
        estado = 1
        obs = self.obs.toPlainText()

        if self.existe(cod) is True:

            sql = """UPDATE pagamento_a_fornecedores set codcc="{codcc}", data="{data}", saldo_anterior={saldo_anterior},
                                   valor_pago={valor_pago}, saldo_actual={saldo_actual}, estado={estado}, 
                                   modified="{modified}", modified_by="{modified_by}", obs="{obs}" WHERE cod="{cod}" 
                                   """.format(cod=cod, codcc=codcc, data=data, saldo_anterior=saldo_anterior,
                                              valor_pago=valor_pago, saldo_actual=saldo_actual,
                                              estado=estado, modified=modified, modified_by=modified_by,
                                              obs=obs)

        else:
            values = """ "{codcc}", "{data}", "{saldo_anterior}", {valor_pago}, {saldo_actual},  
                                                            {estado}, "{obs}", "{created}", "{modified}", 
                                                            "{modified_by}", 
                                                            "{created_by}" 
                                                                        """.format(cod=cod, codcc=codcc, data=data,
                                                                                   saldo_anterior=saldo_anterior,
                                                                                   valor_pago=valor_pago,
                                                                                   saldo_actual=saldo_actual,
                                                                                   estado=estado, created=created,
                                                                                   created_by=created_by,
                                                                                   modified=modified,
                                                                                   modified_by=modified_by,
                                                                                   obs=obs)

            sql = """INSERT INTO pagamento_a_fornecedores (codcc, data, saldo_anterior, valor_pago, saldo_actual, estado, 
            obs, created, modified, modified_by, created_by) values({value})""".format(value=values)

        sql_cc_fornecedores = """UPDATE cc_fornecedores set saldo={}, valor_pago={}+valor_pago WHERE cod={} """.format(
            saldo_actual,
            valor_pago,
            self.cod_cc_fornecedor)

        print(sql_cc_fornecedores)
        print(sql)

        try:
            self.cur.execute(sql_cc_fornecedores)
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

    helloPythonWidget = Pagamento_a_Fornecedor()
    helloPythonWidget.show()

    sys.exit(app.exec_())