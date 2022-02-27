
import sys
from PyQt5.QtWidgets import (QApplication, QDialog, QLabel, QSpinBox, QComboBox, QGroupBox, QFormLayout,
                             QVBoxLayout, QCheckBox, QPushButton, QHBoxLayout, QTabWidget, QWidget,
                             QRadioButton, QSizePolicy, QFileDialog, QMessageBox)

from PyQt5.QtGui import QIcon

LISTA_BARCODES = []
DB_FILE = "lista_de_Empresa.db"

SQL = """CREATE TABLE IF NOT EXISTS config(
empresa VARCHAR(255) UNIQUE NOT NULL PRIMARY KEY ,
f_template VARCHAR(255) DEFAULT "",
rec_template VARCHAR(255) DEFAULT "",
req_template VARCHAR(255) DEFAULT "",
c_cliente INT DEFAULT 1,
cliente_n INT DEFAULT 1,
saldo INT DEFAULT 1,
c_inactivo INT DEFAULT 1,
desc_automatico INT DEFAULT 1,
ac_credito INT DEFAULT 1,
pos1 VARCHAR(255) DEFAULT "",
pos2 VARCHAR(255) DEFAULT "",
pos3 VARCHAR(255) DEFAULT "",
pos4 VARCHAR(255) DEFAULT "",
pos5 VARCHAR(255) DEFAULT "",
so_vd INT DEFAULT 0,
iva_incluso INT DEFAULT 1,
regime INT DEFAULT 1,
isento INT DEFAULT 1,
vendas_zero INT DEFAULT 1,
cop1 INT DEFAULT 1,
cop2 INT DEFAULT 1,
cop3 INT DEFAULT 1,
cop4 INT DEFAULT 1,
cop5 INT DEFAULT 1)
"""

