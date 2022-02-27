# -*- coding: utf-8 -*-
"""
Created on Fri Mar 02 23:18:43 2012

@author: lims
"""
import decimal
import os
import glob
from time import localtime, strftime
import datetime

from PyQt5.QtWidgets import  QLabel, QLineEdit,QVBoxLayout, QToolBar, QMessageBox, QSizePolicy, \
    QTextEdit, QAction, QApplication, QGroupBox, QPushButton, QDateEdit, QCalendarWidget,\
    QHBoxLayout, QWidget, QTableView, QSplashScreen, QAbstractItemView, QSplitter, QMainWindow, \
    QScrollArea, QButtonGroup , QComboBox, QStyleFactory, QSizeGrip, QStatusBar

from PyQt5.QtPrintSupport import QPrintDialog, QPrinter

from PyQt5.QtCore import Qt, QDate, QSize, pyqtSignal, QTimer, pyqtSlot, QSizeF, QSettings
from PyQt5.QtGui import QIcon, QFont, QPixmap, QTextDocument
import sys

from GUI.RibbonButton import RibbonButton
from GUI.RibbonWidget import *

from utilities import codigo as cd
from utilities import stylesheet
from editar_quantidade import EditarValores

from flowlayout import FlowLayout
import sqlite3 as lite

import loginform_vendas as login
from novo_produto import NovoProduto
from flowlayout import FlowLayout

DB_FILENAME = "dados.tsdb"

DATA_HORA_FORMATADA = strftime("%Y-%m-%d %H:%M:%S", localtime())
DATA_ACTUAL = datetime.date.today()
ANO_ACTUAL = DATA_ACTUAL.year
DIA = DATA_ACTUAL.day
MES = DATA_ACTUAL.month
HORA = DATA_ACTUAL.ctime()

APPLICATION_NAME = "Microgest POS"
APPLICATION_VERSION = "1.0.2020"
ORGANIZATION_DOMAIN = "www.microgest.com"
ORGANIZATION_NAME = "Microgest Lda"

