# -*- coding: utf-8 -*-
"""
Created on Fri Mar 02 23:18:43 2012

@author: lims
"""
import decimal
import os
import glob
import sys

from PyQt5.QtWidgets import  (QLabel, QLineEdit,QVBoxLayout, QToolBar, QMessageBox, QSizePolicy,
    QTextEdit, QAction, QApplication, QGroupBox, QPushButton, QDateEdit, QCalendarWidget,
    QHBoxLayout, QWidget, QTableView, QSplashScreen, QAbstractItemView, QSplitter, QMainWindow,
    QGridLayout, QButtonGroup, QComboBox, QStyleFactory, QFrame, QScrollArea, QCommandLinkButton)

from PyQt5.QtCore import QSettings
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

from PyQt5.QtCore import Qt, QDate,  QTimer, QDateTime, QSizeF
from PyQt5.QtGui import QIcon, QFont, QPixmap, QTextDocument

from GUI.RibbonButton import RibbonButton
from GUI.RibbonWidget import *

from sortmodel import MyTableModel

from utilities import codigo as cd
from utilities import stylesheet
from editar_quantidade import EditarValores

from flowlayout import FlowLayout
import sqlite3 as lite

import loginform_vendas as login
from novo_produto import NovoProduto

from utilities import ANO_ACTUAL, DATA_ACTUAL, MES, HORA

DB_FILENAME = "dados.tsdb"

STYLESHEET = """
QMainWindow, QDockWidget, QTabWidget, QDialog, QCommandLinkButton#sair, QTabWidget::title{
border: none;
border-radius: 0px;
padding: 0 8px;
background: #FFFFFF;
}

QToolBar{
border: none;
background: #3a7999;
}

QPushButton, QCommandLinkButton
{
	border: none;
	background: #3a7999;
	color: #f2f2f2;
	border-radius: 2px;
	position: relative;
    padding: 2px;	 
}

QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox{
    border: 1px solid #3a7999;
    border-radius: 0px;
}

QPushButton:hover 
{
	border: none;
	background: #298DC5;
	color: green;
	padding: 10px;
	border-radius: 2px;
	position: relative; 
}

QCommandLinkButton:hover 
{
	border: none;
	background: #298DC5;
	color: green;
	padding: 10px;
	border-radius: 2px;
	position: relative; 
}

QCommandLinkButton:selected 
{
	border: none;
	background: #298DC5;
	color: green;
	padding: 10px;
	border-radius: 2px;
	position: relative; 
}

QTableView {
    color: #4d4e51;
    border: 1px solid #6d6e71;
    gridline-color: #9a9b9e;
    background-color: #bdc1c9;
    selection-color: #4d4e51;
    selection-background-color: #adc5ed;
    border-radius: 0px;
    padding: 0px;
    margin: 0px;
}

QTableView::item:hover  {
    background: #abb0b7;
}

QTableView::item:disabled  {
    color: #85878a;
}

QTableView::item:selected  {
    color: #1b3774;
    background-color: #7cabf9;
}

/* when editing a cell: */
QTableView QLineEdit {
    color: #4d4e51;
    background-color: #b3b8bf;
    border-radius: 0px;
    margin: 0px;
    padding: 0px;
}

QHeaderView {
    border: none;
    background-color: #4d4e51;
    border-top-left-radius: 3px;
    border-top-right-radius: 3px;
    border-bottom-left-radius: 0px;
    border-bottom-right-radius: 0px;
    margin: 0px;
    padding: 0px;
}

QHeaderView::section  {
    background-color: transparent;
    color: #c7c7c9;
    border: 1px solid transparent;
    border-radius: 0px;
    text-align: center;
}

QHeaderView::section::vertical  {
    padding: 0px 6px 0px 6px;
    border-bottom: 1px solid #6d6e71;
}

QHeaderView::section::vertical:first {
    border-top: 1px solid  #6d6e71;
}

QHeaderView::section::vertical:last {
    border-bottom: none;
}

QHeaderView::section::vertical:only-one {
    border: none;
}

QHeaderView::section::horizontal  {
    padding: 0px 0px 0px 6px;
    border-right: 1px solid #6d6e71;
}

QHeaderView::section::horizontal:first {
    border-left: 1px solid #6d6e71;
}

QHeaderView::section::horizontal:last {
    border-left: none;
}

QHeaderView::section::horizontal:only-one {
    border: none;
}

QDockWidget QHeaderView::section {
    border-width: 6px 1px 6px 1px; /* hack to bigger margin for Model Panel table headers */
}

QHeaderView::section:checked {
    color: #1b3774;
    background-color: #7cabf9;
}

 /* style the sort indicator */
QHeaderView::down-arrow {
    image: url(./Styles/images/down_arrow_light.png);
}

QHeaderView::up-arrow {
    image: url(./Styles/images/up_arrow_light.png);
}

QTableCornerButton::section {
    background-color: #4d4e51;
    border: 1px solid #4d4e51;
    border-radius: 0px;
}

QTabWidget{
    border: none;
}

QTabWidget:focus {
    border: none;
}

QTabWidget::pane {
    border: none;
    padding: 0px;
    background-color: #85878a;
    position: absolute;
    top: -15px;
    padding-top: 15px;
}

QTabWidget::tab-bar {
    alignment: center;
}

QTabBar {
    qproperty-drawBase: 0;
    left: 2px;
    background-color: transparent;
}

QTabBar:focus {
    border: 0px transparent black;
}

QTabBar::close-button {
    padding: 0px;
    margin: 0px;
    border-radius: 2px;
    background-image: url(./Styles/images/close_dark.png);
    background-position: center center;
    background-repeat: none;
}

QTabBar::close-button:hover {
    background-color: #7cabf9;
}

QTabBar::close-button:pressed {
    background-color: #adc5ed;
}

QTabBar::scroller { /* the width of the scroll buttons */
    width: 20px;
}

/* the scroll buttons are tool buttons */
QTabBar QToolButton,
QTabBar QToolButton:hover { 
    margin-top: 4px;
    margin-bottom: 4px;
    margin-left: 0px;
    margin-right: 0px;
    padding: 0px;
    border: none;
    background-color: #85878a;
    border-radius: 0px;
}

QTabBar QToolButton::right-arrow:enabled {
     image: url(./Styles/images/right_arrow_light.png);
}

QTabBar QToolButton::right-arrow:disabled,
QTabBar QToolButton::right-arrow:off {
     image: url(./Styles/images/right_arrow_disabled_dark.png);
}

QTabBar QToolButton::right-arrow:hover {
     image: url(./Styles/images/right_arrow_lighter.png);
}

 QTabBar QToolButton::left-arrow:enabled {
     image: url(./Styles/images/left_arrow_light.png);
}

 QTabBar QToolButton::left-arrow:disabled,
 QTabBar QToolButton::left-arrow:off {
     image: url(./Styles/images/left_arrow_disabled_dark.png);
}

 QTabBar QToolButton::left-arrow:hover {
     image: url(./Styles/images/left_arrow_lighter.png);
}

 QTabBar QToolButton::up-arrow:enabled {
     image: url(./Styles/images/up_arrow_light.png);
}

 QTabBar QToolButton::up-arrow:disabled,
 QTabBar QToolButton::up-arrow:off {
     image: url(./Styles/images/up_arrow_disabled_dark.png);
}

 QTabBar QToolButton::up-arrow:hover {
     image: url(./Styles/images/up_arrow_lighter.png);
}

 QTabBar QToolButton::down-arrow:enabled {
     image: url(./Styles/images/down_arrow_light.png);
}

 QTabBar QToolButton::down-arrow:disabled,
 QTabBar QToolButton::down-arrow:off {
     image: url(./Styles/images/down_arrow_disabled_dark.png);
}

 QTabBar QToolButton::down-arrow:hover {
     image: url(./Styles/images/down_arrow_lighter.png);
}

/* TOP and BOTTOM TABS */
QTabBar::tab:top,
QTabBar::tab:bottom {
    color: #c7c7c9;
    border: 1px solid #6d6e71;
    border-left-color: #85878a;
    border-right-width: 0px;
    background-color: #6d6e71;
    padding:2px 15px;
    margin-top: 4px;
    margin-bottom: 4px;
    position: center;
}

QTabBar::tab:top:first,
QTabBar::tab:bottom:first {
    border-top-left-radius: 0px;
    border-bottom-left-radius: 0px;
}

QTabBar::tab:top:last,
QTabBar::tab:bottom:last {
    border-top-right-radius: 0px;
    border-bottom-right-radius: 0px;
    border-right-width: 1px;
}

QTabBar::tab:top:selected,
QTabBar::tab:bottom:selected {
    color: white;
    background-color: #5e90fa;
    border-color: #3874f2;
}

QTabBar::tab:top:!selected:hover,
QTabBar::tab:bottom:!selected:hover {
    color: white;
}

QTabBar::tab:top:only-one ,
QTabBar::tab:bottom:only-one {
    border: 1px solid #1b3774;
    border-radius: 6px;
}

/* LEFT and RIGHT TABS */
QTabBar::tab:left,
QTabBar::tab:right {
    color: #c7c7c9;
    border: 1px solid #6d6e71;
    border-top-color: #85878a;
    border-bottom-width: 0px;
    background-color: #6d6e71;
    padding: 15px 2px;
    margin-left: 4px;
    margin-right: 4px;
    position: center;
}

QTabBar::tab:left:first,
QTabBar::tab:right:first {
    border-top-left-radius: 0px;
    border-top-right-radius: 0px;
}

QTabBar::tab:left:last,
QTabBar::tab:right:last {
    border-bottom-left-radius: 0px;
    border-bottom-right-radius: 0px;
    border-bottom-width: 1px;
}

QTabBar::tab:left:selected,
QTabBar::tab:right:selected {
    color: white;
    background-color: qlineargradient(spread:pad, x1:0.545, y1:1, x2:0, y2:1, stop:0 #3874f2, stop:1 #5e90fa);
    border-color: #3874f2;
}

QTabBar::tab:left:!selected:hover,
QTabBar::tab:right:!selected:hover {
    color: white;
}

QTabBar::tab:left:only-one ,
QTabBar::tab:right:only-one {
    border: 1px solid #1b3774;
    border-radius: 6px;
}
"""
APPLICATION_NAME = "Microgest POS"
APPLICATION_VERSION = "1.0.2020"
ORGANIZATION_DOMAIN = "www.microgest.com"
ORGANIZATION_NAME = "Microgest Lda"


