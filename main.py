# -*- coding: utf-8 -*-

import os
import sys

from PyQt5.QtCore import Qt, QTimer, QDate, QTime, QSettings
from PyQt5.QtGui import QIcon, QFont, QPixmap

from GUI.RibbonButton import RibbonButton
from GUI.RibbonWidget import *


import loginform as login
from utilities import stylesheet


class Gestor(QMainWindow):

    def  __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.conn = ""
        self.database = ""
        self.cur = ""

        self.user = "user"
        self.admin = True
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
        self.licenca = ""
        self.contas = ""

        self.setWindowIcon(QIcon('logo.ico'))

        self.DADOS_DA_EMPRESA = []

        Login = login.Login(self)
        Login.encheempresas()
        Login.setModal(True)
        Login.show()

    def ui(self):

        self.tab = QTabWidget()
        self.tab.setTabsClosable(True)
        self.tab.setTabPosition(1)
        self.tab.setMovable(True)
        self.tab.tabCloseRequested.connect(self.tabClose)
        self.setCentralWidget(self.tab)

        self._ribbon = RibbonWidget(self)
        self.addToolBar(self._ribbon)

        self.setStyleSheet(stylesheet(0))

    def show_startpage(self):
        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count() + 1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Estatísticas":
                # self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one

        import estatisticas
        sp = estatisticas.Estatisticas(self)
        self.tab.addTab(sp, "Estatísticas")

    def accoes(self):

        familias = QAction(QIcon("./icons/familias.ico"), "&Famílias",self)
        subfamilias = QAction(QIcon("./icons/subfamilias.ico"), "&Subfamílias", self)
        produtos = QAction(QIcon("./icons/produtos.ico"), "&Produtos e\nServiços", self)
        armazens = QAction(QIcon("./icons/armazens.ico"), "&Armazéns", self)
        stock = QAction(QIcon("./icons/stock.ico"), "S&tock", self)

        clientes = QAction(QIcon("./icons/clientes.ico"), "&Clientes", self)
        fornecedores = QAction(QIcon("./icons/fornecedores.ico"), "F&ornecedores", self)

        taxas = QAction(QIcon("./icons/taxas.ico"), "Taxas", self)
        documentos = QAction(QIcon("./icons/documentos.ico"), "&Documentos", self)

        users = QAction(QIcon("./icons/users.ico"), "&Usuários",self)
        configuracoes = QAction(QIcon("./icons/cofiguracao.ico"), "Confi&guração",self)

        darkblue = QAction("Dark Blue", self)
        darkgreen = QAction("Dark Green", self)
        darkorange = QAction("Dark Orange", self)
        lightblue = QAction("Light Blue", self)
        lightgreen = QAction("Light Green", self)
        lightorange = QAction("Light Orange", self)
        dark_style = QAction("Dark Style", self)
        normal = QAction("Normal", self)

        darkblue.triggered.connect(lambda: self.setStyleSheet(stylesheet(1)))
        darkgreen.triggered.connect(lambda: self.setStyleSheet(stylesheet(2)))
        darkorange.triggered.connect(lambda: self.setStyleSheet(stylesheet(3)))
        lightblue.triggered.connect(lambda: self.setStyleSheet(stylesheet(4)))
        lightgreen.triggered.connect(lambda: self.setStyleSheet(stylesheet(5)))
        lightorange.triggered.connect(lambda: self.setStyleSheet(stylesheet(6)))
        dark_style.triggered.connect(lambda: self.setStyleSheet(stylesheet(7)))
        normal.triggered.connect(lambda: self.setStyleSheet(stylesheet(0)))

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        toolbox = QToolBox()

        lay = QVBoxLayout()
        lay.setSpacing(0)
        widget = QFrame()

        clientesButton = QCommandLinkButton("Lista de Clientes")
        fornecedoresButton = QCommandLinkButton("Lista de fornecedores")

        clientesButton.addAction(clientes)
        lay.addWidget(clientesButton)

        fornecedoresButton.addAction(fornecedores)
        lay.addWidget(fornecedoresButton)
        lay.addStretch()

        widget.setLayout(lay)
        wid = QGroupBox()

        self.data = QLabel()

        user = QLabel("")
        pc = QLabel("")
        pc_user = QLabel("")
        user.setText("Usuário: %s " % self.user)
        user.setAlignment(Qt.AlignBottom)

        font = QFont("times new roman", 10)
        user.setFont(font)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        dic = os.environ

        #
        cp = dic['COMPUTERNAME']
        pu = dic['USERNAME']
        #
        pc.setText("PC: %s " % cp)
        pc_user.setText("USER: %s " % pu)
        pc.setFont(font)
        pc_user.setFont(font)

        self.user_label = QLabel("Bem Vindo, ")

        self.status = QStatusBar()

        self.status.addWidget(self.data)
        self.status.addWidget(pc)
        self.status.addWidget(pc_user)
        self.status.addWidget(self.user_label)
        self.setStatusBar(self.status)

        timer = QTimer(self)
        timer.timeout.connect(self.horas)
        timer.start(1000)

        frame = QGroupBox()
        #
        toolbox.addItem(wid,"Informação do Sistema")
        toolbox.addItem(frame,"Atalhos")

        clientes.triggered.connect(self.listaclientes)
        fornecedores.triggered.connect(self.listafornecedores)
        users.triggered.connect(self.listausers)
        familias.triggered.connect(self.listafamilias)
        subfamilias.triggered.connect(self.listasubfamilias)
        produtos.triggered.connect(self.listaprodutos)
        armazens.triggered.connect(self.listaarmazems)
        taxas.triggered.connect(self.listataxas)
        stock.triggered.connect(self.listastock)
        documentos.triggered.connect(self.listadocumentos)
        configuracoes.triggered.connect(self.configuracoes)

        # Ribbon
        self.home_tab = self._ribbon.add_ribbon_tab("Início")
        self.catalogo_pane = self.home_tab.add_ribbon_pane("Produtos")
        self.catalogo_pane.add_ribbon_widget(RibbonButton(self, familias, True))
        self.catalogo_pane.add_ribbon_widget(RibbonButton(self, subfamilias, True))
        self.catalogo_pane.add_ribbon_widget(RibbonButton(self, produtos, True))

        self.stock_pane = self.home_tab.add_ribbon_pane("Armazém")
        self.stock_pane.add_ribbon_widget(RibbonButton(self, armazens, True))
        self.stock_pane.add_ribbon_widget(RibbonButton(self, stock, True))

        self.terceiros_pane = self.home_tab.add_ribbon_pane("Terceiros")
        self.terceiros_pane.add_ribbon_widget(RibbonButton(self, clientes, True))
        self.terceiros_pane.add_ribbon_widget(RibbonButton(self, fornecedores, True))

        self.taxas_pane = self.home_tab.add_ribbon_pane("Taxas")
        self.taxas_pane.add_ribbon_widget(RibbonButton(self, taxas, True))

        self.documentos_pane = self.home_tab.add_ribbon_pane("Documentos")
        self.documentos_pane.add_ribbon_widget(RibbonButton(self, documentos, True))

        self.sistema_pane = self.home_tab.add_ribbon_pane("Sistema")
        self.sistema_pane.add_ribbon_widget(RibbonButton(self, users, True))
        self.sistema_pane.add_ribbon_widget(RibbonButton(self, configuracoes, True))

    def init_ribbon(self):
        self.accoes()

    def horas(self):
        self.data.setText(QDate.currentDate().toString("dd-MM-yyyy") + "  " + QTime.currentTime().toString())
        # self.ac.setTime(QTime.currentTime())

    def menuVisible(self):
        self.menu.setVisible(True)

    def dadosEmp(self):
        setings = QSettings()
        self.nome = setings.value("empresa/nome").toString()
        self.cabecalho = setings.value("empresa/cabecalho").toString()
        self.logo = setings.value("empresa/logo").toString()

    def tabClose(self):

        # Remove o Tabulador caso o titulo nao seja "Estatísticas"
        if self.tab.tabText(self.tab.currentIndex()) != "Estatísticas" :self.tab.removeTab(self.tab.currentIndex())
        self.totalTabs = self.tab.count()

    def listaclientes(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count()+1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Clientes":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_clientes

        clientes = lista_de_clientes.MainWindow(self)

        self.fornecedores = self.tab.addTab(clientes, QIcon("./icons/clientes.ico"), "Lista de Clientes")
        clientes.show()
        self.tab.setCurrentIndex(self.fornecedores)

    def listafamilias(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count()+1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Famílias":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_familias

        familias = lista_de_familias.MainWindow(self)

        self.familias = self.tab.addTab(familias, QIcon("./icons/familias.ico"), "Lista de Famílias")
        familias.show()
        self.tab.setCurrentIndex(self.familias)

    def listasubfamilias(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count()+1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Sub Famílias":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_subfamilias

        subfamilias = lista_de_subfamilias.MainWindow(self)

        self.subfamilias = self.tab.addTab(subfamilias, QIcon("./icons/subfamilias.ico"), "Lista de Sub Famílias")
        subfamilias.show()
        self.tab.setCurrentIndex(self.subfamilias)

    def listaprodutos(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count() + 1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Produtos/Serviços":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_produtos

        produtos = lista_de_produtos.MainWindow(self)
        produtos.empresa = self.empresa

        self.produtos = self.tab.addTab(produtos, QIcon("./icons/produtos.ico"), "Lista de Produtos/Serviços")
        produtos.show()
        self.tab.setCurrentIndex(self.produtos)

    def listaarmazems(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count() + 1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Armazéns":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_armazems

        armazems = lista_de_armazems.MainWindow(self)

        self.armazems = self.tab.addTab(armazems, QIcon("./icons/armazens.ico"), "Lista de Armazéns")
        armazems.show()
        self.tab.setCurrentIndex(self.armazems)

    def listataxas(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count() + 1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Taxas":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_taxas

        taxas = lista_de_taxas.MainWindow(self)

        self.taxas = self.tab.addTab(taxas, QIcon("./icons/taxas.ico"), "Lista de Taxas")
        taxas.show()
        self.tab.setCurrentIndex(self.taxas)

    def listastock(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count() + 1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Stock":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_stock

        stock = lista_de_stock.MainWindow(self)
        stock.empresa = self.empresa

        self.stock = self.tab.addTab(stock, QIcon("./icons/stock.ico"), "Lista de Stock")
        stock.show()
        self.tab.setCurrentIndex(self.stock)

    def listadocumentos(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count() + 1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Documentos":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_documentos

        documentos = lista_de_documentos.MainWindow(self)

        self.documentos = self.tab.addTab(documentos, QIcon("./icons/documentos.ico"), "Lista de Documentos")
        documentos.show()
        self.tab.setCurrentIndex(self.documentos)

    def listausers(self):

        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count() + 1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Usuários":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_users

        users = lista_de_users.MainWindow(self)

        self.users = self.tab.addTab(users, QIcon("./icons/users.ico"), "Lista de Usuários")
        users.show()
        self.tab.setCurrentIndex(self.users)

    def listafornecedores(self):
        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count() + 1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Fornecedores":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import lista_de_fornecedores

        fornecedores = lista_de_fornecedores.MainWindow(self)

        self.fornecedores = self.tab.addTab(fornecedores, QIcon("./icons/fornecedores.ico"), "Lista de Fornecedores")
        fornecedores.show()
        self.tab.setCurrentIndex(self.fornecedores)

    def facturas_nao_pagas(self):
        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count() + 1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Lista de Facturas a Receber":
                self.tab.setCurrentIndex(item)
                return

        from lista_de_recibos import MainWindow as nao_pagas

        np = nao_pagas(self)
        facturas_a_receber = self.tab.addTab(np, QIcon("./icons/fornecedores.ico"), "Lista de Facturas a Receber")
        np.show()
        self.tab.setCurrentIndex(facturas_a_receber)

    def factura(self):
        from eliminar_factura import EliminarFacturas

        f = EliminarFacturas(self)
        f.setModal(True)
        f.showMaximized()

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_9:
            self.factura()
        else:
            event.ignore()

    def configuracoes(self):
        # verifies if in the list of tabs finds the name
        for item in range(0, self.tab.count() + 1, 1):

            # if finds the selects the current tab and returns
            if self.tab.tabText(item) == "Configurações":
                self.tab.setCurrentIndex(item)
                return

        # Did not find then makes one
        import configuracoes

        config = configuracoes.Config(self)

        self.config = self.tab.addTab(config, QIcon("./icons/cofiguracao.ico"), "Configurações")
        config.show()
        self.tab.setCurrentIndex(self.config)

    def closeEvent(self, event):
        event.ignore()
        for child in self.findChildren(QMainWindow):
            print(child)
            child.close()

        qApp.quit()

    def enterEvent(self, *args, **kwargs):
        if len(self.DADOS_DA_EMPRESA) > 0:

            if self.DADOS_DA_EMPRESA[1] == 1:
                self.admin = True
            else:
                self.admin = False

            self.user = self.DADOS_DA_EMPRESA[0]
            self.user_label.setText("Bem Vindo, {}".format(self.user))

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
            self.show_startpage()


def run():
    if __name__ == '__main__':
        print("Running main app........")
        import time
        from PyQt5.QtWidgets import QProgressBar
        from utilities import center

        app = QApplication(sys.argv)

        # SplashScreen Begin
        pixmap = QPixmap("./images/black.png")
        splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)
        splash.setMask(pixmap.mask())  # this is usefull if the splashscreen is
        splash.resize(400, 200)

        progressbar = QProgressBar(splash)
        progressbar.setMaximum(10)
        progressbar.setGeometry(0, splash.height()-20, splash.width()+50, 1)

        label = QLabel("<p style='color: white;'>Modulo: Administração</p>", splash)
        label.setGeometry(2, splash.height()-15, int(splash.width()/2), 15)

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

        main = Gestor()
        main.setWindowTitle('Microgest POS')
        main.showMaximized()

        # Fecha o splash
        splash.finish(main)

        sys.exit(app.exec_())

run()
