from decimal import Decimal
from PyQt5.QtWidgets import (QTabWidget, QLabel, QLineEdit, QFormLayout, QVBoxLayout, QToolBar, QMessageBox,
                             QPlainTextEdit, QAction, QApplication, QComboBox, QPushButton, QFileDialog, QHBoxLayout,
                             QGroupBox, QGridLayout, QSizePolicy, QWidget, QDialog)
from PyQt5.QtCore import Qt, QDate, QRegExp
from PyQt5.QtGui import QFont, QRegExpValidator
import sys

from teclado_numerico import Teclado
from teclado_alfanumerico import Teclado as TecladoNumerico
from utilities import codigo as cd


class NovoProduto(QDialog):
    def __init__(self, parent=None):
        super(NovoProduto, self).__init__(parent)

        if self.parent() is not None:
            self.cur = self.parent().cur
            self.conn = self.parent().conn
            self.user = self.parent().user

        self.cod_produto = ""
        self.codigogeral = ""

        boldFont = QFont('Consolas', 16)
        boldFont.setBold(True)

        regex = QRegExp("^(?:\d+\.?\d*|\d*\.?\d+)*$")
        validator = QRegExpValidator(regex)

        self.nome_produto = QLineEdit()
        self.nome_produto.setMaxLength(255)
        self.nome_produto.setFont(boldFont)
        self.nome_produto.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.quantidade_produto = QLineEdit()
        self.quantidade_produto.setValidator(validator)
        self.quantidade_produto.setText("0")
        self.quantidade_produto.setMaxLength(17)
        self.quantidade_produto.setAlignment(Qt.AlignRight)
        self.quantidade_produto.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        self.quantidade_produto.setFont(boldFont)
        self.preco_produto = QLineEdit()
        self.preco_produto.setMaxLength(17)
        self.preco_produto.setValidator(validator)
        self.preco_produto.setText(str(0))
        self.preco_produto.setAlignment(Qt.AlignRight)
        self.preco_produto.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.preco_produto.setFont(boldFont)

        butao_nome = QPushButton("...")
        butao_nome.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        butao_nome.clicked.connect(self.editar_nome)
        butao_quantidade = QPushButton("...")
        butao_quantidade.clicked.connect(self.editar_quantidade)
        butao_quantidade.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        butao_preco = QPushButton("...")
        butao_preco.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        butao_preco.clicked.connect(self.editar_preco)

        layout = QGridLayout()

        produto = QLabel("Descrição")
        produto.setFont(boldFont)
        quantidade = QLabel("Quantidade")
        quantidade.setFont(boldFont)
        preco = QLabel("Preço")
        preco.setFont(boldFont)

        layout.addWidget(produto, 0, 0)
        layout.addWidget(self.nome_produto, 1, 0)
        layout.addWidget(butao_nome, 1, 1)
        layout.addWidget(quantidade, 2, 0)
        layout.addWidget(self.quantidade_produto, 3, 0)
        layout.addWidget(butao_quantidade, 3, 1)
        layout.addWidget(preco, 4, 0)
        layout.addWidget(self.preco_produto, 5, 0)
        layout.addWidget(butao_preco, 5, 1)

        ok = QPushButton("OK")
        ok.clicked.connect(self.aceitar)
        ok.setFixedHeight(40)
        ok.setFont(boldFont)
        cancelar = QPushButton("Cancelar")
        cancelar.clicked.connect(self.close)
        cancelar.setFixedHeight(40)
        cancelar.setFont(boldFont)

        butao_layout = QHBoxLayout()
        butao_layout.addStretch()
        butao_layout.addWidget(ok)
        butao_layout.addWidget(cancelar)

        vlayout = QVBoxLayout()
        vlayout.addLayout(layout)
        vlayout.addLayout(butao_layout)

        self.setLayout(vlayout)

        self.setWindowTitle("Novo Produto")

    def editar_nome(self):
        tc = TecladoNumerico(self.nome_produto)
        tc.setModal(True)
        tc.show()

    def editar_quantidade(self):
        tc = Teclado(self.quantidade_produto)
        tc.setModal(True)
        tc.show()

    def editar_preco(self):
        tc = Teclado(self.preco_produto)
        tc.setModal(True)
        tc.show()

    def produto_existe(self):
        sql = """select nome from produtos where nome="{}" """.format(self.nome_produto.text())

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return True
        else:
            return False

    def aceitar(self):

        self.code = "PR" + cd("abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")
        quantidade = Decimal(self.quantidade_produto.text())
        created = QDate.currentDate().toString('yyyy-MM-dd')
        modified = QDate.currentDate().toString('yyyy-MM-dd')
        foto = ""
        nome = self.nome_produto.text()
        tipo = 0
        cod_barras = ""
        familia = "FM20181111111"
        subfamilia = "SF20181111111"
        custo = Decimal(0)
        preco = Decimal(self.preco_produto.text())
        preco1 =  Decimal(0)
        preco2 =  Decimal(0)
        preco3 =  Decimal(0)
        preco4 =  Decimal(0)
        unidade = "un"
        quantidade_m = Decimal(0)
        quantidade_max = Decimal(0)
        estado = 1
        obs = ""
        cod_taxa = "TX20182222222"

        if self.parent() is not None:
            codarmazem = self.parent().codarmazem
            modified_by = self.parent().user
            created_by = self.parent().user

            values = """ "{cod}", "{nome}", "{cod_barras}", {tipo},"{familia}", "{subfamilia}", {custo}, {preco}, 
                        preco1={preco1}, preco2={preco2}, preco3={preco3}, preco4={preco4},
                        {quantidade}, {quantidade_m}, "{unidade}", "{obs}", {estado}, "{created}", "{modified}", 
                        "{modified_by}", "{created_by}", "{foto}", "{taxa}", {quantidade_max}
                        """.format(cod=self.code, nome=nome, tipo=tipo, cod_barras=cod_barras, familia=familia,
                                   subfamilia=subfamilia,
                                   custo=custo, preco=preco, preco1=preco1, preco2=preco2, preco3=preco3, preco4=preco4,
                                   quantidade=quantidade, quantidade_m=quantidade_m, unidade=unidade, obs=obs,
                                   estado=estado, created=created, modified=modified, modified_by=modified_by,
                                   created_by=created_by, foto=foto, taxa=cod_taxa, quantidade_max=quantidade_max)

            sql_detalhes = """INSERT INTO produtosdetalhe (codproduto, codarmazem, quantidade, created, modified, 
                        modified_by, created_by) VALUES ("{codproduto}", "{codarmazem}", {quantidade}, "{created}", "{modified}", 
                        "{modified_by}", "{created_by}")""".format(codproduto=self.code, codarmazem=codarmazem,
                                                                   quantidade=quantidade, created=created,
                                                                   modified=modified,
                                                                   modified_by=modified_by, created_by=created_by)

            sql = """INSERT INTO produtos (cod, nome, cod_barras, tipo, codfamilia, codsubfamilia, custo, preco,  preco1, 
                        preco2,  preco3,  preco4, quantidade, quantidade_m, unidade, obs, estado, created, modified, 
                        modified_by, created_by, foto, codtaxa, quantidade_max) values({value})""".format(
                value=values)


        try:

            self.cur.execute(sql)
            self.cur.execute(sql_detalhes)
            self.gravar_stock()
            self.parent().codproduto = self.code
            self.parent().quantidade_unitario = quantidade
            self.parent().alterar_quantidade = True
            self.parent().add_record()
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Erro", "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
            return

        self.close()

    def existe_stock(self):
        sql = """SELECT cod FROM stock WHERE cod="{}" """.format('ST20001111111')

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return True
        else:
            return False

    def gravar_stock(self):

        cod_stock = 'ST20001111111'
        cod_fornecedor = "FR20181111111"
        numero_doc = "STOCK Padrão"
        data = QDate.currentDate().toString('yyyy-MM-dd')
        custo = Decimal(0)
        quantidade = Decimal(self.quantidade_produto.text())
        subtotal = custo * quantidade
        taxa = Decimal(17/100) * subtotal
        total = subtotal + taxa
        codproduto = self.code
        validade = "2019-01-01"

        if self.parent() is not None:
            modified_by = self.parent().user
            codarmazem = self.parent().codarmazem
            created_by = self.parent().user

        if self.existe_stock() is False:
            values = """ "{cod}", "{fornecedor}", "{numero}", "{data}", {total}, {iva}, {subtotal}, {saldo}, 
                        "{created}", "{modified}", "{modified_by}", "{created_by}" 
                        """.format(cod=cod_stock, fornecedor=cod_fornecedor, numero=numero_doc, data=data, total=total,
                                   iva=taxa, subtotal=subtotal, created=data, modified=data,
                                   modified_by=modified_by, created_by=created_by, saldo=total)

            sql_stock = """INSERT INTO stock (cod, fornecedor, numero, data, total, taxa, subtotal, saldo, created,
                        modified, modified_by, created_by) values({value})""".format(value=values)


        else:
            sql_stock = """UPDATE stock set numero="{numero}", total=total+{total}, taxa=taxa+{iva}, 
            subtotal=subtotal+{subtotal}, saldo=saldo+{saldo}, modified="{modified}", 
            modified_by="{modified_by}" WHERE cod="{cod}" """.format(cod=cod_stock, fornecedor=cod_fornecedor,
                                                                     numero=numero_doc, data=data,
                       total=total, iva=taxa, subtotal=subtotal, modified=data, modified_by=modified_by, saldo=total)

        stock_detalhe_values = """ "{codstock}", "{codproduto}", "{codarmazem}", {quantidade}, "{validade}",{valor}, 
        {taxa}, {subtotal}, {total} """.format(codstock=cod_stock, codproduto=codproduto, codarmazem=codarmazem,
                                               quantidade=quantidade, validade=validade, valor=custo, taxa=taxa,
                                               subtotal=subtotal, total=total)

        sql_stockdetalhe = """INSERT INTO stockdetalhe (codstock, codproduto, codarmazem, quantidade, validade, 
        valor, taxa, subtotal, total) values({value})""".format(value=stock_detalhe_values)

        self.cur.execute(sql_stock)
        self.cur.execute(sql_stockdetalhe)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    helloPythonWidget = NovoProduto()
    helloPythonWidget.show()

    sys.exit(app.exec_())