class Config(QDialog):
    fact_template = ""
    rec_template = ""
    req_template = ""
    criar_cliente = 1
    cliente_normal = 1
    saldo = 1
    cliente_inactivo = 0
    desconto_automatico = 0
    acima_do_credito = 1
    pos1 = ""
    pos2 = ""
    pos3 = ""
    pos4 = ""
    pos5 = ""
    so_vds = 0
    imposto_incluso = 1
    regime_normal = 0
    insento = 0
    q_abaixo_de_zero = 0
    cop1 = 1
    cop2 = 1
    cop3 = 1
    cop4 = 1
    cop5 = 1

    def __init__(self, parent=None):
        super(Config, self).__init__(parent)
        self.template_bar = QWidget()
        self.cliente_bar = QWidget()
        self.vendas_bar = QWidget()
        self.impressorapos_bar = QWidget()
        self.tab_widget = QTabWidget()

        self.cliente_ui()
        self.template_ui()
        self.pos_ui()
        self.vendas_ui()
        self.ui()
        self.setWindowTitle("Configurações")

        if self.parent() is not None:
            self.empresa = self.parent().empresa
            self.cur = self.parent().cur
            self.conn = self.parent().conn
            self.create_config_table()

        else:
            self.empresa = "Empresa Teste"

    def create_config_table(self):
        try:
            self.cur.execute(SQL)
            self.conn.commit()
        except Exception as e:
            print(e)

    def ui(self):

        gravar = QPushButton("Gravar")
        gravar.clicked.connect(self.gravar_registo)

        spacer1 = QWidget()
        spacer1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button_layout = QHBoxLayout()
        button_layout.addWidget(spacer1)
        button_layout.addWidget(gravar)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tab_widget)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def template_ui(self):
        self.factura_label = QLabel()
        self.recibo_label = QLabel()
        factura_button = QPushButton("...")
        factura_button.clicked.connect(self.factura_tamplate)
        factura_button.setMaximumWidth(40)
        recibo_button = QPushButton("...")
        recibo_button.clicked.connect(self.recibo_tamplate)
        recibo_button.setMaximumWidth(40)

        formlayout = QFormLayout()
        formlayout.addRow(QLabel("Escolha o Template para Facturas, VDs, ...."))
        formlayout.addRow(factura_button, self.factura_label)
        formlayout.addRow(QLabel("Escolha o Template para Recibos"))
        formlayout.addRow(recibo_button, self.recibo_label)
        formlayout.addRow(QLabel("Escolha o Template para Requisições Internas"))

        self.template_bar.setLayout(formlayout)
        self.tab_widget.addTab(self.template_bar, QIcon("./icons/caixa.ico"), "Templates")

    def factura_tamplate(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileNames(self, 'Escolha o Ficheiro', '.', filter='OpenOffice Documents odt(*.odt)')

        if filename:
            ficheiro = filename[0]

        else:
            ficheiro = ""
            QMessageBox.warning(self, 'Escolha o Ficheiro', 'Nenhum Ficheiro escolhido')
            
        self.factura_label.setText(ficheiro)

    def recibo_tamplate(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileNames(self, 'Escolha o Ficheiro', '.',
                                                   filter='OpenOffice Documents odt(*.odt)')

        if filename:
            ficheiro = filename[0]

        else:
            ficheiro = ""
            QMessageBox.warning(self, 'Escolha o Ficheiro', 'Nenhum Ficheiro escolhido')
            return

        self.recibo_label.setText(ficheiro)

    def requisicao_tamplate(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileNames(self, 'Escolha o Ficheiro', '.',
                                                   filter='OpenOffice Documents odt(*.odt)')

        if filename:
            ficheiro = filename[0]

        else:
            ficheiro = ""
            QMessageBox.warning(self, 'Escolha o Ficheiro', 'Nenhum Ficheiro escolhido')
            return

    def pos_ui(self):

        printers = self.getPrinterNameWin32()

        if len(printers) == 0:
            return

        self.impressora_pos1 = QComboBox()
        self.impressora_pos1.addItems(printers)
        self.impressora_pos1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.impressora_pos2 = QComboBox()
        self.impressora_pos2.addItems(printers)
        self.impressora_pos2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.impressora_pos3 = QComboBox()
        self.impressora_pos3.addItems(printers)
        self.impressora_pos3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.impressora_pos4 = QComboBox()
        self.impressora_pos4.addItems(printers)
        self.impressora_pos4.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.impressora_pos5 = QComboBox()
        self.impressora_pos5.addItems(printers)
        self.impressora_pos5.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.copias1 = QSpinBox()
        self.copias1.setMaximumWidth(50)
        self.copias1.setRange(1, 50)
        copias1_layout = QFormLayout()
        copias1_layout.addRow(QLabel("Nº de Copias"), self.copias1)
        self.copias2 = QSpinBox()
        self.copias2.setMaximumWidth(50)
        self.copias2.setRange(1, 50)
        copias2_layout = QFormLayout()
        copias2_layout.addRow(QLabel("Nº de Copias"), self.copias2)
        self.copias3 = QSpinBox()
        self.copias3.setMaximumWidth(50)
        self.copias3.setRange(1, 50)
        copias3_layout = QFormLayout()
        copias3_layout.addRow(QLabel("Nº de Copias"), self.copias3)
        self.copias4 = QSpinBox()
        self.copias4.setMaximumWidth(50)
        self.copias4.setRange(1, 50)
        copias4_layout = QFormLayout()
        copias4_layout.addRow(QLabel("Nº de Copias"), self.copias4)

        formlayout = QFormLayout()
        formlayout.addRow(QLabel("Escolha a Impressora POS 1"))
        formlayout.addRow(self.impressora_pos1, copias1_layout)
        formlayout.addRow(QLabel("Escolha a Impressora POS 2 (Para Cozinha)"))
        formlayout.addRow(self.impressora_pos2, copias2_layout)
        formlayout.addRow(QLabel("Escolha a Impressora A4"))
        formlayout.addRow(self.impressora_pos3, copias3_layout)
        formlayout.addRow(QLabel("Escolha a Impressora A4 (Para Cozinha)"))
        formlayout.addRow(self.impressora_pos4, copias4_layout)

        self.impressorapos_bar.setLayout(formlayout)
        self.tab_widget.addTab(self.impressorapos_bar, QIcon("./icons/Printer.ICO"), "Impressoras POS")

    def getPrinterNameWin32(self):
        strComputer = "."
        import win32com.client
        objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
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

    def cliente_ui(self):

        self.user_pode_criar = QRadioButton("Usuário normal")
        self.gestor_pode_criar = QRadioButton("Só Gestor")
        self.gestor_pode_criar.setChecked(True)

        cliente_layout = QVBoxLayout()
        cliente_layout.addWidget(self.user_pode_criar)
        cliente_layout.addWidget(self.gestor_pode_criar)

        cliente_box = QGroupBox("Criar novo Cliente nas Vendas")
        cliente_box.setLayout(cliente_layout)

        self.cliente_Normal = QCheckBox("Adicionar automaticamente Cliente Normal caso nao se escolheu Cliente")
        self.cliente_com_divida = QCheckBox("Verificar o saldo do cliente nas Facturas")
        self.cliente_Inactivo = QCheckBox("Mostrar Cliente Inactivo nas Vendas")
        self.desconto_cliente = QCheckBox("Efectuar desconto automático para o Cliente")
        self.credito_cliente = QCheckBox("Vender acima do Crédito Máximo do Cliente")

        formlayout = QFormLayout()
        formlayout.addWidget(cliente_box)
        formlayout.addWidget(self.cliente_Normal)
        formlayout.addWidget(self.cliente_com_divida)
        formlayout.addWidget(self.cliente_Inactivo)
        formlayout.addWidget(self.desconto_cliente)
        formlayout.addWidget(self.credito_cliente)

        self.cliente_bar.setLayout(formlayout)
        self.tab_widget.addTab(self.cliente_bar, QIcon("./icons/clientes.ico"), "Clientes")

    def vendas_ui(self):
        self.vd = QCheckBox("Mostrar apenas V.D. nas Vendas")
        self.iva = QCheckBox("Os meus produtos já tem Imposto Incluso")
        self.imposto = QCheckBox("Regime Normal (Sem IVA ou ISPC)")
        self.sem_imposto = QCheckBox("Multi-taxas, alguns produtos/Serviços tem Taxas outros não.")
        self.abaixo_de_zero = QCheckBox("Vender produtos com quantidades abaixo de Zero (0)")

        formlayout = QFormLayout()
        formlayout.addWidget(self.vd)
        formlayout.addWidget(self.iva)
        formlayout.addWidget(self.imposto)
        formlayout.addWidget(self.sem_imposto)
        formlayout.addWidget(self.abaixo_de_zero)

        self.vendas_bar.setLayout(formlayout)
        self.tab_widget.addTab(self.vendas_bar, QIcon("./icons/payment.ico"), "Vendas e Impostos")

    def bool_to_number(self, val=True):
        if val is True:
            return 1
        else:
            return 0

    def showEvent(self, QShowEvent):
        if self.user_pode_criar.isChecked() is False and self.gestor_pode_criar.isChecked() is False:
            self.user_pode_criar.setChecked(1)

        self.mostrar_registo()

    def validar(self):

        self.fact_template = self.factura_label.text()
        self.rec_template = self.recibo_label.text()
        self.criar_cliente = self.bool_to_number(self.user_pode_criar.isChecked())
        self.cliente_normal = self.bool_to_number(self.cliente_Normal.isChecked())
        self.saldo = self.bool_to_number(self.cliente_com_divida.isChecked())
        self.cliente_inactivo = self.bool_to_number(self.cliente_Inactivo.isChecked())
        self.desconto_automatico = self.bool_to_number(self.desconto_cliente.isChecked())
        self.acima_do_credito = self.bool_to_number(self.credito_cliente.isChecked())
        self.pos1 = self.impressora_pos1.currentText()
        self.pos2 = self.impressora_pos2.currentText()
        self.pos3 = self.impressora_pos3.currentText()
        self.pos4 = self.impressora_pos4.currentText()
        self.pos5 = self.impressora_pos5.currentText()
        self.so_vds = self.bool_to_number(self.vd.isChecked())
        self.imposto_incluso = self.bool_to_number(self.iva.isChecked())
        self.regime_normal = self.bool_to_number(self.imposto.isChecked())
        self.insento = self.bool_to_number(self.sem_imposto.isChecked())
        self.q_abaixo_de_zero = self.bool_to_number(self.abaixo_de_zero.isChecked())
        self.cop1 = self.copias1.value()
        self.cop2 = self.copias2.value()
        self.cop3 = self.copias3.value()
        self.cop4 = self.copias4.value()
        self.cop5 = ""

    def gravar_registo(self):
        self.validar()
        
        sql = """REPLACE INTO config VALUES ("{}", "{}", "{}", "{}", {}, {}, {}, {}, {}, {}, "{}", 
        "{}", "{}", "{}", "{}", {}, {}, {}, {}, {}, {}, {}, {}, {}, {})""".format(self.empresa, self.fact_template,
                                                                                  self.rec_template,
                                                                                  self.rec_template,
                                                    self.criar_cliente, self.cliente_normal, self.saldo,
                                                    self.cliente_inactivo, self.desconto_automatico,
                                                    self.acima_do_credito, self.pos1, self.pos2, self.pos3,
                                                    self.pos4, self.pos5, self.so_vds, self.imposto_incluso,
                                                    self.regime_normal, self.insento, self.q_abaixo_de_zero, self.cop1,
                                                              self.cop2, self.cop3, self.cop4, self.cop1)

        try:
            self.cur.execute(sql)
            self.conn.commit()

            QMessageBox.information(self, "Sucesso", "Configurações guardadas com Sucesso!")
        except Exception as e:
            QMessageBox.warning(self, "Erro", "Configurações não foram guardadas. Erro {}".format(e))
            print(e)

    def mostrar_registo(self):
        sql = """SELECT * FROM config WHERE empresa="{}" """.format(self.empresa)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                self.factura_label.setText(item[1])
                self.recibo_label.setText(item[2])
                self.user_pode_criar.setChecked(item[4])
                self.cliente_Normal.setChecked(item[5])
                self.cliente_com_divida.setChecked(item[6])
                self.cliente_Inactivo.setChecked(item[7])
                self.desconto_cliente.setChecked(item[8])
                self.credito_cliente.setChecked(item[9])
                self.impressora_pos1.setCurrentText(item[10])
                self.impressora_pos2.setCurrentText(item[11])
                self.impressora_pos3.setCurrentText(item[12])
                self.impressora_pos4.setCurrentText(item[13])
                self.impressora_pos5.setCurrentText(item[14])
                self.vd.setChecked(item[15])
                self.iva.setChecked(item[16])
                self.imposto.setChecked(item[17])
                self.sem_imposto.setChecked(item[18])
                self.abaixo_de_zero.setChecked(item[19])
                self.copias1.setValue(item[20])
                self.copias2.setValue(item[21])
                self.copias3.setValue(item[22])
                self.copias4.setValue(item[23])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    barcode = Config()
    barcode.show()
    sys.exit(app.exec_())