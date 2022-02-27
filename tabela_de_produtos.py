from PyQt5.QtWidgets import (QMainWindow, qApp, QLabel, QMessageBox, QTableView, QAbstractItemView, QCompleter,
                             QLineEdit, QAction, QToolBar, QStatusBar)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from sortmodel import MyTableModel
from striped_table import StripedTable

# Classe que representa a Lista de Produtos
class ListaDeProdutos(QMainWindow):

    def __init__(self, parent=None):
        super(ListaDeProdutos, self).__init__(parent)

        # controla o codigo
        self.current_id = ""

        # Connect the Database
        self.connect_db()

        # Create the main user interface
        self.ui()

        # Header for the table
        self.header = [qApp.tr('Código'), qApp.tr('Nome'), qApp.tr('Preço'), qApp.tr('Qty')]

        # Search the data
        self.fill_table()
        self.find_w.textEdited.connect(self.fill_table)

    def ui(self):

        # create the view
        self.tv = StripedTable(self)
        self.tv.clicked.connect(self.clicked_slot)
        self.setCentralWidget(self.tv)
        self.create_toolbar()

    def enterEvent(self, *args, **kwargs):
        if self.find_w.hasFocus():
            self.find_w.selectAll()

    def focusInEvent(self, evt):
        self.find_w.selectAll()
        self.fill_table()

    def connect_db(self):
        if self.parent() is None:
            self.db = self.connect_db()
            self.user = ""
        else:
            self.conn = self.parent().conn
            self.cur = self.parent().cur
            self.user = self.parent().user

    def fill_table(self):

        try:
            parente = self.parent()
            codarmazem = parente.codarmazem
        except Exception:

            parente = self.parent().parent().parent().parent().parent().parent()
            codarmazem = parente.codarmazem

        sql = """SELECT produtos.cod, produtos.nome, produtos.preco, produtosdetalhe.quantidade from produtos
                 INNER JOIN produtosdetalhe ON produtos.cod=produtosdetalhe.codproduto WHERE (produtos.nome
                 like "%{nome}%" or produtos.cod_barras like "%{cod_barras}%" or produtos.cod like "%{preco}%") 
                 and produtosdetalhe.codarmazem="{codarmazem}" and produtos.estado=1 
                 """.format(nome=self.find_w.text(), cod_barras=self.find_w.text(),
                            preco=self.find_w.text(), codarmazem=codarmazem)

        print(sql)

        try:
            # self.conn.cmd_refresh(1)
            self.cur.execute(sql)
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]
        except Exception as e:
            print(e)
            return

        if len(data) == 0:
            self.tabledata = [""]
        else:
            self.tabledata = data

        try:
            self.tm = MyTableModel(self.tabledata, self.header, self)
            # set the table model
            self.totalItems = self.tm.rowCount(self)
            self.tv.setModel(self.tm)
            completer = QCompleter()
            completer.setModel(self.tm)
            completer.setCompletionColumn(1)
            self.find_w.setCompleter(completer)

            self.tv.setColumnWidth(0, self.tv.width() * .15)
            self.tv.setColumnWidth(1, self.tv.width() * .6)
            self.tv.setColumnWidth(2, self.tv.width() * .15)
            self.tv.setColumnWidth(3, self.tv.width() * .1)
        except Exception as e:
            return
        # # set row height
        nrows = len(self.tabledata)
        for row in range(nrows):
            self.tv.setRowHeight(row, 25)
        self.create_statusbar()

    def resizeEvent(self, *args, **kwargs):
        try:
            self.tv.setColumnWidth(0, self.tv.width() * .15)
            self.tv.setColumnWidth(1, self.tv.width() * .6)
            self.tv.setColumnWidth(2, self.tv.width() * .15)
            self.tv.setColumnWidth(3, self.tv.width() * .1)
        except Exception as e:
            print(e)

    def create_toolbar(self):
        find = QLabel(qApp.tr("Procurar") + "  ")
        self.find_w = QLineEdit(self)
        self.find_w.setPlaceholderText("Procurar")
        self.find_w.setMaximumWidth(200)

        self.new = QAction(QIcon('./icons/add_2.ico'), qApp.tr("Novo"), self)
        self.delete = QAction(QIcon('./images/editdelete.png'), qApp.tr("Eliminar"), self)
        self.print = QAction(QIcon('./images/fileprint.png'), qApp.tr("Imprimir"), self)
        self.update = QAction(QIcon('./images/pencil.png'), qApp.tr("Editar"), self)
        self.delete.setVisible(False)

        tool = QToolBar()
        tool.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        tool.setContextMenuPolicy(Qt.PreventContextMenu)

        tool.addWidget(find)
        tool.addWidget(self.find_w)
        tool.addAction(self.delete)

        tool.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        self.addToolBarBreak(Qt.BottomToolBarArea)
        self.addToolBar(tool)

    def create_statusbar(self):
        estado = QStatusBar(self)

        self.items = QLabel("Total Items: %s" % self.totalItems)
        estado.addWidget(self.items)
        self.setStatusBar(estado)

    def clicked_slot(self, index):

        self.row = int(index.row())

        indice = self.tm.index(self.row, 0)
        self.current_id = indice.data()
        self.set_code()

    # This Function gets the cod field
    def set_code(self):

        # Yes very bad code, I need to figure out how to reach Clientes
        parente = self.parent().parent().parent().parent().parent().parent()

        print("Parente: ", parente)

        if parente is None:
            return

        if self.current_id == "":
            return

        if parente is not None:
            for child in parente.findChildren(QLineEdit):
                if child.objectName() == "codigo":
                    child.setText(self.current_id)
                    child.setFocus()
                    child.selectAll()

                    parente.cod_produto = self.current_id
                    print("Chamando o parente: ", self.current_id)
                    parente.validar_dados()

