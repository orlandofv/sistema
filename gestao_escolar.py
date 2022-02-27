# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gestao_hoteleira.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

import sys
from decimal import Decimal

from PyQt5.QtCore import (Qt, QMetaObject, QCoreApplication, QRect, QSize)
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
    color: #4f514d;
    border: 1px solid #3a7999;
    gridline-color: orange;
    background-color: white;
    selection-color: #3a7999;
    selection-background-color: #3a7999;
    border-radius: 0px;
    padding: 0px;
    margin: 0px;
}

QTableView::item:hover  {
    background: orange;
}

QTableView::item:disabled  {
    color: #888a85;
}

QTableView::item:selected  {
    color: #5d7619;
    background-color: orange;
}

/* when editing a cell: */
QTableView QLineEdit {
    color: #4f514d;
    background-color: #cccfc9;
    border-radius: 0px;
    margin: 0px;
    padding: 0px;
}

QHeaderView {
    border: none;
    background-color: #4f514d;
    border-top-left-radius: 3px;
    border-top-right-radius: 3px;
    border-bottom-left-radius: 0px;
    border-bottom-right-radius: 0px;
    margin: 0px;
    padding: 0px;
}

QHeaderView::section  {
    background-color: transparent;
    color: #c8c9c7;
    border: 1px solid transparent;
    border-radius: 0px;
    text-align: center;
}

QHeaderView::section::vertical  {
    padding: 0px 6px 0px 6px;
    border-bottom: 1px solid #6f716d;
}

QHeaderView::section::vertical:first {
    border-top: 1px solid  #6f716d;
}

QHeaderView::section::vertical:last {
    border-bottom: none;
}

QHeaderView::section::vertical:only-one {
    border: none;
}

QHeaderView::section::horizontal  {
    padding: 0px 0px 0px 6px;
    border-right: 1px solid #6f716d;
}

QHeaderView::section::horizontal:first {
    border-left: 1px solid #6f716d;
}

QHeaderView::section::horizontal:last {
    border-left: none;
}

QHeaderView::section::horizontal:only-one {
    border: none;
}

"""

class GestaoEscolar(QMainWindow):

    def __init__(self, parent=None):
        super(GestaoEscolar, self).__init__(parent)

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

        self.setStyleSheet(STYLESHEET)

    def tabClose(self):

        # Remove o Tabulador caso o titulo nao seja "Estatísticas"
        if self.tab.tabText(self.tab.currentIndex()) != "Página Inicial" :self.tab.removeTab(self.tab.currentIndex())
        self.totalTabs = self.tab.count()

    def ui(self):

        self.setObjectName("Escolar")
        self.resize(800, 600)
        self.tab = QTabWidget(self)
        self.tab.setTabsClosable(True)
        self.tab.setTabPosition(1)
        self.tab.setMovable(True)
        self.tab.tabCloseRequested.connect(self.tabClose)

        self.tab.setObjectName("tab")

        self.tab.addTab(self.start, QIcon("icons/hotel.ico"), "Página Inicial")
        self.setCentralWidget(self.tab)

        #Statusbar
        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.estudantes_icon = QIcon()
        self.estudantes_icon.addPixmap(QPixmap("icons/Icons-Land-Vista-People-Groups-Meeting-Dark.ico"), QIcon.Normal, QIcon.Off)
        self.docente_icon = QIcon()
        self.docente_icon.addPixmap(QPixmap("icons/LogInpeople.ico"), QIcon.Normal,
                                      QIcon.Off)
        self.empresas_icon = QIcon()
        self.empresas_icon.addPixmap(QPixmap("icons/report.ico"), QIcon.Normal, QIcon.Off)
        self.cursos_icon = QIcon()
        self.cursos_icon.addPixmap(QPixmap("icons/aluno.ico"), QIcon.Normal, QIcon.Off)
        self.formacao_icon = QIcon("images/fileopen.png")
        self.certificacao_icon = QIcon("icons/save.ico")
        
        #Linha
        self.line = QFrame(self.dockWidgetContents)
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.line.setObjectName("line")

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
        action_alunos = QAction(self.estudantes_icon, "Estudantes", self)
        action_empresas = QAction(self.empresas_icon, "Empresas", self)
        action_docentees = QAction(self.docente_icon, "Instrutores", self)
        action_cursos = QAction(self.cursos_icon, "Estudantes", self)
        action_formacao = QAction(self.formacao_icon, "Formação", self)
        action_certificacao = QAction(self.certificacao_icon, "Cerificados", self)
        action_sair = QAction(self.close_icon, "Sair do Sistema", self)
        
        QMetaObject.connectSlotsByName(self)

        self.setWindowIcon(QIcon("icons/escola.ico"))

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
        separator = QAction("-", self)
        separator.setSeparator(True)
        bancos_pane.addAction(separator)
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

    def lista_de_alunos(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count()+1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Estudantes":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_estudantes

        alunos = lista_de_estudantes.ListaDeEstudantes(self)

        self.alunos = self.tab.addTab(alunos, self.estudantes_icon, "Lista de Estudantes")
        alunos.show()
        self.tab.setCurrentIndex(self.alunos)

    def lista_de_docentees(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count()+1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Instrutores":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_docentees

        estudantes = lista_de_docentees.ListaDeInstrutores(self)

        self.estudantes = self.tab.addTab(estudantes, self.estudantes_icon, "Lista de Instrutores")
        estudantes.show()
        self.tab.setCurrentIndex(self.estudantes)

    def listaempresas(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count() + 1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Empresas":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_empresas

        empresas = lista_de_empresas.ListaDeEmpresas(self)
        
        lista_empresas = self.tab.addTab(empresas, self.empresas_icon, "Lista de Empresas")
        empresas.show()
        self.tab.setCurrentIndex(lista_empresas)

    def listacursos(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count()+1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Cursos":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_cursos

        cursos = lista_de_cursos.ListaDeCursos(self)

        self.cursos = self.tab.addTab(cursos, self.cursos_icon, "Lista de Cursos")
        cursos.show()
        self.tab.setCurrentIndex(self.cursos)

    def listaformacao(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count()+1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Formações":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_formacao

        formacao = lista_de_formacao.ListaDeFormacao(self)

        self.formacao = self.tab.addTab(formacao, self.formacao_icon, "Lista de Formações")
        formacao.show()
        self.tab.setCurrentIndex(self.formacao)

    def listaclientes(self):

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

    def lista_certificados(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count()+1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Certificados":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_certificados

        certificados = lista_de_certificados.ListaDeCertificados(self)

        self.certificados = self.tab.addTab(certificados, self.certificacao_icon, "Lista de Certificados")
        certificados.show()
        self.tab.setCurrentIndex(self.certificados)

    def enterEvent(self, *args, **kwargs):
        # try:
        #     self.conn.cmd_refresh(1)
        # except Exception as e:
        #     val = QMessageBox.critical(self, "Erro na base de dados",
        #                          "Conexão com a Base de dados Perdida!!!\n{}.".format(e))
        #     if val == QMessageBox.Ok:
        #         sys.exit()

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    hotel = GestaoEscolar()
    hotel.show()

    sys.exit(app.exec_())