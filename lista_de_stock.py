# -*- coding: utf-8 -*-

import sys
import csv
import subprocess
import os

from PyQt5.QtWidgets import QApplication, QTableView, QAbstractItemView, QMessageBox, QToolBar, \
    QLineEdit, QLabel, QStatusBar, QAction, QMainWindow, qApp, QTabWidget, QComboBox, QFileDialog, QProgressDialog, \
    QDateEdit, QCalendarWidget

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QDate
import sqlite3 as lite

from stock import Cliente
from sortmodel import MyTableModel
from pagamentos_fornecedores import Pagamentos
from striped_table import StripedTable
DB_FILENAME = 'dados.tsdb'


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.entradas_data = []
        # controla o codigo
        self.current_id = ""
        self.current_id2 = ""
        self.codarmazem = ""
        self.totalItems = 0
        self.stock_totalItems = 0
        self.entradas_totalItems = 0
        self.saidas_totalItems = 0
        self.movimento_totalItems = 0
        self.empresa = None

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

        self.find_w.textEdited.connect(self.actualizar_dados)

        # Search the data

    def docs_tabela(self):
        # create the view
        self.tv = StripedTable(self)

    def stock_tabela(self):
        # create the view
        self.tv2 = StripedTable(self)

    def saidas_tabela(self):
        # create the view
        self.tv3 = StripedTable(self)

    def entradas_tabela(self):
        # create the view
        self.tv4 = StripedTable(self)

    def movimento_stock_tabela(self):
        # create the view
        self.tv5 = StripedTable(self)

    def ui(self):

        self.docs_tabela()
        # self.stock_tabela()
        self.saidas_tabela()
        self.entradas_tabela()
        self.movimento_stock_tabela()

        self.tabulador = QTabWidget()
        self.tabulador.addTab(self.tv, QIcon("./icons/caixa.ico"), "Lista de Facturas")
        # self.tabulador.addTab(self.tv2, QIcon("./icons/Deleket-Soft-Scraps-Clipboard.ico"), "Lista de Stock")
        self.tabulador.addTab(self.tv4, QIcon("./icons/Deleket-Soft-Scraps-Clipboard.ico"), "Lista de Entradas")
        self.tabulador.addTab(self.tv3, QIcon("./icons/Deleket-Soft-Scraps-Clipboard.ico"), "Lista de Saídas")
        self.tabulador.addTab(self.tv5, QIcon("./icons/Deleket-Soft-Scraps-Clipboard.ico"), "Movimento de Stock")

        self.tabulador.currentChanged.connect(self.total_items)

        self.setCentralWidget(self.tabulador)
        self.create_toolbar()
        self.enche_armazem()

    def enche_armazem(self):
        sql = """SELECT nome from armazem WHERE estado=1 ORDER BY nome"""

        self.cur.execute(sql)
        data = self.cur.fetchall()
        self.armazem_combo.clear()
        lista = []

        if len(data) > 0:
            for item in data:

                lista.append(item[0])

        lista.append("Todos")
        self.armazem_combo.addItems(lista)

    def getcodarmazem(self, nomearmazem):
        if nomearmazem == "":
            self.codarmazem = ""
            return

        sql = """SELECT cod from armazem WHERE nome="{}" """.format(nomearmazem)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            self.codarmazem = data[0][0]

    def connect_db(self):
        # Connect to database and retrieves data
        try:
            self.conn = lite.connect(DB_FILENAME)
            self.cur = self.conn.cursor()

        except Exception as e:
            sys.exit(True)

    def enterEvent(self, *args, **kwargs):
        self.fill_table()

    def fill_table(self):

        sql = """select stock.cod, fornecedores.nome, stock.numero, stock.taxa, stock.total, stock.pago, stock.saldo, 
        stock.estado, stock.created, stock.created_by from stock 
        JOIN fornecedores ON fornecedores.cod=stock.fornecedor  
        WHERE numero like "%{numero}%" or fornecedor like "%{fornecedor}%" 
        """.format(numero=self.find_w.text(), fornecedor=self.find_w.text())

        try:
            self.cur.execute(sql)
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]
        except Exception as e:
            return

        self.factura_data = []

        if len(data) > 0:
            for item in data:
                lista = list(item)
                if int(lista[7]) == 1:
                    lista[7] = "Finalizado"
                else:
                    lista[7] = "Pendente"
                self.factura_data.append(lista)

        tabledata = self.factura_data

        # Header for the table
        self.factura_header = ["Código", "Fornecedor", "No do Documento", "IVA", "Total", "Valor Pago", "Saldo", "Estado",
                  "Data de Criação", "Criado Por"]

        try:
            self.tm = MyTableModel(tabledata, self.factura_header, self)
            # set the table model
            self.totalItems = self.tm.rowCount(self)
            self.tv.setModel(self.tm)
        except Exception as e:
            return
        # # set row height
        nrows = len(tabledata)
        for row in range(nrows):
            self.tv.setRowHeight(row, 25)
        
    def fill_table_entradas(self):

        if self.armazem_combo.currentText() == "Todos":
            entradas_sql = """select * from entradas WHERE (nome like "%{procura}%" or doc_numero like "%{procura}%" 
                    or entidade like "%{procura}%") AND date_created BETWEEN '{inicial}' AND '{final}' 
                    ORDER BY date_created, nome 
                    """.format(procura=self.find_w.text(),
                               inicial=QDate(self.data_inicial.date()).toString('yyyy-MM-dd'),
                               final=QDate(self.data_final.date()).toString('yyyy-MM-dd'))

        else:
            entradas_sql = """select * FROM entradas WHERE (nome like "%{procura}%" or doc_numero like "%{procura}%" 
            or entidade like "%{procura}%") AND nomearmazem="{armazem}" AND date_created 
            BETWEEN '{inicial}' AND '{final}' ORDER BY date_created, nome  
            """.format(procura=self.find_w.text(), armazem=self.armazem_combo.currentText(),
                               inicial=QDate(self.data_inicial.date()).toString('yyyy-MM-dd'),
                               final=QDate(self.data_final.date()).toString('yyyy-MM-dd'))
        try:
            self.cur.execute(entradas_sql)
            self.entradas_data = [tuple(str(item) for item in t) for t in self.cur.fetchall()]

        except Exception as e:
            QMessageBox.warning(self, "Erro", "Erro.\n{}.".format(e))
            return False

        if len(self.entradas_data) == 0:
            tabledata = ["", "", "", "", "", "", "", "", "", ""]
        else:
            tabledata = self.entradas_data

        header = ["cod", "Documento", "Cod Produto", "Produto", "QTY", "Preço", "Custo","Total", "Entidade", "Data",
                  "Armazém", "Usuário"]

        try:
            tm = MyTableModel(tabledata, header, self)
            # set the table model
            self.entradas_totalItems = tm.rowCount(self)
            self.tv4.setModel(tm)
            self.tv4.setColumnHidden(0, True)

        except Exception as e:
            QMessageBox.warning(self, "Erro", "Erro.\n{}.".format(e))
            return False
        # # set row height
        nrows = len(tabledata)
        for row in range(nrows):
            self.tv4.setRowHeight(row, 25)

        return True

    def fill_table_saidas(self):

        if self.armazem_combo.currentText() == "Todos":
            saidas_sql = """select * from saidas WHERE (nome like "%{procura}%" or 
                    doc_numero like "%{procura}%" or entidade like "%{procura}%") AND date_created BETWEEN '{inicial}'
                     AND '{final}' ORDER BY date_created, nome 
                    """.format(procura=self.find_w.text(),
                               inicial=QDate(self.data_inicial.date()).toString('yyyy-MM-dd'),
                               final=QDate(self.data_final.date()).toString('yyyy-MM-dd'))

        else:
            saidas_sql = """select * from saidas WHERE (nome like "%{procura}%" or 
            doc_numero like "%{procura}%" or entidade like "%{procura}%") AND nomearmazem="{armazem}" 
            AND date_created BETWEEN '{inicial}' AND '{final}' ORDER BY date_created, nome 
            """.format(procura=self.find_w.text(),
                       armazem=self.armazem_combo.currentText(),
                               inicial=QDate(self.data_inicial.date()).toString('yyyy-MM-dd'),
                               final=QDate(self.data_final.date()).toString('yyyy-MM-dd'))

        try:
            self.cur.execute(saidas_sql)
            self.saidas_data = [tuple(str(item) for item in t) for t in self.cur.fetchall()]

        except Exception as e:
            QMessageBox.warning(self, "Erro", "Erro.\n{}.".format(e))
            return False

        if len(self.saidas_data) == 0:
            tabledata = ["", "", "", "", "", "", "", "", "", ""]
        else:
            tabledata = self.saidas_data

        header = ["cod", "Documento", "Cod Produto", "Produto", "QTY", "Preço", "Custo",
                  "Total" , "Entidade", "Data",
                  "Armazém", "Usuário"]

        try:
            tm = MyTableModel(tabledata, header, self)
            # set the table model
            self.saidas_totalItems = tm.rowCount(self)
            self.tv3.setModel(tm)
            self.tv3.setColumnHidden(0, True)
        except Exception as e:
            QMessageBox.warning(self, "Erro", "Erro.\n{}.".format(e))
            return False
        # # set row height
        nrows = len(tabledata)
        for row in range(nrows):
            self.tv3.setRowHeight(row, 25)

        return True

    def fill_table_movimento_stock(self):

        if self.armazem_combo.currentText() == "Todos":
            self.movimento_stock_sql = """select * from movimento_stock WHERE (nome like "%{procura}%" or 
                        doc_numero like "%{procura}%" or entidade like "%{procura}%") AND date_created 
                        BETWEEN '{inicial}' AND '{final}' ORDER BY date_created desc, nome 
                        """.format(procura=self.find_w.text(),
                               inicial=QDate(self.data_inicial.date()).toString('yyyy-MM-dd'),
                               final=QDate(self.data_final.date()).toString('yyyy-MM-dd'))
        else:
            self.movimento_stock_sql = """select * from movimento_stock WHERE (nome like "%{procura}%" or 
            doc_numero like "%{procura}%" or entidade like "%{procura}%") AND nomearmazem="{armazem}" 
            AND date_created BETWEEN '{inicial}' AND '{final}' ORDER BY date_created desc, nome 
            """.format(procura=self.find_w.text(),
                       armazem=self.armazem_combo.currentText(),
                               inicial=QDate(self.data_inicial.date()).toString('yyyy-MM-dd'),
                               final=QDate(self.data_final.date()).toString('yyyy-MM-dd'))

        try:
            self.cur.execute(self.movimento_stock_sql)
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]
        except Exception as e:
            print(e)
            return

        if len(data) == 0:
            tabledata = ["", "", "", "", "", "", "", "", "", ""]
        else:
            tabledata = data

        header = ["cod", "Documento", "Cod Produto", "Produto", "QTY", "Custo","Preço", "Total", "Entidade", "Data",
                  "Armazém", "Usuário"]

        try:
            tm = MyTableModel(tabledata, header, self)
            # set the table model
            self.movimento_totalItems = tm.rowCount(self)
            self.tv5.setModel(tm)
            self.tv5.setColumnHidden(0, True)
        except Exception as e:
            QMessageBox.warning(self, "Erro", "Erro.\n{}.".format(e))
            return False

        # # set row height
        nrows = len(tabledata)
        for row in range(nrows):
            self.tv5.setRowHeight(row, 25)

        return True

    def create_toolbar(self):

        self.find_w = QLineEdit(self)
        self.find_w.setPlaceholderText("Procurar")
        self.find_w.setMaximumWidth(200)
        self.armazem_combo = QComboBox()

        self.new = QAction(QIcon('./icons/add_2.ico'), qApp.tr("Novo"), self)
        self.delete = QAction(QIcon('./images/editdelete.png'), qApp.tr("Eliminar"), self)
        self.print = QAction(QIcon('./images/fileprint.png'),qApp.tr("Imprimir"), self)
        self.update = QAction(QIcon('./images/pencil.png'), qApp.tr("Editar"), self)
        export_csv = QAction(QIcon('./images/icons8-export-csv-50.png'), "Exportar para CSV", self)
        pagamento = QAction(QIcon('./icons/payment.ico'), "Pagamento", self)
        refresh = QAction(QIcon('./icons/refresh.ico'), "", self)

        calendario = QCalendarWidget()
        calendario2 = QCalendarWidget()

        self.data_inicial = QDateEdit()
        self.data_inicial.setDate(QDate.currentDate().addDays(-30))
        self.data_inicial.setCalendarPopup(True)
        self.data_inicial.setCalendarWidget(calendario)

        self.data_final = QDateEdit()
        self.data_final.setDate(QDate.currentDate())
        self.data_final.setCalendarPopup(True)
        self.data_final.setCalendarWidget(calendario2)

        tool = QToolBar()
        tool.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        tool.setContextMenuPolicy(Qt.PreventContextMenu)

        tool.addWidget(QLabel('  De: '))
        tool.addWidget(self.data_inicial)
        tool.addWidget(QLabel('  A:  '))
        tool.addWidget(self.data_final)
        tool.addSeparator()

        tool.addWidget(self.find_w)
        tool.addAction(refresh)
        tool.addSeparator()
        tool.addWidget(QLabel(" Armazém "))
        tool.addWidget(self.armazem_combo)
        tool.addSeparator()
        tool.addAction(self.new)
        tool.addAction(self.update)
        tool.addSeparator()
        tool.addAction(self.delete)
        tool.addSeparator()
        tool.addAction(self.print)
        tool.addAction(export_csv)
        # tool.addSeparator()
        # tool.addAction(pagamento)

        tool.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        self.addToolBarBreak(Qt.BottomToolBarArea)
        self.addToolBar(tool)

        ######################################################################
        self.new.triggered.connect(self.new_data)
        self.delete.triggered.connect(self.removerow)
        self.tv.clicked.connect(self.clicked_slot)
        self.tv.doubleClicked.connect(self.update_data)
        self.update.triggered.connect(self.update_data)
        export_csv.triggered.connect(self.exportar_csv)
        pagamento.triggered.connect(self.novo_pagamento)
        refresh.triggered.connect(self.actualizar_dados)

    def clicked_slot(self, index):
        id = self.tv.model().index(index.row(), 0)
        self.current_id = id.data()

    def actualizar_dados(self):

        if self.tabulador.currentIndex() == 0:
            self.fill_table()

        if self.tabulador.currentIndex() == 1:
            self.fill_table_entradas()

        if self.tabulador.currentIndex() == 2:
            self.fill_table_saidas()

        if self.tabulador.currentIndex() == 3:
            self.fill_table_movimento_stock()

    def create_statusbar(self, totalitems):
        estado = QStatusBar(self)

        self.items = QLabel("Total Items: %s" % totalitems)
        estado.addWidget(self.items)
        self.setStatusBar(estado)

    def novo_pagamento(self):
        pg = Pagamentos(self)
        pg.setModal(True)
        pg.show()

    def total_items(self):

        if self.tabulador.currentIndex() == 0:
            self.create_statusbar(self.totalItems)
        elif self.tabulador.currentIndex() == 1:
            self.create_statusbar(self.entradas_totalItems)
        elif self.tabulador.currentIndex() == 2:
            self.create_statusbar(self.saidas_totalItems)
        elif self.tabulador.currentIndex() == 3:
            self.create_statusbar(self.movimento_totalItems)

    def clickedslot(self, index):

        self.row = int(index.row())

        indice = self.tm.index(self.row, 0)
        self.current_id = indice.data()

    def clickedslot2(self, index):

        self.row = int(index.row())

        indice = self.tm.index(self.row, 0)
        self.current_id2 = indice.data()

    def new_data(self):

        cl = Cliente(self)
        cl.setModal(True)
        cl.showMaximized()

    def update_data(self):

        if self.current_id == "":
            QMessageBox.information(self, "Info", "Selecione o registo a actualizar na tabela")
            return

        sql = """SELECT estado from stock where cod="{}" """.format(self.current_id)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            cl = Cliente(self)

            if int(data[0][0]) == 1:
                if QMessageBox.warning(self, "Aviso", """Este documento já foi finalizado.
                \nSe reabrir as quantidades dos Produtos serão retiradas.\nDesseja continuar?""",
                                       QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
                    if cl.normalizar_stock(self.current_id) is False:
                        QMessageBox.warning(self, "Erro de normalização", "Stock não normalizado")
                    else:
                        QMessageBox.information(self, "Sucesso", "Quantidades retiradas com sucesso!")
                else:
                    return

            cl.codigogeral = self.current_id
            cl.cod.setText(self.current_id)
            cl.gravar_fornecedor.setEnabled(False)
            cl.ativar_fornecedor.setEnabled(True)
            cl.desabilitarfornecedor()
            cl.mostrar_registo(self.current_id)
            cl.setModal(True)
            cl.showMaximized()

    def verifica_finalizado(self, codstock):
        """Verifica se o registo foi finalizado ou nao"""
        sql = """SELECT estado FROM stock WHERE cod="{}" AND estado=1 """.format(codstock)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return True
        else:
            return False

    def removerow(self):

        if self.current_id == "":
            QMessageBox.information(self, "Info", "Selecione o registo a apagar na tabela")
            return

        if QMessageBox.question(self, "Pergunta", str("Deseja eliminar o registo %s?") % self.current_id,
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:

            if self.verifica_finalizado(self.current_id) is True:
                if QMessageBox.question(self, "Pergunta", "O Registo vai diminuir quantidades dos respectivos "
                                                          "pordutos.\nDeseja continuar?",
                                        QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                    from stock import Cliente
                    cl = Cliente(self)
                    cl.normalizar_stock(self.current_id)
                else:
                    return
            else:
                from stock import Cliente
                cl = Cliente(self)
                cl.normalizar_stock(self.current_id)

            stokdetalhe_sql = """DELETE FROM stockdetalhe WHERE codstock="{}" """.format(self.current_id)
            sql = """delete from stock WHERE cod = "{codigo}" """.format(codigo=str(self.current_id))

            try:
                self.cur.execute(stokdetalhe_sql)
                self.cur.execute(sql)
                self.conn.commit()
            except Exception as e:
                QMessageBox.information(self, "Eliminar registo", "Impossivel eliminar registo. Erro: "
                                                                  "{erro}".format(erro=e))
                return

            self.fill_table()
            QMessageBox.information(self, "Sucesso", "Item apagado com sucesso...")

    def exportar_csv(self):

        if self.tabulador.currentIndex() == 1:
            self.exportar_entradas_csv()
        elif self.tabulador.currentIndex() == 2:
            self.exportar_saidas_csv()
        elif self.tabulador.currentIndex() == 3:
            self.exportar_movimento_csv()
        else:
            self.exportar_factura()

    def exportar_factura(self):

        if len(self.factura_data) == 0: return

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

        data = self.factura_data
        csv_header = self.factura_header

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
                csv_write.writerow([self.empresa])
                csv_write.writerow(["CC de Fornecedores de {} a {}".format(self.data_inicial.date().toString('dd-MM-yyyy'),
                                                                  self.data_final.date().toString('dd-MM-yyyy'))])
                csv_write.writerow([])
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

    def exportar_entradas_csv(self):

        if len(self.entradas_data) == 0: return

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

        data = self.entradas_data

        csv_header = ["cod", "Documento", "Cod Produto", "Produto", "QTY", "Preço", "Custo","Total", "Entidade", "Data",
                  "Armazém", "Usuário"]

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
                csv_write.writerow([self.empresa])
                csv_write.writerow(["Entradas do dia {} a {}".format(self.data_inicial.date().toString('dd-MM-yyyy'),
                                                                  self.data_final.date().toString('dd-MM-yyyy'))])
                csv_write.writerow([])
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

    def exportar_saidas_csv(self):

        if len(self.saidas_data) == 0: return

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

        data = self.saidas_data

        csv_header = ["cod", "Documento", "Cod Produto", "Produto", "QTY", "Preço", "Custo","Total", "Entidade", "Data",
                      "Armazém", "Usuário"]

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
                csv_write.writerow([self.empresa])
                csv_write.writerow(["Saidas do dia {} a {}".format(self.data_inicial.date().toString('dd-MM-yyyy'),
                                                                  self.data_final.date().toString('dd-MM-yyyy'))])
                csv_write.writerow([])
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

    def exportar_movimento_csv(self):

        if self.movimento_stock_sql == "": return

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

        self.cur.execute(self.movimento_stock_sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        csv_header = ["cod", "Documento", "Cod Produto", "Produto", "QTY", "Custo", "Preço", "Total", "Entidade", "Data",
                      "Armazém", "Usuário"]

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
                csv_write.writerow([self.empresa])
                csv_write.writerow(["Movimento do dia {} a {}".format(self.data_inicial.date().toString('dd-MM-yyyy'),
                                                                  self.data_final.date().toString('dd-MM-yyyy'))])
                csv_write.writerow([])
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

if __name__ == '__main__':

    app = QApplication(sys.argv)

    helloPythonWidget = MainWindow()
    helloPythonWidget.show()

    sys.exit(app.exec_())

