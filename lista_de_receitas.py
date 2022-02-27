# -*- coding: utf-8 -*-

import sys
import decimal

from PyQt5.QtWidgets import QApplication, QTableView, QAbstractItemView, QMessageBox, QToolBar, \
    QLineEdit, QLabel, QStatusBar, QAction,  qApp, QMainWindow, QComboBox

from PyQt5.QtGui import QIcon, QTextDocument
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtPrintSupport import QPrintPreviewDialog

import sqlite3 as lite

from sortmodel import MyTableModel
from receitas import TRANSACOES

DB_FILENAME = 'dados.tsdb'


class ListaDeReceitas(QMainWindow):
    def __init__(self, parent=None):
        super(ListaDeReceitas, self).__init__(parent)

        # controla o codigo
        self.current_id = ""
        self.sql = ""
        self.valor_anterior = decimal.Decimal(0)
        self.tipo_transacao = 0

        # Connect the Database
        if self.parent() is not None:
            self.user = self.parent().user
            self.codarmazem = self.parent().codarmazem
            self.caixa_numero = self.parent().caixa_numero
            self.cur = self.parent().cur
            self.conn = self.parent().conn
        else:
            self.user = None
            self.codarmazem = None
            self.caixa_numero = None
            self.cur = None
            self.conn = None

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
            sys.exit(True)

    def printlist(self, sql):

        if self.parent() is not None:
            logo = self.parent().empresa_logo
            licenca = self.parent().licenca
        else:
            logo = ""
            licenca = ""

        self.cur.execute(sql)
        data = self.cur.fetchall()

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

        html += "<h1> Lista de Despesas e Receitas </h1>"
        html += "<hr/>"

        html += "<table border='0' width = 80mm style='border: 1px;'>"
        html += "<tr style='background-color: gray;'>"
        html += "<th width = 10% align='center'>Trans.</th>"
        html += "<th width = 5%>Estado</th>"
        html += "<th width = 15%>Valor</th>"
        html += "<th width = 30%>Descrição</th>"
        html += "<th width = 10% align='right'>Criado em</th>"
        html += "<th width = 10% align='right'>Mod. em</th>"
        html += "<th width = 10% align='right'>Criado por</th>"
        html += "<th width = 10% align='right'>Criado por</th>"
        html += "</tr>"

        total_receitas = decimal.Decimal(0.00)
        total_despesas = decimal.Decimal(0.00)

        for cliente in self.data:

            tipo = int(self.combo_lista_de_trasacoes.findText(cliente[1]))

            if  tipo == 0:
                total_despesas += decimal.Decimal(cliente[3])
            else:
                total_receitas += decimal.Decimal(cliente[3])

            html += """<tr> <td align='center'>{}</td>  <td>{}</td> <td  align="right">{}</td>  <td>{}</td>  
            <td>{}</td> <td>{}</td>  <td>{}</td>  
            <td>{}</td> </tr> """.format(cliente[1], cliente[2], cliente[3], cliente[4], cliente[5],
                                         cliente[6], cliente[7], cliente[8])

        html += """<tr> <th align='center'>{}</th>  <td>{}</td> <th align="right">{}</th> <td>{}</td>  
                    <td>{}</td> <td>{}</td>  <td>{}</td>  
                    <td>{}</td> </tr> """.format("Total de Receitas", "", total_receitas, "", "", "", "", "")
        html += """<tr> <th align='center'>{}</th>  <td>{}</td> <th align="right">{}</th> <td>{}</td>  
                            <td>{}</td> <td>{}</td>  <td>{}</td>  
                            <td>{}</td> </tr> """.format("Total de Despesas", "", total_despesas, "", "", "", "", "")
        html += """<tr> <th align='center'>{}</th>  <td>{}</td> <th align="right">{}</th> <td>{}</td>  
                            <td>{}</td> <td>{}</td>  <td>{}</td>  
                            <td>{}</td> </tr> """.format("Saldo", "", total_receitas - total_despesas, "", "", "", "", "")

        html += "</table>"

        html += "<br/>"
        html += "<hr/>"
        html += "<p> Processado por Computador </p>".format(licenca)

        document = QTextDocument()

        document.setHtml(html)

        dlg = QPrintPreviewDialog(self)
        dlg.paintRequested.connect(document.print_)
        dlg.showMaximized()
        dlg.exec_()

    def fill_table(self):

        # Se forem todas das transaçoes
        if self.combo_lista_de_trasacoes.currentIndex() == len(self.transacoes) - 1:
            self.sql = """SELECT cod, tipo, estado, valor, descricao, created, modified, created_by, modified_by 
                    from receitas WHERE (cod like "%{numero}%" OR descricao 
                    like "%{cliente}%") AND codcaixa="{caixa}" 
                    AND codarmazem="{armazem}" """.format(numero=self.find_w.text(), cliente=self.find_w.text(),
                                                          tipo=self.combo_lista_de_trasacoes.currentIndex(),
                                                          armazem=self.parent().codarmazem,
                                                          caixa=self.parent().caixa_numero)
        else:
            self.sql = """SELECT cod, tipo, estado, valor, descricao, created, modified, created_by, modified_by 
                    from receitas WHERE (cod like "%{numero}%" OR descricao like "%{cliente}%") AND tipo={tipo}  
                    AND codcaixa="{caixa}" 
                    AND codarmazem="{armazem}" """.format(numero=self.find_w.text(),
                                                          cliente=self.find_w.text(),
                                                          tipo=self.combo_lista_de_trasacoes.currentIndex(),
                                                          armazem=self.parent().codarmazem,
                                                          caixa=self.parent().caixa_numero)
        try:

            print(self.sql)
            self.cur.execute(self.sql)
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]

        except Exception as e:
            print(e)
            return

        new_list = []
        for l in data:

            lista = list(l)
            t = lista[1]
            lista[1] = TRANSACOES[int(t)]

            if int(lista[2]) == int(1):
                estado = "Activo"
            else:
                estado = "Cancelado"

            lista[2] = estado

            lista[5] = QDateTime().fromString(lista[5], "yyyy-MM-dd H:mm:ss").toString("dd-MM-yyyy H:mm:ss")
            lista[6] = QDateTime().fromString(lista[6], "yyyy-MM-dd H:mm:ss").toString("dd-MM-yyyy H:mm:ss")

            lista = tuple(lista)
            new_list.append(lista)

        data = new_list

        self.data = data

        if len(data) == 0:
            tabledata = ["", "", "", "", "", "", "", "", ""]
        else:
            tabledata = data

        try:

            # Header for the table
            header = [qApp.tr('cod'), "Transação", "Estado", qApp.tr('Valor'), 'Descrição', qApp.tr('Criado em'), qApp.tr('Modificado em'),
                      qApp.tr('Criado pro'), qApp.tr('Modificado por')]

            self.tm = MyTableModel(tabledata, header, self)
            # set the table model
            self.totalItems = self.tm.rowCount(self)
            self.tv.setModel(self.tm)

            self.tv.setColumnHidden(0, True)
            self.tv.setColumnWidth(1, self.tv.width() * .1)
            self.tv.setColumnWidth(2, self.tv.width() * .1)
            self.tv.setColumnWidth(3, self.tv.width() * .1)
            self.tv.setColumnWidth(4, self.tv.width() * .2)
            self.tv.setColumnWidth(5, self.tv.width() * .1)
            self.tv.setColumnWidth(6, self.tv.width() * .1)
            self.tv.setColumnWidth(7, self.tv.width() * .1)
            self.tv.setColumnWidth(8, self.tv.width() * .1)

        except Exception as e:
            print(e)
            return
        # # set row height
        nrows = len(tabledata)
        for row in range(nrows):
            self.tv.setRowHeight(row, 25)
        self.create_statusbar()

    def create_toolbar(self):
        self.transacoes = TRANSACOES
        self.transacoes.append("Todas")

        find = QLabel(qApp.tr("Procurar") + "  ")
        self.find_w = QLineEdit(self)
        self.find_w.setMaximumWidth(200)

        self.new = QAction(QIcon('./icons/add_2.ico'), qApp.tr("Novo"), self)
        self.delete = QAction(QIcon('./images/editdelete.png'), qApp.tr("Eliminar"), self)
        self.print = QAction(QIcon('./images/fileprint.png'),qApp.tr("Imprimir"), self)
        self.update = QAction(QIcon('./images/pencil.png'), qApp.tr("Editar"), self)

        self.combo_lista_de_trasacoes = QComboBox()
        self.combo_lista_de_trasacoes.currentIndexChanged.connect(self.fill_table)
        self.combo_lista_de_trasacoes.addItems(self.transacoes)
        self.combo_lista_de_trasacoes.setCurrentIndex(len(self.combo_lista_de_trasacoes)-1)

        tool = QToolBar()
        tool.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        tool.setContextMenuPolicy(Qt.PreventContextMenu)

        tool.addWidget(find)
        tool.addWidget(self.find_w)
        tool.addAction(self.new)
        tool.addAction(self.update)
        tool.addAction(self.delete)
        tool.addAction(self.print)
        tool.addSeparator()
        tool.addWidget(QLabel("Transação: "))
        tool.addWidget(self.combo_lista_de_trasacoes)

        tool.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        self.addToolBarBreak(Qt.BottomToolBarArea)
        self.addToolBar(tool)

        ######################################################################
        self.new.triggered.connect(self.new_data)
        self.delete.triggered.connect(self.removerow)
        self.tv.doubleClicked.connect(self.update_data)
        self.update.triggered.connect(self.update_data)
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

        tipo = self.tm.index(self.row, 1)
        self.tipo_transacao = tipo.data()

        valor = self.tm.index(self.row, 3)
        self.valor_anterior = valor.data()

    def new_data(self):

        from receitas import DespesasReceitas
        receitas = DespesasReceitas(self)
        receitas.setModal(True)
        receitas.show()

    def update_data(self):

        if self.current_id == "":
            QMessageBox.information(self, "Info", "Selecione o registo a actualizar na tabela")
            return

        from receitas import DespesasReceitas
        receitas = DespesasReceitas(self)
        receitas.cod_receita = self.current_id
        receitas.mostrar_registo(self.current_id)
        receitas.setModal(True)
        receitas.show()

    def removerow(self):

        if self.current_id == "":
            QMessageBox.information(self, "Info", "Selecione o registo a apagar na tabela")
            return

        if QMessageBox.question(self, "Pergunta", str("Deseja eliminar o registo %s?") % self.current_id,
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            sql = """DELETE FROM receitas WHERE cod = "{codigo}" """.format(codigo=str(self.current_id))

            if self.tipo_transacao == 0:
                anterior_sql = """UPDATE caixa SET despesas=despesas-{} 
                                        WHERE cod="{}" """.format(self.valor_anterior, self.caixa_numero)
            else:
                anterior_sql = """UPDATE caixa SET receitas=receitas-{} 
                                                        WHERE cod="{}" """.format(self.valor_anterior, self.caixa_numero)

            try:
                self.cur.execute(anterior_sql)
                self.cur.execute(sql)
                self.conn.commit()
            except Exception as e:
                QMessageBox.warning(self, "Erro", "Registo não removido.\n{}".format(e))
                return False

            self.fill_table()
            QMessageBox.information(self, "Sucesso", "Item apagado com sucesso...")
            return True

if __name__ == '__main__':

    app = QApplication(sys.argv)

    helloPythonWidget = ListaDeReceitas()
    helloPythonWidget.show()

    sys.exit(app.exec_())