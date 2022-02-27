# -*- coding: latin-1 -*-
"""
Created on Fri Mar 02 23:18:43 2012

@author: lims
"""

import sys

from PyQt5.QtSql import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

# import psycopg2 as pg
import sqlite3 as lite

SEXO = ["Masculino", "Femenino"]
TIPO_DOC = ["BI", "DIRE", "PASSAPORTE", "CARTA DE CONDUCAO", "OUTRO"]
PAISES = [
    "África do Sul",
    "Akrotiri",
    "Albânia",
    "Alemanha",
    "Andorra",
    "Angola",
    "Anguila",
    "Antárctida ",
    "Antígua e Barbuda ",
    "Antilhas Neerlandesas ",
    "Arábia Saudita ",
    "Arctic Ocean ",
    "Argélia ",
    "Argentina ",
    "Arménia ",
    "Aruba ",
    "Ashmore and Cartier Islands ",
    "Atlantic Ocean ",
    "Austrália ",
    "Áustria ",
    "Azerbaijão ",
    "Baamas ",
    "Bangladeche ",
    "Barbados ",
    "Barém ",
    "Bélgica ",
    "Belize ",
    "Benim ",
    "Bermudas ",
    "Bielorrússia ",
    "Birmânia ",
    "Bolívia ",
    "Bósnia e Herzegovina ",
    "Botsuana ",
    "Brasil ",
    "Brunei ",
    "Bulgária ",
    "Burquina Faso ",
    "Burúndi ",
    "Butão ",
    "Cabo Verde ",
    "Camarões ",
    "Camboja ",
    "Canadá ",
    "Catar ",
    "Cazaquistão ",
    "Chade ",
    "Chile ",
    "China ",
    "Chipre ",
    "Clipperton Island ",
    "Colômbia ",
    "Comores ",
    "Congo-Brazzaville ",
    "Congo-Kinshasa ",
    "Coral Sea Islands ",
    "Coreia do Norte ",
    "Coreia do Sul ",
    "Costa do Marfim ",
    "Costa Rica ",
    "Croácia ",
    "Cuba ",
    "Dhekelia ",
    "Dinamarca ",
    "Domínica ",
    "Egipto ",
    "Emiratos Árabes Unidos ",
    "Equador ",
    "Eritreia ",
    "Eslováquia ",
    "Eslovénia ",
    "Espanha ",
    "Estados Unidos ",
    "Estónia ",
    "Etiópia ",
    "Faroé ",
    "Fiji ",
    "Filipinas ",
    "Finlândia ",
    "França ",
    "Gabão ",
    "Gâmbia ",
    "Gana ",
    "Gaza Strip ",
    "Geórgia ",
    "Geórgia do Sul e Sandwich do Sul ",
    "Gibraltar ",
    "Granada ",
    "Grécia ",
    "Gronelândia ",
    "Guame ",
    "Guatemala ",
    "Guernsey ",
    "Guiana ",
    "Guiné ",
    "Guiné Equatorial ",
    "Guiné-Bissau ",
    "Haiti ",
    "Honduras ",
    "Hong Kong ",
    "Hungria ",
    "Iémen ",
    "Ilha Bouvet ",
    "Ilha do Natal ",
    "Ilha Norfolk ",
    "Ilhas Caimão ",
    "Ilhas Cook ",
    "Ilhas dos Cocos ",
    "Ilhas Falkland ",
    "Ilhas Heard e McDonald ",
    "Ilhas Marshall ",
    "Ilhas Salomão ",
    "Ilhas Turcas e Caicos ",
    "Ilhas Virgens Americanas ",
    "Ilhas Virgens Britânicas ",
    "Índia ",
    "Indian Ocean ",
    "Indonésia ",
    "Irão ",
    "Iraque ",
    "Irlanda ",
    "Islândia ",
    "Israel ",
    "Itália ",
    "Jamaica",
    "Jan Mayen ",
    "Japão ",
    "Jersey ",
    "Jibuti ",
    "Jordânia ",
    "Kuwait ",
    "Laos ",
    "Lesoto ",
    "Letónia ",
    "Líbano ",
    "Libéria ",
    "Líbia ",
    "Listenstaine ",
    "Lituânia ",
    "Luxemburgo ",
    "Macau ",
    "Macedónia ",
    "Madagáscar ",
    "Malásia ",
    "Malávi ",
    "Maldivas ",
    "Mali ",
    "Malta ",
    "Man, Isle of ",
    "Marianas do Norte ",
    "Marrocos ",
    "Maurícia ",
    "Mauritânia ",
    "Mayotte ",
    "México ",
    "Micronésia ",
    "Moçambique ",
    "Moldávia ",
    "Mónaco ",
    "Mongólia ",
    "Monserrate ",
    "Montenegro ",
    "Mundo ",
    "Namíbia ",
    "Nauru ",
    "Navassa Island ",
    "Nepal ",
    "Nicarágua ",
    "Níger ",
    "Nigéria ",
    "Niue ",
    "Noruega ",
    "Nova Caledónia ",
    "Nova Zelândia ",
    "Omã ",
    "Pacific Ocean ",
    "Países Baixos ",
    "Palau ",
    "Panamá ",
    "Papua-Nova Guiné ",
    "Paquistão ",
    "Paracel Islands ",
    "Paraguai ",
    "Peru ",
    "Pitcairn ",
    "Polinésia Francesa ",
    "Polónia ",
    "Porto Rico ",
    "Portugal ",
    "Quénia ",
    "Quirguizistão ",
    "Quiribáti ",
    "Reino Unido ",
    "República Centro-Africana ",
    "República Checa ",
    "República Dominicana ",
    "Roménia ",
    "Ruanda ",
    "Rússia ",
    "Salvador ",
    "Samoa ",
    "Samoa Americana ",
    "Santa Helena ",
    "Santa Lúcia ",
    "São Cristóvão e Neves ",
    "São Marinho ",
    "São Pedro e Miquelon ",
    "São Tomé e Príncipe ",
    "São Vicente e Granadinas ",
    "Sara Ocidental ",
    "Seicheles ",
    "Senegal ",
    "Serra Leoa ",
    "Sérvia ",
    "Singapura ",
    "Síria ",
    "Somália ",
    "Southern Ocean ",
    "Spratly Islands ",
    "Sri Lanca ",
    "Suazilândia ",
    "Sudão ",
    "Suécia ",
    "Suíça ",
    "Suriname ",
    "Svalbard e Jan Mayen ",
    "Tailândia ",
    "Taiwan ",
    "Tajiquistão ",
    "Tanzânia ",
    "Território Britânico do Oceano Índico ",
    "Territórios Austrais Franceses ",
    "Timor Leste ",
    "Togo ",
    "Tokelau ",
    "Tonga ",
    "Trindade e Tobago ",
    "Tunísia ",
    "Turquemenistão ",
    "Turquia ",
    "Tuvalu ",
    "Ucrânia ",
    "Uganda ",
    "União Europeia ",
    "Uruguai ",
    "Usbequistão ",
    "Vanuatu ",
    "Vaticano ",
    "Venezuela ",
    "Vietname ",
    "Wake Island",
    "Wallis e Futuna",
    "West Bank",
    "Zâmbia",
    "Zimbabué"]

