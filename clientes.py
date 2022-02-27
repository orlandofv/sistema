# -*- coding: utf-8 -*-
"""
Created on Fri Mar 02 23:18:43 2012

@author: lims
"""

from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QFormLayout, QVBoxLayout, QToolBar, QMessageBox,\
    QTextEdit, QAction, QApplication, QCheckBox
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QIcon
import sys

from utilities import codigo as cd
from pricespinbox import price


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

        self.codcliente = ""

    def ui(self):
        html = """<center style= "background-image: './images/control.png'" > <h2 > Cadastro de cliente </h2> </center> """

        self.titulo = QLabel(html)
        cod = QLabel("Codigo")
        nome = QLabel("Nome")
        endereco = QLabel("Endereço")
        nuit = QLabel("NUIT")
        email = QLabel("Email")
        contacto = QLabel("Contactos")
        desconto = QLabel("Desconto nas Compras (%)")
        valor_minimo = QLabel("Valor mínimo para Desconto:")
        max_credito  = QLabel("Valor máximo de crédito:")
        obs = QLabel("Observações")

        self.cod = QLineEdit()
        self.cod.setMaximumWidth(140)
        self.cod.setObjectName("cod")
        self.cod.setAlignment(Qt.AlignRight)
        self.cod.setDisabled(True)
        self.nome = QLineEdit()
        self.nome.setMaxLength(50)
        self.endereco = QLineEdit()
        self.NUIT = QLineEdit()
        self.NUIT.setAlignment(Qt.AlignRight)
        self.NUIT.setMaxLength(9)
        self.email = QLineEdit()
        self.email.setMaxLength(50)
        self.contacto = QLineEdit()
        self.contacto.setMaxLength(255)
        self.desconto = price()
        self.valor_minimo = price()
        self.valor_minimo.setToolTip("Valor Mínimo para se conceder Desconto")
        self.max_credito = price()
        self.obs = QTextEdit()
        self.estado_ckbox = QCheckBox("Activo")
        self.estado_ckbox.setChecked(True)

        grid = QFormLayout()

        grid.addRow(cod, self.cod)
        grid.addRow(nome, self.nome)
        grid.addRow(endereco, self.endereco)
        grid.addRow(nuit, self.NUIT)
        grid.addRow(email, self.email)
        grid.addRow(contacto, self.contacto)
        grid.addRow(desconto, self.desconto)
        grid.addRow(valor_minimo, self.valor_minimo)
        grid.addRow(max_credito, self.max_credito)
        grid.addRow(obs, self.obs)
        grid.addWidget(self.estado_ckbox)

        vLay = QVBoxLayout(self)
        vLay.setContentsMargins(0, 0, 0, 0)

        cLay = QVBoxLayout()
        cLay.setContentsMargins(10, 10, 10, 10)

        cLay.addLayout(grid)

        vLay.addWidget(self.titulo)
        vLay.addLayout(cLay)
        vLay.addWidget(self.tool)
        self.setLayout(vLay)

        self.setWindowTitle("Cadastro de Clientes")

        style = """
            margin: 0;
            padding: 0;
            border-image:url(./images/transferir.jpg) 30 30 stretch;
            background:#303030;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 12px;
            color: #FFFFFF;
        """

        self.titulo.setStyleSheet(style)

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

    def closeEvent(self, evt):
        parent = self.parent()
        try:
            if parent is not None:
                parent.enche_items()
                parent.fill_table(parent.table_header, parent.table_data)
        except Exception as e:
            return

    def fechar(self):
        self.close()

    def limpar(self):
        for child in (self.findChildren(QLineEdit) or self.findChildren(QTextEdit)):
            if child.objectName() not in ["cod", "cal1", "cal2"]: child.clear()

        # gera novo codigo para clientes
        from utilities import codigo
        self.cod.setText("CL" + codigo("CL" + "abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789"))

    def validacao(self):

        if str(self.nome.text()) == "":
            QMessageBox.information(self, "Erro", "Nome do Cliente inválido")
            self.nome.setFocus()
            return False
        else:
            return True

    def mostrar_registo(self):

        sql = """SELECT * from clientes WHERE cod = "{codigo}" """.format(codigo=str(self.cod.text()))
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            self.cod.setText("CL" + cd("abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789"))
        else:
            self.nome.setText(''.join(data[0][1]))
            self.endereco.setText(''.join(data[0][2]))
            self.NUIT.setText(''.join(data[0][3]))
            self.email.setText(''.join(data[0][4]))
            self.contacto.setText(''.join(data[0][5]))
            desconto = float(data[0][6])
            self.desconto.setValue(desconto)
            valor_minimo = float(data[0][7])
            self.valor_minimo.setValue(valor_minimo)
            self.obs.setPlainText(''.join(data[0][8]))
            self.estado_ckbox.setChecked(bool(int(data[0][9])))
            if data[0][14] is not None:
                self.max_credito.setValue(data[0][14])

    def existe(self, codigo):

        sql = """SELECT cod from clientes WHERE cod = "{codigo}" """.format(codigo=str(self.cod.text()))

        self.cur.execute(sql)
        data = self.cur.fetchall()

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
            endereco = self.endereco.text()
            nuit = self.NUIT.text()
            email = self.email.text()
            contactos = self.contacto.text()
            desconto = self.desconto.value()
            valor_minimo = self.valor_minimo.value()
            obs = self.obs.toPlainText()
            created = QDateTime.currentDateTime().toString('yyyy-MM-dd H:m:s')
            modified = QDateTime.currentDateTime().toString('yyyy-MM-dd H:m:s')
            credito = self.max_credito.value()

            self.codcliente = self.cod.text()

            modified_by = self.parent().user
            estado = int(self.estado_ckbox.isChecked())

            if self.parent() is not None:
                created_by = self.parent().user
            else:
                created_by = "User"

            if self.existe(code) is True:

                sql = """UPDATE clientes SET nome="{nome}", endereco="{endereco}", NUIT="{NUIT}", email="{email}", 
                contactos="{contactos}", estado={estado}, desconto={valor_desconto}, valor_minimo = {valor_minimo}, 
                obs="{obs}", modified="{modified}", modified_by="{modified_by}", credito={credito} WHERE cod="{cod}"
                """.format(cod=code, nome=nome, endereco=endereco,NUIT=nuit, email=email, contactos=contactos,
                           valor_desconto=desconto, valor_minimo=valor_minimo, obs=obs,
                           modified=modified, modified_by=modified_by, credito=credito, estado=estado)
            else:
                values = """ "{cod}", "{nome}", "{endereco}", "{NUIT}", "{email}", "{contactos}", {valor_desconto} ,
                 {valor_minimo}, "{obs}", {estado}, "{created}", "{modified}", "{modified_by}", "{created_by}", 
                 credito={credito} """.format(cod=code, nome=nome, endereco=endereco, NUIT=nuit, email=email,
                                              contactos=contactos,
                             valor_desconto=desconto, valor_minimo=valor_minimo, obs=obs, estado=estado,
                             created=created, modified=modified, modified_by=modified_by, created_by=created_by,
                             credito=credito)

                sql = "INSERT INTO clientes (cod, nome, endereco, NUIT,email, contactos, desconto, valor_minimo, " \
                      "obs, estado, created, modified, modified_by, created_by, credito)" \
                      " values({value})".format(value=values)

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