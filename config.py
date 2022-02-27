import sys

from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtWidgets import (QDialog, QPushButton, QHBoxLayout, QVBoxLayout, QGroupBox, QApplication, QFileDialog,
                             QLineEdit, QComboBox, QFormLayout, QLabel, QSpinBox, QWidget, QSizePolicy, QFrame,
                             QMessageBox)

from utilities import get_printer_name_win32 as printer_list
from utilities import testa_caminho

APPLICATION_NAME = "Microgest POS"
APPLICATION_VERSION = "1.0.2020"
ORGANIZATION_DOMAIN = "www.microgest.com"
ORGANIZATION_NAME = "Microgest Lda"


class Config(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.python = None
        self.pos1 = None
        self.pos2 = None
        self.copias_pos1 = None
        self.copias_pos2 = None
        self.impressora1 = None
        self.impressora2 = None
        self.papel_1 = "80mm"
        self.papel_2 = "80mm"
        self.mesas = 10

        self.ui()
        self.setWindowTitle("Configurações Cliente")

        self.get_settings()

    def ui(self):

        self.line_caminho_python = QLineEdit()
        self.line_caminho_python.setEnabled(False)
        self.btn_caminho_python = QPushButton("...")
        self.btn_caminho_python.clicked.connect(self.caminho_python)
        printers = printer_list()

        self.combo_impressora_pos1 = QComboBox()
        self.combo_impressora_pos2 = QComboBox()
        self.papel1 = QComboBox()
        self.papel1.addItems(["80mm", "58mm"])
        self.papel2 = QComboBox()
        self.papel2.addItems(["80mm", "58mm"])
        self.combo_impressora_A41 = QComboBox()
        self.combo_impressora_A42 = QComboBox()
        self.combo_impressora_pos1.addItems(printers)
        self.combo_impressora_pos2.addItems(printers)
        self.combo_impressora_A41.addItems(printers)
        self.combo_impressora_A42.addItems(printers)

        self.spin_pos1 = QSpinBox()
        self.spin_pos1.setRange(1, 99)
        self.spin_pos1.setAlignment(Qt.AlignRight)
        self.spin_pos2 = QSpinBox()
        self.spin_pos2.setRange(1, 99)
        self.spin_pos2.setAlignment(Qt.AlignRight)

        self.form_layout = QFormLayout()
        python_lay = QHBoxLayout()
        python_lay.addWidget(self.line_caminho_python)
        python_lay.addWidget(self.btn_caminho_python)

        python_group = QGroupBox("Caminho do Executável Python do LibreOffice ou OpenOffice")
        python_group.setLayout(python_lay)

        pos1_lay = QHBoxLayout()
        pos1_lay.addWidget(QLabel("Impressora Térmica 1"))
        pos1_lay.addWidget(self.combo_impressora_pos1)
        pos1_lay.addWidget(QLabel("Nº de Cópias"))
        pos1_lay.addWidget(self.spin_pos1)
        pos1_lay.addWidget(self.papel1)

        pos2_lay = QHBoxLayout()
        pos2_lay.addWidget(QLabel("Impressora Térmica 2"))
        pos2_lay.addWidget(self.combo_impressora_pos2)
        pos2_lay.addWidget(QLabel("Nº de Cópias"))
        pos2_lay.addWidget(self.spin_pos2)
        pos2_lay.addWidget(self.papel2)

        self.form_layout.addRow(QLabel("Impressora Normal 1"), self.combo_impressora_A41)
        self.form_layout.addRow(QLabel("Impressora Normal 2"), self.combo_impressora_A42)

        stretch = QWidget()
        stretch.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_gravar = QPushButton("Gravar")
        self.btn_gravar.clicked.connect(self.save_settings)
        btn_fechar = QPushButton("Sair")
        btn_fechar.clicked.connect(self.close)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(stretch)
        btn_layout.addWidget(self.btn_gravar)
        btn_layout.addWidget(btn_fechar)

        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setObjectName("line")

        main_layout = QVBoxLayout()
        main_layout.addWidget(python_group)
        main_layout.addLayout(pos1_lay)
        main_layout.addLayout(pos2_lay)
        main_layout.addLayout(self.form_layout)
        main_layout.addWidget(line)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    # Saves settings
    def save_settings(self):
        settings = QSettings()

        if testa_caminho(self.line_caminho_python.text()) is False:
            QMessageBox.warning(self, "Erro de Gravação", "Caminho Python Inválido")
            return False

        try:
            settings.setValue("MigrogestPOS/python", self.line_caminho_python.text())
            settings.setValue("MigrogestPOS/pos1", self.combo_impressora_pos1.currentText())
            settings.setValue("MigrogestPOS/pos2", self.combo_impressora_pos2.currentText())
            settings.setValue("MigrogestPOS/copias_pos1", self.spin_pos1.value())
            settings.setValue("MigrogestPOS/copias_pos2", self.spin_pos2.value())
            settings.setValue("MigrogestPOS/impressora1", self.combo_impressora_A41.currentText())
            settings.setValue("MigrogestPOS/impressora2", self.combo_impressora_A42.currentText())
            settings.setValue("MigrogestPOS/papelpos1", self.papel1.currentText())
            settings.setValue("MigrogestPOS/papelpos2", self.papel2.currentText())
            # settings.setValue("MigrogestPOS/mesas", self.spin_mesas.value())
            settings.sync()

            QMessageBox.information(self, "Sucesso", "Dados Gravados com Sucesso!")
        except Exception as e:
            QMessageBox.warning(self, "Erro de Gravação", "Dados não Gravados.\nErro {}.".format(e))
            return False

        return True

    def get_settings(self):

        settings = QSettings()
        self.python = settings.value("MigrogestPOS/python", "", str)
        self.pos1 = settings.value("MigrogestPOS/pos1", "", str)
        self.pos2 = settings.value("MigrogestPOS/pos2", "", str)
        self.copias_pos1 = settings.value("MigrogestPOS/copias_pos1", 1, int)
        self.copias_pos2 = settings.value("MigrogestPOS/copias_pos2", 1, int)
        self.impressora1 = settings.value("MigrogestPOS/impressora1", "", str)
        self.impressora2 = settings.value("MigrogestPOS/impressora2", "", str)
        self.papel_1 = settings.value("MigrogestPOS/papelpos1", "", str)
        self.papel_2 = settings.value("MigrogestPOS/papelpos2", "", str)
        self.mesas = settings.value("MigrogestPOS/mesas", 1, int)

        self.line_caminho_python.setText(self.python)
        self.combo_impressora_pos1.setCurrentText(self.pos1)
        self.combo_impressora_pos2.setCurrentText(self.pos2)
        self.spin_pos1.setValue(int(self.copias_pos1))
        self.spin_pos2.setValue(int(self.copias_pos2))
        self.combo_impressora_A41.setCurrentText(self.impressora1)
        self.combo_impressora_A42.setCurrentText(self.impressora2)
        self.papel1.setCurrentText(self.papel_1)
        self.papel2.setCurrentText(self.papel_2)

        print("Configuracaoes restauradas", self.python, self.pos1, self.pos2, self.copias_pos1,
              self.copias_pos2, self.impressora1, self.impressora2, self.papel_1, self.papel_2)

    def caminho_python(self):

        formats = "Executavel Python(*.exe)"

        dialog = QFileDialog(self)
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        path = dialog.getOpenFileName(self, "Escolha o Ficheiro", "", formats)

        if path == "":
            caminho = ""
        else:
            caminho = path[0]

        self.line_caminho_python.setText(caminho)

        return caminho

if __name__ == '__main__':

    app = QApplication(sys.argv)

    app.setApplicationName(APPLICATION_NAME)
    app.setApplicationVersion(APPLICATION_VERSION)
    app.setOrganizationDomain(ORGANIZATION_DOMAIN)
    app.setOrganizationName(ORGANIZATION_NAME)

    config = Config()
    config.show()
    sys.exit(app.exec_())