# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gestao_hoteleira.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

import sys
from decimal import Decimal

from PyQt5.QtCore import (Qt, QMetaObject, QCoreApplication, QRect, QSize)
from PyQt5.QtGui import (QIcon, QPixmap)
from PyQt5.QtWidgets import (QApplication, QTabWidget, QWidget, QComboBox, QFrame, QLineEdit, QLabel, QToolBar, 
                             QMenuBar, QMenu, QStatusBar, QDockWidget, QVBoxLayout, QCommandLinkButton,
                             QMainWindow, QSizePolicy, QAction, QSpacerItem, QStyleFactory, QMessageBox)

import loginform_vendas as login
from utilities import codigo as cd
from startpage import StartPage

from GUI.RibbonButton import RibbonButton
from GUI.RibbonWidget import *

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
	border-radius: 5px;
	position: relative;
    padding: 5px;	 
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
	border-radius: 5px;
	position: relative; 
}

QCommandLinkButton:hover 
{
	border: none;
	background: #298DC5;
	color: green;
	padding: 10px;
	border-radius: 5px;
	position: relative; 
}

QCommandLinkButton:selected 
{
	border: none;
	background: #298DC5;
	color: green;
	padding: 10px;
	border-radius: 5px;
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
    left: 5px;
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
    padding:5px 15px;
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
    padding: 15px 5px;
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


class Ui_MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(Ui_MainWindow, self).__init__(parent)

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
        self.caixa_numero = ""

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
        self.empresa_casas_decimais = 0
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

    def tabClose(self):

        # Remove o Tabulador caso o titulo nao seja "Estatísticas"
        if self.tab.tabText(self.tab.currentIndex()) != "Página Inicial" :self.tab.removeTab(self.tab.currentIndex())
        self.totalTabs = self.tab.count()

    def ui(self):

        self.setObjectName("MainWindow")
        self.resize(800, 600)
        self.tab = QTabWidget(self)
        self.tab.setTabsClosable(True)
        self.tab.setTabPosition(1)
        self.tab.setMovable(True)
        self.tab.tabCloseRequested.connect(self.tabClose)

        self.tab.setObjectName("tab")

        self.tab.addTab(self.start, QIcon("icons/hotel.ico"), "Página Inicial")
        self.setCentralWidget(self.tab)

        #Menu
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        self.menuInicio = QMenu(self.menubar)
        self.menuInicio.setObjectName("menuInicio")
        self.menuCadastro = QMenu(self.menuInicio)
        self.menuCadastro.setObjectName("menuCadastro")
        self.setMenuBar(self.menubar)

        #Statusbar
        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        # Dockwidget
        self.dockWidget = QDockWidget(self)
        self.dockWidget.setWindowTitle("Sidebar")
        # self.dockWidget.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.dockWidget.setFeatures(QDockWidget.DockWidgetMovable)
        self.dockWidget.setObjectName("dockWidget")

        #Widget que tera todos controlos
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")


        self.main_layout = QVBoxLayout(self.dockWidgetContents)
        self.main_layout.setObjectName("main_layout")

        #Layout do dockwidget
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        self.combo_estilo = QComboBox()
        self.combo_estilo.addItems(QStyleFactory.keys())
        self.combo_estilo.activated[str].connect(self.mudar_estilo)

        self.statusbar.addWidget(self.combo_estilo)

        self.setWindowIcon(QIcon("icons/hotel.ico"))

        self._ribbon = RibbonWidget(self)
        self.addToolBar(self._ribbon)
        self.init_ribbon()

    def init_ribbon(self):
        self.accoes()

    def accoes(self):
        # CheckIN
        self.CheckIn = QCommandLinkButton("CHECK IN (Entradas)", "Manuseamento de Entradas", self.dockWidgetContents)
        self.checkin_icon = QIcon()
        self.checkin_icon.addPixmap(QPixmap("icons/clientes.ico"), QIcon.Normal, QIcon.Off)
        self.CheckIn.setIconSize(QSize(32, 32))
        self.CheckIn.setIcon(self.checkin_icon)
        self.CheckIn.setObjectName("CheckIn")
        self.verticalLayout.addWidget(self.CheckIn)

        self.line_3 = QFrame(self.dockWidgetContents)
        self.line_3.setFrameShape(QFrame.HLine)
        self.line_3.setFrameShadow(QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.verticalLayout.addWidget(self.line_3)

        # Reservas
        self.cmd_reservas = QCommandLinkButton("RESERVAS/BOOKINGS", "Manuseamento de Reservas", self.dockWidgetContents)
        self.cmd_reservas.setIconSize(QSize(32, 32))
        self.reservas_icon = QIcon()
        self.reservas_icon.addPixmap(QPixmap("images/http-__iconesbr.oficinadanet.com_10693_64x64.png"), QIcon.Normal,
                                     QIcon.Off)
        self.cmd_reservas.setIcon(self.reservas_icon)
        self.cmd_reservas.setObjectName("cmd_reservas")
        self.verticalLayout.addWidget(self.cmd_reservas)

        self.line_4 = QFrame(self.dockWidgetContents)
        self.line_4.setFrameShape(QFrame.HLine)
        self.line_4.setFrameShadow(QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.verticalLayout.addWidget(self.line_4)

        # Categorias
        self.categorias = QCommandLinkButton("CATEGORIA DE QUARTOS", "Categorias e Preço de Quartos")
        self.categorias.setIconSize(QSize(32, 32))
        self.categorias_icon = QIcon("icons/categorias.ico")
        self.categorias.setIcon(self.categorias_icon)
        self.verticalLayout.addWidget(self.categorias)

        # Quartos
        self.cmd_quartos = QCommandLinkButton("QUARTOS", "Cadastro e Gestão de Quartos", self.dockWidgetContents)
        self.cmd_quartos.setIconSize(QSize(32, 32))
        self.quartos_icon = QIcon("images/sleep_hotel.png")
        self.cmd_quartos.setIcon(self.quartos_icon)
        self.cmd_quartos.setObjectName("cmd_quartos")
        self.verticalLayout.addWidget(self.cmd_quartos)

        self.line_5 = QFrame(self.dockWidgetContents)
        self.line_5.setFrameShape(QFrame.HLine)
        self.line_5.setFrameShadow(QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.verticalLayout.addWidget(self.line_5)

        # hospedes
        self.cmd_hospedes = QCommandLinkButton("HOSPEDES", "Cadastro de Hóspedes", self.dockWidgetContents)
        self.cmd_hospedes.setIconSize(QSize(32, 32))
        self.hospede_icon = QIcon()
        self.hospede_icon.addPixmap(QPixmap("images/hospedes.png"), QIcon.Normal, QIcon.Off)
        self.cmd_hospedes.setIcon(self.hospede_icon)
        self.cmd_hospedes.setObjectName("cmd_hospedes")
        self.verticalLayout.addWidget(self.cmd_hospedes)

        # Espaco Vertical
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        # Label de Usuários
        self.user_Label = QLabel()
        self.verticalLayout.addWidget(self.user_Label)

        # Linha
        self.line = QFrame(self.dockWidgetContents)
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)

        # Butao sair
        self.cmd_sair = QCommandLinkButton(self.dockWidgetContents)
        self.cmd_sair.setIconSize(QSize(32, 32))
        self.close_icon = QIcon()
        self.close_icon.addPixmap(QPixmap("icons/close.ico"), QIcon.Normal, QIcon.Off)
        self.cmd_sair.setIcon(self.close_icon)
        self.cmd_sair.setObjectName("cmd_sair")
        self.verticalLayout.addWidget(self.cmd_sair)

        # Layout Principal
        self.main_layout.addLayout(self.verticalLayout)

        self.dockWidget.setWidget(self.dockWidgetContents)
        self.addDockWidget(Qt.DockWidgetArea(1), self.dockWidget)

        # Accoes
        action_check_in = QAction(self.checkin_icon, "Check IN/OUT", self)
        action_reservas = QAction(self.reservas_icon, "Reservas", self)
        action_categorias = QAction(self.categorias_icon, "Categorias", self)
        action_hospedes = QAction(self.hospede_icon, "Hóspedes", self)
        action_quartos = QAction(self.quartos_icon, "Quartos", self)
        action_sair = QAction(self.close_icon, "Sair", self)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)

        # SINAIS E SLOTS
        self.cmd_hospedes.clicked.connect(self.listahospedes)
        action_hospedes.triggered.connect(self.listahospedes)

        action_quartos.triggered.connect(self.listaquartos)
        self.cmd_quartos.clicked.connect(self.listaquartos)

        self.categorias.clicked.connect(self.listacategorias)
        action_categorias.triggered.connect(self.listacategorias)

        self.CheckIn.clicked.connect(self.listacheck_in)
        action_check_in.triggered.connect(self.listacheck_in)

        self.cmd_reservas.clicked.connect(self.listareservas)
        action_reservas.triggered.connect(self.listareservas)

        self.cmd_sair.clicked.connect(self.close)
        action_sair.triggered.connect(self.close)

        self.retranslateUi(self)
        QMetaObject.connectSlotsByName(self)

        home_tab = self._ribbon.add_ribbon_tab("Inicio")

        hospedes_pane = home_tab.add_ribbon_pane("Hóspedes")
        hospedes_pane.add_ribbon_widget(RibbonButton(self, action_hospedes, True))

        categorias_pane = home_tab.add_ribbon_pane("Quartos")
        categorias_pane.add_ribbon_widget(RibbonButton(self, action_categorias, True))
        categorias_pane.add_ribbon_widget(RibbonButton(self, action_quartos, True))

        reservas_pane = home_tab.add_ribbon_pane("Reservas")
        reservas_pane.add_ribbon_widget(RibbonButton(self, action_reservas, True))

        checkin_pane = home_tab.add_ribbon_pane("Checkin/Checout")
        checkin_pane.add_ribbon_widget(RibbonButton(self, action_check_in, True))

        sistema_pane = home_tab.add_ribbon_pane("Sistema")
        sistema_pane.add_ribbon_widget(RibbonButton(self, action_sair, True))

    def mudar_estilo(self, estilo):
        QApplication.setStyle(QStyleFactory.create(estilo))

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        # self.setWindowTitle(_translate("MainWindow", "Microgest POS"))
        self.menuInicio.setTitle(_translate("MainWindow", "Inicio"))
        self.menuCadastro.setTitle(_translate("MainWindow", "Cadastro"))
        self.CheckIn.setText(_translate("MainWindow", "Check in"))
        self.cmd_reservas.setText(_translate("MainWindow", "Booking (Reservas)"))
        self.cmd_hospedes.setText(_translate("MainWindow", "Hóspedes"))
        self.cmd_quartos.setText(_translate("MainWindow", "Quartos"))
        self.cmd_sair.setText(_translate("MainWindow", "Sair"))
        self.cmd_sair.setToolTip("Sair do Sitema")

    def listacheck_in(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count()+1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Entradas (Check In)":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_check_in

        check_ins = lista_de_check_in.ListaCheckIN(self)
        check_ins.radio_tudo.setChecked(True)

        self.check_in = self.tab.addTab(check_ins, self.checkin_icon, "Lista de Entradas (Check In)")
        check_ins.show()
        self.tab.setCurrentIndex(self.check_in)

    def listareservas(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count()+1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Reservas":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_reservas

        reservass = lista_de_reservas.Lista_de_Reservas(self)

        self.reservas = self.tab.addTab(reservass, self.reservas_icon, "Lista de Reservas")
        reservass.show()
        self.tab.setCurrentIndex(self.reservas)

    def listacategorias(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count()+1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Categorias":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_precos

        categorias = lista_de_precos.Lista_de_Precos(self)

        self.categoria = self.tab.addTab(categorias, self.categorias_icon, "Lista de Categorias")
        categorias.show()
        self.tab.setCurrentIndex(self.categoria)

    def listahospedes(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count()+1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Hóspedes":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_hospedes

        clientes = lista_de_hospedes.MainWindow(self)

        self.fornecedores = self.tab.addTab(clientes, self.hospede_icon, "Lista de Hóspedes")
        clientes.show()
        self.tab.setCurrentIndex(self.fornecedores)

    def listaquartos(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count()+1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Quartos":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_quartos

        quartos = lista_de_quartos.Lista_de_Quartos(self)

        self.quartos = self.tab.addTab(quartos, self.quartos_icon, "Lista de Quartos")
        quartos.show()
        self.tab.setCurrentIndex(self.quartos)

    def enterEvent(self, *args, **kwargs):
        # try:
        #     self.conn.cmd_refresh(1)
        # except Exception as e:
        #     QMessageBox.critical(self, "Erro na base de dados",
        #                          "Conexão com a Base de dados Perdida!!!\n{}.".format(e))
        if len(self.DADOS_DA_EMPRESA) > 0:
            self.user = self.DADOS_DA_EMPRESA[0]

            self.user_Label.setText('Bem Vindo, {} '.format(self.user))
            # self.armazem.setText("Armazém: {}".format(self.nome_armazem))

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

            self.start.bmvindo.setText("Bem Vindo, {}".format(self.empresa))
            self.start.usuario.setText("Usuário: {}".format(self.user))

            if self.empresa_logo != "":

                style2 = """ QDialog{border-image: url(%s);}""" % self.empresa_logo
                self.start.setStyleSheet(style2)
        self.verifica_caixa()

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


if __name__ == '__main__':
    import time
    from utilities import center

    app = QApplication(sys.argv)

    pixmap = QPixmap("./images/black.png")
    splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)
    splash.setMask(pixmap.mask())  # this is usefull if the splashscreen is

    splash.resize(400, 200)

    progressbar = QProgressBar(splash)
    progressbar.setMaximum(10)
    progressbar.setGeometry(0, splash.height() - 20, splash.width() + 50, 1)

    label = QLabel("<p style='color: white;'>Modulo: Hotelaria</p>", splash)
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

    hotel = Ui_MainWindow()
    hotel.showMaximized()

    splash.finish(hotel)

    sys.exit(app.exec_())

