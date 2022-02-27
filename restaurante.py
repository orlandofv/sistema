# -*- coding: utf-8 -*-
"""
Created on Fri Mar 02 23:18:43 2012

@author: lims
"""
import decimal
import sys
import datetime
import os
from time import localtime, strftime
from utilities import printWordDocument, Invoice

from PyQt5.QtWidgets import (QDialog, QLabel, QVBoxLayout, QToolBar, QMessageBox,
                             QAction, QApplication, QGridLayout, QComboBox, QGroupBox, QPushButton, QPlainTextEdit,
                             QCalendarWidget, QDateEdit, QButtonGroup)

from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog, QPrinterInfo
from PyQt5.QtCore import Qt, QSizeF, QDate
from PyQt5.QtGui import QIcon, QFont, QTextDocument, QPaintDevice

from relatorio.templates.opendocument import Template

from documentos import Cliente as doc
from clientes import Cliente as cl
from pricespinbox import price
from utilities import codigo as cd
from decimal import Decimal
from maindialog import Dialog

import sqlite3 as lite

DB_FILENAME = "dados.tsdb"

DATA_HORA_FORMATADA = strftime("%Y-%m-%d %H:%M:%S", localtime())
DATA_ACTUAL = datetime.datetime.today()
date = datetime.datetime.now().date()
ANO_ACTUAL = DATA_ACTUAL.year
DIA = DATA_ACTUAL.day
MES = DATA_ACTUAL.month

class Cliente(Dialog):
    def __init__(self, parent=None, titulo="", imagem=""):
        super(Cliente, self).__init__(parent, titulo, imagem)

        if self.parent() is not None:
            self.valortotal = Decimal(self.parent().totalgeral)
            self.user = self.parent().user
        else:
            self.valortotal = Decimal(0.00)
            self.user = ""

    def ui(self):
        button_font()