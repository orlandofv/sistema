# -*- coding: utf-8 -*-

import sys
import datetime
import time
import random
from pathlib import Path
import subprocess, platform
import decimal
import os
from time import strftime, localtime, ctime

from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QSizePolicy
import serial
from win32com import client

DARK_BLUE = "./Styles/dark-blue.qss"
DARK_GREEN = "./Styles/dark-green.qss"
DARK_ORANGE = "./Styles/dark-orange.qss"
LIGHT_BLUE = "./Styles/light-blue.qss"
LIGHT_GREEN = "./Styles/light-green.qss"
LIGHT_ORANGE = "./Styles/light-orange.qss"
DARK_STYLE = "./Styles/dark.qss"
NORMAL = "./Styles/normal.qss"

SEXO = ["Masculino","Femenino"]

TIPO_DOC = ["BI","DIRE","PASSAPORTE","CARTA DE CONDUCAO","OUTRO"]

UNIDADE = ["Un", "Kg", "L", "m", "Gb", "Tb", "Cm", "Mb", "Outro"]


from ppadb.client import Client as AdbClient
# Default is "127.0.0.1" and 5037

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

# Funções importantes de Datas
DATA_HORA_FORMATADA = strftime("%d-%m-%Y %H:%M:%S", localtime())
# DATA_HORA_FORMATADA_MYSQL = strftime("%Y-%m-%d %H:%M:%S", localtime())
DATA_HORA_FORMATADA_MYSQL = strftime("%Y-%m-%d", localtime())
DATA_ACTUAL = datetime.date.today()
ANO_ACTUAL = DATA_ACTUAL.year
DIA = DATA_ACTUAL.day
MES = DATA_ACTUAL.month
HORA = ctime()

def connect_android_device(serial: str, host="127.0.0.1", port=5037):
    """
    :param serial: Serial Number of Android Device
    :param host: host IP address. Default is "127.0.0.1"
    :param port: port number. Default is 5037
    :return: device
    """
    # Default is "127.0.0.1" and 5037
    client = AdbClient(host, port)
    device = client.device(serial)

    return device


class SendTextSMS:
    """
    Sends SMS to recipient\n
    USAGE:\n
    sms = SendTextSMS("xxxxxxxx", "Important!")\n
    sms.connectPhone()\n
    sms.sendMessage()\n
    sms.disconnectPhone()\n
    print("message sent successfully") \n
    """

    def __init__(self, recipient="xxxxxxxx", message="TextMessage.content not set."):
        self.recipient = recipient
        self.content = message

    def set_recipient(self, number):
        self.recipient = number

    def set_content(self, message):
        self.content = message

    def connect_phone(self):
        self.ser = serial.Serial('COM3', stopbits=1)
        time.sleep(2)

    def send_message(self):
        self.ser.write(b'ATZ\r')
        time.sleep(2)
        self.ser.write(b'AT+CMGF=1\r')
        time.sleep(2)

        self.ser.write('AT+CMGS={}\r'.format(self.recipient).encode())
        time.sleep(2)
        self.ser.write('{}\r'.format(self.content).encode())
        time.sleep(2)

        self.ser.write(chr(26).encode(encoding='utf8'))
        time.sleep(2)

    def disconnect_phone(self):
        self.ser.close()


class ReadTextSMS:
    """
    Reads SMS's from an usb/serial modem\n

    USAGE:\n
    sms = ReadTextSMS()\n
    sms.connect_phone()\n
    sms.read()\n
    sms.disconnect_phone()\n
    """

    def connect_phone(self):
        self.ser = serial.Serial('COM5', 9600, timeout=5)  # connect serial/usb port
        time.sleep(2)

    def read(self):
        self.ser.write('ATZ\r')
        time.sleep(2)
        self.ser.write('AT+CMGF=1\r')  # Put in Text Mode
        time.sleep(2)
        self.ser.write('AT+CMGL="ALL"\r')  # fetch all SMS's
        read = self.ser.readlines()
        i=0
        for msg in read:
            if 'CMGL' in msg:  # CMGL looks for all SMS Messages
                bvb = 'AT+CMGR={}'.format(str(i) + '\r')
                self.ser.write(bvb)  # Fetch all SMS's
                ead = self.ser.readlines()
                for x in ead:
                    print(x)
                    print(i)
                i += 1

    def disconnect_phone(self):
        self.ser.close()


