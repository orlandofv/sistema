import datetime
import decimal
import sys
import os

from utilities import printWordDocument, Invoice

from PyQt5.QtWidgets import (QLineEdit, QToolBar, QMessageBox, qApp, QAction, QApplication, QGroupBox, QPushButton,
                             QComboBox, QDialog, QFormLayout, QHBoxLayout, QTableView, QCheckBox, QAbstractItemView,
                             QSplitter, QStatusBar, QVBoxLayout, QLabel)

from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QIcon, QTextDocument

from PyQt5.QtCore import QDate, QSizeF

from sortmodel import MyTableModel
from utilities import codigo as cd
from pricespinbox import price
from relatorio.templates.opendocument import Template

from GUI.RibbonButton import RibbonButton
from GUI.RibbonWidget import *

# from produtos import Produto as prod
from utilities import ANO_ACTUAL, HORA, MES

from maindialog import Dialog


