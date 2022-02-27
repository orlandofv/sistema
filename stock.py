# -*- coding: utf-8 -*-
"""
Created on Fri Mar 02 23:18:43 2012

@author: lims
"""

import sys
import decimal

from PyQt5.QtWidgets import  QLabel, QLineEdit, QFormLayout, QVBoxLayout, QToolBar, QMessageBox,\
    QTextEdit, QAction, QApplication, QGroupBox, QPushButton, QComboBox, QDateEdit, QCalendarWidget,\
    QHBoxLayout, QWidget, QTableView, QAbstractItemView, QSplitter, QDialog, QSizePolicy, QShortcut

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon, QKeySequence

from sortmodel import MyTableModel

from utilities import codigo as cd
from pricespinbox import price
from produtos import Produto as prod
from taxas import Cliente as tx
from fornecedores import Fornecedor
from armazem import Armazem

import sqlite3 as lite

DB_FILENAME = "dados.tsdb"

class Cliente(QDialog):
    def __init__(self, parent=None):
        super(Cliente, self).__init__(parent)

        self.codfornecedor = ""
        self.codproduto = ""
        self.codarmazem = ""
        self.valortaxa = decimal.Decimal(0)
        self.current_id = ""
        self.codigogeral = ""
        self.numero_doc = ""
        self.total_doc = decimal.Decimal(0)
        self.quantidade_produto = decimal.Decimal(0)
        self.custo_produto = decimal.Decimal(0)
        self.preco_actural = decimal.Decimal(0)

        self.accoes()
        self.ui()

        if self.parent() is None:
            self.db = self.connect_db()
        else:
            self.cur = self.parent().cur
            self.conn = self.parent().conn
            self.user = self.parent().user

        # verifica a existencia dos dados na base de dados
        self.existe(self.cod.text())

        # Mostraregisto caso exista
        self.mostrar_registo(self.codigogeral)

        self.enche_fornecedor()
        self.enchearmazem()

    def ui(self):
        html = """<center style= "background-image: './images/control.png'" > <h2 > Cadastro de stock </h2> </center> """

        controlslayout = QVBoxLayout()
        controlswidget = QWidget()

        splitter = QSplitter()
        splitter.setOrientation(Qt.Horizontal)

        grupocod = QGroupBox("Código do Documento")
        grupofornecedor = QGroupBox("Detalhes do Documento")
        grupodetalhes = QGroupBox("Items do Documento")

        codlayout = QFormLayout()
        fornecedorlayout = QFormLayout()
        detalheslayout = QFormLayout()

        titulo = QLabel(html)

        titulo.setMaximumHeight(30)

        cod = QLabel("Codigo")
        self.cod = QLineEdit()
        self.cod.setEnabled(False)

        codlayout.addRow(cod, self.cod)
        grupocod.setLayout(codlayout)

        fornecedor = QLabel("Selecione o Fornecedor")
        documento = QLabel("Numero do documento (Ex. Factura1235)")
        datadocumento = QLabel("Data do Documento")
        valor_subtotal =  QLabel("Subtotal")
        valor_documento = QLabel("Valor Total do Documento")
        valor_iva = QLabel("Valor de IVA")
        self.gravar_fornecedor = QPushButton("Gravar documento")
        self.gravar_fornecedor.clicked.connect(self.gravardoc)
        self.ativar_fornecedor = QPushButton("Ativar documento")
        self.ativar_fornecedor.clicked.connect(self.habilitarfornecedor)
        self.ativar_fornecedor.setEnabled(False)

        fornecedor_layout = QHBoxLayout()
        self.fornecedor = QComboBox()
        self.fornecedor.setEditable(True)
        self.fornecedor_button = QPushButton(QIcon("./icons/add.ico"), "")
        self.fornecedor_button.clicked.connect(self.gravar_fornecedores)
        fornecedor_layout.addWidget(self.fornecedor)
        fornecedor_layout.addWidget(self.fornecedor_button)
        # self.fornecedor.currentTextChanged.connect(self.enche_fornecedor)
        self.fornecedor.currentIndexChanged.connect(lambda: self.getcodfornecedor(self.fornecedor.currentText()))
        self.numerodocumento = QLineEdit()
        self.datadocumento = QDateEdit()
        self.datadocumento.setDate(QDate.currentDate())
        self.datadocumento.setCalendarPopup(True)
        calendario = QCalendarWidget()
        self.datadocumento.setCalendarWidget(calendario)
        self.valor_subtotal = price()
        self.valor_subtotal.valueChanged.connect(self.calcula_taxa_e_total)
        self.valor_documento = price()
        self.valor_iva = price()

        self.gravardetalhe = QPushButton("Adicionar na Lista")
        self.gravardetalhe.clicked.connect(self.gravardetalhes)
        self.apagarItem = QPushButton("Eliminar Linha")
        self.apagarItem.clicked.connect(self.removerow)
        self.apagarItem.setEnabled(False)

        gravarlayout = QHBoxLayout()

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)

        gravarlayout.addWidget(spacer)
        gravarlayout.addWidget(self.gravar_fornecedor)
        gravarlayout.addWidget(self.ativar_fornecedor)

        fornecedorlayout.addRow(fornecedor, fornecedor_layout)
        fornecedorlayout.addRow(documento, self.numerodocumento)
        fornecedorlayout.addRow(datadocumento, self.datadocumento)
        fornecedorlayout.addRow(valor_subtotal, self.valor_subtotal)
        fornecedorlayout.addRow(valor_iva, self.valor_iva)
        fornecedorlayout.addRow(valor_documento, self.valor_documento)
        fornecedorlayout.addRow(gravarlayout)
        grupofornecedor.setLayout(fornecedorlayout)

        produto = QLabel("Selecione o produto")
        quantidade = QLabel("Qty")
        custo = QLabel("Custo do Produto")
        armazem = "Selecione o Armazém"
        preco = QLabel("Preço Actual")

        self.produto_lineedit = QLineEdit()
        self.findproduto = QPushButton(QIcon("./images/search-icon.png"), "")
        self.produto = QComboBox()
        self.produto.currentIndexChanged.connect(lambda: self.getcodproduto(self.produto.currentText()))
        self.produto.currentTextChanged.connect(lambda: self.getcodproduto(self.produto.currentText()))
        self.findproduto.clicked.connect(self.enche_produtos)
        self.produto_button = QPushButton(QIcon("./icons/add.ico"), "")
        self.produto_button.clicked.connect(self.gravar_produto)
        self.produto.setEditable(True)

        findprodutolayout = QHBoxLayout()
        findprodutolayout.addWidget(self.produto_lineedit)
        findprodutolayout.addWidget(self.findproduto)

        produtolayout = QHBoxLayout()
        produtolayout.addWidget(self.produto)
        produtolayout.addWidget(self.produto_button)

        self.quantidade = price()
        self.validade = QDateEdit(self)

        self.validade.setDate(QDate.currentDate().addYears(1))
        self.validade.setCalendarPopup(True)
        cal = QCalendarWidget()
        self.validade.setCalendarWidget(cal)

        self.quantidade.setRange(1, 999999999999)
        self.quantidade.setSingleStep(1)
        self.custo = price()
        armazemlayout = QHBoxLayout()
        self.armazem = QComboBox()
        self.armazem_button = QPushButton(QIcon("./icons/add.ico"), "")
        self.armazem_button.clicked.connect(self.gravar_armazem)
        armazemlayout.addWidget(self.armazem)
        armazemlayout.addWidget(self.armazem_button)
        self.armazem.setEditable(True)
        # self.armazem.currentTextChanged.connect(self.enchearmazem)
        self.armazem.currentIndexChanged.connect(lambda: self.getcodarmazem(self.armazem.currentText()))
        self.preco = price()

        self.tabela = QTableView(self)
        self.tabela.clicked.connect(self.clickedslot)
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
        
        butoesdetalheleyout = QHBoxLayout()

        spacer1 = QWidget()
        spacer1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        butoesdetalheleyout.addWidget(spacer1)
        butoesdetalheleyout.addWidget(self.gravardetalhe)

        detalheslayout.addRow(QLabel("Cod./Descrição"), findprodutolayout)
        detalheslayout.addRow(produto, produtolayout)
        detalheslayout.addRow(quantidade, self.quantidade)
        detalheslayout.addRow(QLabel("Validade"), self.validade)
        detalheslayout.addRow(custo, self.custo)
        detalheslayout.addRow(armazem, armazemlayout)
        detalheslayout.addRow(preco, self.preco)
        #detalheslayout.addRow(taxalayout)
        # detalheslayout.addRow(self.tabela)
        detalheslayout.addRow(butoesdetalheleyout)
        grupodetalhes.setLayout(detalheslayout)

        controlslayout.addWidget(grupocod)
        controlslayout.addWidget(grupofornecedor)
        controlslayout.addWidget(grupodetalhes)

        controlswidget.setLayout(controlslayout)

        splitter.addWidget(controlswidget)


        tabela_btn_lay = QHBoxLayout()

        spacer2 = QWidget()
        spacer2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)

        tabela_btn_lay.addWidget(spacer2)
        tabela_btn_lay.addWidget(self.apagarItem)

        tabela_lay = QVBoxLayout()
        tabela_lay.addWidget(self.tabela)
        tabela_lay.addLayout(tabela_btn_lay)
        tabela_w = QWidget()

        tabela_w.setLayout(tabela_lay)

        splitter.addWidget(tabela_w)

        mainlayout = QVBoxLayout()
        mainlayout.setContentsMargins(10, 10, 10, 10)

        mainlayout.addWidget(splitter)
        mainlayout.addWidget(self.tool)

        grand_lay = QVBoxLayout()
        grand_lay.setContentsMargins(0, 0, 0, 0)

        grand_lay.addWidget(titulo)
        grand_lay.addLayout(mainlayout)

        self.setLayout(grand_lay)

        self.setWindowTitle("Entrada de Novo STOCK")

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

        self.produto_button.setFixedWidth(30)
        self.armazem_button.setFixedWidth(self.produto_button.width())
        self.fornecedor_button.setFixedWidth(self.produto_button.width())
        self.findproduto.setFixedWidth(self.produto_button.width())

        if self.fornecedor_button.isDefault():
            self.gravardetalhe.setDefault(True)

        self.gravardetalhe.setDefault(True)

        QShortcut(QKeySequence("Enter"), self.produto_lineedit, self.enche_produtos)
        QShortcut(QKeySequence("16777220"), self.produto_lineedit, self.enche_produtos)

    def accoes(self):
        self.tool = QToolBar()
        self.tool.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        gravar = QAction(QIcon("./images/ok.png"), "Gravar\nDados", self)
        # eliminar = QAction(QIcon(-"./icons/new.ico"), "Limpar\nCampos", self)

        fechar = QAction(QIcon("./images/filequit.png"), "&Fechar", self)

        self.tool.addAction(gravar)
        # self.tool.addAction(eliminar)

        self.tool.addSeparator()
        self.tool.addAction(fechar)

        gravar.triggered.connect(self.finalizar_doc)
        # eliminar.triggered.connect(self.limpar)
        fechar.triggered.connect(self.fechar)

    # ==============================================================================
    def fill_table(self):

        header = ["cod", "Documento", "Descrição", "Qty", "Custo", "Preço", "Custo Total", "Armazém"]

        sql = """ select stockdetalhe.cod, stockdetalhe.codstock, produtos.nome, stockdetalhe.quantidade, 
        stockdetalhe.custo, stockdetalhe.valor, stockdetalhe.total, armazem.nome from produtos INNER JOIN stockdetalhe 
        ON produtos.cod=stockdetalhe.codproduto 
        INNER JOIN armazem ON armazem.cod=stockdetalhe.codarmazem 
        WHERE codstock="{codstock}" """.format(codstock=self.cod.text())

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        if len(data) == 0:
            self.tabledata = [('', '', "", "", "", "", "", "")]

            self.apagarItem.setEnabled(False)
        else:
            self.tabledata = data

        try:
            self.tm = MyTableModel(self.tabledata, header, self)
            # set the table model
            self.totalItems = self.tm.rowCount(self)
            self.tabela.setModel(self.tm)
            self.tabela.setColumnHidden(0, True)
            self.tabela.setColumnHidden(1, True)

        except Exception as e:
            return
        # # set row height
        nrows = len(self.tabledata)
        for row in range(nrows):
            self.tabela.setRowHeight(row, 25)

    def clickedslot(self, index):

        self.row = int(index.row())

        self.col = int(index.column())

        indice= self.tm.index(self.row, 0)
        self.current_id = indice.data()

        self.fill_data()

        self.apagarItem.setEnabled(True)

    def gravar_produto(self):
        from produtos import Produto

        cl = Produto(self)
        cl.limpar()
        cl.cod.setFocus()
        cl.cod.selectAll()
        cl.setModal(True)
        cl.show()

    def calcula_taxa_e_total(self):
        subtotal = decimal.Decimal(self.valor_subtotal.value())
        taxa = subtotal * decimal.Decimal(self.valortaxa)
        total = subtotal + taxa

        self.valor_iva.setValue(float(taxa))
        self.valor_documento.setValue(float(total))

    def getcodfornecedor(self, nomefornecedor):
        sql = """select cod from fornecedores WHERE nome= "{nome}" """.format(nome=nomefornecedor)

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        if len(data) > 0:

            self.codfornecedor = "".join(data[0])

        print(self.codfornecedor)

    def getcodproduto(self, nomeproduto):
        sql = """select cod, preco, custo from produtos WHERE nome= "{nome}" """.format(nome=nomeproduto)

        try:
            self.cur.execute(sql)
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]
        except Exception as e:
            QMessageBox.warning(self, "Erro", "Erro:{}".format(e))
            return

        if len(data) > 0:
            self.codproduto = "".join(data[0][0])
            self.custo_produto = decimal.Decimal(data[0][2])
            self.preco_actural = decimal.Decimal(data[0][1])
            self.preco.setValue(self.preco_actural)
            self.custo.setValue(self.custo_produto)
        else:
            self.codproduto = ""

    def getcodarmazem(self, nomearmazem):

        sql = """select cod from armazem WHERE nome= "{nome}" """.format(nome=nomearmazem)

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]
        if len(data) > 0:
            self.codarmazem = "".join(data[0])

    def habilitarfornecedor(self):
        self.gravar_fornecedor.setEnabled(True)
        self.desabilitarfornecedor()
        self.ativar_fornecedor.setEnabled(False)

    def desabilitarfornecedor(self):

        self.fornecedor.setEnabled(not self.fornecedor.isEnabled())
        self.numerodocumento.setEnabled(not self.numerodocumento.isEnabled())
        self.datadocumento.setEnabled(not self.datadocumento.isEnabled())
        self.valor_iva.setEnabled(not self.valor_iva.isEnabled())
        self.valor_documento.setEnabled(not self.valor_documento.isEnabled())
        self.valor_subtotal.setEnabled(not self.valor_subtotal.isEnabled())

    def validacao(self):

        if self.numerodocumento.text() == "":
            QMessageBox.information(self, "Erro de Documento", "Entre o número do documento")
            self.numerodocumento.setFocus()
            return False
        elif self.valor_documento.text() == "":
            self.valor_documento.setValue(decimal.Decimal(0))
            return True
        elif self.valor_iva.text() == "":
            self.valor_iva.setValue(decimal.Decimal(0))
            return True

        elif self.existe_fornecedor(self.codfornecedor) is False:
            QMessageBox.warning(self, "Erro", "Fornecedor não existe na Base de Dados. \n Grave primeiro.")
            self.gravar_fornecedores()
            return False

        else:
            return True

    def gravardoc(self):

        if self.validacao() is True:
            code = self.codigogeral
            fornecedor = self.codfornecedor
            numero = self.numerodocumento.text()
            data = self.datadocumento.date().toString('yyyy-MM-dd')
            subtotal = decimal.Decimal(self.valor_subtotal.value())
            iva = decimal.Decimal(self.valor_iva.value())
            total = decimal.Decimal(self.valor_documento.value())

            created = self.datadocumento.date().toString('yyyy-MM-dd')
            modified = QDate.currentDate().toString('yyyy-MM-dd')

            if self.parent() is not None:
                modified_by = self.parent().user
            else:
                modified_by = "User"
            if self.parent() is not None:
                created_by = self.parent().user
            else:
                created_by = "User"

            if self.existe(code) is True:

                sql = """UPDATE stock set fornecedor="{fornecedor}", numero="{numero}", data="{data}", total={total}, 
                taxa={iva}, subtotal={subtotal}, saldo={saldo}, modified="{modified}", modified_by="{modified_by}" WHERE cod="{cod}"
                """.format(cod=code, fornecedor=fornecedor, numero=numero, data=data, total=total, iva=iva,
                           subtotal=subtotal, modified=modified, modified_by=modified_by, saldo=total)
            else:

                values = """ "{cod}", "{fornecedor}", "{numero}", "{data}", {total}, {iva}, {subtotal}, {saldo},
                "{created}", "{modified}", "{modified_by}", "{created_by}" 
                """.format(cod=code, fornecedor=fornecedor, numero=numero, data=data, total=total, iva=iva,
                           subtotal=subtotal, created=created, modified=modified,
                           modified_by=modified_by, created_by=created_by, saldo=total)

                sql = "INSERT INTO stock (cod, fornecedor, numero, data, total, taxa, subtotal, saldo, created," \
                      " modified, modified_by, created_by) values({value})".format(value=values)

            try:
                self.cur.execute(sql)
                self.conn.commit()
            except Exception as e:
                QMessageBox.critical(self, "Erro", "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
                return

            self.ativar_fornecedor.setEnabled(True)
            self.gravar_fornecedor.setEnabled(False)
            self.desabilitarfornecedor()

    # Metodo que impede a duplicao de quantidades na tabela produtos
    # caso o stock tenha sido finalizado
    def normalizar_stock(self, codstock):
        sql = """SELECT codproduto, quantidade from stockdetalhe WHERE codstock="{}" """.format(codstock)
        self.cur.execute(sql)
        lista= self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        if len(data) > 0:
            for item in data:
                produtos_sql = """ UPDATE produtosdetalhe set quantidade=quantidade-{qty} 
                WHERE codproduto="{cod}" """.format(qty=item[1], cod=item[0])

                self.cur.execute(produtos_sql)
            try:
                sql = """UPDATE stock SET estado=0 WHERE cod="{}" """.format(codstock)
                self.cur.execute(sql)

                self.conn.commit()
            except Exception as e:
                print("Erro: ", e)
                self.conn.rollback()
                return False

            return True
        else:
            return False

    def existe_produto_detalhe(self, codproduto, codarmazem):
        sql =  """SELECT codproduto FROM produtosdetalhe WHERE codproduto="{}" AND codarmazem="{}" """.format(codproduto, codarmazem)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return True

        return False

    def finalizar_doc(self):

        created = self.datadocumento.date().toString('yyyy-MM-dd')
        modified = QDate.currentDate().toString('yyyy-MM-dd')

        if self.parent() is not None:
            modified_by = self.parent().user
        else:
            modified_by = "User"
        if self.parent() is not None:
            created_by = self.parent().user
        else:
            created_by = "User"

        codstock = self.cod.text()

        sql = """select quantidade, codproduto, codarmazem, custo, valor, validade from stockdetalhe WHERE codstock="{cod}"
        """.format(cod=codstock)
        self.cur.execute(sql)
        lista = self.cur.fetchall()
        stockdata = [tuple(str(item) for item in t) for t in lista]
        data = self.datadocumento.date().toString('yyyy-MM-dd')

        if len(stockdata) == 0:
            QMessageBox.warning(self, "Aviso", "Insira Items para poder gravar.")
            return

        for item in stockdata:
            produtos_sql = """UPDATE produtos SET custo={}, preco={} WHERE cod="{}" """.format(item[3], item[4],
                                                                                               item[1])
            self.cur.execute(produtos_sql)

            if self.existe_produto_detalhe(item[1], item[2]) is True:
                produtosdetalhe_sql = """ UPDATE produtosdetalhe set quantidade=quantidade+{qty}, validade="{validade}" 
                WHERE codproduto="{cod}" and codarmazem="{armazem}" """.format(qty=item[0],cod=item[1],
                                                                               armazem=item[2], validade=item[5])
            else:
                produtosdetalhe_sql = """INSERT INTO produtosdetalhe (codproduto, codarmazem, quantidade, created, modified, 
                modified_by, created_by, validade) VALUES ("{codproduto}", "{codarmazem}", {quantidade}, "{created}", "{modified}", 
                "{modified_by}", "{created_by}", "{validade}")""".format(codproduto=item[1], codarmazem=item[2],
                                                           quantidade=item[0], created=created, modified=modified,
                                                           modified_by=modified_by, created_by=created_by,
                                                           validade=item[5])

            print(sql)
            self.cur.execute(produtosdetalhe_sql)

        subtotal = decimal.Decimal(self.valor_subtotal.value())
        total = decimal.Decimal(self.valor_iva.value())
        valortaxa = decimal.Decimal(self.valor_documento.value())

        sql = """UPDATE stock SET data="{data}", estado=1, taxa={taxa}, subtotal={subtotal}, total={total} 
        WHERE cod = "{cod}" """.format(data=data, taxa=valortaxa, subtotal=subtotal, total=total, cod=codstock)

        try:
            self.cur.execute(sql)
            self.conn.commit()
            QMessageBox.information(self, "Informação", "Stock actualizado com sucesso!")
            self.close()
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Erro", "Erro na actualização de Stock.\n{}.".format(e))
            print("Erro ao finalizar", e)

    def gravardetalhes(self):

        if self.validacaodetalhes() is True:

            self.quantidade_produto = decimal.Decimal(self.quantidade.value())
            self.custo_produto = decimal.Decimal(self.custo.value())
            codstock = self.codigogeral
            codproduto = self.codproduto
            codarmazem = self.codarmazem
            quantidade = self.quantidade_produto
            validade = self.validade.date().toString("yyyy-MM-dd")
            valor = decimal.Decimal(self.preco.value())

            subtotal = quantidade * self.custo_produto
            total = subtotal

            if self.existeproduto(codproduto, self.cod.text()) is True:

                sql = """UPDATE stockdetalhe set codstock="{codstock}", codproduto="{codproduto}", 
                codarmazem="{codarmazem}", quantidade={quantidade}, validade="{validade}", valor={valor}, taxa={taxa}, 
                subtotal={subtotal}, total={total}, custo={custo} WHERE codstock="{codstock}" and 
                codproduto="{codproduto}" """.format(codstock=codstock, codproduto=codproduto, codarmazem=codarmazem,
                                                     quantidade=quantidade, validade=validade, valor=valor, taxa=0,
                                                     subtotal=subtotal, total=total, custo=self.custo_produto)
            else:

                values = """ "{codstock}", "{codproduto}", "{codarmazem}", {quantidade}, "{validade}", {valor}, {taxa}, 
                {subtotal}, {total}, {custo} """.format(codstock=codstock, codproduto=codproduto, codarmazem=codarmazem,
                                            quantidade=quantidade, validade=validade, valor=valor, taxa=0,
                                            subtotal=subtotal, total=total, custo=self.custo_produto)

                sql = "INSERT INTO stockdetalhe (codstock, codproduto, codarmazem, quantidade, validade, valor, " \
                      "taxa, subtotal, total, custo) values({value})".format(value=values)
            try:
                self.cur.execute(sql)
                self.conn.commit()

            except Exception as e:
                QMessageBox.critical(self, "Erro", "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
                return

            self.apagarItem.setEnabled(True)
            self.fill_table()

    def enche_fornecedor(self):
        self.fornecedor.clear()

        sql = "SELECT nome FROM fornecedores WHERE estado=1 ORDER BY nome"
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                self.fornecedor.addItems(item)

    def enche_produtos(self):

        print('Tentando encher produtos')

        self.produto.clear()

        sql = """SELECT nome FROM produtos WHERE nome like "%{criteria}%" or cod_barras="{criteria2}" or
        cod="{criteria2}" ORDER BY nome""".format(criteria=self.produto_lineedit.text(), criteria2=self.produto_lineedit.text())

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]
        if len(data) > 0:
            for item in data:
                self.produto.addItems(item)

    def enchearmazem(self):

        self.armazem.clear()

        sql = "SELECT nome FROM armazem"
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                self.armazem.addItems(item)

    def closeEvent(self, evt):
        parent = self.parent()
        if parent is not None:
            parent.fill_table()

    def fechar(self):
        self.close()

    def limpar(self):
        for child in (self.findChildren(QLineEdit) or self.findChildren(QTextEdit)):
            if child.objectName() not in ["cod", "cal1", "cal2"]: child.clear()

        # gera novo codigo para stock
        from utilities import codigo
        self.codigogeral = "ST" + codigo("ST" + "abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")
        self.cod.setText(self.codigogeral)

    def validacaodetalhes(self):

        sql = """SELECT * from stock WHERE cod = "{codigo}" """.format(codigo=str(self.cod.text()))
        try:
            self.cur.execute(sql)
            lista = self.cur.fetchall()
        except Exception as e:
            print(e)
            return

        data = [tuple(str(item) for item in t) for t in lista]

        if self.existe_produto(self.codproduto) is False or self.produto == "":
            QMessageBox.warning(self, "Erro", "Produto não existe na Base de Dados. \n Grave primeiro.")
            return False
        elif self.quantidade.value() == decimal.Decimal(0):
            QMessageBox.warning(self, "Erro de quantidade", "Quantidade deve ser maior que zero (0)")
            self.quantidade.setFocus()
            return False
        elif len(data) == 0:
            if QMessageBox.question(self, "Erro de Documento", "Detalhes do fornecedor ainda não foram gravados."
                                                            " \n Deseja Gravar agora?") == QMessageBox.Yes:
                self.gravardoc()
                return False

        elif self.existe_armazem(self.codarmazem) is False:
            QMessageBox.warning(self, "Erro", "Armazém não existe na Base de Dados. \n Grave primeiro.")
            self.gravar_armazem()
            return False

        else:
            return True

    def existe_produto(self, codproduto):

        sql = """SELECT cod FROM produtos WHERE cod="{}" """.format(codproduto)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return True
        else:
            return False

    def mostrar_registo(self, codigogeral):

        sql = """SELECT f.nome, s.numero, s.data, s.total, s.taxa, sd.codproduto,
        sd.codarmazem, sd.quantidade, sd.valor, s.subtotal  from stock s 
        LEFT JOIN fornecedores f ON f.cod = s.fornecedor 
        LEFT JOIN stockdetalhe sd ON s.cod=sd.codstock
        WHERE s.cod = "{codigo}" """.format(codigo=str(codigogeral))

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        if len(data) == 0:
            self.codigogeral = "ST" + cd("abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")
            self.cod.setText(self.codigogeral)
        else:
            self.fornecedor.setCurrentText(''.join(data[0][0]))
            self.numerodocumento.setText(''.join(data[0][1]))
            self.datadocumento.setDate(QDate.fromString(''.join(data[0][2])))
            self.valor_subtotal.setValue(decimal.Decimal(data[0][9]))
            self.valor_documento.setValue(decimal.Decimal(data[0][3]))
            self.valor_iva.setValue(decimal.Decimal(data[0][4]))

            self.fill_table()

    def fill_data(self):
        if self.current_id == "":
            return

        sql = """ SELECT produtos.cod, produtos.nome, armazem.nome, stockdetalhe.quantidade, 
        stockdetalhe.custo, stockdetalhe.valor from produtos INNER JOIN stockdetalhe ON produtos.cod=stockdetalhe.codproduto INNER JOIN
        armazem ON armazem.cod=stockdetalhe.codarmazem WHERE stockdetalhe.cod="{cod}" 
        """.format(cod=self.current_id)

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        if len(data) == 0:
            return

        self.codproduto = data[0][0]
        print(self.codproduto)
        self.produto.setCurrentText(''.join(data[0][1]))
        self.armazem.setCurrentText(''.join(data[0][2]))
        self.quantidade.setValue(decimal.Decimal(data[0][3]))
        self.custo.setValue(decimal.Decimal(data[0][4]))
        self.preco.setValue(decimal.Decimal(data[0][5]))

    def existe(self, codigo):

        sql = """SELECT cod from stock WHERE cod = "{codigo}" """.format(codigo=str(codigo))

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        if len(data) == 0:
            return False
        else:
            return True

    def existeproduto(self, codproduto, codstock):

        sql = """SELECT cod from stockdetalhe WHERE codstock="{codstock}" and codproduto = "{codproduto}"
         """.format(codstock=str(codstock), codproduto=codproduto)

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        if len(data) == 0:
            return False
        else:
            return True

    def gravar_taxa(self):
        try:
            cl = tx(self)
            cl.setModal(True)
            cl.show()
        except Exception as e:
            QMessageBox.warning(self, "Erro", "Erro {}".format(e))

    def gravar_Produto(self):
        try:
            cl = prod(self)
            cl.setModal(True)
            cl.show()
        except Exception as e:
            QMessageBox.warning(self, "Erro", "Erro {}".format(e))

    def gravar_armazem(self):
        try:
            cl = Armazem(self)
            cl.setModal(True)
            cl.show()
        except Exception as e:
            QMessageBox.warning(self, "Erro", "Erro {}".format(e))

    def gravar_fornecedores(self):
        try:
            cl = Fornecedor(self)
            cl.setModal(True)
            cl.show()
        except Exception as e:
            QMessageBox.warning(self, "Erro", "Erro {}".format(e))

    def existe_fornecedor(self, codfornecedor):
        sql =  """SELECT cod from fornecedores WHERE cod="{}" """.format(codfornecedor)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            return False
        else:
            return True

    def existe_armazem(self, codarmazem):
            sql =  """SELECT cod from armazem WHERE cod="{}" """.format(codarmazem)

            self.cur.execute(sql)
            data = self.cur.fetchall()

            if len(data) == 0:
                return False
            else:
                return True

    def connect_db(self):
        # Connect to database and retrieves data
        try:
            self.conn = lite.connect(DB_FILENAME)
            self.cur = self.conn.cursor()

        except Exception as e:
            QMessageBox.critical(self, "Erro ao conectar a Base de Dados",
                                 "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
            sys.exit(True)

    def removerow(self):

        if self.current_id == "":
            QMessageBox.information(self, "Info", "Selecione o registo a apagar na tabela")
            return

        sql = """delete from stockdetalhe WHERE cod = "{codigo}" """.format(codigo=str(self.current_id))
        self.cur.execute(sql)
        self.conn.commit()
        self.fill_table()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    helloPythonWidget = Cliente()
    helloPythonWidget.show()

    sys.exit(app.exec_())