def divide_sms(sms, n_caracteres):
    '''Divide SMS em n partes e coloca dentro da lista'''
    # Encontra o tamanho da String
    tamanho = len(sms)

    # Faz a divisao inteira
    divisao = tamanho // n_caracteres

    # Encontra o resto da divisao
    resto = tamanho % n_caracteres

    # Se a divisao for igual a zero so existe 1 sms
    if divisao == 0:
        n_sms = 1
    else:
        # Se o resto for maior que zero existe o remanescente da sms, acrescentamos 1 na divisao
        if resto > 0:
            n_sms = divisao + 1
        else:
            n_sms = divisao

    lista_sms = []

    for n in range(n_sms):
        print(n, ': ', sms[n*n_caracteres:n_caracteres*(n+1)])
        lista_sms.append(sms[n*n_caracteres:n_caracteres*(n+1)])

    return lista_sms


def stylesheet(file=1):
    try:
        if file == 1:
            FICHEIRO = open(DARK_BLUE, 'r')
        elif file == 2:
            FICHEIRO = open(DARK_GREEN, 'r')
        elif file == 3:
            FICHEIRO = open(DARK_ORANGE, 'r')
        elif file == 4:
            FICHEIRO = open(LIGHT_BLUE, 'r')
        elif file == 5:
            FICHEIRO = open(LIGHT_GREEN, 'r')
        elif file == 6:
            FICHEIRO = open(LIGHT_ORANGE, 'r')
        elif file == 7:
            FICHEIRO = open(DARK_STYLE, 'r')
        elif file == 0:
            FICHEIRO = open(NORMAL, 'r')
        else:
            return None

        STYLE = FICHEIRO.read()
        return STYLE
    except FileNotFoundError as e:
        print("Ficheiro não encontrado")
        return None

def pingOk(sHost):
    """ Funcao que test ping..."""
    try:
        output = subprocess.check_output("ping -{} 1 {}".format('n' if platform.system().lower()=="windows" else 'c',
                                                                sHost), shell=True)
    except Exception as e:
        output = None
        print("Sem Conexao. {}".format(e))

    return output


# Generates random codes function and appends to year+month+day
def codigo(codigo):

    code = (str(ANO_ACTUAL) + str(MES) + str(DIA)) + "".join(random.choice(codigo) for i in range(4))
    return code


def testa_caminho(file):
    if Path(file).is_file():
        return True
    else:
        return False

def readfile(filename):

    if testa_caminho(filename) == True:
        file = open(filename, "r")
        conteudo = file.read()
        file.close()

        return conteudo
    else:
        print("Ficheiro não existe")

def selecionar_foto(self):

    formats = "Todas as Imagens(*.bmp; *.jpg; *.png; *.ico)"
    self.path = "."

    dialog = QFileDialog(self)
    dialog.setOption(QFileDialog.DontUseNativeDialog, True)
    path = dialog.getOpenDB_FILENAME(self, "Escolha a Foto", self.path, formats)

    if path == "":
        caminho = ""
    else:
        caminho = path[0]

    return caminho

# Rotina que vai mostrar a foto do produto ou serviço,
# ele leva um file

def mostrarfoto(self, foto):
    caminho_legal = foto.replace("/", "\\")
    pixmap = QPixmap(caminho_legal)
    pixmap.scaled(64, 64, Qt.KeepAspectRatio)
    self.foto.setPixmap(pixmap)
    self.foto.setScaledContents(True)
    self.foto.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
    self.fotofile = caminho_legal


def remover_foto(self):
    self.fotofile = ""
    self.foto.setPixmap(QPixmap(""))


