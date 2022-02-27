import os, glob
import subprocess
import sys
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QSpinBox, QComboBox, QGroupBox, QFormLayout, \
    QVBoxLayout, QCheckBox, QPushButton, QHBoxLayout, QLineEdit, QMessageBox

from PyQt5.QtCore import QSettings, QSizeF
from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter
from PyQt5.QtGui import QTextDocument

import barcode
from barcode.writer import ImageWriter
from utilities import codigo as cd
from maindialog import Dialog

LISTA_BARCODES = barcode.PROVIDED_BARCODES

class Barcode(Dialog):
    def __init__(self, parent=None, titulo="", imagem=""):
        super(Barcode, self).__init__(parent, titulo, imagem)
        self.barcode_picture = ""
        self.ui()

    def ui(self):
        sizegroup = QGroupBox()
        self.altura =  QSpinBox()
        self.altura.setMaximumWidth(50)
        self.altura.setRange(5, 500)
        self.largura = QSpinBox()
        self.largura.setMaximumWidth(50)
        self.largura.setRange(30, 500)
        self.copias = QSpinBox()
        self.copias.setMaximumWidth(50)
        self.copias.setRange(1, 1000000000)
        self.barcode_combo = QComboBox()
        self.barcode_combo.addItems(LISTA_BARCODES)
        self.barcode_char = QComboBox()
        self.barcode_char.setEditable(True)
        gravar = QPushButton("Pre-Visualizar")
        gravar.clicked.connect(self.create_barcode)
        gravar_png = QPushButton("Imagem PNG")
        gravar_png.clicked.connect(self.savebarcode_png)
        gravar_svg = QPushButton("Ficheiro SVG")
        gravar_svg.clicked.connect(self.savebarcode_svg)
        gravar_html = QPushButton("Ficheiro HTML")
        gravar_html.clicked.connect(self.savebarcode_html)

        fechar = QPushButton("Fechar")
        fechar.clicked.connect(self.close)

        butonlay  = QHBoxLayout()
        butonlay.addWidget(gravar)
        # butonlay.addWidget(gravar_html)
        butonlay.addWidget(gravar_png)
        butonlay.addWidget(gravar_svg)
        butonlay.addWidget(fechar)

        notas = "Nota: Caracteres especiais, não são aceites em todas classes de Códigos de Barras." \
                "\nAlgumas Classes só aceitam números.\nOutras só funcionamm com prefixos specíficos." \
                "\nEm caso de dúvida use code128 e code39."

        print(notas)
        formlay = QFormLayout()
        formlay.addRow(QLabel("Comprimento"), self.altura)
        formlay.addRow(QLabel("Largura"), self.largura)
        formlay.addRow(QLabel("No. de Copias"), self.copias)
        formlay.addRow(QLabel("Classe de Código de Barras"), self.barcode_combo)
        formlay.addRow(QLabel("Entre o Texto"), self.barcode_char)
        formlay.addRow(QLabel("<p style='color: red;'>Notas:</p>"))
        formlay.addRow(QLabel("<p style='color: red;'>Caracteres especiais, não são aceites em todas classes de Códigos de Barras.</p>"))
        formlay.addRow(QLabel("<p style='color: red;'>Algumas Classes só aceitam números.</p>"))
        formlay.addRow(QLabel("<p style='color: red;'>Outras só funcionamm com prefixos specíficos.</p>"))
        formlay.addRow(QLabel("<p style='color: green;'>Em caso de dúvida use code128 e code39.</p>"))
        formlay.addRow(butonlay)

        sizegroup.setLayout(formlay)
        vboxlay = QVBoxLayout()
        vboxlay.addWidget(sizegroup)
        self.layout().addLayout(vboxlay)
        self.setWindowTitle("Gestor de Código de Baras ")

    def generate_barcode_svg(self):
        classe = self.barcode_combo.currentText()
        char = self.barcode_char.currentText()
        if classe == "" or char == "":
            self.barcode_char.setFocus()
            return False

        try:
            EAN = barcode.get_barcode_class(classe)
            ean = EAN(u'{}'.format(char))
            fullname = ean.save(classe + cd("abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789"))
        except Exception as e:
            QMessageBox.warning(self, "Erro", "Erro na criação do Barcode:\n{}".format(e))
            return False

        return fullname

    def generate_barcode_png(self):
        classe = self.barcode_combo.currentText()
        char = self.barcode_char.currentText()
        if classe == "" or char == "":
            self.barcode_char.setFocus()
            return False

        try:
            EAN = barcode.get_barcode_class('{}'.format(classe))
            ean = EAN(u'{}'.format(char), writer=ImageWriter())
            fullname = ean.save(classe + cd("abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789"))
        except Exception as e:
            QMessageBox.warning(self, "Erro", "Erro na criação do Barcode:\n{}".format(e))
            return False

        return fullname

    def savebarcode_png(self):
        name = self.generate_barcode_png()

        if name is not False:
            filename = os.path.realpath(name)
        else:
            return

        subprocess.Popen(filename, shell=True)

    def savebarcode_svg(self):
        name = self.generate_barcode_svg()

        if name is not False:
            filename = os.path.realpath(name)
        else:
            return

        subprocess.Popen(filename, shell=True)

    def savebarcode_html(self):

        name = self.generate_barcode_png()

        if name is not False:
            filename = os.path.realpath(name)
        else:
            return

        imagem = ""

        for x in range(self.copias.value()):
            imagem += "<tr>"
            imagem += """<img src="{img}" height="{h}" width="{l}"> 
            """.format(img=filename, h=self.altura.value(), l=self.largura.value())
            imagem += "</tr>"
        
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Title</title>
        </head>
        <body>
            <table>
                {imagem}
            </table>
        </body>
        </html>
        """.format(imagem=imagem)

        file_name = cd("abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")
        file_name += '.html'
        file = open(file_name, 'w', encoding='utf8')
        file.writelines(html)

        # subprocess.Popen(file, shell=True)

    def create_barcode(self):

        name = self.generate_barcode_png()

        if name is not False:
            filename = os.path.realpath(name)
        else:
            return

        html = "<table border='0' width = 80mm style='border: 1px;'>"

        for x in range(self.copias.value()):
            html += "<tr>"
            html += """<img src="{img}" height="{h}" width="{l}"> 
            """.format(img=filename, h=self.altura.value(), l=self.largura.value())
            html += "</tr>"

        printer = QPrinter()
        printer.setResolution(printer.HighResolution)
        printer.setPageSize(QPrinter.A4)

        document = QTextDocument()
        document.setPageSize(QSizeF(printer.pageRect().size()))

        document.setHtml(html)
        dlg = QPrintPreviewDialog(self)
        dlg.paintRequested.connect(document.print_)
        dlg.printer().setResolution(QPrinter.HighResolution)

        dlg.showMaximized()
        dlg.exec_()

        # Remove a imagem
        self.remove_barcode(filename)

    def remove_barcode(self, name):
        try:

            for f in glob.glob(name):
                os.remove(f)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    barcode_app = Barcode(None, "Barcodes")
    barcode_app.show()
    sys.exit(app.exec_())
