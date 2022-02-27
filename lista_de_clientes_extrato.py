# -*- coding: utf-8 -*-

import sys
import operator
import os
import subprocess
import csv

from PyQt5.QtWidgets import QApplication, QTableView, QAbstractItemView, QMessageBox, QToolBar, \
    QLineEdit, QLabel, QStatusBar, QAction, QMainWindow, qApp, QFileDialog, QProgressDialog

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant
import sqlite3 as lite
from clientes import Cliente

DB_FILENAME = 'dados.tsdb'


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # controla o codigo
        self.current_id = ""

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
            return
            sys.exit(True)

    def fill_table(self):

        # Header for the table
        header = [qApp.tr('Código'), qApp.tr('Nome'), qApp.tr('Documento'), "Número",qApp.tr('Debito'),
                  qApp.tr('Credito'), "Saldo"]
        
        self.sql = """select clientes.cod, clientes.nome, documentos.nome, 
        CONCAT(facturacao.numero, "/",facturacao.ano), facturacao.debito, 
        facturacao.credito, facturacao.saldo from clientes JOIN facturacao on clientes.cod=facturacao.codcliente
        JOIN documentos ON documentos.cod=facturacao.coddocumento WHERE clientes.nome like "%{nome}%" 
        or documentos.nome like"%{nome}%" or facturacao.saldo like "%{nome}%" AND facturacao.estado=1
        order by clientes.nome
        """.format(nome=self.find_w.text())

        try:
            self.cur.execute(self.sql)
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]
        except Exception as e:
            return

        if len(data) == 0:
            tabledata = ["", "", "", "", "", "", "", "", ""]
        else:
            tabledata = data

        try:
            self.tm = MyTableModel(tabledata, header, self)
            # set the table model
            self.totalItems = self.tm.rowCount(self)
            self.tv.setModel(self.tm)
        except Exception as e:
            return
        # # set row height
        nrows = len(tabledata)
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
        export_csv = QAction(QIcon('./images/icons8-export-csv-50.png'), "Exportar para CSV", self)

        tool = QToolBar()
        tool.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        tool.setContextMenuPolicy(Qt.PreventContextMenu)
        tool.addWidget(find)
        tool.addWidget(self.find_w)
        tool.addSeparator()
        tool.addAction(export_csv)

        tool.setAllowedAreas(Qt.TopToolBarArea|Qt.BottomToolBarArea)
        self.addToolBarBreak(Qt.BottomToolBarArea)
        self.addToolBar(tool)

        ######################################################################
        self.new.triggered.connect(self.new_data)
        self.delete.triggered.connect(self.removerow)
        self.tv.doubleClicked.connect(self.update_data)
        self.update.triggered.connect(self.update_data)
        export_csv.triggered.connect(self.exportar_extracto_csv)
        # self.connect(self.delete, SIGNAL("triggered()"), self.removerow)
        # # self.connect(self.update, SIGNAL("triggered()"), self.updatedata)
        # self.print.triggered.connect(self.printForm)

    def exportar_extracto_csv(self):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(self, 'Guardar Ficheiro', '.', filter='Ficheiros CSV(*.csv)')

        if filename:
            ficheiro = filename
        else:
            QMessageBox.warning(self, 'Gravar Ficheiro', 'Ficheiro não foi gravado')
            return

        if ficheiro.endswith('.csv') is False:
            ficheiro += '.csv'

        caminho = os.path.realpath(ficheiro)

        self.cur.execute(self.sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        csv_header = [qApp.tr('Código'), qApp.tr('Nome'), qApp.tr('Documento'), "Número",qApp.tr('Debito'),
                  qApp.tr('Credito'), "Saldo"]

        action_label = QLabel("Exportando produtos. Aguarde.....")

        progressbar = QProgressDialog()
        progressbar.setLabel(action_label)
        progressbar.setMinimum(0)
        progressbar.setModal(True)
        progressbar.setCancelButtonText("Aguarde....")
        progressbar.setWindowTitle("Exportando para CSV")

        count = 0
        try:
            with open(ficheiro, 'w', newline='', encoding='utf8') as lista_produtos:
                csv_write = csv.writer(lista_produtos, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_write.writerow(csv_header)
                progressbar.show()
                progressbar.setValue(1)

                if len(data) > 0:
                    progressbar.setMaximum(len(data))
                    for x in data:
                        count += 1
                        progressbar.setValue(count)
                        lista = list(x)
                        csv_write.writerow(lista)

                        action_label.setText("Exportando: {}. {}".format(count, lista[1]))
                progressbar.close()
                lista_produtos.close()

                subprocess.Popen(caminho, shell=True)

                QMessageBox.information(self, "Successo!", "Processo terminado com Sucesso!!!")
        except Exception as e:
            QMessageBox.warning(self, "Erro", "Erro: {}.\nVeja se o Ficheiro em causa não está aberto.".format(e))

    def create_statusbar(self):
        estado = QStatusBar(self)
    
        self.items = QLabel("Total Items: %s" % self.totalItems)
        estado.addWidget(self.items)
        self.setStatusBar(estado)

    def clickedslot(self, index):

        self.row = int(index.row())

        nome = self.tm.index(self.row, 1)
        self.find_w.setText(nome.data())

        self.fill_table()

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

        if self.current_id != "CL20181111111":
            if QMessageBox.question(self, "Pergunta", str("Deseja eliminar o registo %s?") % self.current_id,
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                sql = """delete from clientes WHERE cod = "{codigo}" """.format(codigo=str(self.current_id))

                try:
                    self.cur.execute(sql)
                    self.conn.commit()
                    self.fill_table()
                    QMessageBox.information(self, "Sucesso", "Item apagado com sucesso...")
                except Exception as e:
                    QMessageBox.warning(self, "Erro", "Impossivel apagar cliente.")
        else:
            QMessageBox.warning(self, "Erro", "Cliente não pode ser apagado.")

class MyTableModel(QAbstractTableModel):
    def __init__(self, datain, headerdata, parent=None, *args):
        """ datain: a list of lists
            headerdata: a list of strings
        """
        QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = datain
        self.headerdata = headerdata

    def rowCount(self, parent):
        return len(self.arraydata)

    def columnCount(self, parent):
        return len(self.arraydata[0])

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        return QVariant(self.arraydata[index.row()][index.column()])

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerdata[col])
        return QVariant()

    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        self.layoutAboutToBeChanged.emit()
        self.arraydata = sorted(self.arraydata, key=operator.itemgetter(Ncol))
        if order == Qt.DescendingOrder:
            self.arraydata.reverse()
        self.layoutChanged.emit()

# if __name__ == '__main__':
#
#     app = QApplication(sys.argv)
#
#     helloPythonWidget = MainWindow()
#     helloPythonWidget.show()
#
#     sys.exit(app.exec_())