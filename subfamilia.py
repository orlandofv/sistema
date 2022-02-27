# -*- coding: utf-8 -*-
"""
Created on Fri Mar 02 23:18:43 2012

@author: lims
"""

from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QFormLayout, QVBoxLayout, QToolBar, QMessageBox, \
    QTextEdit, QAction, QApplication, QComboBox, QCheckBox, QPushButton, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon
import sys

from utilities import codigo as cd


import sqlite3 as lite

DB_FILENAME = "dados.tsdb"


class Cliente(QDialog):
    def __init__(self, parent=None):
        super(Cliente, self).__init__(parent)

        # retrieves cod from selected subfamilia nome
        self.familiacod = ""

        self.accoes()
        self.ui()

        if self.parent() is None:
            self.db = self.connect_db()
        else:
            self.cur = self.parent().cur
            self.conn = self.parent().conn
            self.user = self.parent().user

        # verifica a existencia dos dados na base de dados
        self.existe(self.cod.text())

        # Mostraregisto caso exista
        self.mostrar_registo()
        self.enchefamilia()

    def enchefamilia(self):
        self.familia_combobox.clear()

        sql = "SELECT nome FROM familia"
        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        for item in data:
            self.familia_combobox.addItems(item)

    def ui(self):
        html = """<center style= "background-image: './images/control.png'" > <h2 > Cadastro de Subfamílias </h2> </center> """

        titulo = QLabel(html)

        cod = QLabel("Código da Família")
        nome = QLabel("Nome da Subfamília")
        familia = QLabel("Escolha a Família")
        obs = QLabel("Observações")

        self.cod = QLineEdit()
        self.cod.setEnabled(False)
        self.nome = QLineEdit()
        
        self.familia_combobox = QComboBox()
        self.familia_combobox.currentTextChanged.connect(self.codfamilia)
        familia_btn = QPushButton('+')
        familia_btn.setMaximumWidth(40)
        familia_btn.clicked.connect(self.adicionar_familia)
        
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self.familia_combobox)
        hbox.addWidget(familia_btn)
        familia_widget = QWidget()
        familia_widget.setLayout(hbox)
        self.obs = QTextEdit()
        self.estado = QCheckBox("Activo")
        self.estado.setChecked(True)

        grid = QFormLayout()

        grid.addRow(cod, self.cod)
        grid.addRow(nome, self.nome)
        grid.addRow(familia, familia_widget)
        grid.addWidget(self.estado)
        grid.addRow(obs, self.obs)

        vLay = QVBoxLayout(self)
        vLay.setContentsMargins(0, 0, 0, 0)

        cLay = QVBoxLayout()
        cLay.setContentsMargins(10, 10, 10, 10)

        cLay.addLayout(grid)

        vLay.addWidget(titulo)
        vLay.addLayout(cLay)
        vLay.addWidget(self.tool)
        self.setLayout(vLay)

        self.setWindowTitle("Cadastro de Famílias")

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

    def adicionar_familia(self):
        from familia import Cliente

        f = Cliente(self)
        f.setModal(True)
        f.show()

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
        eliminar.triggered.connect(self.limpar)
        fechar.triggered.connect(self.fechar)


    # ==============================================================================

    def codfamilia(self):
        sql = """select cod from familia WHERE nome= "{nome}" """.format(nome=self.familia_combobox.currentText())

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]
        if len(data) > 0:
            self.familiacod = "".join(data[0])

    def closeEvent(self, evt):
        parent = self.parent()
        if hasattr(parent, 'enchesubfamilia'):
            parent.enchesubfamilia()
        elif hasattr(parent, 'fill_table'):
            parent.fill_table()

    def fechar(self):
        self.close()

    def limpar(self):
        for child in (self.findChildren(QLineEdit) or self.findChildren(QTextEdit)):
            if child.objectName() not in ["cod", "cal1", "cal2"]: child.clear()

        # gera novo codigo para subfamilia
        self.cod.setText("SF" + cd("SF" + "abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789"))

    def validacao(self):

        if str(self.nome.text()) == "":
            QMessageBox.information(self, "Erro", "Nome do Cliente inválido")
            self.nome.setFocus()
            return False
        else:
            return True

    def mostrar_registo(self):

        sql = """SELECT subfamilia.cod, subfamilia.nome, familia.nome, subfamilia.obs, subfamilia.estado from familia INNER JOIN
         subfamilia ON familia.cod=subfamilia.codfamilia WHERE subfamilia.cod = "{codigo}" """.format(codigo=str(self.cod.text()))
        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        if len(data) == 0:
            self.cod.setText("SF" + cd("abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789"))
        else:
            self.nome.setText(''.join(data[0][1]))
            self.familia_combobox.setCurrentText(''.join(data[0][2]))
            self.obs.setPlainText(''.join(data[0][3]))

            if int(data[0][4]) == 1:
                self.estado.setChecked(True)
            else:
                self.estado.setChecked(False)

    def existe(self, codigo):

        sql = """SELECT cod from subfamilia WHERE cod = "{codigo}" """.format(codigo=str(self.cod.text()))

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        if len(data) == 0:
            codigo = self.cod.text()
            self.codigo = codigo
            return False
        else:
            codigo = ''.join(data[0])
            self.codigo = codigo
            return True

    def add_record(self):

        if self.validacao() is True:
            code = self.cod.text()
            nome = self.nome.text()
            obs = self.obs.toPlainText()
            estado = 1
            if self.estado.isChecked() is False:
                estado = 0

            created = QDate.currentDate().toString('yyyy-MM-dd')
            modified = QDate.currentDate().toString('yyyy-MM-dd')
            if self.parent() is not None:
                modified_by = self.parent().user
            else:
                modified_by = "User"
            if self.parent() is not None:
                created_by = self.parent().user
            else:
                created_by = "User"
            if self.existe(code) is True:

                sql = """UPDATE subfamilia set nome="{nome}", codfamilia="{codfamilia}", obs="{obs}", 
                modified="{modified}", estado="{estado}",
                modified_by="{modified_by}" WHERE cod="{cod}" """.format(cod=code, nome=nome,
                                                                         codfamilia=self.familiacod,
                                                                         obs=obs, modified=modified, estado=estado,
                                                                         modified_by=modified_by)
                try:
                    self.cur.execute(sql)
                    self.conn.commit()
                except Exception as e:
                    QMessageBox.critical(self, "Erro", "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
                    return
            else:
                values = """ "{cod}", "{nome}", "{codfamilia}", "{obs}", "{estado}", "{created}", "{modified}",
                 "{modified_by}","{created_by}" """.format(cod=code, nome=nome, codfamilia=self.familiacod, obs=obs,
                                                           estado=estado, created=created, modified=modified,
                                                           modified_by=modified_by, created_by=created_by)
                try:
                    sql = "INSERT INTO subfamilia (cod, nome, codfamilia, obs, estado, created, modified, modified_by, " \
                          "created_by) values({value})".format(value=values)



                    self.cur.execute(sql)
                    self.conn.commit()
                except Exception as e:
                    QMessageBox.critical(self, "Erro", "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
                    return

            if QMessageBox.question(self, "Pergunta", "Registo Gravado com sucesso!\nDeseja Cadastrar outro Item?",
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                self.limpar()
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

    helloPythonWidget = Cliente()
    helloPythonWidget.show()

    sys.exit(app.exec_())