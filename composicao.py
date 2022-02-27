import sys

from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, \
    QToolBar, QGroupBox, QLineEdit, QFormLayout, QPushButton, \
    QSizePolicy, QWidget, QAction, QApplication, QMessageBox

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from striped_table import StripedTable
from maindialog import Dialog
from pricespinbox import price
from sortmodel import MyTableModel


def fill_products_table(parent, *args):
    """

    :param args: sql, cursor, listview, abstract_model, table_header
    :return:
    """
    if len(args) < 6:
        raise ValueError("The number or args must be at least 2")

    sql = args[0]
    db_cursor = args[1]
    list_view = args[2]
    list_model = args[3]

    db_cursor.execute(sql)
    lista = db_cursor.fetchall()

    if len(lista) > 0:
        table_data = [tuple(str(item) for item in t) for t in lista]
    else:
        table_data = [""]

    header = args[5]
    try:
        table_model = list_model(table_data, header, parent)
        # set the table model
        total_items = table_model.rowCount(parent)
        list_view.setModel(table_model)
        list_view.setColumnHidden(0, True)
        list_view.setColumnHidden(3, True)
        list_view.setColumnHidden(4, True)

    except Exception as e:
        return False

    nrows = len(table_data)
    for row in range(nrows):
        list_view.setRowHeight(row, 30)


class Composicao(Dialog):
    cod_produto = None

    def __init__(self, parent=None):
        super(Composicao, self).__init__(parent)

        self.ui()
        self.setWindowTitle("Composição de Produtos")

    def ui(self):
        """Main User Interface Method"""

        self.quanitidade_produto = price()
        self.quanitidade_composicao = price()

        self.lista_produtos = StripedTable()
        self.lista_produtos_2 = StripedTable()

        nome_produto = QLineEdit()
        nome_produto.setEnabled(False)

        formlay = QFormLayout()
        formlay.addRow(QLabel("Produto"), nome_produto)
        formlay.addRow(QLabel("Quantidade"), self.quanitidade_produto)

        formlay_2 = QFormLayout()
        formlay_2.addRow(QLabel("Quantidade"), self.quanitidade_composicao)
        f_lay = QVBoxLayout()
        f_lay.addWidget(self.lista_produtos)
        f_lay.addLayout(formlay_2)

        lista_grupo = QGroupBox("Lista de Produtos")
        lista_grupo.setLayout(f_lay)

        add_action = QAction(QIcon("./icons/add_2.ico"), "Adicionar", self)
        add_action.triggered.connect(self.add_product)
        remove_action = QAction(QIcon('./icons/remove.ico'), "Remover", self)

        action_toolbar = QToolBar()
        action_toolbar.setOrientation(Qt.Vertical)
        action_toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        action_toolbar.addAction(add_action)
        action_toolbar.addAction(remove_action)

        formlay_3 = QFormLayout()
        formlay_3.addWidget(self.lista_produtos_2)

        lista_composicao = QGroupBox("Composição")
        lista_composicao.setLayout(formlay_3)

        hlay = QHBoxLayout()
        hlay.addWidget(lista_grupo)
        hlay.addWidget(action_toolbar)
        hlay.addWidget(lista_composicao)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.close)
        btnlay = QHBoxLayout()
        btnlay.addWidget(spacer)
        btnlay.addWidget(ok_btn)

        mainlay = QVBoxLayout()
        mainlay.addLayout(formlay)
        mainlay.addLayout(hlay)
        mainlay.addLayout(btnlay)
        mainlay.setContentsMargins(10, 10, 10, 10)

        self.layout().addLayout(mainlay)

    def validation(self):
        if self.quanitidade_produto.value() == 0:
            QMessageBox.warning(self, "Erro", "A Quantidade do Produto deve ser Maior que 0 (zero).")
            self.quanitidade_produto.setFocus()
            return False

        if self.cod_produto is None:
            QMessageBox.warning(self, "Erro", "Selecione o produto na Lista de Produtos.")
            return False

        if self.quanitidade_composicao.value() == 0:
            QMessageBox.warning(self, "Erro", "A Quantidade da composição deve ser Maior que 0 (zero).")
            self.quanitidade_composicao.setFocus()
            return False

        return True

    def add_product(self):
        if self.validation() is False:
            return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_dialog = Composicao()
    main_dialog.show()
    sys.exit(app.exec_())
