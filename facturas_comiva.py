# -*- coding: utf-8 -*-
"""
Created on Fri Mar 02 23:18:43 2012

@author: lims
"""
import decimal
import sys
import datetime
import os
from time import localtime, strftime
from utilities import printWordDocument, Invoice

from PyQt5.QtWidgets import (QDialog, QLabel, QVBoxLayout, QToolBar, QMessageBox,
    QAction, QApplication, QGridLayout, QComboBox, QGroupBox, QPushButton, QPlainTextEdit, QCalendarWidget, QDateEdit)

from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog, QPrinterInfo
from PyQt5.QtCore import Qt, QSizeF, QDate
from PyQt5.QtGui import QIcon, QFont, QTextDocument
from relatorio.templates.opendocument import Template

from documentos import Cliente as doc
from clientes import Cliente as cl
from pricespinbox import price
from utilities import codigo as cd
from decimal import Decimal
from update_remote_db import RemoteDb

import sqlite3 as lite

DB_FILENAME = "dados.tsdb"

DATA_HORA_FORMATADA = strftime("%Y-%m-%d %H:%M:%S", localtime())
DATA_ACTUAL = datetime.datetime.today()
date = datetime.datetime.now().date()
ANO_ACTUAL = DATA_ACTUAL.year
DIA = DATA_ACTUAL.day
MES = DATA_ACTUAL.month
LISTA_DOC = ["VD", "Factura"]

