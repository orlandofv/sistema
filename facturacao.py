# -*- coding: utf-8 -*-
"""
Created on Fri Mar 02 23:18:43 2012

@author: lims
"""

from decimal import Decimal
import glob, os
import sys

from PyQt5.QtCore import Qt, QDate, QTimer, QTime, QSettings, QDateTime
from PyQt5.QtGui import QIcon, QFont, QPixmap, QKeySequence as QKSec

from GUI.RibbonButton import RibbonButton
from GUI.RibbonWidget import *

from sortmodel import MyTableModel
from utilities import codigo as cd
from pricespinbox import *

from facturacao_classe import Facturacao
from documentos import Cliente as doc
from lista_de_recibos import MainWindow as nao_pagas
import loginform_vendas as login
import recibos
from utilities import stylesheet
from tabela_de_produtos import ListaDeProdutos

APPLICATION_NAME = "falcão".upper()
APPLICATION_VERSION = "2021 M8"
ORGANIZATION_DOMAIN = "www.samtics.co.mz"
ORGANIZATION_NAME = "Microgest Lda"
MODULO_NAME = "Factura Pro"


class Cliente(QMainWindow):
    estado_do_fecho_do_programa = False

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

    lista_de_produtos_relacionados = []

    # produtosdetalhe table fields
    preco__do_produto = 0
    quantidade_do_produto = 0
    custo_do_produto = 0
    desconto_do_produto = 0
    taxa_do_produto = 0
    subtotal_do_produto = 0
    custo_total_do_produto = 0
    total_do_produto = 0
    lucro_do_produto = 0
    # produtosdetalhe table fields

    # Primary key -- Random string that begins with FT
    codigogeral = "FT" + cd("FT" + "abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")
    # Primary key

    # Foreign Keys
    codigo_do_documento = "DC20184444444"
    codigo_do_cliente = "CL20181111111"
    codigo_do_armazem = "AR201875cNP1"
    codigo_da_caixa = ""
    # Foreign Keys

    # important facturacao table fields
    numero_do_documento = 1
    data__do_documento = "1981-09-30"
    custo_do_documento = 0
    subtotal_do_documento = 0
    desconto_do_documento = 0
    taxa_do_documento = 0
    total_do_documento = 0
    debito_do_documento = 0
    credito_do_documento = 0
    saldo_do_documento = 0
    troco_do_documento = 0
    banco_do_documento = 0
    cash_do_documento = 0
    tranferencia_do_documento = 0
    estado_documento = 0
    extenso_documento = ""
    ano_documento = 1981
    mes_documento = 9
    obs_documento = ""
    editar_dados_de_facturacao = False

    # facturacao table fields

    def __init__(self, parent=None):
        super(Cliente, self).__init__(parent)

        # Variavel que tranca o programa depois de algum tempo (em sengundos)
        self.fechar_timer = 300 # Tempo em sengundos

        self.caminho_python = None # Permite Impressão pelo LibreOffice
        self.pos1 = None
        self.pos2 = None
        self.copias_pos1 = None
        self.copias_pos2 = None
        self.impressora1 = None
        self.impressora2 = None
        self.totalgeral = Decimal(0)

        self.codigogeral = "FT" + cd("FT" + "abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")
        self.codcliente = "CL20181111111"
        self.cod_produto = ""
        self.coddocumento = "DC20184444444"
        self.custoproduto = 0.00
        self.valortaxa = 0.00
        self.current_id = ""
        self.foto_produto_label = ""
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

        login.MODULO = "facturacao"
        self.setHidden(True)
        self.Login = login.Login(self)
        self.Login.encheempresas()
        self.Login.setModal(True)
        self.Login.showFullScreen()

        self.setStyleSheet(stylesheet(0))

    def trancar_sistema(self):
        self.Login.armazem.setEnabled(False)
        self.Login.empresas.setEnabled(False)
        self.Login.password.clear()
        self.Login.show()

    def init_ribbon(self):
        self.accoes()

    def ui(self):

        self.label_total = QLabel("0.00")

        self.label_total.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        boldFont = QFont('Consolas', 18)
        boldFont.setBold(True)
        self.label_total.setFont(boldFont)

        clientegrupo = QWidget()
        clientegrupo.setVisible(False)
        clientegrupo.setMaximumHeight(70)
        documentogrupo = QWidget()
        documentogrupo.setVisible(False)
        documentogrupo.setMaximumHeight(70)
        detalhesgrupo = QWidget()

        self.tabela = QTableView(self)
        self.tabela.clicked.connect(self.clicked_slot)
        self.tabela.doubleClicked.connect(self.editar_dados)
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

        self.butao_editardetalhe = QPushButton(QIcon("./icons/edit.ico"), "Editar Items")

        self.butao_editardetalhe.setDefault(True)
        self.butao_editardetalhe.setMaximumWidth(120)
        self.butao_editardetalhe.setMinimumWidth(120)
        self.butao_editardetalhe.clicked.connect(self.editar_dados)
        self.butao_apagarItem = QPushButton(QIcon("./icons/remove.ico"), "Eliminar Linha")
        self.butao_apagarItem.setMaximumWidth(120)
        self.butao_apagarItem.setMinimumWidth(120)
        self.butao_apagarItem.clicked.connect(self.removerow)
        self.butao_apagarItem.setShortcut(QKSec.Delete)
        self.butao_apagarItem.setEnabled(False)
        self.butao_apagarTudo = QPushButton(QIcon("./icons/removeall.ico"), "Eliminar Tudo")
        self.butao_apagarTudo.setMinimumWidth(120)
        self.butao_apagarTudo.setMaximumWidth(120)
        self.butao_apagarTudo.clicked.connect(self.removeall)
        self.butao_apagarTudo.setEnabled(False)

        self.line_codigoproduto = QLineEdit()
        self.line_codigoproduto.setObjectName("codigo")
        self.line_codigoproduto.setMaxLength(255)
        self.butao_produto = QPushButton(QIcon("./icons/add.ico"), "")

        regex = QRegExp("^(?:\d+\.?\d*|\d*\.?\d+)*$")
        validator = QRegExpValidator(regex)

        lineedit = QLineEdit()
        lineedit.setValidator(validator)

        self.tabela_produtos = ListaDeProdutos(self)

        self.validade = QDateEdit(self)

        self.validade.setDate(QDate.currentDate())
        cal = QCalendarWidget()
        self.validade.setCalendarPopup(True)
        self.validade.setCalendarWidget(cal)

        toolbox = QToolBox(self)
        toolbox.addItem(self.tabela_produtos, "Lista de Produtos Locais")
        # toolbox.addItem(self.tabela_produtos_remotos, "Lista de Produtos Remotos")

        self.foto_label = QLabel()
        self.foto_produto_label_frame = QGroupBox()
        self.foto_produto_label_frame.setFixedSize(128, 128)

        self.foto_produto_label_layout = QVBoxLayout()
        self.foto_produto_label_layout.addWidget(self.foto_label)
        self.foto_produto_label_frame.setLayout(self.foto_produto_label_layout)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        btn_lay = QHBoxLayout()
        btn_lay.setSpacing(0)
        btn_lay.setContentsMargins(0, 0, 0, 0)
        btn_lay.addWidget(self.butao_editardetalhe)
        btn_lay.addWidget(spacer)
        btn_lay.addWidget(self.butao_apagarItem)
        btn_lay.addWidget(self.butao_apagarTudo)

        ly = QVBoxLayout()
        ly.setSpacing(1)
        ly.setContentsMargins(0, 0, 0, 0)
        ly.addWidget(QLabel("Código/Código de Barras"))
        ly.addWidget(self.line_codigoproduto)

        # self.tabela.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label_total_items = QLabel("")
        ly.addWidget(self.tabela)
        ly.addWidget(self.label_total_items)
        ly.addLayout(btn_lay)

        detalhesgrupo.setLayout(ly)

        controlslayout = QVBoxLayout()
        controlslayout.addWidget(detalhesgrupo)

        splitter = QSplitter(Qt.Horizontal)
        controlswidget = QWidget()

        controlswidget.setLayout(controlslayout)

        splitter.addWidget(controlswidget)
        splitter.addWidget(toolbox)
        # self.tabela_produtos.setParent(self)

        mainlayout = QVBoxLayout()

        boldFont2 = QFont('Consolas', 12)
        boldFont2.setBold(True)

        produtowidget = QWidget()
        self.user_Label = QLabel()
        self.armazem = QLabel("Armazém: {}".format(self.nome_armazem))
        self.armazem.setFont(boldFont2)
        self.user_Label.setFont(boldFont2)
        self.data = QLabel()
        self.data.setFont(boldFont2)

        provlayout = QVBoxLayout()
        provlayout.addWidget(self.user_Label)
        provlayout.addWidget(self.data)
        provlayout.addWidget(self.armazem)

        produtowidget.setLayout(provlayout)

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

        headerlayout = QHBoxLayout()
        headerlayout.addWidget(produtowidget)

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

        controlswidget.setLayout(buttonslayout)

        headerWidget = QGroupBox()
        headerWidget.setFixedHeight(128)

        headerWidget.setLayout(headerlayout)

        hp_lay = QHBoxLayout()

        hp_lay.addWidget(headerWidget)
        hp_lay.addWidget(self.foto_produto_label_frame)

        mainlayout.addLayout(hp_lay)
        mainlayout.addWidget(splitter)

        centralwidget = QWidget()
        centralwidget.setLayout(mainlayout)
        self.setCentralWidget(centralwidget)

        self.setWindowTitle("Microgest Facturação - {}".format(self.empresa))

        self.load_config()

        self.calcula_total_geral()
        self.fill_table()

        timer = QTimer(self)
        timer.timeout.connect(self.horas)
        timer.start(1000)

        self.setWindowIcon(QIcon("logo.ico"))

        # Calls the Invoice creation module
        self.facturacao_modulo = Facturacao()
        self.facturacao_modulo.conn = self.conn
        self.facturacao_modulo.cur = self.cur

        self._ribbon = RibbonWidget(self)
        self.addToolBar(self._ribbon)
        self.init_ribbon()

        # self.setStyleSheet(stylesheet(0))

    def mostrar_configuracoes(self):
        from config import Config

        c = Config(self)
        c.setModal(True)
        c.show()

    def mudar_style(self, style):
        QApplication.setStyle(QStyleFactory.create(style))

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

        butao_fechar = QAction(QIcon("./images/icons8-close-window-50.png"), "Fechar\n(ESC)", self)
        butao_fechar.triggered.connect(self.fechar_aplicativo)
        self.config = QAction(QIcon("./icons/cofiguracao2.ico"), "Configurações", self)
        self.config.triggered.connect(self.mostrar_configuracoes)

        spacer1 = QWidget()
        spacer1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.gravar = QAction(QIcon("./icons/Dollar.ico"), "P&agamento\n(F2)", self)
        self.recibo = QAction(QIcon("./icons/Properties.ico"), "Reci&bo\n(F3)", self)
        self.receitas_despesas = QAction(QIcon("./icons/refresh.ico"), "Receitas\n(F6)", self)
        self.receitas_despesas.setToolTip("&Receitas e Despesas")
        self.gravardoc = QAction(QIcon("./icons/save.ico"), "&Gravar\n(F7)", self)
        self.gravardoc.setToolTip("Gravar documento actual")
        self.abrirdoc = QAction(QIcon("./icons/open.ico"), "&Abrir\n(F11)", self)
        self.segundavia = QAction(QIcon("./icons/stock.ico"), "R&eimprimir\n(F4)", self)
        self.caixa = QAction(QIcon("./icons/report.ico"), "&Caixa\n(F10)", self)
        self.caixa.setToolTip("Fechar/Imprimir Caixa")
        self.facturasnaopagas = QAction(QIcon("./icons/coin_stacks_copper_remove.ico"), "&Não pagas\n(F9)", self)
        self.facturasnaopagas.setToolTip("Ver Facturas não pagas\n(F5)")
        self.trancarsistema = QAction(QIcon("./icons/Logout.ico"), "T&rancar\n(F8)", self)
        self.sobre_o_programa = QAction(QIcon("./icons/users.ico"), "Aplicativo", self)

        self.adicionar_remover_iva = QAction(QIcon("./icons/add.ico"), "+\n&TAXA", self)
        self.adicionar_remover_iva.setCheckable(True)
        self.adicionar_remover_iva.triggered.connect(self.adicionar_ou_remover_taxa)

        cashdrawer_button = QAction(QIcon("./icons/payment.ico"), "&Abrir\n(F12)", self)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.gravar.triggered.connect(self.facturar)
        self.recibo.triggered.connect(self.criar_recibo)
        self.receitas_despesas.triggered.connect(self.receitas)
        self.abrirdoc.triggered.connect(self.abrir_documento)
        self.gravardoc.triggered.connect(self.grava_transacao)
        self.segundavia.triggered.connect(self.segunda_via)
        self.caixa.triggered.connect(self.fecho_caixa)
        self.facturasnaopagas.triggered.connect(self.facturas_nao_pagas)
        self.trancarsistema.triggered.connect(self.trancar_sistema)
        self.sobre_o_programa.triggered.connect(self.mostrar_sobre)
        # cashdrawer_button.triggered.connect(lambda: open_cash_drawer('EPSON TM-T20-42C Receipt'.encode()))

        # Ribbon
        home_tab = self._ribbon.add_ribbon_tab("Início")
        finalizar_pane = home_tab.add_ribbon_pane("Finalizar")
        finalizar_pane.add_ribbon_widget(RibbonButton(self, self.gravar, True))

        reimprimir_pane = home_tab.add_ribbon_pane("Reimprimir")
        reimprimir_pane.add_ribbon_widget(RibbonButton(self, self.segundavia, True))

        finalizar_pane = home_tab.add_ribbon_pane("Facturas")
        finalizar_pane.add_ribbon_widget(RibbonButton(self, self.recibo, True))
        finalizar_pane.add_ribbon_widget(RibbonButton(self, self.facturasnaopagas, True))

        documentos_pane = home_tab.add_ribbon_pane("Documentos")
        documentos_pane.add_ribbon_widget(RibbonButton(self, self.abrirdoc, True))
        documentos_pane.add_ribbon_widget(RibbonButton(self, self.gravardoc, True))

        receitas_pane = home_tab.add_ribbon_pane("Receitas")
        receitas_pane.add_ribbon_widget(RibbonButton(self, self.receitas_despesas, True))

        caixa_pane = home_tab.add_ribbon_pane("Caixa")
        caixa_pane.add_ribbon_widget(RibbonButton(self, self.caixa, True))

        gaveta_pane = home_tab.add_ribbon_pane("Gaveta")
        gaveta_pane.add_ribbon_widget(RibbonButton(self, cashdrawer_button, True))

        sistema_pane = home_tab.add_ribbon_pane("Sistema")
        sistema_pane.add_ribbon_widget(RibbonButton(self, self.trancarsistema, True))
        sistema_pane.add_ribbon_widget(RibbonButton(self, butao_fechar, True))

        iva_pane = home_tab.add_ribbon_pane("+/- TAXA")
        iva_pane.add_ribbon_widget(RibbonButton(self, self.adicionar_remover_iva, True))

        home_tab.add_spacer()

        total_pane = home_tab.add_ribbon_pane("")

        label_grid = total_pane.add_grid_widget(500)
        label_grid.addWidget(QLabel("Subtotal"), 0, 0)
        label_grid.addWidget(QLabel("IVA"), 1, 0)
        label_grid.addWidget(QLabel("Desconto"), 2, 0)
        total_label = QLabel("Total")
        total_label.setFont(self.label_total.font())
        label_grid.addWidget(total_label, 3, 0)

        grid = total_pane.add_grid_widget(500)
        grid.addWidget(self.labelsubtotal, 0, 0)
        grid.addWidget(self.labeltaxa, 1, 0)
        grid.addWidget(self.labeldesconto, 2, 0)
        grid.addWidget(self.label_total, 3, 0)

        sobre_tab = self._ribbon.add_ribbon_tab("Extras")
        sobre_pane = sobre_tab.add_ribbon_pane("Sobre")
        sobre_pane.add_ribbon_widget(RibbonButton(self, self.sobre_o_programa, True))

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
        style_grid.addWidget(self.validade, 2, 2)

        config_pane = sobre_tab.add_ribbon_pane("Configurações")
        config_pane.add_ribbon_widget(RibbonButton(self, self.config, True))

        self.calcula_total_geral()

    def mostrar_sobre(self):
        return QMessageBox.about(self, "Sobre o Programa",
                          """
                          <p>Orlando Filipe Vilanculos, 2018-2020 todos direitos reservados</p>
                          <hr>
                          <a href="#">Clique aqui para Licença</>
                          """)

    def adicionar_ou_remover_taxa(self):
        if self.adicionar_remover_iva.isChecked():
            self.adicionar_remover_iva.setText("-\nTAXA")
            self.adicionar_remover_iva.setIcon(QIcon("./icons/cancel.ico"))
        else:
            self.adicionar_remover_iva.setText("+\nTAXA")
            self.adicionar_remover_iva.setIcon(QIcon("./icons/add.ico"))

    def get_cod_produto(self, codigo):
        """
        Procura o produto na base do codigo ou código de baarras e  retorna codigo
        :param codigo:
        :return:
        """
        sql = """SELECT cod from produtos WHERE cod="{cod}" or cod_barras="{cod_b}" """.format(cod=codigo,
                                                                                               cod_b=codigo)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return data[0][0]
        else:
            return False

    def validar_dados(self):
        if self.line_codigoproduto.text() == "":
            return False

        if self.line_codigoproduto.text() == "" or self.codarmazem == "":
            return False

        codproduto = self.get_cod_produto(self.line_codigoproduto.text())

        self.cod_produto = codproduto
        self.adicionar_item()

        return True

    def keyPressEvent(self, event):

        try:
            if event.key() in (Qt.Key_Enter, 16777220):
                self.validar_dados()

            if event.key() == Qt.Key_F2:
                if self.gravar.isEnabled():
                    self.facturar()

            if event.key() == Qt.Key_F3:
                if self.recibo.isEnabled():
                    self.criar_recibo()

            if event.key() == Qt.Key_F4:
                if self.segundavia.isEnabled():
                    self.segunda_via()

            if event.key() == Qt.Key_F5:
                self.fill_table()

            if event.key() == Qt.Key_F6:
                if self.receitas_despesas.isEnabled():
                    self.receitas()

            if event.key() == Qt.Key_F7:
                if self.gravardoc.isEnabled():
                    self.grava_transacao()

            if event.key() == Qt.Key_F8:
                if self.trancarsistema.isEnabled():
                    self.trancar_sistema()

            if event.key() == Qt.Key_F9:
                if self.facturasnaopagas.isEnabled():
                    self.facturas_nao_pagas()

            if event.key() == Qt.Key_F10:
                if self.caixa.isChecked():
                    self.fecho_caixa()

            if event.key() == Qt.Key_F11:
                if self.abrirdoc.isEnabled():
                    self.abrir_documento()

            if event.key() == Qt.Key_Escape:
                self.close()

            if event.key() == Qt.Key_F12:
                self.removeall()

            if event.key() == Qt.Key_F1:
                self.trancar_sistema()

            event.ignore()

        except Exception as e:
            print(e)

    def set_max_normal(self):
        if self.isMaximized():
            self.butao_restaurar.setIcon(QIcon("./images/icons8-maximize-window-50.png"))
            self.showNormal()
        else:
            self.butao_restaurar.setIcon(QIcon("./images/icons8-restore-window-50.png"))
            self.showMaximized()

    # Requiscaoes internas
    def receitas(self):

        from lista_de_receitas import ListaDeReceitas
        receitas = ListaDeReceitas(self)
        receitas.showMaximized()

    # Modulo que cria a Lista de Precos
    def lista_precos(self, cod):
        sql = """SELECT preco, preco1, preco2, preco3, preco4 from produtos WHERE cod="{}" """.format(cod)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        lista = []
        if len(data) > 0:
            for items in data:
                for item in items:
                    if item > 0.00:
                        lista.append(str(item))
        return lista

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

    def fecho_caixa(self):

        if self.tabelavazia() is False:
            QMessageBox.warning(self, "Transação Activa", "Por favor termine a transação actual.")
            return False

        from lista_de_caixa import MainWindow

        cx = MainWindow(self)
        cx.showMaximized()

        return True

    def horas(self):
        self.data.setText("{}  {} | Documento: {}".format(QDate.currentDate().toString("dd-MM-yyyy"),
                                                          QTime.currentTime().toString(), self.codigogeral))

        self.fechar_timer -= 1
        if self.fechar_timer == 0:
            self.trancar_sistema()

    def facturar(self):

        if self.tabelavazia() is True:
            QMessageBox.warning(self, "Sem dados", "Insira dados para criar documentos.")
            return False

        from facturas import Cliente

        factura = Cliente(self, titulo="Facturação", imagem="./icons/Dollar.ico")

        factura.setModal(True)
        self.limpar_cache()
        factura.setMaximumSize(400, 400)
        factura.setMaximumWidth(400)
        factura.show()

        return True

    def facturas_nao_pagas(self):
        np = nao_pagas(self)
        np.setWindowTitle('Lista de Facturas não Pagas')
        np.showMaximized()

    # Metodo que abre documentos Fechados
    def abrir_documento(self):

        if self.tabelavazia() is False:
            QMessageBox.warning(self, "Transação Activa", "Por favor termine a transação actual.")
            return False

        sql = """ select facturacao.cod from facturacao INNER JOIN facturacaodetalhe 
        ON facturacao.cod=facturacaodetalhe.codfacturacao
        WHERE facturacao.finalizado=0 and facturacaodetalhe.codarmazem="{}" GROUP BY facturacao.cod""".format(self.codarmazem)

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

        if ok:

            if text == "":
                text = "Sem Nome: {}".format(QDateTime.currentDateTime().toString('dd-MM-yyyy HH:mm:ss'))
            else:
                text += ": {}".format(QDateTime.currentDateTime().toString('dd-MM-yyyy HH:mm:ss'))

            sql_facturcao = """UPDATE facturacao SET nome="{}" WHERE cod="{}" """.format(text, self.codigogeral)

            try:
                self.cur.execute(sql_facturcao)
                self.conn.commit()

                QMessageBox.information(self, "Sucesso", "Documento com o nome {}, gravado com Sucesso.".format(text))
            except Exception as e:
                self.conn.rollback()
                QMessageBox.warning(self, "Falha", "Documento não foi gravado")
                return False

            self.gera_codigogeral()
            self.fill_table()

            return True
        else:
            QMessageBox.warning(self, "Falha", "Documento não foi gravado")

            return False

    def reset_labels(self):
        self.label_total.setText("0.00")
        self.labelsubtotal.setText("0.00")
        self.labeldesconto.setText("0.00")
        self.labeltaxa.setText("0.00")
        self.labeltaxa.setText("0.00")
        self.labeldesconto.setText("0.00")
        self.labelsubtotal.setText("0.00")

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

    def criar_recibo(self):

        recibo = recibos.MainWindow(self)
        recibo.setWindowTitle('Criação de Recibos')
        recibo.setModal(True)
        self.limpar_cache()
        recibo.showMaximized()

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
    # Enche a combobox taxas com Lista de taxas
    def enchetaxa(self):

        sql = """SELECT valor FROM taxas"""

        self.cur.execute(sql)
        data = self.cur.fetchall()

        taxas = []

        if len(data) > 0:
            for item in data:
                taxa = Decimal(item[0])
                taxas.append(str(taxa))

        return taxas

    # Acontence quando clicas o tabela
    def clicked_slot(self, index):

        row = int(index.row())
        indice= self.tm.index(row, 1)
        self.current_id = indice.data()
        self.cod_produto = self.current_id

        self.line_codigoproduto.setText(self.cod_produto)
        self.line_codigoproduto.setFocus()
        self.line_codigoproduto.selectAll()

        return self.cod_produto

    def get_produtos_detalhe(self, cod_produto, cod_facturacao):

        if cod_produto == "" or cod_produto is None:
            return False

        sql = """SELECT preco, quantidade, taxa, desconto, subtotal, total FROM facturacaodetalhe 
        WHERE codproduto="{}" AND codfacturacao="{}" """.format(cod_produto, cod_facturacao)

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        if len(data) > 0:
            return data[0][0], data[0][1], data[0][2], data[0][3], data[0][4]
        else:
            return None

    def editar_dados(self):

        if self.current_id == "":
            QMessageBox.warning(self, "Erro", "Escolha dado para editar na tabela")
            return

        preco, quantidade, taxa, desconto, subtotal = self.get_produtos_detalhe(self.current_id, self.codigogeral)

        print("Detalhes: ", preco, quantidade, taxa, desconto, subtotal)
        if taxa == 0:
            valor_taxa = 0
        else:
            try:
                valor_taxa = Decimal(taxa)/(Decimal(desconto) + Decimal(subtotal)) * 100
            except Exception:
                valor_taxa = 0

        total_bruto = Decimal(preco) * Decimal(quantidade)
        try:
            desconto_ = Decimal(desconto)/total_bruto * 100
        except Exception:
            desconto_ = 0

        print("Desconto", desconto_, total_bruto)

        # Convertemos o valor para inteiro
        valor_taxa = int(valor_taxa)

        from editar_dados import EditarValores

        v = EditarValores(self)
        v.cod_produto = self.current_id
        v.setModal(True)
        v.cur = self.cur
        v.lista_de_precos.addItems(self.lista_precos(self.current_id))
        v.nome_produto.setPlainText(self.facturacao_modulo.get_nome_produto(self.current_id))
        v.taxa_produto.addItems(self.enchetaxa())
        # v.preco_produto.setEnabled(self.admin)
        # v.desconto_produto.setEnabled(self.admin)
        # v.taxa_produto.setEnabled(self.admin)
        # v.lista_de_precos.setEnabled(self.admin)

        v.preco_produto.setValue(Decimal(preco))
        v.quantidade_produto.setValue(Decimal(quantidade))
        v.taxa_produto.setCurrentText(str(valor_taxa))
        v.desconto_produto.setValue(desconto_)

        v.quantidade_produto.setFocus()

        self.editar_dados_de_facturacao = True
        v.show()

    def get_foto(self, codproduto):
        sql = "SELECT foto from produtos WHERE cod='{}'".format(codproduto)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return data[0][0]

        return ""

    # Adiciona Linha de produto na Base de dados
    def adicionar_item(self):
        """
        Adiciona Linha de produto na Base de dados
        """
        print(self.get_foto(self.cod_produto))
        self.mostrar_foto(self.get_foto(self.cod_produto))

        if self.calcular_dados_detalhados(self.cod_produto) is True:
            self.add_record()
    
    def mostrar_foto(self, foto):
        pixmap = QPixmap(foto)
        pixmap.scaled(128, 128, Qt.KeepAspectRatio)
        self.foto_label.setPixmap(pixmap)
        self.foto_label.setScaledContents(True)
        self.foto_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

    def aumenta_taxa(self, codfacturacao):
        sql =  """SELECT * from facturacaodetalhe WHERE codfacturacao="{}" """.format(codfacturacao)
        self.cur.execute(sql)

        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                # Obtemos a percentagem da taxa taxa = valor_taxa / (quantidade * preco)
                taxa = item[8] / (item[5]*item[4])

                # Adicionamos a taxa no preco = preco + preco * taxa
                preco = item[4] + item[4] * taxa

                # Computarizar percentagem do desconto.... desconto =  deconto / (desconto +
                desconto = item[7] / (item[7] + item[9])

                # subtotal = preco * quantidade - desconto
                subtotal_bruto = preco * item[5]
                subtotal =  subtotal_bruto - subtotal_bruto * desconto

                # Valor da taxa
                valor_taxa = subtotal * taxa
                total = subtotal + taxa

                lucro = subtotal - item[3]

                self.facturacao_modulo.actualizar_detalhes = True
                cod_produto = item[2]
                self.facturacao_modulo.codproduto = cod_produto
                # self.custo_do_produto = Decimal(self.custo_do_produto)
                self.preco_unitario = Decimal(self.preco)
                # self.quantidade_unitario = Decimal(self.quantidade_unitario)
                self.desconto_do_produto = Decimal(desconto)
                self.taxa_do_produto = Decimal(valor_taxa)
                self.subtotal_do_produto = Decimal(subtotal)
                self.total_do_produto = Decimal(total)
                self.lucro_do_produto = Decimal(lucro)

                self.add_record()

            return True

        return False

    def calcular_dados_detalhados(self, cod_produto):
        """
        calcula valores para a tabela produtosdetalhe
        :param cod_produto: Codigo do produto da tabela produtos
        :return: True se os calculos forem correctos, False caso contrario
        """

        # Gets the cod, preco, custo, foto, nome, quantidade e codtaxa of the product
        detalhes = self.facturacao_modulo.get_produto_detalhe(cod_produto, self.codarmazem)

        if len(detalhes) == 0:
            return False

        # Novos dados
        self.facturacao_modulo.actualizar_detalhes = False

        self.preco_unitario = detalhes[1]
        self.custoproduto = detalhes[2]
        self.quantidade_existente = detalhes[5]
        self.taxa_do_produto = detalhes[6]
        self.quantidade_unitario = 1

        # se a configuração imposto incluso for True divide o valor por 1.17
        if self.imposto_incluso:
            self.preco_unitario = detalhes[1] / Decimal(1.17)

        self.subtotal_do_produto = self.preco_unitario * self.quantidade_unitario
        self.custo_do_produto = str(self.custoproduto)
        self.lucro_do_produto = self.subtotal_do_produto -  self.custoproduto * self.quantidade_unitario
        # O Valor da taxa é um número inteiro por isso divididos por 100
        taxa = Decimal(self.facturacao_modulo.get_valor_taxa(detalhes[6])) / 100
        self.valortaxa = self.subtotal_do_produto * taxa
        self.desconto_do_produto = 0
        self.total_do_produto = str(self.subtotal_do_produto + self.valortaxa)

        self.preco_unitario = str(self.preco_unitario)
        self.quantidade_existente = str(self.quantidade_existente)
        self.subtotal_do_produto = str(self.subtotal_do_produto)
        self.taxa_do_produto = str(self.valortaxa)
        self.lucro_do_produto = str(self.lucro_do_produto)

        return True

    # Busca o codigo do produto baseando no produto seleccionado
    def getcodproduto(self, nome_produto, cod_armazem):

        sql = """select produtos.cod, produtos.preco, produtos.custo, produtos.foto, produtos.nome, 
        produtosdetalhe.quantidade, produtos.codtaxa from produtos INNER JOIN produtosdetalhe ON
        produtos.cod=produtosdetalhe.codproduto WHERE produtos.cod= "{nome}"
        or produtos.cod_barras = "{cod}" and produtosdetalhe.codarmazem="{armazem}" 
        """.format(nome=nome_produto, cod=nome_produto, armazem=cod_armazem)

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        if len(data) > 0:

            self.cod_produto = "".join(data[0][0])
            if self.alterar_de_preco is False:
                self.combo_preco.clear()
                print("Lista de Precos: ", self.lista_precos(self.cod_produto))
                self.combo_preco.addItems(self.lista_precos(self.cod_produto))

            self.preco_unitario = Decimal(data[0][1])
            self.custoproduto = Decimal(data[0][2])
            self.quantidade_unitario = 1.00
            self.combo_produto.setCurrentText("".join(data[0][4]))
            self.quantidade_existente = Decimal(data[0][5])
            self.getvalortaxa(data[0][6])
            self.line_codigoproduto.setText(self.cod_produto)

            try:
                self.foto_produto_label = str("".join(data[0][3]))
                pixmap = QPixmap(self.foto_produto_label)
                pixmap.scaled(128, 128, Qt.KeepAspectRatio)
                self.foto_label.setPixmap(pixmap)
                self.foto_label.setScaledContents(True)
                self.foto_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
            except:
                self.foto_produto_label = ""
                pixmap = QPixmap(self.foto_produto_label)
                self.foto_label.setPixmap(pixmap)
        else:
            self.cod_produto = ""
            self.custoproduto = Decimal(0.00)

    def verifica_existencia(self):
        sql = """select produtos.cod, produtosdetalhe.quantidade, produtos.tipo FROM produtos 
                INNER JOIN produtosdetalhe ON produtos.cod=produtosdetalhe.codproduto WHERE  produtos.cod= "{nome}" 
                and produtosdetalhe.codarmazem="{codarmazem}"
                GROUP BY produtos.cod """.format(nome=self.line_codigoproduto.text(),
                                                 cod=self.line_codigoproduto.text(), codarmazem=self.codarmazem)

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        if len(data) > 0:
            for item in data:
                self.quantidade_existente = Decimal(item[1])
                self.tipo_produto = item[2]

    # Busca o valor da taxa baseando no nome seleccionado
    def getvalortaxa(self, codtaxa):
        sql = """SELECT valor FROM taxas WHERE cod="{codtaxa}" """.format(codtaxa=codtaxa)

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]
        if len(data) > 0:
            for item in data[0]:
                self.valortaxa = Decimal(item)
        else:
            self.valortaxa = Decimal(0.00)

    def closeEvent(self, event):

        if self.fechar_aplicativo() is False:
            event.ignore()
        else:
            self.cur.close()
            self.conn.close()
            self.limpar_cache()
            sys.exit()

    def limpar_cache(self):

        try:
            for f in glob.glob("*.pdf"):
                os.remove(f)
        except Exception as e:
            print(e)

    def fechar_aplicativo(self):
        if self.existe(self.codigogeral) is True:
            if QMessageBox.question(self, "Fechar Programa", "Documento não Finalizado.\n"
                                                          "Deseja gravar e fechar o programa?") == QMessageBox.Yes:

                text = "Auto Gravado: {}".format(QDateTime.currentDateTime().toString('dd-MM-yyyy HH:mm:ss'))

                sql_facturcao = """UPDATE facturacao SET nome="{}" WHERE cod="{}" """.format(text, self.codigogeral)

                self.cur.execute(sql_facturcao)
                self.conn.commit()

                self.salva_estado_posetivo_do_aplicativo()
                sys.exit()
            else:
                return self.salva_estado_negativo_do_aplicativo()
        else:
            self.salva_estado_posetivo_do_aplicativo()
            sys.exit()

    def validacaodetalhes(self):

        if self.cod_produto == "":
            # QMessageBox.information(self, "Erro de Produto/Serviço", "Entre o Produto/Serviço")
            self.line_codigoproduto.setFocus()
            return False
        else:
            # self.combo_cliente.setEnabled(False)
            self.combo_documento.setEnabled(False)

            return True

    # Verifica se ja se fez a facturacao ou nao
    def existe(self, codigo):
        """"""
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

    def verifica_relacao(self, codproduto, codarmazem):
        """Verifies if the product is related with other products"""

        self.lista_de_produtos_relacionados = []
        self.quantidade_relacionado = Decimal(0)
        self.fraccao = Decimal(0)

        sql = """SELECT produtosdetalhe.quantidade, relacoes.quantidade1, relacoes.quantidade2, 
        relacoes.codproduto2 FROM produtosdetalhe 
        INNER JOIN relacoes ON produtosdetalhe.codproduto=relacoes.codproduto1 
        WHERE produtosdetalhe.codproduto="{}" AND produtosdetalhe.quantidade<=0 
        AND produtosdetalhe.codarmazem="{}" order by relacoes.cod """.format(codproduto, codarmazem)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:

            for item in data:

                # Obtemos a quantidade de cada produto relacionado
                quantidade = self.get_quatidade_produto_relacionado(item[3])

                # Obtemos a fracao para ver a existencia
                fraccao = Decimal(item[2]) / Decimal(item[1])

                result = quantidade >= fraccao

                if result is True:
                    self.quantidade_relacionado = quantidade
                    self.fraccao = fraccao
                    return True

        return False

    def get_quatidade_produto_relacionado(self, codporduto2):
        """Verifica a quantidade do produto relacionado"""

        sql = """SELECT quantidade from produtosdetalhe WHERE codproduto="{}" """.format(codporduto2)
        self.cur.execute(sql)
        dados = self.cur.fetchall()

        if len(dados) > 0:
            return Decimal(dados[0][0])
        else:
            return Decimal(0)

    def calcular_quantidade_de_relacoes(self, codproduto, codarmazem, quantidade):

        if self.verifica_relacao(codproduto, codarmazem) is True:
            for item in self.lista_de_produtos_relacionados:
                quantidade
        else:
            print("Produto não tem relação")
            return False

    def compara_quantidades(self, codproduto, codfacturacao):
        """Compara as quantidades existentes na Base de Dados e as quantidades na fila de Vendas/Facturacao"""

        sql_facturacao = """SELECT quantidade FROM facturacaodetalhe WHERE codproduto="{}" and codfacturacao="{}" 
        """.format(codproduto, codfacturacao)
        self.cur.execute(sql_facturacao)
        data = self.cur.fetchall()

        if len(data) > 0:
            return Decimal(data[0][0]) < Decimal(self.quantidade_existente)

        return True

    def get_tipo_produto(self, codproduto):
        """
        Verifica o tipo de item se é produto ou servico
        """

        sql = """SELECT tipo from produtos WHERE cod="{cod}" or cod_barras="{cod_b}"  """.format(cod=codproduto, cod_b=codproduto)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        # Damos prioridade ao produto
        tipo = 0

        if len(data) > 0:
            tipo = int(data[0][0])

        return tipo

    def add_record(self):

        validade = self.validade.date().toString("yyyy-MM-dd")
        
        if Decimal(self.quantidade_existente) <= Decimal(0):
            self.verifica_relacao(self.cod_produto, self.codarmazem)

        # Se for produto ao inves de serviço
        if self.get_tipo_produto(self.cod_produto) == 0:
            # Se não se pode vender produtos com quantidade 0 ou menos
            if self.q_abaixo_de_zero == 0:
                # Se nao tem relacao de quantidades com outros produtos, ou os produtos relacionados nao tem quantidades
                # suficiantes
                if self.verifica_relacao(self.cod_produto, self.codarmazem) is False:
                    if Decimal(self.quantidade_existente) <= Decimal(0):
                        QMessageBox.warning(self, "Quantidade inexistente", "Quantidade não existe.")
                        return False

                # Se a quantidade na facturacao extiver para exceder a quantidade existente
                if self.compara_quantidades(self.cod_produto, self.codigogeral) is False:
                    if self.editar_dados_de_facturacao is False:
                        QMessageBox.warning(self, "Quantidade inexistente",
                                            "Quantidade não existe.\nSó existe {} "
                                            "na Base de Dados".format(self.quantidade_existente))
                        return False

                if Decimal(self.quantidade_unitario) > Decimal(self.quantidade_existente):
                    QMessageBox.warning(self, "Quantidade inexistente",
                                        "Quantidade não existe.\nSó existe {} "
                                        "na Base de Dados".format(self.quantidade_existente))
                    return False

        try:
            # Campos de facturacao detalhe
            self.facturacao_modulo.codproduto = self.cod_produto
            self.facturacao_modulo.custo_produto = self.custo_do_produto
            self.facturacao_modulo.preco = str(self.preco_unitario)
            self.facturacao_modulo.quantidade = str(self.quantidade_unitario)
            self.facturacao_modulo.desconto_produto = self.desconto_do_produto
            self.facturacao_modulo.subtotal_produto = self.subtotal_do_produto
            self.facturacao_modulo.taxa_produto = self.taxa_do_produto
            self.facturacao_modulo.total_produto = self.total_do_produto
            self.facturacao_modulo.lucro_produto = self.lucro_do_produto

            self.facturacao_modulo.total = self.total_do_produto
            self.facturacao_modulo.subtotal = self.subtotal_do_produto
            self.facturacao_modulo.taxa = self.taxa_do_produto
            self.facturacao_modulo.lucro = self.lucro_do_produto
            self.facturacao_modulo.desconto = self.desconto_do_produto
            self.facturacao_modulo.custo = self.custo_do_produto
            self.facturacao_modulo.data = validade
            self.facturacao_modulo.created = validade
            self.facturacao_modulo.modified = validade

            self.facturacao_modulo.create_invoice(self.codigogeral, self.caixa_numero, self.coddocumento,
                                                  self.codcliente, self.user)
            self.fill_table()
            self.line_codigoproduto.setFocus()
            self.line_codigoproduto.selectAll()
            self.calcula_total_geral()

            self.butao_apagarItem.setEnabled(True)
            self.butao_apagarTudo.setEnabled(True)

            self.editar_dados_de_facturacao = False

        except Exception as e:
            QMessageBox.warning(self, "Erro", "Erro: {}".format(e))
            return False

        return True

    def calcula_total_geral(self):

        if self.tabelavazia() is True:
            sql = """ delete from facturacao WHERE cod= '{}' """.format(self.codigogeral)
            self.alterar_de_preco = False

            self.reset_labels()
            self.cur.execute(sql)
            self.conn.commit()
            return False

        sql = """ SELECT sum(custo), sum(desconto), sum(taxa), sum(subtotal), sum(lucro), sum(total) from 
        facturacaodetalhe WHERE codfacturacao="{codfacturacao}" """.format(codfacturacao=self.codigogeral)

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        custo = Decimal(data[0][0])
        desconto = Decimal(data[0][1])
        taxa = Decimal(data[0][2])
        subtotal = Decimal(data[0][3])
        lucro = Decimal(data[0][4])
        total = Decimal(data[0][5])

        facturacaosql = """ UPDATE facturacao set custo={custo}, desconto={desconto}, taxa={taxa}, 
        subtotal={subtotal}, lucro={lucro},
        total={total} WHERE cod="{cod}" """.format(custo=custo, desconto=desconto, taxa=taxa, subtotal=subtotal,
                                                   lucro=lucro, total=total, cod=self.codigogeral)
        self.cur.execute(facturacaosql)
        total_display = '{:20,.2f}'.format(total)
        taxa_display = '{:20,.2f}'.format(taxa)
        subtotal_display = '{:20,.2f}'.format(subtotal)
        desconto_display = '{:20,.2f}'.format(desconto)

        self.label_total.setText(total_display)
        self.labelsubtotal.setText(subtotal_display)
        self.labeldesconto.setText(desconto_display)
        self.labeltaxa.setText(taxa_display)

        self.totalgeral = total
        # Actualiza a tabela ou lista de Items

    def recupera_gravados(self):
        """
        Verifica se existe alguns documentos não finalizados e recupera o codigo caso existam
        :return: codifo do documento
        """
        sql = """SELECT f.cod FROM facturacao f JOIN facturacaodetalhe fd ON f.cod=fd.codfacturacao WHERE 
        f.finalizado=0 and f.created_by="{}" AND fd.codarmazem="{}"
        ORDER BY f.created DESC""".format(self.user, self.codarmazem)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            codigo = data[0][0]
        else:
            codigo = None

        return codigo

    def fill_table(self):

        header = ["DOC", "Artigo", "Descrição", "Qty", "Preço", "Taxa", "Desconto", "Subtotal", "Total"]

        sql = """ select facturacao.cod, facturacaodetalhe.codproduto, produtos.nome, facturacaodetalhe.quantidade, 
           facturacaodetalhe.preco, facturacaodetalhe.taxa, facturacaodetalhe.desconto, facturacaodetalhe.subtotal,
           facturacaodetalhe.total from produtos INNER JOIN facturacaodetalhe 
           ON produtos.cod=facturacaodetalhe.codproduto
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
            self.tabledata = data

        try:
            # set the table model
            self.tm = MyTableModel(self.tabledata, header, self)
            self.totalItems = self.tm.rowCount(self)
            self.label_total_items.setText("ITEMS: {}.".format(self.totalItems))
            self.tabela.setModel(self.tm)
            self.tabela.setColumnHidden(0, True)
            self.tabela.setColumnHidden(1, True)
            self.tabela.setColumnWidth(2, self.tabela.width() * .3)
            self.tabela.setColumnWidth(3, self.tabela.width() * .1)
            self.tabela.setColumnWidth(4, self.tabela.width() * .1)
            self.tabela.setColumnWidth(5, self.tabela.width() * .1)
            self.tabela.setColumnWidth(6, self.tabela.width() * .1)
            self.tabela.setColumnWidth(7, self.tabela.width() * .1)

        except Exception as e:
            print(e)
            return
        # # set row height
        nrows = len(self.tabledata)
        for row in range(nrows):
            self.tabela.setRowHeight(row, 25)

    # Apaga a Linha na tabela facturadetalhe
    def removerow(self):

        if self.current_id == "":
            QMessageBox.information(self, "Info", "Selecione o registo a apagar na tabela")
            return

        sql = """delete from facturacaodetalhe WHERE codproduto="{codigo}" and codfacturacao="{cod}"
        """.format(codigo=str(self.current_id), cod=self.codigogeral)

        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(e)

        self.calcula_total_geral()
        self.fill_table()

        self.line_codigoproduto.setFocus()
        self.line_codigoproduto.selectAll()

    # Apaga a Linha na tabela facturadetalhe
    def removeall(self):

        if self.existe(self.codigogeral):
            sql = """DELETE from facturacaodetalhe WHERE codfacturacao="{}" """.format(self.codigogeral)
            sql2 = """DELETE from facturacao WHERE cod="{}" """.format(self.codigogeral)

            self.cur.execute(sql)
            self.cur.execute(sql2)
            self.conn.commit()

            self.reset_labels()
            self.calcula_total_geral()
            self.fill_table()

            self.butao_apagarTudo.setEnabled(False)
            self.butao_apagarItem.setEnabled(False)

            self.line_codigoproduto.setFocus()
            self.line_codigoproduto.selectAll()

    # Verifica se a tabela está vazia ou não
    def tabelavazia(self):

        if self.codigogeral == "":
            return

        sql = """ SELECT * from facturacaodetalhe WHERE codfacturacao="{cod}" """.format(cod=self.codigogeral)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            return True
        else:
            return False

    def gravadocumento(self):

        cl = doc(self)
        if self.coddocumento == "":
            cl.nome.setText(self.combo_documento.currentText())
        else:
            cl.cod.setText(self.coddocumento)

        cl.mostrar_registo()
        cl.setModal(True)
        cl.show()

    def connect_db(self):
        if self.parent() is None:
            self.db = self.connect_db()
            self.user = ""
        else:
            self.conn = self.parent().conn
            self.cur = self.parent().cur
            self.user = self.parent().user

    def resizeEvent(self, *args, **kwargs):
        self.salvar_config_janelas()

    def enterEvent(self, evt):
        self.fechar_timer = 300

        # try:
        #     self.conn.cmd_refresh(1)
        # except Exception as e:
        #     QMessageBox.critical(self, "Erro na base de dados",
        #                          "Conexão com a Base de dados Perdida!!!\n{}.".format(e))
        self.tabela_produtos.fill_table()

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

        self.verifica_caixa()
        self.load_settings()

        if self.tabelavazia() is False:
            self.salva_estado_negativo_do_aplicativo()
        else:
            self.salva_estado_posetivo_do_aplicativo()

        self.calcula_total_geral()

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
        if settings.papel_1 == "" or settings.papel_2 == "":
            papel1 = "72mm"
            papel2 = "72mm"
        else:
            papel1 = settings.papel_1
            papel2 = settings.papel_2

        self.papel_1 = int(papel1.replace("mm", ""))
        self.papel_2 = int(papel2.replace("mm", ""))

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

    label = QLabel("<p style='color: white;'>Modulo: {}</p>".format(MODULO_NAME), splash)
    label.setGeometry(2, splash.height() - 15, int(splash.width() / 2), 15)

    app_label = QLabel("<strong style='color: #C0C0FF;'>{} {}</strong>".format(APPLICATION_NAME, APPLICATION_VERSION), splash)
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

    main = Cliente()
    main.setWindowIcon(QIcon(QIcon("logo.ico")))
    main.showMaximized()

    # Fecha o splash
    splash.finish(main)

    sys.exit(app.exec_())
