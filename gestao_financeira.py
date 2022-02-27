
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gestao_hoteleira.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

import sys
from decimal import Decimal

from PyQt5.QtCore import (Qt, QMetaObject, QRect, QSize)
from PyQt5.QtGui import QIcon, QPixmap, QKeySequence as QKSec

from GUI.RibbonButton import RibbonButton
from GUI.RibbonWidget import *

from PyQt5.QtWidgets import (QApplication, QTabWidget, QWidget, QComboBox, QFrame, QMessageBox, QLabel, QToolBar,
                             QMenuBar, QMenu, QStatusBar, QDockWidget, QVBoxLayout, QCommandLinkButton,
                             QMainWindow, QSizePolicy, QAction, QSpacerItem, QStyleFactory)

import loginform_vendas as login
from utilities import codigo as cd
from startpage import StartPage

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

QCommandLifnkButton:selected 
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


class GestaoFinanceira(QMainWindow):

    def __init__(self, parent=None):
        super(GestaoFinanceira, self).__init__(parent)

        self.start = StartPage(self)

        self.codigogeral = "FT" + cd("FT" + "abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")
        self.codcliente = "CL20181111111"
        self.cod_produto = ""
        self.coddocumento = "DC20184444444"
        self.custoproduto = 0.00
        self.valortaxa = 0.00
        self.current_id = ""
        self.foto = ""
        self.preco_unitario = Decimal(0.00)
        self.quantidade_unitario = 0.00
        self.alterar_quantidade = False
        self.alterar_de_preco = False
        self.quantidade_existente = 0.00
        self.tipo_produto = 0

        self.conn = ""
        self.database = ""
        self.cur = ""
        self.user = "user"
        self.admin = False
        self.gestor = False
        self.conta = "Banco Teste"

        self.conta_cabecalho = ""
        self.conta_logo = ""
        self.conta_slogan = ""
        self.conta_endereco = ""
        self.conta_contactos = ""
        self.conta_email = ""
        self.conta_web = ""
        self.conta_nuit = ""
        self.conta_casas_decimais = 0
        self.caixa_numero = ""
        self.licenca = ""
        self.contas = ""
        self.incluir_iva = 1
        self.codarmazem = ""
        self.nome_armazem = ""
        self.DADOS_DA_EMPRESA = []

        login.MODULO = "hotel"
        self.setHidden(True)
        self.Login = login.Login(self)
        self.Login.encheempresas()
        self.Login.setModal(True)
        self.Login.showFullScreen()

        # self.setStyleSheet(STYLESHEET)

    def tabClose(self):

        # Remove o Tabulador caso o titulo nao seja "Estatísticas"
        if self.tab.tabText(self.tab.currentIndex()) != "Página Inicial": self.tab.removeTab(self.tab.currentIndex())
        self.totalTabs = self.tab.count()

    def ui(self):

        self.setObjectName("GestaoFinanceira")
        self.setWindowIcon(QIcon("icons/credit_card.ico"))
        self.tab = QTabWidget(self)
        self.tab.setTabsClosable(True)
        self.tab.setTabPosition(1)
        self.tab.setMovable(True)
        self.tab.tabCloseRequested.connect(self.tabClose)
        self.tab.setObjectName("tab")
        self.tab.addTab(self.start, QIcon("icons/credit_card.ico"), "Página Inicial")

        self.setCentralWidget(self.tab)

        # Statusbar
        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        # Fornecedores
        self.cc_fornecedores_icon = QIcon("icons/fornecedores.ico")

        # Clientes
        self.cliente_icon = QIcon()
        self.cliente_icon.addPixmap(QPixmap("icons/clientes2.ico"), QIcon.Normal,
                                      QIcon.Off)
        # Bancos
        self.contas_icon = QIcon()
        self.contas_icon.addPixmap(QPixmap("icons/credit_card.ico"), QIcon.Normal, QIcon.Off)

        # Transações
        self.transacoes_icon = QIcon()
        self.transacoes_icon.addPixmap(QPixmap("icons/creditCard.ico"), QIcon.Normal, QIcon.Off)
        self.cc_clientes_icon = QIcon("icons/clientes.ico")
        self.cc_fornecedor_icon = QIcon("icons/cc_fornecedores.ico")
        self.pagamento_de_clientes_icon = QIcon("icons/ok.ico")
        self.pagamento_a_Fornecedores_icon = QIcon("icons/SUPPLIERS.ico")
        self.cheques_icon = QIcon("icons/coins.ico")
        self.close_icon = QIcon()
        self.close_icon.addPixmap(QPixmap("icons/close.ico"), QIcon.Normal, QIcon.Off)

        # Accoes
        action_fornecedores = self.create_action(self.lista_de_Fornecedores, self.cc_fornecedores_icon,
                                                 "Fornecedores", "Gerir Fornecedores", self)
        action_contas = self.create_action(self.listacontas, self.contas_icon, "Contas",
                                           "Gerir Contas Bancárias", self)
        action_clientes = self.create_action(self.lista_de_clientes, self.cliente_icon, "Clientes", "Gerir Clientes", self)
        action_transacoes = self.create_action(self.listatransacoes, self.transacoes_icon,
                                               "Transações", "Gerir Transações Bancárias", self)
        action_cc_clientes = self.create_action(self.listacc_clientes, self.cc_clientes_icon, "Clientes",
                                                "Gerir Conta Corrente de Clientes", self)
        action_cc_fornecedor = self.create_action(self.lista_cc_fornecedores, self.cc_fornecedor_icon,
                                                  "Fornecedores", "Gerir Conta Corrente de Fornecedores", self)
        action_pagamento_de_clientes = self.create_action(self.listapagamento_de_clientes,
                                                          self.pagamento_de_clientes_icon, "Clientes",
                                                          "Pagamento de Clientes à nossa Empresa", self)
        action_pagamento_a_fornecedores = self.create_action(self.listapagamento_a_fornecedores,
                                                             self.pagamento_a_Fornecedores_icon, "Fornecedores",
                                                             "Pagamentos da nossa Empresa para Fornecedores", self)
        action_cheques = self.create_action(self.listacheques,
                                            self.cheques_icon, "Cheques", "Gestão de Cheques de Clientes", self)

        action_sair = self.create_action(self.close, self.close_icon, "Encerrar", "Sair do Sistema", self)
        self.tab.setContextMenuPolicy(Qt.ActionsContextMenu)
        QMetaObject.connectSlotsByName(self)

        self.combo_estilo = QComboBox()
        self.combo_estilo.addItems(QStyleFactory.keys())
        self.combo_estilo.activated[str].connect(self.mudar_estilo)

        self.statusbar.addWidget(self.combo_estilo)

        self._ribbon = RibbonWidget(self)
        self.addToolBar(self._ribbon)

        # Ribbon
        home_tab = self._ribbon.add_ribbon_tab("Início")
        terceiros_pane = home_tab.add_ribbon_pane("Terceiros")
        terceiros_pane.add_ribbon_widget(RibbonButton(self, action_fornecedores, True))
        terceiros_pane.add_ribbon_widget(RibbonButton(self, action_clientes, True))

        bancos_pane = home_tab.add_ribbon_pane("Bancos")
        bancos_pane.add_ribbon_widget(RibbonButton(self, action_contas, True))
        bancos_pane.add_ribbon_widget(RibbonButton(self, action_transacoes, True))
        bancos_pane.add_separator()
        bancos_pane.add_ribbon_widget(RibbonButton(self, action_cheques, True))

        cc_pane = home_tab.add_ribbon_pane("Contas")
        cc_pane.add_ribbon_widget(RibbonButton(self, action_cc_fornecedor, True))
        cc_pane.add_ribbon_widget(RibbonButton(self, action_cc_clientes, True))

        pagamentos_pane = home_tab.add_ribbon_pane("Pagamentos")
        pagamentos_pane.add_ribbon_widget(RibbonButton(self, action_pagamento_a_fornecedores, True))
        pagamentos_pane.add_ribbon_widget(RibbonButton(self, action_pagamento_de_clientes, True))

        sistema_pane = home_tab.add_ribbon_pane("Sistema")
        sistema_pane.add_ribbon_widget(RibbonButton(self, action_sair, True))

    def create_action(self, triggered_method, icon, title="", tooltip="", parent=None):
        action = QAction(icon, title, parent)
        action.triggered.connect(triggered_method)
        action.setToolTip(tooltip)

        return action

    def mudar_estilo(self, estilo):
        QApplication.setStyle(QStyleFactory.create(estilo))

    def lista_de_Fornecedores(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count() + 1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Fornecedores":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_fornecedores

        cc_fornecedores = lista_de_fornecedores.MainWindow(self)

        self.cc_fornecedores = self.tab.addTab(cc_fornecedores, self.cc_fornecedores_icon, "Lista de Fornecedores")
        cc_fornecedores.show()
        self.tab.setCurrentIndex(self.cc_fornecedores)

    def lista_de_clientes(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count() + 1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Clientes":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_clientes

        clientes = lista_de_clientes.MainWindow(self)

        self.clientes = self.tab.addTab(clientes, self.cc_fornecedores_icon, "Lista de Clientes")
        clientes.show()
        self.tab.setCurrentIndex(self.clientes)

    def listacontas(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count() + 1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Contas":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_contas

        contas = lista_de_contas.Lista_de_Contas(self)

        lista_contas = self.tab.addTab(contas, self.contas_icon, "Lista de Contas")
        contas.show()
        self.tab.setCurrentIndex(lista_contas)

    def listatransacoes(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count() + 1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Transações":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_transacoes

        transacoes = lista_de_transacoes.Lista_de_Trasnsacoes(self)

        self.transacoes = self.tab.addTab(transacoes, self.transacoes_icon, "Lista de Transações")
        transacoes.show()
        self.tab.setCurrentIndex(self.transacoes)

    def listacc_clientes(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count() + 1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "CC Clientes":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_cc_clientes

        cc_clientes = lista_de_cc_clientes.Lista_de_CC_Cliente(self)

        self.cc_clientes = self.tab.addTab(cc_clientes, self.cc_clientes_icon, "CC Clientes")
        cc_clientes.show()
        self.tab.setCurrentIndex(self.cc_clientes)

    def lista_cc_fornecedores(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count() + 1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Fornecedores":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_cc_fornecedores

        cc_fornecedores = lista_de_cc_fornecedores.Lista_de_CC_Fornecedor(self)

        self.cc_fornecedores = self.tab.addTab(cc_fornecedores, self.cc_fornecedor_icon, "Lista de Fornecedores")
        cc_fornecedores.show()
        self.tab.setCurrentIndex(self.cc_fornecedores)

    def listapagamento_de_clientes(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count() + 1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Pagamento de clientes":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_pagamento_de_clientes

        pagamento_de_clientes = lista_de_pagamento_de_clientes.Lista_de_Pagamento_de_Cliente(self)

        lista_pagamento_de_clientes = self.tab.addTab(pagamento_de_clientes, self.pagamento_de_clientes_icon, "Pagamento de clientes")
        pagamento_de_clientes.show()
        self.tab.setCurrentIndex(lista_pagamento_de_clientes)

    def listapagamento_a_fornecedores(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count() + 1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Pagamento de fornecedores":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_pagamento_a_fornecedores

        pagamento_de_fornecedores = lista_de_pagamento_a_fornecedores.Lista_de_Pagamento_a_Fornecedor(self)

        lista_pagamento_de_fornecedores = self.tab.addTab(pagamento_de_fornecedores, self.pagamento_a_Fornecedores_icon, "Pagamento de fornecedores")
        pagamento_de_fornecedores.show()
        self.tab.setCurrentIndex(lista_pagamento_de_fornecedores)

    def listacheques(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count() + 1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Cheques":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_cheques

        cheques = lista_de_cheques.Lista_de_Cheque(self)

        lista_cheques = self.tab.addTab(cheques, self.cheques_icon, "Cheques")
        cheques.show()
        self.tab.setCurrentIndex(lista_cheques)

    def enterEvent(self, *args, **kwargs):
        # try:
        #     self.conn.cmd_refresh(1)
        # except Exception as e:
        #     QMessageBox.critical(self, "Erro na base de dados",
        #                          "Conexão com a Base de dados Perdida!!!\n{}.".format(e))
        if len(self.DADOS_DA_EMPRESA) > 0:
            self.user = self.DADOS_DA_EMPRESA[0]

            self.conta = self.DADOS_DA_EMPRESA[2]
            self.conta_cabecalho = self.DADOS_DA_EMPRESA[3]
            self.conta_logo = self.DADOS_DA_EMPRESA[4]
            self.conta_slogan = self.DADOS_DA_EMPRESA[5]
            self.conta_endereco = self.DADOS_DA_EMPRESA[6]
            self.conta_contactos = self.DADOS_DA_EMPRESA[7]
            self.conta_email = self.DADOS_DA_EMPRESA[8]
            self.conta_web = self.DADOS_DA_EMPRESA[9]
            self.conta_nuit = self.DADOS_DA_EMPRESA[10]
            self.conta_casas_decimais = self.DADOS_DA_EMPRESA[11]
            self.licenca = self.DADOS_DA_EMPRESA[17]
            self.contas = self.DADOS_DA_EMPRESA[18]

            self.start.bmvindo.setText("Bem Vindo, {}".format(self.conta))
            self.start.usuario.setText("Usuário: {}".format(self.user))

            if self.conta_logo != "":
                style2 = """ QDialog{border-image: url(%s);}""" % self.conta_logo
                self.start.setStyleSheet(style2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    hotel = GestaoFinanceira()
    hotel.show()

    sys.exit(app.exec_())