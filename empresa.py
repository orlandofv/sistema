# -*- coding: utf-8 -*-
"""
Created on Fri Mar 02 23:18:43 2012

@author: lims
"""
import sys
from os import path

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QTextEdit, QPushButton, QFormLayout, QVBoxLayout, QFileDialog,\
    QToolBar, QAction, QMessageBox, QApplication, QSpinBox, QComboBox, QTabWidget, QWidget, QRadioButton, QSizePolicy, \
    QProgressDialog, QListWidget

import sqlite3 as lite

DB_FILENAME = "lista_de_Empresa.db"
DB_LIST = "MYSQL"  # , "ORACLE", "SQLServer", "Firebird")
import mysql.connector as mc
database = "database.sql"
FILE = open(database, encoding="utf8")
DB_FILE = FILE.read()

class Empresa(QDialog):

    def __init__(self, parent=None):
        super(Empresa, self).__init__(parent)

        self.resize(600, 600)
        self.logtipo = ""
        self.accoes()
        self.ui()

        if self.parent() is None:
            self.db = self.connect_db()
        else:
            self.conn = self.parent().conn
            self.cur = self.parent().cur

        self.setWindowTitle("Cadastro de Empresas")

    def connect_db(self):

        try:
            self.conn = lite.connect(DB_FILENAME)
            self.cur = self.conn.cursor()

        except Exception as e:
            QMessageBox.critical(self, "Erro ao conectar a Base de Dados",
                                 "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
            sys.exit(True)

    def exists_db(self, host, user, passw, port):

        lista_db = []
        try:
            conn = mc.connect(host=host, user=user, passwd=passw, port=port)
            cur = conn.cursor()
            cur.execute("show databases")
            lista = cur.fetchall()

            for x in lista:
                lista_db.append(x[0])

        except Exception as e:
            print(e)

        return lista_db

    def testar_db(self):
        progress = QProgressDialog(self)
        progress.setWindowTitle("Criando a Base de dados...")
        progress.setLabel(QLabel("Criando a Base de dados...Por Favor aguarde."))
        progress.setMinimum(0)
        progress.setMaximum(125)
        progress.setModal(True)
        progress.show()
        self.lista.clear()

        host = self.host.text()
        user = self.user.text()
        passw = self.passw.text()
        db = self.database.text()
        port = self.port.value()
        cont = 0

        if self.criar_db.isChecked():

            if self.database.text() == "":
                DB_NAME = 'microgest'
            else:
                DB_NAME = self.database.text()

            host = self.host.text()
            user = self.user.text()
            passw = self.passw.text()
            db = DB_NAME.lower()
            port = self.port.value()

            lista = self.exists_db(host, user, passw, port)

            print("Lista de Base de dados: {} ".format(lista))

            if db in lista:
                if self.connect_empresa_db(host, user, passw, db, port) is False:
                    return False
                else:
                    return True
            else:
                if QMessageBox.question(self, "Nova Base de dados",
                                        "Base de dados não existe. Deseseja criar uma nova?") == QMessageBox.Yes:
                    try:
                        conn = mc.connect(host=host, user=user, passwd=passw, port=port)
                        cur = conn.cursor()
                        cur.execute("CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(db))
                        print("Base de dados: {}, criada com sucesso!".format(db))
                        cur.execute("use {}".format(db))
                        results = cur.execute(DB_FILE, multi=True)

                        for cur in results:
                            self.lista.addItem(str(cur.statement))
                            cont +=1
                            progress.setValue(cont)

                        conn.commit()
                        conn.close()
                        progress.close()

                        QMessageBox.information(self, "Sucesso", "Base de dados criada com sucesso!")

                        return True

                    except Exception as e:
                        print(e.args)
                        QMessageBox.warning(self, "Erro", "Erro na criação da Base de Dados.\n{}".format(e))
                        progress.cancel()
                        progress.close()
                        return False
        else:
            if self.connect_empresa_db(host, user, passw, db, port) is False:
                return False
            else:
                return True

    def connect_empresa_db(self, host, user, passw, db, port):

        try:
            self.cnx = mc.connect(host=host, user=user, passwd=passw, db=db, port=port)
            self.cnx_cur = self.cnx.cursor()

            QMessageBox.information(self, "Sucesso", "Conexão da Base de Dados bem sucedida.")
            return True
        except mc.Error as e:
            QMessageBox.critical(self, "Erro de conexão", "Erro na conexão da Base de Dados. \n "
                                                          "A Empresa pode não funcionar. {}.".format(e))
            return False

    def ui(self):

        html = """<center style= "{color:red;}" > <h2 > Cadastro de empresas </h2> </center> """
        # validator2 = QRegExp("^[a-zA-Z ]{1,50}$")

        # self.setFixedSize(600, 600)

        tab = QTabWidget(self)

        titulo = QLabel(html)
        nome = QLabel("Nome da Empresa")
        cabecalho = QLabel("Cabeçalho")
        slogan = QLabel("Slogan")
        endereco = QLabel("Endereço")
        contactos = QLabel("Contatcos")
        email = QLabel("Email")
        web = QLabel("Página Web")
        nuit = QLabel("NUIT")
        casas_decimais = QLabel("Casas Decimais")
        contas = QLabel("Contas Bancárias:")
        licenca = QLabel("Licenca Fiscal")

        base_de_dados = QLabel("Escolha a Base de dados")
        host = QLabel("Host")
        port = QLabel("Porta")
        user = QLabel("User")
        passw = QLabel("Password")
        service = QLabel("Base de dados")

        self.base_de_dados = QComboBox()
        self.base_de_dados.addItem(DB_LIST)
        self.base_de_dados.setCurrentText(DB_LIST[0])
        self.host = QLineEdit()
        self.port = QSpinBox()
        self.port.setRange(1, 999999999)
        self.user = QLineEdit()
        self.passw = QLineEdit()
        self.passw.setEchoMode(QLineEdit.Password)
        self.database = QLineEdit()
        self.conectar_db = QRadioButton("Conectar a Base de dados")
        self.conectar_db.setChecked(True)
        self.criar_db = QRadioButton("Criar e conectar a Base de dados")
        test = QPushButton("Connectar")
        test.clicked.connect(self.testar_db)

        self.base_de_dados.currentTextChanged.connect(self.desabilita_habilita_campos)

        self.nome = QComboBox()
        self.nome.setEditable(True)
        self.nome.currentTextChanged.connect(self.mostrar_registo)

        self.slogan = QLineEdit()
        self.slogan.setMaxLength(255)
        self.endereco = QLineEdit()
        self.endereco.setMaxLength(255)
        self.contactos = QLineEdit()
        self.contactos.setMaxLength(255)
        self.email = QLineEdit()
        self.email.setMaxLength(255)
        self.web = QLineEdit()
        self.web.setMaxLength(255)
        self.nuit = QLineEdit()
        self.nuit.setMaxLength(15)
        # self.nuit.setRange(0, 499999999)
        self.casas_decimais = QSpinBox()
        self.casas_decimais.setRange(0, 9)
        self.cabecalho = QTextEdit()
        self.licenca = QLineEdit()
        self.contas = QLineEdit()
        self.btn = QPushButton("Logo")
        self.btn.clicked.connect(self.selecionar_foto)

        logoHtml = """ QLabel{
            width:40px;
             border-color: #9B9B9B;
             border-bottom-color: #C2C7CB; /* same as pane color */
         }"""

        self.foto = QLabel("Logo")
        self.foto.setStyleSheet(logoHtml)

        self.lista = QListWidget(self)

        grid = QFormLayout()
        grid.addRow(nome, self.nome)
        grid.addRow(slogan, self.slogan)
        grid.addRow(endereco, self.endereco)
        grid.addRow(contactos, self.contactos)
        grid.addRow(email, self.email)
        grid.addRow(web, self.web)
        grid.addRow(nuit, self.nuit)
        grid.addRow(casas_decimais, self.casas_decimais)
        grid.addRow(contas, self.contas)
        grid.addRow(licenca, self.licenca)
        grid.addRow(cabecalho, self.cabecalho)
        grid.addRow(self.btn, self.foto)

        conn_grid = QFormLayout()
        conn_grid.addRow(base_de_dados, self.base_de_dados)
        conn_grid.addRow(host, self.host)
        conn_grid.addRow(port, self.port)
        conn_grid.addRow(user, self.user)
        conn_grid.addRow(passw, self.passw)
        conn_grid.addRow(service, self.database)
        conn_grid.addRow(self.conectar_db, self.criar_db)

        # This is the Main Layout that will hold the title, cLay and ToolBar
        vLay = QVBoxLayout(self)
        vLay.setContentsMargins(0,0,0,0)
        
        cLay = QVBoxLayout()
        cLay.setContentsMargins(10,10,10,10)
        cLay.addLayout(grid)

        # we add titilo, cLay(VBoxLayout) and the ToolBar

        vLay.addWidget(titulo)
        vLay.addWidget(tab)
        vLay.addWidget(self.tool)


        conf_empresa = QWidget()
        conf_empresa.setLayout(cLay)
        conn = QWidget()
        conn_lay = QVBoxLayout()
        conn_lay.addLayout(conn_grid)
        conn_lay.addWidget(self.lista)
        conn_lay.addWidget(test)
        conn.setLayout(conn_lay)

        tab.addTab(conf_empresa, "Dados da Empresa")
        tab.addTab(conn, "Connecções")

        self.setWindowTitle("Dados da Empresa")
        
        style = """
            margin: 0;
            padding: 0;
            border-image:url(./images/splitter_vertical_light.png.jpg) repeat-x;
            background: cyan;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 12px;
            color: #FFFFFF;
        
        """ 
        
        titulo.setStyleSheet(style)

    def selecionar_foto(self):

        formats = "Todas as Imagens(*.bmp; *.jpg; *.png)"
        self.path = "."

        dialog = QFileDialog(self)
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        path = dialog.getOpenFileName(self, "Escolha o Ficheiro", self.path, formats)

        if path == "":
            caminho = ""
        else:
            caminho = path[0]

        self.logtipo = caminho
        self.foto.setText(self.logtipo)

    # Rotina que vai mostrar a foto do produto ou serviço,
    # ele leva um file

    def mostrarfoto(self, foto):
        caminho_legal = foto.replace("/", "\\")
        pixmap = QPixmap(caminho_legal)
        pixmap.scaled(16, 16, Qt.KeepAspectRatio)
        self.foto.setPixmap(pixmap)
        self.foto.setScaledContents(True)
        self.foto.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.fotofile = caminho_legal

    def remover_foto(self):
        self.fotofile = ""
        self.foto.setPixmap(QPixmap(""))

    def validar_db(self):
        if self.database.text() == "":
            return False

        if self.base_de_dados.currentText() == DB_LIST[1]:
            if self.host.text() == "":
                self.host.setFocus()
                return False

            if self.user.text() == "":
                self.user.setFocus()
                return False

            if self.passw.text() == "":
                self.passw.setFocus()
                return False

        if self.base_de_dados.currentText() == DB_LIST[0]:
            self.user.setText("")
            self.host.setText("")
            self.passw.setText("")

            if self.database.text() == "":
                return False

        return True

    # Verifica se a Empresa ja tem ou nao uma base de dados
    def existe_db(self, empresa):

        cur = self.conn.cursor()

        sql = """select empresa from connection WHERE empresa="{}" """.format(empresa)

        cur.execute(sql)
        data = cur.fetchall()

        if len(data) == 0:
            return False

        return True

    # Habilita e desabilita campos nos dados da Base de dados
    def desabilita_habilita_campos(self):

        if self.base_de_dados.currentText() == DB_LIST[0]:

            self.user.setEnabled(False)
            self.passw.setEnabled(False)
            self.host.setEnabled(False)
        else:
            self.user.setEnabled(True)
            self.passw.setEnabled(True)
            self.host.setEnabled(True)

    def setnomedb(self):
        if self.database.text() == "":
            self.database.setText(self.nome.currentText())

    def accoes(self):
        self.tool = QToolBar()
        self.tool.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.tool.setContextMenuPolicy(Qt.PreventContextMenu)

        gravar = QAction(QIcon("./icons/SaveGreen.ico"),"&Gravar dados",self)
        eliminar = QAction(QIcon("./icons/Delete.ico"),"&Eliminar dados",self)

        fechar = QAction(QIcon("./icons/filequit.png"),"&Fechar",self)
        
        self.tool.addAction(gravar)
        self.tool.addAction(eliminar)
        self.tool.addSeparator()
        self.tool.addAction(fechar)

# ==============================================================================
        gravar.triggered.connect(self.gravar)
        eliminar.triggered.connect(self.apagar)
        fechar.triggered.connect(self.fechar)
# ==============================================================================
        
    def fechar(self):
        self.close()

    def mostrar_registo(self):

        sql = """SELECT empresas.cabecalho, empresas.logo, empresas.slogan, empresas.endereco, empresas.contactos, 
        empresas.email, empresas.web, empresas.nuit, empresas.casas_decimais, empresas.licenca, empresas.contas , 
        connection.host, connection.user, connection.passw, connection.db, connection.db_name, connection.port 
        FROM empresas INNER JOIN connection ON empresas.nome=connection.empresa WHERE nome="{}" 
        """.format(self.nome.currentText())

        # Muda o nome da Base de dados
        self.setnomedb()

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]



        if len(data) > 0:

            try:
                for item in data:

                    self.cabecalho.setPlainText(item[0])
                    self.foto.setText(item[1])
                    self.slogan.setText(item[2])
                    self.endereco.setText(item[3])
                    self.contactos.setText(item[4])
                    self.email.setText(item[5])
                    self.web.setText(item[6])
                    self.nuit.setText(str(item[7]))
                    self.casas_decimais.setValue(int(item[8]))
                    self.licenca.setText(item[9])
                    self.contas.setText(item[10])
                    self.host.setText(item[11])
                    self.user.setText(item[12])
                    self.passw.setText(item[13])
                    self.database.setText(item[14])
                    self.base_de_dados.setCurrentText(item[15])
                    self.port.setValue(int(item[16]))
            except Exception as e:
                print("Erro: {}".format(e))

    def showEvent(self, evt):
        self.desabilita_habilita_campos()
        self.mostrar_registo()

    def apagar(self):
        for child in (self.findChildren(QLineEdit) or self.findChildren(QComboBox) or self.findChildren(QTextEdit)):
            child.clear()

    def existe_empresa(self, empresa):
        sql = """ select nome from empresas Where nome ="{}" """.format(empresa)

        try:
            self.cur.execute(sql)
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]

        except Exception as e:
            print("Não há nenhuma Empresa cadastrada. {}.".format(e))
            return False

        if len(data) == 0:
            return False
        else:
            return True

    def gravar(self):

        nome = str(self.nome.currentText())
        cabecalho = str(self.cabecalho.toPlainText())
        logo = self.logtipo
        slogan = self.slogan.text()
        endereco = self.endereco.text()
        contactos = self.contactos.text()
        email = self.email.text()
        web = self.web.text()
        nuit = self.nuit.text()
        casas_decimais = self.casas_decimais.text()
        db_name = self.base_de_dados.currentText()
        host = self.host.text()
        user = self.user.text()
        passw = self.passw.text()
        db = self.database.text()
        licenca = self.licenca.text()
        contas = self.contas.text()
        port = self.port.value()

        if nome == "":
            QMessageBox.warning(self, "Dado necessário", "O nome da Empresa não pode estar Vazio")
            self.nome.setFocus()
            return

        if len(nuit) < 9:
            QMessageBox.warning(self, "Dado necessário", "O NUIT da Empresa deve conter 9 dígitos")
            self.nuit.setFocus()
            return

        if self.database.text() == "":
            QMessageBox.warning(self, "Dado necessário", "O Nome da Base de dados não pode estar vazio.")
            self.database.setFocus()
            return

        if self.existe_db(nome) is True:
            sql1 = """UPDATE connection set host="{}", user="{}", passw="{}", db="{}", db_name="{}", port={}
            WHERE empresa= '{}' """.format(host, user, passw, db, db_name, port, nome)
        else:
            sql1 = """INSERT into connection (empresa, host, user, passw, db, db_name, port) 
            VALUES ('{}', '{}', '{}', '{}', '{}', '{}', {}) """.format(nome, host, user, passw, db, db_name, port)

        if len(casas_decimais) == 0:
            self.casas_decimais.setValue(2)

        if self.existe_empresa(nome) == False:
            
            sql = """INSERT INTO empresas (nome, cabecalho, logo, slogan, endereco, 
            contactos, email, web, nuit, casas_decimais, licenca, contas)
            values ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', {}, {}, '{}', '{}')""".format(nome, cabecalho, logo, slogan,
                                                                                  endereco, contactos, email, web, nuit
                                                                                  , casas_decimais, licenca, contas)
        else:

            sql = """ UPDATE empresas set cabecalho="{}", logo="{}", slogan="{}", endereco="{}", contactos="{}",
            email="{}", web="{}", nuit={}, casas_decimais={}, licenca = '{}', contas = '{}'
            WHERE nome= '{}' """.format(cabecalho, logo, slogan, endereco, contactos,
                                        email, web, nuit, casas_decimais, licenca, contas, nome)
        try:
            self.cur.execute(sql)
            self.cur.execute(sql1)
            self.conn.commit()
            if QMessageBox.question(self, "Sucesso", "Registo gravado com sucesso. "
                                                     "Deseja Fazer o teste da base de dados agora?") == QMessageBox.Yes:
                self.testar_db()

            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Dados não gravados", "Erro na gravação de dados.{}.".format(e))
            print(e)

    def closeEvent(self, evt):

        parente = self.parent()
        if parente is not None:
            parente.fill_table()


class CreateDatabase:

    def __init__(self, host, user, passw, db):

        self.host = host
        self.user = user
        self.passw = passw
        self.db = db

        try:
            self.mydb = mc.connect(
                host=host,
                user=user,
                passwd=passw
            )

            self.cursor = self.mydb.cursor()
        except mc.Error as e:
            print("Erro ao conectar a Base de Dados!")
            return

        self.createdatabase()

    def createdatabase(self):
        dblist = self.cursor("SHOW DATABASES")

        if self.db not in dblist:
            self.cursor.execute("CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(self.db))
            return True
        else:
            return False


if __name__ == '__main__':
    app = QApplication(sys.argv)

    helloPythonWidget = Empresa()
    helloPythonWidget.show()
    sys.exit(app.exec_())
