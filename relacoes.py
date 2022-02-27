import sys, os
from decimal import  Decimal
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QDialog, QComboBox, QVBoxLayout, QFormLayout, QLabel, QMessageBox, QAbstractItemView,
                             QApplication, QTableView, QPushButton, QHBoxLayout, QWidget, QSizePolicy,
                             QCheckBox)

from pricespinbox import price
from sortmodel import MyTableModel


class Relacoes(QDialog):
    cod = None
    cod_produto1 = ""
    cod_produto2 = ""
    quantidade_1 = Decimal(1)
    quantidade_2 = Decimal(0)
    user = ""
    armazem = ""

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        if self.parent() is not None:
            self.conn = self.parent().conn
            self.cur = self.parent().cur
            self.user = self.parent().user

        self.ui()
        self.fill_armzem()

    def ui(self):
        self.armazem_combo = QComboBox()
        self.armazem_combo.currentIndexChanged.connect(lambda: self.get_cod_armazem(self.armazem_combo.currentText()))

        self.codproduto1_combo = QComboBox()
        self.codproduto1_combo.currentIndexChanged.connect(
            lambda: self.get_produto1_cod(self.codproduto1_combo.currentText()))

        self.codproduto1_combo.currentIndexChanged.connect(self.fill_table)

        self.codproduto2_combo = QComboBox()
        self.codproduto2_combo.currentIndexChanged.connect(
            lambda: self.get_produto2_cod(self.codproduto2_combo.currentText()))

        self.codproduto2_combo.currentIndexChanged.connect(self.fill_table)

        self.quantidade1_spin = price()
        self.quantidade1_spin.setValue(1)
        self.quantidade1_spin.setEnabled(False)

        self.quantidade2_spin = price()
        self.diminui_check = QCheckBox("Diminuir stock do produto principal")

        self.tabela = QTableView()
        self.tabela.clicked.connect(self.clicked_slot)
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

        adicionar_item = QPushButton(QIcon("./icons/add.ico"), "Add. Items")
        adicionar_item.clicked.connect(self.add_record)
        remover_item = QPushButton("Remover")
        remover_item.clicked.connect(self.remove_row)
        fechar = QPushButton("Fechar")
        fechar.clicked.connect(self.close)
        spacer =  QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        form_lay = QFormLayout()
        form_lay.addRow(QLabel("Escolha o Armazém"), self.armazem_combo)
        form_lay.addRow(QLabel("Escolha o primeiro Produto"), self.codproduto1_combo)
        form_lay.addWidget(self.diminui_check)
        form_lay.addRow(QLabel("Quantidade do primeito produto"), self.quantidade1_spin)
        form_lay.addRow(QLabel("Escolha o segundo Produto"), self.codproduto2_combo)
        form_lay.addRow(QLabel("Quantidade do segundo produto"), self.quantidade2_spin)

        h_lay = QHBoxLayout()
        h_lay.setSpacing(0)
        h_lay.addWidget(adicionar_item)
        h_lay.addWidget(remover_item)
        h_lay.addWidget(spacer)
        h_lay.addWidget(fechar)

        main_lay = QVBoxLayout()
        main_lay.addLayout(form_lay)
        main_lay.addWidget(QLabel("Relaçoes"))
        main_lay.addWidget(self.tabela)
        main_lay.addLayout(h_lay)

        self.setLayout(main_lay)

        self.setWindowTitle("Relações")

    def validacao(self):
        if self.codproduto2_combo.currentText() == "":
            QMessageBox.warning(self, "Produto Inválido", "Escolha o primeiro produto.")
            return False

        if self.codproduto1_combo.currentText() == "":
            QMessageBox.warning(self, "Produto Inválido", "Escolha o segundo produto.")
            return False

        if self.quantidade1_spin.value() == 0:
            QMessageBox.warning(self, "Quantidade Inválida", "A quantodade do primeiro produto é inválida.")
            return False

        if self.quantidade2_spin.value() == 0:
            QMessageBox.warning(self, "Quantidade Inválida", "A quantodade do segundo produto é inválida.")
            return False

        if self.codproduto1_combo.currentText() == self.codproduto2_combo.currentText():
            QMessageBox.warning(self, "Produtos Iguais", "Os Produtos devem ser direrentes.")
            return False

        if self.armazem == "":
            QMessageBox.warning(self,  "Armazém inválido", "Escolha o Armazém na Base de dados")
            return False

        if self.quantidade2_spin.value() == 0:
            QMessageBox.warning(self, "Quantidade Inválida", "A quantidade do Produto deve ser maior que 0")
            return False

        return True

    def clicked_slot(self, index):

        row = int(index.row())

        # obtemos a chave primaria
        cod = self.tm.index(row, 0)
        self.cod = cod.data()

        quantidade1 = self.tm.index(row, 2)
        self.quantidade_1 = Decimal(quantidade1.data())

    def fill_produtos(self):
        sql = "SELECT nome FROM produtos WHERE tipo=0 AND estado=1 order by nome"
        self.cur.execute(sql)
        data = self.cur.fetchall()

        self.codproduto1_combo.clear()
        self.codproduto2_combo.clear()

        if len(data) > 0:
            for item in data:
                self.codproduto1_combo.addItems(item)
                self.codproduto2_combo.addItems(item)

    def fill_armzem(self):
        """Fills the Armazem Combobox"""
        sql = """select nome from armazem where estado=1 order by nome"""
        self.cur.execute(sql)
        data = self.cur.fetchall()

        self.armazem_combo.clear()

        if len(data) > 0:

            for item in data:
                self.armazem_combo.addItem(item[0])

            # self.armazem_combo.addItem('Todos')
            return True
        else:
            return False

    def get_cod_armazem(self, nome_armazem):
        """Gets Armazem cod based on nome"""

        sql = """SELECT cod from armazem WHERE nome="{}" """.format(nome_armazem)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            self.armazem = data[0][0]
            return self.armazem
        else:

            return ""

    def fill_table(self):

        header = ["cod", "Produto relacionado", "Quantidade", ""]

        sql = """ SELECT r.cod, p.nome, r.quantidade2 FROM relacoes r 
        INNER JOIN produtos p ON p.cod=r.codproduto2 WHERE r.codproduto1="{cod1}" 
        AND codarmazem="{armazem}" """.format(cod1=self.cod_produto1,
                                       armazem=self.get_cod_armazem(self.armazem_combo.currentText()))

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        if len(data) > 0:
            table_data = data
        else:
            table_data = [("", "", "", "")]

        try:
            # set the table model
            self.tm = MyTableModel(table_data, header, self)
            self.totalItems = self.tm.rowCount(self)
            self.tabela.setModel(self.tm)

            self.tabela.setColumnHidden(0, True)
            self.tabela.setColumnWidth(1, .8 * self.tabela.width())
            self.tabela.setColumnWidth(2, .2 * self.tabela.width())

        except Exception as e:
            print(e)

    def remove_row(self):

        if self.cod is None:
            QMessageBox.warning(self, "Info", "Selecione o registo a apagar na tabela")
            return

        sql = """delete from relacoes WHERE cod = "{codigo}" """.format(codigo=str(self.cod))

        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            QMessageBox.warning(self, "Impossivel apagar dados", "Impossivel apagar dados."
                                                                 " Erro: {erro}".format(erro=e))
            return

        self.fill_table()

    def get_user_cod(self, nome):
        sql = """SELECT cod from users WHERE cod="{}" """.format(nome)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return data[0][0]
        else:
            return ""

    def get_produto1_cod(self, nome):
        sql = """SELECT cod from produtos WHERE nome="{}" """.format(nome)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            self.cod_produto1 = data[0][0]
        else:
            self.cod_produto1 = ""

    def get_produto2_cod(self, nome):
        sql = """SELECT cod from produtos WHERE nome="{}" """.format(nome)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            self.cod_produto2 = data[0][0]
        else:
            self.cod_produto2 = ""

    def add_record(self):

        if self.validacao() is False:
            return

        self.user = self.get_user_cod(self.parent().user)

        created = QDate.currentDate().toString('yyyy-MM-dd')
        modified = QDate.currentDate().toString('yyyy-MM-dd')
        self.quantidade_1 = 1
        self.quantidade_2 = Decimal(self.quantidade2_spin.value())

        self.cod = self.produto_existe(self.cod_produto1,
                                       self.cod_produto2)

        if self.cod is None:
            sql = """INSERT INTO relacoes (codproduto1, quantidade1, codproduto2, quantidade2, codarmazem,created, modified,
            created_by, modified_by, obs) 
            VALUES ("{}", {}, "{}", {}, "{}","{}", "{}", "{}", "{}", "{}") """.format(self.cod_produto1, self.quantidade_1, self.cod_produto2,
                                                   self.quantidade_2, self.armazem, created, modified, self.user, self.user, "")
        else:
            sql = """UPDATE relacoes set quantidade1={}, quantidade2={}, codarmazem="{}",modified="{}", modified_by="{}" WHERE cod="{}" 
            """.format(self.quantidade_1, self.quantidade_2, self.armazem, modified, self.user, self.cod)

        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(e)
            self.conn.rollback()
            QMessageBox.warning(self, "Erro na inserçãao", "Relação não foi gravada.\n{}".format(e))

        self.cod = None
        self.fill_table()

    def produto_existe(self, prod1, prod2):
        sql = """SELECT cod FROM relacoes WHERE codproduto1="{}" AND codproduto2="{}" """.format(prod1, prod2)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return data[0][0]

        return None


if __name__ == '__main__':
    app = QApplication(sys.argv)

    helloPythonWidget = Relacoes()
    helloPythonWidget.show()

    sys.exit(app.exec_())