class Cliente(QDialog):
    def __init__(self, parent=None):
        super(Cliente, self).__init__(parent)

        if self.parent() is not None:
            self.valortotal = Decimal(self.parent().totalgeral)
            self.user = self.parent().user
        else:
            self.valortotal = Decimal(0.00)
            self.user = ""

        self.valortransferencia = 0.00
        self.valorcash = 0.00
        self.valorcheque = 00
        self.valortroco = 0.00
        self.soma = 0.00

        self.save_doc = "noprint"

        self.accoes()
        self.ui()

        if self.parent() is None:
            self.db = self.connect_db()
        else:
            self.cur = self.parent().cur
            self.conn = self.parent().conn

        self.enchedocumentos()
        self.encheclientes()
        self.getcoddocumento()
        self.getcodcliente()
        self.calculatroco()

    def ui(self):

        titulo = QLabel("0.00")
        titulo.setText('{}'.format(self.valortotal))
        titulo.setMaximumHeight(70)
        titulo.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        boldFont = QFont('Consolas', 24)
        boldFont.setBold(True)
        titulo.setFont(boldFont)

        boldFont2 = QFont('Consolas', 12)
        boldFont2.setBold(True)

        clientegrupo = QGroupBox("Detalhes do Cliente")
        clientegrupo.setMaximumHeight(70)
        documentogrupo = QGroupBox("Detalhes do Documento")
        documentogrupo.setMaximumHeight(70)
        detalhesgrupo = QGroupBox("Dados de Pagamanto")

        documento = QLabel("Documento")
        documento.setMinimumWidth(100)
        cliente = QLabel("Cliente")
        cliente.setMinimumWidth(100)

        self.combo_documento = QComboBox()
        # self.combo_documento.setEnabled(False)
        self.combo_documento.setFont(boldFont2)
        self.combo_documento.currentTextChanged.connect(self.getcoddocumento)
        self.combo_documento.setEditable(True)
        self.combo_cliente = QComboBox()
        self.combo_cliente.setFont(boldFont2)
        self.combo_cliente.currentTextChanged.connect(self.getcodcliente)
        self.combo_cliente.setEditable(True)
        self.butao_gravarcliente = QPushButton(QIcon("./icons/add.ico"), "")
        self.butao_gravarcliente.clicked.connect(self.edita_cliente)
        self.butao_gravarcliente.setMaximumWidth(80)
        self.butao_gravarcliente.setMinimumWidth(80)
        self.butao_gravardocumento = QPushButton(QIcon("./icons/add.ico"), "")
        self.butao_gravardocumento.setEnabled(False)
        self.butao_gravardocumento.clicked.connect(self.gravadocumento)
        self.butao_gravardocumento.setMaximumWidth(80)
        self.butao_gravardocumento.setMinimumWidth(80)

        dinheiro = QLabel("Numerário")
        dinheiro.setFont(boldFont2)
        transferencia = QLabel("Transferência")
        transferencia.setFont(boldFont2)
        cheque = QLabel("Cheque")
        cheque.setFont(boldFont2)
        troco = QLabel("Troco")
        troco.setFont(boldFont2)
        obs = QLabel("Observações")

        self.dinheiro = price()
        self.dinheiro.setFocus()
        self.dinheiro.setValue(self.valortotal)
        self.dinheiro.valueChanged.connect(self.calculatroco)
        self.dinheiro.setMinimumHeight(30)
        self.dinheiro.setFont(boldFont2)
        self.dinheiro.setMinimumWidth(370)
        self.transferencia = price()
        self.transferencia.valueChanged.connect(self.calculatroco)
        self.transferencia.setMinimumHeight(30)
        self.transferencia.setFont(boldFont2)
        self.transferencia.setMinimumWidth(370)
        self.cheque = price()
        self.cheque.valueChanged.connect(self.calculatroco)
        self.cheque.setMinimumHeight(30)
        self.cheque.setFont(boldFont2)
        self.cheque.setMinimumWidth(370)
        self.troco = price()
        self.troco.setMinimumHeight(30)
        self.troco.setFont(boldFont2)
        self.troco.setMinimumWidth(370)
        validade = QLabel("Data de Vencimento")
        validade.setFont(boldFont2)
        self.validade = QDateEdit(self)
        self.validade.setDisplayFormat('yyyy-MM-dd')
        print(self.validade.date())

        self.validade.setDate(QDate.currentDate().addDays(30))
        cal = QCalendarWidget()
        self.validade.setCalendarWidget(cal)
        self.validade.setCalendarPopup(True)
        self.obs = QPlainTextEdit()

        ly = QGridLayout()
        ly.addWidget(dinheiro, 0, 0, )
        ly.addWidget(self.dinheiro, 0, 1, 1, 7)
        ly.addWidget(transferencia, 1, 0)
        ly.addWidget(self.transferencia, 1, 1, 1, 7)
        ly.addWidget(cheque, 2, 0)
        ly.addWidget(self.cheque, 2, 1, 1, 7)
        ly.addWidget(troco, 3, 0)
        ly.addWidget(self.troco, 3, 1, 1, 7)
        ly.addWidget(validade, 4, 0)
        ly.addWidget(self.validade, 4, 1)
        ly.addWidget(obs, 5, 0)
        ly.addWidget(self.obs, 6, 0, 1, 8)
        detalhesgrupo.setLayout(ly)

        documentoLayout = QGridLayout()
        documentoLayout.addWidget(documento, 0, 0)
        documentoLayout.addWidget(self.combo_documento, 0, 1, 1, 5)
        documentoLayout.addWidget(self.butao_gravardocumento, 0, 7)

        documentogrupo.setLayout(documentoLayout)

        clientelayout = QGridLayout()
        clientelayout.addWidget(cliente, 0, 0)
        clientelayout.addWidget(self.combo_cliente, 0, 1, 1, 5)
        clientelayout.addWidget(self.butao_gravarcliente, 0, 7)

        clientegrupo.setLayout(clientelayout)

        controlslayout = QVBoxLayout()
        controlslayout.addWidget(documentogrupo)
        controlslayout.addWidget(clientegrupo)
        controlslayout.addWidget(detalhesgrupo)

        vLay = QVBoxLayout()

        vLay.addWidget(titulo)
        vLay.addLayout(controlslayout)
        vLay.addWidget(self.tool)
        self.setLayout(vLay)

        self.setWindowTitle("Pagamentos")

    def accoes(self):
        self.tool = QToolBar()
        self.tool.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        gravar_so = QAction(QIcon("./images/ok.png"), "&Gravar Apenas", self)
        gravar = QAction(QIcon("./icons/documentos.ico"), "&Imprimir POS", self)
        gravar_grade = QAction(QIcon("./images/print.png"), "&Imprimir A4", self)
        fechar = QAction(QIcon("./images/filequit.png"), "&Fechar", self)

        self.tool.addAction(gravar_so)
        self.tool.addSeparator()
        self.tool.addAction(gravar)
        self.tool.addSeparator()
        self.tool.addAction(gravar_grade)
        self.tool.addSeparator()
        self.tool.addAction(fechar)

        gravar_so.triggered.connect(self.add_record)
        gravar.triggered.connect(self.save_POS)
        gravar_grade.triggered.connect(self.save_A4)

        fechar.triggered.connect(self.fechar)

    # Método que incrimenta documentos baseando no ano.
    def incrimenta(self, ano, coddocumento):
        sql = """select max(numero) from facturacao WHERE ano={ano} and 
        coddocumento="{coddoc}" """.format(ano=ano, coddoc=coddocumento)

        try:
            self.cur.execute(sql)
            data = self.cur.fetchall()
        except Exception as e:
            return

        if data[0][0] is None:
            self.numero = 1
        else:
            self.numero = data[0][0] + 1

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

    def save_noprint(self):
        self.save_doc = "noprint"
        self.add_record()

    def save_POS(self):

        self.save_doc = "pos"
        self.add_record()

    def save_A4(self):
        self.save_doc = "save"
        self.add_record()

    def add_record(self):

        if self.verifica_cliente(self.combo_cliente.currentText()) is False:
            self.grava_cliente()

        self.getcodcliente()

        if self.valortotal > self.soma:
            self.valorcash = self.valortotal
            self.valorcheque = 0
            self.valortransferencia = 0

            self.dinheiro.setValue(self.valortotal)
            self.cheque.setValue(0.00)
            self.transferencia.setValue(0.00)
            if self.validade.date() < QDate.currentDate():
                QMessageBox.warning(self, "Erro nada Data", "A Data de Vencimento não pode ser menor que a Data actura")
                return
            else:
                validade = self.validade.text()

        validade = self.validade.text()
        self.incrimenta(ANO_ACTUAL, self.coddocumento)

        pago = self.valorcheque + self.valorcash + self.valortransferencia
        self.valortroco = self.troco.value()

        sql = """ UPDATE facturacao SET numero={}, coddocumento="{}", codcliente="{}", troco={},
        banco={}, cash={}, tranferencia={}, finalizado=1, data="{}", created="{}", modified="{}", 
        debito={}, saldo={}, pago={}, validade="{}", obs="{}"  WHERE cod="{}" 
        """.format(self.numero, self.coddocumento, self.codcliente, self.valortroco, self.valorcheque, self.valorcash,
                   self.valortransferencia, DATA_HORA_FORMATADA, date, date, self.valortotal, self.valortotal,
                   pago, validade, self.obs.toPlainText(), self.parent().codigogeral)
        try:
            self.diminui_produtos()

            self.cur.execute(sql)
            self.conn.commit()

            # Imprime recibo para o cliente
            if self.save_doc == "save":
                self.imprime_recibo_grande2(self.parent().codigogeral)

            if self.save_doc == "pos":
                self.imprime_recibo(self.parent().codigogeral)

            self.parent().gera_codigogeral()
            self.close()

        except Exception as e:
            QMessageBox.warning(self, "Erro na criação de Recibos",
                                "Os seus dados não foram gravados. {}.".format(e))
        
        self.fechar()

    def closeEvent(self, QCloseEvent):

        RemoteDb(self)

    def verifica_diminui(self, cod_documento):

        if cod_documento == "":
            return

        sql = """select stock from documentos WHERE cod = '{}' and stock=1 """.format(cod_documento)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return True
        else:
            return False

    def diminui_produtos(self):

        if self.verifica_diminui(self.coddocumento) == False:
            return

        sql = """select quantidade, codproduto from facturacaodetalhe WHERE codfacturacao = '{}' 
                """.format(self.parent().codigogeral)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        sql2 = """select stock from documentos WHERE cod = '{}' """.format(self.coddocumento)
        self.cur.execute(sql2)
        data2 = self.cur.fetchall()

        if len(data2) > 0:
            if data2[0][0] == 1:
                if len(data) > 0:
                    for item in data:
                        sql = """UPDATE produtos set quantidade = quantidade - {} WHERE cod = '{}' """.format(item[0], item[1])
                        self.cur.execute(sql)

    def imprime_recibo(self, codigo):

        sql = """SELECT * FROM factura_geral WHERE codfacturacao = '{}' """.format(codigo)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        # LOGOTIPO
        # html = """
        #                   < table
        #                       width = "100%" >
        #                       < tr >
        #                           < td >
        #                           < img src = '{}' width = "80" >
        #                           < / td >
        #                       </ tr >
        #                   < / table >
        #                   """.format(self.parent().empresa_logo)

        html = ""

        if self.parent() is not None:
            html += "<center> {} </center>".format(self.parent().empresa)
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
        html += "<th width = 10%>Qt.</th>"
        html += "<th width = 60%>Descrição</th>"
        html += "<th width = 30% align='right'>Total</th>"
        html += "</tr>"

        for cliente in data:
            html += """<tr> <td>{}</td> <td>{}</td> <td align="right">{}</td> </tr>
                               """.format(cliente[16], cliente[15], cliente[21])

        html += "</table>"

        html += "<table>"

        html += "<tr>"
        html += "<th width = 50% align='right'>TOTAL</th>"
        html += "<td width = 50% align='right'>{:20,.{casas}f} </td>".format(cliente[8],
                                                                             casas=self.parent().empresa_casas_decimais)
        html += "</tr>"

        # Se o valor pago for maior que o total
        if cliente[24] > cliente[8]:
            html += "<tr>"
            html += "<th width = 50% align='right'>VALOR PAGO</th>"
            html += "<th width = 50% align='right'>{:20,.{casas}f}</th>".format(cliente[24],
                                                                                casas=self.parent().empresa_casas_decimais)
            html += "</tr>"

            html += "<tr>"
            html += "<th width = 50% align='right'>TROCO</th>"
            html += "<th width = 50% align='right'>{:20,.{casas}f}</th>".format(cliente[25],
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

        sql = """SELECT * FROM factura_geral WHERE codfacturacao = '{}' """.format(codigo)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        logo = os.path.realpath(self.parent().empresa_logo)
        empresa =  self.parent().empresa
        endereco = self.parent().empresa_endereco
        contactos = self.parent().empresa_contactos
        web = '{}, {}'.format(self.parent().empresa_email , self.parent().empresa_web)
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

    def imprime_recibo_grande(self, codigo):

        sql = """SELECT * FROM factura_geral WHERE codfacturacao = '{}' """.format(codigo)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        # LOGOTIPO
        # html = """
        #         < table width="100%" height=100%>
        #             < tr >
        #                 < td >
        #                 < img src = '{}' width = "80" >
        #                 < / td >
        #             </ tr >
        #         < / table >
        #         """.format(self.parent().empresa_logo)
        #
        #html += "<hr/>"

        html = ""
        
        if self.parent() is not None:

            empresa_info = """ < table width="100%" style='border-style:solid 1px;border-width:0;'>
                            < tr > < td width="50%"> <h2> {} </h2> < / td > </ tr > 
                            < tr > < td > {} < / td > </ tr >
                            < tr > < td > {} < / td > </ tr >
                            < tr > < td > {} < / td > </ tr >
                        < / table > 
                        """.format(self.parent().empresa, self.parent().empresa_endereco, self.parent().empresa_nuit,
                                   self.parent().empresa_contactos)

            html += """ < table width="100%" style="decimal.Decimal: right; border: 1 solid red;">
                < tr > < td > {} < / td >  < td > {} < / td > </ tr >
             </table>""".format(empresa_info, "")
        else:
            html += "<p> [Nome da Empresa] </p>"
            html += "<p> [Endereco] </p>"
            html += "<p> [NUIT] </p>"
            html += "<p> [CONTACTOS] </p>"

        data_factura = str(data[0][3])

        sql = """select cod from documentos WHERE nome="{}" """.format(data[0][2])
        self.cur.execute(sql)
        dados = self.cur.fetchall()
        docs = ['DC20181111111', 'DC20182222222', 'DC20183333333']
        if dados[0][0] in docs:
            html += "<p align='right'> <h2 style='color: red;'> {}: {}/{}{} </h2> </p>".format(data[0][2], data[0][1],
                                                                                               data[0][23], data[0][22])
        else:
            html += "<p align='right'> <h2> {}: {}/{}{} </h2> </p>".format(data[0][2], data[0][1], data[0][23],
                                                                           data[0][22])

        html += "<p align='right'>DATA: {}</p>".format(data_factura)
        html += "<p align='right'>Operador: {}</p>".format(data[0][4])
        html += "<p>Exmo(a) Sr.(a): {}</p>".format(data[0][10])

        if data[0][11] != "":
            html += "<p>{}</p> ".format(data[0][11])

        if data[0][12] != "":
            html += "<p>NUIT: {}</p>".format(data[0][12])

        if data[0][13] != "":
            html += "<p>Contactos: {}</p>".format(data[0][13])

        html += "<hr/>"

        html += "<table border='0' width = 80mm style='border: 1px;'>"
        html += "<tr style='background-color: gray;'>"
        html += "<th width = 10% align='center'>Qt.</th>"
        html += "<th width = 40%>Descrição</th>"
        html += "<th width = 10% align='right'>Preco</th>"
        html += "<th width = 10% align='right'>IVA</th>"
        html += "<th width = 10% align='right'>Desconto</th>"
        html += "<th width = 10% align='right'>Subtotal</th>"
        html += "<th width = 10% align='right'>Total</th>"
        html += "</tr>"

        for cliente in data:
            html += """<tr> <td align='center'>{}</td>  <td>{}</td>  <td align="right">{}</td>  <td align="right">{}</td>
            <td align="right">{}</td>  <td align="right">{}</td>  <td align="right">{}</td> </tr>
            """.format(cliente[16], cliente[15], cliente[17], cliente[19], cliente[18], cliente[20], cliente[21])

        html += "</table>"

        html += "<table border='0' width = '100%' style='border: 1px;'>"
        html += "<hr/>"
        html += "<tr width = '100%'>"
        html += "<th width = '100%' align='right'><td> <td> <b> SUBTOTAL </b> </td> <td align='right'>" \
                " <b> {:20,.{casas}f} </b> </td></th>".format(cliente[5], casas=self.parent().empresa_casas_decimais)

        html += "</tr>"

        html += "<tr>"
        html += "<th width = '100%' align='right'><td> <td> <b> DESCONTO </b> </td> <td align='right'> " \
                "<b> {:20,.{casas}f} </b> </td></th>".format(cliente[6], casas=self.parent().empresa_casas_decimais)
        html += "</tr>"

        html += "<tr>"
        html += "<th width = '100%' align='right'><td> <td> <b> IVA </b> </td> <td align='right'> " \
                "<b> {:20,.{casas}f} </b> </td></th>".format(cliente[7],
                                                                             casas=self.parent().empresa_casas_decimais)
        html += "</tr>"

        html += "<tr>"
        html += "<th width = '100%' align='right'> <td><td> <b> TOTAL </b> </td> <td align='right'>" \
                "<b> {:20,.{casas}f} </b> </td> </th>".format(cliente[8],
                                                                             casas=self.parent().empresa_casas_decimais)
        html += "</tr>"
        html += "</table>"

        html += "<hr/>"
        html += "<p> {}</p>".format(self.parent().contas)
        html += "<p> Processado por Computador </p>".format(self.parent().licenca)

        document = QTextDocument()

        document.setHtml(html)
        dlg = QPrintPreviewDialog(self)

        for child in dlg.children():
            print(child)

        dlg.paintRequested.connect(document.print_)
        dlg.showMaximized()
        dlg.exec_()

    def callback(self, is_ok):
        if is_ok:
            print('printing finished')
        else:
            print('printing error')

    def calculatroco(self):

        self.valorcash = Decimal(self.dinheiro.value())
        self.valortransferencia = Decimal(self.transferencia.value())
        self.valorcheque = Decimal(self.cheque.value())

        self.troco.setValue(self.trocos(self.valorcash, self.valorcheque, self.valortransferencia))

    def trocos(self, cash, cheque, pos):

        self.soma = Decimal(cash) + Decimal(cheque) + Decimal(pos)

        if self.soma > self.valortotal:
            troco = self.soma - self.valortotal
            return Decimal(troco)
        else:
            return 0.00

    def fechar(self):
        self.close()
        # Busca o codigo do cliente baseando no cliente seleccionado

    def getcodcliente(self):
        sql = """select cod from clientes WHERE nome= "{nome}" """.format(nome=self.combo_cliente.currentText())

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            self.codcliente = "".join(data[0])
        else:
            self.codcliente = ""

    # Busca o codigo do documento baseando no documento seleccionado
    def getcoddocumento(self):
        sql = """select cod from documentos WHERE nome= "{nome}" """.format(nome=self.combo_documento.currentText())

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            self.coddocumento = "".join(data[0])
        else:
            self.coddocumento = ""

        if self.coddocumento != "DC20181111111":
            self.desabilita_valores()
        else:
            self.habilita_valores()

    def habilita_valores(self):
        """ metodo que desabilita a caixa de valores """

        self.dinheiro.setValue(self.valortotal)
        self.transferencia.setValue(0.00)
        self.cheque.setValue(0.00)
        self.troco.setValue(0.00)

        self.dinheiro.setEnabled(True)
        self.transferencia.setEnabled(True)
        self.cheque.setEnabled(True)
        self.troco.setEnabled(True)

    def desabilita_valores(self):
        """ metodo que desabilita a caixa de valores """

        self.dinheiro.setValue(0.00)
        self.transferencia.setValue(0.00)
        self.cheque.setValue(0.00)
        self.troco.setValue(0.00)

        self.dinheiro.setEnabled(False)
        self.transferencia.setEnabled(False)
        self.cheque.setEnabled(False)
        self.troco.setEnabled(False)

    def gravadocumento(self):

        cl = doc(self)
        if self.coddocumento == "":
            cl.nome.setText(self.combo_documento.currentText())
        else:
            cl.cod.setText(self.coddocumento)

        cl.mostrar_registo()
        cl.setModal(True)
        cl.show()

    def grava_cliente(self):

        code = "CL" + cd("abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")

        if self.combo_cliente.currentText() == "":
            nome = "Cliente Normal"
        else:
            nome = self.combo_cliente.currentText()
        endereco = ""
        nuit = ""
        email = ""
        contactos = ""
        desconto = 0
        valor_minimo = 0
        obs = ""
        estado = 1
        created = QDate.currentDate().toString('yyyy-MM-dd')
        modified = QDate.currentDate().toString('yyyy-MM-dd')

        if self.parent() is not None:
            modified_by = self.parent().user
        else:
            modified_by = "User"
        if self.parent() is not None:
            created_by = self.parent().user
        else:
            created_by = "User"

        values = """ "{cod}", "{nome}", "{endereco}", "{NUIT}", "{email}", "{contactos}", {valor_desconto} ,
                     {valor_minimo}, "{obs}", "{estado}", "{created}", "{modified}", "{modified_by}", "{created_by}"
                      """.format(cod=code, nome=nome, endereco=endereco, NUIT=nuit, email=email,
                                 contactos=contactos,
                                 valor_desconto=desconto, valor_minimo=valor_minimo, obs=obs, estado=estado,
                                 created=created, modified=modified, modified_by=modified_by, created_by=created_by)
        try:
            sql = "INSERT INTO clientes (cod, nome, endereco, NUIT,email, contactos, desconto, valor_minimo, " \
                  "obs, estado, created, modified, modified_by, created_by)" \
                  " values({value})".format(value=values)
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            # QMessageBox.warning(self, "Erro", "Cliente não for gravado, grave manualmente")
            return False

        self.codcliente = code

    def edita_cliente(self):

        cli = cl(self)
        if self.codcliente == "":
            cli.nome.setText(self.combo_cliente.currentText())
        else:
            cli.cod.setText(self.codcliente)

        cli.mostrar_registo()
        cli.setModal(True)
        cli.show()

    # Enche a combobox clientes com Lista de clientes
    def encheclientes(self):

        self.combo_cliente.clear()

        sql = """SELECT nome FROM clientes"""
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                self.combo_cliente.addItems(item)

        self.combo_cliente.setCurrentText("")

    # Enche a combobox documento com Lista de documentos
    def enchedocumentos(self):

        self.combo_documento.clear()

        sql = """SELECT nome FROM documentos"""
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                if item[0] != "Recibo":
                    self.combo_documento.addItem(item[0])

            # self.combo_documento.setCurrentText("VD")

    def focusInEvent(self, *args, **kwargs):
        self.encheclientes()
        self.combo_cliente.setFocus()

    def connect_db(self):
        # Connect to database and retrieves data
        try:
            self.conn = lite.connect(DB_FILENAME)
            self.cur = self.conn.cursor()

        except Exception as e:
            QMessageBox.critical(self, "Erro ao conectar a Base de Dados",
                                 "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
            sys.exit(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    helloPythonWidget = Cliente()
    helloPythonWidget.show()

    sys.exit(app.exec_())