def enche_combobox(cursor, tabela, campo):
    """Enche a combobox tendo em conta o cursor da conexao, campo e a tabela em causa"""
    sql = """SELECT {} FROM {}""".format(campo, tabela)

    cursor.execute(sql)
    data = cursor.fetchall()

    lista = []
    if len(data) > 0:
        for x in data:
            lista.append(x[0])

    return lista

def enche_combobox_com_clausula(cursor, tabela, campo, clausula):
    """Enche a combobox tendo em conta o cursor da conexao, campo e a tabela em causa"""
    sql = """SELECT {} FROM {} WHERE {}""".format(campo, tabela, clausula)

    cursor.execute(sql)
    data = cursor.fetchall()

    lista = []
    if len(data) > 0:
        for x in data:
            lista.append(x[0])

    return lista


def get_printer_name_win32():
    strComputer = "."
    objWMIService = client.Dispatch("WbemScripting.SWbemLocator")
    objSWbemServices = objWMIService.ConnectServer(strComputer, "root\cimv2")
    colItems = objSWbemServices.ExecQuery("Select * from Win32_Printer")
    printers = []
    for objItem in colItems:
        printers.append(objItem.Name)
        # print("Attributes: ", objItem.Attributes)
        # print("Availability: ", objItem.Availability)
        # print("Available Job Sheets: ", objItem.AvailableJobSheets)
        # print("Average Pages Per Minute: ", objItem.AveragePagesPerMinute)
        # print("Capabilities: ", objItem.Capabilities)
        # print("Capability Descriptions: ", objItem.CapabilityDescriptions)
        # print("Caption: ", objItem.Caption)
        # print("Character Sets Supported: ", objItem.CharSetsSupported)
        # print("Comment: ", objItem.Comment)
        # print("Configuration Manager Error Code: ", objItem.ConfigManagerErrorCode)
        # print("Configuration Manager User Configuration: ", objItem.ConfigManagerUserConfig)
        # print("Creation Class Name: ", objItem.CreationClassName)
        # print("Current Capabilities: ", objItem.CurrentCapabilities)
        # print("Current Character Set: ", objItem.CurrentCharSet)
        # print("Current Language: ", objItem.CurrentLanguage)
        # print("Current MIME Type: ", objItem.CurrentMimeType)
        # print("Current Natural Language: ", objItem.CurrentNaturalLanguage)
        # print("Current Paper Type: ", objItem.CurrentPaperType)
        # print("Default: ", objItem.Default)
        # print("Default Capabilities: ", objItem.DefaultCapabilities)
        # print("Default Copies: ", objItem.DefaultCopies)
        # print("Default Language: ", objItem.DefaultLanguage)
        # print("Default MIME Type: ", objItem.DefaultMimeType)
        # print("Default Number Up: ", objItem.DefaultNumberUp)
        # print("Default Paper Type: ", objItem.DefaultPaperType)
        # print("Default Priority: ", objItem.DefaultPriority)
        # print("Description: ", objItem.Description)
        # print("Detected Error State: ", objItem.DetectedErrorState)
        # print("Device ID: ", objItem.DeviceID)
        # print("Direct: ", objItem.Direct)
        # print("Do Complete First: ", objItem.DoCompleteFirst)
        # print("Driver Name: ", objItem.DriverName)
        # print("Enable BIDI: ", objItem.EnableBIDI)
        # print("Enable Device Query Print: ", objItem.EnableDevQueryPrint)
        # print("Error Cleared: ", objItem.ErrorCleared)
        # print("Error Description: ", objItem.ErrorDescription)
        # print("Error Information: ", objItem.ErrorInformation)
        # print("Extended Detected Error State: ", objItem.ExtendedDetectedErrorState)
        # print("Extended Printer Status: ", objItem.ExtendedPrinterStatus)
        # print("Hidden: ", objItem.Hidden)
        # print("Horizontal Resolution: ", objItem.HorizontalResolution)
        # print("Installation Date: ", objItem.InstallDate)
        # print("Job Count Since Last Reset: ", objItem.JobCountSinceLastReset)
        # print("Keep Printed Jobs: ", objItem.KeepPrintedJobs)
        # print("Languages Supported: ", objItem.LanguagesSupported)
        # print("Last Error Code: ", objItem.LastErrorCode)
        # print("Local: ", objItem.Local)
        # print("Location: ", objItem.Location)
        # print("Marking Technology: ", objItem.MarkingTechnology)
        # print("Maximum Copies: ", objItem.MaxCopies)
        # print("Maximum Number Up: ", objItem.MaxNumberUp)
        # print("Maximum Size Supported: ", objItem.MaxSizeSupported)
        # print("MIME Types Supported: ", objItem.MimeTypesSupported)
        # print("Name: ", objItem.Name)
        # print("Natural Languages Supported: ", objItem.NaturalLanguagesSupported)
        # print("Network: ", objItem.Network)
        # print("Paper Sizes Supported: ", objItem.PaperSizesSupported)
        # print("Paper Types Available: ", objItem.PaperTypesAvailable)
        # print("Parameters: ", objItem.Parameters)
        # print("PNP Device ID: ", objItem.PNPDeviceID)
        # print("Port Name: ", objItem.PortName)
        # print("Power Management Capabilities: ", objItem.PowerManagementCapabilities)
        # print("Power Management Supported: ", objItem.PowerManagementSupported)
        # print("Printer Paper Names: ", objItem.PrinterPaperNames)
        # print("Printer State: ", objItem.PrinterState)
        # print("Printer Status: ", objItem.PrinterStatus)
        # print("Print Job Data Type: ", objItem.PrintJobDataType)
        # print("Print Processor: ", objItem.PrintProcessor)
        # print("Priority: ", objItem.Priority)
        # print("Published: ", objItem.Published)
        # print("Queued: ", objItem.Queued)
        # print("Raw-Only: ", objItem.RawOnly)
        # print("Separator File: ", objItem.SeparatorFile)
        # print("Server Name: ", objItem.ServerName)
        # print("Shared: ", objItem.Shared)
        # print("Share Name: ", objItem.ShareName)
        # print("Spool Enabled: ", objItem.SpoolEnabled)
        # print("Start Time: ", objItem.StartTime)
        # print("Status: ", objItem.Status)
        # print("Status Information: ", objItem.StatusInfo)
        # print("System Creation Class Name: ", objItem.SystemCreationClassName)
        # print("System Name: ", objItem.SystemName)
        # print("Time Of Last Reset: ", objItem.TimeOfLastReset)
        # print("Until Time: ", objItem.UntilTime)
        # print("Vertical Resolution: ", objItem.VerticalResolution)
        # print("Work Offline: ", objItem.WorkOffline)
        # print("==================================================================================================")

    return printers


