# -*- coding: utf-8 -*-

import sys
import os
import operator
from decimal import Decimal
import datetime
import decimal

from PyQt5.QtWidgets import (QApplication,  QMessageBox, QToolBar, QTableView, QAbstractItemView, QHBoxLayout,
    QLineEdit, QLabel, QStatusBar, QAction, qApp, QFormLayout, QPlainTextEdit, QVBoxLayout, QSpinBox, QDialog,
                             QComboBox)

from PyQt5.QtPrintSupport import QPrintPreviewDialog
from PyQt5.QtGui import QIcon, QFont, QTextDocument
from PyQt5.QtCore import Qt, QDate, QDateTime
import sqlite3 as lite
from relatorio.templates.opendocument import Template

from sortmodel import MyTableModel

# from base import DB_FILENAME, DBCOnnection

from utilities import codigo as cd
from pricespinbox import price
from utilities import printWordDocument, Invoice

DB_FILENAME = 'dados.tsdb'

DATA_ACTUAL = datetime.date.today()
date = datetime.datetime.now().date()
ANO_ACTUAL = DATA_ACTUAL.year
DIA = DATA_ACTUAL.day
MES = DATA_ACTUAL.month


class MainWindow(QDialog):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # controla o codigo
        self.current_id = ""
        self.codcliente = ""
        self.valor_a_pagar = 0.00
        self.valorcash = 0.00
        self.valorcheque = 0.00
        self.valortransferencia = 0.00
        self.codrecibo = ""
        self.codfactura = ""
        self.valortroco = 0.00
        self.soma = 0.00
        self.total = 0.00
        self.tota_divida = 0.00

        # Connect the Database
        if self.parent() is None:
            self.db = self.connect_db()
            self.user = ""
            self.caixa_numero = ""
        else:
            self.caixa_numero = self.parent().caixa_numero
            self.conn = self.parent().conn
            self.cur = self.parent().cur
            self.user = self.parent().user

        # Create the main user interface
        self.ui()

        # Header for the table codfactura, factura, descricao, pago, saldo
        self.header = [qApp.tr('cod'), qApp.tr('Factura'), qApp.tr('Descrição'),qApp.tr('Valor Pago'), qApp.tr('Saldo')]

        # Search the data
        self.fill_table()
        # self.find_w.textEdited.connect(self.fill_table)
        self.enche_ano()
        self.fill_data()

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

        self.titulo = QLabel("0.00")
        self.titulo.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        boldFont = QFont('Consolas', 24)
        boldFont.setBold(True)
        self.titulo.setFont(boldFont)

        cod = QLabel("Número da Factura")

        self.ano = QComboBox()
        self.ano.setMaximumWidth(150)
        self.cod = QSpinBox()
        self.cod.setMaximum(999999999)
        self.cod.setMinimum(1)
        self.cod.setSingleStep(1)
        self.cod.valueChanged.connect(self.get_data)
        cliente = QLabel("Cliente")
        self.cliente = QLineEdit()
        self.cliente.setEnabled(False)
        saldo = QLabel("Saldo")
        self.saldo = price()
        self.saldo.setEnabled(False)
        descricao = QLabel("Descrição")
        self.descricao = QLineEdit()
        valor = QLabel("Valor a Pagar")
        self.valor = price()
        self.valor.valueChanged.connect(self.calculatroco)
        cheque = QLabel("Cheque")
        self.cheque = price()
        self.cheque.valueChanged.connect(self.calculatroco)
        pos = QLabel("POS/Transferencia")
        self.pos = price()
        self.pos.valueChanged.connect(self.calculatroco)
        troco = QLabel("Troco")
        self.troco = price()
        self.troco.setEnabled(False)
        self.obs = QPlainTextEdit(self)
        maxwidth = self.valor.width()
        self.cod.setMaximumWidth(maxwidth)

        layout = QFormLayout()

        layout.addRow(QLabel("Ano"), self.ano)
        layout.addRow(cod, self.cod)
        layout.addRow(cliente, self.cliente)
        layout.addRow(saldo, self.saldo)
        layout.addRow(descricao, self.descricao)
        layout.addRow(valor, self.valor)
        layout.addRow(cheque, self.cheque)
        layout.addRow(pos, self.pos)
        layout.addRow(troco, self.troco)


        self.create_toolbar()

        vboxlayout = QVBoxLayout()
        vboxlayout.addLayout(layout)
        vboxlayout.addWidget(self.obs)

        hlayout = QHBoxLayout()
        hlayout.addLayout(vboxlayout)
        hlayout.addWidget(self.tv)
        mainlayout = QVBoxLayout()
        mainlayout.addWidget(self.titulo)
        mainlayout.addLayout(hlayout)
        mainlayout.addWidget(self.tool)

        self.setLayout(mainlayout)


    def enche_ano(self):
        sql = """SELECT DISTINCT ano from facturacao WHERE coddocumento= "DC20182222222" 
        GROUP BY ano ORDER BY ano desc """

        self.cur.execute(sql)
        lista = self.cur.fetchall()

        data = [tuple(str(item) for item in t) for t in lista]
        try:
            if len(data) > 0:
                for item in data:
                    self.ano.addItems(item)
            else:
                QMessageBox.information(self, "Sem Facturas", "Ainda não foram feitas Facturas.")
                self.close()

        except Exception as e:
            print(e)

    def trocos(self, cash, cheque, pos):

        self.soma = Decimal(cash) + Decimal(cheque) + Decimal(pos)

        if self.soma > Decimal(self.saldo.value()):
            troco = self.soma - Decimal(self.saldo.value())
            return Decimal(troco)
        else:
            return 0.00

    def calculatroco(self):

        self.valorcash = Decimal(self.valor.value())
        self.valortransferencia = Decimal(self.pos.value())
        self.valorcheque = Decimal(self.cheque.value())

        self.troco.setValue(self.trocos(self.valorcash, self.valorcheque, self.valortransferencia))

    def focusInEvent(self, evt):
        self.fill_table()

        # Método que incrimenta documentos baseando no ano.

    # Método que incrimenta documentos baseando no ano.
    def incrimenta(self, ano):
        sql = """select max(numero) from recibos WHERE ano={ano}""".format(ano=ano)

        try:
            self.cur.execute(sql)
            data = self.cur.fetchall()
        except Exception as e:
            return

        if data[0][0] is None:
            self.numero = 1
        else:
            self.numero = data[0][0] + 1

    def fill_data(self):

        if self.codfactura == "":
            # QMessageBox.warning(self, "Selecione a Factura", "Selecione a Factura e pressione a tecla <Enter>.")
            return

        sql = """SELECT clientes.nome from clientes INNER JOIN stock ON 
           clientes.cod = stock.cliente INNER JOIN facturacaodetalhe ON stock.cod=facturacaodetalhe.codstock
           WHERE stock.cod = "{codigo}" """.format(codigo=str(self.cod.text()))

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            self.codrecibo = "RC" + cd("abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")
        else:

            self.combo_cliente.setCurrentText(''.join(data[0][0]))
            self.numerodocumento.setText(''.join(data[0][1]))
            self.datadocumento.setDate(QDate.fromString(''.join(data[0][2])))
            self.valor_documento.setValue(float(data[0][3]))
            self.valorcash.setValue(float(data[0][4]))

            self.fill_table()

    def verifica_cliente(self, nome):

        if nome == "":
            self.combo_cliente.setCurrentText("Cliente Padrão")
            return False

        sql = """select cod, nome from clientes WHERE nome="{}" """.format(nome)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            return False

        return True

    def connect_db(self):
        # Connect to database and retrieves data
        try:
            self.conn = lite.connect(DB_FILENAME)
            self.cur = self.conn.cursor()

        except Exception as e:
            sys.exit(True)

    def keyPressEvent(self, event):

            if event.key() in (Qt.Key_Enter, 16777220):
                if self.cod.hasFocus():
                    self.new_data()

    def get_data(self):
        if self.ano.currentText() == "":

            return

        sql = "select facturacao.cod, facturacao.saldo, facturacao.codcliente, " \
              "clientes.nome, facturacao.modified from facturacao INNER JOIN clientes on " \
              "clientes.cod=facturacao.codcliente " \
              "WHERE facturacao.numero = {} and facturacao.ano = {} and " \
              "facturacao.coddocumento='DC20182222222' and facturacao.estado=1 ".format(self.cod.value(),
                                                                                        self.ano.currentText())

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            self.codfactura = ""
            self.saldo.setValue(0.00)
            self.valor.setValue(0.00)
            self.codcliente = ""
            self.cliente.setText("")
            self.descricao.setText("")
            self.tota_divida = 0.00
            return False
        else:
            self.codfactura = data[0][0]
            self.tota_divida = data[0][1]
            self.saldo.setValue(data[0][1])
            self.valor.setValue(self.saldo.value())
            self.codcliente = data[0][2]
            self.cliente.setText(data[0][3])
            self.descricao.setText("Pagamento da Factura número {}.".format(self.cod.value()))
            return True

    def fill_table(self):

        self.sql = """select codfactura, factura, descricao, pago, saldo from recibosdetalhe 
        WHERE codrecibo='{cod}' """.format(cod=self.codrecibo)

        try:
            self.cur.execute(self.sql)
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]
        except Exception as e:
            return

        if len(data) == 0:
            self.tabledata = ["", "", "", "", ""]
        else:
            self.tabledata = data

        try:
            self.tm = MyTableModel(self.tabledata, self.header, self)
            # set the table model
            self.totalItems = self.tm.rowCount(self)
            self.tv.setModel(self.tm)
            self.tv.setColumnHidden(0, True)
        except Exception as e:
            print(e)
            return
        # # set row height
        nrows = len(self.tabledata)
        for row in range(nrows):
            self.tv.setRowHeight(row, 25)
        # self.create_statusbar()

    def create_toolbar(self):

        self.new = QAction(QIcon('./icons/add_2.ico'), qApp.tr("Adicionar Factura"), self)
        self.delete = QAction(QIcon('./icons/remove.ico'), qApp.tr("Remover Factura Seleccionada"), self)
        self.delete_all = QAction(QIcon('./icons/removeall.ico'), qApp.tr("Remover todas Facturas"), self)
        self.print = QAction(QIcon('./images/fileprint.png'), qApp.tr("Finalizar Recibo"), self)
        self.update = QAction(QIcon('./images/pencil.png'), qApp.tr("Editar"), self)

        self.tool = QToolBar()
        self.tool.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        self.tool.addAction(self.new)
        # self.tool.addAction(self.update)
        self.tool.addSeparator()
        self.tool.addAction(self.delete)
        self.tool.addAction(self.delete_all)
        self.tool.addSeparator()
        self.tool.addAction(self.print)
    
        ######################################################################
        self.new.triggered.connect(self.new_data)
        self.delete.triggered.connect(self.removerow)
        self.delete_all.triggered.connect(self.removeall)
        self.print.triggered.connect(self.finalizar_doc)

    def create_statusbar(self):
        estado = QStatusBar(self)

        self.items = QLabel("Total Items: %s" % self.totalItems)
        estado.addWidget(self.items)
        self.setStatusBar(estado)

    def clickedslot(self, index):

        self.row = int(index.row())

        indice = self.tm.index(self.row, 0)
        self.current_id = indice.data()

    def pago_totalmente(self, cod):
        sql = """select saldo from facturacao WHERE cod = '{}' """.format(cod)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            if data[0][0] > 0.00:
                return False
            else:
                return True
        else:
            return False

    def cliente_diferente(self, codrecibo):
        sql = "select codcliente from recibos WHERE cod = '{}' ".format(codrecibo)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            # O cliente e diferente
            if self.codcliente != data[0][0]:
                return True
            else:
                # O cliente e o mesmo
                return False
        else:
            #O cliente e o mesmo
            return False

    def grava_detalhes(self):

        code = self.codfactura
        codrecibo = self.codrecibo
        factura = self.cod.value()
        pago = Decimal(self.valor.value())
        saldo = self.tota_divida - pago
        descricao = self.descricao.text()

        if self.facturaexiste(code, codrecibo):
            sql = """UPDATE recibosdetalhe set pago = {}, saldo = {}, 
            descricao = '{}' WHERE codfactura="{}" """.format(pago, saldo, descricao, code)
        else:
            sql = """INSERT INTO recibosdetalhe (codrecibo, factura, pago, saldo, descricao, codfactura) 
            VALUES ('{}', {}, {}, {}, '{}', '{}')""".format(codrecibo, factura, pago, saldo, descricao, code)
        try:
            self.cur.execute(sql)
            return True
        except Exception as e:
            QMessageBox.warning(self, "Erro", "Dados não gravados.{}.".format(e))
            return False

    def finalizar_doc(self):

        if self.tabelavazia() is True:
            QMessageBox.critical(self, "Erro de Recibo", "Adicione Factura(s) primeiro.")
            return

        sql = """select pago, codfactura from recibosdetalhe WHERE codrecibo="{}" """.format(self.codrecibo)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:

            for item in data:
                sql = "update facturacao set saldo=saldo-{pago}, credito=credito+{pago} WHERE cod='{cod}' " \
                      "".format(pago=item[0], cod=item[1])
                self.cur.execute(sql)



            sql_update = """update recibos set finalizado=1, obs="{}" WHERE cod="{}" """.format(self.obs.toPlainText(), self.codrecibo)

            self.cur.execute(sql_update)
            self.conn.commit()

            try:
                self.imprime_recibo_grande2(self.codrecibo)
            except Exception as e:
                QMessageBox.warning(self, "Erro na criação de Documento",
                                    "Houve erro na tentativa de criar Documento para imprimir. {}.".format(e))
            self.close()

    def imprime_recibo_grande2(self, codigo):

        sql = """SELECT * FROM recibo_geral WHERE cod = '{}' """.format(codigo)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        logo = os.path.realpath(self.parent().empresa_logo)
        empresa = self.parent().empresa
        endereco = self.parent().empresa_endereco
        contactos = self.parent().empresa_contactos
        web = '{}, {}'.format(self.parent().empresa_email, self.parent().empresa_web)
        nuit = self.parent().empresa_nuit
        casas = self.parent().empresa_casas_decimais
        licenca = self.parent().licenca
        contas = self.parent().contas

        if len(data) > 0:
            doc = "{}/{}{}".format(data[0][14], data[0][15], data[0][16])

            # Data do documento
            data_doc = QDateTime.fromString(str(data[0][17]), 'yyyy-MM-dd H:mm:ss').toString("dd-MM-yyyy")
            vencimento = QDateTime.fromString(str(data[0][2]), 'yyyy-MM-dd H:mm:ss').toString("dd-MM-yyyy")

            line = []
            for item in data:
                line += [{'item': {'name': item[5], 'reference': "{}".format(item[6]),
                                   'price': decimal.Decimal(item[7])},
                          'quantity': decimal.Decimal(item[7]),
                          'amount': decimal.Decimal(item[7])}, ]

            inv = Invoice(customer={'name': 'Orlando Vilanculo',
                                    'address': {'street': 'Smirnov street', 'zip': 1000, 'city': 'Montreux'}},
                          clienteweb=data[0][11],
                          clienteendereco=data[0][9],
                          clientenome=data[0][8],
                          clientenuit=data[0][10],
                          clientecontactos=data[0][19],
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
                          doc="Recibo",
                          datadoc=data_doc,
                          operador=data[0][18],
                          obs=data[0][20],
                          subtotal=data[0][7],
                          desconto=data[0][7],
                          iva=data[0][7],
                          totalgeral=data[0][1],
                          )

            filename = os.path.realpath('template.odt')

            if os.path.isfile(filename) is False:
                QMessageBox.critical(self, "Erro ao Imprimir", "O ficheiro modelo '{}'  não foi encontrado.".format(filename))
                return

            targetfile = self.parent().rec_template

            if os.path.isfile(targetfile) is False:
                QMessageBox.critical(self, "Erro ao Imprimir",
                                     "O ficheiro modelo '{}'  não foi encontrado. \n "
                                     "Reponha-o para poder Imprimir".format(targetfile))
                return

            basic = Template(source='', filepath=targetfile)
            open(filename, 'wb').write(basic.generate(o=inv).render().getvalue())

            doc_out = cd("0123456789") + "{}{}{}{}".format("Recibo", data[0][14], data[0][15], data[0][16])
            out = os.path.realpath("'{}'.pdf".format(doc_out))

            printWordDocument(filename, out)

    def imprime_recibo_grande(self, codigo):

        sql = """SELECT * FROM recibo_geral WHERE cod = '{}' """.format(codigo)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        # LOGOTIPO
        # html = """
        #                       < table width="100%" style="float: right; border: 1px solid red;">
        #                           < tr >
        #                               < td >
        #                               < img src = '{}' width = "80" >
        #                               < / td >
        #                           </ tr >
        #                       < / table >
        #                       """.format(self.parent().empresa_logo)

        html = ""

        html += "<hr/>"

        if self.parent() is not None:

            empresa_info = """ < table width="100%" style="float: right; border: 1 solid red;">
                                          < tr > < td width="50%"> <h2> {} </h2> < / td > </ tr > 
                                          < tr > < td > {} < / td > </ tr >
                                          < tr > < td > {} < / td > </ tr >
                                          < tr > < td > {} < / td > </ tr >
                                      < / table > 
                                      """.format(self.parent().empresa, self.parent().empresa_endereco,
                                                 self.parent().empresa_nuit,
                                                 self.parent().empresa_contactos)

            html += """ < table width="100%" style="float: right; border: 1 solid red;">
                              < tr > < td > {} < / td >  < td > {} < / td > </ tr >
                           </table>""".format(empresa_info, "")
        else:
            html += "<p> [Nome da Empresa] </p>"
            html += "<p> [Endereco] </p>"
            html += "<p> [NUIT] </p>"
            html += "<p> [CONTACTOS] </p>"

        data_factura = data[0][17]

        sql = """select cod from documentos WHERE nome="{}" """.format("Recibo")
        self.cur.execute(sql)
        dados = self.cur.fetchall()
        docs = ['DC20181111111', 'DC20182222222', 'DC20183333333']
        if dados[0][0] in docs:
            html += "<p align='right'> <h2 style='color: red;'> {}: {}/{}{} </h2> </p>".format("Recibo",
                                                                                               data[0][14], data[0][15], data[0][16])
        else:
            html += "<p align='right'> <h2> {}: {}/{}{} </h2> </p>".format(data[0][2], data[0][1], data[0][23],
                                                                           data[0][22])

        html += "<p align='right'>DATA: {}</p>".format(data_factura)
        html += "<p align='right'>Operador: {}</p>".format(data[0][18])

        html += "<p>Exmo(a) Sr.(a): {}</p>".format(data[0][8])

        if data[0][11] != "":
            html += "<p>{}</p> ".format(data[0][9])

        if data[0][12] != "":
            html += "<p>NUIT: {}</p>".format(data[0][10])

        if data[0][13] != "":
            html += "<p>Contactos: {}</p>".format(data[0][11])

        html += "<hr/>"

        html += "<table border='0' width = 80mm style='border: 1px;'>"
        html += "<tr style='background-color: gray;'>"
        html += "<th width = 80% align='left'>Descrição</th>"
        html += "<th width = 20% align='right'>Total</th>"
        html += "</tr>"

        for cliente in data:
            html += """<tr> <td>{}</td>  <td align="right">{}</td> </tr> """.format(cliente[5], cliente[7])

        html += "</table>"

        html += "<table border='0' width = '100%' style='border: 1px;'>"
        html += "<hr/>"
        html += "<tr width = '100%'>"
        html += "<th width = '100%' align='right'><td> <td> <b> TOTAL </b> </td> <td align='right'>" \
                " <b> {:20,.{casas}f} </b> </td></th>".format(cliente[1],
                                                                          casas=self.parent().empresa_casas_decimais)
        html += "</tr>"

        html += "</table>"

        html += "<hr/>"
        html += "<p> {}</p>".format(self.parent().contas)
        html += "<p> Processado por Computador </p>".format(self.parent().licenca)

        document = QTextDocument()

        document.setHtml(html)

        dlg = QPrintPreviewDialog(self)
        dlg.paintRequested.connect(document.print_)
        dlg.showMaximized()
        dlg.exec_()

    def facturaexiste(self, codfactura, codrecibo):
        sql = """select codfactura from recibosdetalhe WHERE codfactura= '{}' and codrecibo="{}" """.format(codfactura, codrecibo)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return True
        else:
            return False

    def reciboexiste(self, codrecibo):
        sql = "select cod from recibos WHERE cod= '{}' ".format(codrecibo)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return True
        else:
            return False

    def recibo_finalizado(self, codrecibo):

        sql = "select finalizado from recibos WHERE cod= '{}'".format(codrecibo)

        self.cur.execute(sql)
        data = self.cur.fetchall()



        if len(data) > 0:
            if data[0][0] == 1:
                return True
            else:
                return False
        else:
            return True

    def showEvent(self, *args, **kwargs):
        self.codrecibo = "RC" + cd("abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")

    def calculatotal(self, codrecibo):

        if self.tabelavazia() is True:
            sql = """delete from recibos WHERE cod="{}" """.format(codrecibo)
            self.cur.execute(sql)
            self.conn.commit()
            self.titulo.setText("0.00")
            self.get_data()
            return

        sql = """select sum(pago) from recibosdetalhe WHERE codrecibo="{}" """.format(codrecibo)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            recibo_sql = "update recibos set total={} WHERE cod = '{}' ".format(data[0][0], codrecibo)

            self.cur.execute(recibo_sql)
            self.conn.commit()

            self.total = data[0][0]
        else:
            self.total = 0.00

        total_display = '{}'.format(self.total)
        self.titulo.setText(total_display)
        return self.total

    # Verifica se a tabela está vazia ou não
    def tabelavazia(self):

        if self.codrecibo == "":
            return

        sql = """ SELECT * from recibosdetalhe WHERE codrecibo="{cod}" """.format(cod=self.codrecibo)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            return True
        else:
            return False

    def new_data(self):

        print(self.codfactura)

        if self.pago_totalmente(self.codfactura) is True:
            QMessageBox.warning(self, 'Pago', 'Factura já foi paga na totalidade.')
            return

        if decimal.Decimal(self.tota_divida) < decimal.Decimal(self.valor.text()):
            QMessageBox.warning(self, 'Valor Errado', 'O Valor a Pagar é maior que o Saldo da Factura')
            self.valor.setValue(self.tota_divida)
            return

        if self.cliente_diferente(self.codrecibo) is True:
            QMessageBox.warning(self, "Cliente Diferente", "O cliente deve ser o mesmo para todas as Facturas.")
            return

        self.incrimenta(ANO_ACTUAL)
        data = QDate.currentDate().toString('yyyy-MM-dd')
        numero = self.numero
        ano = ANO_ACTUAL
        mes = MES
        obs = self.obs.toPlainText()
        cod = self.codrecibo
        codfactura = self.codfactura
        codcliente = self.codcliente
        total = 0.00
        troco = 0.00
        banco = 0.00
        cash = 0.00
        tranferencia = 0.00
        estado = 1
        extenso = ''
        finalizado = 0
        caixa = self.caixa_numero

        created = QDate.currentDate().toString('yyyy-MM-dd')
        modified = QDate.currentDate().toString('yyyy-MM-dd')

        if self.parent() is not None:
            modified_by = self.parent().user
            created_by = self.parent().user
        else:
            modified_by = self.user
            caixa = 'CX2018710cleg'
            created_by = self.user

        if self.reciboexiste(cod) is False:

            values = """ '{cod}', {numero}, '{codfactura}', '{codcliente}', '{data}', {total}, {troco}, {banco}, 
            {cash}, {tranferencia}, '{estado}', '{extenso}', '{ano}', '{mes}', '{obs}', '{created}', '{modified}', 
            '{modified_by}', '{created_by}', {finalizado}, '{caixa}' 
            """.format(cod=cod, numero=numero, codfactura=codfactura, codcliente=codcliente,
                        data=data, total=total, troco=troco, banco=banco, cash=cash, tranferencia=tranferencia,
                        estado=estado, extenso=extenso, ano=ano, mes=mes, obs=obs, created=created,
                        modified=modified, modified_by=modified_by, created_by=created_by, finalizado=finalizado,
                        caixa=caixa)

            sql = """ INSERT INTO recibos (cod, numero, codfactura, codcliente, data, total, troco, banco, cash, 
            tranferencia, estado, extenso, ano, mes, obs, created, modified, modified_by, created_by, 
            finalizado, caixa) VALUES({value})""".format(value=values)
        else:
            sql = "UPDATE recibos set total=total WHERE cod = '{}' ".format(cod)

        try:

            self.cur.execute(sql)
            # Grava detalhes do documento mas depende da tabela mae facturacao
            self.grava_detalhes()

            # So Grava caso nao exista erro nas 2 tabelas
            self.conn.commit()
        except Exception as e:
            QMessageBox.critical(self, "Erro", "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
            return

        # self.limpar()
        self.calculatotal(self.codrecibo)
        print(self.calculatotal(self.codrecibo))
        self.fill_table()

    def removerow(self):

        if self.current_id == "":
            QMessageBox.information(self, "Info", "Selecione o registo a apagar na tabela")
            return


        if QMessageBox.question(self, "Pergunta", str("Deseja eliminar o registo %s?") % self.current_id,
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            sql = """delete from recibosdetalhe WHERE codfactura = "{codigo}" """.format(codigo=str(self.current_id))

            try:
                self.cur.execute(sql)
                self.conn.commit()
            except Exception as e:
                QMessageBox.warning(self, "Impossivel apagar dados", "Impossivel apagar dados."
                                                                     " Erro: {erro}".format(erro=e))
                return

            self.fill_table()
            self.calculatotal(self.codrecibo)
            QMessageBox.information(self, "Sucesso", "Item apagado com sucesso...")

    def closeEvent(self, QCloseEvent):
        print(self.recibo_finalizado(self.codrecibo))

        if self.recibo_finalizado(self.codrecibo) is False:
            if QMessageBox.question(self, "Recibo não finalizado", str("O Recibo não foi finalizado. Deseja sair?"),
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                sql = """delete from recibosdetalhe WHERE codrecibo = "{codigo}" """.format(codigo=str(self.codrecibo))
                sql2 = """delete from recibos WHERE cod = "{codigo}" """.format(codigo=str(self.codrecibo))
                try:
                    self.cur.execute(sql)
                    self.cur.execute(sql2)
                    self.conn.commit()
                except Exception as e:
                    QMessageBox.warning(self, "Impossivel apagar dados", "Impossivel apagar dados."
                                                                         " Erro: {erro}".format(erro=e))
                    return

            else:
                QCloseEvent.ignore()

    def removeall(self):

        if QMessageBox.question(self, "Pergunta", str("Deseja eliminar todos registos?"),
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            sql = """delete from recibosdetalhe WHERE codrecibo = "{codigo}" """.format(codigo=str(self.codrecibo))
            sql2 = """delete from recibos WHERE cod = "{codigo}" """.format(codigo=str(self.codrecibo))
            try:
                self.cur.execute(sql)
                self.cur.execute(sql2)
                self.conn.commit()
            except Exception as e:
                QMessageBox.warning(self, "Impossivel apagar dados", "Impossivel apagar dados."
                                                                     " Erro: {erro}".format(erro=e))
                return

            self.fill_table()
            self.calculatotal(self.codrecibo)
            QMessageBox.information(self, "Sucesso", "Dados apagados com sucesso...")


if __name__ == '__main__':

    app = QApplication(sys.argv)

    helloPythonWidget = MainWindow()
    helloPythonWidget.show()

    sys.exit(app.exec_())