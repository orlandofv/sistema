# -*- coding: utf-8 -*-
import sys

from PyQt5.QtCore import Qt, QCoreApplication, QEvent, QRegExp
from PyQt5.QtGui import QIcon, QFont, QKeyEvent, QRegExpValidator
from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QGridLayout, QApplication, QHBoxLayout


class Teclado(QDialog):

    def __init__(self, parent=None):
        super(Teclado, self).__init__(parent)

        regex = QRegExp("^(?:\d+\.?\d*|\d*\.?\d+)*$")
        validator = QRegExpValidator(regex)

        boldFont = QFont('Consolas', 24)
        boldFont.setBold(True)

        self.number_widget = QLineEdit()
        self.number_widget.setValidator(validator)

        #self.number_widget.setEnabled(False)
        self.number_widget.setText("0")
        self.number_widget.setAlignment(Qt.AlignRight)
        self.number_widget.setFont(boldFont)
        self.number_widget.setFixedHeight(40)
        # self.number_widget.setFocus()
        self.ok = QPushButton("&OK")
        self.cancelar = QPushButton("")
        self.cancelar.clicked.connect(self.close)
        self.ok.setDefault(True)
        self.ponto = QPushButton(".")

        self.ok.setIcon(QIcon("./icons/ok.ico"))
        self.cancelar.setIcon(QIcon("./icons/close_2.ico"))

        self.number_widget.setMaxLength(17)

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
        self.backspace = QPushButton("BSPACE", self)
        self.backspace.clicked.connect(self.backspace_btn)

        btn_grid = QGridLayout()

        btn_grid.addWidget(self.number_widget, 2, 0, 1, 3)
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
        btn_grid.addWidget(self.ponto, 6, 2)
        btn_grid.addWidget(self.backspace, 7, 0)
        btn_grid.addWidget(self.ok, 7, 1)
        btn_grid.addWidget(self.cancelar, 7, 2)

        self.lay = QHBoxLayout()
        self.lay.addLayout(btn_grid)
        self.setLayout(self.lay)

        self.setWindowTitle("Dados de Entrada")
        self.setWindowIcon(QIcon("./icons/Deleket-Sleek-Xp-Basic-Administrator.ico"))

        self.ok.clicked.connect(self.aceite)

        self.btnCalc0.clicked.connect(self.key0)
        self.ponto.clicked.connect(self.key_ponto)
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

        for child in self.findChildren(QPushButton):
            child.setFixedHeight(40)
            child.setFont(boldFont)

        self.setWindowTitle("Teclado")

    def aceite(self):
        if self.parent() is not None:
            try:
                self.parent().setValue(self.number_widget.text())
            except AttributeError:
                self.parent().setText(str(self.number_widget.text()))
            finally:
                print("Parent must be a QLineEdit, QSpinBox, QDoubleSpinBox or QLabel")
        else:
            print("No parent...!")

        self.close()

    def Limpar(self):
        self.number_widget.setText("0")

    def key0(self):

        self.number_widget.setFocus()

        if float(self.number_widget.text()) > 0:
            self.number_widget.setText(self.number_widget.text() + str(self.btnCalc0.text()))

        self.number_widget.clearFocus()

    def key_ponto(self):
        self.number_widget.setFocus()

        if "." not in self.number_widget.text():
            if self.number_widget.text() == "0":
                self.number_widget.setText("0.")
            else:
                self.number_widget.setText(self.number_widget.text() + str(self.ponto.text()))

        self.number_widget.clearFocus()

    def key1(self):
        self.number_widget.setFocus()

        if float(self.number_widget.text()) > 0:
            self.number_widget.setText(self.number_widget.text() + str(self.btnCalc1.text()))
        else:
            if self.number_widget.text() != "0.":
                self.number_widget.setText(str(self.btnCalc1.text()))
            else:
                self.number_widget.setText(self.number_widget.text() + str(self.btnCalc1.text()))

        self.number_widget.clearFocus()

    def key2(self):

        self.number_widget.setFocus()
        if float(self.number_widget.text()) > 0:
            self.number_widget.setText(self.number_widget.text() + str(self.btnCalc2.text()))
        else:
            if self.number_widget.text() != "0.":
                self.number_widget.setText(str(self.btnCalc2.text()))
            else:
                self.number_widget.setText(self.number_widget.text() + str(self.btnCalc2.text()))

        self.number_widget.clearFocus()

    def key3(self):

        self.number_widget.setFocus()
        if float(self.number_widget.text()) > 0:
            self.number_widget.setText(self.number_widget.text() + str(self.btnCalc3.text()))
        else:
            if self.number_widget.text() != "0.":
                self.number_widget.setText(str(self.btnCalc3.text()))
            else:
                self.number_widget.setText(self.number_widget.text() + str(self.btnCalc3.text()))

        self.number_widget.clearFocus()

    def key4(self):
        self.number_widget.setFocus()
        if float(self.number_widget.text()) > 0:
            self.number_widget.setText(self.number_widget.text() + str(self.btnCalc4.text()))
        else:
            if self.number_widget.text() != "0.":
                self.number_widget.setText(str(self.btnCalc4.text()))
            else:
                self.number_widget.setText(self.number_widget.text() + str(self.btnCalc4.text()))

        self.number_widget.clearFocus()

    def key5(self):
        self.number_widget.setFocus()
        if float(self.number_widget.text()) > 0:
            self.number_widget.setText(self.number_widget.text() + str(self.btnCalc5.text()))
        else:
            if self.number_widget.text() != "0.":
                self.number_widget.setText(str(self.btnCalc5.text()))
            else:
                self.number_widget.setText(self.number_widget.text() + str(self.btnCalc5.text()))

        self.number_widget.clearFocus()

    def key6(self):
        self.number_widget.setFocus()
        if float(self.number_widget.text()) > 0:
            self.number_widget.setText(self.number_widget.text() + str(self.btnCalc6.text()))
        else:
            if self.number_widget.text() != "0.":
                self.number_widget.setText(str(self.btnCalc6.text()))
            else:
                self.number_widget.setText(self.number_widget.text() + str(self.btnCalc6.text()))

        self.number_widget.clearFocus()

    def key7(self):
        self.number_widget.setFocus()
        if float(self.number_widget.text()) > 0:
            self.number_widget.setText(self.number_widget.text() + str(self.btnCalc7.text()))
        else:
            if self.number_widget.text() != "0.":
                self.number_widget.setText(str(self.btnCalc7.text()))
            else:
                self.number_widget.setText(self.number_widget.text() + str(self.btnCalc7.text()))

        self.number_widget.clearFocus()

    def key8(self):
        self.number_widget.setFocus()
        if float(self.number_widget.text()) > 0:
            self.number_widget.setText(self.number_widget.text() + str(self.btnCalc8.text()))
        else:
            if self.number_widget.text() != "0.":
                self.number_widget.setText(str(self.btnCalc8.text()))
            else:
                self.number_widget.setText(self.number_widget.text() + str(self.btnCalc8.text()))

        self.number_widget.clearFocus()

    def key9(self):
        self.number_widget.setFocus()
        if float(self.number_widget.text()) > 0:
            self.number_widget.setText(self.number_widget.text() + str(self.btnCalc9.text()))
        else:
            if self.number_widget.text() != "0.":
                self.number_widget.setText(str(self.btnCalc9.text()))
            else:
                self.number_widget.setText(self.number_widget.text() + str(self.btnCalc9.text()))

        self.number_widget.clearFocus()

    def backspace_btn(self):
        # self.number_widget.setFocus()
        self.sendkeys(Qt.Key_Tab)

    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def sendkeys(self, char, modifier=Qt.NoModifier, text=None):
        if not text:
            event = QKeyEvent(QEvent.KeyPress, char, modifier)
        else:
            event = QKeyEvent(QEvent.KeyPress, char, modifier, text)
        QCoreApplication.postEvent(self, event)

    def showEvent(self, evt):
        self.number_widget.setFocus()
        self.center()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    helloPythonWidget = Teclado()
    helloPythonWidget.show()
    sys.exit(app.exec_())