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


class Quarto(QDialog):
    cod_quarto = ""

    def __init__(self, parent=None):
        super(Quarto, self).__init__(parent)

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

        self.enche_quartos()
        self.get_preco()

        self.cod_preco.currentIndexChanged.connect(self.get_preco)


    def ui(self):
        html = """<center style= "background-image: './images/control.png'" > <h2 > Cadastro de Quartos </h2> </center> """

        titulo = QLabel(html)

        self.cod = QSpinBox()
        self.cod.setRange(1, 5000)
        self.cod.setObjectName("cod")
        self.cod.setAlignment(Qt.AlignRight)
        self.cod_preco = QComboBox()
        self.preco = price()
        self.nome = QLineEdit()
        self.obs = QPlainTextEdit()

        grid = QFormLayout()

        grid.addRow(QLabel("Número do Quarto"), self.cod)
        grid.addRow(QLabel("Gategoria"), self.cod_preco)
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

        self.setWindowTitle("Cadastro de Quartos")

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

    def enche_quartos(self):
        sql = """SELECT categoria, valor, cod from categorias"""
        self.cur.execute(sql)
        data = self.cur.fetchall()

        print("Enchedo quartos...")

        if len(data) > 0:
            for item in data:
                self.cod_preco.addItem(str(item[1]) + "-" + str(item[0]))
                LISTADE_PRECOS.append(item[1])
                LISTADE_CODIGOS.append(item[2])

    def get_preco(self):

        print("Pegando o preços...")
        try:
            self.preco.setValue(float(LISTADE_PRECOS[self.cod_preco.currentIndex()]))
            self.cod_quarto = LISTADE_CODIGOS[self.cod_preco.currentIndex()]

        except Exception as e:
            print(e)

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
                parent.enchequartos()
        except Exception as e:
            return

    def fechar(self):
        self.close()


    def validacao(self):

        if str(self.nome.text()) == "":
            QMessageBox.information(self, "Erro", "Nome do Quarto inválido")
            self.nome.setFocus()
            return False
        else:
            return True

    def mostrar_registo(self):

        pass

    def existe(self, codigo):

        sql = """SELECT cod from quartos WHERE cod = "{codigo}" """.format(codigo=str(codigo))

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            codigo = self.cod.text()
            self.codigo = codigo
            return False
        else:
            codigo = int(data[0][0])
            self.codigo = codigo
            return True

    def add_record(self):

        self.codcliente = self.cod.text()

        if self.parent() is not None:
            created_by = self.parent().user
            modified_by = self.parent().user
        else:
            created_by = "User"
            modified_by = "User"

        created = DATA_HORA_FORMATADA
        modified = DATA_HORA_FORMATADA

        code = self.codcliente
        ocupado = 0
        cod_preco = self.cod_quarto
        preco = self.preco.value()
        estado = 1
        obs = self.obs.toPlainText()

        if self.existe(code) is True:

            sql = """UPDATE quartos set cod="{cod}", cod_preco="{cod_preco}", preco={preco},
            estado={estado}, modified="{modified}", modified_by="{modified_by}", obs="{obs}" WHERE cod="{cod}"
            """.format(cod=code, cod_preco=cod_preco, preco=preco, estado=estado, modified=modified,
                       modified_by=modified_by, obs=obs
                       )

        else:
            values = """ "{cod}", "{cod_preco}", "{preco}", {ocupado}, {estado}, "{obs}", "{created}", "{modified}", 
            "{modified_by}", "{created_by}" """.format(cod=code, cod_preco=cod_preco, preco=preco, estado=estado,
                                                       ocupado=ocupado, modified=modified, modified_by=modified_by,
                                                       obs=obs, created=created, created_by=created_by)

            sql = """INSERT INTO quartos (cod, cod_preco, preco, ocupado, estado, obs, 
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

    helloPythonWidget = Quarto()
    helloPythonWidget.show()

    sys.exit(app.exec_())