from utilities import codigo


class Aluno(QDialog):

    def __init__(self, parent=None):
        super(Aluno, self).__init__(parent)

        # controla o codigo
        self.current_id = ""
        self.fotofile = ""

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

    def ui(self):
        html = """<center style= "background-image: './images/control.png'" > <h2 > Cadastro de Alunos </h2> </center> """

        titulo = QLabel(html)
        cod = QLabel("Codigo")
        nome = QLabel("Primeiros nomes")
        apelido = QLabel("Apelido")
        endereco = QLabel("Endereço")
        sexo = QLabel("Sexo")
        email = QLabel("Email")
        nascimento = QLabel("Data de nascimento")
        contacto = QLabel("Contactos")
        emergencia = QLabel("Contactos de Emergência")
        tipo = QLabel("Tipo de Identificação")
        numero = QLabel("Número do documento")
        nacionalidade = QLabel("País")
        validade = QLabel("Validade do documento")
        obs = QLabel("Observações")

        calendario = QCalendarWidget()
        calendario1 = QCalendarWidget()

        self.cod = QLineEdit()
        self.cod.setMaximumWidth(140)
        self.cod.setObjectName("cod")
        self.cod.setAlignment(Qt.AlignRight)
        self.cod.setEnabled(False)
        self.nome = QLineEdit()
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

        self.setWindowTitle("Cadastro de Alunos")

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

        # gera novo codigo para alunos
        from utilities import codigo
        self.cod.setText("CL" + codigo("OPQRSTUVXYWZ0123456789"))

    def connectdb(self):

        self.conn = lite.connect('./db/maindb.db')
        self.cursor = self.conn.cursor()
        self.incrementa()
        self.conn.commit()

    def validacao(self):

        if str(self.nome.text()) == "":
            QMessageBox.warning(self, "Erro", "Nome do Aluno inválido")
            self.nome.setFocus()
            return False
        else:
            return True

    def mostrar_registo(self):

        sql = """SELECT * FROM alunos """
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
                pixmap = QPixmap(item[19])
                pixmap.scaled(64, 64, Qt.KeepAspectRatio)
                self.foto.setPixmap(pixmap)

                try:
                    self.mostrarfoto(''.join(data[0][19]))
                except Exception as e:
                    self.foto.setPixmap(QPixmap(''))

            return True

        return False

    def existe(self, codigo):

        sql = """SELECT cod from alunos WHERE cod = "{codigo}" """.format(codigo=str(codigo))

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
            modified_by = "User"
            created_by = "User"
            foto = self.fotofile

            if self.current_id == "":
                self.current_id = "HS" + codigo("HS" + "abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")

            code = self.current_id

            if self.existe(code):

                sql = """UPDATE alunos SET nome="{nome}", apelido="{apelido}", endereco="{endereco}", sexo="{sexo}",
                                email="{email}", nascimento="{nascimento}", contactos="{contactos}", emergencia="{emergencia}", 
                                tipo_id="{tipo_id}", numero_id="{numero_id}", validade_id="{validade_id}", 
                                nacionalidade="{nacionalidade}", obs="{obs}", estado={estado}, created="{created}", 
                                modified="{modified}", modified_by="{modified_by}", 
                                created_by="{created_by}", foto="{foto}" WHERE cod="{cod}" """.format(nome=nome, apelido=apelido,
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
                                                                                                      foto=foto, cod=code)


            else:
                values = """ "{cod}", "{nome}", "{apelido}", "{endereco}", "{sexo}", "{email}", "{nascimento}", 
                                "{contactos}", "{emergencia}", "{tipo_id}", "{numero_id}", "{validade_id}", 
                                "{nacionalidade}", "{obs}", {estado}, "{created}", "{modified}",
                                "{modified_by}", "{created_by}", "{foto}" """.format(cod=code, nome=nome, apelido=apelido,
                                                                           endereco=endereco,
                                                                           sexo=sexo, email=email,
                                                                           nascimento=nascimento,
                                                                           contactos=contactos, emergencia=emergencia,
                                                                           tipo_id=tipo_id, numero_id=numero_id,
                                                                           validade_id=validade_id,
                                                                           nacionalidade=nacionalidade,
                                                                           obs=obs, estado=estado, created=created,
                                                                           modified=modified, modified_by=modified_by,
                                                                           created_by=created_by, foto=foto)

                sql = """INSERT INTO alunos VALUES ({}) """.format(values)

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
    helloPythonWidget = Aluno()
    helloPythonWidget.show()
#
    sys.exit(app.exec_())