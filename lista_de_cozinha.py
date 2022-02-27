# -*- coding: utf-8 -*-

import datetime
import sys
import os
import decimal
from time import localtime, strftime

from PyQt5.QtWidgets import QApplication, QTableView, QAbstractItemView, QMessageBox, QToolBar, \
    QLineEdit, QLabel, QStatusBar, QAction, QMainWindow, qApp


from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter, QPrintDialog, QPrinterInfo
from PyQt5.QtGui import QIcon, QTextDocument, QBrush
from PyQt5.QtCore import Qt, QSizeF

import sqlite3 as lite

from utilities import printWordDocument, Invoice
from utilities import codigo as cd
from pedidos_cozinha import Pedidos
from sortmodel import MyTableModel
from relatorio.templates.opendocument import Template

DB_FILENAME = 'dados.tsdb'

DATA_ACTUAL = datetime.datetime.today()
date = datetime.datetime.now().date()
ANO_ACTUAL = DATA_ACTUAL.year
DIA = DATA_ACTUAL.day
MES = DATA_ACTUAL.month


class ListaDeCozinha(QMainWindow):
    def __init__(self, parent=None):
        super(ListaDeCozinha, self).__init__(parent)

        # controla o codigo
        self.current_id = ""
        self.coddocumento = 'DC20185555555'
        self.cliente_cod = ""
        self.codfornecedor = ""
        # Connect the Database
        if self.parent() is None:
            self.db = self.connect_db()
            self.user = ""
        else:
            self.conn = self.parent().conn
            self.cur = self.parent().cur
            self.user = self.parent().user
            self.empresa_cod = self.parent().codarmazem
            self.empresa = self.parent().nome_armazem
            self.caixa_numero = self.parent().caixa_numero
            self.empresa_logo = self.parent().empresa_logo
            self.empresa_endereco = self.parent().empresa_endereco
            self.empresa_contactos = self.parent().empresa_contactos
            self.empresa_email = self.parent().empresa_email
            self.empresa_web = self.parent().empresa_web
            self.empresa_nuit = self.parent().empresa_nuit
            self.empresa_casas_decimais = self.parent().empresa_casas_decimais
            self.licenca = self.parent().licenca
            self.contas = self.parent().contas
            self.incluir_iva = self.parent().incluir_iva

        # Create the main user interface
        self.ui()

        # Header for the table
        
        # Search the data
        self.setWindowTitle("Lista de Requisições")
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

    def enterEvent(self, *args, **kwargs):
        self.fill_table()

    def connect_db(self):
        # Connect to database and retrieves data
        try:
            self.conn = lite.connect(DB_FILENAME)
            self.cur = self.conn.cursor()

        except Exception as e:
            sys.exit(True)

    def fill_table(self):

        self.sql = """select cozinha.cod, cozinha.mesa, cozinha.estado, clientes.nome, cozinha.obs 
        FROM cozinha JOIN armazem ON armazem.cod=cozinha.codarmazem JOIN clientes ON 
        clientes.cod=cozinha.codcliente WHERE (armazem.nome like "%{nome}%" or cozinha.numero like "%{numero}%") 
        order by cozinha.numero""".format(nome=self.find_w.text(), numero=self.find_w.text())

        try:
            self.cur.execute(self.sql)
            data = self.cur.fetchall()
        except Exception as e:
            print(e)
            return

        self.tabledata = data

        if len(data) == 0:
            self.tabledata = ["", "", "", "", ""]
        else:
            self.tabledata = data

        header = [qApp.tr('Código'), qApp.tr('No'), qApp.tr('Estado'), qApp.tr('Requisitante'), "Notas"]

        try:
            self.tm = MyTableModel(self.tabledata, header, self)
            # set the table model
            self.totalItems = self.tm.rowCount(self)
            self.tv.setModel(self.tm)
            self.tv.setColumnHidden(0, 1)
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

        self.new = QAction(QIcon('./icons/add_2.ico'), qApp.tr("Criar nova Requisição."), self)
        self.aprovar_documento = QAction(QIcon('./images/editedit.png'), qApp.tr("Aprovar/Finalizar documento."), self)
        self.delete = QAction(QIcon('./images/editdelete.png'), qApp.tr("Reprovar documento"), self)
        self.printA4 = QAction(QIcon('./images/fileprint.png'),qApp.tr("Imprimir"), self)
        self.printPOS = QAction(QIcon("./icons/documentos.ico"), qApp.tr("Imprimir POS/Finalizar"), self)
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
        tool.addAction(self.aprovar_documento)
        tool.addAction(self.delete)
        tool.addSeparator()
        tool.addAction(self.printA4)
        tool.addAction(self.printPOS)

        tool.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        self.addToolBarBreak(Qt.BottomToolBarArea)
        self.addToolBar(tool)

        ######################################################################
        self.aprovar_documento.triggered.connect(self.new_data)
        self.delete.triggered.connect(self.removerow)
        self.tv.doubleClicked.connect(self.update_data)
        self.update.triggered.connect(self.update_data)
        self.new.triggered.connect(self.new_doc)
        # self.connect(self.delete, SIGNAL("triggered()"), self.removerow)
        # # self.connect(self.update, SIGNAL("triggered()"), self.updatedata)
        # self.print.triggered.connect(self.printForm)
        self.printPOS.triggered.connect(self.imprimePOS)
        self.printA4.triggered.connect(self.impremeA4)

    def create_statusbar(self):
        estado = QStatusBar(self)

        self.items = QLabel("Total Items: %s" % self.totalItems)
        estado.addWidget(self.items)
        self.setStatusBar(estado)

    def clickedslot(self, index):

        self.row = int(index.row())

        indice = self.tm.index(self.row, 0)
        self.current_id = indice.data()

        cl = self.tm.index(self.row, 4)
        self.cliente_cod = cl.data()

    def new_data(self):
        if self.current_id == "":
            return

        if self.registo_finalizado() is True:
            QMessageBox.warning(self, "Aviso: Documento Finalizado", "Documento já foi finalizado.")
            return

        sql = """UPDATE cozinha set estado=1 WHERE  cod="{}" """.format(self.current_id)

        if QMessageBox.question(self, "Pergunta",
                               "Deseja Aprovar esta requisção?.\nAviso: sta acção não pode ser revertida.") == QMessageBox.Yes:

            try:
                self.diminui_produtos()
                self.aumenta_produtos()
                self.cur.execute(sql)
                self.conn.commit()

                QMessageBox.information(self, "Sucesso", "Operação concluida com Sucesso!!!")
            except Exception as e:
                QMessageBox.warning(self, "Erro", "Dasos não gravados.{}.".format(e))

    def new_doc(self):
        cozinha = Pedidos(self)
        cozinha.setWindowTitle("Requisição de Stock")
        cozinha.setModal(True)
        cozinha.showMaximized()

    def update_data(self):

        if self.current_id == "":
            QMessageBox.information(self, "Info", "Selecione o registo a actualizar na tabela")
            return

        cl = Pedidos(self)
        cl.setWindowTitle("Requisição de Stock")
        cl.codigogeral = self.current_id
        cl.fill_data()
        cl.fill_table2()
        cl.habilita_desabilita_impressao()

        if self.registo_finalizado() is True:
            cl.doc_finalizado(1)

        cl.setModal(True)
        cl.show()

    def impremeA4(self):
        if self.current_id == "":
            return

        try:
            self.imprime_recibo_grande2(self.current_id)
        except Exception as e:
            QMessageBox.warning(self, "Erro na criação de Documento",
                                "Houve erro na tentativa de criar Documento para imprimir. {}.".format(e))

    def  imprimePOS(self):
        try:
            self.segundavia_POS(self.current_id)
        except Exception as e:
            QMessageBox.warning(self, "Erro na criação de Documento",
                                "Houve erro na tentativa de criar Documento para imprimir. {}.".format(e))

    def segundavia_POS(self, codigo):

        sql = """SELECT * FROM factura_geral WHERE codrequisicao = '{}' """.format(codigo)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        # LOGOTIPO
        # html = """
        #                           < table
        #                               width = "100%" >
        #                              < tr >
        #                                   < td >
        #                                   < img src = '{}' width = "80" >
        #                                   < / td >
        #                              </ tr >
        #                          < / table >
        #                           """.format(self.parent().empresa_logo)

        html = ""

        if self.parent() is not None:
            html += "<center> {} </center>".format(self.parent().nome_armazem)
            html += "<center> {} </center>".format(self.parent().empresa_endereco)
            html += "<center> NUIT: {} </center>".format(self.parent().empresa_nuit)
            html += "<center> Contactos: {} </center>".format(self.parent().empresa_contactos)
        else:
            html += "<center> [Nome da Empresa] </center>"
            html += "<center> [Endereco] </center>"
            html += "<center> [NUIT] </center>"
            html += "<center> [CONTACTOS] </center>"

        html += "<p align='right'> {}: {}/{}{}</p>".format(data[0][2], data[0][1], data[0][23], data[0][22])
        html += "<p align='right'>DATA: {}</p>".format(data[0][3])

        html += "<p>Exmo(a) Sr.(a): {}</p>".format(data[0][10])

        html += "<hr/>"

        html += "<table border='0' width = 80mm style='border: thin;'>"
        html += "<tr>"

        if self.coddocumento != 'DC20185555555':
            html += "<th width = 60%>Descrição</th>"
            html += "<th width = 10%>Qt.</th>"
            html += "<th width = 10%>Preço.</th>"
            html += "<th width = 20% align='right'>Total</th>"

        else:
            html += "<th width = 80%>Descrição</th>"
            html += "<th width = 20%>Qt.</th>"

        html += "</tr>"

        for cliente in data:
            if self.coddocumento != 'DC20185555555':
                html += """<tr> <td>{}</td> <td>{}</td> <td align="right">{}</td> <td align="right">{}</td> </tr>
                                           """.format(cliente[15], cliente[16], cliente[17], cliente[21])
            else:
                html += """<tr> <td>{}</td> <td>{}</td> </tr>
                                                           """.format(cliente[15], cliente[16])

        html += "</table>"

        html += "<table>"

        if self.coddocumento != 'DC20185555555':
            html += "<tr>"
            html += "<td width = 50% align='right'>SUBTOTAL</td>"
            html += "<td width = 50% align='right'>{:20,.{casas}f} </td>".format(cliente[5],
                                                                                 casas=self.parent().empresa_casas_decimais)
            html += "<tr>"
            html += "<td width = 50% align='right'>IVA(17%)</td>"
            html += "<td width = 50% align='right'>{:20,.{casas}f} </td>".format(cliente[7],
                                                                                 casas=self.parent().empresa_casas_decimais)
            html += "<tr>"
            html += "<th width = 50% align='right'>TOTAL</th>"
            html += "<td width = 50% align='right'>{:20,.{casas}f} </td>".format(cliente[8],
                                                                                 casas=self.parent().empresa_casas_decimais)
            html += "</tr>"

        html += "</table>"

        html += "<hr/>"
        html += "<p> {}</p>".format(self.parent().contas)
        html += "<p> Processado por Computador  </p>".format(self.parent().licenca)

        document = QTextDocument()
        document.setHtml(html)

        printer = QPrinter()
        info = QPrinterInfo.defaultPrinter().printerName()

        printer.setResolution(printer.HighResolution)
        printer.setPaperSize(QSizeF(self.parent().papel_1,  1000), printer.Millimeter)
        printer.setPrinterName(self.parent().pos1)
        dialog = QPrintDialog()
        dialog.setContentsMargins(0, 0, 0, 0)
        # printer.setOutputFormat(QPrinter.PdfFormat)
        # printer.setOutputFileName("{}.pdf".format(data[0][0]))
        # printer.setPageMargins(0, 0, 10, 0, QPrinter.Millimeter)
        document.setPageSize(QSizeF(printer.pageRect().size()))
        # document.setDocumentMargin(0)
        document.print_(printer)
        dialog.accept()

    def imprime_recibo_grande2(self, codigo):
        if codigo == "":
            return

        sql = """SELECT * FROM factura_geral WHERE codrequisicao = '{}' """.format(codigo)

        print('Imprimir', sql)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        logo = os.path.realpath(self.parent().empresa_logo)
        empresa = self.parent().nome_armazem
        endereco = self.parent().empresa_endereco
        contactos = self.parent().empresa_contactos
        web = '{}, {}'.format(self.parent().empresa_email, self.parent().empresa_web)
        nuit = self.parent().empresa_nuit
        casas = self.parent().empresa_casas_decimais
        licenca = self.parent().licenca
        contas = self.parent().contas

        if len(data) > 0:
            doc = "{}/{}{}".format(data[0][1], data[0][23], data[0][22])
            try:
                data_doc = datetime.datetime.strptime(str(data[0][3]), "%Y-%m-%d").strftime("%d-%m-%Y")
            except ValueError:
                data_doc = ""

            try:
                vencimento = datetime.datetime.strptime(str(data[0][28]), "%Y-%m-%d").strftime("%d-%m-%Y")
            except ValueError:
                vencimento = ""

            line = []
            if self.parent().incluir_iva == 0:
                for item in data:
                    line += [{'item': {'name': item[15], 'reference': item[16],
                                       'price': decimal.Decimal(item[19]), 'armazem': data[0][30]},
                              'quantity': decimal.Decimal(item[21] / item[16]),
                              'amount': decimal.Decimal(item[21])}, ]
            else:
                for item in data:
                    line += [{'item': {'name': item[15], 'reference': item[16],
                                       'price': decimal.Decimal(item[19]), 'armazem': data[0][30]},
                              'quantity': decimal.Decimal(item[17]),
                              'amount': decimal.Decimal(item[20]), 'armazem': data[0][30]},]

            inv = Invoice(customer={'name': 'Orlando Vilanculo',
                                    'address': {'street': 'Smirnov street', 'zip': 1000, 'city': 'Montreux'}},
                          clienteweb=data[0][13],
                          clienteendereco=data[0][11],
                          clientenome=data[0][10],
                          clientenuit=data[0][12],
                          clientecontactos=data[0][27],
                          empresanome=empresa,
                          empresaendereco=endereco,
                          empresanuit=nuit,
                          empresacontactos=contactos,
                          empresaweb=web,
                          contas=contas,
                          licenca=licenca,
                          vencimento=vencimento,
                          lines=line,
                          id=doc,
                          status='late',
                          doc=data[0][2],
                          datadoc=data_doc,
                          operador=data[0][4],
                          obs=data[0][29],
                          subtotal=data[0][5],
                          desconto=data[0][6],
                          iva=data[0][7],
                          totalgeral=data[0][8],

                          )

            # Verifica o Ficheiro de entrada Template
            filename = os.path.realpath('template.odt')
            if os.path.isfile(filename) is False:
                QMessageBox.critical(self, "Erro ao Imprimir",
                                     "O ficheiro modelo '{}'  não foi encontrado.".format(filename))
                return

            # Verifica o ficheiro de saida
            if self.coddocumento == "DC20185555555":
                targetfile = self.parent().req_template
            else:
                targetfile = self.parent().fact_template

            if os.path.isfile(targetfile) is False:
                QMessageBox.critical(self, "Erro ao Imprimir",
                                     "O ficheiro modelo '{}'  não foi encontrado. \n "
                                     "Reponha-o para poder Imprimir".format(targetfile))
                return

            basic = Template(source='', filepath=targetfile)
            open(filename, 'wb').write(basic.generate(o=inv).render().getvalue())

            doc_out = cd("0123456789") + "{}{}{}{}".format(data[0][2], data[0][1], data[0][23], data[0][22])
            out = os.path.realpath("'{}'.pdf".format(doc_out))


            printWordDocument(filename, out)

    def removerow(self):

        if self.current_id == "":
            QMessageBox.information(self, "Info", "Selecione o registo a apagar na tabela")
            return

        if QMessageBox.question(self, "Pergunta", str("Deseja eliminar o registo %s?") % self.current_id,
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:

            if self.registo_finalizado() is True:
                QMessageBox.warning(self, "Registo não pode ser apagado.",
                                    "Registo Finalizado não pode ser apagado.")
                return

            sql = """delete from cozinha WHERE cod = "{codigo}" and estado=0 """.format(codigo=str(self.current_id))
            sql1 = """delete from requisicaodetalhe WHERE codrequisicao = "{codigo}" """.format(
                codigo=str(self.current_id))

            try:
                self.cur.execute(sql1)
                self.cur.execute(sql)
                self.conn.commit()
                self.fill_table()
                QMessageBox.information(self, "Sucesso", "Item apagado com sucesso...")
            except Exception as e:
                print("Erro: ", e)

    def registo_finalizado(self):
        estadosql = """SELECT estado from cozinha WHERE cod="{}" and estado=1 """.format(self.current_id)

        self.cur.execute(estadosql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return True
        else:
            return False


if __name__ == '__main__':

    app = QApplication(sys.argv)

    helloPythonWidget = ListaDeCozinha()
    helloPythonWidget.show()

    sys.exit(app.exec_())