class Cliente(QMainWindow):

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
        super(Cliente, self).__init__(parent)

        self.totalgeral = 0.00

        estilo = QStyleFactory.create("Fusion")
        # estilo = QStyle(styles)
        QApplication.setStyle(estilo)

        self.totalItems = 0

        # Controla a Mesa seleccionada
        self.numero_da_mesa = 0
        # Variavel que controla o número de Mesas a exibir
        self.numero_mesas = 10
        # Controla se deve se imprimir a ordem ou não depois de cria-la
        self.imprimir_ordem = True
        # Exigir ordem antes de Imprimir a Conta do Cliente
        self.exigir_ordem = True
        # Imprimir Items apgados na lista de pedidos
        self.imprimir_items_apagados = True

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

        login.MODULO = "RESTAURANTE"
        self.Login = login.Login(self)
        self.Login.encheempresas()
        self.Login.setModal(True)
        self.setHidden(True)
        self.Login.showFullScreen()

    def ui(self):

        self.central_widget = QWidget()

        style = """
            QScrollArea {
            font-size: 36px;
            padding: 5px;    
            border: 1px solid #5e90fa;
            border-radius: 2px;
            margin: 7px;
            background-color: #5e90fa;
            color: #fff;   
        }
        """

        scroll = QScrollArea()
        scroll.setStyleSheet(style)

        scroll.setWidget(self.central_widget)
        scroll.setWidgetResizable(True)
        self.button_layout = FlowLayout()
        self.button_layout.setContentsMargins(50, 50, 50, 50)

        self.setCentralWidget(scroll)

        try:
            self.load_settings()
            self.cria_mesas(self.numero_mesas)
        except Exception as e:
            print(e)

        self.load_button_list()

        self._ribbon = RibbonWidget(self)
        self.addToolBar(self._ribbon)
        self.init_ribbon()

        self.setStyleSheet(stylesheet(0))
        self.setWindowIcon(QIcon('./icons/sandes.ico'))

    def init_ribbon(self):
        self.accoes()

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
        if settings.mesas in (None, ""):
            settings.mesas = 1

        self.numero_mesas = settings.mesas
        self.papel_1 = int(settings.papel_1.replace("mm", ""))
        self.papel_2 = int(settings.papel_2.replace("mm", ""))

    # Metodo que cria mesas e visualiza no ui
    def cria_mesas(self, numero_de_mesas):

        self.btn_mesasgroup = SpecialButtonGroup()
        self.btn_mesasgroup.setExclusive(False)

        buttonFont = QFont('Consolas', 24)
        buttonFont.setBold(True)

        for x in range(1, numero_de_mesas + 1):

            self.btn_mesas = QCommandLinkButton(self)
            # self.btn_mesas.setStyleSheet(style)
            self.btn_mesas.setIcon(QIcon())
            # self.btn_mesas.setMinimumSize(40, 40)
            self.btn_mesas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.btn_mesas.setFont(buttonFont) ,
            self.btn_mesas.setCheckable(True)
            # self.btn_mesas.setIcon(QIcon("./icons/Flameia-Fruity-Hearts-Water-melon.ico"))
            # self.btn_mesas.setFixedHeight(40)
            self.btn_mesas.setText(str(x))
            self.btn_mesas.setObjectName(str(x))
            # print(x, self.codigogeral, self.get_table_username(x, self.codigogeral))
            # self.btn_mesas.setDescription(self.get_table_username(x))
            self.btn_mesas.setToolTip("Mesa {}.".format(x))
            self.btn_mesasgroup.addButton(self.btn_mesas, x)

            self.button_layout.addWidget(self.btn_mesas)
        
        self.btn_mesasgroup.buttonClicked[int].connect(self.on_button_clicked)

        mainlayout = QVBoxLayout()
        mainlayout.setContentsMargins(10, 10, 10 , 10)
        mainlayout.addLayout(self.button_layout)

        self.central_widget.setLayout(mainlayout)

    # Metodo que detecta qual botao foi clicado no ButtonGroup
    def on_button_clicked(self, id):
        for button in self.btn_mesasgroup.buttons():
            if button is self.btn_mesasgroup.button(id):
                self.numero_da_mesa = int(button.objectName())

        if self.numero_da_mesa <= 0:
            return False

        # Obtemos o cádigo geral da facturacao
        self.buscar_codigo(self.numero_da_mesa)

        if self.gravar_mesa(self.numero_da_mesa) is False:
            return False

        # Mostra a janela de Vendas de produtos
        self.abrir_conta(self.numero_da_mesa)

        return True

    # Verifica se a mesa está ocupada ou nao
    def buscar_codigo(self, numero_mesa):
        sql = """SELECT f.cod FROM mesas m INNER JOIN facturacao f ON f.cod=m.codfacturacao 
        WHERE m.numero={} and f.finalizado=0 """.format(numero_mesa)
        self.cur.execute(sql)
        dados = self.cur.fetchall()

        if len(dados) > 0:
            self.codigogeral = dados[0][0]

        return self.codigogeral

    # Grava a mesa na base de dados e marca como ocupado ou reabre caso esteja ocupada
    def gravar_mesa(self, numero_mesa):

        modified = created = QDate.currentDate().toString("yyyy-MM-dd")
        modified_by = created_by = self.user

        desc = ""
        obs = ""

        if self.existe(self.numero_da_mesa, self.codigogeral) is False:

            sql = """INSERT INTO mesas(numero, descricao, codfacturacao, estado, created, modified, modified_by, 
            created_by, obs) VALUES ({}, "{}", "{}", {}, "{}", "{}", "{}", "{}", "{}") 
            """.format(numero_mesa, desc, self.codigogeral, 1, created, modified, modified_by, created_by, obs )

            try:
                self.add_record()
                self.cur.execute(sql)
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                QMessageBox.warning(self, "Erro", "Houve erro na criação do Pedido.\n{}.".format(e))
                return False

        return True

    def abrir_conta(self, numero_mesa):

        from vendas_restaurante import VendasRestaurante

        vendas = VendasRestaurante(self)
        vendas.caixa_numero = self.caixa_numero
        vendas.empresa = self.empresa
        vendas.codarmazem = self.codarmazem
        vendas.nome_armazem = self.nome_armazem
        vendas.numero_da_mesa = numero_mesa
        vendas.empresa_cabecalho = self.empresa_cabecalho
        vendas.empresa_logo = self.empresa_logo
        vendas.empresa_slogan = self.empresa_slogan
        vendas.empresa_endereco = self.empresa_endereco
        vendas.empresa_contactos = self.empresa_contactos
        vendas.empresa_email = self.empresa_email
        vendas.empresa_web = self.empresa_web
        vendas.empresa_nuit = self.empresa_nuit
        vendas.empresa_casas_decimais = self.empresa_casas_decimais
        vendas.licenca = self.licenca
        vendas.contas = self.contas

        buttonFont = QFont('Oldman BookStyle', 14)
        buttonFont.setBold(True)

        vendas.mesa_Label.setText("{}".format(numero_mesa))

        # Desabilitamos a mesa
        # vendas.mesa_Label.setEnabled(False)

        vendas.mesa_Label.setFont(buttonFont)
        vendas.setWindowTitle("Microgest POS - {}".format(self.empresa))
        vendas.gravar_documento()
        vendas.mostrar_todos()
        vendas.load_config(self.empresa)
        vendas.codigogeral = self.codigogeral

        vendas.fact_template = self.fact_template
        vendas.rec_template = self.rec_template
        vendas.req_template = self.req_template
        vendas.criar_cliente = self.criar_cliente
        vendas.cliente_normal = self.cliente_normal
        vendas.saldo = self.saldo
        vendas.cliente_inactivo = self.cliente_inactivo
        vendas.desconto_automatico = self.desconto_automatico
        vendas.acima_do_credito = self.acima_do_credito
        vendas.pos1 = self.pos1
        vendas.pos2 = self.pos2
        vendas.pos3 = self.pos3
        vendas.pos4 = self.pos3
        vendas.pos5 = self.pos5
        vendas.so_vds = self.so_vds
        vendas.imposto_incluso = self.imposto_incluso
        vendas.regime_normal = self.regime_normal
        vendas.multi_taxas = self.multi_taxas
        vendas.q_abaixo_de_zero = self.q_abaixo_de_zero
        vendas.cop1 = self.cop1
        vendas.cop2 = self.cop2
        vendas.cop3 = self.cop3
        vendas.cop4 = self.cop4
        vendas.cop5 = self.cop5

        vendas.admin = self.admin
        vendas.gestor = self.gestor

        if vendas.tabelavazia() is False:
            vendas.habilitar_butoes(True)
            vendas.tabela.setFocus()

        vendas.cod_line.setFocus()
        vendas.calcula_total_geral()

        # Desabilita todas funcionalidades caso usuario seja diferente
        user = self.get_user(self.numero_da_mesa, self.user)

        vendas.setEnabled(user)

        # Define o user que pode apagar os ITEMS
        if vendas.verificar_permisao_apagar(self.user) == 1:
            print("Usuario pode apagar...")
            vendas.setEnabled(True)

        # Fim

        vendas.setWindowModality(Qt.WindowModal)
        # Exibe a janela principal

        vendas.showMaximized()

        return True

    def get_table_username(self, numero_mesa):
        sql = """SELECT users.nome from users 
        INNER JOIN mesas ON users.cod=mesas.created_by 
        WHERE mesas.numero={}""".format(numero_mesa)

        print(sql)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return data[0][0]

        return ""

    def get_user(self, numero_mesa, user):

        sql = """SELECT mesas.created_by from mesas 
        INNER JOIN facturacao ON mesas.codfacturacao=facturacao.cod 
        WHERE mesas.numero={} AND mesas.created_by="{}" AND facturacao.finalizado=0
        """.format(numero_mesa, user)

        self.cur.execute(sql)
        dados = self.cur.fetchall()

        if len(dados) > 0:
            return True

        if self.admin:
            return True

        if self.gestor:
            return True

        return False

    # Verifica se a mesa está ocupada ou nao
    def verificar_mesas(self, numero_mesa):
        sql = """SELECT m.numero FROM mesas m INNER JOIN facturacao f ON f.cod=m.codfacturacao 
        WHERE m.numero={} AND f.finalizado=0 """.format(numero_mesa)
        self.cur.execute(sql)
        dados = self.cur.fetchall()

        if len(dados) > 0:
            return True

        return False

    def keyPressEvent(self, event):
        try:
            if event.key() in (Qt.Key_Enter, 16777220):
                if self.cod_line.text() != "":
                    self.codproduto = self.cod_line.text()
                    self.add_record()

            elif event.key() == Qt.Key_Escape:
                self.close()

        except Exception as e:
            print(e)

    def enterEvent(self, evt):

        # try:
        #     self.conn.cmd_refresh(1)
        # except Exception as e:
        #     QMessageBox.critical(self, "Erro na base de dados",
        #                          "Conexão com a Base de dados Perdida!!!\n{}.".format(e))
        if len(self.DADOS_DA_EMPRESA) > 0:

            self.user = self.DADOS_DA_EMPRESA[0]
            self.user_Label.setText("Bem Vindo, {}.".format(self.user))

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
        self.load_button_list()

    # Faz check de mesas ocupadas
    def load_button_list(self):
        for x in range(1, self.numero_mesas + 1):
            if self.verificar_mesas(x) is True:
                self.btn_mesasgroup.button(x).setChecked(self.verificar_mesas(x))

    def novo_item(self):
        pr = NovoProduto(self)
        pr.setModal(True)
        pr.show()

    def verifica_admin(self):
        pass

    def load_config(self):
        sql = """SELECT * FROM config WHERE empresa="{}" """.format(self.empresa)
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

        self.combo_estilo = QComboBox()
        self.combo_estilo.addItems(QStyleFactory.keys())
        self.combo_estilo.activated[str].connect(self.mudar_estilo)
        self.user_Label = QLabel("")
        self.user_Label.setText('Bem Vindo, {} '.format(self.user))
        status = QStatusBar()
        status.addWidget(self.user_Label)
        self.setStatusBar(status)

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

        normal.triggered.connect(lambda: self.setStyleSheet(stylesheet(0)))

        maintool = QToolBar()
        maintool.setContextMenuPolicy(Qt.PreventContextMenu)
        maintool.setMaximumHeight(32)
        maintool.setIconSize(QSize(32, 32))
        maintool.setMovable(False)

        butao_minimizar = QAction(QIcon("./images/icons8-minimize-window-50.png"), "Minimizar", self)
        self.butao_restaurar = QAction(QIcon("./images/icons8-restore-window-50.png"), "Restaurar/Maximizar", self)
        self.butao_restaurar.triggered.connect(self.set_max_normal)
        # self.butao_restaurar.setVisible(False)
        butao_fechar = QAction(QIcon("./images/icons8-close-window-50.png"), "Fechar", self)
        butao_minimizar.triggered.connect(self.showMinimized)
        butao_fechar.triggered.connect(sys.exit)
        self.config = QAction(QIcon("./icons/cofiguracao2.ico"), "Configurações", self)
        self.config.triggered.connect(self.configurar)

        spacer1 = QWidget()
        spacer1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # maintool.addWidget(self.user_Label)
        maintool.addWidget(spacer1)

        maintool.addAction(self.config)
        maintool.addWidget(self.combo_estilo)

        self.tool = QToolBar("Acções")

        self.tool.setContextMenuPolicy(Qt.PreventContextMenu)
        self.tool.setIconSize(QSize(32, 32))
        self.tool.setFixedHeight(48)
        self.tool.setMovable(False)

        segundavia = QAction(QIcon("./icons/stock.ico"), "R&eimprimir\n(F4)", self)
        caixa = QAction(QIcon("./icons/report.ico"), "Caixa\n(F10)", self)
        produtos = QAction(QIcon("./icons/produtos.ico"), "Imprimir\n(F2)", self)
        produtos.triggered.connect(self.imprime_produtos)
        trancar_sistema = QAction(QIcon("./icons/Logout.ico"), "T&rancar\n(F8)", self)
        sobre_o_programa = QAction(QIcon("./icons/users.ico"), "Aplicativo", self)

        self.tool.addAction(segundavia)
        self.tool.addSeparator()
        self.tool.addAction(caixa)
        self.tool.addSeparator()
        self.tool.addAction(trancar_sistema)
        self.cashdrawer_button = QAction(QIcon("./icons/payment.ico"), "&Abrir Gaveta", self)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tool.addWidget(spacer)

        self.tool.addAction(self.cashdrawer_button)
        self.tool.addWidget(QLabel('Data: '))

        calendario = QCalendarWidget()
        self.validade = QDateEdit()
        self.validade.setDate(QDate.currentDate())
        self.validade.setCalendarPopup(True)
        self.validade.setCalendarWidget(calendario)

        self.tool.addWidget(self.validade)

        segundavia.triggered.connect(self.segundavia)
        caixa.triggered.connect(self.fecho_caixa)
        trancar_sistema.triggered.connect(self.trancar_sistema)

        # Ribbon
        home_tab = self._ribbon.add_ribbon_tab("Início")

        reimprimir_pane = home_tab.add_ribbon_pane("Reimprimir")
        reimprimir_pane.add_ribbon_widget(RibbonButton(self, segundavia, True))

        finalizar_pane = home_tab.add_ribbon_pane("Caixa")
        finalizar_pane.add_ribbon_widget(RibbonButton(self, caixa, True))

        produtos_pane = home_tab.add_ribbon_pane("Produtos")
        produtos_pane.add_ribbon_widget(RibbonButton(self, produtos, True))

        sistema_pane = home_tab.add_ribbon_pane("Sistema")
        sistema_pane.add_ribbon_widget(RibbonButton(self, trancar_sistema, True))
        sistema_pane.add_ribbon_widget(RibbonButton(self, butao_fechar, True))

        sobre_tab = self._ribbon.add_ribbon_tab("Extras")
        sobre_pane = sobre_tab.add_ribbon_pane("Sobre")
        sobre_pane.add_ribbon_widget(RibbonButton(self, sobre_o_programa, True))

        style_pane = sobre_tab.add_ribbon_pane("Estilos")
        style_grid = style_pane.add_grid_widget(500)
        style_grid.addWidget(RibbonButton(self, darkorange, False), 0, 0)
        style_grid.addWidget(RibbonButton(self, darkblue, False), 1, 0)
        style_grid.addWidget(RibbonButton(self, darkgreen, False), 2, 0)

        style_grid.addWidget(RibbonButton(self, lightorange, False), 0, 1)
        style_grid.addWidget(RibbonButton(self, lightblue, False), 1, 1)
        style_grid.addWidget(RibbonButton(self, lightgreen, False), 2, 1)

        style_grid.addWidget(RibbonButton(self, dark_style, False), 0, 2)
        style_grid.addWidget(RibbonButton(self, normal, False), 1, 2)
        style_grid.addWidget(self.combo_estilo, 2, 2)

        config_pane = sobre_tab.add_ribbon_pane("Configurações")
        config_pane.add_ribbon_widget(RibbonButton(self, self.config, True))

    def imprime_produtos(self):

        if (self.admin or self.gestor) is False:
            return False

        sql = """SELECT cod, nome FROM familia ORDER BY nome"""
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            html = """
                <!DOCTYPE html>
                    <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <title>Template de Recibos POS</title>
                        </head>
                    
                        <body style="font-size:8px;">

            """

            html += "<center> LISTA DE ITEMS </center>"
            html += "<center>***</center>"
            html += "<hr/>"
            html += "<center align='left'>{}</center>".format(HORA)
            html += "<center align='left'>Usuário: {}</center>".format(self.user)

            html += "<table border='0' width = 80mm style='border: thin;'>"

            for familia in data:
                html += "<tr><td colspan=2>+{}</td><td></td></tr>".format(familia[1])
                sql = """SELECT cod, nome FROM subfamilia WHERE codfamilia="{}" ORDER BY nome """.format(familia[0])
                self.cur.execute(sql)
                data = self.cur.fetchall()
                print(familia[1])
                if len(data) > 0:
                    for subfamilia in data:
                        html += "<tr><td colspan=2>++{}</td><td></td></tr>".format(subfamilia[1])
                        sql = """SELECT p.nome, pd.quantidade FROM produtos p 
                        INNER JOIN produtosdetalhe pd
                        ON p.cod=pd.codproduto 
                        WHERE p.codsubfamilia="{}" ORDER BY p.nome""".format(subfamilia[0])
                        self.cur.execute(sql)
                        data = self.cur.fetchall()
                        if len(data) > 0:
                            for produto in data:
                                html += "<tr><td>{}</td><td>{}</td></tr>".format(produto[1], produto[0])
            html += "</table>"
            html += """
                </body>
            </html>
            """

            printer = QPrinter()
            printer.setPrinterName(self.pos1)
            printer.setResolution(96)
            printer.setPaperSize(QSizeF(self.papel_1,  3276), printer.Millimeter)
            printer.setPageMargins(0, 0, 10, 0, QPrinter.Millimeter)

            document = QTextDocument()
            document.setHtml(html)
            document.setPageSize(QSizeF(printer.pageRect().size()))

            dialog = QPrintDialog()
            document.print_(printer)
            dialog.accept()

            return True
        else:
            return False

    def configurar(self):
        if self.admin:
            from config import Config

            c = Config(self)
            c.setModal(True)
            self.spin_mesas = QSpinBox()
            self.spin_mesas.setRange(1, 1000)
            self.check_criar_ordem = QCheckBox("Criar Ordem antes da Conta")
            self.check_imprimir_ordem = QCheckBox("Imprimir ordem")
            self.check_imprimir_items_apagados = QCheckBox("Imprimir Items apagados")
            c.btn_gravar.clicked.connect(self.save_settings)
            c.form_layout.addRow(QLabel("Nº de Mesas"), self.spin_mesas)
            c.form_layout.addWidget(self.check_criar_ordem)
            c.form_layout.addWidget(self.check_imprimir_ordem)
            c.form_layout.addWidget(self.check_imprimir_items_apagados)
            self.get_settings()
            c.show()

    def save_settings(self):

        settings = QSettings()

        try:
            settings.setValue("MigrogestPOS/mesas", self.spin_mesas.value())
            settings.setValue("MigrogestPOS/imprimir_ordem", self.check_imprimir_ordem.isChecked())
            settings.setValue("MigrogestPOS/exigir_ordem", self.check_criar_ordem.isChecked())
            settings.setValue("MigrogestPOS/imprimir_items_apagados", self.check_imprimir_items_apagados.isChecked())

            settings.sync()
        except Exception as e:
            QMessageBox.warning(self, "Erro de Gravação", "Dados não Gravados.\nErro {}.".format(e))
            return False

        return True

    def get_settings(self):

        settings = QSettings()
        mesas = settings.value("MigrogestPOS/mesas", 1, int)
        self.imprimir_ordem = settings.value("MigrogestPOS/imprimir_ordem", True, bool)
        self.exigir_ordem = settings.value("MigrogestPOS/exigir_ordem", True, bool)
        self.imprimir_items_apagados = settings.value("MigrogestPOS/imprimir_items_apagados", True, bool)

        self.spin_mesas.setValue(int(mesas))
        self.check_imprimir_ordem.setChecked(self.imprimir_ordem)
        self.check_criar_ordem.setChecked(self.exigir_ordem)
        self.check_imprimir_items_apagados.setChecked(self.imprimir_items_apagados)

    def set_max_normal(self):
        if self.isMaximized():
            self.butao_restaurar.setIcon(QIcon("./images/icons8-maximize-window-50.png"))
            self.showNormal()
        else:
            self.butao_restaurar.setIcon(QIcon("./images/icons8-restore-window-50.png"))
            self.showMaximized()

    def trancar_sistema(self):
        self.Login.armazem.setEnabled(False)
        self.Login.empresas.setEnabled(False)
        self.Login.password.clear()
        self.Login.show()

    def fecho_caixa(self):
        from lista_de_caixa import MainWindow

        cx = MainWindow(self)
        cx.showMaximized()

    def segundavia(self):
        sql = """ SELECT * from facturacao WHERE finalizado=1"""
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            QMessageBox.information(self, "Sem documentos", "Não Existe nenhum documento finalizado")
            return

        from segundavia import Cliente

        gravado = Cliente(self)
        gravado.setModal(True)
        gravado.cancelar.setEnabled(self.admin)
        gravado.activar.setEnabled(self.admin)
        gravado.usar_items.setEnabled(False)
        self.limpar_cache()
        gravado.show()

    def gera_codigogeral(self):
        self.codigogeral = "FT" + cd("FT" + "abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")

    def fechar(self):
        self.close()

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

    # Verifica se ja se fez a facturacao ou nao
    def existe(self, mesa, codigo):

        sql = """SELECT m.cod, m.codfacturacao FROM mesas m INNER JOIN facturacao f ON f.cod=m.codfacturacao 
        WHERE m.numero={mesa} AND f.cod="{cod}" """.format(mesa=mesa, cod=codigo)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        print(sql)

        if len(data) == 0:
            print("Codigo nao Existe")
            return False
        else:
            print("codigo Existe")
            return True

    def add_record(self):

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

        # created = QDate.fromString(str(self.validade.text())).toString("yyyy-MM-dd")
        created = QDate.currentDate().toString("yyyy-MM-dd")
        modified = created

        caixa = self.caixa_numero

        modified_by = created_by = self.user

        if self.existe(self.numero_da_mesa, self.codigogeral) is True:

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
                        total=total, lucro=lucro, debito=pago, credito= 0.00, troco=troco, banco=banco,
                        cash=cash, tranferencia=tranferencia, estado=estado,ano=ano,
                        mes=mes, obs=obs, created=created, modified=modified, modified_by=modified_by,
                        created_by=created_by, caixa=caixa)

            sql = """INSERT INTO facturacao (cod, numero, coddocumento ,codcliente, data, custo, subtotal,
            desconto, taxa, total,  lucro, debito, credito,troco, banco, cash, tranferencia, estado, ano, mes, 
            obs, created, modified, modified_by, created_by, caixa) values({value})""".format(value=values)

        print(sql)

        try:
            self.cur.execute(sql)
            return False
        except Exception as e:
             QMessageBox.critical(self, "Erro", "Os seus dados não foram gravados. Erro: {erro}, created: {c} ".format(erro=e, c=created))
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


