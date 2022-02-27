# -*- coding: utf-8 -*-

import sys


from PyQt5.QtWidgets import QApplication, QTableView, QAbstractItemView, QMessageBox, QToolBar, \
    QLineEdit, QLabel, QStatusBar, QAction, QMainWindow, qApp

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sqlite3 as lite

from usuarios import user
from sortmodel import MyTableModel

DB_FILENAME = 'dados.tsdb'

LISTA_USERS = ["admin", "user"]


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

        #Header for the table
        self.header = [qApp.tr('Usuário'), qApp.tr('Nome'), qApp.tr('Endereço'), qApp.tr('sexo'), qApp.tr('Email'),
                       "Data de Nascimento", "Contactos", "Nacionalidade"]

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

    def fill_table(self):

        self.sql = """select cod, nome, endereco, sexo, email, nascimento, contacto, nacionalidade 
        from users WHERE cod or nome like "%{nome}%" """.format(nome=self.find_w.text())

        try:
            self.cur.execute(self.sql)
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]
        except Exception as e:
            return

        self.tabledata = data

        if len(data) == 0:
            self.tabledata = ["", "", "", "", "", "", "", ""]
        else:
            self.tabledata = data

        try:
            self.tm = MyTableModel(self.tabledata, self.header, self)
            # set the table model
            self.totalItems = self.tm.rowCount(self)
            self.tv.setModel(self.tm)
        except Exception as e:
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
        tool.addSeparator()
        tool.addAction(self.new)
        tool.addAction(self.update)
        tool.addSeparator()
        tool.addAction(self.delete)
        tool.addSeparator()
        tool.addAction(self.print)

        tool.setAllowedAreas(Qt.TopToolBarArea|Qt.BottomToolBarArea)
        self.addToolBarBreak(Qt.BottomToolBarArea)
        self.addToolBar(tool)

        ######################################################################
        self.new.triggered.connect(self.new_data)
        self.delete.triggered.connect(self.removerow)
        self.tv.doubleClicked.connect(self.update_data)
        self.update.triggered.connect(self.update_data)
        # self.connect(self.delete, SIGNAL("triggered()"), self.removerow)
        # # self.connect(self.update, SIGNAL("triggered()"), self.updatedata)
        # self.print.triggered.connect(self.printForm)

    def create_statusbar(self):
        estado = QStatusBar(self)
    
        self.items = QLabel("Total Items: %s" % self.totalItems)
        estado.addWidget(self.items)
        self.setStatusBar(estado)

    def clickedslot(self, index):

        self.row = int(index.row())

        indice= self.tm.index(self.row, 0)
        self.current_id = indice.data()

    def new_data(self):

        cl = user(self)
        cl.setModal(True)
        cl.show()

    def update_data(self):

        if self.current_id == "":
            QMessageBox.information(self, "Info", "Selecione o registo a actualizar na tabela")
            return

        cl = user(self)
        cl.u_id.setText(self.current_id)
        cl.mostrar_registo()
        cl.setModal(True)
        cl.show()

    def removerow(self):
    
        if self.current_id == "":
            QMessageBox.information(self, "Info", "Selecione o registo a apagar na tabela")
            return

        if self.current_id not in LISTA_USERS:
            if QMessageBox.question(self, "Pergunta", str("Deseja eliminar o registo %s?") % self.current_id,
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                sql = """delete from users WHERE cod = "{codigo}" """.format(codigo=str(self.current_id))
                self.cur.execute(sql)
                self.conn.commit()
                self.fill_table()
                QMessageBox.information(self, "Sucesso", "Item apagado com sucesso...")
        else:
            QMessageBox.warning(self, "Erro", "Usuário não pode ser apagado")

# if __name__ == '__main__':
#
#     app = QApplication(sys.argv)
#
#     helloPythonWidget = MainWindow()
#     helloPythonWidget.show()
#
#     sys.exit(app.exec_())