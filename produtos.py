# -*- coding: utf-8 -*-
"""
Created on Fri Mar 02 23:18:43 2012

@author: lims
"""

from decimal import Decimal
from PyQt5.QtWidgets import (QTabWidget, QLabel, QLineEdit, QFormLayout, QVBoxLayout, QToolBar, QMessageBox,
                             QTextEdit, QAction, QApplication, QComboBox, QPushButton, QFileDialog, QHBoxLayout,
                             QGroupBox, QDateEdit, QCalendarWidget, QSizePolicy, QWidget, QCheckBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon, QPixmap
import sys


from utilities import codigo as cd, UNIDADE
from pricespinbox import price
from maindialog import Dialog

import sqlite3 as lite

DB_FILENAME = "dados.tsdb"

TIPO_PRODUTO = ["Produto", "Serviço"]

class Produto(Dialog):
    def __init__(self, parent=None, titulo = "Produtos/Serviços", imagem = QIcon("./icons/produtos.ico")):
        super(Produto, self).__init__(parent, titulo, imagem)

        self.fotofile = ""
        self.codarmazem = ""
        self.taxacod = ""
        self.codstock = 'ST20001111111'
        self.fornecedorcod = ""
        self.valortaxa = Decimal(0)
        self.novo_produto = False

        self.accoes()
        self.ui()

        self.user = self.parent().user

        self.cur = self.parent().cur
        self.conn = self.parent().conn

        # verifica a existencia dos dados na base de dados
        self.existe(self.cod.text())

        # Mostraregisto caso exista
        self.mostrar_registo()

        self.enchefamilia()
        self.enchesubfamilia()
        self.enchearmazem()
        self.enche_taxas()
        self.enche_fornecedor()
        # self.getcodarmazem(self.armazem.currentText())

    def ui(self):

        cod = QLabel("Código do Item")
        tipo = QLabel("Tipo")
        nome = QLabel("Nome")
        cod_barras = QLabel("Código de Barras")
        custo = QLabel("Custo")
        preco = QLabel("Preço Principal(Sem Taxa)")
        preco1 = QLabel("Preço 1(Sem Taxa)")
        preco2 = QLabel("Preço 2(Sem Taxa)")
        preco3 = QLabel("Preço 3(Sem Taxa)")
        preco4 = QLabel("Preço 4(Sem Taxa)")
        quantidade = QLabel("Quantidade Inicial")
        quantidade_m = QLabel("Quantidade Mínima")
        unidade = QLabel("Unidade de Medida")
        obs = QLabel("Observações")

        self.cod = QLineEdit()
        self.cod.editingFinished.connect(self.mostrar_registo)
        self.nome_produto = QLineEdit()
        self.nome_produto.setMaxLength(255)
        self.nome_produto.textChanged.connect(self.contar_caracteres)
        self.nome_produto.textChanged.connect(self.copiar_texto)
        self.descricao_produto = QTextEdit()
        self.familia_combobox = QComboBox()
        self.subfamilia = QComboBox()
        self.familia_combobox.currentTextChanged.connect(self.enchesubfamilia)
        self.subfamilia.currentTextChanged.connect(self.codsubfamilia)
        self.cod_barras = QLineEdit()
        self.tipo = QComboBox()
        self.tipo.addItems(TIPO_PRODUTO)
        self.armazem = QComboBox()
        self.armazem.currentTextChanged.connect(lambda: self.getcodarmazem(self.armazem.currentText()))
        self.custo = price()
        self.taxa_box = QComboBox()
        self.taxa_box.currentTextChanged.connect(lambda: self.getcodtaxa(self.taxa_box.currentText()))
        self.fornecedor_combo = QComboBox()
        self.fornecedor_combo.currentTextChanged.connect(lambda: self.getcodfornecedor(
            self.fornecedor_combo.currentText()))
        self.preco = price()
        self.preco1 = price()
        self.preco2 = price()
        self.preco3 = price()
        self.preco4 = price()
        self.validade = QDateEdit(self)
        self.validade.setDisplayFormat('dd-MM-yyyy')

        self.validade.setDate(QDate.currentDate().addYears(1))
        cal = QCalendarWidget()
        self.validade.setCalendarPopup(True)
        self.validade.setCalendarWidget(cal)
        self.quantidade = price()
        self.quantidade_m = price()
        self.quantidade_max = price()
        self.unidade = QComboBox()
        self.unidade.addItems(UNIDADE)
        self.obs = QTextEdit()
        self.estado = QCheckBox("Activo")
        self.favorito = QCheckBox("Favorito")
        self.promocao = QCheckBox("Promoção")
        self.estado.setChecked(True)

        self.foto = QLabel()
        self.foto.setFixedSize(32, 32)
        self.adicionarfoto = QPushButton(QIcon("./icons/add.ico"), "Seleccionar foto")
        # self.adicionarfoto.setDefault(False)
        self.adicionarfoto.setAutoDefault(False)
        self.adicionarfoto.clicked.connect(self.escolher_foto)
        self.removefoto = QPushButton(QIcon("./icons/remove.ico"), "Remover Foto")
        self.removefoto.setAutoDefault(False)
        self.removefoto.clicked.connect(self.remover_foto)
        self.fotodialog = QFileDialog(self, "Seleccionar Foto")

        armazem_box = QHBoxLayout()
        armazem_btn = QPushButton("+")
        armazem_btn.clicked.connect(self.adicionar_armazem)
        armazem_btn.setMaximumWidth(40)
        armazem_box.addWidget(self.armazem)
        armazem_box.addWidget(armazem_btn)

        familia_box = QHBoxLayout()
        familia_btn = QPushButton("+")
        familia_btn.clicked.connect(self.adicionar_familia)
        familia_btn.setMaximumWidth(40)
        familia_box.addWidget(self.familia_combobox)
        familia_box.addWidget(familia_btn)

        subfamilia_box = QHBoxLayout()
        subfamilia_btn = QPushButton("+")
        subfamilia_btn.clicked.connect(self.adicionar_subfamilia)
        subfamilia_btn.setMaximumWidth(40)
        subfamilia_box.addWidget(self.subfamilia)
        subfamilia_box.addWidget(subfamilia_btn)

        taxas_box = QHBoxLayout()
        taxas_btn = QPushButton("+")
        taxas_btn.clicked.connect(self.adicionar_taxas)
        taxas_btn.setMaximumWidth(40)
        taxas_box.addWidget(self.taxa_box)
        taxas_box.addWidget(taxas_btn)

        fornecedor_box = QHBoxLayout()
        fornecedor_btn = QPushButton("+")
        fornecedor_btn.clicked.connect(self.adicionar_fornecedor)
        fornecedor_btn.setMaximumWidth(40)
        fornecedor_box.addWidget(self.fornecedor_combo)
        fornecedor_box.addWidget(fornecedor_btn)

        buttonslayout = QHBoxLayout()
        buttonslayout.addWidget(self.adicionarfoto)
        buttonslayout.addWidget(self.removefoto)

        fotolayout = QVBoxLayout()
        fotolayout.addWidget(self.foto)
        fotolayout.addLayout(buttonslayout)

        # Grade da Foto
        fotogrid = QGroupBox("FOTO do Produto/Serviço")
        fotogrid.setLayout(fotolayout)

        formlayout = QFormLayout()
        formlayout2 = QFormLayout()

        self.numero_caracteres = QLabel("255 Caracteres")
        formlayout.addRow(cod, self.cod)
        formlayout.addWidget(self.numero_caracteres)
        formlayout.addRow(nome, self.nome_produto)
        formlayout.addRow(QLabel('Descrição do Item'), self.descricao_produto)
        formlayout.addRow(tipo, self.tipo)
        formlayout.addRow(QLabel("Armazém Padrão"), armazem_box)
        formlayout.addRow(cod_barras, self.cod_barras)
        formlayout.addRow(QLabel("Familia"), familia_box)
        formlayout.addRow(QLabel("Subfamilia"), subfamilia_box)
        formlayout.addRow(QLabel("Taxa"), taxas_box)
        formlayout.addRow(preco, self.preco)
        formlayout.addRow(quantidade, self.quantidade)
        formlayout.addRow(QLabel("Fornecedor"), fornecedor_box)
        formlayout.addRow(self.estado)
        formlayout.addRow(self.favorito, self.promocao)

        # Leyout de Outros preços
        formlayout2.addRow(custo, self.custo)
        formlayout2.addRow(QLabel("Validade"), self.validade)
        formlayout2.addRow(preco1, self.preco1)
        formlayout2.addRow(preco2, self.preco2)
        formlayout2.addRow(preco3, self.preco3)
        formlayout2.addRow(preco4, self.preco4)
        formlayout2.addRow(QLabel("Quantidade Máxima"), self.quantidade_max)
        formlayout2.addRow(quantidade_m, self.quantidade_m)
        formlayout2.addRow(unidade, self.unidade)
        formlayout2.addWidget(fotogrid)
        formlayout2.addRow(obs, self.obs)

        submainlayout = QVBoxLayout()
        submainlayout.addLayout(formlayout)
        # submainlayout.addWidget(fotogrid)

        precos1_widget = QWidget()
        precos1_widget.setLayout(submainlayout)
        precos2_widget = QWidget()
        precos2_widget.setLayout(formlayout2)
        
        tabulador = QTabWidget()
        tabulador.addTab(precos1_widget, "Dados principais")
        tabulador.addTab(precos2_widget, "Dados avançados")

        mainlayout = QVBoxLayout(self)
        mainlayout.setContentsMargins(10, 10, 10, 10)
        mainlayout.addWidget(tabulador)
        mainlayout.addWidget(self.tool)
        self.layout().addLayout(mainlayout)

        self.setWindowTitle("Cadastro de produtos")

    def contar_caracteres(self):
        if len(self.nome_produto.text()) < 256:
            self.numero_caracteres.setText("{} Caracteres".format(255 - len(self.nome_produto.text())))

    def copiar_texto(self, text):
        return self.descricao_produto.setText(text)

    def adicionar_taxas(self):
        from taxas import Cliente

        f = Cliente(self)
        f.setModal(True)
        f.show()

    def adicionar_familia(self):
        from familia import Cliente

        f = Cliente(self)
        f.setModal(True)
        f.show()

    def adicionar_subfamilia(self):
        from subfamilia import Cliente

        f = Cliente(self)
        f.setModal(True)
        f.show()

    def adicionar_armazem(self):
        from armazem import Armazem

        f = Armazem(self)
        f.setModal(True)
        f.show()

    def adicionar_fornecedor(self):
        from fornecedores import Fornecedor
        f = Fornecedor(self)
        f.setModal(True)
        f.show()

    def accoes(self):
        self.tool = QToolBar()
        self.tool.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        gravar = QAction(QIcon("./images/ok.png"), "&Gravar e \nFechar", self)
        gravar_clonar = QAction(QIcon("./images/filesaveas.png"), "G&ravar e \nClonar Dados ", self)
        gravar_criar = QAction(QIcon("./images/filesave.png"), "Gravar e \n&Criar Novo ", self)
        eliminar = QAction(QIcon("./icons/new.ico"), "&Limpar\nCampos", self)

        fechar = QAction(QIcon("./images/filequit.png"), "&Fechar", self)

        self.tool.addAction(gravar)
        self.tool.addAction(gravar_clonar)
        self.tool.addAction(gravar_criar)
        self.tool.addAction(eliminar)

        self.tool.addSeparator()
        self.tool.addAction(fechar)

        gravar.triggered.connect(self.gravar_apenas)
        gravar_clonar.triggered.connect(self.gravar_clonar)
        gravar_criar.triggered.connect(self.gravar_criar)
        eliminar.triggered.connect(self.limpar)
        fechar.triggered.connect(self.fechar)

    def gravar_apenas(self):
        if self.add_record() is True:
            self.close()

    def gravar_clonar(self):
        if self.add_record() is True:
            self.cod.setText("PR" + cd("abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789"))
            self.nome_produto.selectAll()
            self.nome_produto.setFocus()

    def gravar_criar(self):
        if self.add_record() is True:
            self.limpar()
            self.nome_produto.selectAll()
            self.nome_produto.setFocus()

    # Enche a Combobox Familia
    def enchefamilia(self):
        self.familia_combobox.clear()

        sql = "SELECT nome FROM familia"
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                self.familia_combobox.addItems(item)

    def enchesubfamilia(self):

        # clear the combobox
        self.subfamilia.clear()

        # Procura o nome na tabela familia baseando-se no codigo da Familia na tabela subfamilia
        sql = """select subfamilia.nome from familia INNER JOIN subfamilia ON familia.cod=subfamilia.codfamilia
         WHERE familia.nome= "{nome}" """.format(nome=self.familia_combobox.currentText())

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                self.subfamilia.addItems(item)

            # Encontra o código da Familia
            self.getcodfamilia()

    def codsubfamilia(self):
        sql = """select cod from subfamilia WHERE nome= "{nome}" """.format(nome=self.subfamilia.currentText())
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0: return

        for item in data:
            self.subfamiliacod = item[0]

    def getcodfamilia(self):
        sql = """select cod from familia WHERE nome= "{nome}" """.format(nome=self.familia_combobox.currentText())

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0: return

        self.familiacod = "".join(data[0])

    def getcodfornecedor(self, nomefornecedor):
        sql = """select cod from fornecedores WHERE nome= "{nome}" """.format(nome=nomefornecedor)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0: return

        self.fornecedorcod = "".join(data[0])

    def getcodtaxa(self, nometaxa):
        sql = """select cod, valor from taxas WHERE nome= "{nome}" """.format(nome=nometaxa)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0: return

        self.taxacod = data[0][0]
        self.valortaxa = Decimal(data[0][1])

    def enchearmazem(self):

        self.armazem.clear()

        sql = "SELECT nome FROM armazem"
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                self.armazem.addItems(item)

    def enche_fornecedor(self):
        self.fornecedor_combo.clear()

        sql = "SELECT nome FROM fornecedores"
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                self.fornecedor_combo.addItems(item)

    def enche_taxas(self):
        self.taxa_box.clear()

        sql = "SELECT nome FROM taxas"
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                self.taxa_box.addItems(item)

    def getcodarmazem(self, codarmazem):
        sql = """select cod from armazem WHERE nome= "{nome}" """.format(nome=codarmazem)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0: return

        for item in data:
            self.codarmazem = item[0]

            print(self.codarmazem)

    def closeEvent(self, evt):
        parent = self.parent()
        if hasattr(parent, 'enche_produtos'):
            parent.enche_produtos()
        elif hasattr(parent, 'fill_table'):
            parent.fill_table()

    def fechar(self):
        self.close()

    def limpar(self):

        self.nome_produto.setText("")
        self.obs.setPlainText("")
        self.cod.setText("PR" + cd("abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789"))
        self.cod.selectAll()
        self.custo.setValue(0.00)
        self.preco.setValue(0.00)
        self.preco1.setValue(0.00)
        self.preco2.setValue(0.00)
        self.preco3.setValue(0.00)
        self.preco4.setValue(0.00)
        self.quantidade.setValue(0.00)
        self.quantidade_m.setValue(0.00)

    def validacao(self):

        if self.custo.text() == "": self.custo.setValue(0.00)
        if self.preco.text() == "": self.preco.setValue(0.00)
        if self.quantidade.text() == "": self.quantidade.setValue(0.00)
        if self.quantidade_m.text() == "": self.quantidade_m.setValue(0.00)

        if self.cod.text() == "":
            QMessageBox.warning(self, "Erro", "Entre o código do produto")
            self.cod.setFocus()
            return False
        elif str(self.nome_produto.text()) == "":
            QMessageBox.warning(self, "Erro", "Nome do produto inválido")
            self.nome_produto.setFocus()
            return False
        elif str(self.familia_combobox.currentText()) == "":
            QMessageBox.warning(self, "Erro", "Cadastre Famílias de Produtos Primeiro")
            return False
        elif str(self.subfamilia.currentText()) == "":
            QMessageBox.warning(self, "Erro", "Cadastre Sub Famílias de Produtos Primeiro")
            return False
        elif self.armazem == "":
            QMessageBox.warning(self, "Erro", "Cadastre Armazém Primeiro")
            return False
        else:
            return True

    def focusOutEvent(self, *args, **kwargs):
        print("A bazar...o Focus.")
        if self.cod.hasFocus():
            self.mostrar_registo()

    def get_nome_taxa(self, codtaxa):
        sql = """SELECT nome from taxas where cod="{}" """.format(codtaxa)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return data[0][0]

        return 'IVA'

    def mostrar_registo(self):

        sql = """ SELECT DISTINCT produtos.nome, produtos.cod_barras, familia.nome, subfamilia.nome, produtos.custo, 
        produtos.preco, produtosdetalhe.quantidade, produtos.quantidade_m, produtos.unidade, produtos.obs, 
        produtos.foto, produtos.preco1, produtos.preco2, produtos.preco3, produtos.preco4, produtos.tipo, 
        produtos.estado, produtos.codtaxa, produtos.favorito, produtos.promocao, produtos.descricao from produtos 
        LEFT JOIN familia ON familia.cod=produtos.codfamilia 
        LEFT JOIN subfamilia ON subfamilia.codfamilia=familia.cod 
        LEFT JOIN produtosdetalhe ON produtosdetalhe.codproduto=produtos.cod
        WHERE produtos.cod="{codigo}" GROUP BY produtos.cod """.format(codigo=str(self.cod.text()))

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        if len(data) > 0:
            self.nome_produto.setText(''.join(data[0][0]))
            self.cod_barras.setText(''.join(data[0][1]))
            self.familia_combobox.setCurrentText(''.join(data[0][2]))
            self.subfamilia.setCurrentText(''.join(data[0][3]))
            self.custo.setValue(Decimal(data[0][4]))
            self.preco.setValue(Decimal(data[0][5]))
            self.preco1.setValue(Decimal(data[0][11]))
            self.preco2.setValue(Decimal(data[0][12]))
            self.preco3.setValue(Decimal(data[0][13]))
            self.preco4.setValue(Decimal(data[0][14]))
            self.tipo.setCurrentIndex(int(data[0][15]))
            self.quantidade.setValue(Decimal(data[0][6]))
            self.taxa_box.setCurrentText(self.get_nome_taxa(data[0][17]))
            self.quantidade_m.setValue(Decimal(data[0][7]))
            self.unidade.setCurrentText(''.join(data[0][8]))
            self.obs.setPlainText(''.join(data[0][9]))
            self.estado.setChecked(bool(int(data[0][16])))
            self.favorito.setChecked(bool(int(data[0][18])))
            self.promocao.setChecked(bool(int(data[0][19])))
            self.descricao_produto.setText(str(data[0][20]))

            try:
                self.fotofile = data[0][10]
                self.mostrar_foto(self.fotofile)
                print('foto: ', self.fotofile)
            except Exception as e:
                print(e)
                self.foto.setPixmap(QPixmap(''))

    def existe(self, codigo):

        sql = """SELECT cod from produtos WHERE cod = "{codigo}" """.format(codigo=codigo)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            self.novo_produto = True
            return False
        else:
            self.novo_produto = False
            codigo = ''.join(data[0])
            self.codigo = codigo
            return True

    def selecionar_foto(self):

        formats = "Todas as Imagens(*.bmp; *.jpg; *.png)"
        self.path = "."

        dialog = QFileDialog(self)
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        path = dialog.getOpenFileName(self, "Escolha a Foto", self.path, formats)

        if path == "":
            caminho = ""
        else:
            caminho = path[0]

        self.fotofile = caminho
        return self.fotofile

    def escolher_foto(self):
        self.mostrar_foto(self.selecionar_foto())

    def mostrar_foto(self, foto):
        pixmap = QPixmap(foto)
        pixmap.scaled(64, 64, Qt.KeepAspectRatio)
        self.foto.setPixmap(pixmap)
        self.foto.setScaledContents(True)
        self.foto.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

    def remover_foto(self):
        self.foto.setPixmap(QPixmap(""))

    def lista_armazem(self):
        """
        Metodo que retorna o codigo de todos armazens
        :return: lista de codigos de Armazem
        """
        sql = """SELECT cod from armazem"""
        self.cur.execute(sql)
        data = self.cur.fetchall()

        lista = []

        for l in data:
            lista.append(l[0])

        return lista

    def add_record(self):

        if self.validacao() is False:
            return False

        code = self.cod.text()
        if self.tipo.currentText() == "Produto":
            tipo = 0
        else:
            tipo = 1

        if code == "":
            QMessageBox.warning(self, 'Erro de código', "Código é de preenchimento obrigatório.")
            self.cod.setFocus()
            return False

        cod_taxa = self.taxacod
        nome = self.nome_produto.text()
        descricao = self.descricao_produto.toPlainText()
        familia = self.familiacod
        subfamilia = self.subfamiliacod
        cod_barras = self.cod_barras.text()
        
        custo = Decimal(self.custo.value())
        preco = Decimal(self.preco.value())
        preco1 = Decimal(self.preco1.value())
        preco2 = Decimal(self.preco2.value())
        preco3 = Decimal(self.preco3.value())
        preco4 = Decimal(self.preco4.value())
        quantidade = Decimal(self.quantidade.value())
        quantidade_m = Decimal(self.quantidade_m.value())
        quantidade_max = Decimal(self.quantidade_max.value())
        unidade = self.unidade.currentText()
        obs = self.obs.toPlainText()

        favorito = int(self.favorito.isChecked())
        promocao = int(self.promocao.isChecked())
        estado = int(self.estado.isChecked())

        created = QDate.currentDate().toString('yyyy-MM-dd')
        modified = QDate.currentDate().toString('yyyy-MM-dd')
        foto = self.fotofile

        modified_by = created_by =  self.parent().user

        sql_list = []
        if self.existe(code) is True:
            sql = """UPDATE produtos set nome="{nome}", cod_barras="{cod_barras}", tipo={tipo},codfamilia="{familia}",
            codsubfamilia="{subfamilia}", custo={custo}, preco={preco}, preco1={preco1}, preco2={preco2}, 
            preco3={preco3}, preco4={preco4}, quantidade={quantidade}, quantidade_m={quantidade_m}, 
            unidade="{unidade}", obs="{obs}", estado={estado}, modified="{modified}", modified_by="{modified_by}", 
            created="{created}", created_by="{created_by}", foto="{foto}", codtaxa="{taxa}", 
            quantidade_max={quantidade_max}, favorito={favorito}, promocao={promocao}, descricao="{descricao}" 
            WHERE cod="{cod}"
            """.format(cod=code, nome=nome,tipo=tipo, familia=familia, subfamilia=subfamilia, cod_barras=cod_barras,
                       custo=custo, preco=preco, preco1=preco1, preco2=preco2, preco3=preco3, preco4=preco4,
                       quantidade=quantidade, quantidade_m=quantidade_m, unidade=unidade, obs=obs,
                       estado=estado, modified=modified, modified_by=modified_by,
                       created=created, created_by=created_by, foto=foto, taxa=cod_taxa,
                       quantidade_max=quantidade_max, favorito=favorito, promocao=promocao, descricao=descricao)

            sql_detalhes = """UPDATE produtosdetalhe set quantidade={quantidade}, modified="{modified}", 
            modified_by="{modified_by}" WHERE codproduto="{cod}" 
            AND codarmazem="{codarmazem}" """.format(quantidade=quantidade, cod=code, codarmazem=self.codarmazem,
                                                     modified=modified, modified_by=modified_by)

            sql_list.append(sql_detalhes)

            mensagem = "Registo Actualizado com Sucesso!"
        else:
            values = """ "{cod}", "{nome}", "{cod_barras}", {tipo},"{familia}", "{subfamilia}", {custo}, {preco}, 
            preco1={preco1}, preco2={preco2}, preco3={preco3}, preco4={preco4},
            {quantidade}, {quantidade_m}, "{unidade}", "{obs}", {estado}, "{created}", "{modified}", 
            "{modified_by}", "{created_by}", "{foto}", "{taxa}", {quantidade_max}, {favorito}, {promocao}, 
            "{descricao}"
            """.format(cod=code, nome=nome, tipo=tipo, cod_barras=cod_barras, familia=familia, subfamilia=subfamilia,
                       custo=custo, preco=preco, preco1=preco1, preco2=preco2, preco3=preco3, preco4=preco4,
                       quantidade=quantidade, quantidade_m=quantidade_m, unidade=unidade, obs=obs,
                       estado=estado, created=created, modified=modified, modified_by=modified_by,
                       created_by=created_by, foto=foto, taxa=cod_taxa, quantidade_max=quantidade_max,
                       favorito=favorito, promocao=promocao, descricao=descricao)

            for codarmazem in self.lista_armazem():
                if codarmazem == self.codarmazem:
                    q = quantidade
                else:
                    q = 0

                sql_detalhes = """INSERT INTO produtosdetalhe (codproduto, codarmazem, quantidade, created, 
                modified, modified_by, created_by) VALUES ("{codproduto}", "{codarmazem}", {quantidade}, 
                "{created}", "{modified}", "{modified_by}", "{created_by}")""".format(codproduto=code,
                                                                                      codarmazem=codarmazem,
                                                                                      quantidade=q,
                                                                                      created=created,
                                                                                      modified=modified,
                                                                                      modified_by=modified_by,
                                                                                      created_by=created_by)
                sql_list.append(sql_detalhes)

            sql = """INSERT INTO produtos (cod, nome, cod_barras, tipo, codfamilia, codsubfamilia, custo, preco,  preco1, 
            preco2,  preco3,  preco4, quantidade, quantidade_m, unidade, obs, estado, created, modified, 
            modified_by, created_by, foto, codtaxa, quantidade_max, favorito, promocao, descricao) values({value})
            """.format(value=values)

            mensagem = "Registo Gravado com Sucesso!"

        try:
            self.cur.execute(sql)
            for x in sql_list:
                self.cur.execute(x)
            self.gravar_stock()
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Erro", "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
            return False

        QMessageBox.information(self, "Sucesso", mensagem)

        return True

    def gravar_stock(self):

        cod_stock = "ST" + cd("ST" + "abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")
        cod_fornecedor = self.fornecedorcod
        data = QDate.currentDate().toString('yyyy-MM-dd')
        custo = Decimal(self.custo.text())
        quantidade = Decimal(self.quantidade.value())
        subtotal = custo * quantidade
        taxa = self.valortaxa/100 * subtotal
        total = subtotal + taxa
        codproduto = self.cod.text()
        validade = self.validade.date().toString('yyyy-MM-dd')

        if self.parent() is not None:
            created_by = modified_by = self.parent().user
        else:
            created_by = modified_by = "User"

        if self.novo_produto is True:
            numero_doc = "STOCK INICIAL {}".format(data)
        else:
            numero_doc = "ACTUALIZAÇÃO DO STOCK {}".format(data)

        values = """ "{cod}", "{fornecedor}", "{numero}", "{data}", {total}, {iva}, {subtotal}, {saldo}, 
                    "{created}", "{modified}", "{modified_by}", "{created_by}", {estado} 
                    """.format(cod=cod_stock, fornecedor=cod_fornecedor, numero=numero_doc, data=data, total=total,
                               iva=taxa, subtotal=subtotal, created=data, modified=data,
                               modified_by=modified_by, created_by=created_by, saldo=total, estado=1)

        sql_stock = """INSERT INTO stock (cod, fornecedor, numero, data, total, taxa, subtotal, saldo, created,
                    modified, modified_by, created_by, estado) values({value})""".format(value=values)

        sql_list = []

        for codarmazem in self.lista_armazem():
            if codarmazem == self.codarmazem:
                q = quantidade
            else:
                q = 0

            stock_detalhe_values = """ "{codstock}", "{codproduto}", "{codarmazem}", {quantidade}, "{validade}",{valor}, {taxa}, 
            {subtotal}, {total} """.format(codstock=cod_stock, codproduto=codproduto, codarmazem=codarmazem,
                                           quantidade=q, validade=validade, valor=custo, taxa=taxa, subtotal=subtotal,
                                           total=total)

            sql_stockdetalhe = """INSERT INTO stockdetalhe (codstock, codproduto, codarmazem, quantidade, validade, 
            valor, taxa, subtotal, total) values({value})""".format(value=stock_detalhe_values)

            print(sql_stockdetalhe)

            sql_list.append(sql_stockdetalhe)

        self.cur.execute(sql_stock)
        for x in sql_list:
            self.cur.execute(x)
        self.novo_produto = False

    def connect_db(self):
        # Connect to database and retrieves data
        try:
            self.conn = lite.connect(DB_FILENAME)
            self.cur = self.conn.cursor()

        except Exception as e:
            QMessageBox.critical(self, "Erro ao conectar a Base de Dados",
                                 "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
            sys.exit(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    helloPythonWidget = Produto()
    helloPythonWidget.show()

    sys.exit(app.exec_())
