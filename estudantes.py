# -*- coding: latin-1 -*-
"""
Created on Fri Mar 02 23:18:43 2012

@author: lims
"""

import sys

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

# import psycopg2 as pg
import sqlite3 as lite

SEXO = ["Masculino", "Femenino"]
TIPO_DOC = ["BI", "DIRE", "PASSAPORTE", "CARTA DE CONDUCAO", "OUTRO"]
PAISES = [
    "�frica do Sul",
    "Akrotiri",
    "Alb�nia",
    "Alemanha",
    "Andorra",
    "Angola",
    "Anguila",
    "Ant�rctida ",
    "Ant�gua e Barbuda ",
    "Antilhas Neerlandesas ",
    "Ar�bia Saudita ",
    "Arctic Ocean ",
    "Arg�lia ",
    "Argentina ",
    "Arm�nia ",
    "Aruba ",
    "Ashmore and Cartier Islands ",
    "Atlantic Ocean ",
    "Austr�lia ",
    "�ustria ",
    "Azerbaij�o ",
    "Baamas ",
    "Bangladeche ",
    "Barbados ",
    "Bar�m ",
    "B�lgica ",
    "Belize ",
    "Benim ",
    "Bermudas ",
    "Bielorr�ssia ",
    "Birm�nia ",
    "Bol�via ",
    "B�snia e Herzegovina ",
    "Botsuana ",
    "Brasil ",
    "Brunei ",
    "Bulg�ria ",
    "Burquina Faso ",
    "Bur�ndi ",
    "But�o ",
    "Cabo Verde ",
    "Camar�es ",
    "Camboja ",
    "Canad� ",
    "Catar ",
    "Cazaquist�o ",
    "Chade ",
    "Chile ",
    "China ",
    "Chipre ",
    "Clipperton Island ",
    "Col�mbia ",
    "Comores ",
    "Congo-Brazzaville ",
    "Congo-Kinshasa ",
    "Coral Sea Islands ",
    "Coreia do Norte ",
    "Coreia do Sul ",
    "Costa do Marfim ",
    "Costa Rica ",
    "Cro�cia ",
    "Cuba ",
    "Dhekelia ",
    "Dinamarca ",
    "Dom�nica ",
    "Egipto ",
    "Emiratos �rabes Unidos ",
    "Equador ",
    "Eritreia ",
    "Eslov�quia ",
    "Eslov�nia ",
    "Espanha ",
    "Estados Unidos ",
    "Est�nia ",
    "Eti�pia ",
    "Faro� ",
    "Fiji ",
    "Filipinas ",
    "Finl�ndia ",
    "Fran�a ",
    "Gab�o ",
    "G�mbia ",
    "Gana ",
    "Gaza Strip ",
    "Ge�rgia ",
    "Ge�rgia do Sul e Sandwich do Sul ",
    "Gibraltar ",
    "Granada ",
    "Gr�cia ",
    "Gronel�ndia ",
    "Guame ",
    "Guatemala ",
    "Guernsey ",
    "Guiana ",
    "Guin� ",
    "Guin� Equatorial ",
    "Guin�-Bissau ",
    "Haiti ",
    "Honduras ",
    "Hong Kong ",
    "Hungria ",
    "I�men ",
    "Ilha Bouvet ",
    "Ilha do Natal ",
    "Ilha Norfolk ",
    "Ilhas Caim�o ",
    "Ilhas Cook ",
    "Ilhas dos Cocos ",
    "Ilhas Falkland ",
    "Ilhas Heard e McDonald ",
    "Ilhas Marshall ",
    "Ilhas Salom�o ",
    "Ilhas Turcas e Caicos ",
    "Ilhas Virgens Americanas ",
    "Ilhas Virgens Brit�nicas ",
    "�ndia ",
    "Indian Ocean ",
    "Indon�sia ",
    "Ir�o ",
    "Iraque ",
    "Irlanda ",
    "Isl�ndia ",
    "Israel ",
    "It�lia ",
    "Jamaica",
    "Jan Mayen ",
    "Jap�o ",
    "Jersey ",
    "Jibuti ",
    "Jord�nia ",
    "Kuwait ",
    "Laos ",
    "Lesoto ",
    "Let�nia ",
    "L�bano ",
    "Lib�ria ",
    "L�bia ",
    "Listenstaine ",
    "Litu�nia ",
    "Luxemburgo ",
    "Macau ",
    "Maced�nia ",
    "Madag�scar ",
    "Mal�sia ",
    "Mal�vi ",
    "Maldivas ",
    "Mali ",
    "Malta ",
    "Man, Isle of ",
    "Marianas do Norte ",
    "Marrocos ",
    "Maur�cia ",
    "Maurit�nia ",
    "Mayotte ",
    "M�xico ",
    "Micron�sia ",
    "Mo�ambique ",
    "Mold�via ",
    "M�naco ",
    "Mong�lia ",
    "Monserrate ",
    "Montenegro ",
    "Mundo ",
    "Nam�bia ",
    "Nauru ",
    "Navassa Island ",
    "Nepal ",
    "Nicar�gua ",
    "N�ger ",
    "Nig�ria ",
    "Niue ",
    "Noruega ",
    "Nova Caled�nia ",
    "Nova Zel�ndia ",
    "Om� ",
    "Pacific Ocean ",
    "Pa�ses Baixos ",
    "Palau ",
    "Panam� ",
    "Papua-Nova Guin� ",
    "Paquist�o ",
    "Paracel Islands ",
    "Paraguai ",
    "Peru ",
    "Pitcairn ",
    "Polin�sia Francesa ",
    "Pol�nia ",
    "Porto Rico ",
    "Portugal ",
    "Qu�nia ",
    "Quirguizist�o ",
    "Quirib�ti ",
    "Reino Unido ",
    "Rep�blica Centro-Africana ",
    "Rep�blica Checa ",
    "Rep�blica Dominicana ",
    "Rom�nia ",
    "Ruanda ",
    "R�ssia ",
    "Salvador ",
    "Samoa ",
    "Samoa Americana ",
    "Santa Helena ",
    "Santa L�cia ",
    "S�o Crist�v�o e Neves ",
    "S�o Marinho ",
    "S�o Pedro e Miquelon ",
    "S�o Tom� e Pr�ncipe ",
    "S�o Vicente e Granadinas ",
    "Sara Ocidental ",
    "Seicheles ",
    "Senegal ",
    "Serra Leoa ",
    "S�rvia ",
    "Singapura ",
    "S�ria ",
    "Som�lia ",
    "Southern Ocean ",
    "Spratly Islands ",
    "Sri Lanca ",
    "Suazil�ndia ",
    "Sud�o ",
    "Su�cia ",
    "Su��a ",
    "Suriname ",
    "Svalbard e Jan Mayen ",
    "Tail�ndia ",
    "Taiwan ",
    "Tajiquist�o ",
    "Tanz�nia ",
    "Territ�rio Brit�nico do Oceano �ndico ",
    "Territ�rios Austrais Franceses ",
    "Timor Leste ",
    "Togo ",
    "Tokelau ",
    "Tonga ",
    "Trindade e Tobago ",
    "Tun�sia ",
    "Turquemenist�o ",
    "Turquia ",
    "Tuvalu ",
    "Ucr�nia ",
    "Uganda ",
    "Uni�o Europeia ",
    "Uruguai ",
    "Usbequist�o ",
    "Vanuatu ",
    "Vaticano ",
    "Venezuela ",
    "Vietname ",
    "Wake Island",
    "Wallis e Futuna",
    "West Bank",
    "Z�mbia",
    "Zimbabu�"]

