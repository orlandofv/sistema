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


class Cheque(QDialog):
    cod_cheque = 0
    cod_documento = 0
    cod_cliente = 0

    valor_aterior = 0

    def __init__(self, parent=None):
        super(Cheque, self).__init__(parent)

        if self.parent() is None:
            self.db = self.connect_db()
        else:
            self.cur = self.parent().cur
            self.conn = self.parent().conn

        self.accoes()
        self.ui()

        self.enche_clientes()

    def ui(self):
        html = """<center style= "background-image: './images/control.png'" > <h2 > Gestão de Cheques </h2> </center> """

        titulo = QLabel(html)

        self.cliente = QComboBox()
        self.cliente.currentIndexChanged.connect(lambda: self.get_codcliente(self.cliente.currentText()))
        self.cheque = QLineEdit()
        self.banco = QLineEdit()
        self.valor_cheque = price()
        calendario = QCalendarWidget()
        calendario1 = QCalendarWidget()
        self.data_entrada = QDateEdit()
        self.data_entrada.setCalendarPopup(True)
        self.data_entrada.setCalendarWidget(calendario)
        self.data_entrada.setDate(QDate.currentDate())
        self.data_vencimento = QDateEdit()
        self.data_vencimento.setCalendarPopup(True)
        self.data_vencimento.setCalendarWidget(calendario1)
        self.data_vencimento.setDate(QDate.currentDate())
        self.obs = QPlainTextEdit()

        grid = QFormLayout()

        grid.addRow(QLabel("Cliente"), self.cliente)
        grid.addRow(QLabel("Nº do Cheque"), self.cheque)
        grid.addRow(QLabel("Banco"), self.banco)
        grid.addRow(QLabel("Montante do Cheque"), self.valor_cheque)
        grid.addRow(QLabel("Data de Entrada"), self.data_entrada)
        grid.addRow(QLabel("Data de Vencimento"), self.data_vencimento)
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

        self.setWindowTitle("Cadastro de Gestão de Cheques")

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

    def enche_clientes(self):
        dados = enche_combobox(self.cur, "clientes", "nome")

        self.cliente.clear()

        if len(dados) > 0:
            self.cliente.addItems(dados)
            return True

        return False

    def get_codcliente(self, nome_cliente):
        dados = enche_combobox_com_clausula(self.cur, "clientes", "cod", """nome="{}" """.format(nome_cliente))

        print("cliente: ", dados)

        if len(dados) > 0:
            self.cod_cliente = dados[0]

        return self.cod_cliente

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
                parent.enchecheques()
        except Exception as e:
            return

    def fechar(self):
        self.close()

    def validacao(self):

        if self.valor_cheque.value() == 0:
            QMessageBox.warning(self, "Erro", "Valor a pagar Inválido")
            self.valor_cheque.setFocus()
            return False
        elif self.cheque.text() == "":
            QMessageBox.warning(self, "Erro", "Entre o número do cheque")
            self.cheque.setFocus()
            return False
        elif self.banco.text() == "":
            QMessageBox.warning(self, "Erro", "Entre o nome do Banco")
            self.banco.setFocus()
            return False
        else:
            return True

    def mostrar_registo(self, codigo):

        sql = """select c.nome, p.cheque_numero, p.banco, p.valor, p.data_entrada, p.data_vencimento, p.obs 
        FROM cheques p INNER JOIN clientes c ON c.cod=p.cod_cliente WHERE p.cod={}""".format(codigo)

        print(sql)

        self.cur.execute(sql)
        data_entrada = self.cur.fetchall()

        if len(data_entrada) > 0:
            for x in data_entrada:
                self.cliente.setCurrentText(x[0])
                self.cheque.setText(x[1])
                self.banco.setText(x[2])
                self.valor_cheque.setValue(x[3])
                self.data_entrada.setDate(x[4])
                self.data_vencimento.setDate(x[5])
                self.obs.setPlainText(x[6])

    def existe(self, codigo):

        sql = """SELECT cod from cheques WHERE cod = "{codigo}" """.format(codigo=str(codigo))

        self.cur.execute(sql)
        data_entrada = self.cur.fetchall()

        if len(data_entrada) == 0:
            self.cod_cheque = codigo
            return False
        else:
            codigo = int(data_entrada[0][0])
            self.cod_cheque = codigo
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

        cod = self.cod_cheque
        cod_cliente = self.cod_cliente
        cheque_numero =self.cheque.text()
        banco = self.banco.text()
        valor = self.valor_cheque.value()
        data_entrada = QDate(self.data_entrada.date()).toString("yyyy-MM-dd")
        data_vencimento = QDate(self.data_vencimento.date()).toString("yyyy-MM-dd")
        estado = 1
        obs = self.obs.toPlainText()
        "cheque_numero, banco, valor, data_entrada, data_vencimento"

        if self.existe(cod) is True:

            sql = """UPDATE cheques set cod_cliente="{cod_cliente}", cheque_numero="{cheque_numero}", banco="{banco}", 
            valor={valor}, data_entrada="{data_entrada}", data_vencimento="{data_vencimento}", estado={estado}, 
            modified="{modified}", modified_by="{modified_by}", obs="{obs}" WHERE cod="{cod}" 
            """.format(cod=cod, cod_cliente=cod_cliente,
                       cheque_numero=cheque_numero,
                       banco=banco, valor=valor,
                       data_entrada=data_entrada,
                       data_vencimento=data_vencimento,
                       estado=estado, modified=modified,
                       modified_by=modified_by,
                       obs=obs)

        else:
            values = """ "{cod_cliente}", "{cheque_numero}", "{banco}", "{valor}", "{data_entrada}", 
            "{data_vencimento}", {estado}, "{obs}", "{created}", "{modified}", "{modified_by}", "{created_by}" 
                                                                        """.format(cod=cod, cod_cliente=cod_cliente,
                                                                                   cheque_numero=cheque_numero,
                                                                                   banco=banco, valor=valor,
                                                                                   data_entrada=data_entrada,
                                                                                   data_vencimento=data_vencimento,
                                                                                   estado=estado, created=created,
                                                                                   created_by=created_by,
                                                                                   modified=modified,
                                                                                   modified_by=modified_by,
                                                                                   obs=obs)

            sql = """INSERT INTO cheques (cod_cliente, cheque_numero, banco, valor, data_entrada, data_vencimento, 
            estado, obs, created, modified, modified_by, created_by) values({value})""".format(value=values)

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
        # Connect to database and retrieves data_entrada
        try:
            self.conn = lite.connect(DB_FILENAME)
            self.cur = self.conn.cursor()

        except Exception as e:
            QMessageBox.critical(self, "Erro ao conectar a Base de Dados",
                                 "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
            sys.exit(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    helloPythonWidget = Cheque()
    helloPythonWidget.show()

    sys.exit(app.exec_())