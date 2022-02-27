# -*- coding: utf-8 -*-
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QComboBox,QGridLayout, QApplication, QMessageBox, \
    QSplashScreen

import sqlite3 as lite

DB_FILENAME = "dados.tsdb"
EMPRESA_DB = "lista_de_Empresa.db"


class Login(QDialog):

    def __init__(self, parent=None):
        super(Login, self).__init__(parent)

        self.tentativas = 5
        self.contador = 0

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

        btn_grid.addWidget(self.empresas, 0, 0, 1, 3)
        btn_grid.addWidget(self.users, 1, 0, 1, 3)
        btn_grid.addWidget(self.password, 2, 0, 1, 3)
        btn_grid.addWidget(self.btnCalc7, 3, 0)
        btn_grid.addWidget(self.btnCalc8, 3, 1)
        btn_grid.addWidget(self.btnCalc9, 3, 2)
        btn_grid.addWidget(self.btnCalc4, 4, 0)
        btn_grid.addWidget(self.btnCalc5, 4, 1)
        btn_grid.addWidget(self.btnCalc6, 4, 2)
        btn_grid.addWidget(self.btnCalc1, 5, 0)
        btn_grid.addWidget(self.btnCalc2, 5, 1)
        btn_grid.addWidget(self.btnCalc3, 5, 2)
        btn_grid.addWidget(self.btnCalc0, 6, 0)
        btn_grid.addWidget(self.limpar, 6, 1)
        btn_grid.addWidget(self.fechar, 6, 2)
        btn_grid.addWidget(self.ok, 7, 0, 1, 3)

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

        # self.resize(300, 300)
        self.setFixedSize(300, 320)
        # self.encheempresas()

        print("Empresas. {}".format(self.empresas.currentText()))
        
        self.connect_db()
        self.encheusers()

    def empresa_selecionada(self):

        sql = """SELECT empresas.cabecalho, empresas.logo, empresas.slogan, empresas.endereco, empresas.contactos,
               empresas.email, empresas.web, empresas.nuit, empresas.casas_decimais, connection.host, connection.user,
               connection.passw, connection.db FROM empresas INNER JOIN connection ON empresas.nome=connection.empresa 
               WHERE nome="{}" """.format(self.empresas.currentText())

        try:
            conn = lite.connect(EMPRESA_DB)
            cur = conn.cursor()
            cur.execute(sql)
            data = cur.fetchall()

            if len(data) > 0:
                for item in data:
                    self.empresa_cabecalho = item[0]
                    self.empresa_logo = item[1]
                    self.empresa_slogan = item[2]
                    self.empresa_endereco = item[3]
                    self.empresa_contactos = item[4]
                    self.empresa_email = item[5]
                    self.empresa_web = item[6]
                    self.empresa_nuit = item[7]
                    self.empresa_casas_decimais = item[8]
                    self.empresa_host = item[9]
                    self.empresa_user = item[10]
                    self.empresa_passw = item[11]
                    self.empresa_db = item[12]

                    self.mostrareg()
            else:
                print("Não há Empresas Cadastradas.")

        except Exception as e:
            print("Ocurreu um erro na conexão da base de dados Empresas. {}".format(e))

    def connect_db(self):
        # Connect to database and retrieves data

        self.conn = lite.connect(DB_FILENAME)
        self.cur = self.conn.cursor()

            # except Exception as e:
            #     QMessageBox.critical(self, "Erro ao conectar a Base de Dados",
            #                          "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
            #     sys.exit(True)

    def aceite(self):
        sql = """select cod, senha from users WHERE cod="{cod}" and senha="{senha}"
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
                                                             "Faltam {contador} Tentativas".format(contador=tentativas))
            self.Limpar()
            return
        else:

            self.parent().user = data[0][0]
            self.parent().empresa = ""
            self.parent().accoes()
            self.parent().showMaximized()
            self.hide()

    # Enche a combobox lista de Empresas
    def encheempresas(self, lista):
        self.empresas.addItems(lista)

    def encheusers(self):
        sql = "SELECT cod FROM users"
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
        if self.parent() is not None:
            self.parent().close()
        sys.exit

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#
#     helloPythonWidget = Login()
#     helloPythonWidget.show()
#     sys.exit(app.exec_())