def converte_para_pdf(caminho_python_do_libreoffice, ficheiro_entrada, ficheiro_saida):

    """
    # Converte o Ficheiro de odt para odf

    :param caminho_python_do_libreoffice: Caminho do Python na pasta de LibreOffice
    :param ficheiro_entrada: nome do ficheiro odf a ser convertido para pdf
    :param ficheiro_saida: nome do ficheiro pdf gerado apos a conversao
    :return: retorna True em caso de sucesso e False em caso de falha
    """

    saida = os.path.realpath(ficheiro_saida)

    try:
        # conv = unoconv.
        uniconv_pdf_conversion = """ "{}" unoconv -f pdf -o "{}" "{}" """.format(
            caminho_python_do_libreoffice, saida, ficheiro_entrada)

        print("Unoconv: ", uniconv_pdf_conversion)

        # Executa o cmd que converte o ficheiro odt em pdf
        # "C:\Program Files\LibreOffice\program\python.exe" unoconv.py -f pdf -o orlas.pdf template.odt
        subprocess.Popen(uniconv_pdf_conversion, shell=True)

        s = """ "{}" """.format(saida)
        print(s)
        subprocess.Popen(str(saida), shell=True)

        print("Documento convertido pelo unoconv com Sucesso.")

        return True
    except Exception as e:
        print("Não foi possível converter o documento. Erro: \n{}.".format(e))
        return False


