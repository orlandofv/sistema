# -*- coding: utf-8 -*-

import sys
import operator
from decimal import Decimal
import os
import subprocess
import csv

from PyQt5.QtWidgets import QApplication, QTableView, QAbstractItemView, QMessageBox, QToolBar, \
    QLineEdit, QLabel, QStatusBar, QAction, QMainWindow, qApp, QHBoxLayout, QDateEdit, QGroupBox, QCalendarWidget, \
    QFileDialog, QProgressDialog

from PyQt5.QtGui import QIcon, QTextDocument
from PyQt5.QtPrintSupport import QPrintPreviewDialog
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant, QDate
import sqlite3 as lite

DB_FILENAME = 'dados.tsdb'


class Lista_de_Cheque(QMainWindow):
    def __init__(self, parent=None):
        super(Lista_de_Cheque, self).__init__(parent)

        # controla o codigo
        self.current_id = ""
        self.lista_de_Cheques = []
        self.list_de_dados_normal = []

        # Header for the table
        self.header = [qApp.tr('Cod'), "Cliente", qApp.tr('Nº de Cheque'), "Banco", qApp.tr('Montante'),
                       qApp.tr('Data de Entrada'), qApp.tr('Data de Vencimento'), qApp.tr('Notas'), ""]

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
        self.procurar_registo.textEdited.connect(self.fill_table)

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
        data_inicial = QDate(self.data_inicial.date()).toString("yyyy-MM-dd")
        data_final = QDate(self.data_final.date()).toString("yyyy-MM-dd")

        sql = """select p.cod, c.nome, p.cheque_numero, p.banco, p.valor, p.data_entrada, p.data_vencimento, p.obs 
        FROM cheques p INNER JOIN clientes c ON c.cod=p.cod_cliente WHERE  ((c.nome like "%{nome}%" 
        OR p.cheque_numero like "%{nome}%" or p.valor like "%{nome}%" or p.banco like "%{nome}%") 
        AND p.data_entrada BETWEEN "{i}" AND "{f}") """.format(nome=self.procurar_registo.text(),
                                                               i=data_inicial, f=data_final)
        try:
            self.cur.execute(sql)
            lista = self.cur.fetchall()
            self.list_de_dados_normal = lista

            data = [list(str(item) for item in t) for t in lista]

            i = 0
            for x in data:
                x[4] = "{:20,.2f}".format(Decimal(x[4]))
                x[5] = QDate.fromString(x[5], "yyyy-MM-dd").toString("dd-MM-yyyy")
                x[6] = QDate.fromString(x[6], "yyyy-MM-dd").toString("dd-MM-yyyy")
                i += 1

            self.lista_de_Cheques = data

        except Exception as e:
            print(e)
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

            self.tv.setColumnHidden(0, True)

        except Exception as e:
            return
        # # set row height
        nrows = len(self.tabledata)
        for row in range(nrows):
            self.tv.setRowHeight(row, 25)

        self.create_statusbar()

    def create_toolbar(self):
        find = QLabel(qApp.tr("Procurar") + "  ")
        self.procurar_registo = QLineEdit(self)
        self.procurar_registo.setMaximumWidth(200)

        novo_registo = QAction(QIcon('./icons/add_2.ico'), qApp.tr("Novo"), self)
        apagar_registo = QAction(QIcon('./images/editdelete.png'), qApp.tr("Eliminar"), self)
        imprimir_dados = QAction(QIcon('./images/fileprint.png'), qApp.tr("Imprimir"), self)
        actualizar_registo = QAction(QIcon('./images/pencil.png'), qApp.tr("Editar"), self)
        export_csv = QAction(QIcon('./images/icons8-export-csv-50.png'), "Exportar para CSV", self)
        export_csv.triggered.connect(self.exportar_csv)

        caixa_de_datas = QHBoxLayout()
        caixa_de_datas.setContentsMargins(5, 0, 5, 5)

        calendario = QCalendarWidget()
        calendario1 = QCalendarWidget()

        self.data_inicial = QDateEdit()
        self.data_inicial.setCalendarPopup(True)
        self.data_inicial.setCalendarWidget(calendario)
        self.data_final = QDateEdit()
        self.data_final.setCalendarPopup(True)
        self.data_final.setCalendarWidget(calendario1)

        self.data_inicial.setDate(QDate.currentDate().addDays(-30))
        self.data_final.setDate(QDate.currentDate())

        caixa_de_datas.addWidget(QLabel(" Data Inicial: "))
        caixa_de_datas.addWidget(self.data_inicial)
        caixa_de_datas.addWidget(QLabel(" Data Final: "))
        caixa_de_datas.addWidget(self.data_final)
        caixa_widget = QGroupBox("Datas")
        caixa_widget.setLayout(caixa_de_datas)

        tool = QToolBar()
        tool.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        tool.setContextMenuPolicy(Qt.PreventContextMenu)
        tool.addWidget(find)
        tool.addWidget(self.procurar_registo)
        tool.addSeparator()
        tool.addAction(novo_registo)
        tool.addAction(actualizar_registo)
        tool.addSeparator()
        tool.addAction(apagar_registo)
        tool.addSeparator()
        tool.addAction(imprimir_dados)
        tool.addSeparator()
        tool.addAction(export_csv)
        tool.addWidget(caixa_widget)

        tool.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        self.addToolBarBreak(Qt.BottomToolBarArea)
        self.addToolBar(tool)

        ######################################################################
        novo_registo.triggered.connect(self.new_data)
        apagar_registo.triggered.connect(self.removerow)
        self.tv.doubleClicked.connect(self.update_data)
        actualizar_registo.triggered.connect(self.update_data)
        imprimir_dados.triggered.connect(self.imprime_lista)

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

        from cheques import Cheque
        cl = Cheque(self)
        cl.setModal(True)
        cl.show()

    def update_data(self):

        if self.current_id == "":
            QMessageBox.information(self, "Info", "Selecione o registo a actualizar na tabela")
            return

        from cheques import Cheque
        cl = Cheque(self)
        cl.cod_cheque = self.current_id
        cl.mostrar_registo(self.current_id)
        cl.setModal(True)
        cl.show()

    def removerow(self):

        if self.current_id == "":
            QMessageBox.information(self, "Info", "Selecione o registo a apagar na tabela")
            return

        if self.current_id != "CL20181111111":
            if QMessageBox.question(self, "Pergunta", str("Deseja eliminar o registo %s?") % self.current_id,
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                sql = """delete from cheques WHERE cod = "{codigo}" """.format(codigo=str(self.current_id))

                try:
                    self.cur.execute(sql)
                    self.conn.commit()
                    self.fill_table()
                    QMessageBox.information(self, "Sucesso", "Item apagado com sucesso...")
                except Exception as e:
                    QMessageBox.warning(self, "Erro", "Impossivel apagar conta.")
        else:
            QMessageBox.warning(self, "Erro", "Cheque não pode ser apagado.")

    def imprime_lista(self):
        """Imprime no ecra a Lista geral de produtos baseado em um Critério"""
        if self.lista_de_Cheques == []:
            return

        dados = self.lista_de_Cheques

        html = "<center> <h2> Lista de Cheques </h2> </center>"
        html += "<hr/>"

        html += "<br/>"

        html += "<table border=0 width = 80mm style='border: thin;'>"

        html += "<tr style='background-color:#c0c0c0;'>"
        html += "<th width = 15%>{}</th>".format(self.header[1])
        html += "<th width = 20%>{}</th>".format(self.header[2])
        html += "<th width = 15%>{}</th>".format(self.header[3])
        html += "<th width = 10%>{}</th>".format(self.header[4])
        html += "<th width = 15%>{}</th>".format(self.header[5])
        html += "<th width = 15%>{}</th>".format(self.header[6])
        html += "<th width = 10%>{}</th>".format(self.header[7])
        html += "</tr>"

        for cliente in dados:
            html += """<tr> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td>  
            </tr>""".format(cliente[1], cliente[2], cliente[3], cliente[4], cliente[5], cliente[6], cliente[7])

        dados_total = self.list_de_dados_normal

        total = 0
        for x in dados_total:
            total += x[4]

        html += """<tr style="font: bold;"> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td> 
        <td>{}</td> </tr>""".format("TOTAL", "", "", "{:20,.2f}".format(total), "", "", "")
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

    def exportar_csv(self):

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

        data = self.list_de_dados_normal
        csv_header = self.header

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
                csv_write = csv.writer(lista_produtos, delimiter=',', quotechar='"',
                                       quoting=csv.QUOTE_MINIMAL, dialect='excel')
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
    helloPythonWidget = Lista_de_Cheque()
    helloPythonWidget.show()
#
    sys.exit(app.exec_())