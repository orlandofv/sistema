# -*- coding: utf-8 -*-
"""
Created on Fri Mar 02 23:18:43 2012

@author: lims
"""
import decimal
import sys
import datetime
import os
from time import strftime

from utilities import converte_para_pdf, Invoice, HORA, printWordDocument

from PyQt5.QtWidgets import (QDialog, QLabel, QVBoxLayout, QToolBar, QMessageBox,
    QAction, QApplication, QGridLayout, QComboBox, QGroupBox, QPushButton, QPlainTextEdit, QCalendarWidget,
                             QDateEdit, QProgressDialog)

from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog, QPrinterInfo
from PyQt5.QtCore import Qt, QSizeF, QDate, QDateTime
from PyQt5.QtGui import QIcon, QFont, QTextDocument, QPaintDevice
from relatorio.templates.opendocument import Template

from GUI.RibbonButton import RibbonButton
from GUI.RibbonWidget import *

from documentos import Cliente as doc
from clientes import Cliente as cl
from pricespinbox import price
from utilities import codigo as cd
from utilities import DATA_ACTUAL, DATA_HORA_FORMATADA, ANO_ACTUAL, DIA, MES
from decimal import Decimal

from maindialog import Dialog

import sqlite3 as lite


class Cliente(Dialog):
    def __init__(self, parent=None, titulo="", imagem=""):
        super(Cliente, self).__init__(parent, titulo, imagem)

        self.valor_total = Decimal(self.parent().totalgeral)
        self.user = self.parent().user
        self.cur = self.parent().cur
        self.conn = self.parent().conn

        self.valortransferencia = decimal.Decimal(0)
        self.valorcash = decimal.Decimal(0)
        self.valorcheque = 00
        self.valortroco = decimal.Decimal(0)
        self.soma = decimal.Decimal(0)

        # Varialvel que guarda a mensagem de crédito do Cliente
        self.messagem_de_credito = ""

        self.save_doc = "noprint"

        self.accoes()
        self.ui()

        self.enchedocumentos()
        self.encheclientes()
        self.getcoddocumento()
        self.codcliente = self.get_cod_cliente(self.combo_cliente.currentText())
        self.calculatroco()

    def ui(self):

        titulo = QLabel("decimal.Decimal(0)")
        titulo.setText('{}'.format(self.valor_total))
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
        # self.combo_documento.setEditable(True)
        self.combo_cliente = QComboBox()
        self.combo_cliente.setFont(boldFont2)
        self.combo_cliente.currentTextChanged.connect(self.get_cod_cliente)
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

        dinheiro = QLabel("Numerário (F6)")
        dinheiro.setFont(boldFont2)
        transferencia = QLabel("Móvel (F7)")
        transferencia.setFont(boldFont2)
        cheque = QLabel("POS (F8)")
        cheque.setFont(boldFont2)
        troco = QLabel("Troco")
        troco.setFont(boldFont2)
        obs = QLabel("Observações")

        self.line_pagamento_cash = price()
        self.line_pagamento_cash.setFocus()
        self.line_pagamento_cash.setValue(self.valor_total)
        self.line_pagamento_cash.valueChanged.connect(self.calculatroco)
        self.line_pagamento_cash.setMinimumHeight(30)
        self.line_pagamento_cash.setFont(boldFont2)
        self.line_pagamento_cash.setMinimumWidth(370)
        self.line_pagamento_movel = price()
        self.line_pagamento_movel.valueChanged.connect(self.calculatroco)
        self.line_pagamento_movel.setMinimumHeight(30)
        self.line_pagamento_movel.setFont(boldFont2)
        self.line_pagamento_movel.setMinimumWidth(370)
        self.line_pagamento_pos = price()
        self.line_pagamento_pos.valueChanged.connect(self.calculatroco)
        self.line_pagamento_pos.setMinimumHeight(30)
        self.line_pagamento_pos.setFont(boldFont2)
        self.line_pagamento_pos.setMinimumWidth(370)
        self.troco = price()
        self.troco.setMinimumHeight(30)
        self.troco.setFont(boldFont2)
        self.troco.setMinimumWidth(370)
        validade = QLabel("Data de Vencimento")
        validade.setFont(boldFont2)
        self.validade = QDateEdit(self)

        self.validade.setDate(QDate.currentDate().addDays(7))
        cal = QCalendarWidget()
        self.validade.setCalendarPopup(True)
        self.validade.setCalendarWidget(cal)
        self.obs = QPlainTextEdit()

        ly = QGridLayout()
        ly.addWidget(dinheiro, 0, 0, )
        ly.addWidget(self.line_pagamento_cash, 0, 1, 1, 7)
        ly.addWidget(transferencia, 1, 0)
        ly.addWidget(self.line_pagamento_movel, 1, 1, 1, 7)
        ly.addWidget(cheque, 2, 0)
        ly.addWidget(self.line_pagamento_pos, 2, 1, 1, 7)
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

        lay_todos_controlos = QVBoxLayout()
        lay_todos_controlos.addWidget(titulo)
        lay_todos_controlos.setContentsMargins(10, 10, 10, 10)
        lay_todos_controlos.addLayout(controlslayout)
        vLay.addLayout(lay_todos_controlos)
        vLay.addWidget(self.tool)
        self.layout().addLayout(vLay)

        self.setWindowTitle("Pagamentos")

    def accoes(self):
        self.tool = QToolBar()
        self.tool.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.gravar = QAction(QIcon("./icons/documentos.ico"), "&Imprimir \n POS(F2)", self)
        self.gravar_so = QAction(QIcon("./images/ok.png"), "&Gravar \n Apenas(F3)", self)
        self.gravar_grande = QAction(QIcon("./images/print.png"), "&Imprimir \n A4(F4)", self)
        self.fechar = QAction(QIcon("./images/filequit.png"), "&Fechar ou \n Cancelar(ESC)", self)

        gravar_so = RibbonButton(self, self.gravar_so, True)
        gravar = RibbonButton(self, self.gravar, True)
        gravar_grande = RibbonButton(self, self.gravar_grande, True)
        fechar = RibbonButton(self, self.fechar, True)

        self.tool.addWidget(gravar_so)
        # self.tool.addAction(self.gravar_so)
        self.tool.addSeparator()
        self.tool.addWidget(gravar)
        self.tool.addSeparator()
        self.tool.addWidget(gravar_grande)
        self.tool.addSeparator()
        self.tool.addWidget(fechar)

        self.gravar_so.triggered.connect(self.add_record)
        self.gravar.triggered.connect(self.save_pos)
        self.gravar_grande.triggered.connect(self.save_a4)
        self.fechar.triggered.connect(self.close)

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

    def save_pos(self):

        self.save_doc = "pos"
        self.add_record()

    def save_a4(self):
        self.save_doc = "save"
        self.add_record()

    def verifica_credito(self, codcliente):

        if self.coddocumento == 'DC20182222222':

            sql = """select credito from clientes WHERE cod = "{}" """.format(codcliente)

            self.cur.execute(sql)
            data = self.cur.fetchall()
            if len(data) > 0:
                credito = decimal.Decimal(data[0][0])
            else:
                credito = decimal.Decimal(0)

            sql = """select sum(saldo) from facturacao WHERE codcliente = "{}" 
            GROUP BY facturacao.codcliente """.format(codcliente)

            self.cur.execute(sql)
            data = self.cur.fetchall()

            if len(data) > 0:
                if data[0][0] is None:
                    saldo = decimal.Decimal(0)
                else:
                    saldo = decimal.Decimal(data[0][0])
            else:
                saldo = decimal.Decimal(0)

            # Se nao tiver direito a credito
            try:
                if self.parent().saldo == 1:
                    if credito == decimal.Decimal(0):
                        self.messagem_de_credito = "Cliente não tem direito a Crédito."
                        return False
                    # Se o saldo for maior ou igual ao credito
                    elif credito <= saldo:
                        self.messagem_de_credito = "Cliente tem Saldo superior ao Crédito." \
                                                   "\n Saldo: {}, Crédito máximo {}.".format(saldo, credito)
                        return False
                    # Se o crediro for menor que a soma do saldo e o valor total
                    elif credito <= saldo + self.valor_total:
                        self.messagem_de_credito = "Crédito Actual {} + Saldo {} superam o Crédito." \
                                                   "\n Saldo: {}, Crédito máximo {}.".format(self.valor_total,
                                                                                             saldo, saldo, credito)
                        return False
                    else:
                        return True
            except AttributeError:
                print("Nao se aplica saldo")

            return True

    def add_record(self):

        cancelar = QPushButton("Cancelar")
        cancelar.setEnabled(False)

        self.progress = QProgressDialog(self)
        self.progress.setWindowTitle("Criando o Documento...")
        self.progress.setLabel(QLabel("Criando o Documento...Por Favor aguarde."))
        self.progress.setEnabled(False)
        self.progress.setCancelButton(cancelar)
        self.progress.setMinimum(0)
        self.progress.setMaximum(10)

        self.progresso = 1
        self.progress.setValue(self.progresso)
        #
        # try:
        #     self.conn.cmd_refresh(1)
        # except Exception as e:
        #     QMessageBox.critical(self, "Erro na base de dados",
        #                          "Conexão com a Base de dados Perdida!!!\n{}.".format(e))
        if self.verifica_cliente(self.combo_cliente.currentText()) is False:
            self.grava_cliente()

        # Verifica o codido do cliente
        self.codcliente = self.get_cod_cliente(self.combo_cliente.currentText())

        if self.verifica_credito(self.codcliente) is False:
            QMessageBox.warning(self, "Crédito insuficiente",
                                "{}".format(self.messagem_de_credito))
            return

        if self.valor_total > self.soma:
            self.valorcash = self.valor_total
            self.valorcheque = 0
            self.valortransferencia = 0

            self.line_pagamento_cash.setValue(self.valor_total)
            self.line_pagamento_pos.setValue(decimal.Decimal(0))
            self.line_pagamento_movel.setValue(decimal.Decimal(0))
            if self.validade.date() < QDate.currentDate():
                QMessageBox.warning(self, "Erro nada Data", "A Data de Vencimento não pode ser menor que a Data actura")
                return

        error = None

        try:
            comissao = decimal.Decimal(self.parent().comissao.value())
            pagamento_agente = decimal.Decimal(self.parent().pagamento_agente.value())
            custo = comissao + pagamento_agente
        except AttributeError as e:
            error = e
            print(e)

        validade = self.validade.date().toString("yyyy-MM-dd")
        self.incrimenta(ANO_ACTUAL, self.coddocumento)

        pago = self.valorcheque + self.valorcash + self.valortransferencia
        self.valortroco = self.troco.value()

        self.progress.setModal(True)
        self.progress.show()
        self.progresso += 1
        self.progress.setValue(self.progresso)

        self.data_final = QDateTime.currentDateTime().toString('yyyy-MM-dd H:m:ss')
        data = QDateTime.currentDateTime().toString('yyyy-MM-dd H:m:ss')

        if error is not None:
            sql = """ UPDATE facturacao SET estado=1, numero={}, coddocumento="{}", codcliente="{}", troco={},
            banco={}, cash={}, tranferencia={}, finalizado=1, data="{}", created="{}", 
            debito={}, saldo={}, pago={}, validade="{}", obs="{}", caixa="{}" WHERE cod="{}" 
            """.format(self.numero, self.coddocumento, self.codcliente, self.valortroco, self.valorcheque, self.valorcash,
                       self.valortransferencia, data, data, 0, self.valor_total,
                       pago, validade, self.obs.toPlainText(), self.parent().caixa_numero, self.parent().codigogeral)
        else:
            print("Tem erro")
            sql = """ UPDATE facturacao SET estado=1, numero={}, coddocumento="{}", codcliente="{}", troco={},
                        banco={}, cash={}, tranferencia={}, finalizado=1, data="{}", created="{}", 
                        debito={}, saldo={}, pago={}, validade="{}", obs="{}", caixa="{}", lucro=subtotal-{}
                        WHERE cod="{}" 
                        """.format(self.numero, self.coddocumento, self.codcliente, self.valortroco, self.valorcheque,
                                   self.valorcash,
                                   self.valortransferencia, data, data, data,
                                   self.valor_total,
                                   pago, validade, self.obs.toPlainText(), self.parent().caixa_numero, custo,
                                   self.parent().codigogeral)
        print(sql)
        try:
            self.diminui_produtos()
            self.cur.execute(sql)
            self.conn.commit()

        except Exception as e:
            QMessageBox.warning(self, "Erro na gravação",
                                "Os seus dados não foram gravados. {}.".format(e))

        # Imprime os Recibos
        self.fazer_impressao()

        self.parent().gera_codigogeral()
        self.progress.setValue(self.progress.maximum())
        self.progress.close()
        self.close()

        if self.parent().parent() is not None:
            self.parent().close()


    def fazer_impressao(self):

        try:
            # Imprime recibo para o cliente
            print("Tentando imprimir")
            if self.save_doc == "save":
                self.imprime_recibo_grande2(self.parent().codigogeral, self.parent().fact_template, self.parent())
                # self.imprime_recibo_grande2(self.parent().codigogeral, 'copia.odt', self.parent())

            if self.save_doc == "pos":
                if self.parent().copias_pos1 in (None, 0, 1):
                    self.imprime_recibo(self.parent().codigogeral, self.parent())
                else:
                    for x in range(int(self.parent().copias_pos1)):
                        self.imprime_recibo(self.parent().codigogeral, self.parent())

            self.progresso += 1
            self.progress.setValue(self.progresso)
        except Exception as e:
            QMessageBox.warning(self, "Erro na criação de Documento",
                                "Houve erro na tentativa de criar Documento para imprimir. {}.".format(e))

    def closeEvent(self, QCloseEvent):

        ## RemoteDb(self)
        pass

    def verifica_se_diminui_stock(self, cod_documento):
        """
        Verifica se o documento em causa abate stock ou não
        :param cod_documento:
        :return:
        """
        if cod_documento == "":
            return False

        sql = """select stock from documentos WHERE cod = '{}' and stock=1 AND estado=1 """.format(cod_documento)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return True
        else:
            return False

    # Verifica se a relacao
    def verifica_relacao(self, codproduto, codarmazem):

        sql = """SELECT codproduto1, codproduto2, quantidade1, quantidade2, codarmazem
        FROM relacoes where codproduto1="{}" and codarmazem="{}" """.format(codproduto, codarmazem)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return True
        else:
            return False

    # Diminiu quantidades de produtos na tabela produtosdetalhe
    def diminui_produtos(self):

        # Verifica se documento tem o campo de stock=1, para diminuir stock
        if self.verifica_se_diminui_stock(self.coddocumento) is False:
            return

        sql = """SELECT facturacaodetalhe.quantidade, facturacaodetalhe.codproduto, facturacaodetalhe.codarmazem 
        FROM produtos INNER JOIN facturacaodetalhe ON produtos.cod=facturacaodetalhe.codproduto 
        WHERE codfacturacao = '{}' and produtos.tipo=0 """.format(self.parent().codigogeral)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                self.progresso += 1
                print("Diminuido {} do produto {}".format(item[0], item[1]))
                self.progress.setValue(self.progresso)

                sql = """UPDATE produtosdetalhe set quantidade=quantidade - {}, contagem=contagem+{}
                WHERE codproduto = "{}" AND codarmazem="{}" """.format(decimal.Decimal(item[0]),
                                                                   decimal.Decimal(item[0]),
                                                                   item[1], self.parent().codarmazem)

                self.cur.execute(sql)

                if self.verifica_relacao(item[1], self.parent().codarmazem) is True:
                    print("Produto {} tem links".format(item[1]))
                    self.update_links(item[1], self.parent().codarmazem, decimal.Decimal(item[0]))
                else:
                    print("Produto {} nao tem links".format(item[1]))

            try:
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                QMessageBox.warning(self, "Erro", "Erro na diminuição de stock.\n.".format(e))

    def update_links(self, codproduto, codarmazem, qt):

        r_sql = """SELECT r.codproduto1, r.codproduto2, r.quantidade1, r.quantidade2, p.custo, p.preco FROM 
        relacoes r
        JOIN produtos p ON p.cod=r.codproduto1  
        WHERE r.codproduto1="{}" 
        AND r.codarmazem="{}" """.format(codproduto, codarmazem)

        self.cur.execute(r_sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                preco = item[5]
                quantidade = item[2] * item[3] * qt
                subtotal_produto = 0
                desconto_produto = 0
                taxa_produto = 0
                total_produto = 0
                lucro_produto = 0
                custo_produto = item[4]
                codfacturacao = self.parent().codigogeral
                c_produto = item[1]

                print("\tActualizando a relacao do ITEM {}".format(c_produto))
                print("\tCodigo: {}, quantidade: {}, preco: {}, custo: {}.".format(codfacturacao, quantidade, preco,
                                                                                custo_produto))

                sql = """INSERT INTO facturacaodetalhe (codfacturacao, codproduto, custo, preco, quantidade,
                subtotal, desconto, taxa, total, lucro, codarmazem, print) VALUES 
                ("{}", "{}", {}, {}, {}, {}, {}, {}, {}, {}, "{}", 0) """.format(codfacturacao, c_produto, custo_produto, preco, quantidade,
                                   subtotal_produto, desconto_produto, taxa_produto, total_produto,
                                   lucro_produto, self.parent().codarmazem)
                #
                u_sql = """UPDATE produtosdetalhe set quantidade=quantidade - {}, contagem=contagem+{}
                WHERE codproduto = "{}" AND codarmazem="{}" """.format(quantidade, quantidade,
                                                                       c_produto, codarmazem)

                print(sql, "\n\n", u_sql)

                self.cur.execute(sql)
                self.cur.execute(u_sql)

    def get_numero_mesa(self, codfacturacao):
        sql = """SELECT numero FROM mesas WHERE codfacturacao="{}" """.format(codfacturacao)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return data[0][0]

        return None

    def total_de_items(self, codfacturacao):
        sql = """SELECT SUM(quantidade) from facturacaodetalhe WHERE codfacturacao="{}" """.format(codfacturacao)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        return Decimal(data[0][0])

    def imprime_recibo(self, codigo, parent):

        import codecs

        file = codecs.open('pos_template.html', 'r', encoding="utf-8")
        items_file = codecs.open('items.html', 'r', encoding="utf-8")
        items_contents = items_file.read()

        content = file.read()

        sql = """SELECT DISTINCT `codfacturacao`, `numerofactura`, `nomedocumento`, `data`, `user`, `subtotal_geral`, 
        `desconto_geral`, `taxa_geral`, `total_geral`, `extenso`, `cliente`, `endereco`, `NUIT`, `email`, `codproduto`, 
        `produto`, SUM(`quantidade`), `preco`, `desconto`, `taxa`, `subtotal`,  SUM(`total`), `ano`, `mes`, `pago`,
        `troco`, `coddocumento`, `contactos`, `validade`, `obs`, `nome` 
        FROM factura_geral WHERE codfacturacao = '{}' AND print=1  
        GROUP BY produto """.format(codigo)

        self.cur.execute(sql)
        data = self.cur.fetchall()
        items_list = data

        logo = ""

        if parent is not None:

            if parent.empresa_logo != "":
                logo = parent.empresa_logo

        empresa = parent.empresa
        endereco = parent.empresa_endereco
        nuit = parent.empresa_nuit
        contactos = parent.empresa_contactos
        documento = "{}: {}/{}{}".format(data[0][2], data[0][1], data[0][23], data[0][22])
        data_actual = data[0][3]
        user = data[0][4]
        cliente = data[0][10]

        numero_mesa = ""
        if self.get_numero_mesa(codigo) is not None:
            numero_mesa = "Mesa no.: {}".format(self.get_numero_mesa(codigo))

        if data[0][11] != "":
            cliente_endereco = data[0][11]

        if data[0][12] != "":
            cliente_nuit = data[0][12]

        total_items = self.total_de_items(codigo)
        subtotal = "{:20,.{casas}f}".format(data[0][5], casas=2)
        iva = "{:20,.{casas}f}".format(data[0][7], casas=2)
        total = "{:20,.{casas}f}".format(data[0][8], casas=2)
        pago  = "{:20,.{casas}f}".format(data[0][24], casas=2)
        trocos = "{:20,.{casas}f}".format(data[0][25], casas=2)
        contas = parent.contas

        items = ""
        for item in items_list:

            if item[16] == 0:
                preco = 0
            else:
                preco = item[21]/item[16]

            descricao = item[15]
            qt = item[16]
            total_linha = item[21]

            items += items_contents.format(descricao=descricao, qt=qt, preco=preco,
                                           total_linha=total_linha)

        receipt = content.format(logo=logo, empresa=empresa, endereco=endereco, nuit=nuit,
                                 contactos=contactos, documento=documento, data=data_actual, user=user,
                                 cliente=cliente, total_items=total_items, subtotal=subtotal,
                                 iva=iva, total=total, pago=pago, trocos=trocos,
                                 contas=contas, items=items, mesa=numero_mesa)

        printer = QPrinter()
        printer.setPrinterName(parent.pos1)
        printer.setResolution(72)
        # printer.setFullPage(True)

        printer.setPaperSize(QSizeF(self.parent().papel_1,  3276), printer.Millimeter)
        printer.setPageMargins(0, 0, 10, 0, QPrinter.Millimeter)

        document = QTextDocument()
        document.setHtml(receipt)
        document.setPageSize(QSizeF(printer.pageRect().size()))

        dialog = QPrintDialog()
        document.print_(printer)
        dialog.accept()

    def imprime_recibo_grande2(self, codigo, template, parent):

        sql = """SELECT * FROM factura_geral WHERE codfacturacao = '{}' AND print=1 """.format(codigo)

        try:
            self.cur.execute(sql)
            data = self.cur.fetchall()
        except Exception as e:
            QMessageBox.warning(self, 'Erro', e)
            return False

        logo = os.path.realpath(parent.empresa_logo)
        empresa = parent.empresa
        endereco = parent.empresa_endereco
        contactos = parent.empresa_contactos
        web = '{}, {}'.format(parent.empresa_email, parent.empresa_web)
        nuit = parent.empresa_nuit
        casas = parent.empresa_casas_decimais
        licenca = parent.licenca
        contas = parent.contas

        if len(data) > 0:

            doc = "{}/{}{}".format(data[0][1], data[0][23], data[0][22])

            # Data do documento
            data_doc = QDateTime.fromString(str(data[0][3]), 'yyyy-MM-dd H:mm:ss').toString("dd-MM-yyyy")

            # Data de Vencimento
            vencimento = QDateTime.fromString(str(data[0][28]), 'yyyy-MM-dd H:mm:ss').toString("dd-MM-yyyy")

            line = []
            for item in data:
                line += [{'item': {'name': item[15], 'reference': item[16], 'desc': item[32],
                                   'price': "{:20,.2f}".format(decimal.Decimal(item[19])), 'armazem': data[0][30]},
                          'quantity': "{:20,.2f}".format(decimal.Decimal(item[17])), 'codigo': item[14],
                          'amount': "{:20,.2f}".format(decimal.Decimal(item[20])), 'armazem': data[0][30]}, ]

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
                          subtotal="{:20,.2f}".format(data[0][5]),
                          desconto="{:20,.2f}".format(data[0][6]),
                          iva="{:20,.2f}".format(data[0][7]),
                          totalgeral="{:20,.2f}".format(data[0][8]),
                          armazem=data[0][30]
                          )

            # Verifica o Ficheiro de entrada Template
            filename = os.path.realpath('template.odt')
            if os.path.isfile(filename) is False:
                QMessageBox.critical(self, "Erro ao Imprimir",
                                     "O ficheiro modelo '{}'  não foi encontrado.".format(filename))
                return False

            # Ficheiro de Entrada
            targetfile = template

            if os.path.isfile(targetfile) is False:
                QMessageBox.critical(self, "Erro ao Imprimir",
                                     "O ficheiro modelo '{}'  não foi encontrado. \n "
                                     "Reponha-o para poder Imprimir".format(targetfile))
                return

            print("No basic", targetfile, filename)
            basic = Template(source='', filepath=targetfile)


            try:
                print("escrevendo no file")
                open(filename, 'wb').write(basic.generate(o=inv).render().getvalue())
            except Exception as e:
                QMessageBox.warning(self, 'Erro', 'Erro ao abrir ficheiro tempate.odt.\n{}.'.format(e.args[0]))
                return False

            print("Criando ficheiro de saida")
            doc_out = cd("0123456789") + "{}{}{}{}".format(data[0][2], data[0][1], data[0][23], data[0][22])

            print("Caminho real do ficheiro de saida e anexar o formato pdf")
            out = os.path.realpath("{}.pdf".format(doc_out))

            # Imprime para pdf usando unoconv, libreoffice ou openoffice
            # print("Criando caminho Python")

            # caminho = parent.caminho_python  # os.path.realpath("C:/Program Files/LibreOffice/program
            # /python-core-3.5.7/bin/python.exe")

            # Imprime para pdf usando libreoffice
            # converte_para_pdf(caminho, filename, out)

            # Imprime para pdf usando word
            printWordDocument(filename, out)

    def imprime_copia(self, codigo):

        sql = """SELECT * FROM factura_geral WHERE codfacturacao = '{}' AND print=1 """.format(codigo)

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
            for item in data:
                line += [{'item': {'name': item[15], 'reference': item[16],
                                   'price': decimal.Decimal(item[19]), 'armazem': data[0][30]},
                          'quantity': "{:20,.2f}".format(decimal.Decimal(item[17])), 'codigo': item[14],
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
                          iva = "{:20,.2f}".format(data[0][7]),
                          totalgeral=data[0][8],
                          armazem=data[0][30]
                          )

            # Verifica o Ficheiro de entrada Template
            filename = os.path.realpath('template.odt')
            if os.path.isfile(filename) is False:
                QMessageBox.critical(self, "Erro ao Imprimir",
                                     "O ficheiro modelo '{}'  não foi encontrado.".format(filename))
                return

            targetfile = 'copia.odt'

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

        # html += "<hr/>"

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
            html += "<center align='left'> [Nome da Empresa] </center>"
            html += "<center align='left'> [Endereco] </center>"
            html += "<center align='left'> [NUIT] </center>"
            html += "<center align='left'> [CONTACTOS] </center>"

        data_factura = str(data[0][3])

        sql = """select cod from documentos WHERE nome="{}" """.format(data[0][2])
        self.cur.execute(sql)
        dados = self.cur.fetchall()
        docs = ['DC20181111111', 'DC20182222222', 'DC20183333333']
        if dados[0][0] in docs:
            html += "<center align='left'> <h2 style='color: red;'> {}: {}/{}{} </h2> </center>".format(data[0][2], data[0][1],
                                                                                               data[0][23], data[0][22])
        else:
            html += "<center align='left'> <h2> {}: {}/{}{} </h2> </center>".format(data[0][2], data[0][1], data[0][23],
                                                                           data[0][22])

        html += "<center align='left'>DATA: {}</center>".format(data_factura)
        html += "<center align='left'>Operador: {}</center>".format(data[0][4])
        html += "<center align='left'>Exmo(a) Sr.(a): {}</center>".format(data[0][10])

        if data[0][11] != "":
            html += "<center align='left'>{}</center> ".format(data[0][11])

        if data[0][12] != "":
            html += "<center align='left'>NUIT: {}</center>".format(data[0][12])

        if data[0][13] != "":
            html += "<center align='left'>Contactos: {}</center>".format(data[0][13])

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
        html += "<center align='left'> {}</center>".format(self.parent().contas)
        html += "<center align='left'> Processado por Computador </center>".format(self.parent().licenca)

        document = QTextDocument()

        document.setHtml(html)
        dlg = QPrintPreviewDialog(self)

        dlg.paintRequested.connect(document.print_)
        dlg.showMaximized()
        dlg.exec_()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F3:
            if self.gravar.isVisible() or self.gravar.isEnabled():
                self.save_pos()
        elif event.key() == Qt.Key_F2:
            if self.gravar_so.isVisible() or self.gravar_so.isEnabled():
                self.add_record()
        elif event.key() == Qt.Key_F4:
            if self.gravar_grande.isEnabled() or self.gravar_grande.isVisible():
                self.save_a4()
        elif event.key() == Qt.Key_F6:
            self.editar_cash()
        elif event.key() == Qt.Key_F7:
            self.editar_movel()
        elif event.key() == Qt.Key_F8:
            self.editar_pos()
        elif event.key() == Qt.Key_Escape:
            self.close()
        else:
            event.ignore()

    def callback(self, is_ok):
        if is_ok:
            print('printing finished')
        else:
            print('printing error')

    def calculatroco(self):

        self.valorcash = Decimal(self.line_pagamento_cash.value())
        self.valortransferencia = Decimal(self.line_pagamento_movel.value())
        self.valorcheque = Decimal(self.line_pagamento_pos.value())

        trocos = self.trocos(self.valorcash, self.valorcheque, self.valortransferencia)
        self.troco.setValue(trocos)

        return trocos

    def trocos(self, cash, cheque, pos):

        self.soma = Decimal(cash) + Decimal(cheque) + Decimal(pos)

        if self.soma > self.valor_total:
            troco = self.soma - self.valor_total
            return Decimal(troco)
        else:
            return decimal.Decimal(0)

    def get_cod_cliente(self, nome_do_cliente):
        sql = """select cod from clientes WHERE nome= "{nome}" """.format(nome=nome_do_cliente)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            codcliente = "".join(data[0])
        else:
            codcliente = ""

        return codcliente

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
            self.validade.setDate(QDate.currentDate().addMonths(1))
        else:
            self.validade.setDate(QDate.currentDate())
            self.habilita_valores()

    def habilita_valores(self):
        """ metodo que desabilita a caixa de valores """

        self.line_pagamento_cash.setValue(self.valor_total)
        self.line_pagamento_movel.setValue(decimal.Decimal(0))
        self.line_pagamento_pos.setValue(decimal.Decimal(0))
        self.troco.setValue(decimal.Decimal(0))

        self.line_pagamento_cash.setEnabled(True)
        self.line_pagamento_movel.setEnabled(True)
        self.line_pagamento_pos.setEnabled(True)
    
    def editar_cash(self):
        if self.line_pagamento_cash.isEnabled():
            self.line_pagamento_cash.setFocus()

            return True

        return False

    def editar_pos(self):
        if self.line_pagamento_pos.isEnabled():
            self.line_pagamento_pos.setFocus()
            return True

        return False

    def editar_movel(self):
        if self.line_pagamento_movel.isEnabled():
            self.line_pagamento_movel.setFocus()
            return True

        return False

    def desabilita_valores(self):
        """ metodo que desabilita a caixa de valores """

        self.line_pagamento_cash.setValue(decimal.Decimal(0))
        self.line_pagamento_movel.setValue(decimal.Decimal(0))
        self.line_pagamento_pos.setValue(decimal.Decimal(0))
        self.troco.setValue(decimal.Decimal(0))

        self.line_pagamento_cash.setEnabled(False)
        self.line_pagamento_movel.setEnabled(False)
        self.line_pagamento_pos.setEnabled(False)
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

        self.codcliente = self.get_cod_cliente(self.combo_cliente.currentText())

        cli = cl(self)
        if self.codcliente == "":
            cli.nome.setText(self.combo_cliente.currentText())
        else:
            cli.cod.setText(self.codcliente)

        cli.mostrar_registo()
        cli.setModal(True)
        cli.show()
    #
    # def enterEvent(self, *args, **kwargs):
    #     self.encheclientes()
    #     self.enchedocumentos()

    # Enche a combobox clientes com Lista de clientes
    def encheclientes(self):

        self.combo_cliente.clear()

        # Mostra clientes Inactivos
        try:
            if self.parent().cliente_inactivo == 1:
                sql = """SELECT nome FROM clientes ORDER BY nome"""
            else:
                sql = """SELECT nome FROM clientes WHERE estado=1 ORDER BY nome"""
        except Exception as e:
            QMessageBox.warning(self, "Erro", "Erro na listagem de Clientes.\n{}".format(e))
            sql = """SELECT nome FROM clientes ORDER BY nome"""

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                self.combo_cliente.addItems(item)

        self.combo_cliente.setCurrentText("")

    # Enche a combobox documento com Lista de documentos
    def enchedocumentos(self):

        self.combo_documento.clear()

        if self.parent().admin is True:
            sql = """SELECT nome FROM documentos WHERE estado=1"""
        else:
            sql = """SELECT nome FROM documentos WHERE visivel=1 AND estado=1"""

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


if __name__ == '__main__':
    app = QApplication(sys.argv)

    helloPythonWidget = Cliente()
    helloPythonWidget.show()

    sys.exit(app.exec_())