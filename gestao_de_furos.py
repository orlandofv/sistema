# -*- coding: utf-8 -*-
"""
Created on Fri Mar 02 23:18:43 2012

@author: lims
"""
import sys
import datetime
import decimal
from time import gmtime, strftime
import glob, os
import subprocess

from PyQt5.QtWidgets import (QLineEdit, QToolBar, QMessageBox, qApp, QAction, QGroupBox, QPushButton,
                             QComboBox, QMainWindow, QSizePolicy, QHBoxLayout, QTableView, QCheckBox, QAbstractItemView,
                             QSplitter, QStatusBar, QGridLayout, QToolBox, QSplashScreen, QSizeGrip, QDateEdit,
                             QCalendarWidget, QStyleFactory, QLabel, QWidget, QVBoxLayout, QApplication, QTabWidget)

from PyQt5.QtCore import Qt, QDate, QTimer, QTime, QSize, QRegExp
from PyQt5.QtGui import QIcon, QFont, QPixmap, QRegExpValidator

import startpage
from sortmodel import MyTableModel
from utilities import codigo as cd
from pricespinbox import *

from lista_de_taxas import MainWindow as tx
from lista_de_documentos import MainWindow as docs
from lista_de_recibos import MainWindow as nao_pagas
import loginform as login
import recibos
from utilities import stylesheet
import lista_de_clientes as l_clientes
import lista_de_users as l_usuarios

data_hoje = strftime("%Y-%m-%d %H:%M:%S", gmtime())
today = datetime.date.today()
year = today.year
day = today.day
month = today.month

LOGGED = False
NOME_EMPRESA = ""