def abre_ficheiro(filename=None):
    print("Tentando abrir o  ficheiro...", filename)
    f = None
    while f is None:
        f = readfile(filename)
        print("File is None...")
        if f is not None:
            print(filename)
            subprocess.Popen(filename, shell=True)
            break

    print("A Sair.....")


def printWordDocument(filename, out_file):
    word = client.Dispatch("Word.Application")
    wdFormatPDF = 17

    doc = word.Documents.Open(filename)
    doc.SaveAs(out_file, FileFormat=wdFormatPDF)
    doc.Close()
    word.Quit()
    subprocess.Popen(out_file, shell=True)

def mostrar_sobre():
    sobre = """
    <p>Orlando Filipe Vilanculos, 2018-2020 todos direitos reservados</p>
    <hr>
    <a href="#">Clique aqui para Licença</>"""

    return sobre

class Invoice(dict):

    @property
    def total(self):
        return decimal.Decimal(sum(l['amount'] for l in self['lines']))

    @property
    def vat(self):
        return decimal.Decimal(self.total * 0.21)

# Esta classe retorna o nome dos campos da tabela num base de dados MySQL
class CamposdaTabela:

    cur = ""
    database = ""
    tabela = ""

    # Serve para tabelas com campos com chave primaria autoincrement
    def tabela_auto_increment(self):
        database = self.database
        tabela = self.tabela
        colunas_sql = "SHOW COLUMNS FROM {}.{}".format(database, tabela)

        self.cur.execute(colunas_sql)
        data_colunas = self.cur.fetchall()

        lista_colunas = []
        for coluna in data_colunas:
            lista_colunas.append(coluna[0])

        lista_colunas.pop(0)

        tupla_campos = tuple(lista_colunas)
        return str(tupla_campos).replace("'", "")

    # Serve para tabelas com campos com chave primaria nao autoincrement
    def tabela_normal(self):
        database = self.database
        tabela = self.tabela
        colunas_sql = "SHOW COLUMNS FROM {}.{}".format(database, tabela)

        self.cur.execute(colunas_sql)
        data_colunas = self.cur.fetchall()

        lista_colunas = []
        for coluna in data_colunas:
            lista_colunas.append(coluna[0])

        tupla_campos = tuple(lista_colunas)
        return str(tupla_campos).replace("'", "")
#
#
# def open_cash_drawer(printername):
#     printerhandler = win32print.OpenPrinter(printername)
#     cash_drawer_open_command = chr(27) + chr(112) + chr(0) + chr(25) + chr(250)
#     win32print.StartDocPrinter(printerhandler, 1, ('Cash Drawer Open', None, 'RAW'))
#     win32print.WritePrinter(printerhandler, cash_drawer_open_command)
#     win32print.EndDocPrinter(printerhandler)
#     win32print.ClosePrinter(printerhandler)


def center(QWidget, QApp):
    """
    Centers PyQt5 Widget
    :param QWidget: The widget to be centered
    :param QApp: QAplicatipn
    :return: None
    """
    frameGm = QWidget.frameGeometry()
    screen = QApp.desktop().screenNumber(QApp.desktop().cursor().pos())
    centerPoint = QApp.desktop().screenGeometry(screen).center()
    frameGm.moveCenter(centerPoint)
    QWidget.move(frameGm.topLeft())


def load_html(html_file=None):
    """
    Loads html file with parameters
    :param html_file:
    :return: html content is file exists or False if file does not exist
    """
    import codecs

    try:
        file = codecs.open(html_file, 'r', encoding="utf-8")
        content = file.read()
    except Exception as e:
        print(e)
        return False

    return content


def refresh_db(database_connection=None):
    """
    Refreshes MySql database connection using the original mysql python connector
    :param database_connection:
    :return: true
    """
    try:
        database_connection.cmd_refresh(1)
    except Exception as e:
        print("Conexão com a Base de dados Perdida!!!\n{}.".format(e))

        return False

    return True