class Vendas(QMainWindow):

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
    favorito = 0
    promocao = 0
    mais_vendidos = 0

    def __init__(self, parent=None):
        super(Vendas, self).__init__(parent)

        timer = QTimer(self)
        timer.timeout.connect(self.horas)
        timer.start(1000)

        self.trancar_automaticamente = 0

        estilo = QStyleFactory.create("Fusion")
        # estilo = QStyle(styles)
        QApplication.setStyle(estilo)

        self.totalItems = 0

        self.subfamilia_first_time = True
        self.produtos_first_time = True
        self.familia_first_time = True

        # Esses parametros facilitam a navegacao na Base de dados
        self.familia_offset = 0
        self.subfamilia_offset = 0
        self.produtos_offset = 0

        self.familia_len = 0
        self.subfamilia_len = 0
        self.produtos_len = 0

        self.grupo_clicado = 1

        self.tabela_row = 0
        self.cod_facturacaodetalhe = None

        self.codigogeral = "FT" + cd("FT" + "abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")
        self.codcliente = "CL20181111111"
        self.codproduto = ""
        self.nome_produto = ""
        self.coddocumento = "DC20184444444"
        self.custoproduto = decimal.Decimal(0.00)
        self.valortaxa = decimal.Decimal(0.00)
        self.current_id = ""
        self.foto = ""
        self.preco_unitario = decimal.Decimal(0.00)
        self.quantidade_unitario = decimal.Decimal(1.00)
        self.alterar_quantidade = False
        self.alterar_de_preco = False
        self.quantidade_existente = decimal.Decimal(0.00)
        self.tipo_produto = 0

        self.conn = ""
        self.database = ""
        self.cur = ""
        self.user = "user"
        self.admin = False
        self.gestor = False
        self.empresa = "Empresa Teste"

        self.empresa_cabecalho = ""
        self.empresa_logo = ""
        self.empresa_slogan = ""
        self.empresa_endereco = ""
        self.empresa_contactos = ""
        self.empresa_email = ""
        self.empresa_web = ""
        self.empresa_nuit = ""
        self.empresa_casas_decimais = ""
        self.caixa_numero = ""
        self.licenca = ""
        self.contas = ""
        self.incluir_iva = 1
        self.codarmazem = ""
        self.nome_armazem = ""
        self.DADOS_DA_EMPRESA = []

        if self.parent() is None:
            self.setStyleSheet(STYLESHEET)

            login.MODULO = "facturacao"
            self.Login = login.Login(self)
            self.Login.encheempresas()
            self.Login.setModal(True)
            self.setHidden(True)
            self.Login.showFullScreen()
        else:
            self.conn = self.parent().conn
            self.cur = self.parent().cur
            self.ui()

    def horas(self):
        # self.data.setText("{}  {} | Documento: {}".format(QDate.currentDate().toString("dd-MM-yyyy"),
        #                                                   QTime.currentTime().toString(), self.codigogeral))

        self.trancar_automaticamente += 1
        # print("Trancar: ", self.trancar_automaticamente)
        # if self.trancar_automaticamente == 60:
        #     self.trancarsistema()

    def mouseDoubleClickEvent(self, *args, **kwargs):
        print("Mouse Click")
        self.trancar_automaticamente = 0

    def mouseMoveEvent(self, evt):
        print("Mouse Move")
        self.trancar_automaticamente = 0

    def load_settings(self):
        from config import Config

        settings = Config(self)
        self.caminho_python = settings.python
        self.pos1 = settings.pos1
        self.pos2 = settings.pos2
        self.copias_pos1 = settings.copias_pos1
        self.copias_pos2 = settings.copias_pos2
        self.impressora1 = settings.impressora1
        self.impressora2 = settings.impressora2
        self.numero_mesas = settings.mesas
        self.papel_1 = int(settings.papel_1.replace("mm", ""))
        self.papel_2 = int(settings.papel_2.replace("mm", ""))

    def ui(self):

        self.label_total = QLabel("0.00")

        taxa = QLabel("Taxa")
        taxa.setAlignment(Qt.AlignRight)
        desconto = QLabel("Desconto")
        desconto.setAlignment(Qt.AlignRight)
        subtotal = QLabel("Subtotal")
        subtotal.setAlignment(Qt.AlignRight)

        self.labeltaxa = QLabel("0.00")
        self.labeltaxa.setAlignment(Qt.AlignRight)
        self.labeldesconto = QLabel("0.00")
        self.labeldesconto.setAlignment(Qt.AlignRight)
        self.labelsubtotal = QLabel("0.00")
        self.labelsubtotal.setAlignment(Qt.AlignRight)

        boldFont2 = QFont('Consolas', 12)
        boldFont2.setBold(True)

        self.user_Label = QLabel('')
        self.user_Label.setFont(boldFont2)

        self.sem_registo_label = QLabel("Sem Registo")

        self.label_total.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        boldFont = QFont('Consolas', 24)
        boldFont.setBold(True)
        self.label_total.setFont(boldFont)

        self.validade = QDateEdit(self)
        # self.validade.setDisplayFormat('yyyy-MM-dd')

        self.validade.setDate(QDate.currentDate())
        cal = QCalendarWidget()
        self.validade.setCalendarPopup(True)
        self.validade.setCalendarWidget(cal)

        self.tabela = QTableView(self)
        self.tabela.clicked.connect(self.clickedslot)
        self.tabela.setAlternatingRowColors(True)

        # hide grid
        self.tabela.setShowGrid(False)

        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)

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

        self.cod_line = QLineEdit()
        self.cod_line.setMaxLength(255)
        self.cod_line.setFocus()
        self.cod_line.setMinimumHeight(25)
        self.cod_line.setPlaceholderText('Código de Barras/Codigo do Produto ')

        boldFont = QFont('Consolas', 14)
        boldFont.setBold(True)

        self.cod_line.setFont(boldFont)

        # Widget Pricipal dos Botoes Familia, Subfamilia e Produtos
        controlswidget = QWidget()

        # Splitter Horizontal que divide a tabela dos botoes
        splitter = QSplitter(Qt.Horizontal)
        familiagrupo = QGroupBox("Categorias")
        familiagrupo.setFixedHeight(70)
        subfamiliagrupo = QGroupBox("Grupos")
        subfamiliagrupo.setFixedWidth(150)
        produtosgrupo = QGroupBox("Produtos")

        # Layout da Familia de produtos, estara por cima de todos
        familia_layout =  QHBoxLayout()
        familia_layout.setContentsMargins(0, 0, 0, 0)
        familia_layout.setStretch(1, 1)
        familia_layout.setSpacing(0)

        self.familia_layout = QHBoxLayout()
        self.familia_layout.setContentsMargins(5, 0, 5, 0)
        self.familia_layout.setStretch(1, 1)
        self.familia_layout.setSpacing(1)

        self.familia_button_w = QWidget()
        familia_scroll = QScrollArea()
        familia_scroll.setWidget(self.familia_button_w)
        familia_scroll.setWidgetResizable(True)

        self.familia_button_w.setLayout(self.familia_layout)
        #
        # familia_btn_previous = QPushButton(QIcon("./icons/previous.ico"), "")
        # familia_btn_previous.setFixedSize(80, 40)
        # familia_btn_previous.clicked.connect(self.familia_previous)

        # familia_btn_next = QPushButton(QIcon("./icons/next.ico"), "")
        # familia_btn_next.setFixedSize(80, 40)
        # familia_btn_next.clicked.connect(self.familia_next)

        # familia_layout.addWidget(familia_btn_previous)
        familia_layout.addWidget(familia_scroll)
        # familia_layout.addWidget(familia_btn_next)

        familiagrupo.setLayout(familia_layout)

        # Layout de Subfalilias a esquerda e Produtos a direita
        subfamilia_layout = QVBoxLayout()
        subfamilia_layout.setSpacing(0)

        self.subfamilia_button_w = QWidget()
        subfamilia_scroll = QScrollArea()
        subfamilia_scroll.setWidget(self.subfamilia_button_w)
        subfamilia_scroll.setWidgetResizable(True)

        subfamilia_layout.addWidget(subfamilia_scroll)

        self.subfamilia_layout = QVBoxLayout()
        self.subfamilia_layout.setContentsMargins(0, 0, 0, 0)
        subfamiliagrupo.setLayout(subfamilia_layout)

        # Layout de Produtos, Normalmente deve ser flowlayout
        produtos_layout = QVBoxLayout()

        # navigation_btn_first = QPushButton(QIcon("./icons/first.ico"), "")
        # navigation_btn_first.setFixedSize(80, 40)
        # navigation_btn_first.clicked.connect(self.navigation_first)
        #
        # navigation_btn_previous = QPushButton(QIcon("./icons/previous.ico"), "")
        # navigation_btn_previous.setFixedSize(80, 40)
        # navigation_btn_previous.clicked.connect(self.navigation_previous)
        #
        # navigation_btn_next = QPushButton(QIcon("./icons/next.ico"), "")
        # navigation_btn_next.setFixedSize(80, 40)
        # navigation_btn_next.clicked.connect(self.navigation_next)
        #
        # navigation_btn_last = QPushButton(QIcon("./icons/last.ico"), "")
        # navigation_btn_last.setFixedSize(80, 40)
        # navigation_btn_last.clicked.connect(self.navigation_last)

        self.navigation_btn_todos = QPushButton(QIcon("./icons/todos.ico"), "TODOS")
        self.navigation_btn_todos.setCheckable(True)
        self.navigation_btn_todos.setFixedHeight(40)
        self.navigation_btn_todos.clicked.connect(self.mostrar_todos)

        self.navigation_btn_favorito = QPushButton(QIcon("./icons/favorito.ico"), "FAVORITOS")
        self.navigation_btn_favorito.setCheckable(True)
        self.navigation_btn_favorito.setFixedHeight(40)
        self.navigation_btn_favorito.clicked.connect(self.mostrar_favorito)

        self.navigation_btn_promocao = QPushButton(QIcon("./icons/promocao.ico"), "EM PROMOÇÃO")
        self.navigation_btn_promocao.setCheckable(True)
        self.navigation_btn_promocao.setFixedHeight(40)
        self.navigation_btn_promocao.clicked.connect(self.mostrar_promocao)

        self.navigation_btn_mais_saida = QPushButton(QIcon("./icons/mais_saida.ico"), "COM + SAIDA")
        self.navigation_btn_mais_saida.setCheckable(True)
        self.navigation_btn_mais_saida.setFixedHeight(40)
        self.navigation_btn_mais_saida.clicked.connect(self.mostrar_maisvendidos)

        self.produtos_button_w = QWidget()
        produtos_scroll = QScrollArea()
        produtos_scroll.setWidget(self.produtos_button_w)
        produtos_scroll.setWidgetResizable(True)

        self.produtos_layout = FlowLayout()
        self.produtos_layout.setContentsMargins(0, 0, 0, 0)

        self.produtos_button_w.setLayout(self.produtos_layout)

        produtos_nav_lay = QHBoxLayout()
        produtos_nav_lay.setSpacing(1)
        # produtos_nav_lay.addWidget(navigation_btn_first)
        # produtos_nav_lay.addWidget(navigation_btn_previous)
        # produtos_nav_lay.addWidget(navigation_btn_next)
        # produtos_nav_lay.addWidget(navigation_btn_last)
        produtos_nav_lay.addStretch(1)
        produtos_nav_lay.addWidget(self.navigation_btn_todos)
        produtos_nav_lay.addWidget(self.navigation_btn_favorito)
        produtos_nav_lay.addWidget(self.navigation_btn_mais_saida)
        produtos_nav_lay.addWidget(self.navigation_btn_promocao)

        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setObjectName("line")

        produtos_layout.addWidget(produtos_scroll)
        produtos_layout.addWidget(line)
        produtos_layout.addLayout(produtos_nav_lay)

        produtosgrupo.setLayout(produtos_layout)

        # Layout Principal de Familia e Produtos
        familia_produtos_lay = QVBoxLayout()
        familia_produtos_lay.setStretch(1, 1)
        familia_produtos_lay.setSpacing(0)
        familia_produtos_lay.setContentsMargins(0, 0, 0, 0)
        familia_produtos_lay.addWidget(familiagrupo)
        familia_produtos_lay.addWidget(produtosgrupo)

        # Layout de subfamilia e Layout de Familia e Produtos
        subfamilia_produtos_lay = QHBoxLayout()
        subfamilia_produtos_lay.addWidget(self.cod_line)
        subfamilia_produtos_lay.addWidget(subfamiliagrupo)
        subfamilia_produtos_lay.addLayout(familia_produtos_lay)

        controlswidget.setLayout(subfamilia_produtos_lay)

        splitter.addWidget(controlswidget)

        totalwidget = QWidget()
        totalwidget.setFixedWidth(400)
        total_layout = QVBoxLayout()
        gridlay = QGridLayout()

        self.total = QLineEdit()
        self.total.setAlignment(Qt.AlignRight)
        self.subtotal = QLineEdit()
        self.subtotal.setAlignment(Qt.AlignRight)
        self.taxa = QLineEdit()
        self.taxa.setAlignment(Qt.AlignRight)
        self.desconto = QLineEdit()
        self.desconto.setAlignment(Qt.AlignRight)
        boldFont2 = QFont('Consolas', 12)
        boldFont2.setBold(True)

        self.total.setFont(boldFont2)
        self.subtotal.setFont(boldFont2)
        self.taxa.setFont(boldFont2)
        self.desconto.setFont(boldFont2)

        self.total.setEnabled(False)
        self.subtotal.setEnabled(False)
        self.taxa.setEnabled(False)
        self.desconto.setEnabled(False)

        self.butao_adicionar_quantidade = QPushButton("AUMENTAR")
        self.butao_adicionar_quantidade.clicked.connect(self.aumentar_quantidade)
        self.butao_adicionar_quantidade.setFixedHeight(40)
        self.butao_adicionar_quantidade.setIcon(QIcon("./icons/add.ico"))
        self.butao_remover_quantidade = QPushButton("DIMINUIR")
        self.butao_remover_quantidade.clicked.connect(self.remove_record)
        self.butao_remover_quantidade.setFixedHeight(40)
        self.butao_remover_quantidade.setIcon(QIcon("./icons/remove.ico"))
        self.butao_selecionar_cima = QPushButton("CIMA")
        self.butao_selecionar_cima.clicked.connect(self.mover_cima)
        self.butao_selecionar_cima.setMaximumWidth(60)
        self.butao_selecionar_cima.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred))
        self.butao_selecionar_baixo = QPushButton("BAIXO")
        self.butao_selecionar_baixo.clicked.connect(self.mover_baixo)
        self.butao_selecionar_baixo.setMaximumWidth(60)
        self.butao_selecionar_baixo.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred))
        self.butao_selecionar_baixo.setIcon(QIcon("./icons/down.ico"))
        self.butao_apagarItem = QPushButton("APAGAR")
        self.butao_apagarItem.clicked.connect(self.removerow)
        self.butao_apagarItem.setFixedHeight(40)
        self.butao_apagarItem.setIcon(QIcon("./icons/Delete.ico"))
        self.butao_apagarTudo = QPushButton("ELIMINAR TODOS")
        self.butao_apagarTudo.clicked.connect(self.removeall)
        self.butao_apagarTudo.setFixedHeight(40)
        self.butao_apagarTudo.setIcon(QIcon("./icons/deleteall.ico"))
        self.butao_editar = QPushButton("EDITAR")
        self.butao_editar.clicked.connect(self.editar_preco_quantidade)
        self.butao_editar.setFixedHeight(40)
        self.butao_editar.setIcon(QIcon("./icons/documentos.ico"))
        self.butao_editar.setEnabled(False)
        self.butao_fechar = QPushButton("FECHAR")
        self.butao_fechar.setIcon(QIcon("./icons/close.ico"))
        self.butao_fechar.clicked.connect(self.close)
        self.butao_fechar.setFixedHeight(40)
        self.butao_fechar.setIcon(QIcon("./icons/shutdown.ico"))

        gridlay.addWidget(QLabel("Subtotal:"), 0, 0)
        gridlay.addWidget(self.subtotal, 0, 1, 1, 2)
        gridlay.addWidget(QLabel("Desconto:"), 1, 0)
        gridlay.addWidget(self.desconto, 1, 1, 1, 2)
        gridlay.addWidget(QLabel("Taxa:"), 2, 0)
        gridlay.addWidget(self.taxa, 2, 1, 1, 2)
        gridlay.addWidget(QLabel("Total:"), 3, 0)
        gridlay.addWidget(self.total, 3, 1, 1, 2)
        gridlay.addWidget(self.butao_adicionar_quantidade, 4, 0)
        gridlay.addWidget(self.butao_remover_quantidade, 4, 1)
        gridlay.addWidget(self.butao_selecionar_cima, 4, 2, 2, 1)
        gridlay.addWidget(self.butao_apagarItem, 5, 0, 1, 2)
        gridlay.addWidget(self.butao_selecionar_baixo, 6, 2, 2, 1)
        gridlay.addWidget(self.butao_apagarTudo, 6, 0, 1, 2)
        gridlay.addWidget(self.butao_editar, 7, 0)
        gridlay.addWidget(self.butao_fechar, 7, 1)

        self.label_total_items = QLabel("")

        total_layout.addWidget(self.tabela)
        total_layout.addWidget(self.label_total_items)
        total_layout.addLayout(gridlay)
        totalwidget.setLayout(total_layout)
        splitter.addWidget(totalwidget)

        mainlayout = QVBoxLayout()

        mainlayout.addWidget(self.cod_line)
        mainlayout.addWidget(splitter)

        centralwidget = QWidget()
        centralwidget.setLayout(mainlayout)

        self.setCentralWidget(centralwidget)
        self.setWindowTitle("Microgest POS")

        self.load_config(self.empresa)

        style = """
            margin: 0;
            padding: 0;
            border-image:url(./images/transferir.jpg) 30 30 stretch;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 24px;
            text-align: center;
        """

        self.label_total.setStyleSheet(style)

        # Enchemos os butoes familia
        self.mostrar_todos()
        self.habilitar_butoes(False)

        try:
            self.load_settings()
        except Exception as e:
            print(e)

        self._ribbon = RibbonWidget(self)
        self.addToolBar(self._ribbon)
        self.init_ribbon()

        self.setStyleSheet(stylesheet(0))

    def focusInEvent(self, *args, **kwargs):
        if self.cod_line.hasFocus():
            print("Hi swona")

    def keyPressEvent(self, event):
        try:
            if event.key() in (Qt.Key_Enter, 16777220, Qt.Key_F10):
                if self.cod_line.text() != "":
                    self.codproduto = self.cod_line.text()
                    self.add_record()

            if event.key() == Qt.Key_F2:
                if self.gravar.isEnabled() or self.gravar.isVisible():
                    self.facturar()

            if event.key() == Qt.Key_F3:
                if self.recibo.isEnabled() or self.recibo.isVisible():
                    self.criar_recibo()

            if event.key() == Qt.Key_F4:
                if self.segundavia.isEnabled() or self.segundavia.isVisible():
                    self.segunda_via()

            if event.key() == Qt.Key_F5:
                self.fill_table()

            if event.key() == Qt.Key_F6:
                if self.receitas_despesas.isEnabled() or self.receitas_despesas.isVisible():
                    self.receitas()

            if event.key() == Qt.Key_F7:
                if self.gravardoc.isEnabled() or self.gravardoc.isVisible():
                    self.grava_transacao()

            if event.key() == Qt.Key_F8:
                if self.trancarsistema.isEnabled() or self.trancarsistema.isVisible():
                    self.trancar_sistema()

            if event.key() == Qt.Key_F10:
                if self.caixa.isEnabled() or self.caixa.isVisible():
                    self.fecho_caixa()

            if event.key() == Qt.Key_F11:
                if self.abrirdoc.isEnabled() or self.abrirdoc.isVisible():
                    self.abrir_documento()

            if event.key() == Qt.Key_Escape:
                self.close()

            if event.key() == Qt.Key_F12:
                self.removeall()

            event.ignore()

        except Exception as e:
            print(e)

    def enterEvent(self, evt):

        self.trancar_automaticamente = 0

        # try:
        #     self.conn.cmd_refresh(1)
        # except Exception as e:
        #     QMessageBox.critical(self, "Erro na base de dados",
        #                          "Conexão com a Base de dados Perdida!!!\n{}.".format(e))
        self.cod_line.setFocus()
        self.cod_line.selectAll()

        if len(self.DADOS_DA_EMPRESA) > 0:

            self.user = self.DADOS_DA_EMPRESA[0]

            self.user_Label.setText('Bem Vindo, {} '.format(self.user))

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
            self.licenca = self.DADOS_DA_EMPRESA[17]
            self.contas = self.DADOS_DA_EMPRESA[18]

        # self.getvalortaxa()
        self.verifica_caixa()
        self.verifica_admin()

        self.fill_table()

    def novo_item(self):
        pr = NovoProduto(self)
        pr.setModal(True)
        pr.show()

    def verifica_admin(self):
        pass

    def load_config(self, empresa):
        sql = """SELECT * FROM config WHERE empresa="{}" """.format(empresa)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                self.fact_template = item[1]
                self.rec_template = item[2]
                self.req_template = item[3]
                self.criar_cliente = item[4]
                self.cliente_normal = item[5]
                self.saldo = item[6]
                self.cliente_inactivo = item[7]
                self.desconto_automatico = item[8]
                self.acima_do_credito = item[9]
                self.pos1 = item[10]
                self.pos2 = item[11]
                self.pos3 = item[12]
                self.pos4 = item[13]
                self.pos5 = item[14]
                self.so_vds = item[15]
                self.imposto_incluso = item[16]
                self.regime_normal = item[17]
                self.multi_taxas = item[18]
                self.q_abaixo_de_zero = item[19]
                self.cop1 = item[20]
                self.cop2 = item[21]
                self.cop3 = item[22]
                self.cop4 = item[23]
                self.cop5 = item[24]

    def mudar_estilo(self, estilo):
        QApplication.setStyle(QStyleFactory.create(estilo))

    def accoes(self):

        self.combo_style = QComboBox()
        self.combo_style.addItems(QStyleFactory.keys())
        self.combo_style.activated[str].connect(self.mudar_style)

        darkblue = QAction("DARK BLUE", self)
        darkgreen = QAction("DARK GREEN", self)
        darkorange = QAction("DARK ORANGE", self)
        lightblue = QAction("LIGHT BLUE", self)
        lightgreen = QAction("LIGHT GREEN", self)
        lightorange = QAction("LIGHT ORANGE", self)
        dark_style = QAction("DARK STYLE", self)
        normal = QAction("NORMAL STYLE", self)

        darkblue.triggered.connect(lambda: self.setStyleSheet(stylesheet(1)))
        darkgreen.triggered.connect(lambda: self.setStyleSheet(stylesheet(2)))
        darkorange.triggered.connect(lambda: self.setStyleSheet(stylesheet(3)))
        lightblue.triggered.connect(lambda: self.setStyleSheet(stylesheet(4)))
        lightgreen.triggered.connect(lambda: self.setStyleSheet(stylesheet(5)))
        lightorange.triggered.connect(lambda: self.setStyleSheet(stylesheet(6)))
        dark_style.triggered.connect(lambda: self.setStyleSheet(stylesheet(7)))
        normal.triggered.connect(lambda: self.setStyleSheet(stylesheet(0)))

        self.accao_fechar = QAction(QIcon("./images/icons8-close-window-50.png"), "Fechar\n(ESC)", self)
        self.accao_fechar.triggered.connect(self.close)
        self.config = QAction(QIcon("./icons/cofiguracao2.ico"), "Configurações", self)
        self.config.triggered.connect(self.mostrar_configuracoes)

        spacer1 = QWidget()
        spacer1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.gravar = QAction(QIcon("./icons/Dollar.ico"), "P&agamento\n(F2)", self)
        self.recibo = QAction(QIcon("./icons/Properties.ico"), "Recibo\n(F3)", self)
        self.receitas_despesas = QAction(QIcon("./icons/refresh.ico"), "Receitas\n(F6)", self)
        self.receitas_despesas.setToolTip("Receitas e Despesas")
        self.gravardoc = QAction(QIcon("./icons/save.ico"), "&Gravar\n(F7)", self)
        self.gravardoc.setToolTip("Gravar documento actual")
        self.abrirdoc = QAction(QIcon("./icons/open.ico"), "&Abrir\n(F11)", self)
        self.segundavia = QAction(QIcon("./icons/stock.ico"), "R&eimprimir\n(F4)", self)
        self.caixa = QAction(QIcon("./icons/report.ico"), "Caixa\n(F10)", self)
        self.caixa.setToolTip("Fechar/Imprimir Caixa")
        self.trancarsistema = QAction(QIcon("./icons/Logout.ico"), "T&rancar\n(F8)", self)
        self.sobre_o_programa = QAction(QIcon("./icons/users.ico"), "Aplicativo", self)
        self.cashdrawer_button = QAction(QIcon("./icons/payment.ico"), "&Abrir\n(F12)", self)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.gravar.triggered.connect(self.facturar)
        self.receitas_despesas.triggered.connect(self.receitas)
        self.abrirdoc.triggered.connect(self.abrir_documento)
        self.gravardoc.triggered.connect(self.grava_transacao)
        self.segundavia.triggered.connect(self.segunda_via)
        self.caixa.triggered.connect(self.fecho_caixa)
        self.trancarsistema.triggered.connect(self.trancar_sistema)
        self.sobre_o_programa.triggered.connect(self.mostrar_sobre)

        # Ribbon
        self.home_tab = self._ribbon.add_ribbon_tab("Início")
        self.finalizar_pane = self.home_tab.add_ribbon_pane("Finalizar")
        self.finalizar_pane.add_ribbon_widget(RibbonButton(self, self.gravar, True))

        self.reimprimir_pane = self.home_tab.add_ribbon_pane("Reimprimir")
        self.reimprimir_pane.add_ribbon_widget(RibbonButton(self, self.segundavia, True))

        self.documentos_pane = self.home_tab.add_ribbon_pane("Documentos")
        self.documentos_pane.add_ribbon_widget(RibbonButton(self, self.abrirdoc, True))
        self.documentos_pane.add_ribbon_widget(RibbonButton(self, self.gravardoc, True))

        self.receitas_pane = self.home_tab.add_ribbon_pane("Receitas")
        self.receitas_pane.add_ribbon_widget(RibbonButton(self, self.receitas_despesas, True))

        self.caixa_pane = self.home_tab.add_ribbon_pane("Caixa")
        self.caixa_pane.add_ribbon_widget(RibbonButton(self, self.caixa, True))

        self.gaveta_pane = self.home_tab.add_ribbon_pane("Gaveta")
        self.gaveta_pane.add_ribbon_widget(RibbonButton(self, self.cashdrawer_button, True))

        self.sistema_pane = self.home_tab.add_ribbon_pane("Sistema")
        self.sistema_pane.add_ribbon_widget(RibbonButton(self, self.trancarsistema, True))
        self.sistema_pane.add_ribbon_widget(RibbonButton(self, self.accao_fechar, True))

        self.home_tab.add_spacer()

        self.total_pane = self.home_tab.add_ribbon_pane("")

        self.sobre_tab = self._ribbon.add_ribbon_tab("Extras")
        self.sobre_pane = self.sobre_tab.add_ribbon_pane("Sobre")
        self.sobre_pane.add_ribbon_widget(RibbonButton(self, self.sobre_o_programa, True))

        self.style_pane = self.sobre_tab.add_ribbon_pane("Estilos")
        self.style_grid = self.style_pane.add_grid_widget(500)
        self.style_grid.addWidget(RibbonButton(self, darkorange, False), 0, 0)
        self.style_grid.addWidget(RibbonButton(self, darkblue, False), 1, 0)
        self.style_grid.addWidget(RibbonButton(self, darkgreen, False), 2, 0)

        self.style_grid.addWidget(RibbonButton(self, lightorange, False), 0, 1)
        self.style_grid.addWidget(RibbonButton(self, lightblue, False), 1, 1)
        self.style_grid.addWidget(RibbonButton(self, lightgreen, False), 2, 1)

        self.style_grid.addWidget(RibbonButton(self, dark_style, False), 0, 2)
        self.style_grid.addWidget(RibbonButton(self, normal, False), 1, 2)
        self.style_grid.addWidget(self.combo_style, 2, 2)

        self.config_pane = self.sobre_tab.add_ribbon_pane("Configurações")
        self.config_pane.add_ribbon_widget(RibbonButton(self, self.config, True))

        self.calcula_total_geral()

    def receitas(self):

        from lista_de_receitas import ListaDeReceitas
        receitas = ListaDeReceitas(self)
        receitas.showMaximized()

    def salvar_config_janelas(self):
        settings = QSettings()
        settings.setValue("MigrogestPOS/facturacao/width", self.width())
        settings.setValue("MigrogestPOS/facturacao/heigth", self.height())
        settings.setValue("MigrogestPOS/facturacao/maximized", self.isMaximized())
        settings.setValue("MigrogestPOS/facturacao/left", self.x())
        settings.setValue("MigrogestPOS/facturacao/right", self.y())

        return True

    def recupera_config_janelas(self):
        settings = QSettings()
        x = settings.value("MigrogestPOS/facturacao/left", 0, int)
        y = settings.value("MigrogestPOS/facturacao/right", 0, int)
        comprimento_da_janela_principal = settings.value("MigrogestPOS/facturacao/heigth", 800, int)
        largura_da_janela_principal = settings.value("MigrogestPOS/facturacao/width", 800, int)

        maximazed = settings.value("MigrogestPOS/facturacao/maximized", False, bool)

        return x, y, comprimento_da_janela_principal, largura_da_janela_principal, maximazed

    def salva_estado_posetivo_do_aplicativo(self):
        """
        Salva o estado de fecho do aplicativo, se não tiver sido vem fechado recupera os ultimos dados
        :return:
        """
        settings = QSettings()
        return settings.setValue("MigrogestPOS/facturacao/fechado", True)

    def salva_estado_negativo_do_aplicativo(self):
        """
        Salva o estado de fecho do aplicativo, se não tiver sido vem fechado recupera os ultimos dados
        :return:
        """
        settings = QSettings()
        return settings.setValue("MigrogestPOS/facturacao/fechado", False)

    def recupera_estado_do_aplicativo(self):
        """
        recupera o estado de fecho do aplicativo, se não tiver sido vem fechado recupera os ultimos dados
        :return:
        """
        settings = QSettings()
        return settings.value("MigrogestPOS/facturacao/fechado", True, bool)

    def fechar_aplicativo(self):

        if self.tabelavazia() is False:
            if QMessageBox.question(self, "Fechar Programa", "Documento não Finalizado.\n"
                                                          "Deseja gravar e fechar o programa?") == QMessageBox.Yes:

                self.salva_estado_posetivo_do_aplicativo()
                return True
            else:
                self.salva_estado_negativo_do_aplicativo()
                return False
        else:
            self.salva_estado_posetivo_do_aplicativo()
            return True

    def mudar_style(self, style):
        QApplication.setStyle(QStyleFactory.create(style))

    def mostrar_sobre(self):
        if self.parent():
            if self.parent().admin is False:
                return False

        return QMessageBox.about(self, "Sobre o Programa",
                          """
                          <p>Orlando Filipe Vilanculos, 2018-2020 todos direitos reservados</p>
                          <hr>
                          <a href="#">Clique aqui para Licença</>
                          """)

    def mostrar_configuracoes(self):
        if self.admin is True:
            from config import Config

            c = Config(self)
            c.setModal(True)
            c.show()

    def init_ribbon(self):
        self.accoes()

    def configurar(self):
        if self.admin:
            from config import Config

            c = Config(self)
            c.setModal(True)
            c.show()
        return True

    def set_max_normal(self):
        if self.isMaximized():
            self.butao_restaurar.setIcon(QIcon("./images/icons8-maximize-window-50.png"))
            self.showNormal()
        else:
            self.butao_restaurar.setIcon(QIcon("./images/icons8-restore-window-50.png"))
            self.showMaximized()

    def editar_preco_quantidade(self):

        if self.current_id == "":
            QMessageBox.information(self, "Info", "Selecione o registo na tabela")
            return

        editar = EditarValores(self)
        editar.nome_produto.setPlainText(self.nome_produto)
        editar.preco_produto.setText(str(self.preco_unitario))
        editar.quantidade_produto.setText(str(self.quantidade_unitario))
        editar.cod_produto = self.codproduto
        editar.codigogeral = self.codigogeral
        editar.cod_facturacaodetalhe = self.cod_facturacaodetalhe
        editar.preco_produto.setEnabled(self.admin)
        editar.butao_preco.setEnabled(self.admin)

        editar.setModal(True)
        editar.show()

    def mover_cima(self):

        if self.totalItems == 0:
            return

        if self.tabela.hasFocus() is False:
            self.tabela.setFocus()

        if self.tabela_row > 0:
            self.tabela_row -= 1

        self.tabela.selectRow(self.tabela_row)
        indice = self.tm.index(self.tabela_row, 0)
        self.current_id = indice.data()

        produto = self.tm.index(self.tabela_row, 1)
        codproduto = produto.data()
        self.codproduto = codproduto

        nome_produto = self.tm.index(self.tabela_row, 2)
        nome = nome_produto.data()
        self.nome_produto = nome

        preco = self.tm.index(self.tabela_row, 4)
        self.preco_unitario = decimal.Decimal(preco.data())

        self.cod_line.setText(self.codproduto)

    def mover_baixo(self):

        if self.totalItems == 0:
            return

        if self.tabela.hasFocus() is False:
            self.tabela.setFocus()

        if self.tabela_row < self.totalItems:
            self.tabela_row += 1

        self.tabela.selectRow(self.tabela_row)
        indice = self.tm.index(self.tabela_row, 0)
        self.current_id = indice.data()

        produto = self.tm.index(self.tabela_row, 1)
        codproduto = produto.data()
        self.codproduto = codproduto

        nome_produto = self.tm.index(self.tabela_row, 2)
        nome = nome_produto.data()
        self.nome_produto = nome

        preco = self.tm.index(self.tabela_row, 4)
        self.preco_unitario = decimal.Decimal(preco.data())

    def aumentar_quantidade(self):

        if self.current_id == "": return

        if self.codproduto == "": return

        print(self.codigogeral, " ", self.codproduto)

        self.add_record()

    def habilitar_butoes(self, bool=False):
        self.butao_apagarItem.setEnabled(bool)
        self.butao_apagarTudo.setEnabled(bool)
        self.butao_adicionar_quantidade.setEnabled(bool)
        self.butao_remover_quantidade.setEnabled(bool)
        self.butao_selecionar_baixo.setEnabled(bool)
        self.butao_selecionar_cima.setEnabled(bool)

    def diminuir_produtos(self):
        if self.current_id == "": return

        if self.codproduto == "": return

        self.remove_record()

    def mostrar_favorito(self):
        self.promocao = 0
        self.favorito = 1
        self.mais_vendidos = 0
        self.offset = 0
        self.unfill(self.familia_layout)
        self.unfill(self.subfamilia_layout)
        self.unfill(self.produtos_layout)
        self.adicionarfamilia(self.offset)
        self.navigation_btn_todos.setChecked(False)
        self.navigation_btn_mais_saida.setChecked(False)
        self.navigation_btn_promocao.setChecked(False)

    def mostrar_promocao(self):
        self.favorito = 0
        self.promocao = 1
        self.mais_vendidos = 0
        self.offset = 0
        self.unfill(self.familia_layout)
        self.unfill(self.subfamilia_layout)
        self.unfill(self.produtos_layout)
        self.adicionarfamilia(self.offset)
        self.navigation_btn_todos.setChecked(False)
        self.navigation_btn_mais_saida.setChecked(False)
        self.navigation_btn_favorito.setChecked(False)

    def mostrar_todos(self):
        self.favorito = 0
        self.promocao = 0
        self.mais_vendidos = 0
        self.offset = 0
        self.unfill(self.familia_layout)
        self.unfill(self.subfamilia_layout)
        self.unfill(self.produtos_layout)
        self.adicionarfamilia(self.offset)
        self.navigation_btn_todos.setChecked(True)
        self.navigation_btn_favorito.setChecked(False)
        self.navigation_btn_promocao.setChecked(False)
        self.navigation_btn_mais_saida.setChecked(False)

    def mostrar_maisvendidos(self):
        self.promocao = 0
        self.favorito = 0
        self.mais_vendidos = 1
        self.offset = 0
        self.unfill(self.familia_layout)
        self.unfill(self.subfamilia_layout)
        self.unfill(self.produtos_layout)
        self.adicionarfamilia(self.offset)
        self.navigation_btn_todos.setChecked(False)
        self.navigation_btn_favorito.setChecked(False)
        self.navigation_btn_promocao.setChecked(False)

    def adicionarfamilia(self, offset):

        if self.mais_vendidos == 1:
            sql = """ select DISTINCT familia.cod, familia.nome from familia JOIN produtos ON 
            familia.cod=produtos.codfamilia JOIN produtosdetalhe ON produtos.cod=produtosdetalhe.codproduto 
            WHERE produtosdetalhe.contagem>0 AND produtosdetalhe.codarmazem="{}" AND familia.estado=1
            GROUP BY familia.cod order by produtosdetalhe.contagem DESC """.format(self.codarmazem, offset)
        elif self.favorito == 1:
            sql = """ select DISTINCT familia.cod, familia.nome from familia JOIN produtos ON 
            familia.cod=produtos.codfamilia JOIN produtosdetalhe ON produtos.cod=produtosdetalhe.codproduto 
            WHERE produtos.favorito=1 AND produtosdetalhe.codarmazem="{}" AND familia.estado=1 GROUP BY familia.cod 
            order by familia.nome """.format(self.codarmazem, offset)
        elif self.promocao == 1:
            sql = """ select DISTINCT familia.cod, familia.nome from familia JOIN produtos ON 
            familia.cod=produtos.codfamilia JOIN produtosdetalhe ON produtos.cod=produtosdetalhe.codproduto 
            WHERE produtos.promocao=1 AND produtosdetalhe.codarmazem="{}" AND familia.estado=1 GROUP BY familia.cod 
            order by familia.nome """.format(self.codarmazem, offset)
        else:
            sql = """ select DISTINCT familia.cod, familia.nome from familia JOIN produtos ON familia.cod=produtos.codfamilia
            JOIN produtosdetalhe ON produtos.cod=produtosdetalhe.codproduto WHERE produtosdetalhe.codarmazem="{}" AND 
            familia.estado=1
            GROUP BY familia.cod order by familia.nome """.format(self.codarmazem, offset)

        self.btn_familia_group = QButtonGroup()
        self.btn_familia_group.setExclusive(True)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:

            buttonFont = QFont('Consolas', 8)

            for x in data:
                self.btn_familia_ = QPushButton(self)
                self.btn_familia_.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                self.btn_familia_.setCheckable(True)
                self.btn_familia_.setIcon(QIcon("./icons/Flameia-Fruity-Hearts-Water-melon.ico"))
                self.btn_familia_.setFont(buttonFont)
                self.btn_familia_.setFixedHeight(40)
                self.btn_familia_.setText(str(x[1]))
                self.btn_familia_.setObjectName(str(x[0]))
                self.btn_familia_.setToolTip(str(x[0]))
                self.btn_familia_group.addButton(self.btn_familia_)

                # Adicionamos os produtos
                if self.familia_first_time is False:
                    self.unfill(self.familia_layout)
                    self.familia_first_time = True

                self.familia_layout.addWidget(self.btn_familia_)
                self.familia_button_w.setLayout(self.familia_layout)

            self.familia_first_time = False
        else:
            self.unfill(self.familia_layout)
            # self.familia_layout.addWidget(self.sem_registo_label)

        self.btn_familia_group.buttonClicked.connect(lambda: self.adicionarsubfamilia(
            self.btn_familia_group.checkedButton().objectName(), self.subfamilia_offset))

    def item_len(self, sql):

        self.cur.execute(sql)
        data = self.cur.fetchall()

        return len(data)

    def familia_next(self):

        # Tamanho da Lista de dados
        tamanho = self.item_len("select cod from familia WHERE estado=1")

        if self.familia_offset < tamanho:
            self.familia_offset += 5
            self.adicionarfamilia(self.familia_offset)
        else:
            self.familia_first()

    def familia_previous(self):
        if self.familia_offset > 0:
            self.familia_offset -= 5

        self.adicionarfamilia(self.familia_offset)

    def familia_first(self):
        self.familia_offset = 0

        self.adicionarfamilia(self.familia_offset)

    def familia_last(self):
        tamanho = self.item_len("select cod from familia")

        # Extraimos a parte inteira da divisao
        parte_inteira = tamanho//5

        ultimo_registo = parte_inteira * 5
        self.familia_offset = ultimo_registo

        self.adicionarfamilia(self.familia_offset)

    def adicionarsubfamilia(self, familia, offset):

        if self.mais_vendidos == 1:
            sql = """ SELECT DISTINCT subfamilia.cod, subfamilia.nome from subfamilia JOIN produtos ON
                        subfamilia.cod=produtos.codsubfamilia JOIN produtosdetalhe 
                        ON produtos.cod=produtosdetalhe.codproduto WHERE produtosdetalhe.codarmazem="{}" 
                        AND produtosdetalhe.contagem>0  AND subfamilia.codfamilia ="{}" AND subfamilia.estado=1 
                        GROUP BY subfamilia.cod 
                        order by produtosdetalhe.contagem DESC """.format(self.codarmazem, familia, offset)
        elif self.promocao == 1:
            sql = """ SELECT DISTINCT subfamilia.cod, subfamilia.nome from subfamilia JOIN produtos ON
                        subfamilia.cod=produtos.codsubfamilia JOIN produtosdetalhe ON produtos.cod=produtosdetalhe.codproduto
                        WHERE produtosdetalhe.codarmazem="{}" AND produtos.promocao=1  AND subfamilia.codfamilia ="{}" 
                        AND subfamilia.estado=1 GROUP BY subfamilia.cod order by subfamilia.nome """.format(self.codarmazem, familia, offset)
        elif self.favorito == 1:
            sql = """ SELECT DISTINCT subfamilia.cod, subfamilia.nome from subfamilia JOIN produtos ON
                        subfamilia.cod=produtos.codsubfamilia JOIN produtosdetalhe ON produtos.cod=produtosdetalhe.codproduto
                        WHERE produtosdetalhe.codarmazem="{}" AND produtos.favorito=1 AND subfamilia.codfamilia ="{}" 
                        AND subfamilia.estado=1 GROUP BY subfamilia.cod 
                        order by subfamilia.nome """.format(self.codarmazem, familia, offset)

        else:
            sql = """ SELECT DISTINCT subfamilia.cod, subfamilia.nome from subfamilia JOIN produtos ON
            subfamilia.cod=produtos.codsubfamilia JOIN produtosdetalhe ON produtos.cod=produtosdetalhe.codproduto
            WHERE produtosdetalhe.codarmazem="{}" AND subfamilia.codfamilia ="{}" AND subfamilia.estado=1 GROUP BY subfamilia.cod 
            order by subfamilia.nome """.format(self.codarmazem, familia, offset)

        self.btn_subfamilia_group = QButtonGroup()
        self.btn_subfamilia_group.setExclusive(True)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:

            buttonFont = QFont('Consolas', 8)

            for x in data:
                self.btn_subfamilia_ = QPushButton(self)
                self.btn_subfamilia_.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
                self.btn_subfamilia_.setFont(buttonFont)
                self.btn_subfamilia_.setCheckable(True)
                self.btn_subfamilia_.setIcon(QIcon("./icons/Flameia-Fruity-Hearts-Water-melon.ico"))
                self.btn_subfamilia_.setFont(buttonFont)
                # self.btn_subfamilia_.setFixedHeight(40)
                self.btn_subfamilia_.setText(str(x[1]))
                self.btn_subfamilia_.setObjectName(str(x[0]))
                self.btn_subfamilia_.setToolTip(str(x[0]))
                self.btn_subfamilia_group.addButton(self.btn_subfamilia_)

                if self.subfamilia_first_time is False:
                    self.unfill(self.subfamilia_layout)
                    self.subfamilia_first_time = True

                self.subfamilia_layout.addWidget(self.btn_subfamilia_)
                self.subfamilia_button_w.setLayout(self.subfamilia_layout)

            self.subfamilia_first_time = False
            self.unfill(self.produtos_layout)
        else:
            self.unfill(self.subfamilia_layout)
            # self.subfamilia_layout.addWidget(self.sem_registo_label)

        self.subfamilia_offset = 0
        self.grupo_clicado = 1

        self.btn_subfamilia_group.buttonClicked.connect(lambda: self.adicionarprodutos(
            self.btn_subfamilia_group.checkedButton().objectName(), self.produtos_offset))

    def subfamilia_next(self):

        if self.btn_familia_group.checkedButton() is None:
            return

        familia = self.btn_familia_group.checkedButton().objectName()
        if familia == "":
            return

        # Tamanho da Lista de dados
        tamanho = self.item_len("""select cod from subfamilia WHERE codfamilia = "{}" """.format(familia))
        # Parte inteira da divisao da lista
        parte_inteira = tamanho // 5

        print("subfamilia offset", self.subfamilia_offset)

        # Se o tamanho da lista de items for maior que o limite
        if tamanho > 5:

            # Se a parte inteira for maior que zero
            if parte_inteira > 0:
                # Resto da divisao da lista de dados
                resto = tamanho - parte_inteira * 5
                if resto > 5:
                    self.subfamilia_offset += 5
                    self.adicionarsubfamilia(familia, self.subfamilia_offset)
                else:
                    self.subfamilia_last()

    def subfamilia_previous(self):
        if self.btn_familia_group.checkedButton() is None:
            return

        familia = self.btn_familia_group.checkedButton().objectName()
        if familia == "":
            return

        if self.subfamilia_offset > 0:
            self.subfamilia_offset -= 5

        self.adicionarsubfamilia(familia, self.subfamilia_offset)

    def subfamilia_first(self):
        if self.btn_familia_group.checkedButton() is None:
            return

        familia = self.btn_familia_group.checkedButton().objectName()
        if familia == "":
            return

        self.subfamilia_offset = 0

        self.adicionarsubfamilia(familia, self.subfamilia_offset)

    def subfamilia_last(self):
        if self.btn_familia_group.checkedButton() is None:
            return

        familia = self.btn_familia_group.checkedButton().objectName()
        if familia == "":
            return

        tamanho = self.item_len("""select cod from subfamilia WHERE codfamilia = "{}" """.format(familia))

        # Extraimos a parte inteira da divisao
        parte_inteira = tamanho//5

        ultimo_registo = parte_inteira * 5
        self.subfamilia_offset = ultimo_registo

        self.adicionarsubfamilia(familia, self.subfamilia_offset)

    def adicionarprodutos(self, subfamilia, offset):

        if self.mais_vendidos ==1:
            sql = """ select DISTINCT produtos.cod, produtos.nome, produtos.preco, produtosdetalhe.quantidade from produtos 
            JOIN produtosdetalhe 
                        ON produtos.cod=produtosdetalhe.codproduto JOIN subfamilia ON subfamilia.cod=produtos.codsubfamilia
                        WHERE produtosdetalhe.codarmazem="{}" AND produtosdetalhe.contagem>0 
                        AND produtos.codsubfamilia ="{}" AND produtos.estado=1 GROUP BY produtos.cod 
                        order by produtosdetalhe.contagem DESC """.format(self.codarmazem, subfamilia, offset)

        elif self.promocao ==1:
            sql = """ select DISTINCT produtos.cod, produtos.nome, produtos.preco, produtosdetalhe.quantidade from produtos 
            JOIN produtosdetalhe 
                        ON produtos.cod=produtosdetalhe.codproduto JOIN subfamilia ON subfamilia.cod=produtos.codsubfamilia
                        WHERE produtosdetalhe.codarmazem="{}" AND produtos.promocao=1 AND produtos.codsubfamilia ="{}" 
                        AND produtos.estado=1 GROUP BY produtos.cod 
                        order by produtos.nome """.format(self.codarmazem, subfamilia, offset)

        elif self.favorito:
            sql = """ select DISTINCT produtos.cod, produtos.nome, produtos.preco, produtosdetalhe.quantidade from produtos JOIN produtosdetalhe 
                        ON produtos.cod=produtosdetalhe.codproduto JOIN subfamilia ON subfamilia.cod=produtos.codsubfamilia
                        WHERE produtosdetalhe.codarmazem="{}" AND produtos.favorito=1 AND produtos.codsubfamilia ="{}" 
                        AND produtos.estado=1 GROUP BY produtos.cod 
                        order by produtos.nome """.format(self.codarmazem, subfamilia, offset)

        else:
            sql = """ select DISTINCT produtos.cod, produtos.nome, produtos.preco, produtosdetalhe.quantidade from produtos JOIN produtosdetalhe 
                        ON produtos.cod=produtosdetalhe.codproduto JOIN subfamilia ON subfamilia.cod=produtos.codsubfamilia
                        WHERE produtosdetalhe.codarmazem="{}" AND produtos.codsubfamilia ="{}" AND produtos.estado=1 GROUP BY produtos.cod 
                        order by produtos.nome """.format(self.codarmazem, subfamilia, offset)

        self.btn_produtos_group = QButtonGroup()
        self.btn_produtos_group.setExclusive(True)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:

            buttonFont = QFont('Consolas', 8)
            tamanho = self.max_lista(data) * 7

            for x in data:
                self.btn_produtos_ = QCommandLinkButton(self)
                self.btn_produtos_.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
                self.btn_produtos_.setFont(buttonFont)
                self.btn_produtos_.setCheckable(True)
                self.btn_produtos_.setIcon(QIcon("./icons/Flameia-Fruity-Hearts-Water-melon.ico"))
                self.btn_produtos_.setFont(buttonFont)
                # self.btn_produtos_.setFixedHeight(40)
                self.btn_produtos_.setText(str(x[1]))
                self.btn_produtos_.setDescription("Preco: {}, Qty: {}".format(str(x[2]), "---"))
                # self.btn_produtos_.setDescription("Preco: {}, Qty: {}".format(str(x[2]), str(x[3])))
                self.btn_produtos_.setObjectName(str(x[0]))
                self.btn_produtos_.setToolTip(str(x[0]))
                self.btn_produtos_group.addButton(self.btn_produtos_)

                self.btn_produtos_.setFixedWidth(tamanho)

                if self.produtos_first_time is False:
                    self.unfill(self.produtos_layout)
                    self.produtos_first_time = True

                self.produtos_layout.addWidget(self.btn_produtos_)
                self.produtos_button_w.setLayout(self.produtos_layout)

            self.produtos_first_time = False
        else:
            self.unfill(self.produtos_layout)
            # self.produtos_layout.addWidget(self.sem_registo_label)

        # Faz a insercao de produtos na Base de dados
        self.btn_produtos_group.buttonClicked.connect(self.gravar_produtos)

        self.produtos_offset = 0
        self.grupo_clicado = 2

    def gravar_produtos(self):
        self.codproduto = self.btn_produtos_group.checkedButton().objectName()
        self.cod_line.setText(self.codproduto)
        self.add_record()

    def produtos_next(self):
        if self.btn_subfamilia_group.checkedButton() is None:
            return

        subfamilia = self.btn_subfamilia_group.checkedButton().objectName()
        if subfamilia == "":
            return

        tamanho = self.item_len("""select cod FROM produtos WHERE codsubfamilia = "{}" """.format(subfamilia))
        parte_inteira = tamanho//50

        # Se o tamanho da lista de items for maior que o limite
        if tamanho > 50:

            # Se a parte inteira for maior que zero
            if parte_inteira > 0:
                # Resto da divisao da lista de dados
                resto = tamanho - parte_inteira * 50
                if resto > 20:
                    self.produtos_offset += 50
                    self.adicionarprodutos(subfamilia, self.produtos_offset)
                else:
                    self.produtos_last()

    def produtos_previous(self):
        if self.btn_subfamilia_group.checkedButton() is None:
            return

        subfamilia = self.btn_subfamilia_group.checkedButton().objectName()
        if subfamilia == "":
            return

        if self.produtos_offset > 0:
            self.produtos_offset -= 50

        self.adicionarprodutos(subfamilia, self.produtos_offset)

    def produtos_first(self):
        if self.btn_subfamilia_group.checkedButton() is None:
            return

        subfamilia = self.btn_subfamilia_group.checkedButton().objectName()
        if subfamilia == "":
            return

        self.produtos_offset = 0

        self.adicionarprodutos(subfamilia, self.produtos_offset)

    def produtos_last(self):
        if self.btn_subfamilia_group.checkedButton() is None:
            return

        subfamilia = self.btn_subfamilia_group.checkedButton().objectName()
        if subfamilia == "":
            return

        tamanho = self.item_len("""select cod FROM produtos  WHERE codsubfamilia = "{}" """.format(subfamilia))

        # Extraimos a parte inteira da divisao
        parte_inteira = tamanho//50

        ultimo_registo = parte_inteira * 50
        self.produtos_offset = ultimo_registo

        self.adicionarprodutos(subfamilia, self.produtos_offset)

    def familia_navigation_first(self):
        self.familia_first()

    def familia_navigation_next(self):
        self.familia_next()

    def familia_navigation_previous(self):
        self.familia_previous()

    def familia_navigation_last(self):
        self.familia_last()

    def navigation_first(self):
        
        if self.grupo_clicado == 1:
            self.subfamilia_first()
        else:
            self.produtos_first()

    def navigation_next(self):
        
        if self.grupo_clicado == 1:
            self.subfamilia_next()
        else:
            self.produtos_next()

    def navigation_previous(self):
        
        if self.grupo_clicado == 1:
            self.subfamilia_previous()
        else:
            self.produtos_previous()
    
    def navigation_last(self):
        
        if self.grupo_clicado == 1:
            self.subfamilia_last()
        else:
            self.produtos_last()

    def max_lista(self, lista):

        l = []
        for i in lista:
            l.append(len(i[1]))

        return int(max(l))

    def unfill(self, lay):
        def deleteItems(layout):
            if layout is not None:
                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
                    else:
                        deleteItems(item.layout())

        deleteItems(lay)

    def fill_table(self):

        header = ["DOC", "Artigo", "Descrição", "Qty", "Preço", "Taxa", "Desconto", "Subtotal", "Total",  "",
                  "Hora", ""]

        sql = """ select facturacao.cod, facturacaodetalhe.codproduto, produtos.nome, facturacaodetalhe.quantidade, 
           facturacaodetalhe.preco, facturacaodetalhe.taxa, facturacaodetalhe.desconto, facturacaodetalhe.subtotal,
           facturacaodetalhe.total, facturacaodetalhe.cod, facturacaodetalhe.created, facturacaodetalhe.ordem 
           FROM produtos INNER JOIN facturacaodetalhe ON produtos.cod=facturacaodetalhe.codproduto
           INNER JOIN facturacao  ON facturacao.cod=facturacaodetalhe.codfacturacao WHERE 
           (facturacao.cod="{facturacaocod}") """.format(facturacaocod=self.codigogeral)

        try:
            self.cur.execute(sql)
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]

        except Exception as e:
            print(e)
            return

        if len(data) == 0:
            self.tabledata = [('', '', '', "", "", "", "", "", "")]
        else:
            l = []
            for x in data:
                row = list(x)

                row[10] = QDateTime.fromString(row[10], "yyyy-MM-dd HH:mm:ss").toString("HH:mm:ss")

                l.append(row)

            self.tabledata = l

        try:
            # set the table model
            self.tm = MyTableModel(self.tabledata, header, self)
            self.totalItems = self.tm.rowCount(self)
            self.label_total_items.setText("ITEMS: {}.".format(self.totalItems))
            self.tabela.setModel(self.tm)
            self.tabela.setColumnHidden(0, True)
            self.tabela.setColumnHidden(1, True)
            self.tabela.setColumnHidden(5, True)
            self.tabela.setColumnHidden(6, True)
            self.tabela.setColumnHidden(7, True)
            self.tabela.setColumnHidden(9, True)

            self.tabela.setColumnWidth(2, self.tabela.width() * 0.35)
            self.tabela.setColumnWidth(3, self.tabela.width() * 0.1)
            self.tabela.setColumnWidth(4, self.tabela.width() * 0.1)
            self.tabela.setColumnWidth(8, self.tabela.width() * 0.15)
            self.tabela.setColumnWidth(10, self.tabela.width() * 0.2)
            self.tabela.setColumnWidth(11, self.tabela.width() * 0.1)

        except Exception as e:
            print(e)
            return
        # # set row height
        nrows = len(self.tabledata)
        for row in range(nrows):
            self.tabela.setRowHeight(row, 30)

    def clickedslot(self, index):

        self.row = int(index.row())
        self.col = int(index.column())

        indice= self.tm.index(self.row, 0)
        self.current_id = indice.data()

        produto = self.tm.index(self.row, 1)
        codproduto = produto.data()
        self.codproduto = codproduto

        nome_produto = self.tm.index(self.row, 2)
        nome = nome_produto.data()
        self.nome_produto = nome

        preco = self.tm.index(self.row, 4)
        self.preco_unitario = decimal.Decimal(preco.data())

        self.butao_apagarItem.setEnabled(True)
        self.butao_editar.setEnabled(True)

    def getcodfornecedor(self):
        sql = """select cod from fornecedores WHERE nome= "{nome}" """.format(nome=self.fornecedor.currentText())

        self.cur.execute(sql)
        data = self.cur.fetchall()
        self.codfornecedor = "".join(data[0])

    def getcodarmazem(self):
        sql = """select cod from armazem WHERE nome= "{nome}" """.format(nome=self.armazem.currentText())

        self.cur.execute(sql)
        data = self.cur.fetchall()
        self.codarmazem = "".join(data[0])

    def getvalortaxa(self):

        if self.regime_normal == 1:
            self.valortaxa = decimal.Decimal(0)
        else:
            sql = """SELECT valor from taxas WHERE cod="TX20182222222" """

            self.cur.execute(sql)
            data = self.cur.fetchall()

            if len(data) > 0:
                self.valortaxa = decimal.Decimal(data[0][0])
            else:
                self.valortaxa = decimal.Decimal(0)

    def habilitarfornecedor(self):
        self.gravar_fornecedor.setEnabled(True)
        self.desabilitarfornecedor()
        self.ativar_fornecedor.setEnabled(False)

    def desabilitarfornecedor(self):

        self.fornecedor.setEnabled(not self.fornecedor.isEnabled())
        self.numerodocumento.setEnabled(not self.numerodocumento.isEnabled())
        self.datadocumento.setEnabled(not self.datadocumento.isEnabled())
        self.valor_pago.setEnabled(not self.valor_pago.isEnabled())
        self.valor_documento.setEnabled(not self.valor_documento.isEnabled())

    def trancar_sistema(self):
        self.Login.armazem.setEnabled(False)
        self.Login.empresas.setEnabled(False)
        self.Login.password.clear()
        self.Login.show()

    def fecho_caixa(self):
        from lista_de_caixa import MainWindow

        cx = MainWindow(self)
        cx.showMaximized()

    def segunda_via(self):

        if self.tabelavazia() is False:
            QMessageBox.warning(self, "Transação Activa", "Por favor termine a transação actual.")
            return False

        sql = """ SELECT * from facturacao WHERE finalizado=1"""
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            QMessageBox.information(self, "Sem documentos", "Não Existe nenhum documento finalizado")
            return False

        from segundavia import Cliente

        gravado = Cliente(self)
        gravado.setModal(True)
        self.limpar_cache()
        gravado.show()

        return True

    def reimprimir(self):
        sql = """ SELECT * from facturacao WHERE finalizado=1"""
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            QMessageBox.information(self, "Sem documentos", "Não Existe nenhum documento finalizado")
            return

        from segundavia import Cliente

        gravado = Cliente(self)
        gravado.setModal(True)
        self.limpar_cache()
        gravado.show()

    def gera_codigogeral(self):
        """
        Cria o código Geral de facturação
        :return: True se o programa tiver sido bem fechado e False caso contrario
        """
        self.codigogeral = "FT" + cd("FT" + "abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")
        self.fill_table()

        return  self.codigogeral

        # if self.recupera_estado_do_aplicativo() is True:
        #
        #     self.reset_labels()
        # else:
        #     self.codigogeral = self.recupera_gravados()
        #     self.fill_table()
        #     self.calcula_total_geral()
        #     self.salva_estado_negativo_do_aplicativo()

    def gravar_documento(self):
        self.codigogeral = "FT" + cd("FT" + "abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")
        self.label_total.setText("0.00")
        self.labelsubtotal.setText("0.00")
        self.labeldesconto.setText("0.00")
        self.labeltaxa.setText("0.00")
        self.labeltaxa.setText("0.00")
        self.labeldesconto.setText("0.00")
        self.labelsubtotal.setText("0.00")

        self.fill_table()

    # Metodo que abre documentos Fechados
    def abrir_documento(self):

        if self.tabelavazia() is False:
            QMessageBox.warning(self, "Transação Activa", "Por favor termine a transação actual.")
            return False

        sql = """ select facturacao.cod from facturacao INNER JOIN facturacaodetalhe 
        ON facturacao.cod=facturacaodetalhe.codfacturacao
        WHERE facturacao.finalizado=0 and facturacaodetalhe.codarmazem="{}" GROUP BY facturacao.cod""".format(
            self.codarmazem)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            QMessageBox.information(self, "Sem documentos", "Não Existe nenhum documento não finalizado")
            return False

        from gravados import Cliente

        gravado = Cliente(self)
        gravado.setModal(True)
        gravado.show()

        return True

    # Grava a transacao corrente
    def grava_transacao(self):
        text, ok = QInputDialog.getText(self, "Gravar documento", "Entre o nome do documento")

        print()
        if ok:
            sql_facturcao = """UPDATE facturacao SET nome="{}" WHERE cod="{}" """.format(text, self.codigogeral)

            try:
                self.cur.execute(sql_facturcao)
                self.conn.commit()

                QMessageBox.information(self, "Sucesso",
                                        "Documento com o nome {}, gravado com Sucesso.".format(text))
            except Exception as e:
                self.conn.rollback()
                QMessageBox.Warning(self, "Falha", "Documento não foi gravado")
                return False

            self.gera_codigogeral()
            self.fill_table()

            return True
        else:
            QMessageBox.Warning(self, "Falha", "Documento não foi gravado")

            return False

    def validacao(self):
        pass

    # Grava as linhas dos produtos na tabela facturacaodetalhe
    def gravadetalhes_problems(self):
        try:
            codfacturacao = self.codigogeral
            codproduto = self.codproduto
            valorcusto = decimal.Decimal(self.custoproduto)

            if self.quantidade.value() == 0.00:
                quantidade = decimal.Decimal(self.quantidade_unitario)
            else:
                quantidade = decimal.Decimal(self.quantidade.value())

            # Calculo de valores para a base de dados
            preco = decimal.Decimal(self.preco_unitario)
            desconto = decimal.Decimal(self.desconto.value() / 100)
            custo = quantidade * valorcusto
            valortaxa = decimal.Decimal(self.valortaxa / 100)
            valordesconto = quantidade * preco * desconto

            if self.taxa.isChecked() is True:
                subtotal = quantidade * preco - valordesconto
                taxa = valortaxa * quantidade * preco
                total = subtotal + taxa
            else:
                preco_unitario = decimal.Decimal(preco / (1 + valortaxa))
                valordesconto = quantidade * preco_unitario * desconto
                subtotal = quantidade * preco_unitario - valordesconto
                taxa = preco_unitario * quantidade * valortaxa
                total = preco * quantidade - valordesconto
                preco = preco_unitario

            lucro = subtotal - custo
        except Exception as e:
            QMessageBox.critical(self, "Erro grave", "Aconteceu erro grave nos seus dados. verifique-os.")
            return

        values = """ "{codfacturacao}", "{codproduto}", {custo}, {preco}, {quantidade}, {subtotal}, {desconto}, 
        {taxa}, {total}, {lucro}, "{codarmazem}" """.format(codfacturacao=codfacturacao, codproduto=codproduto,
                                                            custo=custo,
                                                            preco=preco, quantidade=quantidade,
                                                            subtotal=subtotal,
                                                            desconto=valordesconto, taxa=taxa, total=total,
                                                            lucro=lucro, codarmazem=self.codarmazem)

        sql = """INSERT INTO facturacaodetalhe (codfacturacao, codproduto, custo, preco, quantidade, subtotal, 
        desconto, taxa, total, lucro, codarmazem) values({values}) """.format(values=values)

        try:
            self.cur.execute(sql)
        except Exception as e:
            QMessageBox.critical(self, "Erro", "Os seus detalhes não foram gravados. Erro: {erro} ".format(erro=e))
            return

    def enchefornecedor(self):

        sql = "SELECT nome FROM fornecedores WHERE estado=1"
        self.cur.execute(sql)
        data = self.cur.fetchall()
        if len(data) > 0:
            for item in data:
                self.fornecedor.addItems(item)

    def encheprodutos(self):

        sql = "SELECT nome FROM produtos"
        self.cur.execute(sql)
        data = self.cur.fetchall()
        if len(data) > 0:
            for item in data:
                self.produto.addItems(item)

    def enchearmazem(self):

        sql = "SELECT nome FROM armazem"
        self.cur.execute(sql)
        data = self.cur.fetchall()
        if len(data) > 0:
            for item in data:
                self.armazem.addItems(item)

    def enchetaxas(self):

        sql = "SELECT nome FROM taxas"
        self.cur.execute(sql)
        data = self.cur.fetchall()
        if len(data) > 0:
            for item in data:
                self.taxa.addItems(item)

    def closeEvent(self, evt):

        print("Tentando fechar.......")

        if self.fechar_aplicativo() is False:
            print("Impedido de fechar")
            evt.ignore()
        else:
            print("Pode fechar")
            parent = self.parent()
            if parent is not None:
                parent.fill_table()

            sys.exit()

    def limpar(self):
        for child in (self.findChildren(QLineEdit) or self.findChildren(QTextEdit)):
            if child.objectName() not in ["cod", "cal1", "cal2"]: child.clear()

        # gera novo codigo para stock
        from utilities import codigo
        self.cod.setText("DC" + codigo("DC" + "abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789"))

    def verifica_caixa(self):
        from caixa import caixa
        caixa_form = caixa(self)

        sql = """select cod from caixa WHERE estado=0 and codarmazem="{}" """.format(self.codarmazem)
        self.cur.execute(sql)

        data = self.cur.fetchall()

        if len(data) > 0:
            self.caixa_numero = data[0][0]
        else:
            if QMessageBox.question(self, "Caixa não aberta",
                                    "Deseja abrir a caixa agora?") == QMessageBox.Yes:
                caixa_form.setModal(True)
                caixa_form.show()
            else:
                sys.exit()

    def mostrar_registo(self):

        sql = """SELECT fornecedores.nome, stock.numero, stock.data, stock.valor, stock.pago, produtosdetalhe.codproduto,
        produtosdetalhe.codarmazem, produtosdetalhe.quantidade, produtosdetalhe.valor  from fornecedores INNER JOIN stock ON 
        fornecedores.cod = stock.fornecedor INNER JOIN produtosdetalhe ON stock.cod=produtosdetalhe.codstock
        WHERE stock.cod = "{codigo}" """.format(codigo=str(self.cod.text()))

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            self.cod.setText("DC" + cd("abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789"))
        else:

            self.fornecedor.setCurrentText(''.join(data[0][0]))
            self.numerodocumento.setText(''.join(data[0][1]))
            self.datadocumento.setDate(QDate.fromString(''.join(data[0][2])))
            self.valor_documento.setValue(float(data[0][3]))
            self.valor_pago.setValue(float(data[0][4]))

            self.fill_table()

    # Metodo que busca dados na Base de Dados e enche nos Campos do formulario
    def fill_data(self):
        if self.codproduto == "":
            return

        sql = """ SELECT facturacaodetalhe.codproduto, facturacaodetalhe.preco, facturacaodetalhe.quantidade,
         (facturacaodetalhe.desconto*100)/facturacaodetalhe.preco*facturacaodetalhe.quantidade, produtos.cod, 
         facturacaodetalhe.total, produtosdetalhe.quantidade 
         from facturacaodetalhe INNER JOIN produtos 
         ON facturacaodetalhe.codproduto=produtos.cod
        WHERE (facturacaodetalhe.codfacturacao="{cod}" and facturacaodetalhe.codproduto="{codproduto}") or 
        (facturacaodetalhe.codfacturacao="{cod}" and produtos.cod_barras="{cod_barras}") 
        """.format(cod=self.codigogeral, codproduto=self.codproduto, cod_barras=self.codproduto)

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

    # Verifica se ja se fez a facturacao ou nao
    def existe(self, codigo):

        sql = """SELECT cod from facturacao WHERE cod = "{codigo}" """.format(codigo=str(codigo))

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            return False
        else:
            return True

    # Verifica se o produto existe na tabela detalhe ou nao
    def existeproduto(self, codproduto, codstock):

        sql = """SELECT cod from facturacaodetalhe WHERE codfacturacao="{codstock}" and codproduto = "{codproduto}"
         """.format(codstock=str(codstock), codproduto=codproduto)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            return False
        else:
            return True

    def verifica_existencia(self):

        sql = """select produtos.cod, produtosdetalhe.quantidade, produtos.tipo, produtos.preco, produtos.custo, 
        produtos.preco_de_venda, produtos.preco1, produtos.preco2, produtos.preco3, produtos.preco4
        FROM produtos INNER JOIN produtosdetalhe ON produtos.cod=produtosdetalhe.codproduto WHERE  produtos.cod= "{cod}" 
        and produtosdetalhe.codarmazem="{codarmazem}" """.format(cod=self.codproduto, codarmazem=self.codarmazem)

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        if len(data) > 0:

            for item in data:
                print("Existencia qty {}, preco {}, cod{} :".format(item[1], item[3], item[0]))

                self.quantidade_existente = decimal.Decimal(item[1])
                self.tipo_produto = int(item[2])

                if int(item[5]) == 0:
                    self.preco_unitario = decimal.Decimal(item[3])
                elif int(item[5]) == 1:
                    self.preco_unitario = decimal.Decimal(item[6])
                elif int(item[5]) == 2:
                    self.preco_unitario = decimal.Decimal(item[7])
                elif int(item[5]) == 3:
                    self.preco_unitario = decimal.Decimal(item[8])
                elif int(item[5]) == 4:
                    self.preco_unitario = decimal.Decimal(item[9])

                print("Preco unitario", self.preco_unitario)
                self.custoproduto = decimal.Decimal(item[4])

    def get_quantidade_facturacao(self, codigo, codproduto):
        sql = """SELECT quantidade from facturacaodetalhe WHERE codfacturacao="{}" 
        and codproduto="{}" """.format(codigo, codproduto)
        self.cur.execute(sql)

        data = self.cur.fetchall()

        if len(data) > 0:
            if self.existe(self.codigogeral) is False:
                if data[0][0] >= self.quantidade_existente:
                    return False
                else:
                    return True

    def remove_record(self):
        print("Admin: ", self.admin, "Gestor: ", self.gestor)
        if self.admin is False:
            return False

        sql = """SELECT quantidade from facturacaodetalhe 
        WHERE codfacturacao="{}" and codproduto="{}" """.format(self.codigogeral, self.codproduto)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            quantidade_existente = decimal.Decimal(data[0][0])
            if quantidade_existente > 1:
                self.alterar_quantidade = True

                print("Quantidade antes: ", quantidade_existente)

                self.quantidade_unitario = decimal.Decimal(data[0][0]) - 1

                print("Quantidade depois: ", self.quantidade_unitario)
                self.add_record()

        return True

    def add_record(self):

        if self.codproduto == "":
            return

        # Verifica a quantidade Existente na Base de dados, e colhe preco e custo
        self.verifica_existencia()

        if self.alterar_quantidade is False:
            self.quantidade_unitario = 1

        # Se o tipo de produto for Produto e não Servico
        if int(self.tipo_produto) == 0:

            if self.get_quantidade_facturacao(self.codigogeral, self.codproduto) is False:
                QMessageBox.warning(self, "Quantidade inexistente", "Quantidade não existe na Base de dados.\n"
                                                                    "Existência {}".format(self.quantidade_existente))
                return

        valortaxa = decimal.Decimal(self.valortaxa / 100)

        code = self.codigogeral
        numero = 0
        # data = QDate.currentDate().toString('yyyy-MM-dd')
        coddocumento = self.coddocumento
        codcliente = self.codcliente

        quantidade = self.quantidade_unitario
        preco = decimal.Decimal(self.preco_unitario)
        custo = self.custoproduto * quantidade
        desconto = decimal.Decimal(0.00)

        valordesconto = quantidade * preco * desconto
        subtotal = quantidade * preco - valordesconto
        taxa = valortaxa * quantidade * preco
        total = subtotal + taxa

        lucro = subtotal - custo

        pago = 0.00
        troco = 0.00
        banco = 0.00
        cash = 0.00
        tranferencia = 0.00
        estado = 1
        extenso = ""

        data = DATA_ACTUAL

        ano = ANO_ACTUAL
        mes = MES
        obs = ""

        print(self.validade.text())

        # created = QDate.fromString(str(self.validade.text())).toString("yyyy-MM-dd")
        created = QDate.currentDate().toString("yyyy-MM-dd")
        modified = created

        caixa = self.caixa_numero

        if self.parent() is not None:
            modified_by = self.parent().user
        else:
            modified_by = self.user
        if self.parent() is not None:
            created_by = self.parent().user
        else:
            created_by = self.user

        if self.existe(self.codigogeral) is True:

            sql = """UPDATE facturacao set custo=custo+{custo}, subtotal=subtotal+{subtotal}, 
            desconto=desconto+{desconto}, taxa=taxa+{taxa}, total=total+{total}, lucro=lucro+{lucro}, caixa="{caixa}" 
            WHERE cod="{cod}" """.format(cod=code, custo=custo, subtotal=subtotal, desconto=valordesconto,
                                        taxa=taxa, total=total, lucro=lucro, caixa=caixa)
        else:
            values = """ "{cod}", {numero}, "{coddocumento}", "{codcliente}", "{data}", {custo}, {subtotal}, 
            {desconto}, {taxa}, {total}, {lucro}, {debito},{credito}, {troco}, {banco}, {cash}, {tranferencia}, {estado}, 
            {ano}, {mes}, "{obs}", "{created}", "{modified}", "{modified_by}", "{created_by}", "{caixa}"
             """.format(cod=code, numero=numero, coddocumento=coddocumento, codcliente=codcliente,
                        data=data, custo=custo, subtotal=subtotal, desconto=valordesconto, taxa=taxa,
                        total=total, lucro=lucro, debito=pago, credito= 0.00,troco=troco, banco=banco,
                        cash=cash, tranferencia=tranferencia, estado=estado,ano=ano,
                        mes=mes, obs=obs, created=created, modified=modified, modified_by=modified_by,
                        created_by=created_by, caixa=caixa)

            sql = """INSERT INTO facturacao (cod, numero, coddocumento ,codcliente, data, custo, subtotal,
            desconto, taxa, total,  lucro, debito, credito,troco, banco, cash, tranferencia, estado, ano, mes, 
            obs, created, modified, modified_by, created_by, caixa) values({value})""".format(value=values)

        try:

            print(sql)
            
            self.cur.execute(sql)
            # Grava detalhes do documento mas depende da tabela mae facturacao
            self.gravadetalhes()

            # So Grava caso nao exista erro nas 2 tabelas
            self.conn.commit()
        except Exception as e:
             QMessageBox.critical(self, "Erro", "Os seus dados não foram gravados. Erro: {erro}, created: {c} ".format(erro=e, c=created))
             return

        self.alterar_quantidade = False
        # self.codproduto = ""
        self.fill_table()
        self.cod_line.setFocus()
        self.calcula_total_geral()
        self.habilitar_butoes(True)

    # Grava as linhas dos produtos na tabela facturacaodetalhe
    def gravadetalhes(self):

        codfacturacao = self.codigogeral
        codproduto = self.codproduto
        valorcusto = decimal.Decimal(self.custoproduto)

        quantidade = decimal.Decimal(self.quantidade_unitario)

        # Calculo de valores para a base de dados
        preco = decimal.Decimal(self.preco_unitario)
        desconto = decimal.Decimal(0.00)
        custo = quantidade * valorcusto
        valortaxa = decimal.Decimal(self.valortaxa / 100)
        valordesconto = quantidade * preco * desconto

        subtotal = quantidade * preco - valordesconto
        taxa = valortaxa * quantidade * preco
        total = subtotal + taxa

        print("Taxa: ", taxa)

        lucro = subtotal - custo

        if self.alterar_quantidade is True:
            sql = """UPDATE facturacaodetalhe SET quantidade={}, subtotal=custo*quantidade, total=preco*quantidade,
            lucro=total-custo*quantidade WHERE cod={} """.format(self.quantidade_unitario, self.cod_facturacaodetalhe)

            self.alterar_quantidade = False
        else:
            values = """ "{codfacturacao}", "{codproduto}", {custo}, {preco}, {quantidade}, {subtotal}, {desconto}, 
            {taxa}, {total}, {lucro}, "{codarmazem}" """.format(codfacturacao=codfacturacao, codproduto=codproduto,
                                                                custo=custo,
                                                                preco=preco, quantidade=quantidade,
                                                                subtotal=subtotal,
                                                                desconto=valordesconto, taxa=taxa, total=total,
                                                                lucro=lucro, codarmazem=self.codarmazem)

            sql = """INSERT INTO facturacaodetalhe (codfacturacao, codproduto, custo, preco, quantidade, subtotal, 
            desconto, taxa, total, lucro, codarmazem) values({values}) """.format(values=values)

        self.cur.execute(sql)

    def calcula_total_geral(self):

        sql = """ SELECT sum(custo), sum(desconto), sum(taxa), sum(subtotal), sum(lucro), sum(total) from 
        facturacaodetalhe WHERE codfacturacao="{codfacturacao}" """.format(codfacturacao=self.codigogeral)

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        print(data[0][5])

        if data[0][5] != "None":
            custo = decimal.Decimal(data[0][0])
            desconto = decimal.Decimal(data[0][1])
            taxa = decimal.Decimal(data[0][2])
            subtotal = decimal.Decimal(data[0][3])
            lucro = decimal.Decimal(data[0][4])
            total = decimal.Decimal(data[0][5])
        else:
            custo = decimal.Decimal(0)
            desconto = decimal.Decimal(0)
            taxa = decimal.Decimal(0)
            subtotal = decimal.Decimal(0)
            lucro = decimal.Decimal(0)
            total = decimal.Decimal(0)

        facturacaosql = """ UPDATE facturacao set custo={custo}, desconto={desconto}, taxa={taxa}, 
        subtotal={subtotal}, lucro={lucro},
        total={total} WHERE cod="{cod}" """.format(custo=custo, desconto=desconto, taxa=taxa, subtotal=subtotal,
                                                   lucro=lucro, total=total, cod=self.codigogeral)
        self.cur.execute(facturacaosql)
        total_display = '{}'.format(total)
        taxa_display = '{}'.format(taxa)
        subtotal_display = '{}'.format(subtotal)
        desconto_display = '{}'.format(desconto)

        self.total.setText(total_display)
        self.subtotal.setText(subtotal_display)
        self.desconto.setText(desconto_display)
        self.taxa.setText(taxa_display)

        self.totalgeral = total
        # Actualiza a tabela ou lista de Items
        # Verifica se a tabela está vazia ou não

    def tabelavazia(self):

        if self.codigogeral == "":
            return

        sql = """ SELECT * from facturacaodetalhe WHERE codfacturacao="{cod}" """.format(cod=self.codigogeral)

        print(sql)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            return True
        else:
            return False

    def connect_db(self):
        # Connect to database and retrieves data
        try:
            self.conn = lite.connect(DB_FILENAME)
            self.cur = self.conn.cursor()

        except Exception as e:
            QMessageBox.critical(self, "Erro ao conectar a Base de Dados",
                                 "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
            sys.exit(True)

    # Apaga a Linha na tabela facturadetalhe
    def removerow(self):

        if (self.gestor or self.admin) is False:
            return False

        if self.current_id == "":
            QMessageBox.information(self, "Info", "Selecione o registo a apagar na tabela")
            return False

        sql = """delete from facturacaodetalhe WHERE codproduto="{codigo}" and codfacturacao="{cod}"
        """.format(codigo=str(self.codproduto), cod=self.codigogeral)

        try:
            self.cur.execute(sql)
            self.conn.commit()
            self.calcula_total_geral()
            self.fill_table()

            self.cod_line.setFocus()
            self.cod_line.selectAll()

            return True
        except Exception as e:
            print(e)
            return False

    # Apaga a Linha na tabela facturadetalhe
    def removeall(self):

        if self.admin is False:
            return False

        if self.existe(self.codigogeral):
            sql = """DELETE from facturacaodetalhe WHERE codfacturacao="{}" """.format(self.codigogeral)
            sql2 = """DELETE from facturacao WHERE cod="{}" """.format(self.codigogeral)

            self.cur.execute(sql)
            self.cur.execute(sql2)
            self.conn.commit()

            self.label_total.setText("0.00")
            self.calcula_total_geral()
            self.fill_table()

            self.cod_line.setFocus()
            self.cod_line.selectAll()

            self.habilitar_butoes(False)
            self.butao_editar.setEnabled(False)

        return True

    def facturar(self):

        if self.tabelavazia() is True:
            return False

        if self.existe(self.codigogeral) is True:

            from facturas import Cliente

            factura = Cliente(self, titulo="Facturação", imagem="./icons/Dollar.ico")

            factura.setModal(True)
            factura.gravar_grande.setVisible(False)
            self.limpar_cache()
            factura.show()

        return True

    def limpar_cache(self):

        try:

            for f in glob.glob("*.pdf"):
                os.remove(f)

        except Exception as e:
            print(e)

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
    import time
    from PyQt5.QtWidgets import QProgressBar
    from utilities import center

    app = QApplication(sys.argv)

    app.setApplicationName(APPLICATION_NAME)
    app.setApplicationVersion(APPLICATION_VERSION)
    app.setOrganizationDomain(ORGANIZATION_DOMAIN)
    app.setOrganizationName(ORGANIZATION_NAME)

    # SplashScreen Begin
    pixmap = QPixmap("./images/black.png")
    splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)
    splash.setMask(pixmap.mask())  # this is usefull if the splashscreen is
    splash.resize(400, 200)

    progressbar = QProgressBar(splash)
    progressbar.setMaximum(10)
    progressbar.setGeometry(0, splash.height() - 20, splash.width() + 50, 1)

    label = QLabel("<p style='color: white;'>Modulo: TOUCH POS</p>", splash)
    label.setGeometry(2, splash.height() - 15, int(splash.width() / 2), 15)

    app_label = QLabel("<strong style='color: #C0C0FF;'>Falcão 2021 M.08</strong>".upper(), splash)
    app_label.setGeometry(2, 0, splash.width(), 30)

    center(splash, app)
    splash.show()

    messages = ["Inicializando Modules", "Inicializando App", "Processando Eventos...",
                "Esperando por recursos...", "Carregando Widgets...", "Carregando Ficheiros...",
                "Carregando Estatísticas...", "Fim do Carregamento...",
                "Mostrando Login...", "Mostrando Login...", "Mostrando Login...", "Mostrando Login..."]

    for i in range(11):
        progressbar.setValue(i)
        t = time.time()
        splash.showMessage(messages[i], Qt.AlignRight | Qt.AlignBottom, Qt.yellow)
        while time.time() < t + .1:
            app.processEvents()

    time.sleep(1)

    splash.showMessage(u'Inicializando...', Qt.AlignRight | Qt.AlignBottom, Qt.yellow)

    main_facturacao = Vendas()
    main_facturacao.showMaximized()

    # now kill the spmain_facturacaolashscreen
    splash.finish(main_facturacao)

    sys.exit(app.exec_())