class Main(QMainWindow):

    # Configuracoes das Vendas
    fact_template = ""
    rec_template = ""
    req_template = ""
    criar_cliente = 1
    cliente_normal = 1
    saldo = 1
    cliente_inactivo = 0
    desconto_automatico = 0
    acima_do_credito = 1
    pos1 = ""
    pos2 = ""
    pos3 = ""
    pos4 = ""
    pos5 = ""
    so_vds = 0
    imposto_incluso = 1
    regime_normal = 0
    multi_taxas = 0
    q_abaixo_de_zero = 0
    cop1 = 1
    cop2 = 1
    cop3 = 1
    cop4 = 1
    cop5 = 1

    def __init__(self, parent=None):
        super(Main, self).__init__(parent)

        self.codigogeral = "FT" + cd("FT" + "abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")
        self.codcliente = "CL20181111111"
        self.codproduto = ""
        self.coddocumento = "DC20184444444"
        self.custoproduto = 0.00
        self.valortaxa = 0.00
        self.current_id = ""
        self.foto = ""
        self.preco_unitario = decimal.Decimal(0.00)
        self.quantidade_unitario = 0.00
        self.alterar_quantidade = False
        self.alteracao_de_preco = False
        self.quantidade_existente = 0.00
        self.tipo_produto = 0

        self.conn = ""
        self.database = ""
        self.cur = ""
        self.user = "user"
        self.admin = False
        self.gestor = False
        self.empresa = "Empresa Teste"
        self.custos = 0
        self.preco = 0
        self.user = ""
        self.empresa_cabecalho = ""
        self.empresa_logo = ""
        self.empresa_slogan = ""
        self.empresa_endereco = ""
        self.empresa_contactos = ""
        self.empresa_email = ""
        self.empresa_web = ""
        self.empresa_nuit = ""
        self.empresa_casas_decimais = 0
        self.caixa_numero = ""
        self.licenca = ""
        self.contas = ""
        self.incluir_iva = 1
        self.codarmazem = ""
        self.nome_armazem = ""
        self.DADOS_DA_EMPRESA = []

        login.MODULO = "facturacao"
        self.setHidden(True)
        self.Login = login.Login(self)
        # self.Login.encheempresas()
        # self.Login.setModal(True)
        self.Login.show()

    def trancar_sistema(self):
        self.Login.armazem.setEnabled(False)
        self.Login.empresas.setEnabled(False)
        self.Login.password.clear()
        self.Login.show()

    def ui(self):

        self.setWindowFlags(Qt.FramelessWindowHint)
        sizegrip = QSizeGrip(self)

        mainlayout = QVBoxLayout()

        boldFont2 = QFont('Consolas', 12)
        boldFont2.setBold(True)

        produtowidget = QWidget()
        self.user_Label = QLabel()
        #self.armazem = QLabel("Armazém: {}".format(self.nome_armazem))
        # self.armazem.setFont(boldFont2)
        self.user_Label.setFont(boldFont2)
        self.data = QLabel()
        self.data.setFont(boldFont2)

        provlayout = QVBoxLayout()
        provlayout.addWidget(self.user_Label)
        provlayout.addWidget(self.data)

        produtowidget.setLayout(provlayout)

        valorlayout = QHBoxLayout()

        headerlayout = QHBoxLayout()
        headerlayout.addWidget(produtowidget)
        headerlayout.addLayout(valorlayout)

        # Layout de Produtos, Normalmente deve ser flowlayout
        self.combo_produtoslayout = QHBoxLayout()

        #Layout da Familia de produtos, estara por cima de todos
        self.familialayout = QHBoxLayout()

        # Layout de Subfalilias a esquerda e Produtos a direita
        self.subfamilialayout = QVBoxLayout()
        subbuttonslayout = QHBoxLayout()
        subbuttonslayout.addLayout(self.subfamilialayout)
        subbuttonslayout.addLayout(self.combo_produtoslayout)

        buttonslayout = QVBoxLayout()
        buttonslayout.addLayout(self.familialayout)
        buttonslayout.addLayout(subbuttonslayout)

        headerWidget = QGroupBox()
        headerWidget.setMaximumHeight(120)

        headerWidget.setLayout(headerlayout)

        tabulador = QTabWidget()
        tabulador.setTabPosition(2)
        self.start = startpage.startPage(self)
        clientes = l_clientes.MainWindow(self)
        usuario = l_usuarios.MainWindow(self)
        facturas = nao_pagas(self)
        taxas = tx(self)
        documentos = docs(self)

        tabulador.addTab(self.start, "Bem Vindo")
        tabulador.addTab(clientes, "Clientes")
        tabulador.addTab(usuario, "Usuários")
        tabulador.addTab(facturas, "Dívidas")
        tabulador.addTab(taxas, "Taxas")
        tabulador.addTab(documentos, "Documentos")

        mainlayout.addWidget(headerWidget)
        mainlayout.addWidget(tabulador)
        mainlayout.addWidget(sizegrip, 0, Qt.AlignBottom | Qt.AlignRight)
        #mainlayout.addWidget(self.tool)

        centralwidget = QWidget()
        centralwidget.setLayout(mainlayout)
        self.setCentralWidget(centralwidget)

        self.setWindowTitle("Microgest Facturação - {}".format(self.empresa))

        timer = QTimer(self)
        timer.timeout.connect(self.horas)
        timer.start(1000)

        self.setWindowIcon(QIcon("logo.ico"))
        # self.setStyleSheet("QMainWindow, QDialog {background: #A8F2ED} QPushButton {background: #A8F2ED} QPushButton:hover {background: rgb(30, 30, 30)}")

    def set_max_normal(self):
        if self.isMaximized():
            self.butao_restaurar.setIcon(QIcon("./images/icons8-maximize-window-50.png"))
            self.showNormal()
        else:
            self.butao_restaurar.setIcon(QIcon("./images/icons8-restore-window-50.png"))
            self.showMaximized()

    def mudar_estilo(self, estilo):
        QApplication.setStyle(QStyleFactory.create(estilo))

    def config(self):
        from empresa import Empresa

        e = Empresa(self)
        e.setModal(True)
        e.show()

    def accoes(self):

        self.combo_estilo = QComboBox()
        self.combo_estilo.addItems(QStyleFactory.keys())
        self.combo_estilo.activated[str].connect(self.mudar_estilo)
        configuracoes = QAction(QIcon("./icons/cofiguracao.ico"), "Configurações", self)
        configuracoes.triggered.connect(self.config)

        darkblue = QAction("DB", self)
        darkgreen = QAction("DG", self)
        darkorange = QAction("DO", self)
        lightblue = QAction("LB", self)
        lightgreen = QAction("LG", self)
        lightorange = QAction("LO", self)
        dark_style = QAction("DA", self)
        normal = QAction("NO", self)

        darkblue.triggered.connect(lambda: self.setStyleSheet(stylesheet(1)))
        darkgreen.triggered.connect(lambda: self.setStyleSheet(stylesheet(2)))
        darkorange.triggered.connect(lambda: self.setStyleSheet(stylesheet(3)))
        lightblue.triggered.connect(lambda: self.setStyleSheet(stylesheet(4)))
        lightgreen.triggered.connect(lambda: self.setStyleSheet(stylesheet(5)))
        lightorange.triggered.connect(lambda: self.setStyleSheet(stylesheet(6)))
        dark_style.triggered.connect(lambda: self.setStyleSheet(stylesheet(7)))

        normal.triggered.connect(lambda: self.setStyleSheet(""))

        maintool = QToolBar()
        maintool.setContextMenuPolicy(Qt.PreventContextMenu)
        maintool.setMaximumHeight(32)
        maintool.setIconSize(QSize(32, 32))
        maintool.setMovable(False)

        butao_minimizar = QAction(QIcon("./icons/icons8-minimize-window-50.png"), "Minimizar", self)
        self.butao_restaurar = QAction(QIcon("./icons/icons8-restore-window-50.png"), "Restaurar/Maximizar", self)
        self.butao_restaurar.triggered.connect(self.set_max_normal)
        # self.butao_restaurar.setVisible(False)
        butao_fechar = QAction(QIcon("./icons/icons8-close-window-50.png"), "Fechar", self)
        butao_minimizar.triggered.connect(self.showMinimized)
        butao_fechar.triggered.connect(sys.exit)

        spacer1 = QWidget()
        spacer1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        maintool.addWidget(QLabel("Microgest POS - [{}]".format(self.empresa)))
        maintool.addWidget(spacer1)

        maintool.addWidget(self.combo_estilo)
        maintool.addAction(darkblue)
        maintool.addAction(darkgreen)
        maintool.addAction(darkorange)
        maintool.addAction(lightblue)
        maintool.addAction(lightgreen)
        maintool.addAction(lightorange)
        maintool.addAction(dark_style)
        maintool.addAction(normal)
        maintool.addAction(butao_minimizar)
        maintool.addAction(self.butao_restaurar)
        maintool.addAction(butao_fechar)
        self.tool = QToolBar("Acções")

        self.tool.setContextMenuPolicy(Qt.PreventContextMenu)
        self.tool.setIconSize(QSize(48, 48))
        self.tool.setFixedHeight(48)
        self.tool.setMovable(False)

        gravar = QAction(QIcon("./icons/Dollar.ico"), "&Finalizar documento", self)
        recibo = QAction(QIcon("./icons/Properties.ico"), "C&riar Recibo", self)
        self.aprovar_requisicao = QAction(QIcon("./icons/familias.ico"), "Aprovar Requisição", self)
        gravardoc = QAction(QIcon("./icons/Dario-Arnaez-Genesis-3G-User-Files.ico"), "&Gravar Documento", self)
        abrirdoc = QAction(QIcon("./icons/open.ico"), "&Abrir Documento Gravado", self)
        segundavia = QAction(QIcon("./icons/stock.ico"), "&Segunda Via/ Cancelamento de Documentos", self)
        caixa = QAction(QIcon("./icons/report.ico"), "&Fechar/Imprimir Caixa", self)
        facturas_nao_pagas = QAction(QIcon("./icons/coin_stacks_copper_remove.ico"), "V&er Facturas não pagas", self)
        trancar_sistema = QAction(QIcon("./icons/Logout.ico"), "&Trancar sistema", self)

        self.tool.addAction(gravar)
        self.tool.addAction(recibo)
        self.tool.addAction(self.aprovar_requisicao)
        # self.tool.addSeparator()
        self.tool.addAction(gravardoc)
        self.tool.addAction(abrirdoc)
        # self.tool.addSeparator()
        self.tool.addAction(segundavia)
        # self.tool.addSeparator()
        self.tool.addAction(caixa)
        # self.tool.addSeparator()
        self.tool.addAction(facturas_nao_pagas)
        # self.tool.addSeparator()
        self.tool.addAction(trancar_sistema)

        self.cashdrawer_button = QAction(QIcon("./icons/payment.ico"), "&Abrir Gaveta", self)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tool.addWidget(spacer)

        self.tool.addAction(configuracoes)

        self.addToolBar(Qt.TopToolBarArea, maintool)
        self.addToolBarBreak()
        self.addToolBar(Qt.TopToolBarArea, self.tool)

    def horas(self):
        self.data.setText("{}  {} ".format(QDate.currentDate().toString("dd-MM-yyyy"),
                                                          QTime.currentTime().toString()))

    def enterEvent(self, evt):

        print('Fazendo refresh da connexao:')
        # self.conn.cmd_refresh(1)
        # self.tabela_produtos.fill_table()

        if len(self.DADOS_DA_EMPRESA) > 0:

            self.user = self.DADOS_DA_EMPRESA[0]

            self.user_Label.setText('Bem Vindo, {} '.format(self.user))
            self.start.user = self.user
            self.start.ui()
            self.empresa = self.DADOS_DA_EMPRESA[2]
            self.empresa_cabecalho = self.DADOS_DA_EMPRESA[3]
            self.empresa_logo = self.DADOS_DA_EMPRESA[4]
            self.empresa_slogan = self.DADOS_DA_EMPRESA[5]
            self.empresa_endereco = self.DADOS_DA_EMPRESA[6]
            self.empresa_contactos = self.DADOS_DA_EMPRESA[7]
            self.empresa_email = self.DADOS_DA_EMPRESA[8]
            self.empresa_web = self.DADOS_DA_EMPRESA[9]
            self.empresa_nuit = self.DADOS_DA_EMPRESA[10]
            self.empresa_casas_decimais = self.DADOS_DA_EMPRESA[11]
            self.licenca = self.DADOS_DA_EMPRESA[12]
            self.contas = self.DADOS_DA_EMPRESA[13]
            self.custos = self.DADOS_DA_EMPRESA[14]
            self.preco = self.DADOS_DA_EMPRESA[15]

        # self.getcodcliente()
        # self.getcoddocumento()
        # self.getcodproduto()
        # verifica se existe uma caixa aberta
        # self.verifica_caixa()
        # self.verifica_admin()

    def verifica_admin(self):

        if self.imposto_incluso == 1:
            self.taxa.setChecked(False)
        else:
            self.taxa.setChecked(True)

        self.desconto.setEnabled(self.admin)
        self.combo_taxa.setEnabled(self.admin)
        self.taxabutton.setEnabled(self.admin)
        self.taxabutton.setEnabled(self.admin)
        self.taxa.setEnabled(self.admin)
        self.combo_preco.setEnabled(self.admin)

        if self.gestor == 1 or self.admin ==1:
            self.aprovar_requisicao.setEnabled(1)

    def mousePressEvent(self, event):
        self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.isMaximized():
            return

        x = event.globalX()
        y = event.globalY()
        x_w = self.offset.x()
        y_w = self.offset.y()
        self.move(x - x_w, y - y_w)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    pixmap = QPixmap("./icons/black.png")
    splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)
    # splash.setMask(pixmap.mask())  # this is usefull if the splashscreen is

    splash.showFullScreen()
    splash.showMessage(u'Starting...', Qt.AlignRight | Qt.AlignBottom, Qt.yellow)

    # make sure Qt really display the splash screen
    app.processEvents()

    # start tha main app window ainwindow = ...
    # ...

    main_facturacao = Main()
    main_facturacao.showMaximized()

    # now kill the spmain_facturacaolashscreen
    splash.finish(main_facturacao)

    sys.exit(app.exec_())