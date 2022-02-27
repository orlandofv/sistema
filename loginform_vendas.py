# -*- coding: utf-8 -*-
import sys
from pathlib import Path

from PyQt5.QtGui import *
from PyQt5.QtWidgets import (QFormLayout, QLineEdit, QPushButton, QComboBox, QGridLayout, QApplication,
                             QMessageBox, QLabel, QGroupBox, QVBoxLayout, QHBoxLayout, QSizePolicy,
                             QWidget, QSplitter, QDialog)
from PyQt5.QtCore import Qt
from teclado_alfanumerico import Teclado

import sqlite3 as lite

DB_FILENAME = "dados.tsdb"
EMPRESA_DB = "lista_de_Empresa.db"
DADOS_DA_EMPRESA = []
MODULO = ""

STYLE = """
QDialog {border: 3px solid blue;
}
"""

class Login(QDialog):

    def __init__(self, parent=None):
        super(Login, self).__init__(parent)

        self.setStyleSheet(STYLE)
        boldFont = QFont('Consolas', 14)
        boldFont.setBold(True)

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
        self.codarmazem = ""
        self.nome_armazem = ""

        self.users = QComboBox()
        self.password = QLineEdit()
        self.password.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setFocus()
        self.ok = QPushButton("&OK")

        self.ok.setFocusPolicy(Qt.StrongFocus)
        self.ok.setFocus()
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

        grupo = QGroupBox('')
        grupolayout = QVBoxLayout()

        empresa = QLabel("Escolha a Empresa")
        usuario = QLabel("Usuário")
        senha = QLabel('Senha')
        armazem = QLabel("Armazém")
        self.armazem = QComboBox()
        self.armazem.currentIndexChanged.connect(self.getcodarmazem)

        form_lay = QFormLayout()

        teclado_btn = QPushButton("...")

        teclado_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # teclado_btn.setMaximumWidth(40)
        form_lay.addRow(self.password, teclado_btn)
        teclado_btn.clicked.connect(self.mostrar_teclado)

        grupolayout.addWidget(empresa)
        grupolayout.addWidget(self.empresas)
        grupolayout.addWidget(usuario)
        grupolayout.addWidget(self.users)
        grupolayout.addWidget(senha)
        grupolayout.addLayout(form_lay)
        grupolayout.addWidget(armazem)
        grupolayout.addWidget(self.armazem)

        grupo.setLayout(grupolayout)

        btn_grid = QGridLayout()

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

        logolabel = QLabel()

        pixmap = QPixmap("./images/luxury_hotel-wallpaper-1680x1260.jpg")
        pixmap.scaled(64, 64, Qt.KeepAspectRatio)

        logolabel.setPixmap(pixmap)
        logolabel.setScaledContents(True)
        logolabel.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))

        logingroup = QGroupBox("Dados de Entrada")
        logingroup.setMinimumWidth(800)
        logingroup.setLayout(btn_grid)

        spliter = QSplitter(Qt.Horizontal)
        spliter.clearFocus()

        logingroup.setMinimumWidth(spliter.width() * .5)
        spliter.addWidget(logolabel)
        spliter.addWidget(logingroup)

        mainlayout = QHBoxLayout()

        mainlayout.addWidget(spliter)

        self.setLayout(mainlayout)

        for child in self.findChildren(QPushButton):
            child.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred))
            child.setDefault(False)
            child.setFont(boldFont)

        self.ok.setDefault(True)

        for child in self.findChildren(QComboBox):
            child.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred))
            child.setFont(boldFont)

        for child in self.findChildren(QLineEdit):
            child.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred))
            child.setFont(boldFont)

        self.setWindowTitle("Dados de Entrada")
        self.setWindowIcon(QIcon("./icons/Deleket-Sleek-Xp-Basic-Administrator.ico"))

    def mostrar_teclado(self):
        tc = Teclado(self.password)
        tc.descricao.setEchoMode(QLineEdit.Password)
        tc.setModal(True)
        tc.show()

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
                    self.enchearmazens()

            else:
                self.users.clear()
                self.armazem.clear()

                print("Base de dados para a Empresa {} não foi criada.".format(self.empresas.currentText()))

        except Exception as e:
            print("Ocurreu um erro na conexão da base de dados Empresas. {}".format(e))


        self.setWindowTitle("Login")

    def keyPressEvent(self, event):
        try:
            if event.key() in (Qt.Key_Enter, 16777220):
                self.aceite()
            elif event.key() == Qt.Key_Escape:
                self.close()

        except Exception as e:
            print(e)

    def connect_db(self):
        # Connect to database and retrieves data

        try:
            self.conn_empresa = lite.connect(EMPRESA_DB)
            self.cur_empresa = self.conn_empresa.cursor()

            # sql = """CREATE TABLE IF NOT EXISTS config(
            #                 id autoicrement primary key,
            #                 nomeempresa text,
            #                 FOREIGN KEY (nomeempresa) REFERENCES empresas(nome)
            #                 )"""
            #
            #
            # self.cur_empresa.execute(sql)
            # for x in range(101):
            #     sql2 = "ALTER TABLE config ADD COLUMN config{} INTEGER DEFAULT 1".format(x)
            #     self.cur_empresa.execute(sql2)
            #
            # self.conn_empresa.commit()

        except Exception as e:
            QMessageBox.critical(self, "Erro ao conectar a Base de Dados",
                                 "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
            sys.exit(True)

    def connect_empresa_db(self):
        # Connect to database and retrieves data

        if self.empresa_db_name == "SQLITE":

            path = Path(self.empresa_db)

            try:
                self.conn = lite.connect(str(path))
                self.cur = self.conn.cursor()

            except Exception as e:
                QMessageBox.critical(self, "Erro ao conectar a Base de Dados",
                                     "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
                sys.exit(True)
        else:
            import mysql.connector as mc

            self.conn = mc.connect(host=self.empresa_host,
                                    user=self.empresa_user,
                                    passwd=self.empresa_passw,
                                    db=self.empresa_db,
                                   port=self.empresa_port)

            self.cur = self.conn.cursor()

            # sql = "SELECT * FROM INFORMATION_SCHEMA.INNODB_SYS_TABLESPACES WHERE NAME ='{}/caixa'".format(self.empresa_db)
            sql = "SHOW COLUMNS FROM {}.facturacaodetalhe".format(self.empresa_db)
            self.cur.execute(sql)
            data = self.cur.fetchall()

            print(self.conn)
            # print("lista=",data)

            print('warnings: ', self.conn.get_warnings, 'Server Version: ', self.conn.get_server_version(),
                  'Server Info: ', self.conn.get_server_info())

    def aceite(self):

        sql = """select cod, senha, admin, gestor from users WHERE cod='{cod}' and senha='{senha}'
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
            self.password.setFocus()

            return

        else:
            # Verifica se é administrador

            DADOS_DA_EMPRESA.clear()
            self.parent().DADOS_DA_EMPRESA.clear()

            # Se nao for admin
            if data[0][2] == 0:

                if MODULO == "facturacao" or MODULO == "RESTAURANTE" :

                    if data[0][3] == 1:
                        self.parent().gestor = True
                    else:
                        self.parent().gestor = False

                    if data[0][2] == 1:
                        self.parent().admin = True
                    else:
                        self.parent().admin = False

                    DADOS_DA_EMPRESA.append(data[0][0])
                    DADOS_DA_EMPRESA.append(data[0][2])
                    self.fill_empresa()

                    self.parent().DADOS_DA_EMPRESA = DADOS_DA_EMPRESA

                    if self.empresas.isEnabled() is True:
                        self.parent().empresa = self.empresas.currentText()
                        self.parent().setWindowTitle("Microgest POS - {}".format(self.parent().empresa))
                        self.parent().conn = self.conn
                        self.parent().database = self.conn.database
                        self.parent().cur = self.cur
                        self.parent().ui()
                        self.parent().gera_codigogeral()
                        
                        

                    self.hide()

                elif MODULO == "hotel":

                    if data[0][3] == 1:
                        self.parent().gestor = True
                    else:
                        self.parent().gestor = False

                    if data[0][2] == 1:
                        self.parent().admin = True
                    else:
                        self.parent().admin = False

                    DADOS_DA_EMPRESA.append(data[0][0])
                    DADOS_DA_EMPRESA.append(data[0][2])
                    self.fill_empresa()

                    self.parent().DADOS_DA_EMPRESA = DADOS_DA_EMPRESA

                    if self.empresas.isEnabled() is True:
                        self.parent().empresa = self.empresas.currentText()
                        self.parent().setWindowTitle("Microgest POS - {}".format(self.parent().empresa))
                        self.parent().conn = self.conn
                        self.parent().database = self.conn.database
                        self.parent().cur = self.cur
                        self.parent().ui()

                    self.hide()

                else:
                    QMessageBox.critical(self, "Acesso restrito", "Só Administradores podem aceder este módulo")
            else:

                if MODULO == "hotel":

                    if data[0][3] == 1:
                        self.parent().gestor = True
                    else:
                        self.parent().gestor = False

                    if data[0][2] == 1:
                        self.parent().admin = True
                    else:
                        self.parent().admin = False

                    DADOS_DA_EMPRESA.append(data[0][0])
                    DADOS_DA_EMPRESA.append(data[0][2])
                    self.fill_empresa()

                    self.parent().DADOS_DA_EMPRESA = DADOS_DA_EMPRESA

                    if self.empresas.isEnabled() is True:
                        self.parent().empresa = self.empresas.currentText()
                        self.parent().setWindowTitle("Microgest POS - {}".format(self.parent().empresa))
                        self.parent().conn = self.conn
                        self.parent().database = self.conn.database
                        self.parent().cur = self.cur
                        self.parent().ui()

                    self.hide()
                else:
                    if data[0][3] == 1:
                        self.parent().gestor = True
                    else:
                        self.parent().gestor = False

                    if data[0][2] == 1:
                        self.parent().admin = True
                    else:
                        self.parent().admin = False

                    DADOS_DA_EMPRESA.append(data[0][0])
                    DADOS_DA_EMPRESA.append(data[0][2])
                    self.fill_empresa()

                    self.parent().DADOS_DA_EMPRESA = DADOS_DA_EMPRESA

                    if self.empresas.isEnabled() is True:
                        self.parent().empresa = self.empresas.currentText()
                        self.parent().setWindowTitle("Microgest POS - {}".format(self.parent().empresa))
                        self.parent().conn = self.conn
                        self.parent().database = self.conn.database
                        self.parent().cur = self.cur
                        self.parent().ui()
                        self.parent().gera_codigogeral()

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

    def enchearmazens(self):

        self.armazem.clear()

        sql = "SELECT nome FROM armazem WHERE estado=1 and mostrar=1 order by nome"
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                self.armazem.addItems(item)

    def getcodarmazem(self):
        if self.armazem.currentText() == "":
            self.codarmazem = ""
            return

        sql = """SELECT cod from armazem WHERE nome="{}" """.format(self.armazem.currentText())
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            self.codarmazem = data[0][0]
            if self.parent() is not None:
                self.parent().codarmazem = self.codarmazem
                self.parent().nome_armazem = self.armazem.currentText()

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

        self.encra = QApplication.desktop().screenGeometry(screen)

    def showEvent(self, evt):
        self.password.setFocus()
        self.center()

    def closeEvent(self, evt):
        sys.exit()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    helloPythonWidget = Login()
    helloPythonWidget.showFullScreen()
    sys.exit(app.exec_())