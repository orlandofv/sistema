# -*- coding: utf-8 -*-

import sys
import decimal

from PyQt5.QtWidgets import QApplication, QTableView, QAbstractItemView, QMessageBox, QToolBar, \
    QLineEdit, QLabel, QStatusBar, QAction, QMainWindow, qApp

from PyQt5.QtGui import QIcon, QTextDocument
from PyQt5.QtCore import Qt
from PyQt5.QtPrintSupport import QPrintPreviewDialog

import sqlite3 as lite

from facturas_nao_pagas import Cliente
from sortmodel import MyTableModel
DB_FILENAME = 'dados.tsdb'

LISTA_TAXAS = ["TX20181111111", "TX20182222222"]

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # controla o codigo
        self.current_id = ""
        self.sql = ""

        # Connect the Database
        if self.parent() is None:
            self.db = self.connect_db()
            self.user = ""
        else:
            self.conn = self.parent().conn
            self.cur = self.parent().cur
            self.user = self.parent().user

        # Create the main user interface
        self.ui()

        # Header for the table
        self.header = [qApp.tr('Número'), qApp.tr('Data'), 'Dias', qApp.tr('Cliente'), qApp.tr('Total'),
                       qApp.tr('Saldo'), qApp.tr('Crédito'), "Notas"]

        # Search the data
        self.fill_table()
        self.find_w.textEdited.connect(self.fill_table)

    def ui(self):

        # create the view
        self.tv = QTableView(self)

        # set the minimum size
        self.tv.setMinimumSize(400, 300)

        # hide grid
        self.tv.setShowGrid(False)

        self.tv.setSelectionBehavior(QAbstractItemView.SelectRows)
        # set the font

        # hide vertical header
        vh = self.tv.verticalHeader()
        vh.setVisible(False)

        # set horizontal header properties and stretch last column
        hh = self.tv.horizontalHeader()
        hh.setStretchLastSection(True)

        # set column width to fit contents
        self.tv.resizeColumnsToContents()

        # enable sorting
        self.tv.setSortingEnabled(True)

        self.tv.clicked.connect(self.clickedslot)
        self.tv.setAlternatingRowColors(True)
        self.tv.setFocus()
        self.setCentralWidget(self.tv)
        self.create_toolbar()

    def focusInEvent(self, evt):
        self.fill_table()

    def connect_db(self):
        # Connect to database and retrieves data
        try:
            self.conn = lite.connect(DB_FILENAME)
            self.cur = self.conn.cursor()

        except Exception as e:
            sys.exit(True)

    def printlist(self, sql):

        self.cur.execute(sql)
        data = self.cur.fetchall()
        # LOGOTIPO
        # html = """
        #                 < table width="100%" style="float: right; border: 1px solid red;">
        #                    < tr >
        #                         < td >
        #                         < img src = '{}' width = "80" >
        #                         < / td >
        #                     </ tr >
        #                 < / table >
         #                """.format(logo)

        # html += "<hr/>"

        html = ""

        if self.parent() is not None:
            html += "<p> {} </p>".format(self.parent().empresa)
            html += "<p> {} </p>".format(self.parent().empresa_endereco)
            html += "<p> NUIT: {} </p>".format(self.parent().empresa_nuit)
            html += "<p> Contactos: {} </p>".format(self.parent().empresa_contactos)
        else:
            html += "<p> [Nome da Empresa] </p>"
            html += "<p> [Endereco] </p>"
            html += "<p> [NUIT] </p>"
            html += "<p> [CONTACTOS] </p>"

        html += "<h1> Lista de Facturas não Pagas </h1>"
        html += "<hr/>"

        html += "<table border='0' width = 80mm style='border: 1px;'>"
        html += "<tr style='background-color: gray;'>"
        html += "<th width = 5% align='center'>No.</th>"
        html += "<th width = 10%>Data</th>"
        html += "<th width = 5%>Dias</th>"
        html += "<th width = 30%>Cliente</th>"
        html += "<th width = 10% align='right'>Total</th>"
        html += "<th width = 10% align='right'>Saldo</th>"
        html += "<th width = 10% align='right'>Crédito</th>"
        html += "<th width = 20% align='right'>Notas</th>"
        html += "</tr>"

        saldo = decimal.Decimal(0.00)
        total = decimal.Decimal(0.00)
        credito = decimal.Decimal(0.00)

        for cliente in data:
            saldo += cliente[5]
            credito += cliente[6]
            total += cliente[4]

            html += """<tr> <td align='center'>{}</td>  <td>{}</td> <td>{}</td>  <td>{}</td>  
            <td align="right">{}</td> <td align="right">{}</td>  <td align="right">{}</td>  
            <td>{}</td> </tr> """.format(cliente[0], cliente[1], cliente[2], cliente[3], cliente[4],
                                         cliente[5], cliente[6], cliente[7])

        html += """<tr> <td align='center'>{}</td>  <td>{}</td> <td>{}</td> <td>{}</td>  
                    <td align="right">{}</td> <td align="right">{}</td>  <td align="right">{}</td>  
                    <td>{}</td> </tr> """.format("", "", "", "", total, saldo, credito, "")

        html += "</table>"

        html += "<br/>"
        html += "<hr/>"
        html += "<p> Processado por Computador"

        document = QTextDocument()

        document.setHtml(html)

        dlg = QPrintPreviewDialog(self)
        dlg.paintRequested.connect(document.print_)
        dlg.showMaximized()
        dlg.exec_()

    def fill_table(self):

        self.sql = """select numero, data, DATEDIFF(CURDATE() , data) as Dias, cliente, total, saldo, credito, obs 
        from facturas_nao_pagas WHERE numero like "%{numero}%" or cliente like "%{cliente}%" 
        """.format(numero=self.find_w.text(), cliente=self.find_w.text())

        try:
            self.cur.execute(self.sql)
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]
        except Exception as e:
            return

        if len(data) == 0:
            self.tabledata = ["", "", "", "", "", "", "", ""]
        else:
            self.tabledata = data

        try:
            self.tm = MyTableModel(self.tabledata, self.header, self)
            # set the table model
            self.totalItems = self.tm.rowCount(self)
            self.tv.setModel(self.tm)

            self.tv.setColumnWidth(0, self.tv.width()* .1)
            self.tv.setColumnWidth(1, self.tv.width()* .1)
            self.tv.setColumnWidth(2, self.tv.width()* .3)
            self.tv.setColumnWidth(3, self.tv.width()* .1)
            self.tv.setColumnWidth(4, self.tv.width()* .1)
            self.tv.setColumnWidth(5, self.tv.width()* .1)
            self.tv.setColumnWidth(6, self.tv.width()* .2)

        except Exception as e:
            print(e)
            return
        # # set row height
        nrows = len(self.tabledata)
        for row in range(nrows):
            self.tv.setRowHeight(row, 25)
        self.create_statusbar()

    def create_toolbar(self):
        find = QLabel(qApp.tr("Procurar") + "  ")
        self.find_w = QLineEdit(self)
        self.find_w.setMaximumWidth(200)

        self.new = QAction(QIcon('./icons/add_2.ico'), qApp.tr("Novo"), self)
        self.delete = QAction(QIcon('./images/editdelete.png'), qApp.tr("Eliminar"), self)
        self.print = QAction(QIcon('./images/fileprint.png'),qApp.tr("Imprimir"), self)
        self.update = QAction(QIcon('./images/pencil.png'), qApp.tr("Editar"), self)

        tool = QToolBar()
        tool.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        tool.setContextMenuPolicy(Qt.PreventContextMenu)

        tool.addWidget(find)
        tool.addWidget(self.find_w)
        tool.addAction(self.print)

        tool.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        self.addToolBarBreak(Qt.BottomToolBarArea)
        self.addToolBar(tool)

        ######################################################################
        # self.new.triggered.connect(self.new_data)
        # self.delete.triggered.connect(self.removerow)
        # self.tv.doubleClicked.connect(self.update_data)
        # self.update.triggered.connect(self.update_data)
        # self.connect(self.delete, SIGNAL("triggered()"), self.removerow)
        # # self.connect(self.update, SIGNAL("triggered()"), self.updatedata)
        self.print.triggered.connect(lambda: self.printlist(self.sql))

    def create_statusbar(self):
        estado = QStatusBar(self)

        self.items = QLabel("Total Items: %s" % self.totalItems)
        estado.addWidget(self.items)
        self.setStatusBar(estado)

    def clickedslot(self, index):

        self.row = int(index.row())

        indice = self.tm.index(self.row, 0)
        self.current_id = indice.data()

    def new_data(self):

        cl = Cliente(self)
        cl.setModal(True)
        cl.show()

    def update_data(self):

        if self.current_id == "":
            QMessageBox.information(self, "Info", "Selecione o registo a actualizar na tabela")
            return

        cl = Cliente(self)
        cl.cod.setText(self.current_id)
        cl.mostrar_registo()
        cl.setModal(True)
        cl.show()

    def removerow(self):

        if self.current_id == "":
            QMessageBox.information(self, "Info", "Selecione o registo a apagar na tabela")
            return

        if self.current_id not in LISTA_TAXAS:
            if QMessageBox.question(self, "Pergunta", str("Deseja eliminar o registo %s?") % self.current_id,
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                sql = """delete from facturas_nao_pagas WHERE cod = "{codigo}" """.format(codigo=str(self.current_id))
                self.cur.execute(sql)
                self.conn.commit()
                self.fill_table()
                QMessageBox.information(self, "Sucesso", "Item apagado com sucesso...")
        else:
            QMessageBox.warning(self, "Erro", "Taxa não pode ser apagada")

if __name__ == '__main__':

    app = QApplication(sys.argv)

    helloPythonWidget = MainWindow()
    helloPythonWidget.show()

    sys.exit(app.exec_())