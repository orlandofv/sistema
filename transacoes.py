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
LISTA_DE_TRANSACOES = {1: "Depósito", 2: "Levantamento", 3: "Transferência", 4: "Envio de Dinheiro"}
LISTA_DE_CONTAS = []


class Transacao(QDialog):
    cod_transacao = 0
    cod_conta = 0

    def __init__(self, parent=None):
        super(Transacao, self).__init__(parent)

        if self.parent() is None:
            self.db = self.connect_db()
        else:
            self.cur = self.parent().cur
            self.conn = self.parent().conn

        self.accoes()
        self.ui()

        self.enche_contas()
        self.enche_usuarios()

    def ui(self):
        html = """<center style= "background-image: './images/control.png'" > <h2 > Cadastro de Transações </h2> </center> """

        titulo = QLabel(html)

        self.tipo_transacao = QComboBox()
        self.tipo_transacao.addItems(LISTA_DE_TRANSACOES.values())
        self.conta = QComboBox()
        self.conta.currentIndexChanged.connect(lambda: self.get_codconta(self.conta.currentIndex()))
        calendario = QCalendarWidget()
        self.data = QDateEdit()
        self.data.setCalendarPopup(True)
        self.data.setCalendarWidget(calendario)
        self.data.setDate(QDate.currentDate())
        self.valor = price()
        self.usuario = QComboBox()
        self.obs = QPlainTextEdit()

        grid = QFormLayout()

        grid.addRow(QLabel("Tipo de Transação"), self.tipo_transacao)
        grid.addRow(QLabel("Nº de Conta"), self.conta)
        grid.addRow(QLabel("Data da Transação"), self.data)
        grid.addRow(QLabel("Valor/Montante"), self.valor)
        grid.addRow(QLabel("Usuário"), self.usuario)
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

        self.setWindowTitle("Cadastro de Transações")

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

    def enche_contas(self):
        sql = """SELECT cod, nome_banco, conta from contas"""
        self.cur.execute(sql)
        data = self.cur.fetchall()

        self.conta.clear()
        LISTA_DE_CONTAS.clear()

        if len(data) > 0:
            for x in data:
                self.conta.addItem("{} - {}".format(x[1],x[2]))
                LISTA_DE_CONTAS.append(int(x[0]))

            return True

        return False

    def get_codconta(self, indice):
        try:
            self.cod_conta = LISTA_DE_CONTAS[indice]
        except Exception as e:
            print(e)

        print("Conta: ", self.cod_conta)
        return self.cod_conta

    def set_nomeconta(self, codconta):
        sql = """SELECT nome_banco, conta from contas WHERE cod={}""".format(codconta)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for x in data:
                conta = self.conta.setCurrentText("{} - {}".format(x[0], x[1]))
        else:
            conta = ""

        return conta

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
                parent.enchetransacoes()
        except Exception as e:
            return

    def fechar(self):
        self.close()

    def validacao(self):

        if self.valor.value() == 0:
            QMessageBox.information(self, "Erro", "Valor do Transação inválido")
            self.valor.setFocus()
            return False
        else:
            return True

    def mostrar_registo(self, codigo):

        sql = """SELECT * from transacoes WHERE cod={} """.format(codigo)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for x in data:
                self.tipo_transacao.setCurrentText(x[1])
                self.conta.setCurrentText(self.set_nomeconta(self.get_codconta(self.conta.currentIndex())))
                self.data.setDate(x[3])
                self.valor.setValue(x[4])
                self.usuario.setCurrentText(x[5])
                self.obs.setPlainText(x[7])

    def existe(self, codigo):

        sql = """SELECT cod from transacoes WHERE cod = "{codigo}" """.format(codigo=str(codigo))

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            self.cod_transacao = codigo
            return False
        else:
            codigo = int(data[0][0])
            self.cod_transacao = codigo
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

        cod = self.cod_transacao
        tipo_trasacao = self.tipo_transacao.currentText()

        if self.cod_conta == 0:
            self.get_codconta(self.conta.currentIndex())

        conta = self.cod_conta

        data = QDate(self.data.date()).toString("yyyy-MM-dd")
        valor = self.valor.value()
        usuario = self.usuario.currentText()
        estado = 1
        obs = self.obs.toPlainText()

        if self.existe(cod) is True:

            sql = """UPDATE transacoes set tipo_trasacao="{tipo_trasacao}", conta="{conta}", data="{data}", 
            valor="{valor}", usuario="{usuario}", estado={estado}, modified="{modified}", modified_by="{modified_by}", 
            obs="{obs}" WHERE cod="{cod}" """.format(cod=cod, tipo_trasacao=tipo_trasacao, conta=conta, data=data, valor=valor,
                                         usuario=usuario, estado=estado, modified=modified, modified_by=modified_by,
                                         obs=obs)

        else:
            values = """ "{tipo_trasacao}", "{conta}", "{data}", "{valor}", "{usuario}", {estado}, "{obs}", 
            "{created}", "{modified}", "{modified_by}", "{created_by}" 
            """.format(tipo_trasacao=tipo_trasacao, conta=conta, data=data, valor=valor, usuario=usuario,
                       estado=estado, modified=modified, modified_by=modified_by, obs=obs, created=created,
                       created_by=created_by)

            sql = """INSERT INTO transacoes (tipo_trasacao, conta, data, valor, usuario, estado, obs, 
            created, modified, modified_by, created_by) values({value})""".format(value=values)

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

    helloPythonWidget = Transacao()
    helloPythonWidget.show()

    sys.exit(app.exec_())