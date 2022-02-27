# -*- coding: utf-8 -*-
"""
Created on Fri Mar 02 23:18:43 2012

@author: lims
"""
import decimal
import datetime
import os
import sys

from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QToolBar, QMessageBox, \
    QAction, QApplication, QTableView, QAbstractItemView, QComboBox, QFormLayout, QPushButton, QDateTimeEdit, \
    QCalendarWidget
from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter, QPrintDialog, QPrinterInfo
from PyQt5.QtCore import QSizeF, Qt, QDateTime
from PyQt5.QtGui import QIcon, QTextDocument, QBrush, QFont

from sortmodel import MyTableModel
from utilities import codigo as cd
from utilities import printWordDocument, Invoice, CamposdaTabela
from relatorio.templates.opendocument import Template

from lista_de_clientes_extrato import MainWindow as cl
from utilities import ANO_ACTUAL, converte_para_pdf

import sqlite3 as lite

DB_FILENAME = "dados.tsdb"
LISTA_DOC = ["VD", "Factura", "Recibo"]


class Cliente(QDialog):
    def __init__(self, parent=None):
        super(Cliente, self).__init__(parent)

        self.user = self.parent().user

        self.accoes()
        self.ui()

        if self.parent() is None:
            self.db = self.connect_db()
        else:
            self.cur = self.parent().cur
            self.conn = self.parent().conn

        self.codfacturacao = ""
        self.coddocumento = ""

        self.encher_clientes()
        self.enche_ano()
        self.enche_caixas()

    def ui(self):
        html = """<center style= "background-image: './images/control.png'" > <h2 > Cancelamento/Impressão de Documentos </h2> </center> """

        self.conta = 0

        titulo = QLabel(html)

        vLay = QVBoxLayout()
        self.tabela = QTableView(self)

        # self.tabela.clicked.connect(self.clickedslot)
        self.tabela.setAlternatingRowColors(True)

        # hide grid
        self.tabela.setShowGrid(False)

        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        # set the font

        # hide vertical header
        vh = self.tabela.verticalHeader()
        vh.setVisible(False)

        # set horizontal header properties and stretch last column
        hh = self.tabela.horizontalHeader()
        hh.setStretchLastSection(True)

        # set column width to fit contents
        self.tabela.resizeColumnsToContents()

        # enable sorting
        self.tabela.setSortingEnabled(True)

        label = QLabel("Selecione o Tipo Documento")
        label3 = QLabel("Selecione o Documento")

        self.ano = QComboBox()
        self.documentos_box = QComboBox()
        self.documento_numero = QComboBox()
        self.data = QDateTimeEdit()
        print(self.data.displayFormat())
        self.data.setDisplayFormat('dd-MM-yyyy h:mm:ss')
        self.data.setCalendarPopup(True)
        self.data.setCalendarWidget(QCalendarWidget(self))
        self.clientes_combo = QComboBox()
        self.cliente_butao = QPushButton("Alterar C&liente")
        self.cliente_butao.clicked.connect(self.grava_cliente)

        self.data_butao = QPushButton("Alterar D&ata")
        self.data_butao.clicked.connect(self.grava_data)

        self.documentos_box.currentTextChanged.connect(lambda: self.getcoddocumento(self.documentos_box.currentText()))
        self.ano.currentTextChanged.connect(lambda: self.getcoddocumento(self.documentos_box.currentText()))

        self.documento_numero.currentTextChanged.connect(self.getcodfactura)
        self.documentos_box.setFocus()

        formlay = QFormLayout()

        formlay.addRow(QLabel("Ano"), self.ano)
        formlay.addRow(label, self.documentos_box)
        formlay.addRow(label3, self.documento_numero)
        formlay.addRow(QLabel("Data do documento"), self.data)
        formlay.addWidget(self.data_butao)
        formlay.addRow(QLabel("Selecione o Cliente"), self.clientes_combo)
        formlay.addWidget(self.cliente_butao)

        vLay.addWidget(titulo)
        vLay.addLayout(formlay)
        vLay.addWidget(self.tabela)
        vLay.addWidget(self.tool)
        self.setLayout(vLay)

        self.setWindowTitle("Cancelamento/Impressão de Documentos")

        style = """
            margin: 0;
            padding: 0;
            border-image:url(./images/transferir.jpg) 30 30 stretch;
            background:#303030;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 12px;
            color: #FFFFFF;
        """

        titulo.setStyleSheet(style)

    def grava_cliente(self) -> bool:
        if self.codfacturacao is None or self.codfacturacao == "":
            return False

        sql = """UPDATE facturacao set codcliente="{}" WHERE cod="{}" """.format(
            self.get_codcliente(self.clientes_combo.currentText()), self.codfacturacao)

        print(sql)

        try:
            self.cur.execute(sql)
            self.conn.commit()
            QMessageBox.information(self, "Sucesso", "Cliente actualizado com sucesso!")
            return True
        except Exception as e:
            QMessageBox.warning(self, "Erro", "Cliente não foi actualizado.\n{}".format(e))
            return False

    def grava_data(self) -> bool:
        if self.codfacturacao is None or self.codfacturacao == "":
            return False

        sql = """UPDATE facturacao set created="{}", data="{}" WHERE cod="{}" """.format(
        self.data.date().toString('yyyy-MM-dd'), self.data.date().toString('yyyy-MM-dd'), self.codfacturacao)

        print(sql)

        if self.data.dateTime() > QDateTime.currentDateTime():
            QMessageBox.warning(self, "Data errada", "A data não pode ser superior a data actual")
            return False

        try:
            self.cur.execute(sql)
            self.conn.commit()
            QMessageBox.information(self, "Sucesso", "Data actualizada com sucesso!")
        except Exception as e:
            QMessageBox.warning(self, "Erro", "Data não foi actualizada.\n{}".format(e))
            return False

        return True

    def encher_clientes(self):
        sql = """SELECT nome FROM clientes"""
        self.cur.execute(sql)
        data = self.cur.fetchall()

        self.clientes_combo.clear()

        print("Enchendo Clientes...")

        if len(data) > 0:
            for nome in data:
                self.clientes_combo.addItem(nome[0])

        return data

    def get_codcliente(self, nome):
        sql = """SELECT cod from clientes WHERE nome="{}" """.format(nome)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        codcliente = None

        if len(data) > 0:
            codcliente = data[0][0]

        return codcliente

    def accoes(self):
        self.tool = QToolBar()
        self.tool.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.cancelar = QAction(QIcon("./icons/cancel.ico"), "&Cancelar\nDocumento", self)
        # self.cancelar.setEnabled(self.parent().admin)

        self.activar = QAction(QIcon("./images/ok.png"), "&Activar\nDocumento", self)
        # self.activar.setEnabled(self.parent().admin)

        self.imprimir_POS = QAction(QIcon("./icons/documentos.ico"), "&Imprimir\nPOS", self)
        self.imprimir_A4 = QAction(QIcon("./images/print.png"), "I&mprimir\nA4", self)
        self.usar_items = QAction(QIcon("./icons/down.ico"), "Usar\nItems", self)
        self.extrato = QAction(QIcon("./icons/coins.ico"), "Extracto\ndo Cliente", self)
        self.fechar = QAction(QIcon("./images/filequit.png"), "&Fechar", self)

        self.tool.addAction(self.cancelar)
        self.tool.addAction(self.activar)
        self.tool.addSeparator()
        self.tool.addAction(self.imprimir_POS)
        self.tool.addAction(self.imprimir_A4)
        self.tool.addSeparator()
        self.tool.addAction(self.usar_items)
        self.tool.addSeparator()
        self.tool.addAction(self.extrato)
        self.tool.addSeparator()
        self.tool.addAction(self.fechar)

        self.activar.triggered.connect(lambda: self.activar_desactivar_doc(1))
        self.cancelar.triggered.connect(lambda: self.activar_desactivar_doc(0))
        self.usar_items.triggered.connect(lambda: self.usar_Items(self.codfacturacao))
        self.imprimir_A4.triggered.connect(lambda: self.segundavia_A4(self.codfacturacao))
        self.imprimir_POS.triggered.connect(lambda: self.segundavia_POS(self.codfacturacao))
        self.extrato.triggered.connect(self.extracto_clientes)
        self.fechar.triggered.connect(self.close)

    def enche_ano(self):
        sql = "select DISTINCT ano from facturacao group by ano order by ano"

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                self.ano.addItem(str(item[0]))

        self.ano.setCurrentText(str(ANO_ACTUAL))

    def extracto_clientes(self):

        cliente = cl(self)
        cliente.find_w.setText(self.clientes_combo.currentText())
        cliente.fill_table()
        cliente.show()

    def usar_Items(self, cod_factura):

        if self.documentos_box.currentText() == 'Recibo':
            QMessageBox.warning(self, "Erro", "Essa função não pode ser aplicada para Recibos!")
            return False

        codigogeral = "FT" + cd("FT" + "abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")

        sql = "select * from facturacao WHERE cod = '{}'".format(cod_factura)

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        if len(data) > 0:

            for x in data:
                lista = list(x)
                lista[0] = codigogeral
                lista[27] = 0
                lista[1] = 0
                lista[2] = "DC20184444444"
                tupla = tuple(lista)

            # Insere dados na tabela facturacao
            facturacao_sql = "INSERT INTO facturacao VALUES {} ".format(tupla)

            print("Ja passei facturacao")

            # Trabalhando com a tabela codfacturacao
            sql = "select * from facturacaodetalhe WHERE codfacturacao = '{}'".format(cod_factura)
            self.cur.execute(sql)
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]

            list_sql = []
            count = 0

            if len(data) > 0:
                for x in data:
                    lista = list(x)

                    print(lista)

                    # Retiramos a chave secundaria para criar nova entrada
                    lista.pop(0)
                    print(lista)
                    lista[0] = codigogeral
                    lista.pop(11)
                    print(lista)
                    lista.pop(12)
                    lista.pop(12)
                    print(lista)

                    print(lista)

                    tupla = tuple(lista)

                    t = CamposdaTabela()
                    t.cur = self.cur
                    t.database = self.parent().database
                    t.tabela = "facturacaodetalhe"

                    print(tupla)

                    detalhe_sql = """INSERT INTO facturacaodetalhe 
                    (codfacturacao, codproduto, custo, preco, quantidade, subtotal, desconto, taxa, total, lucro, 
                    codarmazem, created) VALUES {} """.format(tupla)

                    count += 1

                    list_sql.append(detalhe_sql)
            try:
                self.cur.execute(facturacao_sql)

                for d_sql in list_sql:
                    self.cur.execute(d_sql)

                if self.parent() is not None:
                    self.codfacturacao = codigogeral
                    self.parent().codigogeral = codigogeral
                    self.parent().fill_table()
                    self.parent().line_codigoproduto.setFocus()
                    self.parent().calcula_total_geral()
                    self.parent().butao_apagarItem.setEnabled(True)
                    self.parent().butao_apagarTudo.setEnabled(True)

                self.conn.commit()
                self.close()
            except Exception as e:
                self.conn.rollback()
                QMessageBox.warning(self, "Erro", "Erro na conversão do documento.\n{}".format(e))

    def imprime_recibo2(self, codigo):

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
        vencimento = data[0][2]

        if len(data) > 0:
            doc = "{}/{}{}".format(data[0][14], data[0][15], data[0][16])
            try:
                data_doc = datetime.datetime.strptime(str(data[0][17]), "%Y-%m-%d").strftime("%d-%m-%Y")
            except ValueError:
                data_doc = ""

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
                QMessageBox.critical(self, "Erro ao Imprimir", "O ficheiro modelo 'template.odt'  não foi encontrado.")
                return

            targetfile = self.parent().rec_template

            if os.path.isfile(targetfile) is False:
                QMessageBox.critical(self, "Erro ao Imprimir",
                                     "O ficheiro modelo '{}'  não foi encontrado. \n "
                                     "Reponha-o para poder Imprimir".format(targetfile))
                return

            basic = Template(source='', filepath=targetfile)
            open(filename, 'wb').write(basic.generate(o=inv).render().getvalue())

            doc_out =cd("0123456789") + "{}{}{}{}".format("Recibo", data[0][14], data[0][15], data[0][16])
            out = os.path.realpath("'{}'.pdf".format(doc_out))
            print(out)

            # caminho = self.parent().caminho_python  # os.path.realpath("C:/Program Files/LibreOffice/program
            # /python-core-3.5.7/bin/python.exe")

            # converte_para_pdf(caminho, filename, out)

            printWordDocument(filename, out)

    def imprime_recibo(self):
        sql = """SELECT * FROM recibo_geral WHERE cod = '{}' """.format(self.codfacturacao)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        # LOGOTIPO
        html = """
                                       < table width="100%" style="float: right; border: 1px solid red;">
                                           < tr >
                                               < td > 
                                               < img src = '{}' width = "80" > 
                                               < / td >
                                           </ tr >
                                       < / table > 
                                       """.format(self.parent().empresa_logo)

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

        sql = """select cod from documentos WHERE nome='{}' """.format("Recibo")
        self.cur.execute(sql)
        dados = self.cur.fetchall()
        docs = ['DC20181111111', 'DC20182222222', 'DC20183333333']
        if dados[0][0] in docs:
            html += "<p align='right'> <h2 style='color: red;'> {}: {}/{}{} </h2> </p>".format("Recibo",
                                                                                               data[0][14], data[0][15],
                                                                                               data[0][16])
        else:
            html += "<p align='right'> <h2> {}: {}/{}{} </h2> </p>".format(data[0][2], data[0][1], data[0][23],
                                                                           data[0][22])

        html += "<p align='right'>DATA: {}</p>".format(data_factura)
        html += "<p align='right'>Operador: {}</p>".format(data[0][4])

        html += "<p>Exmo(a) Sr.(a): {}</p>".format(data[0][8])

        if data[0][11] != "":
            html += "<p>{}</p> ".format(data[0][9])

        if data[0][12] != "":
            html += "<p>NUIT: {}</p>".format(data[0][10])

        if data[0][13] != "":
            html += "<p>Contactos: {}</p>".format(data[0][11])

        html += "<hr/>"

        html += "<table border=0 width = 80mm style='border: 1px;'>"
        html += "<tr style='background-color: gray;'>"
        html += "<th width = 80% align='left'>Descrição</th>"
        html += "<th width = 20% align='right'>Total</th>"
        html += "</tr>"

        for cliente in data:
            html += """<tr> <td>{}</td>  <td align="right">{:20,.2f}</td> </tr> """.format(cliente[5], cliente[7])

        html += "</table>"

        html += "<table border=0 width = 100% style='border: 1px;'>"
        html += "<hr/>"
        html += "<tr width = 100%>"
        html += "<th width = 100% align='right'><td> <td> <b> TOTAL </b> </td> <td align='right'>" \
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

    def imprime_recibo_grande2(self, codigo):

        sql = """SELECT * FROM factura_geral WHERE codfacturacao = '{}' AND print=1 """.format(codigo)

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
            for item in data:
                line += [{'item': {'name': item[15], 'reference': item[16],
                                   'price': decimal.Decimal(item[19]), 'armazem': data[0][30]},
                          'quantity': "{:20,.2f}".format(decimal.Decimal(item[17])), 'codigo': item[14],
                          'amount': decimal.Decimal(item[20]), 'armazem': data[0][30]}, ]

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
                          iva="{:20,.2f}".format(data[0][7]),
                          totalgeral=data[0][8],
                          armazem=data[0][30]
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

            print("No basic", targetfile, filename)
            basic = Template(source='', filepath=targetfile)

            print("escrevendo no file")
            open(filename, 'wb').write(basic.generate(o=inv).render().getvalue())

            print("Criando ficheiro de saida")
            doc_out = cd("0123456789") + "{}{}{}{}".format(data[0][2], data[0][1], data[0][23], data[0][22])

            print("Caminho real do ficheiro de saida e anexar o formato pdf")
            out = os.path.realpath("'{}'.pdf".format(doc_out))

            # Imprime para pdf usando unoconv, libreoffice ou openoffice
            # print("Criando caminho Python")
            caminho = self.parent().caminho_python  # os.path.realpath("C:/Program Files/LibreOffice/program
            # /python-core-3.5.7/bin/python.exe")

            # converte_para_pdf(caminho, filename, out)

            # Imprime para pdf usando word
            printWordDocument(filename, out)

    def segundavia_A4(self, codigo):

        try:
            if self.documentos_box.currentText() == 'Recibo':
                self.imprime_recibo2(codigo)
            else:
                from facturas import Cliente
                f = Cliente(self.parent())
                f.imprime_recibo_grande2(codigo, self.parent().fact_template, self.parent())
                # f.imprime_recibo_grande2(codigo, 'copia.odt', self.parent())
        except Exception as e:
            QMessageBox.critical(self, "Erro", e.args[0])
            return False

        return True

    def segundavia_POS(self, codigo):
        from facturas import Cliente

        if self.documentos_box.currentText() != 'Recibo':
            f = Cliente(self.parent())
            print("imprimindo recibo")
            try:
                f.imprime_recibo(codigo, self.parent())
            except Exception as e:
                QMessageBox.warning(self, "Erro", "{}".format(e))
                return False

        return True

    def verifica_diminui(self, cod_documento):

        if cod_documento == "":
            return False

        sql = """select stock from documentos WHERE cod = '{}' and stock=1 """.format(cod_documento)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return True
        else:
            return False

    # Aumanta quantidades de produtos na tabela produtosdetalhe
    def aumenta_produtos(self):

        # Verifica se documento tem o campo de stock=1, para diminuir stock
        if self.verifica_diminui(self.coddocumento) == False:
            return

        sql = """SELECT facturacaodetalhe.quantidade, facturacaodetalhe.codproduto, facturacaodetalhe.codarmazem 
        FROM produtos INNER JOIN facturacaodetalhe ON produtos.cod=facturacaodetalhe.codproduto 
        WHERE codfacturacao = '{}' and produtos.tipo=0 """.format(self.codfacturacao)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                sql = """UPDATE produtosdetalhe set quantidade = quantidade + {}
                WHERE codproduto = "{}" AND codarmazem="{}" """.format(item[0], item[1], item[2])

                self.cur.execute(sql)

            try:
                self.conn.commit()
            except Exception as e:
                QMessageBox.warning(self, "Erro", "Erro na diminuição de stock.\n.".format(e))

    # Diminiu quantidades de produtos na tabela produtosdetalhe
    def diminui_produtos(self):

        # Verifica se documento tem o campo de stock=1, para diminuir stock
        if self.verifica_diminui(self.coddocumento) == False:
            return

        sql = """SELECT facturacaodetalhe.quantidade, facturacaodetalhe.codproduto, facturacaodetalhe.codarmazem 
        FROM produtos INNER JOIN facturacaodetalhe ON produtos.cod=facturacaodetalhe.codproduto 
        WHERE codfacturacao = '{}' and produtos.tipo=0 """.format(self.codfacturacao)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                sql = """UPDATE produtosdetalhe set quantidade = quantidade - {}
                WHERE codproduto = "{}" AND codarmazem="{}" """.format(item[0], item[1], item[2])

                self.cur.execute(sql)

            try:
                self.conn.commit()
            except Exception as e:
                QMessageBox.warning(self, "Erro", "Erro na diminuição de stock.\n.".format(e))

    def verifica_estado(self, coddocumento):
        if coddocumento == "":
            return

        sql = """SELECT estado from facturacao WHERE cod="{}" """.format(coddocumento)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
                return int(data[0][0])

    def activar_desactivar_doc(self, estado):
        if self.documentos_box.currentText() == "" or self.codfacturacao=='':
            QMessageBox.warning(self, "Aviso", "Nenhum documento selecionado.")
            return

        if estado == 0:
            accao = "cancelado"
        else:
            accao = "activado"

        if self.coddocumento == 'DC20183333333':
            sql = "update recibos set estado = {} WHERE cod ='{}' ".format(estado, self.codfacturacao)
            self.cur.execute(sql)
        else:

            if estado == 1:
                if self.verifica_estado(self.codfacturacao) == 1:
                    QMessageBox.warning(self, "Aviso", "Documento está {}.".format(accao))
                    return

                self.diminui_produtos()
            else:
                if self.verifica_estado(self.codfacturacao) == 0:
                    QMessageBox.warning(self, "Aviso", "Documento está {}.".format(accao))
                    return

                self.aumenta_produtos()

            sql = """UPDATE facturacao set estado = {} WHERE cod='{}' """.format(estado, self.codfacturacao)
            self.cur.execute(sql)

        try:
            self.conn.commit()
            QMessageBox.information(self, "Informação", "Documento {}.".format(accao))
        except Exception as e:
            self.conn.rollback()
            QMessageBox.warning(self, "Aviso", "Dacumento não foi cancelado.\n{}.".format(e))

    def enche_caixas(self):

        sql = "select documentos.nome from documentos"

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                self.documentos_box.addItem(item[0])

    def getcodfactura(self):

        if self.documento_numero.currentText() == "":
            self.codfacturacao = ""
            return

        if self.documentos_box.currentText() == 'Recibo':

            sql = """select cod from recibos WHERE 
            numero={} and ano={} """.format(self.documento_numero.currentText(), int(self.ano.currentText()))
        else:
            sql = """select codfacturacao from factura_geral WHERE 
            numerofactura={} and nomedocumento='{}' and ano={} """.format(
            self.documento_numero.currentText(), self.documentos_box.currentText(), int(self.ano.currentText()))

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data)> 0:
            self.codfacturacao = data[0][0]
            self.enche_cliente(self.codfacturacao)
        else:
            self.codfacturacao = ""
            self.documento_numero.clear()

        self.fill_table(self.codfacturacao)

    def enche_cliente(self, cod_factura):

        if self.documentos_box.currentText() == 'Recibo':
            sql = """select nome, created from recibo_geral WHERE cod = '{}' """.format(cod_factura)
        else:
            sql = """select distinct cliente, data from factura_geral WHERE codfacturacao = '{}' """.format(cod_factura)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            self.clientes_combo.setCurrentText(data[0][0])
            self.data.setDate(data[0][1])

    def getcoddocumento(self, nome_documento):

        # Limpamos o codigo de Facturacao
        self.codfacturacao = ""

        if nome_documento == "":
            return

        sql = "select cod from documentos WHERE nome='{}' ".format(nome_documento)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            self.coddocumento = data[0][0]

            self.enchedocumentos(self.coddocumento)

    def enchedocumentos(self, cod_documento):

        self.documento_numero.clear()
        if cod_documento == 'DC20183333333':
            sql = """select numero, cod from recibos WHERE ano={} and numero>0 order by numero desc """.format(int(self.ano.currentText()))
        else:
            sql = """select distinct numerofactura, codfacturacao from factura_geral WHERE coddocumento = '{}'
            and ano={} and numerofactura>0 group by numerofactura order by numerofactura desc """.format(cod_documento, int(self.ano.currentText()))

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                self.documento_numero.addItem(str(item[0]))

                self.codfacturacao = item[1]

            self.getcodfactura()

        else:
            self.codfacturacao = ""
            self.documento_numero.clear()

    def fill_table(self, cod_facturacao):

        if cod_facturacao == "":return

        if self.documentos_box.currentText() == 'Recibo':
            sql = """select factura, descricao, total from recibo_geral 
            WHERE cod='{}' """.format(cod_facturacao)
            header = ["Factura", "Descrição", "Total"]
        else:
            sql = """select quantidade, produto, preco, taxa, total from factura_geral 
                       WHERE codfacturacao='{}' """.format(cod_facturacao)
            header = ["Quantiade", "Descrição", "Preço", "Taxa","Total"]

        try:
            self.cur.execute(sql)
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]

        except:
            return

        if len(data) == 0:
            if self.documentos_box.currentText() == 'Recibo':
                self.tabledata = ['', '', '']
            else:
                self.tabledata = ['', '', '', '', '']

        try:
            self.tabledata = data
            # set the table model
            self.tm = MyTableModel(self.tabledata, header, self)
            self.totalItems = self.tm.rowCount(self)
            self.tabela.setModel(self.tm)

        except:
            return

        # # set row height
        nrows = len(self.tabledata)
        for row in range(nrows):
            self.tabela.setRowHeight(row, 25)

    def closeEvent(self, evt):
        parent = self.parent()
        try:
            if parent is not None:
                parent.fill_table()
        except:
            return

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
