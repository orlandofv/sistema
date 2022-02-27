from decimal import Decimal
from PyQt5.QtWidgets import (QRadioButton, QLabel, QLineEdit, QFormLayout, QVBoxLayout, QToolBar, QMessageBox,
                             QPlainTextEdit, QAction, QApplication, QComboBox, QPushButton, QFileDialog, QHBoxLayout,
                             QGroupBox, QGridLayout, QSizePolicy, QWidget, QDialog, QStackedWidget)
from PyQt5.QtCore import Qt, QDate, QRegExp
from PyQt5.QtGui import QFont, QRegExpValidator
import sys

from teclado_numerico import Teclado
from pricespinbox import price


class Desconto(QDialog):
    def __init__(self, parent=None):
        super(Desconto, self).__init__(parent)

        self.setWindowTitle("Desconto")

        self.total_geral = Decimal(0)

        self.cod_produto = ""
        self.codigogeral = ""

        self.ui()

        self.limitar_desconto()

        if self.parent() is not None:
            self.conn = self.parent().conn
            self.cur = self.conn.cursor()

    def ui(self):
        boldFont = QFont('Consolas', 16)
        boldFont.setBold(True)

        # regex = QRegExp("^(?:\d+\.?\d*|\d*\.?\d+)*$")
        # validator = QRegExpValidator(regex)

        self.total_label = QLabel("0.00")
        self.desconto_label = QLabel("0.00")
        self.valor_label = QLabel("0.00")
        self.taxa_label = QLabel("0.00")
        self.total_geral_label = QLabel("0.00")
        self.total_label.setAlignment(Qt.AlignRight)
        self.desconto_label.setAlignment(Qt.AlignRight)
        self.valor_label.setAlignment(Qt.AlignRight)
        self.taxa_label.setAlignment(Qt.AlignRight)
        self.total_geral_label.setAlignment(Qt.AlignRight)
        self.total_label.setFont(boldFont)
        self.desconto_label.setFont(boldFont)
        self.valor_label.setFont(boldFont)
        self.taxa_label.setFont(boldFont)
        self.total_geral_label.setFont(boldFont)

        self.nome_produto = QPlainTextEdit()
        self.nome_produto.setEnabled(False)
        self.quantidade_produto = price()
        self.desconto_produto = price()
        self.lista_de_precos = QComboBox()
        self.preco_produto = price()
        self.taxa_produto = QComboBox()

        descontogrupo = QGroupBox("Desconto")

        self.desconto_percentual = QRadioButton("Por Percentagem")
        self.desconto_percentual.clicked.connect(self.limitar_desconto)
        self.desconto_percentual.setChecked(True)
        self.desconto_por_valor = QRadioButton("Por valor")
        self.desconto_por_valor.clicked.connect(self.limitar_desconto)

        self.desconto_label.setFont(boldFont)
        self.desconto_percentual.setFont(boldFont)
        self.desconto_produto.setFont(boldFont)
        self.desconto_por_valor.setFont(boldFont)

        hbox = QHBoxLayout()
        hbox.addWidget(self.desconto_percentual)
        hbox.addWidget(self.desconto_por_valor)

        vbox = QVBoxLayout()
        vbox.addWidget(self.total_label)
        vbox.addLayout(hbox)
        vbox.addWidget(self.desconto_produto)
        descontogrupo.setLayout(vbox)

        totahbox = QFormLayout()
        total = QLabel("Total Bruto : ")
        desconto = QLabel("Desconto: ")
        taxa = QLabel("Taxa: ")
        valoractual = QLabel("Subtotal: ")
        total_geral = QLabel("Total Geral: ")
        total.setFont(boldFont)
        desconto.setFont(boldFont)
        taxa.setFont(boldFont)
        valoractual.setFont(boldFont)
        total_geral.setFont(boldFont)

        #totahbox.addRow(total, self.total_label)
        totahbox.addRow(desconto, self.desconto_label)
        totahbox.addRow(taxa, self.taxa_label)
        totahbox.addRow(valoractual, self.valor_label)
        totahbox.addRow(total_geral, self.total_geral_label)

        totalgrupo = QGroupBox()
        totalgrupo.setLayout(totahbox)

        layout = QGridLayout()

        layout.addWidget(descontogrupo, 10, 0)

        detalhe = QWidget()
        detalhe.setLayout(layout)

        spacer1 = QWidget()
        spacer1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.stackedwidget = QStackedWidget(self)

        self.stackedwidget.addWidget(detalhe)
        self.stackedwidget.addWidget(totalgrupo)

        ok = QPushButton("OK")
        ok.setDefault(True)
        ok.clicked.connect(self.aceitar)
        cancelar = QPushButton("C&ancelar")
        cancelar.clicked.connect(self.close)

        butao_layout = QHBoxLayout()
        butao_layout.addStretch()
        butao_layout.addWidget(ok)
        butao_layout.addWidget(cancelar)

        vlayout = QVBoxLayout()

        vlayout.addWidget(self.stackedwidget)
        vlayout.addLayout(butao_layout)

        self.setLayout(vlayout)

    def adicionar_preco(self):
        if self.lista_de_precos.currentText() == "": return

        self.preco_produto.setValue(Decimal(self.lista_de_precos.currentText()))

    def limita_descontos(self):

        self.total_bruto = Decimal(self.preco_produto.value()) * Decimal(self.quantidade_produto.value())

        if self.total_bruto == 0:
            self.desconto_produto.setRange(0, 0)

        if self.desconto_percentual.isChecked():
            self.desconto_produto.setRange(0, 100)
        else:
            self.desconto_produto.setRange(0, self.total_bruto)

        subtotal, desconto, taxa, total = self.calcula_valores()

        self.total_geral_label.setText(str(total))
        self.taxa_label.setText(str(taxa))
        self.desconto_label.setText(str(desconto))
        self.valor_label.setText(str(self.total_bruto))
        self.total_label.setText(str(subtotal))

    def calcula_valores(self):

        if self.desconto_percentual.isChecked():
            desconto = Decimal(self.total_bruto) * Decimal(self.desconto_produto.value()) / 100
        else:
            desconto = Decimal(self.desconto_produto.value())

        # Fiz append de '0' para casos em que a combobox taxa for vazia
        valor_taxa = str(self.taxa_produto.currentText()) + '0'

        if int(valor_taxa) > 0:
            taxa = self.total_bruto * Decimal(str(self.taxa_produto.currentText())) / 100
        else:
            taxa = Decimal(0)

        subtotal = Decimal(self.total_bruto) - desconto
        desconto = desconto
        taxa = taxa
        total = subtotal + taxa

        return subtotal, desconto, taxa, total

    def validar_dados(self):

        # Gets the cod, preco, custo, foto, nome, quantidade e codtaxa of the product
        if self.parent() is None: return

        # produtos.cod, produtos.preco, produtos.custo, produtos.foto, produtos.nome,
        #         produtosdetalhe.quantidade, produtos.codtaxa
        detalhes = self.parent().facturacao_modulo.get_produto_detalhe(self.cod_produto, self.parent().codarmazem)

        if len(detalhes) == 0: return False

        subtotal, desconto, taxa_, total = self.calcula_valores()

        self.preco_unitario = Decimal(self.preco_produto.value())
        self.quantidade_unitario = Decimal(self.quantidade_produto.value())
        self.custoproduto = detalhes[2]
        self.custo = self.quantidade_unitario * self.custoproduto

        # Para ver se a quantidade existe na base de dados ou nao
        self.quantidade_existente = detalhes[5]

        self.desconto = desconto
        self.subtotal = subtotal

        self.custo_do_produto = Decimal(self.custoproduto)
        self.lucro = self.subtotal - self.custo_do_produto

        # Porcausa das Financas locais de Moz a taxa nao pode ser retirada do desconto
        self.taxa = taxa_

        self.custo_do_produto = str(self.custo_do_produto)
        self.preco_unitario = str(self.preco_unitario)
        self.quantidade_unitario = str(self.quantidade_unitario)
        self.custo = str(self.custo)
        self.subtotal = str(self.subtotal)
        self.desconto = str(self.desconto)
        self.taxa = str(self.taxa)
        self.lucro = str(self.lucro)
        self.total = str(total)

        return True

    def limitar_desconto(self):
        self.desconto_produto.setValue(0)
        self.desconto_produto.setFocus()

        if self.desconto_percentual.isChecked():
            self.desconto_produto.setRange(0, 100)
        else:
            self.desconto_produto.setRange(0, self.total_geral)

    def get_lines(self, codfacturacao):
        sql = """SELECT codproduto from facturacaodetalhe WHERE codfacturacao = "{}" """.format(codfacturacao)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        return data

    def aceitar(self):
        total = self.total_geral

        if self.desconto_percentual.isChecked():
            valor_desconto = total * Decimal(self.desconto_produto.value()) / 100
            valor_desconto_p = self.desconto_produto.value()/100
        else:
            valor_desconto = Decimal(self.desconto_produto.value())
            valor_desconto_p = Decimal(self.desconto_produto.value()) / total

        if self.parent() is not None:
            try:
                sql = """UPDATE facturacao set total={total}-{desconto}, subtotal=subtotal-{desconto},
                lucro=custo-{total},  
                desconto={desconto} WHERE cod="{cod}" """.format(desconto=valor_desconto, total=total,
                                                                 cod=self.codigogeral)
                print(sql)
                self.cur.execute(sql)

                if len(self.get_lines(self.codigogeral)) > 0:
                    for x in self.get_lines(self.codigogeral):
                        sql_d = """UPDATE facturacaodetalhe set total=total-(total*{desconto}), 
                        desconto={total}*{desconto}, 
                        subtotal=subtotal-subtotal*{desconto}, preco=preco-preco*{desconto}, lucro=custo-{total}
                        WHERE codfacturacao="{codf}" AND codproduto="{codp}" """.format(desconto=valor_desconto_p, total=total,
                                                                codf=self.codigogeral, codp=x[0])
                        print(sql_d)
                        self.cur.execute(sql_d)

                self.conn.commit()
                QMessageBox.information(self, "Sucesso", "Desconto efectuado com sucesso!")
                self.parent().fill_table()
                self.parent().cod_line.setFocus()
                self.parent().calcula_total_geral()
                self.close()

            except Exception as e:
                QMessageBox.warning(self, "Erro", "Houve um erro na operação:\n{}.".format(e))
                self.close()


