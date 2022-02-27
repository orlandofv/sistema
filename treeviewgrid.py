import sys
import decimal

from PyQt5.QtWidgets import  QLabel, QLineEdit, QMainWindow, QVBoxLayout, QToolBar, QMessageBox,\
    QAction, QApplication, QGroupBox, QPushButton, QComboBox, QDateEdit, QCalendarWidget,\
    QHBoxLayout, QWidget, QTableView, QAbstractItemView, QSplitter, QTreeView, qApp

from sortmodel import MyTableModel
from treeview_test import CustomNode, CustomModel


class TreeViewGrid(QMainWindow):

    def __init__(self, parent=None):
        super(TreeViewGrid, self).__init__(parent)
        self.setWindowTitle("My Grid TreeView")

        self.ui()
        self.connect_db()
        self.fill_grid()

    def ui(self):
        self.table = QTableView(self)

        self.treeview = QTreeView(self)
        self.treeview.clicked.connect(self.clicked_slot)
        self.treeview.resize(self.treeview.width() + self.table.width()/2, self.width())

        spliter = QSplitter()

        spliter.addWidget(self.treeview)
        spliter.addWidget(self.table)

        self.setCentralWidget(spliter)

        search_toolbar = QToolBar()

    def fill_grid(self):

        items = []
        items.append(CustomNode("Todos"))

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

    def clicked_slot(self, val):
        print(val.data())
        print(val.row())
        print(val.column())

        model = self.treeview.model()
        # Tentamos ver ser a contagem dos subitems, se for zero asuminos que
        # seja root ou o nivel mais alto de items

        data = model.rowCount(val)

        if data == 0:
            print("Pai ou filho sem nada")

    def fill_produtos_table(self):

        if self.armazem_combo.currentText() == "Todos":

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
        produtos_header = [qApp.tr('Código'), qApp.tr('Descrição'), qApp.tr('Cód. de Barras'), qApp.tr('Custo'),
                                qApp.tr('Preço'), qApp.tr('Preço1'), qApp.tr('Preço2'), qApp.tr('Preço3'),
                                qApp.tr('Preço4'),
                                qApp.tr('Quantidade'), "Q. Mínima", "Unidade", "Observações", ]

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
            self.tm = MyTableModel(tabledata, produtos_header, self)
            # set the table model
            self.totalItems = self.tm.rowCount(self)
            self.table.setModel(self.tm)

        except Exception as e:
            return

        # # set row height
        nrows = len(tabledata)
        for row in range(nrows):
            self.table.setRowHeight(row, 25)

    def connect_db(self):
        import mysql.connector as mc

        self.conn = mc.connect(host='127.0.0.1',
                               user='root',
                               passwd='abc123@123',
                               db='agencia_boa',
                               port=3306)

        self.cur = self.conn.cursor()

        print('warnings: ', self.conn.get_warnings, 'Server Version: ', self.conn.get_server_version(),
              'Server Info: ', self.conn.get_server_info())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    t = TreeViewGrid()
    t.show()
    sys.exit(app.exec_())