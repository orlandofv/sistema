# -*- coding: utf-8 -*-
"""
Created on Fri Mar 02 23:18:43 2012

@author: lims
"""
import datetime
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QSpinBox, QFormLayout, QVBoxLayout, QToolBar, QMessageBox,\
    QTextEdit, QAction, QApplication, QComboBox, QPlainTextEdit
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
LISTADE_PRECOS = []
LISTADE_CODIGOS = []


class Banco(QDialog):
    cod_banco = 0

    def __init__(self, parent=None):
        super(Banco, self).__init__(parent)

        self.accoes()
        self.ui()

        if self.parent() is None:
            self.db = self.connect_db()
        else:
            self.cur = self.parent().cur
            self.conn = self.parent().conn

    def ui(self):
        html = """<center style= "background-image: './images/control.png'" > <h2 > Cadastro de Contas </h2> </center> """

        titulo = QLabel(html)

        self.nome = QLineEdit()
        self.nome.setMaxLength(50)
        self.conta = QLineEdit()
        self.conta.setMaxLength(20)
        self.nib = QLineEdit()
        self.nib.setMaxLength(20)
        self.swift = QLineEdit()
        self.swift.setMaxLength(20)
        self.endereco_banco = QLineEdit()
        self.endereco_banco.setMaxLength(255)
        self.obs = QPlainTextEdit()

        grid = QFormLayout()

        grid.addRow(QLabel("Nome do Banco"), self.nome)
        grid.addRow(QLabel("Endereço"), self.endereco_banco)
        grid.addRow(QLabel("Nº da Conta"), self.conta)
        grid.addRow(QLabel("NIB"), self.nib)
        grid.addRow(QLabel("SWIFT"), self.swift)
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

        self.setWindowTitle("Cadastro de Bancos")

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
                parent.enchebancos()
        except Exception as e:
            return

    def fechar(self):
        self.close()


    def validacao(self):

        if str(self.endereco.text()) == "":
            QMessageBox.information(self, "Erro", "Nome do Banco inválido")
            self.endereco.setFocus()
            return False
        else:
            return True

    def mostrar_registo(self, codigo):

        sql = """SELECT * from Bancos WHERE cod={} """.format(codigo)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for x in data:
                self.nome.setText(x[1])
                self.conta.setText(x[2])
                self.nib.setText(x[3])
                self.swift.setText(x[4])
                self.endereco_banco.setText(x[5])
                self.obs.setPlainText(x[7])

    def existe(self, codigo):

        sql = """SELECT cod from bancos WHERE cod = "{codigo}" """.format(codigo=str(codigo))

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            self.cod_banco = codigo
            return False
        else:
            codigo = int(data[0][0])
            self.cod_banco = codigo
            return True

    def add_record(self):

        self.nomecliente = self.nome.text()

        if self.parent() is not None:
            created_by = self.parent().user
            modified_by = self.parent().user
        else:
            created_by = "User"
            modified_by = "User"

        created = DATA_HORA_FORMATADA
        modified = DATA_HORA_FORMATADA

        cod = self.cod_banco
        nome_banco = self.nome.text()
        conta = self.nib.text()
        nib = self.nib.text()
        swift = self.nib.text()
        endereco = self.endereco_banco.text()
        estado = 1
        obs = self.obs.toPlainText()

        if self.existe(cod) is True:

            sql = """UPDATE bancos set nome_banco="{nome_banco}", conta="{conta}", nib="{nib}", swift="{swift}",
            endereco="{endereco}", estado={estado}, modified="{modified}", modified_by="{modified_by}", obs="{obs}" 
            WHERE cod="{cod}" """.format(cod=cod, nome_banco=nome_banco, conta=conta, nib=nib, swift=swift,
                                         endereco=endereco, estado=estado, modified=modified, modified_by=modified_by,
                                         obs=obs)

        else:
            values = """ "{nome_banco}", "{conta}", "{nib}", "{swift}", "{endereco}", {estado}, "{obs}", 
            "{created}", "{modified}", "{modified_by}", "{created_by}" 
            """.format(nome_banco=nome_banco, conta=conta, nib=nib, swift=swift, endereco=endereco,
                       estado=estado, modified=modified, modified_by=modified_by, obs=obs, created=created,
                       created_by=created_by)

            sql = """INSERT INTO bancos (nome_banco, conta, nib, swift, endereco, estado, obs, 
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

    helloPythonWidget = Banco()
    helloPythonWidget.show()

    sys.exit(app.exec_())