# -*- coding: utf-8 -*-
"""
Created on Fri Mar 02 23:18:43 2012

@author: lims
"""

from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QFormLayout, QVBoxLayout, QToolBar, QMessageBox, \
    QTextEdit, QAction, QApplication, QCheckBox
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon
import sys

from utilities import codigo as cd


import sqlite3 as lite

DB_FILENAME = "dados.tsdb"


class Cliente(QDialog):
    def __init__(self, parent=None):
        super(Cliente, self).__init__(parent)

        self.accoes()
        self.ui()

        if self.parent() is None:
            self.db = self.connect_db()
        else:
            self.cur = self.parent().cur
            self.conn = self.parent().conn

        # verifica a existencia dos dados na base de dados
        self.existe(self.cod.text())

        # Mostraregisto caso exista
        self.mostrar_registo()

    def ui(self):
        html = """<center style= "background-image: './images/control.png'" > <h2 > Cadastro de Documentos </h2> </center> """

        titulo = QLabel(html)

        cod = QLabel("Código do Documento")
        nome = QLabel("Descrição")
        obs = QLabel("Observações")

        self.cod = QLineEdit()
        self.cod.setEnabled(False)
        self.nome = QLineEdit()
        self.stock = QCheckBox("Documento abate Stock")
        self.subtotal = QCheckBox("Documento inclui\exibe Subtotal")
        self.subtotal.setChecked(True)
        self.desconto = QCheckBox("Documento inclui\exibe Desconto")
        self.desconto.setChecked(True)
        self.taxa = QCheckBox("Documento inclui\exibe Taxa")
        self.taxa.setChecked(True)
        self.total = QCheckBox("Documento inclui\exibe Total")
        self.visivel = QCheckBox("Visível para todos usuários")
        self.estado = QCheckBox("Activo")
        self.estado.setChecked(True)
        self.total.setChecked(True)
        self.obs = QTextEdit()

        grid = QFormLayout()

        grid.addRow(cod, self.cod)
        grid.addRow(nome, self.nome)
        grid.addRow(self.stock)
        grid.addRow(self.subtotal)
        grid.addRow(self.desconto)
        grid.addRow(self.taxa)
        grid.addRow(self.total)
        grid.addRow(self.visivel)
        grid.addRow(self.estado)
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

        self.setWindowTitle("Cadastro de Documentos")

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
        eliminar.triggered.connect(self.limpar)
        fechar.triggered.connect(self.fechar)

    # ==============================================================================

    def closeEvent(self, evt):
        parent = self.parent()
        try:
            if parent is not None:
                parent.fill_table()
        except Exception as e:
            return

    def fechar(self):
        self.close()

    def limpar(self):
        for child in (self.findChildren(QLineEdit) or self.findChildren(QTextEdit)):
            if child.objectName() not in ["cod", "cal1", "cal2"]: child.clear()

        # gera novo codigo para documentos
        self.cod.setText("DC" + cd("abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789"))

    def validacao(self):

        if str(self.nome.text()) == "":
            QMessageBox.information(self, "Erro", "Entre nome da Documento")
            self.nome.setFocus()
            return False
        else:
            return True

    def mostrar_registo(self):

        sql = """SELECT * from documentos WHERE cod = "{codigo}" """.format(codigo=str(self.cod.text()))
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            self.cod.setText("DC" + cd("abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789"))
        else:
            self.nome.setText(''.join(data[0][1]))

            if data[0][2] == 1:
                self.subtotal.setChecked(True)
            else:
                self.subtotal.setChecked(False)

            if data[0][3] == 1:
                self.desconto.setChecked(True)
            else:
                self.desconto.setChecked(False)

            if data[0][4] == 1:
                self.taxa.setChecked(True)
            else:
                self.taxa.setChecked(False)

            if data[0][5] == 1:
                self.total.setChecked(True)
            else:
                self.total.setChecked(False)

            if data[0][11] == 1:
                self.stock.setChecked(True)
            else:
                self.stock.setChecked(False)

            if data[0][13] == 1:
                self.visivel.setChecked(True)
            else:
                self.visivel.setChecked(False)

            if data[0][12] == 1:
                self.estado.setChecked(True)
            else:
                self.estado.setChecked(False)

            self.obs.setPlainText(''.join(data[0][6]))

    def existe(self, codigo):

        sql = """SELECT cod from documentos WHERE cod = "{codigo}" """.format(codigo=codigo)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            return False
        else:
            return True

    def add_record(self):

        if self.validacao() is True:
            code = self.cod.text()
            nome = self.nome.text()
            obs = self.obs.toPlainText()
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

            if self.subtotal.isChecked() is True:
                subtotal = 1
            else:
                subtotal = 0

            if self.total.isChecked() is True:
                total = 1
            else:
                total = 0

            if self.taxa.isChecked() is True:
                taxa = 1
            else:
                taxa = 0

            if self.desconto.isChecked() is True:
                desconto = 1
            else:
                desconto = 0

            if self.stock.isChecked() is True:
                stock = 1
            else:
                stock = 0

            if self.visivel.isChecked()is True:
                visivel = 1
            else:
                visivel = 0

            if self.estado.isChecked()is True:
                estado = 1
            else:
                estado = 0

            if self.existe(code) is True:

                sql = """UPDATE documentos set nome="{nome}", subtotal={subtotal}, desconto={desconto}, taxa={taxa}, 
                total={total}, obs="{obs}", modified="{modified}", modified_by="{modified_by}", stock={stock}, visivel={visivel}
                ,estado={estado} WHERE cod="{cod}" """.format(cod=code, nome=nome, subtotal=subtotal, desconto=desconto, taxa=taxa,
                                              total=total, obs=obs, modified=modified, modified_by=modified_by,
                                              stock=stock, visivel=visivel, estado=estado)
            else:
                values = """ "{cod}", "{nome}", {subtotal}, {desconto}, {taxa} , {total}, "{obs}", "{created}",
                 "{modified}", "{modified_by}", "{created_by}", {stock}, {visivel}, {estado}
                 """.format(cod=code, nome=nome, subtotal=subtotal, desconto=desconto, taxa=taxa, total=total,
                            obs=obs, created=created, modified=modified, modified_by=modified_by, created_by=created_by,
                            stock=stock, visivel=visivel, estado=estado)

                sql = "INSERT INTO documentos (cod, nome, subtotal, desconto, taxa, total, obs, created, modified, modified_by, " \
                      "created_by, stock, visivel, estado) values({value})".format(value=values)

            print(sql)

            try:
                self.cur.execute(sql)
                self.conn.commit()
            except Exception as e:
                QMessageBox.critical(self, "Erro", "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
                return

            if QMessageBox.question(self, "Pergunta", "Registo Gravado com sucesso!\nDeseja Cadastrar outro Item?",
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                self.limpar()
                self.nome.setFocus()
            else:
                self.close()
        else:
            print('Erro de Validacao')

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