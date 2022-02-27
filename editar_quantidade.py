from decimal import Decimal
from PyQt5.QtWidgets import (QTabWidget, QLabel, QLineEdit, QFormLayout, QVBoxLayout, QToolBar, QMessageBox,
                             QPlainTextEdit, QAction, QApplication, QComboBox, QPushButton, QFileDialog, QHBoxLayout,
                             QGroupBox, QGridLayout, QSizePolicy, QWidget, QDialog)
from PyQt5.QtCore import Qt, QDate, QRegExp
from PyQt5.QtGui import QFont, QRegExpValidator
import sys

from teclado_numerico import Teclado

class EditarValores(QDialog):
    def __init__(self, parent=None):
        super(EditarValores, self).__init__(parent)

        self.cod_produto = None
        self.codigogeral = None
        self.cod_facturacaodetalhe = None

        boldFont = QFont('Consolas', 16)
        boldFont.setBold(True)

        regex = QRegExp("^(?:\d+\.?\d*|\d*\.?\d+)*$")
        validator = QRegExpValidator(regex)

        self.nome_produto = QPlainTextEdit()
        self.nome_produto.setEnabled(False)
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

        butao_quantidade = QPushButton("...")
        butao_quantidade.clicked.connect(self.editar_quantidade)
        butao_quantidade.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.butao_preco = QPushButton("...")
        self.butao_preco.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.butao_preco.clicked.connect(self.editar_preco)

        layout = QGridLayout()

        produto = QLabel("Produto")
        produto.setFont(boldFont)
        quantidade = QLabel("Quantidade")
        quantidade.setFont(boldFont)
        preco = QLabel("Preço")
        preco.setFont(boldFont)

        layout.addWidget(self.nome_produto, 0, 0, 1, 2)
        layout.addWidget(quantidade, 1, 0)
        layout.addWidget(self.quantidade_produto, 2, 0)
        layout.addWidget(butao_quantidade, 2, 1)
        layout.addWidget(preco, 3, 0)
        layout.addWidget(self.preco_produto, 4, 0)
        layout.addWidget(self.butao_preco, 4, 1)

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

        self.setWindowTitle("Editar Dados")

    def editar_quantidade(self):
        tc = Teclado(self.quantidade_produto)
        tc.setModal(True)
        tc.show()

    def editar_preco(self):
        tc = Teclado(self.preco_produto)
        tc.setModal(True)
        tc.show()

    def aceitar(self):
        if self.parent() is not None:
            print("Aceitando Valores...")

            try:
                self.parent().preco_unitario = Decimal(self.preco_produto.text())
                self.parent().quantidade_unitario = Decimal(self.quantidade_produto.text())
                self.parent().alterar_quantidade = True
                self.parent().add_record()
            except Exception as e:
                print(e)

        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    helloPythonWidget = EditarValores()
    helloPythonWidget.show()

    sys.exit(app.exec_())

