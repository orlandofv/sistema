# -*- coding: utf-8 -*-
"""
Created on Fri Mar 02 23:18:43 2012

@author: lims
"""

from PyQt5.QtWidgets import QDoubleSpinBox, QLineEdit, QComboBox
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
casas_decimais = 2


class price(QDoubleSpinBox):
    def __init__(self, parent=None):
        super(price, self).__init__(parent)

        self.setMaximumWidth(130)
        self.setRange(-999999999999, 999999999999)
        self.setDecimals(casas_decimais)
        self.setAlignment(Qt.AlignRight)

    def focusInEvent(self, evt):
        for child in self.findChildren(QLineEdit):
            child.selectAll()

    def mouseDoubleClickEvent(self, *args, **kwargs):
        self.selectAll()

class Preco_Combobox(QComboBox):

    def __init__(self, parent=None):
        super(Preco_Combobox, self).__init__(parent)

        self.setCurrentText("1")

    def focusInEvent(self, QFocusEvent):
        print("Esta aqui o Focus")

    def enterEvent(self, *args, **kwargs):
        print("Entrou......")

    def leaveEvent(self, *args, **kwargs):
        if self.currentText() == "":
            self.setCurrentText("1")

