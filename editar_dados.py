from decimal import Decimal
from PyQt5.QtWidgets import (QRadioButton, QLabel, QLineEdit, QFormLayout, QVBoxLayout, QToolBar, QMessageBox,
                             QPlainTextEdit, QAction, QApplication, QComboBox, QPushButton, QFileDialog, QHBoxLayout,
                             QGroupBox, QGridLayout, QSizePolicy, QWidget, QDialog, QStackedWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sys

from pricespinbox import price


class EditarValores(QDialog):
    def __init__(self, parent=None):
        super(EditarValores, self).__init__(parent)

        self.cod_produto = ""
        self.codigogeral = ""

        self.preco = 0
        self.quantidade = 0
        self.subtotal = 0
        self.desconto = 0
        self.taxa = 0
        self.total = 0
        self.lucro = 0
        self.custo = 0

        self.total_bruto = 0

        self.ui()

        self.limita_descontos()

    def ui(self):
        boldFont = QFont('Consolas', 12)
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
        self.quantidade_produto.valueChanged.connect(self.limita_descontos)
        self.desconto_produto = price()
        self.desconto_produto.valueChanged.connect(self.limita_descontos)
        self.lista_de_precos = QComboBox()
        self.lista_de_precos.currentIndexChanged.connect(self.adicionar_preco)
        self.preco_produto = price()
        self.preco_produto.valueChanged.connect(self.limita_descontos)
        self.taxa_produto = QComboBox()
        self.taxa_produto.currentIndexChanged.connect(self.limita_descontos)

        descontogrupo = QGroupBox("Desconto")

        self.desconto_percentual = QRadioButton("Por Percentagem")
        self.desconto_percentual.setChecked(True)
        self.desconto_percentual.clicked.connect(self.limita_descontos)
        self.desconto_por_valor = QRadioButton("Por valor")
        self.desconto_por_valor.clicked.connect(self.limita_descontos)

        hbox = QHBoxLayout()
        hbox.addWidget(self.desconto_percentual)
        hbox.addWidget(self.desconto_por_valor)

        vbox = QVBoxLayout()
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

        totahbox.addRow(total, self.total_label)
        totahbox.addRow(desconto, self.desconto_label)
        totahbox.addRow(taxa, self.taxa_label)
        totahbox.addRow(valoractual, self.valor_label)
        totahbox.addRow(total_geral, self.total_geral_label)

        totalgrupo = QGroupBox()
        totalgrupo.setLayout(totahbox)

        layout = QGridLayout()

        layout.addWidget(self.nome_produto, 1, 0, )
        layout.addWidget(QLabel("Lista de Preços"), 2, 0)
        layout.addWidget(self.lista_de_precos, 3, 0)
        layout.addWidget(QLabel("Preço"), 4, 0)
        layout.addWidget(self.preco_produto, 5, 0)
        layout.addWidget(QLabel("Quantidade"), 6, 0)
        layout.addWidget(self.quantidade_produto, 7, 0)
        layout.addWidget(QLabel("Lista de Taxas"), 8, 0)
        layout.addWidget(self.taxa_produto, 9, 0)
        layout.addWidget(descontogrupo, 10, 0)

        detalhe = QWidget()
        detalhe.setLayout(layout)

        self.expand_button = QPushButton("+")
        self.expand_button.clicked.connect(self.expandir_diminuir)

        spacer1 = QWidget()
        spacer1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        expand_layout = QHBoxLayout()
        expand_layout.addWidget(spacer1)
        expand_layout.addWidget(self.expand_button)

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
        vlayout.addLayout(expand_layout)
        vlayout.addWidget(self.stackedwidget)
        vlayout.addLayout(butao_layout)

        self.setLayout(vlayout)
        self.setWindowTitle("Editar Dados")

    def expandir_diminuir(self):

        if self.expand_button.text() == "+":
            self.expand_button.setText("-")
            self.stackedwidget.setCurrentIndex(1)
        else:
            self.expand_button.setText("+")
            self.stackedwidget.setCurrentIndex(0)

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
            self.desconto_produto.setRange(0 , self.total_bruto)

        subtotal, desconto, taxa, total = self.calcula_valores()

        self.total_geral_label.setText(str(total))
        self.taxa_label.setText(str(taxa))
        self.desconto_label.setText(str(desconto))
        self.valor_label.setText(str(self.total_bruto))
        self.total_label.setText(str(subtotal))

    def calcula_valores(self):

        if self.desconto_percentual.isChecked():
            # Calcula desconto baseando em percentagem
            desconto = Decimal(self.total_bruto) * Decimal(self.desconto_produto.value()) / 100
        else:
            # Calcula desconto baseando em Valor
            desconto = Decimal(self.desconto_produto.value())

        # Fiz append de '0' para casos em que a combobox taxa for vazia
        valor_taxa = str(self.taxa_produto.currentText()) + '0'

        subtotal = Decimal(self.total_bruto) - desconto

        if int(valor_taxa) > 0 :

            if self.parent().imposto_incluso:
                print("Subtotal", subtotal)
                print("Taxa", Decimal(str(self.taxa_produto.currentText())) / 100)
                print("Taxa do subtotal", 1 + Decimal(str(self.taxa_produto.currentText())) / 100)

                subtotal = subtotal / (1 + Decimal(str(self.taxa_produto.currentText())) / 100)

            taxa = subtotal * Decimal(str(self.taxa_produto.currentText())) / 100

        else:
            taxa = Decimal(0)

        print("Subtotal 2", subtotal)

        total = subtotal + taxa

        return subtotal, desconto, taxa, total

    def validar_dados(self):

        # Gets the cod, preco, custo, foto, nome, quantidade e codtaxa of the product
        # produtos.cod, produtos.preco, produtos.custo, produtos.foto, produtos.nome,
        #         produtosdetalhe.quantidade, produtos.codtaxa
        detalhes = self.parent().facturacao_modulo.get_produto_detalhe(self.cod_produto, self.parent().codarmazem)

        if len(detalhes) == 0: return False

        subtotal, desconto, taxa_, total = self.calcula_valores()

        self.preco_unitario = Decimal(self.preco_produto.value())
        self.quantidade_unitario = Decimal(self.quantidade_produto.value())

        self.custoproduto = detalhes[2]
        self.custo_do_produto = Decimal(self.custoproduto)
        self.custo = self.quantidade_unitario * self.custo_do_produto
        
        # Para ver se a quantidade existe na base de dados ou nao
        self.quantidade_existente = detalhes[5]
    
        self.desconto = desconto
        self.subtotal = subtotal

        self.lucro = self.subtotal - self.custo
        self.taxa = taxa_
        self.total = total

        return True

    def aceitar(self):
        if self.parent() is not None:

            try:
                if self.validar_dados() is True:
                    # Actualizar dados

                    self.parent().facturacao_modulo.actualizar_detalhes = True
                    self.parent().cod_produto = self.cod_produto
                    self.parent().facturacao_modulo.codproduto = self.cod_produto
                    self.parent().custo_do_produto = Decimal(self.custo_do_produto)
                    self.parent().preco_unitario = Decimal(self.preco_unitario)
                    self.parent().quantidade_unitario = Decimal(self.quantidade_unitario)
                    self.parent().desconto_do_produto = Decimal(self.desconto)
                    self.parent().taxa_do_produto = Decimal(self.taxa)
                    self.parent().subtotal_do_produto = Decimal(self.subtotal)
                    self.parent().total_do_produto = Decimal(self.total)
                    self.parent().lucro_do_produto = Decimal(self.lucro)

                    if self.parent().add_record() is True:
                        self.close()

            except Exception as e:
                QMessageBox.warning(self, "Erro", "Houve um erro na operação:\n{}.".format(e))
                self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    helloPythonWidget = EditarValores()
    helloPythonWidget.show()

    sys.exit(app.exec_())

