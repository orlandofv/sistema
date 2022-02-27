# -*- coding: utf-8 -*-
import sys
import os
from pathlib import Path
from PyQt5.QtGui import *
from PyQt5.QtWidgets import (QDialog, QLineEdit, QPushButton, QComboBox, QGridLayout, QApplication,
                             QMessageBox, QLabel, QGroupBox, QVBoxLayout)
from PyQt5.QtCore import Qt

import sqlite3 as lite

DB_FILENAME = "dados.tsdb"
EMPRESA_DB = "lista_de_Empresa.db"
DADOS_DA_EMPRESA = []
MODULO = ""


class Login(QDialog):

    def __init__(self, parent=None):
        super(Login, self).__init__(parent)

        self.tentativas = 5
        self.contador = 0

        self.nome_empresa = ""
        self.empresas = QComboBox()

        self.empresa_cabecalho = ""
        self.empresa_logo = ""
        self.empresa_slogan = ""
        self.empresa_endereco = ""
        self.empresa_contactos = ""
        self.empresa_email = ""
        self.empresa_web = ""
        self.empresa_nuit = ""
        self.empresa_casas_decimais = ""
        self.empresa_host = ""
        self.empresa_user = ""
        self.empresa_passw = ""
        self.empresa_db = ""

        self.users = QComboBox()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setFocus()
        self.ok = QPushButton("&OK")
        self.ok.setDefault(True)
        self.fechar = QPushButton("&Fechar")

        self.ok.setIcon(QIcon("./icons/ok.ico"))

        self.password.setMaxLength(30)

        self.limpar = QPushButton("&Limpar")
        self.btnCalc0 = QPushButton("0", self)
        self.btnCalc1 = QPushButton("1", self)
        self.btnCalc2 = QPushButton("2", self)
        self.btnCalc3 = QPushButton("3", self)
        self.btnCalc4 = QPushButton("4", self)
        self.btnCalc5 = QPushButton("5", self)
        self.btnCalc6 = QPushButton("6", self)
        self.btnCalc7 = QPushButton("7", self)
        self.btnCalc8 = QPushButton("8", self)
        self.btnCalc9 = QPushButton("9", self)

        btn_grid = QGridLayout()

        grupo = QGroupBox('')
        grupolayout = QVBoxLayout()


        empresa = QLabel("Escolha a Empresa")
        usuario = QLabel("Usuário")

        grupolayout.addWidget(empresa)
        grupolayout.addWidget(self.empresas)
        grupolayout.addWidget(usuario)
        grupolayout.addWidget(self.users)
        grupolayout.addWidget(self.password)
        grupo.setLayout(grupolayout)

        btn_grid.addWidget(grupo, 0, 0, 1, 3)
        btn_grid.addWidget(self.btnCalc7, 1, 0)
        btn_grid.addWidget(self.btnCalc8, 1, 1)
        btn_grid.addWidget(self.btnCalc9, 1, 2)
        btn_grid.addWidget(self.btnCalc4, 2, 0)
        btn_grid.addWidget(self.btnCalc5, 2, 1)
        btn_grid.addWidget(self.btnCalc6, 2, 2)
        btn_grid.addWidget(self.btnCalc1, 3, 0)
        btn_grid.addWidget(self.btnCalc2, 3, 1)
        btn_grid.addWidget(self.btnCalc3, 3, 2)
        btn_grid.addWidget(self.btnCalc0, 4, 0)
        btn_grid.addWidget(self.limpar, 4, 1)
        btn_grid.addWidget(self.fechar, 4, 2)
        btn_grid.addWidget(self.ok, 5, 0, 1, 3)

        self.setLayout(btn_grid)

        self.setWindowTitle("Dados de Entrada")
        self.setWindowIcon(QIcon("./icons/Deleket-Sleek-Xp-Basic-Administrator.ico"))

        self.ok.clicked.connect(self.aceite)
        self.fechar.clicked.connect(sys.exit)

        self.btnCalc0.clicked.connect(self.key0)
        self.btnCalc1.clicked.connect(self.key1)
        self.btnCalc2.clicked.connect(self.key2)
        self.btnCalc3.clicked.connect(self.key3)
        self.btnCalc4.clicked.connect(self.key4)
        self.btnCalc5.clicked.connect(self.key5)
        self.btnCalc6.clicked.connect(self.key6)
        self.btnCalc7.clicked.connect(self.key7)
        self.btnCalc8.clicked.connect(self.key8)
        self.btnCalc9.clicked.connect(self.key9)
        self.limpar.clicked.connect(self.Limpar)

        self.connect_db()
        self.encheempresas()

        self.empresas.currentTextChanged.connect(self.empresa_selecionada)
        # self.encheusers()

    def empresa_selecionada(self):

        sql = """SELECT empresas.cabecalho, empresas.logo, empresas.slogan, empresas.endereco, empresas.contactos,
               empresas.email, empresas.web, empresas.nuit, empresas.casas_decimais, connection.host, connection.user,
               connection.passw, connection.db, connection.db_name, empresas.licenca, empresas.contas, connection.port 
               FROM empresas INNER JOIN connection ON empresas.nome=connection.empresa WHERE 
               nome="{}" """.format(self.empresas.currentText())
        try:

            cur = self.cur_empresa
            cur.execute(sql)
            data = cur.fetchall()

            if len(data) > 0:
                for item in data:
                    self.empresa_cabecalho = str(item[0])
                    self.empresa_logo = str(item[1])
                    self.empresa_slogan = str(item[2])
                    self.empresa_endereco = str(item[3])
                    self.empresa_contactos = str(item[4])
                    self.empresa_email = str(item[5])
                    self.empresa_web = str(item[6])
                    self.empresa_nuit = str(item[7])
                    self.empresa_casas_decimais = str(item[8])
                    self.empresa_host = str(item[9])
                    self.empresa_user = str(item[10])
                    self.empresa_passw = str(item[11])
                    self.empresa_db = str(item[12])
                    self.empresa_db_name = str(item[13])
                    self.licenca = str(item[14])
                    self.contas = str(item[15])
                    self.empresa_port = str(item[16])

                    self.connect_empresa_db()
                    self.encheusers()

            else:
                self.users.clear()
                print("Base de dados para a Empresa {} não foi criada.".format(self.empresas.currentText()))

        except Exception as e:
            print("Ocurreu um erro na conexão da base de dados Empresas. {}".format(e))

    def connect_db(self):
        # Connect to database and retrieves data

        try:
            self.conn_empresa = lite.connect(EMPRESA_DB)
            self.cur_empresa = self.conn_empresa.cursor()
        except Exception as e:
            QMessageBox.critical(self, "Erro ao conectar a Base de Dados",
                                 "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
            sys.exit(True)

    def connect_empresa_db(self):
        # # Connect to database and retrieves data
        # if self.empresa_db_name == "SQLITE":
        #
        #     path = Path(self.empresa_db)
        #
        #     try:
        #         self.conn = lite.connect(str(path))
        #         self.cur = self.conn.cursor()
        #
        #     except Exception as e:
        #         QMessageBox.critical(self, "Erro ao conectar a Base de Dados",
        #                              "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
        #         sys.exit(True)
        # else:
        import mysql.connector as mc

        self.conn = mc.connect(host=self.empresa_host,
                                user=self.empresa_user,
                                passwd=self.empresa_passw,
                                db=self.empresa_db,
                               port=self.empresa_port)

        self.cur = self.conn.cursor()

        print('warnings: ', self.conn.get_warnings,'Server Version: ', self.conn.get_server_version(),
              'Server Info: ', self.conn.get_server_info())

    def aceite(self):
        sql = """select cod, senha, admin from users WHERE cod='{cod}' and senha='{senha}'
         """.format(cod=self.users.currentText(), senha=self.password.text())

        try:
            self.cur.execute(sql)
            data = self.cur.fetchall()
        except Exception as e:
            return

        if len(data) == 0:

            self.contador += 1

            tentativas = 5 - self.contador

            if tentativas == 0:
                sys.exit()

            QMessageBox.information(self, "Credências Errados", "Por Favor verifique seus dados!!! \n "
                                                                "Faltam {contador} Tentativas".format(
                contador=tentativas))
            self.Limpar()
            return
        else:
            #Verifica se é administrador

            print(MODULO)

            if data[0][2] == 0:

                if MODULO == "facturacao":
                    # self.parent().user = data[0][0]
                    self.parent().conn = self.conn
                    self.parent().database = self.conn.database
                    self.parent().cur = self.cur
                    self.parent().empresa = self.empresas.currentText()
                    self.parent().setWindowTitle("Microgest POS - {}".format(self.parent().empresa))
                    DADOS_DA_EMPRESA.append(data[0][0])
                    DADOS_DA_EMPRESA.append(data[0][2])
                    self.fill_empresa()
                    self.parent().DADOS_DA_EMPRESA = DADOS_DA_EMPRESA
                    self.parent().ui()
                    self.parent().accoes()
                    self.parent().showMaximized()

                else:
                    QMessageBox.critical(self, "Acesso restrito", "Só Administradores podem aceder este módulo")
                    sys.exit()
            else:

                self.parent().conn = self.conn
                self.parent().database = self.conn.database
                self.parent().cur = self.cur
                self.parent().empresa = self.empresas.currentText()
                self.parent().setWindowTitle("Microgest POS - {}".format(self.parent().empresa))
                DADOS_DA_EMPRESA.append(data[0][0])
                DADOS_DA_EMPRESA.append(data[0][2])
                self.fill_empresa()
                self.parent().DADOS_DA_EMPRESA = DADOS_DA_EMPRESA
                self.parent().ui()
                self.parent().accoes()
                self.parent().showMaximized()

            print("DB: {}".format(self.conn.database))
            self.hide()

    def fill_empresa(self):
        DADOS_DA_EMPRESA.append(self.empresas.currentText())
        DADOS_DA_EMPRESA.append(self.empresa_cabecalho)
        DADOS_DA_EMPRESA.append(self.empresa_logo)
        DADOS_DA_EMPRESA.append(self.empresa_slogan)
        DADOS_DA_EMPRESA.append(self.empresa_endereco)
        DADOS_DA_EMPRESA.append(self.empresa_contactos)
        DADOS_DA_EMPRESA.append(self.empresa_email)
        DADOS_DA_EMPRESA.append(self.empresa_web)
        DADOS_DA_EMPRESA.append(self.empresa_nuit)
        DADOS_DA_EMPRESA.append(self.empresa_casas_decimais)
        DADOS_DA_EMPRESA.append(self.empresa_host)
        DADOS_DA_EMPRESA.append(self.empresa_user)
        DADOS_DA_EMPRESA.append(self.empresa_passw)
        DADOS_DA_EMPRESA.append(self.empresa_db)
        DADOS_DA_EMPRESA.append(self.empresa_db_name)
        DADOS_DA_EMPRESA.append(self.licenca)
        DADOS_DA_EMPRESA.append(self.contas)

    # Enche a combobox lista de Empresas
    def encheempresas(self):

        self.empresas.clear()

        sql = "select nome from Empresas"

        cur = self.cur_empresa
        cur.execute(sql)
        data = cur.fetchall()

        if len(data) > 0:
            for item in data:
                self.empresas.addItems(item)

            self.nome_empresa = self.empresas.currentText()

    def encheusers(self):

        self.users.clear()

        sql = "SELECT cod FROM users WHERE estado=1 order by cod"
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                self.users.addItems(item)

    def Limpar(self):
        self.password.setText("")

    def key0(self):
        self.password.setFocus()
        self.password.setText(self.password.text() + self.btnCalc0.text())
        self.password.clearFocus()

    def key1(self):
        self.password.setFocus()
        self.password.setText(self.password.text() + self.btnCalc1.text())
        self.password.clearFocus()

    def key2(self):
        self.password.setFocus()
        self.password.setText(self.password.text() + self.btnCalc2.text())
        self.password.clearFocus()

    def key3(self):
        self.password.setFocus()
        self.password.setText(self.password.text() + self.btnCalc3.text())
        self.password.clearFocus()

    def key4(self):
        self.password.setFocus()
        self.password.setText(self.password.text() + self.btnCalc4.text())
        self.password.clearFocus()

    def key5(self):
        self.password.setFocus()
        self.password.setText(self.password.text() + self.btnCalc5.text())
        self.password.clearFocus()

    def key6(self):
        self.password.setFocus()
        self.password.setText(self.password.text() + self.btnCalc6.text())
        self.password.clearFocus()

    def key7(self):
        self.password.setFocus()
        self.password.setText(self.password.text() + self.btnCalc7.text())
        self.password.clearFocus()

    def key8(self):
        self.password.setFocus()
        self.password.setText(self.password.text() + self.btnCalc8.text())
        self.password.clearFocus()

    def key9(self):
        self.password.setFocus()
        self.password.setText(self.password.text() + self.btnCalc9.text())
        self.password.clearFocus()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def showEvent(self, evt):
        self.password.setFocus()
        self.center()

    def closeEvent(self, evt):
        sys.exit(True)

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == Qt.Key_Escape:
            self.close()
        elif a0.key() in (Qt.Key_Enter, 16777220, Qt.Key_F10):
            self.aceite()
        else:
            a0.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    helloPythonWidget = Login()
    helloPythonWidget.show()
    sys.exit(app.exec_())