from utilities import codigo


class Estudante(QDialog):

    def __init__(self, parent=None):
        super(Estudante, self).__init__(parent)

        # controla o codigo
        self.current_id = ""
        self.fotofile = ""
        self.codEmpresa = ""
        self.nomeEmpresa = ""

        # Connect the Database
        if self.parent() is None:
            self.db = self.connect_db()
            self.user = ""
        else:
            self.conn = self.parent().conn
            self.cur = self.parent().cur
            self.user = self.parent().user

        self.update_data = False
        self.accoes()
        self.ui()
        self.enche_empresas()

    def ui(self):
        html = """<center style= "background-image: './images/control.png'" > <h2 > Cadastro de Estudantes </h2> </center> """

        titulo = QLabel(html)
        cod = QLabel("Codigo")
        nome = QLabel("Primeiros nomes")
        apelido = QLabel("Apelido")
        endereco = QLabel("Endere�o")
        sexo = QLabel("Sexo")
        email = QLabel("Email")
        nascimento = QLabel("Data de nascimento")
        contacto = QLabel("Contactos")
        emergencia = QLabel("Contactos de Emerg�ncia")
        tipo = QLabel("Tipo de Identifica��o")
        numero = QLabel("N�mero do documento")
        nacionalidade = QLabel("Pa�s")
        validade = QLabel("Validade do documento")
        obs = QLabel("Observa��es")

        calendario = QCalendarWidget()
        calendario1 = QCalendarWidget()

        self.cod = QLineEdit()
        self.cod.setMaximumWidth(140)
        self.cod.setObjectName("cod")
        self.cod.setAlignment(Qt.AlignRight)
        self.cod.setEnabled(False)
        self.nome = QLineEdit()
        self.empresa = QComboBox()
        self.empresa.currentIndexChanged.connect(lambda: self.get_cod_empresa(self.empresa.currentText()))
        self.apelido = QLineEdit()
        self.endereco = QLineEdit()
        self.sexo = QComboBox()
        self.sexo.setMaximumWidth(140)
        self.sexo.addItems(SEXO)
        self.email = QLineEdit()
        self.nascimento = QDateEdit()
        self.nascimento.setDate(QDate.currentDate())
        self.nascimento.setObjectName("cal1")
        self.nascimento.setCalendarPopup(True)
        self.nascimento.setCalendarWidget(calendario)
        self.nascimento.setMaximumWidth(140)
        self.nascimento.setAlignment(Qt.AlignRight)
        self.contacto = QLineEdit()
        self.emergencia = QLineEdit()
        self.tipo = QComboBox()
        self.tipo.setMaximumWidth(140)
        self.tipo.addItems(TIPO_DOC)
        self.numero = QLineEdit()
        self.numero.setMaximumWidth(140)
        self.numero.setMaxLength(15)
        self.numero.setAlignment(Qt.AlignRight)
        self.nacionalidade = QComboBox()
        self.nacionalidade.setMaximumWidth(280)
        lista = QStringListModel()
        lista.setStringList(PAISES)
        self.nacionalidade.setModel(lista)

        self.validade = QDateEdit()
        self.validade.setDate(QDate.currentDate())
        self.validade.setCalendarPopup(True)
        self.validade.setCalendarWidget(calendario1)
        self.validade.setObjectName("cal2")
        self.validade.setMaximumWidth(140)
        self.validade.setAlignment(Qt.AlignRight)
        self.obs = QTextEdit()

        self.foto = QLabel()
        self.foto.setFixedSize(256, 256)
        self.adicionarfoto = QPushButton(QIcon("./icons/add.ico"), "Seleccionar foto")
        self.adicionarfoto.setAutoDefault(False)
        self.adicionarfoto.clicked.connect(self.selecionar_foto)
        self.removefoto = QPushButton(QIcon("./icons/remove.ico"), "Remover Foto")
        self.removefoto.setAutoDefault(False)
        self.removefoto.clicked.connect(self.remover_foto)
        self.fotodialog = QFileDialog(self, "Seleccionar Foto")

        buttonslayout = QHBoxLayout()

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)

        spacer1 = QWidget()
        spacer1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)

        spacer2 = QWidget()
        spacer2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)

        fotoframe = QGroupBox()
        fotoframe.setMaximumSize(256, 256)
        foto_layout = QHBoxLayout()
        foto_layout.setContentsMargins(0, 0, 0, 0)
        foto_layout.addWidget(self.foto)
        fotoframe.setLayout(foto_layout)
        fotoframe.setContentsMargins(0, 0, 0, 0)

        fotolay = QHBoxLayout()

        fotolay.addWidget(spacer1)
        fotolay.addWidget(fotoframe)
        fotolay.addWidget(spacer2)

        buttonslayout.addWidget(spacer)
        buttonslayout.addWidget(self.adicionarfoto)
        buttonslayout.addWidget(self.removefoto)

        fotolayout = QVBoxLayout()
        fotolayout.addLayout(fotolay)
        fotolayout.addLayout(buttonslayout)

        # Grade da Foto
        fotogrid = QGroupBox("FOTO")
        fotogrid.setLayout(fotolayout)

        grid = QFormLayout()

        grid.addRow(nome, self.nome)
        grid.addRow(apelido, self.apelido)
        grid.addRow(QLabel("Empresa"), self.empresa)
        grid.addRow(endereco, self.endereco)
        grid.addRow(sexo, self.sexo)
        grid.addRow(email, self.email)
        grid.addRow(nascimento, self.nascimento)
        grid.addRow(contacto, self.contacto)
        grid.addRow(emergencia, self.emergencia)
        grid.addRow(tipo, self.tipo)
        grid.addRow(numero, self.numero)
        grid.addRow(validade, self.validade)
        grid.addRow(nacionalidade, self.nacionalidade)
        grid.addRow(obs, self.obs)

        vLay = QVBoxLayout(self)
        vLay.setContentsMargins(0, 0, 0, 0)

        cLay = QVBoxLayout()
        cLay.setContentsMargins(10, 10, 10, 10)

        cLay.addLayout(grid)
        data_grid = QWidget()
        data_grid.setLayout(cLay)

        self.stack = QStackedWidget()
        self.stack.addWidget(data_grid)
        self.stack.addWidget(fotogrid)

        self.stack_button = QPushButton("FOTO")
        self.stack_button.clicked.connect(self.foto_dados)

        vLay.addWidget(titulo)
        vLay.addWidget(self.stack)
        vLay.addWidget(self.stack_button)
        vLay.addWidget(self.tool)

        self.setLayout(vLay)

        self.setWindowTitle("Cadastro de Estudantes")

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

        style2 = """
            QDialog{margin: 0;
        	padding: 0;
            border-image:url(./images/aqua.JPG) 30 30 stretch;
            background:#C0C0CC;
        	font-family: Arial, Helvetica, sans-serif;
        	font-size: 12px;
        	color: #FFFFFF;}
        """

    def enche_empresas(self):
        sql = """SELECT nome FROM clientes ORDER BY nome"""
        self.cur.execute(sql)

        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                self.empresa.addItem(item[0])

            return True

        return False

    def get_cod_empresa(self, nome):
        sql = """SELECT cod FROM clientes WHERE nome="{nome}" """.format(nome=nome)
        self.cur.execute(sql)

        data = self.cur.fetchall()

        if len(data) > 0:
            self.codEmpresa = data[0][0]
            return True

        return False

    def get_nome_empresa(self, codigo):
        sql = """SELECT nome FROM clientes WHERE cod="{cod}" """.format(cod=codigo)
        self.cur.execute(sql)

        data = self.cur.fetchall()

        if len(data) > 0:
            self.nomeEmpresa = data[0][0]
            return self.nomeEmpresa

        return ""

    def foto_dados(self):
        if self.stack_button.text() == "FOTO":
            self.stack.setCurrentIndex(1)
            self.stack_button.setText("DADOS")
        else:
            self.stack.setCurrentIndex(0)
            self.stack_button.setText("FOTO")

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

        self.mostrarfoto(caminho)

    def mostrarfoto(self, foto):

        pixmap = QPixmap(foto)
        pixmap.scaled(64, 64, Qt.KeepAspectRatio)
        self.foto.setPixmap(pixmap)
        self.foto.setScaledContents(True)
        self.foto.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.fotofile = foto

        return foto

    def remover_foto(self):
        self.fotofile = ""
        self.foto.setPixmap(QPixmap(""))

    def connect_db(self):
        pass

    def accoes(self):
        self.tool = QToolBar()
        self.tool.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.tool.setContextMenuPolicy(Qt.PreventContextMenu)

        gravar = QAction(QIcon("./images/ok.png"), "Gravar\nDados", self)
        eliminar = QAction(QIcon("icons/new.ico"), "Limpar\nCampos", self)

        fechar = QAction(QIcon("./images/filequit.png"), "&Fechar", self)

        self.tool.addAction(gravar)
        self.tool.addAction(eliminar)

        self.tool.addSeparator()
        self.tool.addAction(fechar)

        gravar.triggered.connect(self.addRecord)
        eliminar.triggered.connect(self.limpar)
        fechar.triggered.connect(self.fechar)
        
    def fechar(self):
        self.close()

    def limpar(self):
        for child in (self.findChildren(QLineEdit) or self.findChildren(QTextEdit)):
            if child.objectName() not in ["cod", "cal1", "cal2"]: child.clear()

        # gera novo codigo para estudantes
        from utilities import codigo
        self.cod.setText("CL" + codigo("OPQRSTUVXYWZ0123456789"))

    def connectdb(self):

        self.conn = lite.connect('./db/maindb.db')
        self.cursor = self.conn.cursor()
        self.incrementa()
        self.conn.commit()

    def validacao(self):

        if str(self.nome.text()) == "":
            QMessageBox.warning(self, "Erro", "Nome do Estudante inv�lido")
            self.nome.setFocus()
            return False
        else:
            return True

    def mostrar_registo(self):

        sql = """SELECT * FROM estudantes where cod ="{}" """.format(self.current_id)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                self.nome.setText(item[1])
                self.apelido.setText(item[2])
                self.endereco.setText(item[3])
                self.sexo.setCurrentText(item[4])
                self.email.setText(item[5])
                self.nascimento.setDate(QDate.fromString(item[6]))
                self.contacto.setText(item[7])
                self.emergencia.setText(item[8])
                self.tipo.setCurrentText(item[9])
                self.numero.setText(item[10])
                self.validade.setDate(QDate.fromString(item[11]))
                self.nacionalidade.setCurrentIndex(self.nacionalidade.findText(item[12]))
                self.obs.setPlainText(item[13])

                try:
                    self.fotofile = ''.join(data[0][19])
                    self.mostrarfoto(self.fotofile)
                except Exception as e:
                    self.foto.setPixmap(QPixmap(''))

                nome = self.get_nome_empresa(data[0][20])
                self.empresa.setCurrentText(nome)

            return True

        return False

    def existe(self, codigo):

        sql = """SELECT cod from estudantes WHERE cod = "{codigo}" """.format(codigo=str(codigo))

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

    def addRecord(self):

        if self.validacao() == True:
            nome = self.nome.text()
            apelido = self.apelido.text()
            endereco = self.endereco.text()
            sexo = self.sexo.currentText()
            email = self.email.text()
            nascimento = self.nascimento.date().toString("yyyy-MM-dd")
            contactos = self.contacto.text()
            emergencia = self.emergencia.text()
            tipo_id = self.tipo.currentText()
            numero_id = self.numero.text()
            nacionalidade = self.nacionalidade.currentText()
            validade_id = self.validade.date().toString("yyyy-MM-dd")
            obs = self.obs.toPlainText()
            estado = 1
            created = QDate.currentDate().toString("yyyy-MM-dd")
            modified = QDate.currentDate().toString("yyyy-MM-dd")
            modified_by = self.user
            created_by = self.user
            foto = self.fotofile
            empresa = self.codEmpresa

            if self.current_id == "":
                self.current_id = "HS" + codigo("HS" + "abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")

            code = self.current_id

            if self.existe(code):

                sql = """UPDATE estudantes SET nome="{nome}", apelido="{apelido}", endereco="{endereco}", sexo="{sexo}",
                                email="{email}", nascimento="{nascimento}", contactos="{contactos}", emergencia="{emergencia}", 
                                tipo_id="{tipo_id}", numero_id="{numero_id}", validade_id="{validade_id}", 
                                nacionalidade="{nacionalidade}", obs="{obs}", estado={estado}, created="{created}", 
                                modified="{modified}", modified_by="{modified_by}", 
                                created_by="{created_by}", foto="{foto}", empresa="{empresa}" WHERE cod="{cod}" """.format(
                    nome=nome, apelido=apelido,
                    endereco=endereco, sexo=sexo,
                    email=email,
                    nascimento=nascimento,
                    contactos=contactos,
                    emergencia=emergencia,
                    tipo_id=tipo_id,
                    numero_id=numero_id,
                    validade_id=validade_id,
                    nacionalidade=nacionalidade,
                    obs=obs, estado=estado,
                    created=created,
                    modified=modified,
                    modified_by=modified_by,
                    created_by=created_by,
                    foto=foto, cod=code,
                    empresa=empresa)


            else:
                values = """ "{cod}", "{nome}", "{apelido}", "{endereco}", "{sexo}", "{email}", "{nascimento}", 
                                "{contactos}", "{emergencia}", "{tipo_id}", "{numero_id}", "{validade_id}", 
                                "{nacionalidade}", "{obs}", {estado}, "{created}", "{modified}",
                                "{modified_by}", "{created_by}", "{foto}", "{empresa}" """.format(cod=code, nome=nome, apelido=apelido,
                                                                           endereco=endereco,
                                                                           sexo=sexo, email=email,
                                                                           nascimento=nascimento,
                                                                           contactos=contactos, emergencia=emergencia,
                                                                           tipo_id=tipo_id, numero_id=numero_id,
                                                                           validade_id=validade_id,
                                                                           nacionalidade=nacionalidade,
                                                                           obs=obs, estado=estado, created=created,
                                                                           modified=modified, modified_by=modified_by,
                                                                           created_by=created_by, foto=foto,
                                                                                                  empresa=empresa)

                sql = """INSERT INTO estudantes VALUES ({}) """.format(values)

            try:
                self.cur.execute(sql)
                self.conn.commit()

                if QMessageBox.question(self, "Pergunta", "Registo Gravado com sucesso!\nDeseja Cadastrar outro Item?",
                                        QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                    self.limpar()
                else:
                    self.close()

                return True
            except Exception as e:
                self.conn.rollback()
                print(e)
                return False

    def closeEvent(self, evt):
        if self.parent() is not None:
            self.parent().fill_table()


if __name__ == '__main__':

    app = QApplication(sys.argv)
#
    helloPythonWidget = Estudante()
    helloPythonWidget.show()
#
    sys.exit(app.exec_())