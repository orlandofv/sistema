import datetime
import decimal
from time import localtime, strftime
import sys
import os
import subprocess
from utilities import printWordDocument, Invoice

from PyQt5.QtWidgets import (QLineEdit, QToolBar, QMessageBox, qApp, QAction, QApplication, QGroupBox, QPushButton,
                             QComboBox, QDialog, QFormLayout, QHBoxLayout, QTableView, QCheckBox, QAbstractItemView,
                             QSplitter, QStatusBar, QVBoxLayout, QLabel)

from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter, QPrintDialog, QPrinterInfo
from PyQt5.QtGui import QIcon, QTextDocument, QBrush

from PyQt5.QtCore import Qt, QDate, QSizeF

from sortmodel import MyTableModel
from utilities import codigo as cd
from pricespinbox import price
from relatorio.templates.opendocument import Template

from produtos import Produto as prod

DATA_HORA_FORMATADA = strftime("%Y-%m-%d %H:%M:%S", localtime())
DATA_ACTUAL = datetime.date.today()
ANO_ACTUAL = DATA_ACTUAL.year
DIA = DATA_ACTUAL.day
MES = DATA_ACTUAL.month


#Classe que representa a Lista de Produtos
class Requiscao(QDialog):
    def __init__(self, parent=None):
        super(Requiscao, self).__init__(parent)

        # controla o codigo
        self.current_id = ""
        self.current_id2 = ""
        self.empresa_host = "127.0.0.1"
        self.empresa_user = "root"
        self.empresa_passw = "abc123@123"
        self.empresa_db = "copia"
        self.empresa_port = 3306
        self.coddocumento = "DC20185555555"
        self.codarmazem2 = ""
        self.numero = 0

        self.codcliente = ""

        self.codigogeral = "FT" + cd("FT" + "abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")
        self.preco_unitario = 0.00
        self.quantidade_unitaria = 0.00
        self.valor_total = 0.00

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

        # create the view
        self.tv = QTableView(self)

        # set the minimum size
        self.tv.setMinimumSize(400, 300)

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
        self.tabela.setMinimumSize(400, 300)

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

        self.butao_adicionar = QPushButton(QIcon('./icons/add_2.ico'), "")
        self.butao_adicionar.setDefault(True)
        self.butao_adicionar.clicked.connect(self.add_record)
        self.butao_remover_linha = QPushButton(QIcon('./icons/remove.ico'), "")
        self.butao_remover_linha.setEnabled(False)
        self.butao_remover_linha.clicked.connect(self.removerow)
        self.butao_remover = QPushButton(QIcon('./images/editdelete.png'), "")
        self.butao_remover.setEnabled(False)
        self.butao_remover.clicked.connect(self.removeall)

        self.quantidade = price()

        self.quantidade.valueChanged.connect(lambda: self.calculatotal(self.preco.value(), self.quantidade.value()))
        self.preco = price()
        self.total = price()

        armazembox = QVBoxLayout()
        armazembox.addWidget(self.tv)

        formlay = QFormLayout()
        formlay.addRow(QLabel("Qty"), self.quantidade)
        formlay.addRow(QLabel("Preço"), self.preco)
        formlay.addRow(QLabel("Total"), self.total)
        armazembox.addLayout(formlay)

        butonbox = QVBoxLayout()
        butonbox.addSpacing(150)
        butonbox.addWidget(self.butao_adicionar)
        butonbox.addWidget(self.butao_remover_linha)
        butonbox.addWidget(self.butao_remover)
        butonbox.addSpacing(150)

        hlay = QHBoxLayout()
        hlay.addLayout(armazembox)
        hlay.addLayout(butonbox)
        hlay.addWidget(self.tabela)

        mainlay = QVBoxLayout()
        mainlay.addWidget(self.tool)
        mainlay.addLayout(hlay)


        self.setLayout(mainlay)
        #centralwidget.setLayout(mainlay)

        # self.setCentralWidget(centralwidget)
        # self.create_toolbar()

    def focusInEvent(self, evt):
        self.fill_table()


    def doc_finalizado(self, finalizado=0):
        if finalizado == 1:
            self.tv.setEnabled(False)
            self.tabela.setEnabled(False)
            self.butao_adicionar.setEnabled(False)
            self.butao_remover.setEnabled(False)
            self.butao_remover_linha.setEnabled(False)
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
            self.codarmazem1 = ""
            return

        sql = """SELECT cod from armazem WHERE nome="{}" """.format(nomearmazem)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        print(nomearmazem)
        if len(data) > 0:
            self.codarmazem1 = data[0][0]

    def fill_table(self):

        if self.armazem_combo.currentText() == "Todos":

            self.sql = """SELECT produtos.cod, produtos.nome, MAX(produtos.preco), SUM(stockdetalhe.quantidade), 
                    armazem.nome from produtos
                             INNER JOIN stockdetalhe ON produtos.cod=stockdetalhe.codproduto 
                             INNER JOIN armazem ON armazem.cod=stockdetalhe.codarmazem
                             WHERE (produtos.nome
                             like "%{nome}%" or produtos.cod_barras like "%{cod_barras}%" or produtos.cod like "%{preco}%") 
                            
                             GROUP BY produtos.cod""".format(nome=self.find_w.text(), cod_barras=self.find_w.text(),
                                                             preco=self.find_w.text())
        else:
            armazem = self.armazem_combo.currentText()

            self.sql = """SELECT produtos.cod, produtos.nome, MAX(produtos.preco), SUM(stockdetalhe.quantidade), 
            armazem.nome from produtos
                     INNER JOIN stockdetalhe ON produtos.cod=stockdetalhe.codproduto 
                     INNER JOIN armazem ON armazem.cod=stockdetalhe.codarmazem
                     WHERE (produtos.nome
                     like "%{nome}%" or produtos.cod_barras like "%{cod_barras}%" or produtos.cod like "%{preco}%") 
                     and armazem.nome="{armazem}"  
                     GROUP BY produtos.cod""".format(nome=self.find_w.text(), cod_barras=self.find_w.text(),
                                                     preco=self.find_w.text(), armazem=armazem)

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
            self.tv.setColumnWidth(0, self.tv.width()*.1)
            self.tv.setColumnWidth(1, self.tv.width() * .4)
            self.tv.setColumnWidth(2, self.tv.width() * .1)
            self.tv.setColumnWidth(3, self.tv.width() * .1)
            self.tv.setColumnWidth(4, self.tv.width() * .3)
        except Exception as e:
            return
        # # set row height
        nrows = len(self.tabledata)
        for row in range(nrows):
            self.tv.setRowHeight(row, 25)
        # self.create_statusbar()

        # Encontra o codigo do armazem
        self.getcodarmazem(self.armazem_combo.currentText())


    def fill_table2(self):

        header = ["DOC", "Cód.", "Descrição", "Qty", "Armazém", "codarmazem"]

        sql = """ select requisicao.cod, requisicaodetalhe.codproduto, produtos.nome, requisicaodetalhe.quantidade,  
           armazem.nome, armazem.cod from produtos, requisicao, requisicaodetalhe, armazem 
           WHERE (produtos.cod=requisicaodetalhe.codproduto 
           AND requisicao.cod=requisicaodetalhe.codrequisicao AND armazem.cod=requisicaodetalhe.codarmazem1) AND 
           (requisicao.cod="{requisicaocod}") """.format(requisicaocod=self.codigogeral)

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

        try:
            # set the table model
            self.tm2 = MyTableModel(self.tabledata, header, self)
            self.totalItems = self.tm2.rowCount(self)
            self.tabela.setModel(self.tm2)
            self.tabela.setColumnHidden(0, True)
            self.tabela.setColumnWidth(1, self.tabela.width()*.1)
            self.tabela.setColumnWidth(2, self.tabela.width()*.5)
            self.tabela.setColumnWidth(3, self.tabela.width() * .1)
            self.tabela.setColumnWidth(4, self.tabela.width() * .3)
            self.tabela.setColumnHidden(5, True)

        except Exception as e:
            print(e)
            return
        # # set row height
        nrows = len(self.tabledata)
        for row in range(nrows):
            self.tabela.setRowHeight(row, 25)

    def validacaodetalhes(self):

        self.quantidade_unitaria = self.quantidade.value()
        self.preco_unitario = self.preco.value()

        if self.quantidade_unitaria <= 0:
            return  False
        else:
            return True

    def existe(self, codigo):

        sql = """SELECT cod from requisicao WHERE cod = "{codigo}" """.format(codigo=str(codigo))

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            return False
        else:
            return True

    def grava_cliente(self):

        code = self.codarmazem2

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

                sql = """UPDATE requisicao set custo=custo+{custo}, subtotal=subtotal+{subtotal}, 
                desconto=desconto+{desconto}, taxa=taxa+{taxa}, total=total+{total}, lucro=lucro+{lucro} 
                WHERE cod="{cod}" """.format(cod=code, custo=custo, subtotal=subtotal, desconto=desconto,
                                            taxa=taxa, total=total, lucro=lucro)
            else:
                values = """ "{cod}", {numero}, "{coddocumento}", "{codcliente}", "{data}", {custo}, {subtotal}, 
                {desconto}, {taxa}, {total}, {lucro}, {debito},{credito}, {troco}, {banco}, {cash}, {tranferencia}, {estado}, 
                {ano}, {mes}, "{obs}", "{created}", "{modified}", "{modified_by}", "{created_by}", "{caixa}", "{codarmazem}", {finalizado}
                 """.format(cod=code, numero=numero, coddocumento=coddocumento, codcliente=codcliente,
                            data=data, custo=custo, subtotal=subtotal, desconto=desconto, taxa=taxa,
                            total=total, lucro=lucro, debito=pago, credito= 0.00,troco=troco, banco=banco,
                            cash=cash, tranferencia=tranferencia, estado=estado,ano=ano,
                            mes=mes, obs=obs, created=created, modified=modified, modified_by=modified_by,
                            created_by=created_by, caixa=self.caixa_numero, codarmazem=self.codarmazem2, finalizado=1)

                sql = """ INSERT INTO requisicao (cod, numero, coddocumento ,codcliente, data, custo, subtotal,
                 desconto, taxa, total,  lucro, debito, credito,troco, banco, cash, tranferencia, estado, ano, mes, 
                 obs, created, modified, modified_by, created_by, caixa, codarmazem, finalizado) values({value})""".format(value=values)


            try:

                self.cur.execute(sql)
                # Grava detalhes do documento mas depende da tabela mae requisicao
                self.gravadetalhes()

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
        self.butao_remover_linha.setEnabled(not self.tabelavazia())
        self.butao_remover.setEnabled(not self.tabelavazia())

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

        sql = """SELECT cod from requisicaodetalhe WHERE codrequisicao="{codstock}" and codproduto = "{codproduto}"
            and codarmazem1="{codarmazem}" """.format(codstock=str(codstock), codproduto=codproduto,
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
            codrequisicao = self.codigogeral
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

        # Verifica a Existencia do Produto na tabela requisicaodetalhe
        if self.existeproduto(codproduto, codrequisicao, self.codarmazem1) is True:
            sql = """ UPDATE requisicaodetalhe set custo={custo}, preco={preco}, quantidade={quantidade}, 
            subtotal={subtotal}, desconto={desconto}, taxa={taxa}, total={total}, lucro={lucro}, codarmazem1="{codarmazem}" 
            WHERE (codrequisicao="{codrequisicao}" AND codproduto="{codproduto}" AND codarmazem1="{codarmazem}") 
            """.format(codrequisicao=codrequisicao, codproduto=codproduto, custo=custo, preco=preco,
                       quantidade=quantidade, subtotal=subtotal, desconto=desconto, taxa=taxa,
                       total=total, lucro=lucro, codarmazem=self.codarmazem1)
            self.alterar_quantidade = False
        else:
            values = """ "{codrequisicao}", "{codproduto}", {custo}, {preco}, {quantidade}, {subtotal}, {desconto}, 
            {taxa}, {total}, {lucro}, "{codarmazem}", "{codarmazem2}" """.format(codrequisicao=codrequisicao, codproduto=codproduto, custo=custo,
                                               preco=preco, quantidade=quantidade, subtotal=subtotal,
                                               desconto=desconto, taxa=taxa, total=total, lucro=lucro,
                                                                                 codarmazem=self.codarmazem1, codarmazem2=self.codarmazem2)

            sql = """INSERT INTO requisicaodetalhe (codrequisicao, codproduto, custo, preco, quantidade, subtotal, 
            desconto, taxa, total, lucro, codarmazem1, codarmazem2 ) values({values}) """.format(values=values)

        print('detalhes:  ', sql)
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

        sql = """ SELECT requisicaodetalhe.codproduto, requisicaodetalhe.preco, requisicaodetalhe.quantidade,
            requisicaodetalhe.total FROM requisicaodetalhe INNER JOIN produtos 
            ON requisicaodetalhe.codproduto=produtos.cod
           WHERE (requisicaodetalhe.codrequisicao="{cod}" and requisicaodetalhe.codproduto="{codproduto}") or 
           (requisicaodetalhe.codrequisicao="{cod}" and produtos.cod_barras="{cod_barras}") 
           """.format(cod=self.codigogeral, codproduto=self.current_id2, cod_barras=self.current_id2)

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        print('fill data', self.current_id2, data)
        if len(data) == 0:
            return

        if decimal.Decimal(data[0][2]) > 0:
            self.quantidade.setMaximum(decimal.Decimal(data[0][2]))
        else:
            self.quantidade.setMinimum(0.00)
            self.quantidade.setMaximum(0.00)

        self.preco.setValue(decimal.Decimal(data[0][1]))
        self.quantidade.setValue(decimal.Decimal(data[0][2]))
        self.total.setValue(decimal.Decimal(data[0][3]))
        self.quantidade.setFocus()

    def setmaxquantidade(self):
        sql = """SELECT SUM(quantidade) from stockdetalhe WHERE codproduto="{}" 
        and codarmazem="{}" """.format(self.current_id2, self.codarmazem1)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        print(sql, data)

        if len(data) > 0:
            self.quantidade.setMinimum(0.00)
            self.quantidade.setMaximum(decimal.Decimal(data[0][0]))

    def clickedslot2(self, index):

        self.row = int(index.row())

        indice = self.tm2.index(self.row, 1)
        self.current_id2 = indice.data()

        self.codproduto = self.current_id2

        codarmazem = self.tm2.index(self.row, 5)
        self.codarmazem1 = codarmazem.data()

        self.fill_data()

    def create_toolbar(self):
        find = QLabel(qApp.tr("Procurar") + "  ")
        self.find_w = QLineEdit(self)
        self.find_w.setPlaceholderText("Procurar no Stock")
        self.find_w.setMaximumWidth(200)

        self.ok = QAction(QIcon('./images/editedit.png'), qApp.tr("Gravar/Sair"), self)
        self.delete = QAction(QIcon('./images/editdelete.png'), qApp.tr("Eliminar"), self)
        self.printA4 = QAction(QIcon('./images/fileprint.png'), qApp.tr("Imprimir A4/Finalizar"), self)
        self.printPOS = QAction(QIcon("./icons/documentos.ico"), qApp.tr("Imprimir POS/Finalizar"), self)
        self.printPOS.setEnabled(False)
        self.printA4.setEnabled(False)
        self.update = QAction(QIcon('./images/pencil.png'), qApp.tr("Editar"), self)
        self.delete.setVisible(False)
        self.armazem_combo = QComboBox(self)
        self.armazem_combo.currentIndexChanged.connect(self.fill_table)

        self.tool = QToolBar()
        self.tool.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.tool.addWidget(find)
        self.tool.addWidget(self.find_w)
        self.tool.addWidget(QLabel("  Armazém "))
        self.tool.addWidget(self.armazem_combo)
        self.tool.addSeparator()
        self.tool.addAction(self.ok)
        # tool.addAction(self.update)
        # tool.addSeparator()
        #tool.addAction(self.delete)
        # tool.addSeparator()
        self.tool.addAction(self.printA4)
        self.tool.addAction(self.printPOS)

        # self.tool.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        # self.addToolBarBreak(Qt.BottomToolBarArea)
        # self.addToolBar(selftool)

        ######################################################################
        self.ok.triggered.connect(self.close)
        # self.delete.triggered.connect(self.removerow)
        # self.tv.doubleClicked.connect(self.update_data)
        # self.update.triggered.connect(self.update_data)
        # self.connect(self.delete, SIGNAL("triggered()"), self.removerow)
        # # self.connect(self.update, SIGNAL("triggered()"), self.updatedata)
        self.printPOS.triggered.connect(self.imprimePOS)
        self.printA4.triggered.connect(self.impremeA4)

    def impremeA4(self):
        try:
            self.imprime_recibo_grande2(self.codigogeral)
        except Exception as e:
            QMessageBox.warning(self, "Erro na criação de Documento",
                                "Houve erro na tentativa de criar Documento para imprimir. {}.".format(e))

    def  imprimePOS(self):
        try:
            self.segundavia_POS(self.codigogeral)
        except Exception as e:
            QMessageBox.warning(self, "Erro na criação de Documento",
                                "Houve erro na tentativa de criar Documento para imprimir. {}.".format(e))

    def segundavia_POS(self, codigo):

        sql = """SELECT * FROM factura_geral WHERE codrequisicao = '{}' """.format(codigo)

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

        if self.parent() is not None:
            html += "<center> {} </center>".format(self.parent().empresa)
            html += "<center> {} </center>".format(self.parent().empresa_endereco)
            html += "<center> NUIT: {} </center>".format(self.parent().empresa_nuit)
            html += "<center> Contactos: {} </center>".format(self.parent().empresa_contactos)
        else:
            html += "<center> [Nome da Empresa] </center>"
            html += "<center> [Endereco] </center>"
            html += "<center> [NUIT] </center>"
            html += "<center> [CONTACTOS] </center>"

        html += "<p align='right'> {}: {}/{}{}</p>".format(data[0][2], data[0][1], data[0][23], data[0][22])
        html += "<p align='right'>DATA: {}</p>".format(data[0][3])

        html += "<p>Exmo(a) Sr.(a): {}</p>".format(data[0][10])

        html += "<hr/>"

        html += "<table border='0' width = 80mm style='border: thin;'>"
        html += "<tr>"

        if self.coddocumento != 'DC20185555555':
            html += "<th width = 60%>Descrição</th>"
            html += "<th width = 10%>Qt.</th>"
            html += "<th width = 10%>Preço.</th>"
            html += "<th width = 20% align='right'>Total</th>"

        else:
            html += "<th width = 80%>Descrição</th>"
            html += "<th width = 20%>Qt.</th>"

        html += "</tr>"

        for cliente in data:
            if self.coddocumento != 'DC20185555555':
                html += """<tr> <td>{}</td> <td>{}</td> <td align="right">{}</td> <td align="right">{}</td> </tr>
                                           """.format(cliente[15], cliente[16], cliente[17], cliente[21])
            else:
                html += """<tr> <td>{}</td> <td>{}</td> </tr>
                                                           """.format(cliente[15], cliente[16])

        html += "</table>"

        html += "<table>"

        if self.coddocumento != 'DC20185555555':
            html += "<tr>"
            html += "<td width = 50% align='right'>SUBTOTAL</td>"
            html += "<td width = 50% align='right'>{:20,.{casas}f} </td>".format(cliente[5],
                                                                                 casas=self.parent().empresa_casas_decimais)
            html += "<tr>"
            html += "<td width = 50% align='right'>IVA(17%)</td>"
            html += "<td width = 50% align='right'>{:20,.{casas}f} </td>".format(cliente[7],
                                                                                 casas=self.parent().empresa_casas_decimais)
            html += "<tr>"
            html += "<th width = 50% align='right'>TOTAL</th>"
            html += "<td width = 50% align='right'>{:20,.{casas}f} </td>".format(cliente[8],
                                                                                 casas=self.parent().empresa_casas_decimais)
            html += "</tr>"

        html += "</table>"

        html += "<hr/>"
        html += "<p> {}</p>".format(self.parent().contas)
        html += "<p> Processado por Computador  </p>".format(self.parent().licenca)

        document = QTextDocument()
        document.setHtml(html)

        printer = QPrinter()
        info = QPrinterInfo.defaultPrinter().printerName()

        printer.setResolution(printer.HighResolution)
        printer.setPaperSize(QSizeF(self.parent().papel_1,  1000), printer.Millimeter)
        printer.setPrinterName(self.parent().pos1)
        dialog = QPrintDialog()
        dialog.setContentsMargins(0, 0, 0, 0)
        # printer.setOutputFormat(QPrinter.PdfFormat)
        # printer.setOutputFileName("{}.pdf".format(data[0][0]))
        # printer.setPageMargins(0, 0, 10, 0, QPrinter.Millimeter)
        document.setPageSize(QSizeF(printer.pageRect().size()))
        # document.setDocumentMargin(0)
        document.print_(printer)
        dialog.accept()

    def imprime_recibo_grande2(self, codigo):
        if codigo == "":
            return

        sql = """SELECT * FROM factura_geral WHERE codrequisicao = '{}' """.format(codigo)

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

    def incrimenta(self, ano, coddocumento):
        sql = """select max(numero) from requisicao WHERE ano={ano} and 
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
        sql = """SELECT nome from armazem WHERE estado=1 and cod<>"{}" order by nome""".format(self.codarmazem2)

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
        print('codigo ', cod.data(),self.codarmazem1)

        self.current_id = indice.data()

        self.codproduto = self.current_id

        preco = self.tm.index(self.row, 2)
        quantidade = self.tm.index(self.row, 3)

        try:
            self.preco_unitario = decimal.Decimal(preco.data())
            self.quantidade_unitaria = decimal.Decimal(quantidade.data())

            if self.quantidade_unitaria > 0:
                self.quantidade.setMaximum(self.quantidade_unitaria)
            else:
                self.quantidade.setMinimum(0.00)
                self.quantidade.setMaximum(0.00)

            self.preco.setValue(self.preco_unitario)
            self.quantidade.setValue(1.00)
            self.calculatotal(self.preco_unitario, decimal.Decimal(self.quantidade.value()))
            self.butao_adicionar.click()
            self.quantidade.setFocus()

        except Exception as e:
            print(e)

    def calculatotal(self, preco, quantidade):

        self.total.setValue(decimal.Decimal(preco) * decimal.Decimal(quantidade))

    def new_data(self):

        cl = prod(self)
        cl.setModal(True)
        cl.show()

    def update_data(self):

        if self.current_id == "":
            QMessageBox.information(self, "Info", "Selecione o registo a actualizar na tabela")
            return

        cl = prod(self)
        cl.cod.setText(self.current_id)
        cl.mostrar_registo()
        cl.setModal(True)
        cl.show()

    def removerow(self):

        if self.current_id2 == "":
            QMessageBox.information(self, "Info", "Selecione o registo a apagar na tabela")
            return

        sql = """delete from requisicaodetalhe WHERE codproduto="{codigo}" and codrequisicao="{cod}"
                and codarmazem1="{codarmazem}" """.format(codigo=str(self.current_id2), cod=self.codigogeral,
                                                         codarmazem=self.codarmazem1)
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            QMessageBox.warning(self, "Impossivel apagar dados", "Impossivel apagar dados."
                                                                 " Erro: {erro}".format(erro=e))
            return

        if self.tabelavazia() is True:
            sql = """ delete from requisicao WHERE cod= '{}' """.format(self.codigogeral)
            self.cur.execute(sql)
            self.conn.commit()

        self.habilita_desabilita_impressao()
        self.fill_table2()

        # Apaga a Linha na tabela facturadetalhe

        # Verifica se a tabela está vazia ou não

    def tabelavazia(self):

        if self.codigogeral == "":
            return

        sql = """ SELECT * from requisicaodetalhe WHERE codrequisicao="{cod}" """.format(cod=self.codigogeral)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            return True
        else:
            return False

    def removeall(self):

        if self.existe(self.codigogeral):
            sql = """DELETE from requisicaodetalhe WHERE codrequisicao="{}" """.format(self.codigogeral)
            sql2 = """DELETE from requisicao WHERE cod="{}" """.format(self.codigogeral)

            self.cur.execute(sql)
            self.cur.execute(sql2)
            self.conn.commit()

            self.fill_table2()

            self.preco.setValue(0.00)
            self.quantidade.setValue(1.00)
            self.habilita_desabilita_impressao()


if __name__ == '__main__':
    app =QApplication(sys.argv)
    main_form = Requiscao()
    main_form.show()
    app.exec_()