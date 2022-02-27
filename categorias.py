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


class Categoria(QDialog):

    cod_categoria = 0

    def __init__(self, parent=None):
        super(Categoria, self).__init__(parent)

        self.accoes()
        self.ui()

        if self.parent() is None:
            self.db = self.connect_db()
        else:
            self.cur = self.parent().cur
            self.conn = self.parent().conn

        # verifica a existencia dos dados na base de dados
        # self.existe(self.cod.text())

        # Mostraregisto caso exista
        # self.mostrar_registo()

    def ui(self):
        html = """<center style= "background-image: './images/control.png'" > <h2 > Cadastro de Categorias </h2> </center> """

        titulo = QLabel(html)

        self.preco = price()
        self.nome_categoria = QLineEdit()
        self.obs = QPlainTextEdit()

        grid = QFormLayout()

        grid.addRow(QLabel("Gategoria"), self.nome_categoria)
        grid.addRow(QLabel("Preço"), self.preco)
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

        self.setWindowTitle("Cadastro de Categorias")

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
                parent.enchecategorias()
        except Exception as e:
            return

    def fechar(self):
        self.close()


    def validacao(self):

        if str(self.nome.text()) == "":
            QMessageBox.information(self, "Erro", "Nome do Categoria inválido")
            self.nome.setFocus()
            return False
        else:
            return True

    def mostrar_registo(self, cod):

        sql = """SELECT cod, valor, categoria, obs FROM categorias WHERE cod={} """.format(cod)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data)>0:
            self.preco.setValue(data[0][1])
            self.nome_categoria.setText(data[0][2])
            self.obs.setPlainText(data[0][3])

    def existe(self, codigo):

        sql = """SELECT cod from categorias WHERE cod = "{codigo}" """.format(codigo=str(codigo))

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            self.cod_categoria = 0
            return False
        else:
            self.cod_categoria = data[0][0]
            return True

    def add_record(self):

        if self.parent() is not None:
            created_by = self.parent().user
            modified_by = self.parent().user
        else:
            created_by = "User"
            modified_by = "User"

        created = DATA_HORA_FORMATADA
        modified = DATA_HORA_FORMATADA
        code = self.cod_categoria
        preco = self.preco.value()
        obs = self.obs.toPlainText()
        categoria = self.nome_categoria.text()

        if self.existe(code) is True:

            sql = """UPDATE categorias set categoria="{categoria}", valor="{preco}", modified="{modified}", modified_by="{modified_by}", obs="{obs}" WHERE cod="{cod}"
            """.format(cod=code, preco=preco, modified=modified, categoria=categoria, modified_by=modified_by, obs=obs
                       )

        else:
            values = """ "{valor}", "{categoria}", "{obs}", "{created}", "{modified}", "{modified_by}", "{created_by}" 
            """.format(valor=preco, categoria=categoria, obs=obs, created=created, modified=modified,
                       modified_by=modified_by, created_by=created_by)

            sql = """INSERT INTO categorias (valor, categoria, obs, 
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

    helloPythonWidget = Categoria()
    helloPythonWidget.show()

    sys.exit(app.exec_())