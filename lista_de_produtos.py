# -*- coding: utf-8 -*-

import sys
import  subprocess
import csv
import os
from decimal import Decimal
from PyQt5.QtWidgets import QApplication, QSplitter, QMessageBox, QToolBar, \
    QLineEdit, QLabel, QStatusBar, QAction, QMainWindow, qApp, QTabWidget, QDateEdit, QCalendarWidget, \
    QProgressDialog, QFileDialog, QComboBox, QHBoxLayout, QWidget, QTreeView, QAbstractItemView

from PyQt5.QtGui import QIcon, QTextDocument
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtPrintSupport import QPrintPreviewDialog

from sortmodel import MyTableModel
from treeview_test import *

from produtos import Produto
from utilities import codigo as cd
from utilities import DATA_HORA_FORMATADA, HORA
from striped_table import StripedTable

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.__familia = None
        self.__subfamilia = None

        self.empresa = None
        # controla o codigo
        self.current_id = ""
        self.produtos_sql = ""
        self.zero_stock_sql = ""
        self.mais_vendido_sql = ""
        self.stock_negativo_sql = ""
        self.stock_semsaida_sql = ""
        self.cod_armazem = None

        # Connect the Database
        if self.parent() is None:
            self.db = self.connect_db()
            self.user = ""
        else:
            self.conn = self.parent().conn
            self.cur = self.parent().cur
            self.cur2 = self.parent().cur
            self.user = self.parent().user
            self.setWindowIcon(self.parent().windowIcon())

        # Create the main user interface
        self.ui()

        self.fill_produtos_table()

        self.tab.tabBarClicked.connect(lambda: print(self.tab.currentIndex()))
        self.find_w.textChanged.connect(self.fill_produtos_table)
        self.find_w.textChanged.connect(self.fill_maisvendido_table)
        self.find_w.textChanged.connect(self.fill_zerostock_table)
        self.find_w.textChanged.connect(self.fill_negativestock_table)
        self.find_w.textChanged.connect(self.fill_semsaida_table)


    def get_familiacod(self, nome_familia):
        sql = """select cod from familia WHERE nome="{}" """.format(nome_familia)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return data[0][0]

        return None

    def get_subfamiliacod(self, nome_subfamilia):
        sql = """select cod from subfamilia WHERE nome="{}" """.format(nome_subfamilia)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return data[0][0]

        return None

    def resizeEvent(self, QResizeEvent):
        gm = self.frameGeometry()
        self.treeview.setMaximumWidth(gm.width()/6)

    def ui(self):

        self.treeview = QTreeView(self)
        self.treeview.clicked.connect(self.clicked_slot)
        self.treeview.setMaximumWidth(400)

        self.treeview.setSelectionBehavior(QAbstractItemView.SelectRows)
        # set the font

        # set horizontal header properties and stretch last column
        hh = self.treeview.header()
        hh.setVisible(False)

        self.treeview.setAlternatingRowColors(True)

        # create the view
        self.tv = StripedTable(self)
        self.tv.clicked.connect(self.clickedslot)

        spliter = QSplitter()

        spliter.addWidget(self.treeview)
        spliter.addWidget(self.tv)

        # create the view
        self.mais_vendido_tv = StripedTable(self)
        self.mais_vendido_tv.clicked.connect(self.clickedslot)

        # create the view
        self.zero_stock_tv = StripedTable(self)
        self.zero_stock_tv.clicked.connect(self.clickedslot)

        # create the view
        self.stock_negativo_tv = StripedTable(self)

        self.stock_negativo_tv.clicked.connect(self.clickedslot)

        # create the view
        self.stock_semsaida_tv = StripedTable(self)
        self.stock_semsaida_tv.clicked.connect(self.clickedslot)

        self.tab = QTabWidget()
        self.tab.tabBarClicked.connect(self.mudar_datas)
        self.tab.addTab(spliter, "Lista Geral de Produtos/Serviços")
        self.tab.addTab(self.mais_vendido_tv, "Produtos/Serviços mais vendidos")
        self.tab.addTab(self.zero_stock_tv, "Produtos com Stock Zero")
        self.tab.addTab(self.stock_negativo_tv, "Produtos com Stock Negativo")
        self.tab.addTab(self.stock_semsaida_tv, "Produtos sem Saída")

        self.setCentralWidget(self.tab)

        self.create_toolbar()
        self.enche_armazem()
        self.fill_grid()

    def fill_grid(self):

        items = []
        items.append(CustomNode("Todos Items"))

        sql_familias = "SELECT cod, nome FROM familia"

        self.cur.execute(sql_familias)
        data = self.cur.fetchall()

        for x in data:
            items.append(CustomNode(x[1]))
            sql_subfamilias = """SELECT nome FROM subfamilia WHERE codfamilia="{}" """.format(x[0])
            self.cur.execute(sql_subfamilias)
            data_1 = self.cur.fetchall()

            for y in data_1:
                items[-1].addChild(CustomNode(y))

        self.add_data(items)

    def add_data(self, data):

        self.cm = CustomModel(data)
        self.treeview.setModel(self.cm)
        h = self.treeview.header()
        h.setHidden(True)
        self.treeview.setUniformRowHeights(50)

    def clicked_slot(self, val):
        # print(val.data())
        # print(val.row())
        # print(val.column())

        current_index = self.treeview.currentIndex()

        if current_index.parent().data() is None:
            if val.data() == "Todos Items":
                self.fill_produtos_table()
                self.__familia = None
                self.__subfamilia = None
            else:
                self.__familia = self.get_familiacod(val.data())
                self.__subfamilia = None
                self.fill_produtos_table(self.__familia)
        else:
            self.__familia = self.get_familiacod(current_index.parent().data())
            self.__subfamilia = self.get_subfamiliacod(val.data())
            self.fill_produtos_table(self.__familia, self.__subfamilia)

    def create_toolbar(self):

        self.find_w = QLineEdit(self)
        self.find_w.setPlaceholderText("Procurar")
        self.find_w.setMaximumWidth(200)
        self.procurar = QAction(QIcon('./icons/zoom.ico'), "", self)
        self.armazem_combo = QComboBox()
        self.armazem_combo.currentTextChanged.connect(lambda: self.get_codarmazem(self.armazem_combo.currentText()))

        self.new = QAction(QIcon('./icons/add_2.ico'), qApp.tr("Novo"), self)
        self.delete = QAction(QIcon('./images/editdelete.png'), qApp.tr("Eliminar"), self)
        self.imprimir = QAction(QIcon('./images/fileprint.png'), qApp.tr("Imprimir"), self)
        self.update = QAction(QIcon('./images/pencil.png'), qApp.tr("Editar"), self)
        export_csv = QAction(QIcon('./images/icons8-export-csv-50.png'), "Exportar para CSV", self)
        export_csv_simples = QAction(QIcon('./images/icons8-export-csv-50.png'), "Lista Normal para CSV", self)
        import_csv = QAction(QIcon('./images/icons8-import-csv-50.png'), "Importar de CSV", self)
        relacoes = QAction(QIcon('./icons/relacoes.ico'), "Links", self)

        calendar1 = QCalendarWidget()
        calendar2 = QCalendarWidget()
        self.data_inicial = QDateEdit()
        self.data_inicial.setDate(QDate.currentDate().addDays(-30))
        self.data_inicial.setCalendarPopup(True)
        self.data_inicial.setCalendarWidget(calendar1)
        self.data_final = QDateEdit()
        self.data_final.setDate(QDate.currentDate())
        self.data_final.setCalendarPopup(True)
        self.data_final.setCalendarWidget(calendar2)

        tool = QToolBar()
        tool.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        tool.addWidget(self.find_w)
        # tool.addAction(self.procurar)
        tool.addSeparator()
        tool.addAction(self.new)
        tool.addAction(self.update)
        tool.addSeparator()
        tool.addAction(self.delete)

        tool2 = QToolBar()
        tool2.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        tool2.addAction(self.imprimir)
        tool2.addSeparator()
        tool2.addAction(export_csv)
        tool2.addAction(export_csv_simples)
        tool2.addAction(import_csv)
        tool2.addSeparator()
        tool2.addAction(relacoes)

        datas_lay = QHBoxLayout()

        datas_lay.addWidget(QLabel(" Data Inicial: "))
        datas_lay.addWidget(self.data_inicial)
        datas_lay.addWidget(QLabel(" Data Final: "))
        datas_lay.addWidget(self.data_final)
        self.datas_widget = QWidget()
        self.datas_widget.setLayout(datas_lay)
        tool.addWidget(self.datas_widget)
        tool.addWidget(QLabel("Armazém "))
        tool.addWidget(self.armazem_combo)

        tool.setAllowedAreas(Qt.TopToolBarArea|Qt.BottomToolBarArea)
        self.addToolBar(Qt.TopToolBarArea, tool)
        self.addToolBarBreak(Qt.TopToolBarArea)
        self.addToolBar(Qt.BottomToolBarArea, tool2)
        
        self.new.triggered.connect(self.new_data)
        self.delete.triggered.connect(self.removerow)
        self.tv.doubleClicked.connect(self.update_data)
        self.update.triggered.connect(self.update_data)
        self.imprimir.triggered.connect(self.imprime_lista_de_produtos)
        import_csv.triggered.connect(self.importar_csv)
        export_csv.triggered.connect(self.exportar_csv)
        export_csv_simples.triggered.connect(self.imprime_produtos)
        relacoes.triggered.connect(self.relacoes)

    def keyPressEvent(self, QKeyEvent) -> None:
        if QKeyEvent.key() in (Qt.Key_Enter, 16777220):
            self.update_data()
        else:
            QKeyEvent.ignore()

    def relacoes(self):
        from relacoes import Relacoes

        rl = Relacoes(self)
        rl.setModal(True)
        rl.fill_produtos()
        rl.show()

    def mudar_datas(self):
        if self.tab.currentIndex() == 0:
            self.datas_widget.setVisible(False)
        else:
            self.datas_widget.setVisible(True)

    def enche_armazem(self):
        sql = """SELECT nome from armazem WHERE estado=1 order by nome"""

        self.cur.execute(sql)
        data = self.cur.fetchall()
        self.armazem_combo.clear()
        lista = []

        if len(data) > 0:
            for item in data:
                lista.append(item[0])

        lista.append("Todos")
        self.armazem_combo.addItems(lista)

    def exportar_csv(self):

        if self.tab.currentIndex() == 0:
            self.exportar_stock_csv()
        elif self.tab.currentIndex() == 1:
            self.exportar_maisvendido_csv()
        elif self.tab.currentIndex() == 2:
            self.exportar_zerostock_csv()
        elif self.tab.currentIndex() == 3:
            self.exportar_negativo_csv()
        elif self.tab.currentIndex() == 4:
            self.exportar_semsaida_csv()
        else:
            QMessageBox.warning(self, "Aviso","Esta função aplica-se a todas outras abas excepto a aba corrente!!")

    def get_tamanho_do_ficheiro(self, ficheiro):
        try:
            f = open(ficheiro)
            tamanho = f.readlines()
            return len(tamanho)
        except Exception as e:
            print(e)
            return False

    def get_codarmazem(self, nome_armazem):
        codarmazem = None

        if nome_armazem == "Todos" or nome_armazem == "":
            return codarmazem

        sql = """SELECT cod FROM armazem WHERE nome="{}" """.format(nome_armazem)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            codarmazem = data[0][0]

        self.cod_armazem = codarmazem

        return codarmazem

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


    def tamanho_lista_armazem(self):
        """
        Metodo que retorna o tamanho da lista de Armazens
        :return: Tamanho de armazem
        """
        sql = """SELECT cod from armazem"""
        self.cur.execute(sql)
        data = self.cur.fetchall()

        lista = []

        for l in data:
            lista.append(l[0])

        return len(lista)

    def existe_codstock(self, codstock):
        sql =  """SELECT cod from stock WHERE cod="{}" """.format(codstock)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return True

        return False

    def importar_csv(self):
        import codecs
        from decimal import Decimal

        formats = "Ficheiros CSV(*.csv)"
        self.path = "."

        dialog = QFileDialog(self)
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        filename = dialog.getOpenFileName(self, "Escolha o Ficheiro", self.path, formats)

        cod_stock = "ST" + cd("ST" + "abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")
        cod_fornecedor = "FR20181111111"

        armazem = self.get_codarmazem(self.armazem_combo.currentText())

        if armazem is False:
            QMessageBox.warning(self, "Escolha o Armazém", "Escolha apenas 1 (um)  Armazém.")
            return False

        if filename:
            tamanho = self.get_tamanho_do_ficheiro(filename[0])
            print(tamanho)
        else:
            QMessageBox.warning(self, "Erro do Ficheiro", "Ficheiro Inválido")
            return False

        progress = QProgressDialog(self)
        progress.setMinimum(0)
        progress.setMaximum(0)
        progress.setModal(True)
        progress.setWindowTitle("Importando Items")
        progress.show()

        try:
            produtos_list_sql = []
            produtos_detalhe_list_sql = []
            stock_detalhe_list = []

            if filename:

                ficheiro = codecs.open(filename[0], encoding='utf-8')

                tamanho_de_armazens = self.tamanho_lista_armazem()
                progress.setMaximum((tamanho-1) * tamanho_de_armazens)

                count = 0
                count_progress = 0
                for row in csv.reader(ficheiro):
                    print(row)

                    # Se não for o cabecalho do ficheito
                    if count > 0:
                        cod = str(row[0])
                        nome = str(row[1])
                        cod_barras = str(row[2])
                        codfamilia = str(row[3])
                        codsubfamilia = str(row[4])
                        custo = Decimal(row[5])
                        preco = Decimal(row[6])
                        quantidade = Decimal(row[7])
                        quantidade_m = Decimal(row[8])
                        unidade = str(row[9])
                        obs = str(row[10])
                        estado = int(row[11])
                        foto = str(row[12])
                        created = QDate.currentDate().toString('yyyy-MM-dd')
                        modified = QDate.currentDate().toString('yyyy-MM-dd')
                        modified_by = self.user
                        created_by = self.user

                        # created = str(row[13])
                        # modified = str(row[14])
                        # modified_by = str(row[15])
                        # created_by = str(row[16])
                        preco1 = Decimal(row[17])
                        preco2 = Decimal(row[18])
                        preco3 = Decimal(row[19])
                        preco4 = Decimal(row[20])
                        tipo = int(row[21])
                        codtaxa = str(row[22])
                        quantidade_max = Decimal(row[23])
                        favorito = int(row[24])
                        promocao = int(row[25])
                        preco_de_venda = int(row[26])

                        data = QDate.currentDate().toString('yyyy-MM-dd')
                        subtotal = custo * quantidade
                        taxa = Decimal(17 / 100) * subtotal
                        total = subtotal + taxa

                        taxa_geral = Decimal(0)
                        subtotal_geral = Decimal(0)
                        total_geral = Decimal(0)

                        if str(row[27]) == "":
                            validade = QDate.currentDate().addDays(30).toString("yyyy-MM-dd")
                        else:
                            validade = str(row[27])

                        if self.armazem_combo.currentText() == "Todos":
                            for codarmazem in self.lista_armazem():
                                sql_detalhes = """REPLACE INTO produtosdetalhe (codproduto, codarmazem, quantidade, created, modified, 
                                                                modified_by, created_by, validade, contagem) VALUES ("{codproduto}", "{codarmazem}", {quantidade}, 
                                                                "{created}", "{modified}", "{modified_by}", "{created_by}", "{validade}", 0)""".format(
                                    codproduto=cod, codarmazem=codarmazem,
                                    quantidade=quantidade, created=created,
                                    modified=modified,
                                    modified_by=modified_by, created_by=created_by,
                                    validade=validade)

                                stock_detalhe_values = """ "{codstock}", "{codproduto}", "{codarmazem}", {quantidade},
                                "{validade}",{valor}, {taxa}, {subtotal}, 
                                {total} """.format(codstock=cod_stock, codproduto=cod, codarmazem=codarmazem,
                                                   quantidade=quantidade, validade=validade, valor=custo, taxa=taxa,
                                                   subtotal=subtotal, total=total)

                                sql_stockdetalhe = """INSERT INTO stockdetalhe (codstock, codproduto, codarmazem, 
                                quantidade, validade, valor, taxa, subtotal, total) 
                                values({value})""".format(value=stock_detalhe_values)

                                produtos_detalhe_list_sql.append(sql_detalhes)
                                stock_detalhe_list.append(sql_stockdetalhe)

                                taxa_geral += taxa
                                subtotal_geral += subtotal
                                total_geral += total

                                print(sql_detalhes)

                                count_progress += 1
                                progress.setValue(count_progress)
                                progress.setLabelText("Adicnonando: {} :{}".format(nome, quantidade))

                        else:
                            for codarmazem in self.lista_armazem():
                                if codarmazem == armazem:
                                    q = quantidade
                                else:
                                    q = 0

                                subtotal = custo * q
                                taxa = Decimal(17 / 100) * subtotal
                                total = subtotal + taxa

                                sql_detalhes = """REPLACE INTO produtosdetalhe (codproduto, codarmazem, quantidade, created, modified, 
                                modified_by, created_by, validade, contagem) VALUES ("{codproduto}", "{codarmazem}", {quantidade}, 
                                "{created}", "{modified}", "{modified_by}", "{created_by}", "{validade}", 0)""".format(
                                                                        codproduto=cod, codarmazem=codarmazem,
                                                                        quantidade=q, created=created,
                                                                        modified=modified,
                                                                        modified_by=modified_by, created_by=created_by,
                                                                        validade=validade)

                                stock_detalhe_values = """ "{codstock}", "{codproduto}", "{codarmazem}", {quantidade},
                                "{validade}",{valor}, {taxa}, {subtotal}, 
                                {total} """.format(codstock=cod_stock, codproduto=cod, codarmazem=codarmazem,
                                                   quantidade=q, validade=validade, valor=custo, taxa=taxa,
                                                   subtotal=subtotal, total=total)

                                sql_stockdetalhe = """INSERT INTO stockdetalhe (codstock, codproduto, codarmazem, 
                                quantidade, validade, valor, taxa, subtotal, total) values({value})""".format(
                                value=stock_detalhe_values)

                                taxa_geral += taxa
                                subtotal_geral += subtotal
                                total_geral += total

                                print(sql_detalhes)
                                produtos_detalhe_list_sql.append(sql_detalhes)
                                stock_detalhe_list.append(sql_stockdetalhe)

                                count_progress += 1
                                progress.setValue(count_progress)
                                progress.setLabelText("Adicnonando: {} :{}".format(nome, q))

                        values = """ "{cod}",  "{nome}", "{cod_barras}", "{codfamilia}", "{codsubfamilia}", {custo},
                        {preco}, {quantidade}, {quantidade_m}, "{unidade}", "{obs}", {estado}, "{foto}", 
                        "{created}", "{modified}", "{modified_by}", "{created_by}", {preco1}, {preco2}, {preco3}, 
                        {preco4}, {tipo}, "{codtaxa}", {quantidade_max}, {favorito}, {promocao}, {preco_de_venda} 
                        """.format(cod=cod, nome=nome, cod_barras=cod_barras,
                                                                   codfamilia=codfamilia,
                                                                   codsubfamilia=codsubfamilia, custo=custo, preco=preco,
                                                                   quantidade=quantidade,
                                                                   quantidade_m=quantidade_m, unidade=unidade, obs=obs,
                                                                   estado=estado, foto=foto,
                                                                   created=created, modified=modified,
                                                                   modified_by=modified_by, created_by=created_by,
                                                                   preco1=preco1, preco2=preco2, preco3=preco3,
                                                                   preco4=preco4, tipo=tipo, codtaxa=codtaxa,
                                                                   quantidade_max=quantidade_max, favorito=favorito,
                                                                   promocao=promocao,
                                                                   preco_de_venda=preco_de_venda)

                        sql = """REPLACE INTO produtos VALUES ({value})""".format(value=values)
                        produtos_list_sql.append(sql)

                    count += 1

                numero_doc = "STOCK INICIAL {}".format(created)

                values = """ "{cod}", "{fornecedor}", "{numero}", "{data}", {total}, {iva}, {subtotal}, {saldo}, 
                "{created}", "{modified}", "{modified_by}", "{created_by}", {estado} 
                """.format(cod=cod_stock, fornecedor=cod_fornecedor, numero=numero_doc, data=created,
                           total=total_geral, iva=taxa_geral, subtotal=subtotal_geral, created=data, modified=modified,
                           modified_by=modified_by, created_by=created_by, saldo=total_geral, estado=1)

                sql_stock = """INSERT INTO stock (cod, fornecedor, numero, data, total, taxa, subtotal, saldo, created,
                                    modified, modified_by, created_by, estado) values({value})""".format(value=values)

                for x in produtos_list_sql:
                    self.cur.execute(x)

                for y in produtos_detalhe_list_sql:
                    self.cur.execute(y)

                self.cur.execute(sql_stock)

                for z in stock_detalhe_list:
                    self.cur.execute(z)

                self.conn.commit()

                progress.close()
                QMessageBox.information(self, "Sucesso!!", "{} Items importados com sucesso.".format(tamanho-1))
            else:
                QMessageBox.warning(self, "Escolha o Ficheiro", 'Nenhum ficheiro escolhido')
                return False

        except Exception as e:
            progress.close()
            self.conn.rollback()
            print("Erro, {}.".format(e.args))
            QMessageBox.warning(self, "Erro ao recarregar o Ficheiro", "Aconteceu um erro: {}.".format(e))
            return False

        return True

    def gravar_stock(self,codstock, cod, custo, quantidade, validade, created_by, armazem):

        cod_stock = codstock
        cod_fornecedor = "FR20181111111"
        data = QDate.currentDate().toString('yyyy-MM-dd')
        custo = custo
        quantidade = quantidade
        subtotal = custo * quantidade
        taxa = Decimal(17/100) * subtotal
        total = subtotal + taxa
        codproduto = cod
        validade = validade
        created_by = modified_by = created_by

        numero_doc = "STOCK INICIAL {}".format(data)

        values = """ "{cod}", "{fornecedor}", "{numero}", "{data}", {total}, {iva}, {subtotal}, {saldo}, 
                    "{created}", "{modified}", "{modified_by}", "{created_by}", {estado} 
                    """.format(cod=cod_stock, fornecedor=cod_fornecedor, numero=numero_doc, data=data, total=total,
                               iva=taxa, subtotal=subtotal, created=data, modified=data,
                               modified_by=modified_by, created_by=created_by, saldo=total, estado=1)

        sql_stock = """INSERT INTO stock (cod, fornecedor, numero, data, total, taxa, subtotal, saldo, created,
                    modified, modified_by, created_by, estado) values({value})""".format(value=values)

        sql_list = []

        for codarmazem in self.lista_armazem():
            if codarmazem == armazem:
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

        # Grava se não existir o codigo
        if self.existe_codstock(codstock) is False:
            self.cur.execute(sql_stock)

        for x in sql_list:
            self.cur.execute(x)

    def cancel_operation(self, window):
        window.setModal(False)

    def exportar_zerostock_csv(self):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(self, 'Guardar Ficheiro', '.', filter='Ficheiros CSV(*.csv)')

        if filename:
            ficheiro = filename
        else:
            QMessageBox.warning(self, 'Gravar Ficheiro', 'Ficheiro não foi gravado')
            return

        if ficheiro.endswith('.csv') is False:
            ficheiro += '.csv'

        caminho = os.path.realpath(ficheiro)

        self.cur.execute(self.zero_stock_sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        csv_header = [qApp.tr('Código'), qApp.tr('Descrição'), qApp.tr('Quantidade')]

        action_label = QLabel("Exportando produtos. Aguarde.....")

        progressbar = QProgressDialog()
        progressbar.setLabel(action_label)
        progressbar.setMinimum(0)
        progressbar.setModal(True)
        progressbar.setCancelButtonText("Aguarde....")
        progressbar.setWindowTitle("Exportando para CSV")

        count = 0
        try:
            with open(ficheiro, 'w', newline='', encoding='utf8') as lista_produtos:
                csv_write = csv.writer(lista_produtos, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_write.writerow(csv_header)
                progressbar.show()
                progressbar.setValue(1)

                if len(data) > 0:
                    progressbar.setMaximum(len(data))
                    for x in data:
                        count += 1
                        progressbar.setValue(count)
                        lista = list(x)
                        csv_write.writerow(lista)

                        action_label.setText("Exportando: {}. {}".format(count, lista[1]))
                progressbar.close()
                lista_produtos.close()

                subprocess.Popen(caminho, shell=True)

                QMessageBox.information(self, "Successo!", "Processo terminado com Sucesso!!!")
        except Exception as e:
            QMessageBox.warning(self, "Erro", "Erro: {}.\nVeja se o Ficheiro em causa não está aberto.".format(e))

    def fill_treeview(self):

        data_ = self.data_inicial.date().toString('yyyy-MM-dd')
        sql = """SELECT cod, nome FROM familia ORDER BY nome"""
        self.cur.execute(sql)
        self.familia_data = self.cur.fetchall()

        self.familia_list = []
        self.subfamilia_list = []
        self.produtos_list = []

        lista = []

        if len(self.familia_data) > 0:
            for familia in self.familia_data:
                lista.append([familia[1]])
                self.familia_list.append(CustomNode(familia[1]))

                sql = """SELECT cod, nome FROM subfamilia WHERE codfamilia="{}" ORDER BY nome """.format(familia[0])
                self.cur.execute(sql)
                self.subfamilia_data = self.cur.fetchall()
                if len(self.subfamilia_data) > 0:
                    for subfamilia in self.subfamilia_data:
                        lista.append([subfamilia[1]])
                        self.subfamilia_list.append(CustomNode(subfamilia[1]))
                        self.familia_list[-1].addChild(CustomNode(self.subfamilia_list))

                        if self.armazem_combo.currentText() == "Todos":
                            sql = """
                                    SELECT DISTINCT 
                                    p.cod, p.nome, p.cod_barras, p.custo, p.preco, p.preco1, p.preco2, 
                                    p.preco3, p.preco4, 
                                    pd.quantidade + COALESCE(SUM(case when d.stock=1 then fd.quantidade ELSE 0 END), 0) - 
                                    COALESCE(SUM(case when s.estado=1 then sd.quantidade ELSE 0 END), 0) AS qt, 
                                    p.quantidade_m, p.unidade, p.obs
                                    FROM produtos p 
                                                    LEFT JOIN produtosdetalhe pd ON p.cod = pd.codproduto
                                                    LEFT JOIN facturacaodetalhe fd ON p.cod = fd.codproduto
                                                    LEFT JOIN facturacao f ON f.cod = fd.codfacturacao AND f.modified >= '{data}' 
                                                    LEFT JOIN documentos d ON d.cod = f.coddocumento    
                                                    LEFT JOIN stockdetalhe sd ON p.cod = sd.codproduto
                                                    LEFT JOIN stock s ON s.cod = sd.codstock AND s.created < '{data}'

                                    WHERE 
                                        (p.cod LIKE "%{cod}%"
                                    OR    
                                        p.nome LIKE "%{nome}%")
                                    AND  p.codsubfamilia="{sub}"
                                    GROUP BY p.cod 
                                    ORDER BY p.nome
                                    """.format(nome=self.find_w.text(), cod=self.find_w.text(), data=data_,
                                               sub=subfamilia[0])
                        else:
                            sql = """
                                    SELECT DISTINCT 
                        				p.cod, p.nome, p.cod_barras, p.custo, p.preco, p.preco1, p.preco2, 
                        				p.preco3, p.preco4, 
                        				pd.quantidade + COALESCE(SUM(case when d.stock=1 then fd.quantidade ELSE 0 END), 0) - 
                        				COALESCE(SUM(case when s.estado=1 then sd.quantidade ELSE 0 END), 0) AS qt,
                        				p.quantidade_m, p.unidade, p.obs
                                    FROM produtos p 
                                                    LEFT JOIN produtosdetalhe pd ON p.cod = pd.codproduto
                                                    LEFT JOIN facturacaodetalhe fd ON p.cod = fd.codproduto
                                                    LEFT JOIN facturacao f ON f.cod = fd.codfacturacao AND f.modified >= '{data}' 
                                                    LEFT JOIN documentos d ON d.cod = f.coddocumento 
                                                    LEFT JOIN armazem a ON a.cod = fd.codarmazem AND a.nome = "{armazem}"
                                                    LEFT JOIN stockdetalhe sd ON p.cod = sd.codproduto
                                                    LEFT JOIN stock s ON s.cod = sd.codstock AND s.created = '{data}'                         
                                    WHERE 
                                        (p.cod LIKE "%{cod}%"
                                    OR    
                                        p.nome LIKE "%{nome}%")
                                    AND p.codsubfamilia="{sub}"
                                    GROUP BY p.cod 
                                    ORDER BY p.nome
                                    """.format(nome=self.find_w.text(), cod=self.find_w.text(),
                                               armazem=self.armazem_combo.currentText(), data=data_, sub=subfamilia[0])

                        self.cur.execute(sql)
                        self.produto_data = self.cur.fetchall()
                        if len(self.produto_data) > 0:
                            for produto in self.produto_data:
                                lista.append(produto)

                                self.produtos_list.append(CustomNode(produto))

        tv = QTreeView(self)
        tv.setModel(CustomModel(self.familia_data))

    def imprime_produtos(self):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(self, 'Guardar Ficheiro', '.', filter='Ficheiros CSV(*.csv)')

        if filename:
            ficheiro = filename
        else:
            QMessageBox.warning(self, 'Gravar Ficheiro', 'Ficheiro não foi gravado')
            return

        if ficheiro.endswith('.csv') is False:
            ficheiro += '.csv'

        caminho = os.path.realpath(ficheiro)

        action_label = QLabel("Exportando produtos. Aguarde.....")

        progressbar = QProgressDialog()
        progressbar.setLabel(action_label)
        progressbar.setMinimum(0)
        progressbar.setModal(True)
        progressbar.setCancelButtonText("Aguarde....")
        progressbar.setWindowTitle("Exportando para CSV")

        data_ = self.data_inicial.date().toString('yyyy-MM-dd')
        sql = """SELECT cod, nome FROM familia ORDER BY nome"""
        self.cur.execute(sql)
        data = self.cur.fetchall()

        lista = []

        if len(data) > 0:
            for familia in data:
                lista.append([familia[1]])
                sql = """SELECT cod, nome FROM subfamilia WHERE codfamilia="{}" ORDER BY nome """.format(familia[0])
                self.cur.execute(sql)
                self.subfamilia_data = self.cur.fetchall()
                if len(data) > 0:
                    for subfamilia in data:
                        lista.append([subfamilia[1]])
                        if self.armazem_combo.currentText() == "Todos":
                            sql = """
                                    SELECT DISTINCT 
                                    p.cod, p.nome, p.cod_barras, p.custo, p.preco, p.preco1, p.preco2, 
                                    p.preco3, p.preco4, 
                                    pd.quantidade + COALESCE(SUM(case when d.stock=1 then fd.quantidade ELSE 0 END), 0) - 
                                    COALESCE(SUM(case when s.estado=1 then sd.quantidade ELSE 0 END), 0) AS qt, 
                                    p.quantidade_m, p.unidade, p.obs
                                    FROM produtos p 
                                                    LEFT JOIN produtosdetalhe pd ON p.cod = pd.codproduto
                                                    LEFT JOIN facturacaodetalhe fd ON p.cod = fd.codproduto
                                                    LEFT JOIN facturacao f ON f.cod = fd.codfacturacao AND f.modified >= '{data}' 
                                                    LEFT JOIN documentos d ON d.cod = f.coddocumento    
                                                    LEFT JOIN stockdetalhe sd ON p.cod = sd.codproduto
                                                    LEFT JOIN stock s ON s.cod = sd.codstock AND s.created < '{data}'

                                    WHERE 
                                        (p.cod LIKE "%{cod}%"
                                    OR    
                                        p.nome LIKE "%{nome}%")
                                    AND  p.codsubfamilia="{sub}"
                                    GROUP BY p.cod 
                                    ORDER BY p.nome
                                    """.format(nome=self.find_w.text(), cod=self.find_w.text(), data=data_,
                                               sub=subfamilia[0])
                        else:
                            sql = """
                                    SELECT DISTINCT 
                        				p.cod, p.nome, p.cod_barras, p.custo, p.preco, p.preco1, p.preco2, 
                        				p.preco3, p.preco4, 
                        				pd.quantidade + COALESCE(SUM(case when d.stock=1 then fd.quantidade ELSE 0 END), 0) - 
                        				COALESCE(SUM(case when s.estado=1 then sd.quantidade ELSE 0 END), 0) AS qt,
                        				p.quantidade_m, p.unidade, p.obs
                                    FROM produtos p 
                                                    LEFT JOIN produtosdetalhe pd ON p.cod = pd.codproduto
                                                    LEFT JOIN facturacaodetalhe fd ON p.cod = fd.codproduto
                                                    LEFT JOIN facturacao f ON f.cod = fd.codfacturacao AND f.modified >= '{data}' 
                                                    LEFT JOIN documentos d ON d.cod = f.coddocumento 
                                                    LEFT JOIN armazem a ON a.cod = fd.codarmazem AND a.nome = "{armazem}"
                                                    LEFT JOIN stockdetalhe sd ON p.cod = sd.codproduto
                                                    LEFT JOIN stock s ON s.cod = sd.codstock AND s.created = '{data}'                         
                                    WHERE 
                                        (p.cod LIKE "%{cod}%"
                                    OR    
                                        p.nome LIKE "%{nome}%")
                                    AND p.codsubfamilia="{sub}"
                                    GROUP BY p.cod 
                                    ORDER BY p.nome
                                    """.format(nome=self.find_w.text(), cod=self.find_w.text(),
                                               armazem=self.armazem_combo.currentText(), data=data_, sub=subfamilia[0])

                        self.cur.execute(sql)
                        data = self.cur.fetchall()
                        if len(data) > 0:
                            for produto in data:
                                lista.append(produto)

        progressbar.setMaximum(len(lista))
        count = 0

        try:
            with open(ficheiro, 'w', newline='', encoding='utf8') as lista_produtos:
                csv_write = csv.writer(lista_produtos, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_write.writerow([self.empresa])
                csv_write.writerow(['DATA: {}'.format(self.data_final.date().toString('dd-MM-yyyy'))])
                csv_write.writerow([])
                csv_write.writerow(["Cod", "Nome", "Cod de Barras", "Custo", "Preço", "Preço1", "Preço2", "Preço3",
                                    "Preço4", "Quantidade", "Quantidade_m", "Unidade", "Notas"])
                progressbar.show()
                progressbar.setValue(1)

                for x in lista:
                    count += 1
                    progressbar.setValue(count)
                    csv_write.writerow(x)

                    action_label.setText("Exportando: {}. {}".format(count, lista[1]))

                progressbar.close()
                lista_produtos.close()

                subprocess.Popen(caminho, shell=True)

                QMessageBox.information(self, "Successo!", "Processo terminado com Sucesso!!!")

        except Exception as e:
            print(e)

    def exportar_stock_csv(self):

        print("Exportando stock....")
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(self, 'Guardar Ficheiro', '.', filter='Ficheiros CSV(*.csv)')

        if filename:
            ficheiro = filename
        else:
            QMessageBox.warning(self, 'Gravar Ficheiro', 'Ficheiro não foi gravado')
            return

        if ficheiro.endswith('.csv') is False:
            ficheiro += '.csv'

        caminho = os.path.realpath(ficheiro)

        self.cur.execute(self.produtos_sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        action_label = QLabel("Exportando produtos. Aguarde.....")

        progressbar = QProgressDialog()
        progressbar.setLabel(action_label)
        progressbar.setMinimum(0)
        progressbar.setModal(True)
        progressbar.setCancelButtonText("Aguarde....")
        progressbar.setWindowTitle("Exportando para CSV")

        count = 0
        try:
            with open(ficheiro, 'w', newline='', encoding='utf8') as lista_produtos:
                csv_write = csv.writer(lista_produtos, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_write.writerow([self.empresa])
                csv_write.writerow(['DATA: {}'.format(self.data_final.date().toString('dd-MM-yyyy'))])
                csv_write.writerow([])
                csv_write.writerow(['Cod.', 'Produto', 'Qty', 'Custo', 'Preço', 'Custo Total',
                                    'Total Venda', 'Lucro Total'])
                progressbar.show()
                progressbar.setValue(1)

                total_geral = 0
                custo_total = 0
                lucro_total = 0

                if len(data) > 0:
                    progressbar.setMaximum(len(data))
                    for x in data:
                        count += 1
                        progressbar.setValue(count)
                        lista = list(x)
                        custo = float(x[3]) * float(x[9])
                        total = float(x[4]) * float(x[9])
                        lucro = total - custo

                        total_geral += total
                        custo_total += custo
                        lucro_total += lucro

                        nova_lista = [x[0], x[1], x[9], x[3], x[4], custo, total, lucro]

                        csv_write.writerow(nova_lista)

                        action_label.setText("Exportando: {}. {}".format(count, lista[1]))
                    csv_write.writerow(['Total', '', '', '', '', custo_total, total_geral, lucro_total])

                progressbar.close()
                lista_produtos.close()

                subprocess.Popen(caminho, shell=True)

                QMessageBox.information(self, "Successo!", "Processo terminado com Sucesso!!!")
        except Exception as e:
            QMessageBox.warning(self, "Erro", "Erro: {}.\nVeja se o Ficheiro em causa não está aberto.".format(e))

    def exportar_negativo_csv(self):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(self, 'Guardar Ficheiro', '.', filter='Ficheiros CSV(*.csv)')

        if filename:
            ficheiro = filename
        else:
            QMessageBox.warning(self, 'Gravar Ficheiro', 'Ficheiro não foi gravado')
            return

        if ficheiro.endswith('.csv') is False:
            ficheiro += '.csv'

        caminho = os.path.realpath(ficheiro)

        self.cur.execute(self.stock_negativo_sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        csv_header = [qApp.tr('Código'), qApp.tr('Descrição'), qApp.tr('Quantidade') ]

        action_label = QLabel("Exportando produtos. Aguarde.....")

        progressbar = QProgressDialog()
        progressbar.setLabel(action_label)
        progressbar.setMinimum(0)
        progressbar.setModal(True)
        progressbar.setCancelButtonText("Aguarde....")
        progressbar.setWindowTitle("Exportando para CSV")

        count = 0
        try:
            with open(ficheiro, 'w', newline='', encoding='utf8') as lista_produtos:
                csv_write = csv.writer(lista_produtos, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                csv_write.writerow([self.empresa])
                csv_write.writerow(['DATA: {}'.format(DATA_HORA_FORMATADA)])
                csv_write.writerow([])
                csv_write.writerow(csv_header)
                progressbar.show()
                progressbar.setValue(1)

                if len(data) > 0:
                    progressbar.setMaximum(len(data))
                    for x in data:
                        count += 1
                        progressbar.setValue(count)
                        lista = list(x)
                        csv_write.writerow(lista)

                        action_label.setText("Exportando: {}. {}".format(count, lista[1]))
                progressbar.close()
                lista_produtos.close()

                subprocess.Popen(caminho, shell=True)

                QMessageBox.information(self, "Successo!", "Processo terminado com Sucesso!!!")
        except Exception as e:
            QMessageBox.warning(self, "Erro", "Erro: {}.\nVeja se o Ficheiro em causa não está aberto.".format(e))

    def exportar_semsaida_csv(self):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(self, 'Guardar Ficheiro', '.', filter='Ficheiros CSV(*.csv)')

        if filename:
            ficheiro = filename
        else:
            QMessageBox.warning(self, 'Gravar Ficheiro', 'Ficheiro não foi gravado')
            return

        if ficheiro.endswith('.csv') is False:
            ficheiro += '.csv'

        caminho = os.path.realpath(ficheiro)

        self.cur.execute(self.stock_semsaida_sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        csv_header = [qApp.tr('Código'), qApp.tr('Descrição'), qApp.tr('Quantidade') ]

        action_label = QLabel("Exportando produtos. Aguarde.....")

        progressbar = QProgressDialog()
        progressbar.setLabel(action_label)
        progressbar.setMinimum(0)
        progressbar.setModal(True)
        progressbar.setCancelButtonText("Aguarde....")
        progressbar.setWindowTitle("Exportando para CSV")

        count = 0
        try:
            with open(ficheiro, 'w', newline='', encoding='utf8') as lista_produtos:
                csv_write = csv.writer(lista_produtos, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_write.writerow([self.empresa])
                csv_write.writerow(['DATA: {}'.format(DATA_HORA_FORMATADA)])
                csv_write.writerow([])
                csv_write.writerow(csv_header)
                progressbar.show()
                progressbar.setValue(1)

                if len(data) > 0:
                    progressbar.setMaximum(len(data))
                    for x in data:
                        count += 1
                        progressbar.setValue(count)
                        lista = list(x)
                        csv_write.writerow(lista)

                        action_label.setText("Exportando: {}. {}".format(count, lista[1]))
                progressbar.close()
                lista_produtos.close()

                subprocess.Popen(caminho, shell=True)

                QMessageBox.information(self, "Successo!", "Processo terminado com Sucesso!!!")
        except Exception as e:
            QMessageBox.warning(self, "Erro", "Erro: {}.\nVeja se o Ficheiro em causa não está aberto.".format(e))

    def exportar_maisvendido_csv(self):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(self, 'Guardar Ficheiro', '.', filter='Ficheiros CSV(*.csv)')

        if filename:
            ficheiro = filename
        else:
            QMessageBox.warning(self, 'Gravar Ficheiro', 'Ficheiro não foi gravado')
            return

        if ficheiro.endswith('.csv') is False:
            ficheiro += '.csv'

        caminho = os.path.realpath(ficheiro)

        self.cur.execute(self.mais_vendido_sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        csv_header = [qApp.tr('Código'), qApp.tr('Descrição'), qApp.tr('Quantidade') ]

        action_label = QLabel("Exportando produtos. Aguarde.....")

        progressbar = QProgressDialog()
        progressbar.setLabel(action_label)
        progressbar.setMinimum(0)
        progressbar.setModal(True)
        progressbar.setCancelButtonText("Aguarde....")
        progressbar.setWindowTitle("Exportando para CSV")

        count = 0
        try:
            with open(ficheiro, 'w', newline='', encoding='utf8') as lista_produtos:
                csv_write = csv.writer(lista_produtos, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_write.writerow([self.empresa])
                csv_write.writerow(['DATA: {}'.format(DATA_HORA_FORMATADA)])
                csv_write.writerow([])
                csv_write.writerow(csv_header)
                progressbar.show()
                progressbar.setValue(1)

                if len(data) > 0:
                    progressbar.setMaximum(len(data))
                    for x in data:
                        count += 1
                        progressbar.setValue(count)
                        lista = list(x)
                        csv_write.writerow(lista)

                        action_label.setText("Exportando: {}. {}".format(count, lista[1]))
                progressbar.close()
                lista_produtos.close()

                subprocess.Popen(caminho, shell=True)

                QMessageBox.information(self, "Successo!", "Processo terminado com Sucesso!!!")
        except Exception as e:
            QMessageBox.warning(self, "Erro", "Erro: {}.\nVeja se o Ficheiro em causa não está aberto.".format(e))

    def connect_db(self):
        pass

    def fill_produtos_table(self, familia=None, subfamilia=None):

        # data = self.data_inicial.date().toString('yyyy-MM-dd')

        if self.armazem_combo.currentText() == "Todos":
            print('Selecionando Todos...')
            self.produtos_sql = """SELECT
            p.cod, p.nome, p.cod_barras, p.custo, p.preco, p.preco1, p.preco2,
            p.preco3, p.preco4, pd.quantidade, p.quantidade_m, p.unidade, p.obs
            from produtos p
            INNER JOIN produtosdetalhe pd ON p.cod=pd.codproduto WHERE (p.nome
            like "%{nome}%" or p.cod_barras like "%{cod_barras}%" or p.cod like "%{preco}%") 
            """.format(nome=self.find_w.text(), cod_barras=self.find_w.text(),
                            preco=self.find_w.text())
        else:
            print('Usando o armazém: {}.'.format(self.armazem_combo.currentText()))

            self.produtos_sql = """SELECT
                        p.cod, p.nome, p.cod_barras, p.custo, p.preco, p.preco1, p.preco2,
                        p.preco3, p.preco4, pd.quantidade, p.quantidade_m, p.unidade, p.obs
                        from produtos p
                        INNER JOIN produtosdetalhe pd ON p.cod=pd.codproduto WHERE (p.nome
                        like "%{nome}%" or p.cod_barras like "%{cod_barras}%" or p.cod like "%{preco}%") 
                        """.format(nome=self.find_w.text(), cod_barras=self.find_w.text(),
                                   preco=self.find_w.text())

        # Header for the table
        self.produtos_header = [qApp.tr('Código'), qApp.tr('Descrição'), qApp.tr('Cód. de Barras'), qApp.tr('Custo'),
                  qApp.tr('Preço'), qApp.tr('Preço1'),qApp.tr('Preço2'),qApp.tr('Preço3'),qApp.tr('Preço4'),
                  qApp.tr('Quantidade'), "Q. Mínima", "Unidade", "Observações", ]

        if familia not in ("", None):
            self.produtos_sql += """ AND p.codfamilia="{}" """.format(familia)

        if subfamilia not in ("", None):
            self.produtos_sql += """ AND p.codsubfamilia="{}" """.format(subfamilia)

        print(self.produtos_sql)

        try:
            self.cur.execute(self.produtos_sql)
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]
        except Exception as e:
            return

        if len(data) == 0:
            tabledata = ["", "", "", "", "", "", "", "", ""]
        else:
            tabledata = data

        try:
            self.tm = MyTableModel(tabledata, self.produtos_header, self)
            # set the table model
            self.totalItems = self.tm.rowCount(self)
            self.tv.setModel(self.tm)

            self.tv.setColumnHidden(5, True)
            self.tv.setColumnHidden(6, True)
            self.tv.setColumnHidden(7, True)
            self.tv.setColumnHidden(8, True)

        except Exception as e:
            print(e)
            return False

        # # set row height
        nrows = len(tabledata)
        for row in range(nrows):
            self.tv.setRowHeight(row, 25)

        self.create_statusbar()

    def fill_maisvendido_table(self):

        self.mais_vendido_sql = """select produtos.cod, produtos.nome, sum(facturacaodetalhe.quantidade) as qt 
        from produtos INNER JOIN facturacaodetalhe ON produtos.cod=facturacaodetalhe.codproduto INNER JOIN
        facturacao ON facturacao.cod=facturacaodetalhe.codfacturacao INNER JOIN documentos 
        ON documentos.cod=facturacao.coddocumento WHERE produtos.nome like
        "%{nome}%" AND documentos.stock=1 AND (facturacao.modified BETWEEN "{inicial}" AND "{final}") group by produtos.cod order by qt desc  
        """.format(nome=self.find_w.text(),
                   inicial = QDate(self.data_inicial.date()).toString('yyyy-MM-dd'),
                   final = QDate(self.data_final.date()).toString('yyyy-MM-dd'))

        print(self.mais_vendido_sql)

        # Header for the table
        header = [qApp.tr('Código'), qApp.tr('Descrição'), qApp.tr('Quantidade')]

        try:
            self.cur.execute(self.mais_vendido_sql)
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]
        except Exception as e:
            return

        if len(data) == 0:
            tabledata = ["", "", "", ""]
        else:
            tabledata = data

        try:
            tm = MyTableModel(tabledata, header, self)
            # set the table model
            totalItems = tm.rowCount(self)
            self.mais_vendido_tv.setModel(tm)
        except Exception as e:
            return

        # # set row height
        nrows = len(tabledata)
        for row in range(nrows):
            self.mais_vendido_tv.setRowHeight(row, 25)

    def fill_zerostock_table(self):

        self.zero_stock_sql = """select DISTINCT p.cod, p.nome, pd.quantidade from produtos p 
        INNER JOIN produtosdetalhe pd ON p.cod=pd.codproduto
        WHERE p.nome like"%{nome}%" AND pd.quantidade=0 GROUP BY p.cod order by p.nome 
        """.format(nome=self.find_w.text())

        # Header for the table
        header = [qApp.tr('Código'), qApp.tr('Descrição'), qApp.tr('Quantidade')]
        try:
            self.cur.execute(self.zero_stock_sql)
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]
        except Exception as e:
            return

        if len(data) == 0:
            tabledata = ["", "", "", ""]
        else:
            tabledata = data

        try:
            tm = MyTableModel(tabledata, header, self)
            # set the table model
            totalItems = tm.rowCount(self)
            self.zero_stock_tv.setModel(tm)
        except Exception as e:
            return

        # # set row height
        nrows = len(tabledata)
        for row in range(nrows):
            self.zero_stock_tv.setRowHeight(row, 25)

    def fill_negativestock_table(self):

        self.stock_negativo_sql = """select DISTINCT p.cod, p.nome, pd.quantidade from produtos p 
        INNER JOIN produtosdetalhe pd ON p.cod=pd.codproduto
        WHERE p.nome like
        "%{nome}%" AND pd.quantidade<0 GROUP BY p.cod order by p.nome """.format(nome=self.find_w.text())

        # Header for the table
        header = [qApp.tr('Código'), qApp.tr('Descrição'), qApp.tr('Quantidade')]
        try:
            self.cur.execute(self.stock_negativo_sql)
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]
        except Exception as e:
            return

        if len(data) == 0:
            tabledata = ["", "", ""]
        else:
            tabledata = data

        try:
            tm = MyTableModel(tabledata, header, self)
            # set the table model
            totalItems = tm.rowCount(self)
            self.stock_negativo_tv.setModel(tm)
        except Exception as e:
            return

        # # set row height
        nrows = len(tabledata)
        for row in range(nrows):
            self.stock_negativo_tv.setRowHeight(row, 25)

    def fill_semsaida_table(self):

        data_inicial = self.data_inicial.date().toString("yyyy-MM-dd")
        data_final = self.data_final.date().toString("yyyy-MM-dd")

        self.stock_semsaida_sql = """SELECT DISTINCT p.cod, p.nome, f.modified, fd.quantidade
        FROM produtos p
        JOIN facturacaodetalhe fd ON p.cod=fd.codproduto
        JOIN facturacao f ON f.cod=fd.codfacturacao
        WHERE p.nome LIKE "%{nome}%" AND
        f.modified NOT BETWEEN "{inicial}" AND "{final}" GROUP BY p.cod order by p.nome  
        """.format(nome=self.find_w.text(), inicial=data_inicial, final=data_final)

        # Header for the table
        header = [qApp.tr('Código'), qApp.tr('Descrição'), "Ultima data de venda",qApp.tr('Quantidade')]

        try:
            self.cur.execute(self.stock_semsaida_sql)
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]
        except Exception as e:
            print("erro de sql no metodo fill_semsaida_table: ", e)
            return

        if len(data) == 0:
            tabledata = ["", "", ""]
        else:
            tabledata = data

        try:
            tm = MyTableModel(tabledata, header, self)
            # set the table model
            totalItems = tm.rowCount(self)
            self.stock_semsaida_tv.setModel(tm)
        except Exception as e:
            return

        # # set row height
        nrows = len(tabledata)
        for row in range(nrows):
            self.stock_semsaida_tv.setRowHeight(row, 25)

    def create_statusbar(self):

        estado = QStatusBar(self)
        items = QLabel("Total Items: %s" % self.totalItems)
        estado.addWidget(items)
        self.setStatusBar(estado)

    def clickedslot(self, index):

        row = int(index.row())
        indice= self.tm.index(row, 0)
        self.current_id = indice.data()
        self.create_statusbar()

    def new_data(self):

        cl = Produto(self)
        cl.limpar()
        cl.cod.setFocus()
        cl.cod.selectAll()
        cl.setModal(True)
        cl.show()

    def update_data(self):

        if self.current_id == "":
            QMessageBox.information(self, "Info", "Selecione o registo a actualizar na tabela")
            return

        cl = Produto(self)
        cl.cod.setText(self.current_id)
        cl.mostrar_registo()
        cl.setModal(True)
        cl.show()

    def removerow(self):
    
        if self.current_id == "":
            QMessageBox.information(self, "Info", "Selecione o registo a apagar na tabela")
            return
    
        if QMessageBox.question(self, "Pergunta", str("Deseja eliminar o registo %s?") % self.current_id,
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            stock_sql = """delete from stockdetalhe where codproduto="{}" """.format(str(self.current_id))
            facturacao_sql = """delete from facturacaodetalhe where codproduto="{}" """.format(str(self.current_id))
            produtos_sql = """delete from produtosdetalhe where codproduto="{}" """.format(str(self.current_id))
            sql = """delete from produtos WHERE cod = "{codigo}" """.format(codigo=str(self.current_id))

            try:
                self.cur.execute(stock_sql)
                self.cur.execute(facturacao_sql)
                self.cur.execute(produtos_sql)
                self.cur.execute(sql)
                self.conn.commit()
            except Exception as e:
                QMessageBox.warning(self, "Impossivel apagar dados", "Impossivel apagar dados."
                                                                     " Erro: {erro}".format(erro=e))
                return

            self.fill_produtos_table()
            QMessageBox.information(self, "Sucesso", "Item apagado com sucesso...")

    def imprime_lista_de_produtos(self):
        """Imprime no ecra a Lista geral de produtos baseado em um Critério"""
        if self.produtos_sql == "":
            return

        self.cur.execute(self.produtos_sql)
        dados = self.cur.fetchall()

        html = "<center> <h2> Lista de Produtos </h2> </center>"
        html += "<hr/>"

        html += "<br/>"

        html += "<table border=0 width = 80mm style='border: thin;'>"

        # print self.printer.width()

        html += "<tr style='background-color:#c0c0c0;'>"
        html += "<th width = 5%>Ref.</th>"
        html += "<th width = 30%>Descrição</th>"
        html += "<th width = 5%>Qt.</th>"
        html += "<th width = 10%>Custo</th>"
        html += "<th width = 10%>Preço</th>"
        html += "<th width = 15%>Custo Total</th>"
        html += "<th width = 15%>Venda Total</th>"
        html += "<th width = 10%>Lucro</th>"
        html += "</tr>"

        custo_total = Decimal(0)
        venda_total = Decimal(0)
        for cliente in dados:

            venda_total += cliente[9] * cliente[4]
            custo_total += cliente[9] * cliente[3]

            html += """<tr> <td>{}</td> <td>{}</td> <td>{}</td> 
            <td align="right">{:20,.2f}</td> <td align="right">{:20,.2f}</td> 
            <td align="right">{:20,.2f}</td> <td align="right">{:20,.2f}</td>
            <td align="right">{:20,.2f}</td> 
            </tr>""".format(cliente[0], cliente[1], cliente[9], cliente[3], cliente[4], Decimal(cliente[9]* cliente[3]),
                            Decimal(cliente[9]* cliente[4]), Decimal(cliente[9] * cliente[4] - cliente[9] * cliente[3]))

        lucro_total = venda_total - custo_total

        html += """<tr> <td></td> <td></td> <td></td> 
                    <td align="right"></td> <td align="right"></td> 
                    <td align="right">{:20,.2f}</td> <td align="right">{:20,.2f}</td>
                    <td align="right">{:20,.2f}</td> 
                    </tr>""".format(custo_total,venda_total, lucro_total)
        html += "</table>"

        html += "<hr/>"

        html += """<p style = "margin: 0 auto;
                   font-family: Arial, Helvetica, sans-serif;
                   position: absolute;
                   bottom: 10px;">processador por computador</p>"""

        document = QTextDocument()

        document.setHtml(html)

        dlg = QPrintPreviewDialog(self)
        dlg.paintRequested.connect(document.print_)
        dlg.showMaximized()
        dlg.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    helloPythonWidget = Produto()
    helloPythonWidget.show()

    sys.exit(app.exec_())