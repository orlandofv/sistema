import datetime
import decimal
import sys
import os

from utilities import printWordDocument, Invoice

from PyQt5.QtWidgets import (QLineEdit, QToolBar, QMessageBox, qApp, QAction, QApplication, QGroupBox, QPushButton,
                             QComboBox, QDialog, QFormLayout, QHBoxLayout, QTableView, QCheckBox, QAbstractItemView,
                             QSplitter, QStatusBar, QVBoxLayout, QLabel)

from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QIcon, QTextDocument, QFont

from PyQt5.QtCore import QDate, QSizeF, Qt

from sortmodel import MyTableModel
from utilities import codigo as cd
from pricespinbox import price
from relatorio.templates.opendocument import Template

from GUI.RibbonButton import RibbonButton
from GUI.RibbonWidget import *

# from produtos import Produto as prod
from utilities import ANO_ACTUAL, HORA, MES, DATA_ACTUAL

from maindialog import Dialog


#Classe que representa a Lista de Produtos
class Pedidos(Dialog):
    def __init__(self, parent=None, titulo="", imagem=""):
        super(Pedidos, self).__init__(parent, titulo, imagem)

        self.codigogeral = "FT" + cd("FT" + "abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")
        self.preco_unitario = 0.00
        self.quantidade_unitaria = 0.00
        self.valor_total = 0.00
        self.coddocumento = "DC20185555555"
        self.numero = 1

        self.numero_da_mesa = self.parent().numero_da_mesa
        self.user = self.parent().user

        self.current_id2 = None

        # Connect the Database
        if self.parent() is None:
            self.db = self.connect_db()
            self.user = ""
        else:
            self.conn = self.parent().conn
            self.cur = self.parent().cur
            self.user = self.parent().user
            self.empresa_logo = self.parent().empresa_logo
            self.nomearmazem2 = self.parent().empresa
            self.numero_da_mesa = self.parent().numero_da_mesa

        self.create_toolbar()

        # Create the main user interface
        self.ui()

        self.incrimenta(ANO_ACTUAL, self.coddocumento)
        # Header for the table

        self.enche_armazem()

        # Search the data
        self.fill_table()
        self.find_w.textEdited.connect(self.fill_table)

    def ui(self):
        print("Create UI...")

        # create the view
        self.tv = QTableView(self)

        # set the minimum size
        # self.tv.setMinimumSize(400, 300)

        # hide grid
        self.tv.setShowGrid(False)

        self.tv.setSelectionBehavior(QAbstractItemView.SelectRows)
        # set the font

        # hide vertical header
        vh = self.tv.verticalHeader()
        vh.setVisible(False)

        # set horizontal header properties and stretch last column
        hh = self.tv.horizontalHeader()
        hh.setStretchLastSection(True)

        # set column width to fit contents
        self.tv.resizeColumnsToContents()

        # enable sorting
        self.tv.setSortingEnabled(True)

        self.tv.clicked.connect(self.clickedslot)
        self.tv.setAlternatingRowColors(True)

        # create the view
        self.tabela = QTableView(self)

        # set the minimum size
        # self.tabela.setMinimumSize(400, 300)

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

        self.tabela.clicked.connect(self.clickedslot2)
        self.tabela.setAlternatingRowColors(True)

        self.action_adicionar = QAction(QIcon('./icons/add_2.ico'), qApp.tr("Adicionar"), self)
        self.action_adicionar.triggered.connect(self.add_record)
        action_adicionar = RibbonButton(self, self.action_adicionar, True)

        self.action_remover_linha = QAction(QIcon('./icons/remove.ico'), qApp.tr("Remover \n Linha"), self)
        self.action_remover_linha.setEnabled(False)
        self.action_remover_linha.triggered.connect(self.removerow)
        action_remover_linha = RibbonButton(self, self.action_remover_linha, True)

        self.action_remover = QAction(QIcon('./images/editdelete.png'), qApp.tr("Remover \n Tudo"), self)
        self.action_remover.setEnabled(False)
        self.action_remover.triggered.connect(self.removeall)
        action_remover = RibbonButton(self, self.action_remover, True)

        boldfont = QFont('Consolas', 18)

        self.quantidade = price()
        self.quantidade.setFont(boldfont)
        self.quantidade.setRange(0, 999999999)
        self.quantidade.valueChanged.connect(lambda: self.calculatotal(self.preco.value(), self.quantidade.value()))
        self.preco = price()
        self.preco.setFont(boldfont)
        self.total = price()
        self.total.setFont(boldfont)

        armazembox = QVBoxLayout()
        armazembox.addWidget(self.tv)

        formlay = QFormLayout()
        formlay.addRow(QLabel("Qty"), self.quantidade)
        formlay.addRow(QLabel("Preço"), self.preco)
        formlay.addRow(QLabel("Total"), self.total)
        armazembox.addLayout(formlay)

        butonbox = QVBoxLayout()
        butonbox.addWidget(action_adicionar)
        butonbox.addWidget(action_remover_linha)
        butonbox.addWidget(action_remover)

        hlay = QHBoxLayout()
        hlay.addLayout(armazembox)
        hlay.addLayout(butonbox)
        hlay.addWidget(self.tabela)

        mainlay = QVBoxLayout()
        mainlay.addWidget(self.tool)
        mainlay.addLayout(hlay)
        mainlay.setContentsMargins(10, 10, 10, 10)

        self.layout().addLayout(mainlay)

    def focusInEvent(self, evt):
        self.fill_table()

    def keyPressEvent(self, event):
        try:
            if event.key() in (Qt.Key_Enter, 16777220):
                self.add_record()
            elif event.key() == Qt.Key_F2:
                self.imprime_pos()
            elif event.key() == Qt.Key_Escape:
                self.close()

        except Exception as e:
            print(e)

    def doc_finalizado(self, finalizado=0):
        if finalizado == 1:
            self.tv.setEnabled(False)
            self.tabela.setEnabled(False)
            self.action_adicionar.setEnabled(False)
            self.action_remover.setEnabled(False)
            self.action_remover_linha.setEnabled(False)
            self.tool.setEnabled(False)

    def connect_db(self):
        import mysql.connector as mc

        self.conn = mc.connect(host=self.empresa_host,
                               user=self.empresa_user,
                               passwd=self.empresa_passw,
                               db=self.empresa_db,
                               port=self.empresa_port)

        self.cur = self.conn.cursor()

        return

    def gravardoc(self):
        self.codigogeral = "FT" + cd("FT" + "abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")
        self.fill_table2()

    def getcodarmazem(self, nomearmazem):
        if nomearmazem == "":
            self.codarmazem = ""
            return

        sql = """SELECT cod from armazem WHERE nome="{}" """.format(nomearmazem)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        print(nomearmazem)
        if len(data) > 0:
            self.codarmazem = data[0][0]

    def fill_table(self):

        self.sql = """SELECT produtos.cod, produtos.nome, produtos.preco, produtosdetalhe.quantidade, 
                armazem.nome from produtos
                         INNER JOIN produtosdetalhe ON produtos.cod=produtosdetalhe.codproduto 
                         INNER JOIN armazem ON armazem.cod=produtosdetalhe.codarmazem
                         WHERE (produtos.nome
                         like "%{nome}%" or produtos.cod_barras like "%{cod_barras}%" or produtos.cod like "%{preco}%") 
                        
                         GROUP BY produtos.cod""".format(nome=self.find_w.text(), cod_barras=self.find_w.text(),
                                                         preco=self.find_w.text())

        try:
            self.cur.execute(self.sql)
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]
        except Exception as e:
            print(e)
            return

        if len(data) == 0:
            self.tabledata = ["", "", "", "", ""]
        else:
            self.tabledata = data

        header = [qApp.tr('Cód.'), qApp.tr('Descrição'), qApp.tr('Preço'), qApp.tr('Qty'), 'Armazém']
        try:
            self.tm = MyTableModel(self.tabledata, header, self)
            # set the table model
            self.totalItems = self.tm.rowCount(self)
            self.tv.setModel(self.tm)
            self.tv.setColumnHidden(0, True)
            self.tv.setColumnHidden(3, True)
            self.tv.setColumnHidden(4, True)

            self.tv.setColumnWidth(1, self.tv.width() * .8)
            self.tv.setColumnWidth(2, self.tv.width() * .2)

        except Exception as e:
            return
        # # set row height
        nrows = len(self.tabledata)
        for row in range(nrows):
            self.tv.setRowHeight(row, 30)
        # self.create_statusbar()

        # Encontra o codigo do armazem
        self.getcodarmazem(self.armazem_combo.currentText())


    def fill_table2(self):

        header = ["DOC", "Cód.", "Descrição", "Qty", "Armazém", "codarmazem"]

        sql = """ select cozinha.cod, cozinhadetalhe.codproduto, produtos.nome, cozinhadetalhe.quantidade,  
           armazem.nome, armazem.cod from produtos, cozinha, cozinhadetalhe, armazem 
           WHERE (produtos.cod=cozinhadetalhe.codproduto 
           AND cozinha.cod=cozinhadetalhe.codcozinha AND armazem.cod=cozinhadetalhe.codarmazem) 
           AND codfacturacao="{codf}" """.format(codf=self.parent().codigogeral)

        print(sql)
        try:
            self.cur.execute(sql)
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]

        except Exception as e:
            print(e)
            return

        if len(data) == 0:
            self.tabledata = [('', '', '', "", "", "")]
        else:
            self.tabledata = data
            self.habilita_desabilita_impressao()
            self.action_remover.setEnabled(True)
            self.action_remover_linha.setEnabled(True)

        try:
            # set the table model
            self.tm2 = MyTableModel(self.tabledata, header, self)
            self.totalItems = self.tm2.rowCount(self)
            self.tabela.setModel(self.tm2)
            self.tabela.setColumnHidden(0, True)
            self.tabela.setColumnHidden(1, True)
            self.tabela.setColumnHidden(4, True)
            self.tabela.setColumnHidden(5, True)

            self.tabela.setColumnWidth(2, self.tabela.width()*.8)
            self.tabela.setColumnWidth(3, self.tabela.width() * .2)

        except Exception as e:
            print(e)
            return
        # # set row height
        nrows = len(self.tabledata)
        for row in range(nrows):
            self.tabela.setRowHeight(row, 30)

    def validacaodetalhes(self):

        self.quantidade_unitaria = self.quantidade.value()
        self.preco_unitario = self.preco.value()

        if self.quantidade_unitaria <= 0:
            return  False
        else:
            return True

    def existe(self, codigo):

        sql = """SELECT cod from cozinha WHERE cod = "{codigo}" """.format(codigo=str(codigo))

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            return False
        else:
            return True

    def grava_cliente(self):

        code = self.numero_da_mesa

        nome = self.nomearmazem2
        endereco = ""
        nuit = ""
        email = ""
        contactos = ""
        desconto = 0
        valor_minimo = 0
        obs = ""
        estado = 0
        created = QDate.currentDate().toString('yyyy-MM-dd')
        modified = QDate.currentDate().toString('yyyy-MM-dd')

        if self.parent() is not None:
            modified_by = self.parent().user
        else:
            modified_by = "User"
        if self.parent() is not None:
            created_by = self.parent().user
        else:
            created_by = "User"

        values = """ "{cod}", "{nome}", "{endereco}", "{NUIT}", "{email}", "{contactos}", {valor_desconto} ,
                     {valor_minimo}, "{obs}", "{estado}", "{created}", "{modified}", "{modified_by}", "{created_by}"
                      """.format(cod=code, nome=nome, endereco=endereco, NUIT=nuit, email=email,
                                 contactos=contactos,
                                 valor_desconto=desconto, valor_minimo=valor_minimo, obs=obs, estado=estado,
                                 created=created, modified=modified, modified_by=modified_by, created_by=created_by)
        try:
            sql = "INSERT INTO clientes (cod, nome, endereco, NUIT,email, contactos, desconto, valor_minimo, " \
                  "obs, estado, created, modified, modified_by, created_by)" \
                  " values({value})".format(value=values)
            self.cur.execute(sql)
            self.conn.commit()

            print("Clientes gravado com sucesso")
        except Exception as e:
            # QMessageBox.warning(self, "Erro", "Cliente não for gravado, grave manualmente")
            return False

        self.codcliente = code

    def getcodcliente(self):
        sql = """select cod from clientes WHERE nome="{nome}" """.format(nome=self.nomearmazem2)



        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            self.codcliente = "".join(data[0])
        else:
            self.codcliente = ""

    def add_record(self):
        if self.quantidade.value() == 0:
            QMessageBox.warning(self, "Erro", "Quantidade deve ser maior que zero (0)")
            self.quantidade.setFocus()
            return False

        if self.validacaodetalhes() is True:

            try:
                code = self.codigogeral
                numero = self.numero
                data = QDate.currentDate().toString('yyyy-MM-dd')
                coddocumento = "DC20185555555"
                quantidade = self.quantidade_unitaria
                preco = self.preco_unitario
                custo = preco * quantidade
                desconto = 0.00
                subtotal = preco * quantidade
                taxa = 0.00
                total = preco * quantidade
                lucro = 0.00
            except Exception as e:
                QMessageBox.critical(self, "Erro grave", "Aconteceu erro grave nos seus dados. verifique-os."
                                                         "\n{}.".format(e))
                return

            pago = 0.00
            troco = 0.00
            banco = 0.00
            cash = 0.00
            tranferencia = 0.00
            estado = 0
            extenso = ""
            ano = ANO_ACTUAL
            mes = MES
            obs = ""
            created = QDate.currentDate().toString('yyyy-MM-dd')
            modified = QDate.currentDate().toString('yyyy-MM-dd')

            if self.parent() is not None:
                modified_by = self.parent().user
                print('Parente ', self.parent(), "Empresa", self.parent().empresa, "Estado" ,
                      self.verifica_cliente(self.parent().empresa))
                if self.verifica_cliente(self.parent().empresa) is False:
                    self.grava_cliente()

                self.getcodcliente()
                codcliente = self.codcliente
                self.caixa_numero = self.parent().caixa_numero
            else:
                codcliente = "CL20181111111"
                modified_by = self.user
                self.caixa_numero = "CX2018107J5Q8"

            if self.parent() is not None:
                created_by = self.parent().user
            else:
                created_by = self.user


            if self.existe(self.codigogeral) is True:

                sql = """UPDATE cozinha set custo=custo+{custo}, subtotal=subtotal+{subtotal}, 
                desconto=desconto+{desconto}, taxa=taxa+{taxa}, total=total+{total}, lucro=lucro+{lucro},
                codfacturacao="{codfacturacao}" 
                WHERE cod="{cod}" """.format(cod=code, custo=custo, subtotal=subtotal, desconto=desconto,
                                            taxa=taxa, total=total, lucro=lucro,codfacturacao=self.parent().codigogeral )
            else:
                values = """ "{cod}", {numero}, "{coddocumento}", "{codcliente}", "{data}", {custo}, {subtotal}, 
                {desconto}, {taxa}, {total}, {lucro}, {debito},{credito}, {troco}, {banco}, {cash}, {tranferencia}, {estado}, 
                {ano}, {mes}, "{obs}", "{created}", "{modified}", "{modified_by}", "{created_by}", "{caixa}", 
                "{codarmazem}", {finalizado}, {mesa}, "{codfacturacao}"
                 """.format(cod=code, numero=numero, coddocumento=coddocumento, codcliente=codcliente,
                            data=data, custo=custo, subtotal=subtotal, desconto=desconto, taxa=taxa,
                            total=total, lucro=lucro, debito=pago, credito= 0.00,troco=troco, banco=banco,
                            cash=cash, tranferencia=tranferencia, estado=estado,ano=ano,
                            mes=mes, obs=obs, created=created, modified=modified, modified_by=modified_by,
                            created_by=created_by, caixa=self.caixa_numero, codarmazem=self.codarmazem,
                            finalizado=1, mesa=self.numero_da_mesa, codfacturacao=self.parent().codigogeral)

                sql = """ INSERT INTO cozinha (cod, numero, coddocumento, codcliente, data, custo, subtotal,
                 desconto, taxa, total,  lucro, debito, credito,troco, banco, cash, tranferencia, estado, ano, mes, 
                 obs, created, modified, modified_by, created_by, caixa, codarmazem, finalizado,
                 mesa, codfacturacao) values({value})""".format(value=values)
            try:

                self.cur.execute(sql)

                # Grava detalhes do documento mas depende da tabela mae cozinha
                self.gravadetalhes()

                # Adiciona produto na mesa
                self.add_record_produto()

                # So Grava caso nao exista erro nas 2 tabelas
                self.conn.commit()
            except Exception as e:
                QMessageBox.critical(self, "Erro", "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
                return

            # self.limpar()
            self.fill_table2()
            self.quantidade.setValue(0.00)
            self.habilita_desabilita_impressao()

    def habilita_desabilita_impressao(self):

        self.printPOS.setEnabled(not self.tabelavazia())
        self.printA4.setEnabled(not self.tabelavazia())
        self.action_remover_linha.setEnabled(not self.tabelavazia())
        self.action_remover.setEnabled(not self.tabelavazia())

    def verifica_cliente(self, nome):

        if nome == "":
            print("Nao Econtrado o Cliente.")
            return False

        sql = """select cod, nome from clientes WHERE nome="{}" """.format(nome)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            return False

        return True

    def existeproduto(self, codproduto, codstock, codarmazem):

        sql = """SELECT cod from cozinhadetalhe WHERE codcozinha="{codstock}" and codproduto = "{codproduto}"
            and codarmazem="{codarmazem}" """.format(codstock=str(codstock), codproduto=codproduto,
                                                     codarmazem=codarmazem)

        print("Existe", sql)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            return False
        else:
            return True

    def gravadetalhes(self):
        try:
            codcozinha = self.codigogeral
            codproduto = self.codproduto

            if self.quantidade.value() == 0.00:
                quantidade =  decimal.Decimal(self.quantidade_unitaria)
            else:
                quantidade = decimal.Decimal(self.quantidade.value())

            if self.preco.value() == 0.00:
                preco = decimal.Decimal(self.preco.value())
            else:
                preco = decimal.Decimal(self.preco.value())

            custo = quantidade * preco
            desconto = 0.00

            subtotal = preco * quantidade
            total = subtotal

            lucro = 0.00
            taxa = 0.00
        except Exception as e:
            QMessageBox.critical(self, "Erro grave", "Aconteceu erro grave nos seus dados. verifique-os.\n{}".format(e))
            return

        # Verifica a Existencia do Produto na tabela cozinhadetalhe
        if self.existeproduto(codproduto, codcozinha, self.codarmazem) is True:
            sql = """ UPDATE cozinhadetalhe set custo={custo}, preco={preco}, quantidade={quantidade}, 
            subtotal={subtotal}, desconto={desconto}, taxa={taxa}, total={total}, lucro={lucro}, codarmazem="{codarmazem}" 
            WHERE (codcozinha="{codcozinha}" AND codproduto="{codproduto}" AND codarmazem="{codarmazem}") 
            """.format(codcozinha=codcozinha, codproduto=codproduto, custo=custo, preco=preco,
                       quantidade=quantidade, subtotal=subtotal, desconto=desconto, taxa=taxa,
                       total=total, lucro=lucro, codarmazem=self.codarmazem)
            self.alterar_quantidade = False
        else:
            values = """ "{codcozinha}", "{codproduto}", {custo}, {preco}, {quantidade}, {subtotal}, {desconto}, 
            {taxa}, {total}, {lucro}, "{codarmazem}", "{numero_da_mesa}" """.format(codcozinha=codcozinha, codproduto=codproduto, custo=custo,
                                               preco=preco, quantidade=quantidade, subtotal=subtotal,
                                               desconto=desconto, taxa=taxa, total=total, lucro=lucro,
                                                                                 codarmazem=self.codarmazem, numero_da_mesa=self.numero_da_mesa)

            sql = """INSERT INTO cozinhadetalhe (codcozinha, codproduto, custo, preco, quantidade, subtotal, 
            desconto, taxa, total, lucro, codarmazem, mesa ) values({values}) """.format(values=values)

        try:
            self.cur.execute(sql)
        except Exception as e:
            QMessageBox.critical(self, "Erro", "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
            return

    def resizeEvent(self, *args, **kwargs):
        try:
            self.tv.setColumnWidth(0, self.tv.width() * .1)
            self.tv.setColumnWidth(1, self.tv.width() * .4)
            self.tv.setColumnWidth(2, self.tv.width() * .1)
            self.tv.setColumnWidth(3, self.tv.width() * .1)
            self.tv.setColumnWidth(4, self.tv.width() * .3)
        except Exception as e:
            print(e)

        # Metodo que busca dados na Base de Dados e enche nos Campos do formulario

    def fill_data(self):
        if self.codigogeral == "":
            return

        self.codproduto = self.current_id2

        sql = """ SELECT cozinhadetalhe.codproduto, cozinhadetalhe.preco, cozinhadetalhe.quantidade,
            cozinhadetalhe.total FROM cozinhadetalhe INNER JOIN produtos 
            ON cozinhadetalhe.codproduto=produtos.cod
           WHERE (cozinhadetalhe.codcozinha="{cod}" and cozinhadetalhe.codproduto="{codproduto}") or 
           (cozinhadetalhe.codcozinha="{cod}" and produtos.cod_barras="{cod_barras}")
           """.format(cod=self.codigogeral, codproduto=self.current_id2, cod_barras=self.current_id2,)

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        print('fill data', self.current_id2, data)
        if len(data) == 0:
            return

        self.preco.setValue(decimal.Decimal(data[0][1]))
        self.quantidade.setValue(decimal.Decimal(data[0][2]))
        self.total.setValue(decimal.Decimal(data[0][3]))
        self.quantidade.setFocus()

    def clickedslot2(self, index):

        self.row = int(index.row())

        indice = self.tm2.index(self.row, 1)
        self.current_id2 = indice.data()

        self.codproduto = self.current_id2

        self.codarmazem = self.parent().codarmazem

        self.fill_data()

    def mostrar_teclado(self):
        from teclado_alfanumerico import Teclado
        tc = Teclado(self.find_w)
        tc.setModal(True)
        tc.show()

    def create_toolbar(self):
        print("Create ToolBar...")

        boldfont = QFont('Consolas', 18)

        self.find_w = QLineEdit(self)
        self.find_w.setFont(boldfont)
        self.find_w.setPlaceholderText("Procurar no Stock")
        self.find_w.setMaximumWidth(200)
        btn_teclado = QPushButton("...")
        btn_teclado.setFont(boldfont)

        btn_teclado.setDefault(False)
        btn_teclado.clicked.connect(self.mostrar_teclado)

        self.ok = QAction(QIcon('./images/editedit.png'), qApp.tr("Gravar/Sair"), self)
        self.delete = QAction(QIcon('./images/editdelete.png'), qApp.tr("Eliminar"), self)
        self.printA4 = QAction(QIcon('./images/fileprint.png'), qApp.tr("Imprimir A4"), self)
        self.printPOS = QAction(QIcon("./icons/documentos.ico"), qApp.tr("Imprimir\nPOS(F2)"), self)
        self.printPOS.setEnabled(False)
        self.printA4.setEnabled(False)
        self.printA4.setVisible(False)
        self.update = QAction(QIcon('./images/pencil.png'), qApp.tr("Editar"), self)
        self.delete.setVisible(False)
        self.armazem_combo = QComboBox(self)
        self.armazem_combo.setVisible(False)
        self.armazem_combo.currentIndexChanged.connect(self.fill_table)

        ok = RibbonButton(self, self.ok, True)
        # print_a4 = RibbonButton(self, self.printA4, True)
        print_pos = RibbonButton(self, self.printPOS, True)

        self.tool = QToolBar()
        self.tool.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.tool.addWidget(self.find_w)
        self.tool.addWidget(btn_teclado)
        self.tool.addWidget(self.armazem_combo)
        self.tool.addSeparator()
        self.tool.addWidget(ok)
        # self.tool.addWidget(print_a4)
        self.tool.addWidget(print_pos)

        ######################################################################
        self.ok.triggered.connect(self.close)
        self.printPOS.triggered.connect(self.imprime_pos)
        self.printA4.triggered.connect(self.impremeA4)

    def impremeA4(self):
        try:
            self.imprime_recibo_grande2(self.codigogeral)
        except Exception as e:
            QMessageBox.warning(self, "Erro na criação de Documento",
                                "Houve erro na tentativa de criar Documento para imprimir. {}.".format(e))

    def  imprime_pos(self):
        try:
            if self.parent().copias_pos2 > 0:
                for x in range(self.parent().copias_pos2):
                    self.segundavia_POS(self.codigogeral)

        except Exception as e:
            QMessageBox.warning(self, "Erro na criação de Documento",
                                "Houve erro na tentativa de criar Documento para imprimir. {}.".format(e))

    def segundavia_POS(self, codigo):

        sql = """SELECT c.numero, p.nome, cd.quantidade, cd.total, c.mesa FROM cozinha c
        INNER JOIN cozinhadetalhe cd ON c.cod=cd.codcozinha
        INNER JOIN produtos p ON p.cod=cd.codproduto WHERE c.cod = '{}' """.format(codigo)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        # LOGOTIPO
        html = """
                           < table
                               width = "100%" >
                               < tr >
                                   < td >
                                   < img src = '{}' width = "80" >
                                   < / td >
                               </ tr >
                           < / table >
                           """.format(self.parent().empresa_logo)
        html = ""

        if self.parent() is not None:
            html += "<div style='width:100%; border:1px solid;'>"
            html += "<center> {} </center>".format(self.parent().empresa)
            html += "<center> {} </center>".format(self.parent().empresa_endereco)
            if self.parent().empresa_nuit != "":
                html += "<center> NUIT: {} </center>".format(self.parent().empresa_nuit)
            html += "<center> Contactos: {} </center>".format(self.parent().empresa_contactos)
        else:
            html = "<center> [Nome da Empresa] </center>"
            html += "<center> [Endereco] </center>"
            html += "<center> [NUIT] </center>"
            html += "<center> [CONTACTOS] </center>"

        # html += "<p align='right'> {}: {}/{}{}</p>".format(data[0][2], data[0][1], data[0][23], data[0][22])
        html += "<br/>"
        html += "<hr/>"
        html += "<center> PEDIDO nº {} - MESA: {} </center>".format(data[0][0], data[0][4])
        html += "<hr/>"
        html += "<p align='right'>{}</p>".format(HORA)
        html += "<p align='right'>Usuário: {}</p>".format(self.parent().parent().user)

        html += "<table border='0' width = 80mm style='border: thin;'>"

        html += "<tr>"

        if self.coddocumento != 'DC20185555555':
            html += "<th width = 60%>Descrição</th>"
            html += "<th width = 10%>Qt.</th>"
            html += "<th width = 20% align='right'>TOTAL</th>"

        else:
            html += "<th width = 80%>Descrição</th>"
            html += "<th width = 20%>Qt.</th>"
            html += "<th width = 20% align='right'>TOTAL</th>"

        html += "</tr>"

        total = 0

        for cliente in data:
            total += cliente[3]
            html += """<tr> <td>{}</td> <td>{}</td> <td>{}</td> </tr> """.format(cliente[1], cliente[2], cliente[3])

        html += "</table>"

        html += "<hr/>"

        html += "<table>"
        html += """<tr> <td>TOTAL</td> <td></td> <td>{}</td> </tr> """.format(total)
        html += "</table>"

        html += "<hr/>"
        html += "<p> {}</p>".format(self.parent().contas)
        html += "<p> Processado por Computador  </p>".format(self.parent().licenca)
        html += "</div>"

        printer = QPrinter()
        printer.setPrinterName(self.parent().pos2)

        # printer.setFullPage(True)
        # printer.setPaperSource(printer.Auto)

        printer.setResolution(72)
        printer.setPaperSize(QSizeF(self.parent().papel_2,  3276), printer.Millimeter)
        printer.setPageMargins(0, 0, 10, 0, QPrinter.Millimeter)
        document = QTextDocument()
        # font = document.defaultFont()
        # s = font.toString().split(",")
        # # document.setDefaultFont(QFont("{}".format(s[0]), 6))
        document.setHtml(html)
        document.setPageSize(QSizeF(printer.pageRect().size()))

        dialog = QPrintDialog()
        document.print_(printer)
        dialog.accept()
        self.close()

    def imprime_recibo_grande2(self, codigo):
        if codigo == "":
            return

        sql = """SELECT * FROM cozinha WHERE cod = '{}' """.format(codigo)

        print('Imprimir', sql)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        logo = os.path.realpath(self.parent().empresa_logo)
        empresa = self.parent().empresa
        endereco = self.parent().empresa_endereco
        contactos = self.parent().empresa_contactos
        web = '{}, {}'.format(self.parent().empresa_email, self.parent().empresa_web)
        nuit = self.parent().empresa_nuit
        casas = self.parent().empresa_casas_decimais
        licenca = self.parent().licenca
        contas = self.parent().contas

        if len(data) > 0:
            doc = "{}/{}{}".format(data[0][1], data[0][23], data[0][22])
            try:
                data_doc = datetime.datetime.strptime(str(data[0][3]), "%Y-%m-%d").strftime("%d-%m-%Y")
            except ValueError:
                data_doc = ""

            try:
                vencimento = datetime.datetime.strptime(str(data[0][28]), "%Y-%m-%d").strftime("%d-%m-%Y")
            except ValueError:
                vencimento = ""

            line = []
            if self.parent().incluir_iva == 0:
                for item in data:
                    line += [{'item': {'name': item[15], 'reference': item[16],
                                       'price': decimal.Decimal(item[19]), 'armazem': data[0][30]},
                              'quantity': decimal.Decimal(item[21] / item[16]),
                              'amount': decimal.Decimal(item[21])}, ]
            else:
                for item in data:
                    line += [{'item': {'name': item[15], 'reference': item[16],
                                       'price': decimal.Decimal(item[19]), 'armazem': data[0][30]},
                              'quantity': decimal.Decimal(item[17]),
                              'amount': decimal.Decimal(item[20]), 'armazem': data[0][30]},]

            inv = Invoice(customer={'name': 'Orlando Vilanculo',
                                    'address': {'street': 'Smirnov street', 'zip': 1000, 'city': 'Montreux'}},
                          clienteweb=data[0][13],
                          clienteendereco=data[0][11],
                          clientenome=data[0][10],
                          clientenuit=data[0][12],
                          clientecontactos=data[0][27],
                          empresanome=empresa,
                          empresaendereco=endereco,
                          empresanuit=nuit,
                          empresacontactos=contactos,
                          empresaweb=web,
                          contas=contas,
                          licenca=licenca,
                          vencimento=vencimento,
                          lines=line,
                          id=doc,
                          status='late',
                          doc=data[0][2],
                          datadoc=data_doc,
                          operador=data[0][4],
                          obs=data[0][29],
                          subtotal=data[0][5],
                          desconto=data[0][6],
                          iva=data[0][7],
                          totalgeral=data[0][8],

                          )

            # Verifica o Ficheiro de entrada Template
            filename = os.path.realpath('template.odt')
            if os.path.isfile(filename) is False:
                QMessageBox.critical(self, "Erro ao Imprimir",
                                     "O ficheiro modelo '{}'  não foi encontrado.".format(filename))
                return

            # Verifica o ficheiro de saida
            if self.coddocumento == "DC20185555555":
                targetfile = self.parent().req_template
            else:
                targetfile = self.parent().fact_template

            if os.path.isfile(targetfile) is False:
                QMessageBox.critical(self, "Erro ao Imprimir",
                                     "O ficheiro modelo '{}'  não foi encontrado. \n "
                                     "Reponha-o para poder Imprimir".format(targetfile))
                return

            basic = Template(source='', filepath=targetfile)
            open(filename, 'wb').write(basic.generate(o=inv).render().getvalue())

            doc_out = cd("0123456789") + "{}{}{}{}".format(data[0][2], data[0][1], data[0][23], data[0][22])
            out = os.path.realpath("'{}'.pdf".format(doc_out))


            printWordDocument(filename, out)

    def enterEvent(self, *args, **kwargs):
        self.fill_table()

    def incrimenta(self, ano, coddocumento):
        sql = """select max(numero) from cozinha WHERE ano={ano} and 
           coddocumento="{coddoc}" """.format(ano=ano, coddoc=coddocumento)


        try:
            self.cur.execute(sql)
            data = self.cur.fetchall()
        except Exception as e:
            return

        if data[0][0] is None or data[0][0]== 0:
            self.numero = 1
        else:
            self.numero = data[0][0] + 1

    def enche_armazem(self):
        sql = """SELECT nome from armazem WHERE estado=1 and cod<>"{}" order by nome""".format(self.numero_da_mesa)

        self.cur.execute(sql)
        data = self.cur.fetchall()
        self.armazem_combo.clear()
        lista = []

        if len(data) > 0:
            for item in data:

                lista.append(item[0])

        # lista.append("Todos")
        self.armazem_combo.addItems(lista)

    def create_statusbar(self):
        estado = QStatusBar(self)

        self.items = QLabel("Total Items: %s" % self.totalItems)
        estado.addWidget(self.items)
        self.setStatusBar(estado)

    def clickedslot(self, index):

        self.row = int(index.row())

        indice = self.tm.index(self.row, 0)
        cod = self.tm.index(self.row, 4)
        self.getcodarmazem(cod.data())
        print('codigo ', cod.data(),self.codarmazem)

        self.current_id = indice.data()

        self.codproduto = self.current_id

        preco = self.tm.index(self.row, 2)
        quantidade = self.tm.index(self.row, 3)

        try:
            self.preco_unitario = decimal.Decimal(preco.data())
            self.quantidade_unitaria = decimal.Decimal(quantidade.data())

            self.preco.setValue(self.preco_unitario)
            self.quantidade.setValue(1.00)
            self.calculatotal(self.preco_unitario, decimal.Decimal(self.quantidade.value()))
            # self.action_adicionar.click()
            self.quantidade.setFocus()

        except Exception as e:
            print(e)

    def calculatotal(self, preco, quantidade):

        self.total.setValue(decimal.Decimal(preco) * decimal.Decimal(quantidade))

    def remove_record(self):
        print("Admin: ", self.admin, "Gestor: ", self.gestor)
        if self.gestor or self.admin is False:
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

    # Apaga a Linha na tabela facturadetalhe
    def remove_row(self):

        if (self.parent().gestor or self.parent().admin) is False:
            return False

        sql = """delete from facturacaodetalhe WHERE codproduto="{codigo}" and codfacturacao="{cod}"
        """.format(codigo=str(self.codproduto), cod=self.parent().codigogeral)

        try:
            self.cur.execute(sql)
            return True
        except Exception as e:
            print(e)
            return False

        # Apaga a Linha na tabela facturadetalhe

    def remove_all(self):

        if (self.parent().gestor or self.parent().admin) is False:
            return False

        print("Removendo Tudo....")
        sql = """SELECT codproduto from cozinhadetalhe WHERE codcozinha ="{}" """.format(self.codigogeral)

        self.cur.execute(sql)
        data = self.cur.fetchall()
        print(data)

        if len(data) > 0:
            for cod in data:
                sql = """delete from facturacaodetalhe WHERE codproduto="{codigo}" and codfacturacao="{cod}"
                """.format(codigo=str(cod[0]), cod=self.parent().codigogeral)

                print(sql)
                self.cur.execute(sql)

        return True

    def removerow(self):

        if self.current_id2 is None or self.current_id2 == "":
            QMessageBox.information(self, "Info", "Selecione o registo a apagar na tabela")
            return

        sql = """delete from cozinhadetalhe WHERE codproduto="{codigo}" and codcozinha="{cod}"
                and codarmazem="{codarmazem}" """.format(codigo=str(self.current_id2), cod=self.codigogeral,
                                                         codarmazem=self.codarmazem)
        try:
            self.cur.execute(sql)
            self.remove_row()
            self.conn.commit()

        except Exception as e:
            QMessageBox.warning(self, "Impossivel apagar dados", "Impossivel apagar dados."
                                                                 " Erro: {erro}".format(erro=e))
            return

        if self.tabelavazia() is True:
            sql = """ delete from cozinha WHERE cod= '{}' """.format(self.codigogeral)
            self.cur.execute(sql)
            self.conn.commit()

        self.habilita_desabilita_impressao()
        self.fill_table2()

        self.parent().fill_table()
        self.parent().cod_line.setFocus()
        self.parent().calcula_total_geral()
        self.parent().habilitar_butoes(True)

        # Apaga a Linha na tabela facturadetalhe

        # Verifica se a tabela está vazia ou não

    def tabelavazia(self):

        if self.codigogeral == "":
            return

        sql = """ SELECT * from cozinhadetalhe WHERE codcozinha="{cod}" """.format(cod=self.codigogeral)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            return True
        else:
            return False

    def removeall(self):

        if self.existe(self.codigogeral):
            sql = """DELETE from cozinhadetalhe WHERE codcozinha="{}" """.format(self.codigogeral)
            sql2 = """DELETE from cozinha WHERE cod="{}" """.format(self.codigogeral)

            self.remove_all()
            self.cur.execute(sql)
            self.cur.execute(sql2)
            self.conn.commit()

            self.fill_table2()

            self.preco.setValue(0.00)
            self.quantidade.setValue(1.00)
            self.habilita_desabilita_impressao()

            self.parent().label_total.setText("0.00")
            self.parent().calcula_total_geral()
            self.parent().fill_table()

            self.parent().habilitar_butoes(False)
            self.parent().butao_editar.setEnabled(False)

    def add_record_produto(self):

        if self.codproduto == "":
            return

        # Verifica a quantidade Existente na Base de dados, e colhe preco e custo
        self.parent().verifica_existencia()

        if self.parent().alterar_quantidade is False:
            self.quantidade_unitario = 1

        # Se o tipo de produto for Produto e não Servico
        if int(self.parent().tipo_produto) == 0:

            if self.parent().get_quantidade_facturacao(self.parent().codigogeral, self.codproduto) is False:
                QMessageBox.warning(self, "Quantidade inexistente", "Quantidade não existe na Base de dados.\n"
                                                                    "Existência {}".format(self.quantidade_existente))
                return

        v = self.valortaxa()

        valortaxa = decimal.Decimal(v / 100)

        code = self.parent().codigogeral
        numero = 0
        # data = QDate.currentDate().toString('yyyy-MM-dd')
        coddocumento = self.parent().coddocumento
        codcliente = self.parent().codcliente

        quantidade = decimal.Decimal(self.quantidade.value())
        preco = decimal.Decimal(self.preco_unitario)
        custo = self.parent().custoproduto * quantidade
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

        caixa = self.parent().caixa_numero

        if self.parent() is not None:
            modified_by = self.parent().user
        else:
            modified_by = self.user
        if self.parent() is not None:
            created_by = self.parent().user
        else:
            created_by = self.user

        if self.parent().existe(self.parent().codigogeral) is True:

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
                        total=total, lucro=lucro, debito=pago, credito=0.00, troco=troco, banco=banco,
                        cash=cash, tranferencia=tranferencia, estado=estado, ano=ano,
                        mes=mes, obs=obs, created=created, modified=modified, modified_by=modified_by,
                        created_by=created_by, caixa=caixa)

            sql = """INSERT INTO facturacao (cod, numero, coddocumento ,codcliente, data, custo, subtotal,
            desconto, taxa, total,  lucro, debito, credito,troco, banco, cash, tranferencia, estado, ano, mes, 
            obs, created, modified, modified_by, created_by, caixa) values({value})""".format(value=values)

        try:

            print(sql)

            self.cur.execute(sql)
            # Grava detalhes do documento mas depende da tabela mae facturacao
            self.gravadetalhes_produtos()
        except Exception as e:
            QMessageBox.critical(self, "Erro",
                                 "Os seus dados não foram gravados. Erro: {erro}, created: {c} ".format(erro=e,
                                                                                                        c=created))
            return

        self.parent().alterar_quantidade = False
        # self.codproduto = ""
        self.parent().fill_table()
        self.parent().cod_line.setFocus()
        self.parent().calcula_total_geral()
        self.parent().habilitar_butoes(True)

    # Grava as linhas dos produtos na tabela facturacaodetalhe
    def gravadetalhes_produtos(self):

        codfacturacao = self.parent().codigogeral
        codproduto = self.codproduto
        valorcusto = decimal.Decimal(self.parent().custoproduto)

        quantidade = decimal.Decimal(self.quantidade.value())

        # Calculo de valores para a base de dados
        preco = decimal.Decimal(self.preco_unitario)
        desconto = decimal.Decimal(0.00)
        custo = quantidade * valorcusto

        valortaxa = decimal.Decimal(self.valortaxa() / 100)
        valordesconto = quantidade * preco * desconto

        subtotal = quantidade * preco - valordesconto
        taxa = valortaxa * quantidade * preco
        total = subtotal + taxa

        lucro = subtotal - custo

        # Verifica a Existencia do Produto na tabela facturacaodetalhe
        if self.parent().existeproduto(codproduto, codfacturacao) is True:

            if self.alterar_quantidade is True:
                sql = """ UPDATE facturacaodetalhe set custo={custo}, preco={preco},quantidade={quantidade}, 
                                subtotal={subtotal}, desconto={desconto}, taxa={taxa}, total={total}, lucro={lucro},
                                codarmazem="{codarmazem}" 
                                WHERE (codfacturacao="{codfacturacao}" and codproduto="{codproduto}") 
                                """.format(codfacturacao=codfacturacao, codproduto=codproduto, custo=custo, preco=preco,
                                           quantidade=quantidade, subtotal=subtotal, desconto=valordesconto, taxa=taxa,
                                           total=total, lucro=lucro, codarmazem=self.codarmazem)
            else:

                sql = """ UPDATE facturacaodetalhe set custo=custo+{custo}, preco={preco},
                quantidade=quantidade+{quantidade}, subtotal=subtotal+{subtotal}, desconto=desconto+{desconto}, 
                taxa=taxa+{taxa}, total=total+{total}, lucro=lucro+{lucro}, codarmazem="{codarmazem}" WHERE 
                (codfacturacao="{codfacturacao}" 
                and codproduto="{codproduto}") """.format(codfacturacao=codfacturacao, codproduto=codproduto,
                                                          custo=custo, preco=preco, quantidade=quantidade,
                                                          subtotal=subtotal, desconto=valordesconto, taxa=taxa,
                                                          total=total, lucro=lucro, codarmazem=self.codarmazem)

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

    def valortaxa(self):

        sql = """SELECT codtaxa from produtos WHERE cod="{}" """.format(self.codproduto)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            return decimal.Decimal(0)

        sql = """SELECT valor from taxas WHERE cod="{}" """.format(data[0][0])

        self.cur.execute(sql)
        data = self.cur.fetchall()

        return decimal.Decimal(data[0][0])


if __name__ == '__main__':
    app = QApplication(sys.argv)
#
    helloPythonWidget = Pedidos()
    helloPythonWidget.show()
#
    sys.exit(app.exec_())

