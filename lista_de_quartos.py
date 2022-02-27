# -*- coding: utf-8 -*-

import sys
import operator

from PyQt5.QtWidgets import QApplication, QTableView, QAbstractItemView, QMessageBox, QToolBar, \
    QLineEdit, QLabel, QStatusBar, QAction, QMainWindow, qApp

from PyQt5.QtGui import QIcon, QTextDocument
from PyQt5.QtPrintSupport import QPrintPreviewDialog
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant
import sqlite3 as lite

DB_FILENAME = 'dados.tsdb'


class Lista_de_Quartos(QMainWindow):
    def __init__(self, parent=None):
        super(Lista_de_Quartos, self).__init__(parent)

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
        header = [qApp.tr('Número'), qApp.tr('Preco'), "Categoria", qApp.tr('Estado'), qApp.tr('Comentários')]

        self.sql = """select quartos.cod, quartos.preco, categorias.categoria, quartos.ocupado, quartos.obs 
        from quartos INNER JOIN categorias ON categorias.cod=quartos.cod_preco WHERE  quartos.cod like "%{nome}%" 
        OR quartos.ocupado like "%{nome}%" or quartos.preco like "%{nome}%" or categorias.categoria like "%{nome}%" 
        """.format(nome=self.find_w.text())

        try:
            self.cur.execute(self.sql)
            lista = self.cur.fetchall()

            data = [tuple(str(item) for item in t) for t in lista]

            nova_lista = []

            for item in data:

                i = list(item)

                if i[3] == '0':
                    i[3] = "Livre"
                else:
                    i[3] = "Ocupado"

                nova_lista.append(i)

        except Exception as e:
            print(e)
            return

        if len(data) == 0:
            self.tabledata = ["", "", "", "", "", "", "", ""]
        else:
            self.tabledata = nova_lista

        try:
            self.tm = MyTableModel(self.tabledata, header, self)
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
        self.print = QAction(QIcon('./images/fileprint.png'), qApp.tr("Imprimir"), self)
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

        tool.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        self.addToolBarBreak(Qt.BottomToolBarArea)
        self.addToolBar(tool)

        ######################################################################
        self.new.triggered.connect(self.new_data)
        self.delete.triggered.connect(self.removerow)
        self.tv.doubleClicked.connect(self.update_data)
        self.update.triggered.connect(self.update_data)
        self.print.triggered.connect(self.imprime_lista)

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

        from quartos import Quarto
        cl = Quarto(self)
        cl.setModal(True)
        cl.show()

    def update_data(self):

        if self.current_id == "":
            QMessageBox.information(self, "Info", "Selecione o registo a actualizar na tabela")
            return

        from quartos import Quarto
        cl = Quarto(self)
        cl.cod.setValue(int(self.current_id))
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
                sql = """delete from quartos WHERE cod = "{codigo}" """.format(codigo=str(self.current_id))

                try:
                    self.cur.execute(sql)
                    self.conn.commit()
                    self.fill_table()
                    QMessageBox.information(self, "Sucesso", "Item apagado com sucesso...")
                except Exception as e:
                    QMessageBox.warning(self, "Erro", "Impossivel apagar quarto.")
        else:
            QMessageBox.warning(self, "Erro", "Quarto não pode ser apagado.")

    def imprime_lista(self):
        """Imprime no ecra a Lista geral de produtos baseado em um Critério"""
        if self.sql == "":
            return

        self.cur.execute(self.sql)
        dados = self.cur.fetchall()

        html = "<center> <h2> Lista de Quartos </h2> </center>"
        html += "<hr/>"

        html += "<br/>"

        html += "<table border=0 width = 80mm style='border: thin;'>"

        html += "<tr style='background-color:#c0c0c0;'>"
        html += "<th width = 15%>Número</th>"
        html += "<th width = 15%>Preço</th>"
        html += "<th width = 20%>Categoria</th>"
        html += "<th width = 15%>Estado</th>"
        html += "<th width = 35%>Comentários</th>"
        html += "</tr>"

        for cliente in dados:

            if cliente[3] == 0:
                estado = "Livre"
            else:
                estado = "Ocupado"

            html += """<tr> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td>  
            </tr>""".format(cliente[0], cliente[1], cliente[2], estado, cliente[4])
        html += "</table>"

        html += """<p style = "margin: 0 auto;
                   font-family: Arial, Helvetica, sans-serif;
                   position: absolute;
                   bottom: 10px;">processador por computador</p>"""

        document = QTextDocument()

        document.setHtml(html)

        dlg = QPrintPreviewDialog(self)
        dlg.paintRequested.connect(document.print_)
        dlg.showMaximized()
        dlg.exec_()

    def enterEvent(self, *args, **kwargs):
        self.fill_table()


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


if __name__ == '__main__':

    app = QApplication(sys.argv)
#
    helloPythonWidget = Lista_de_Quartos()
    helloPythonWidget.show()
#
    sys.exit(app.exec_())