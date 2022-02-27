import sys
from decimal import Decimal

from PyQt5.QtWidgets import (QApplication, QLabel, QSpinBox,
                             QHBoxLayout, QVBoxLayout, QSplitter, QPushButton,
                             QWidget, QSizePolicy, QMessageBox)

from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

from maindialog import Dialog
from sortmodel import MyTableModel
from striped_table import StripedTable
from utilities import codigo as cd
from utilities import ANO_ACTUAL, DATA_HORA_FORMATADA_MYSQL, MES
from pricespinbox import price


class Divisao(Dialog):
    def __init__(self, parent=None, titulo="", imagem=""):
        super(Divisao, self).__init__(parent, titulo, imagem)

        self.ui()

        self.caixa_numero = self.parent().caixa_numero
        self.codarmazem = self.parent().codarmazem
        self.user = self.parent().user

        self.adicionar_quantidade = False

        self.mesa_1 = 0
        self.mesa_2 = 0
        self.current_id = 0
        self.current_id_2 = 0
        self.cod_produto = None
        self.cod_produto_2 = None

        self.quantidade = 0
        self.subtotal = 0
        self.taxa = 0
        self.total = 0
        self.lucro = 0
        self.desconto = 0
        self.custo = 0
        self.preco = 0

        self.quantidade_2 = 0
        self.subtotal_2 = 0
        self.taxa_2 = 0
        self.total_2 = 0
        self.lucro_2 = 0
        self.desconto_2 = 0
        self.custo_2 = 0
        self.preco_2 = 0

        self.conn = self.parent().conn
        self.cur = self.conn.cursor()
        self.codigogeral = self.parent().codigogeral
        print(self.codigogeral)
        self.fill_table()
        self.fill_table2(self.spin_mesa_2.value())

        self.mesas_livres = []

        for x in range(1, self.parent().parent().numero_mesas + 1):
            if self.verificar_mesa(x) is False:
                self.mesas_livres.append(x)

    def ui(self):
        spin_style = """
            QSpinBox, QDoubleSpinBox {
                font-size: 36px;
            }
        """

        label_font = QFont('Oldman BookStyle', 14)
        label_font.setBold(True)

        self.spin_quantidade_1 = price()
        self.spin_quantidade_1.setStyleSheet(spin_style)
        self.spin_quantidade_2 = price()
        self.spin_quantidade_2.setStyleSheet(spin_style)

        self.spin_mesa_1 = QSpinBox()
        self.spin_mesa_1.setAlignment(Qt.AlignRight)
        self.spin_mesa_1.setStyleSheet(spin_style)
        self.spin_mesa_1.setEnabled(False)
        self.spin_mesa_1.setRange(1, 100)

        self.spin_mesa_2 = QSpinBox()
        self.spin_mesa_2.valueChanged.connect(self.mudar_mesa_2)
        self.spin_mesa_2.setAlignment(Qt.AlignRight)
        self.spin_mesa_2.setStyleSheet(spin_style)
        self.spin_mesa_2.setRange(1, 100)

        self.tabela_mesa_1 = StripedTable()
        self.tabela_mesa_1.clicked.connect(self.clickedslot)
        self.tabela_mesa_2 = StripedTable()
        self.tabela_mesa_2.clicked.connect(self.clickedslot_2)

        hbox1 = QHBoxLayout()

        label1 = QLabel("Da Mesa:")
        label1.setFont(label_font)

        hbox1.addWidget(label1)
        hbox1.addWidget(self.spin_mesa_1)

        self.label_total_items = QLabel("0")

        vbox1 = QVBoxLayout()
        vbox1.addLayout(hbox1)
        vbox1.addWidget(self.tabela_mesa_1)
        vbox1.addWidget(self.label_total_items)
        vbox1.addWidget(self.spin_quantidade_1)

        group1 = QWidget()
        group1.setLayout(vbox1)

        hbox2 = QHBoxLayout()

        label2 = QLabel("Para a Mesa:")
        label2.setFont(label_font)

        hbox2.addWidget(label2)
        hbox2.addWidget(self.spin_mesa_2)

        self.label_total_items_2 = QLabel("0")

        vbox2 = QVBoxLayout()
        vbox2.addLayout(hbox2)
        vbox2.addWidget(self.tabela_mesa_2)
        vbox2.addWidget(self.label_total_items_2)
        vbox2.addWidget(self.spin_quantidade_2)

        group2 = QWidget()
        group2.setLayout(vbox2)

        button_1 = QPushButton(QIcon('./icons/Deleket-Soft-Scraps-Button-Next.ico'), "")
        button_1.clicked.connect(self.dividir_conta_1_2)
        button_1.setMinimumSize(50, 50)
        button_2 = QPushButton(QIcon('./icons/previous.ico'), "")
        button_2.setMinimumSize(50, 50)
        button_2.clicked.connect(self.dividir_conta_2_1)

        vbox3 = QVBoxLayout()
        vbox3.setContentsMargins(0, 50, 0, 0)
        vbox3.setSpacing(0)

        vbox3.addWidget(button_1)
        vbox3.addWidget(button_2)

        group3 = QWidget()
        group3.setLayout(vbox3)

        splitter = QSplitter()

        splitter.addWidget(group1)
        splitter.addWidget(group3)
        splitter.addWidget(group2)

        btn_cancel = QPushButton(QIcon(""), "&Fechar")
        btn_cancel.setDefault(True)

        btn_cancel.clicked.connect(self.close)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        btn_box = QHBoxLayout()
        btn_box.setContentsMargins(5, 5, 10, 5)

        btn_box.addWidget(spacer)
        btn_box.addWidget(btn_cancel)

        mainlayout = QVBoxLayout()
        mainlayout.setContentsMargins(5, 5, 5, 5)

        mainlayout.addWidget(splitter)
        mainlayout.addLayout(btn_box)

        self.layout().addLayout(mainlayout)

        self.setWindowTitle("Divisão de Conta")

    def dividir_conta_2_1(self):
        if self.spin_mesa_1.value() == self.spin_mesa_2.value():
            QMessageBox.warning(self, "Erro", "A Mesas devem ser diferentes!")
            return False

        # A quantidade a transferir deve ser maior que zero(0)
        if self.spin_quantidade_2.value() == 0:
            QMessageBox.warning(self, "Quantidade", "A Quantidade deve ser maior que zero (0).")
            return False

        # A quantidade a transferir não deve ser maior que a quantidade existente
        if self.spin_quantidade_2.value() > self.quantidade_2:
            self.spin_quantidade_2.setValue(self.quantidade_2)
            return False

        quantidade_total = self.quantidade_2
        quantidade_destino = self.spin_quantidade_2.value()
        quantidade_remanescente = quantidade_total - quantidade_destino

        # codfacturacao, codproduto, custo_produto, preco, quantidade, subtotal_produto, desconto_produto,
        # taxa_produto, total_produto, lucro_produto, codarmazem
        self.current_id = self.parent().codigogeral

        print("Codigos: 1. {}, 2. {} ".format(self.current_id, self.current_id_2))

        self.enviar_conta_1_2(self.current_id, self.cod_produto_2, self.custo_2, self.preco_2, quantidade_destino,
                              self.subtotal_2, self.desconto_2, self.taxa_2, self.total_2, self.lucro_2, self.codarmazem)

        # Actualiza dados da tabela destino
        print('Quantidade 1: {}'.format(quantidade_destino))

        if self.adicionar_quantidade is True:
            self.update_data_2(self.current_id, self.cod_produto_2, self.preco_2, quantidade_destino,
                               self.taxa_2, self.custo_2)
        else:
            self.update_data(self.current_id, self.cod_produto_2, self.preco_2, quantidade_destino,
                               self.taxa_2, self.custo_2)

        # Actualiza dados da tabela origem
        print('Quantidade 2: {}'.format(quantidade_remanescente))

        self.update_data(self.current_id_2, self.cod_produto_2, self.preco_2, quantidade_remanescente,
                         self.taxa_2, self.custo_2)

        # Se a quantidade que resta for igual a zero apagamos o produto origem
        self.delete_product(self.cod_produto_2, self.current_id_2)

        self.parent().calcula_total_geral()
        self.fill_table()
        self.fill_table2(self.spin_mesa_2.value())

    def dividir_conta_1_2(self):
        if self.spin_mesa_1.value() == self.spin_mesa_2.value():
            QMessageBox.warning(self, "Erro", "A Mesas devem ser diferentes!")
            return False

        # A quantidade a transferir deve ser maior que zero(0)
        if self.spin_quantidade_1.value() == 0:
            QMessageBox.warning(self, "Quantidade", "A Quantidade deve ser maior que zero (0).")
            return False

        # A quantidade a transferir não deve ser maior que a quantidade existente
        if self.spin_quantidade_1.value() > self.quantidade:
            self.spin_quantidade_1.setValue(self.quantidade)
            return False

        quantidade_total = self.quantidade
        quantidade_destino = self.spin_quantidade_1.value()
        quantidade_remanescente = quantidade_total - quantidade_destino

        # codfacturacao, codproduto, custo_produto, preco, quantidade, subtotal_produto, desconto_produto,
        # taxa_produto, total_produto, lucro_produto, codarmazem

        print("Codigos: 1. {}, 2. {} ".format(self.current_id, self.current_id_2))

        self.enviar_conta_1_2(self.current_id_2, self.cod_produto, self.custo, self.preco, quantidade_destino,
                              self.subtotal, self.desconto, self.taxa, self.total, self.lucro, self.codarmazem)

        # Actualiza dados da tabela destino
        print('Quantidade 1: {}'.format(quantidade_destino))

        if self.adicionar_quantidade is True:
            self.update_data_2(self.current_id_2, self.cod_produto, self.preco, quantidade_destino,
                             self.taxa, self.custo)
        else:
            self.update_data(self.current_id_2, self.cod_produto, self.preco, quantidade_destino,
                             self.taxa, self.custo)

        # Actualiza dados da tabela origem
        print('Quantidade 2: {}'.format(quantidade_remanescente))

        self.update_data(self.current_id, self.cod_produto, self.preco, quantidade_remanescente,
                         self.taxa, self.custo)

        # Se a quantidade que resta for igual a zero apagamos o produto origem
        self.delete_product(self.cod_produto, self.current_id)

        self.parent().calcula_total_geral()
        self.fill_table()
        self.fill_table2(self.spin_mesa_2.value())

    def update_data(self, cod_facturacao, cod_produto, preco, quantidade, taxa, custo):
        """Updates data records"""
        subtotal_linha = Decimal(quantidade) * Decimal(preco)
        taxa_linha = Decimal(taxa)
        total_linha = subtotal_linha * taxa_linha + subtotal_linha
        custo_linha = Decimal(custo) * Decimal(quantidade)
        lucro_linha = subtotal_linha - custo_linha

        facturacao_detalhe_sql = """UPDATE facturacaodetalhe SET preco={}, quantidade={}, custo={},
        subtotal={}, taxa={}, total={}, lucro={} 
        WHERE codfacturacao="{}" and codproduto="{}" """.format(preco, quantidade, custo_linha, subtotal_linha,
                                                                taxa_linha, total_linha, lucro_linha, cod_facturacao,
                                                                cod_produto)

        print(facturacao_detalhe_sql)

        try:
            self.cur.execute(facturacao_detalhe_sql)
            self.conn.commit()
            return True
        except Exception as e:
            print("Erro:\n'{}' ".format(e))
            return False

    def update_data_2(self, cod_facturacao, cod_produto, preco, quantidade, taxa, custo):
        """Updates data records"""
        subtotal_linha = Decimal(quantidade) * Decimal(preco)
        taxa_linha = Decimal(taxa)
        total_linha = subtotal_linha * taxa_linha + subtotal_linha
        custo_linha = Decimal(custo) * Decimal(quantidade)
        lucro_linha = subtotal_linha - custo_linha

        facturacao_detalhe_sql = """UPDATE facturacaodetalhe SET preco={}, quantidade=quantidade+{}, custo=custo+{},
        subtotal=subtotal+{}, taxa=taxa+{}, total=total+{}, lucro=lucro+{} 
        WHERE codfacturacao="{}" and codproduto="{}" """.format(preco, quantidade, custo_linha, subtotal_linha,
                                                                taxa_linha, total_linha, lucro_linha, cod_facturacao,
                                                                cod_produto)

        print(facturacao_detalhe_sql)

        try:
            self.cur.execute(facturacao_detalhe_sql)
            self.conn.commit()
            return True
        except Exception as e:
            print("Erro:\n'{}' ".format(e))
            return False

    def enviar_conta_1_2(self, *args):
        """
        List of facturacao fields
        :param args: codfacturacao, codproduto, custo_produto, preco, quantidade, subtotal_produto, desconto_produto,
        taxa_produto, total_produto, lucro_produto, codarmazem
        :return: saves data in database
        """

        if len(args) < 11:
            print('Menor numero de argumentos, o numero de argumentos deve seguir a sequencia: ' +
                  """codfacturacao, codproduto, custo_produto, preco, quantidade, subtotal_produto, desconto_produto,
                  taxa_produto, total_produto, lucro_produto, codarmazem""")
            return False

        cod = args[0]

        # Facturacao existe
        if args[0] is not None:

            if self.existe_produto(args[1], args[0]):
                self.adicionar_quantidade = True
                print("Facturacao existe, produto existe")
                sql_fd = """
                UPDATE facturacaodetalhe SET quantidade=quantidade WHERE codfacturacao="{}" 
                """.format(cod)
            else:
                self.adicionar_quantidade = False
                print("Facturacao existe, produto nao existe")
                detalhes_values = (cod, args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8],
                                   args[8], self.codarmazem)

                sql_fd = """
                INSERT INTO facturacaodetalhe (codfacturacao, codproduto, custo, preco, quantidade,
                subtotal, desconto, taxa, total, lucro, codarmazem) VALUES {}""".format(detalhes_values)

                print(sql_fd)

        else:

            self.adicionar_quantidade = False
            print("Facturacao nao existe")

            cod = "FT" + cd("FT" + "abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")

            values = (
            cod, 1, "DC20181111111", "CL20181111111", DATA_HORA_FORMATADA_MYSQL, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, "", ANO_ACTUAL, MES, "Inserido das mesas", DATA_HORA_FORMATADA_MYSQL, DATA_HORA_FORMATADA_MYSQL,
            self.user, self.user, 0, self.caixa_numero, 0, 0, 0)

            sql_f = """
            INSERT INTO facturacao (cod, numero, coddocumento, codcliente, data, custo, subtotal, desconto,
            taxa, total, lucro, debito, credito, saldo, troco, banco, cash, tranferencia, estado, extenso, ano, mes,
            obs, created, modified, modified_by, created_by, finalizado, caixa, pago, comissao, pagamento)
            VALUES {}""".format(values)

            detalhes_values = (cod, args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8],
                               args[8], self.codarmazem)

            sql_fd = """
            INSERT INTO facturacaodetalhe (codfacturacao, codproduto, custo, preco, quantidade,
            subtotal, desconto, taxa, total, lucro, codarmazem) VALUES {}""".format(detalhes_values)

            sql = """REPLACE INTO mesas(numero, descricao, codfacturacao, estado, created, modified, modified_by, 
                        created_by, obs) VALUES ({}, "{}", "{}", {}, "{}", "{}", "{}", "{}", "{}") 
                        """.format(self.spin_mesa_2.value(), "", cod, 1,
                                   DATA_HORA_FORMATADA_MYSQL, DATA_HORA_FORMATADA_MYSQL, self.user,
                                   self.user, "")
            print(sql)

            self.cur.execute(sql_f)
            self.cur.execute(sql)
        try:
            self.cur.execute(sql_fd)
            self.conn.commit()
        except Exception as e:
            print("Erro: {}".format(e))
            return False

        return True

    def delete_product(self, cod_product, cod_facturacao):
        sql = """DELETE FROM facturacaodetalhe WHERE codproduto="{}" 
        AND codfacturacao="{}" AND quantidade=0 """.format(
            cod_product, cod_facturacao)

        print('delete: ', sql)

        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            QMessageBox.warning(self, "Erro", "Não foi possivel eliminar o registo {}.\n{}.".format(cod_product, e))

    def existe_produto(self, produto, codfacturacao):

        sql = """
            SELECT codproduto from facturacaodetalhe WHERE codproduto="{}" AND codfacturacao="{}"
        """.format(produto, codfacturacao)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if not data:
            return False

        return True

    def mudar_mesa_2(self):
        self.mesa_2 = self.spin_mesa_2.value()

        if self.mesa_2 > 0:
            self.fill_table2(self.mesa_2)

        return self.mesa_2

    # Verifica se a mesa está ocupada ou nao
    def verificar_mesa(self, numero_mesa):
        sql = """SELECT m.numero FROM mesas m INNER JOIN facturacao f ON f.cod=m.codfacturacao 
        WHERE m.numero={} AND f.finalizado=0 """.format(numero_mesa)
        self.cur.execute(sql)
        dados = self.cur.fetchall()

        if len(dados) > 0:
            return True

        return False

    def fill_table(self):
        print("Fazendo refresh da tabela 1")

        header = ["DOC", "Artigo", "Descrição", "Qty", "Subtotal", "Taxa", "Total", "Lucro", "Desconto",
                  "Custo", "Preco"]

        sql = """ select facturacao.cod, facturacaodetalhe.codproduto, produtos.nome, facturacaodetalhe.quantidade
            ,facturacaodetalhe.subtotal, facturacaodetalhe.taxa, facturacaodetalhe.total, facturacaodetalhe.lucro,
            facturacaodetalhe.desconto, facturacaodetalhe.custo, facturacaodetalhe.preco 
            from produtos INNER JOIN facturacaodetalhe ON produtos.cod=facturacaodetalhe.codproduto
            INNER JOIN facturacao  ON facturacao.cod=facturacaodetalhe.codfacturacao WHERE 
           (facturacao.cod="{facturacaocod}") """.format(facturacaocod=self.codigogeral)

        try:
            self.cur.execute(sql)
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]

        except Exception as e:
            print("Erro no fill Table: ", e)
            return

        if len(data) == 0:
            tabledata = [('', '', '', "", "", "", "", "", "")]
        else:
            tabledata = data

        try:
            # set the table model
            self.tm = MyTableModel(tabledata, header, self)
            self.totalItems = self.tm.rowCount(self)
            self.label_total_items.setText("ITEMS: {}.".format(self.totalItems))

            self.tabela_mesa_1.setModel(self.tm)
            self.tabela_mesa_1.setColumnHidden(0, True)
            self.tabela_mesa_1.setColumnHidden(1, True)
            self.tabela_mesa_1.setColumnHidden(4, True)
            self.tabela_mesa_1.setColumnHidden(5, True)
            self.tabela_mesa_1.setColumnHidden(6, True)
            self.tabela_mesa_1.setColumnHidden(7, True)
            self.tabela_mesa_1.setColumnHidden(8, True)
            self.tabela_mesa_1.setColumnHidden(9, True)
            self.tabela_mesa_1.setColumnHidden(10, True)

            self.tabela_mesa_1.setColumnWidth(2, self.tabela_mesa_1.width() * .8)
            self.tabela_mesa_1.setColumnWidth(3, self.tabela_mesa_1.width() * .2)

        except Exception as e:
            print("Erro fill 2: ", e)
            return
        # # set row height
        nrows = len(tabledata)
        for row in range(nrows):
            self.tabela_mesa_1.setRowHeight(row, 30)

    def clickedslot(self, index):

        row = int(index.row())

        indice = self.tm.index(row, 0)
        self.current_id = indice.data()

        indice_2 = self.tm.index(row, 1)
        self.cod_produto = indice_2.data()

        indice_3 = self.tm.index(row, 3)
        self.quantidade = float(indice_3.data())

        indice_4 = self.tm.index(row, 4)
        self.subtotal = indice_4.data()

        indice_5 = self.tm.index(row, 5)
        self.taxa = indice_5.data()

        indice_6 = self.tm.index(row, 6)
        self.total = indice_6.data()

        indice_7 = self.tm.index(row, 7)
        self.lucro = indice_7.data()

        indice_8 = self.tm.index(row, 8)
        self.desconto = indice_8.data()

        indice_9 = self.tm.index(row, 9)
        self.custo = indice_9.data()

        indice_10 = self.tm.index(row, 10)
        self.preco = indice_10.data()

        self.spin_quantidade_1.setValue(Decimal(self.quantidade))
        self.spin_quantidade_1.setFocus()

    def fill_table2(self, mesa):

        print("Fazendo refresh da tabela 2")

        header = ["DOC", "Artigo", "Descrição", "Qty", "Subtotal", "Taxa", "Total", "Lucro", "Desconto",
                  "Custo", "Preco"]

        sql = """SELECT f.cod, fd.codproduto, p.nome, fd.quantidade, fd.subtotal, fd.taxa, fd.total, fd.lucro,
        fd.desconto, fd.custo, fd.preco FROM mesas m 
        INNER JOIN facturacao f ON f.cod=m.codfacturacao
        INNER JOIN facturacaodetalhe fd ON f.cod=fd.codfacturacao 
        INNER JOIN produtos p ON p.cod=fd.codproduto
        WHERE m.numero={} AND f.finalizado=0 """.format(mesa)

        try:
            self.cur.execute(sql)
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]
        except Exception as e:
            print("Fill Table 3 no 2:", e)
            return False

        if len(data) == 0:
            tabledata = [('', '', '', '',)]
            self.current_id_2 = None
        else:
            tabledata = data
            self.current_id_2 = data[0][0]

        try:
            # set the table model
            self.tm2 = MyTableModel(tabledata, header, self)
            self.totalItems = self.tm2.rowCount(self)
            self.label_total_items_2.setText("ITEMS: {}.".format(self.totalItems))

            self.tabela_mesa_2.setModel(self.tm2)
            self.tabela_mesa_2.setColumnHidden(0, True)
            self.tabela_mesa_2.setColumnHidden(1, True)
            self.tabela_mesa_2.setColumnHidden(0, True)
            self.tabela_mesa_2.setColumnHidden(1, True)
            self.tabela_mesa_2.setColumnHidden(4, True)
            self.tabela_mesa_2.setColumnHidden(5, True)
            self.tabela_mesa_2.setColumnHidden(6, True)
            self.tabela_mesa_2.setColumnHidden(7, True)
            self.tabela_mesa_2.setColumnHidden(8, True)
            self.tabela_mesa_2.setColumnHidden(9, True)
            self.tabela_mesa_2.setColumnHidden(10, True)

            self.tabela_mesa_2.setColumnWidth(2, self.tabela_mesa_2.width() * .8)
            self.tabela_mesa_2.setColumnWidth(3, self.tabela_mesa_2.width() * .2)

        except Exception as e:
            print(e)
            return
        # # set row height
        nrows = len(tabledata)
        for row in range(nrows):
            self.tabela_mesa_2.setRowHeight(row, 30)

    def clickedslot_2(self, index):

        row = int(index.row())

        indice = self.tm2.index(row, 0)
        self.current_id_2 = indice.data()

        indice_2 = self.tm2.index(row, 1)
        self.cod_produto_2 = indice_2.data()

        indice_3 = self.tm2.index(row, 3)
        self.quantidade_2 = float(indice_3.data())

        indice_4 = self.tm2.index(row, 4)
        self.subtotal_2 = indice_4.data()

        indice_5 = self.tm2.index(row, 5)
        self.taxa_2 = indice_5.data()

        indice_6 = self.tm2.index(row, 6)
        self.total_2 = indice_6.data()

        indice_7 = self.tm2.index(row, 7)
        self.lucro_2 = indice_7.data()

        indice_8 = self.tm2.index(row, 8)
        self.desconto_2 = indice_8.data()

        indice_9 = self.tm2.index(row, 9)
        self.custo_2 = indice_9.data()

        indice_10 = self.tm2.index(row, 10)
        self.preco_2 = indice_10.data()

        self.spin_quantidade_2.setValue(Decimal(self.quantidade_2))
        self.spin_quantidade_2.setFocus()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    helloPythonWidget = Divisao()
    helloPythonWidget.show()

    sys.exit(app.exec_())