class SpecialButtonGroup(QButtonGroup):
    buttonDoubleClicked = pyqtSignal()
    clicked = pyqtSignal()

    def __init__(self, *args, **kwargs):
        QButtonGroup.__init__(self, *args, **kwargs)
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.clicked.emit)
        super().buttonClicked.connect(self.checkDoubleClick)

    @pyqtSlot()
    def checkDoubleClick(self):
        if self.timer.isActive():
            self.buttonDoubleClicked.emit()
            self.timer.stop()
        else:
            self.timer.start(250)


if __name__ == '__main__':
    import time
    from utilities import center

    app = QApplication(sys.argv)

    app.setApplicationName(APPLICATION_NAME)
    app.setApplicationVersion(APPLICATION_VERSION)
    app.setOrganizationDomain(ORGANIZATION_DOMAIN)
    app.setOrganizationName(ORGANIZATION_NAME)

    pixmap = QPixmap("./images/black.png")
    splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)
    splash.setMask(pixmap.mask())  # this is usefull if the splashscreen is

    splash.resize(400, 200)

    progressbar = QProgressBar(splash)
    progressbar.setMaximum(10)
    progressbar.setGeometry(0, splash.height() - 20, splash.width() + 50, 1)

    label = QLabel("<p style='color: white;'>Modulo: Restauração</p>", splash)
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

    main_facturacao = Cliente()
    main_facturacao.showMaximized()

    # now kill the spmain_facturacaolashscreen
    splash.finish(main_facturacao)

    sys.exit(app.exec_())