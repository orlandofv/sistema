# -*- coding: utf-8 -*-
"""
Created on Fri Mar 02 23:18:43 2012

@author: lims
"""

from decimal import Decimal
import datetime
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QSpinBox, QFormLayout, QVBoxLayout, QToolBar, QMessageBox,\
    QWidget, QAction, QApplication, QComboBox, QPlainTextEdit, QDateTimeEdit, QCalendarWidget, QHBoxLayout, \
    QPushButton
from PyQt5.QtPrintSupport import QPrintPreviewDialog

from PyQt5.QtCore import Qt, QDateTime, QDateTime
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QTextDocument

import sys
from time import localtime, strftime

from pricespinbox import price
from utilities import codigo as cd
import sqlite3 as lite

DB_FILENAME = "dados.tsdb"
DATA_HORA_FORMATADA = strftime("%Y-%m-%d %H:%M:%S", localtime())
DATA_ACTUAL = datetime.date.today()
ANO_ACTUAL = DATA_ACTUAL.year
DIA = DATA_ACTUAL.day
MES = DATA_ACTUAL.month
LISTA_DE_PRECOS = []
PAGAMENTO = ["PAGAMENTO DIRECTO", "TRANSFERENCIA", "CHEQUE", "CASH", "M-PESA", "CONTA MOVEL", "M-CASH", "E-MOLA"]


class Check_in(QDialog):
    valor_total_a_pagar = Decimal(0)
    valor_total_da_divida = Decimal(0)
    valor_total_pago = Decimal(0)
    valor_do_quarto = Decimal(0)
    codigo = 0
    codfacturacao = "FT" + cd("FT" + "abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")

    def __init__(self, parent=None):
        super(Check_in, self).__init__(parent)
        self.html = """<p style= "background-image: './images/control.png'" > 
                <h2 > Cadastro de Entradas (Check In) </h2> </p> """

        self.accoes()
        self.ui()

        self.cur = self.parent().cur
        self.conn = self.parent().conn
        self.user = self.parent().user
        self.caixa_numero = self.parent().caixa_numero
        self.empresa_logo = self.parent().empresa_logo
        self.empresa = self.parent().empresa
        self.empresa_endereco = self.parent().empresa_endereco
        self.empresa_contactos = self.parent().empresa_contactos
        self.empresa_email = self.parent().empresa_email
        self.empresa_web = self.parent().empresa_web
        self.empresa_nuit = self.parent().empresa_nuit
        self.empresa_casas_decimais = self.parent().empresa_casas_decimais
        self.licenca = self.parent().licenca
        self.contas = self.parent().contas

        self.codfacturacao = "FT" + cd("FT" + "abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")
        self.calcula_valor()

    def ui(self):

        self.titulo = QLabel(self.html)
        self.quarto_numero = QComboBox()
        self.quarto_numero.currentIndexChanged.connect(self.calcula_valor)
        self.quarto_numero.currentIndexChanged.connect(lambda: self.get_preco(self.quarto_numero.currentText()))
        quarto_buton = QPushButton("...")
        quarto_buton.clicked.connect(self.cria_quartos)
        quarto_buton.setMaximumWidth(40)
        quarto_lay = QHBoxLayout()
        quarto_lay.setContentsMargins(0, 0, 0, 0)
        quarto_lay.addWidget(self.quarto_numero)
        quarto_lay.addWidget(quarto_buton)
        quarto_widget = QWidget()
        quarto_widget.setLayout(quarto_lay)
        self.nome_hospede = QComboBox()
        self.nome_hospede.currentIndexChanged.connect(self.calcula_valor)
        hospede_buton = QPushButton("...")
        hospede_buton.clicked.connect(self.cria_hospedes)
        hospede_buton.setMaximumWidth(40)
        hospede_lay = QHBoxLayout()
        hospede_lay.setContentsMargins(0, 0, 0, 0)
        hospede_lay.addWidget(self.nome_hospede)
        hospede_lay.addWidget(hospede_buton)
        hospede_widget = QWidget()
        hospede_widget.setLayout(hospede_lay)
        self.data_entrada = QDateTimeEdit()
        self.data_entrada.setDateTime(QDateTime.currentDateTime())
        self.data_entrada.dateChanged.connect(self.calcula_valor)
        # self.data_entrada.dateChanged.connect(lambda: self.get_preco(self.quarto_numero.currentText()))
        self.data_entrada.setCalendarPopup(True)
        self.dias = QSpinBox()
        self.dias.setRange(1, 999999)
        self.dias.setEnabled(False)
        # self.data_entrada.setDateTime(DATA_HORA_FORMATADA)
        self.data_saida = QDateTimeEdit()
        self.data_saida.dateChanged.connect(self.calcula_valor)
        # self.data_saida.dateChanged.connect(lambda: self.get_preco(self.quarto_numero.currentText()))
        self.data_saida.setCalendarPopup(True)
        # self.data_saida.setDateTime(DATA_HORA_FORMATADA)
        self.caledar1 = QCalendarWidget()
        self.caledar2 = QCalendarWidget()
        self.data_entrada.setCalendarWidget(self.caledar1)
        self.data_saida.setCalendarWidget(self.caledar2)
        self.data_saida.setDateTime(QDateTime.currentDateTime().addDays(7))
        self.total_a_pagar = price()
        self.total_a_pagar.setEnabled(False)
        self.total_a_pagar.valueChanged.connect(self.limita_pagamento)
        self.total_pago = price()
        self.total_pago.valueChanged.connect(self.calcula_saldo)
        self.total_divida = price()
        self.obs = QPlainTextEdit()
        self.vouncher = QLineEdit()
        self.moeda = QLineEdit()
        self.moeda.setText("Metical")
        self.forma_pagamento = QComboBox()
        self.forma_pagamento.setEditable(True)
        self.forma_pagamento.addItems(PAGAMENTO)
        self.forma_pagamento.setCurrentText("PAGAMENTO DIRECTO")

        grid = QFormLayout()

        grid.addRow(QLabel("Selecione o quarto"), quarto_widget)
        grid.addRow(QLabel("Hóspede"), hospede_widget)
        grid.addRow(QLabel("Voucher"), self.vouncher)
        grid.addRow(QLabel("Forma de Pagamento"), self.forma_pagamento)
        grid.addRow(QLabel("Moeda"), self.moeda)
        grid.addRow(QLabel("Data de Entrada"), self.data_entrada)
        grid.addRow(QLabel("Data de Saída"), self.data_saida)
        grid.addRow(QLabel("Total de dias"), self.dias)
        grid.addRow(QLabel("Valor a pagar"), self.total_a_pagar)
        grid.addRow(QLabel("Valor Pago"), self.total_pago)
        grid.addRow(QLabel("Valor em Divida"), self.total_divida)
        grid.addRow(QLabel("Observações"), self.obs)

        vLay = QVBoxLayout(self)
        vLay.setContentsMargins(0, 0, 0, 0)

        cLay = QVBoxLayout()
        cLay.setContentsMargins(10, 10, 10, 10)

        cLay.addLayout(grid)

        vLay.addWidget(self.titulo)
        vLay.addLayout(cLay)
        vLay.addWidget(self.tool)
        self.setLayout(vLay)

        self.setWindowTitle("Entradas (Check In)")

        style = """
            margin: 0;
            padding: 0;
            border-image:url(./images/transferir.jpg) 30 30 stretch;
            background:#303030;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 12px;
            color: #FFFFFF;
        """

        self.titulo.setStyleSheet(style)

    def cria_clientes(self):
        from clientes import Cliente

        cl = Cliente(self)
        cl.setModal(True)
        cl.show()

    def cria_hospedes(self):
        from hospedes import Hospede

        cl = Hospede(self)
        cl.setModal(True)
        cl.show()

    def cria_quartos(self):
        from quartos import Quarto

        cl = Quarto(self)
        cl.setModal(True)
        cl.show()

    def enche_hospedes(self):
        sql = """SELECT nome, apelido from hospedes where estado=1"""

        self.cur.execute(sql)
        data = self.cur.fetchall()

        self.nome_hospede.clear()

        if len(data) > 0:
            for item in data:
                nome = "{}".format(item[0])
                self.nome_hospede.addItem(nome)

            return True

        return False

    def enche_quartos(self):

        sql = """SELECT cod, preco FROM quartos WHERE ocupado=0 order by cod"""

        self.cur.execute(sql)
        data = self.cur.fetchall()

        LISTA_DE_PRECOS = []

        self.quarto_numero.clear()

        if len(data) > 0:
            for item in data:
                self.quarto_numero.addItem(str(item[0]))
                LISTA_DE_PRECOS.append(item[1])

            return True

        return False

    def limita_pagamento(self):
        # self.total_pago.setRange(0, self.total_a_pagar.value())
        self.valor_total_a_pagar = Decimal(self.total_a_pagar.value())
        self.valor_total_pago = self.valor_total_a_pagar

    def calcula_saldo(self):

        if self.total_pago.value() > self.total_a_pagar.value():
            self.total_pago.setValue(self.total_a_pagar.value())
            return False

        self.total_divida.setValue(self.total_a_pagar.value() - self.total_pago.value())

        return True

    def calcula_valor(self):

        if self.quarto_numero.currentText() == "":
            return False

        valor_do_quarto = self.get_preco(int(self.quarto_numero.currentText()))
        dias = self.get_dias()

        total = dias * valor_do_quarto

        self.dias.setValue(dias)
        self.total_a_pagar.setValue(total)
        self.total_pago.setValue(total)

        return True

    def get_dias(self):

        entrada = self.data_entrada.dateTime().toPyDateTime()
        saida = self.data_saida.dateTime().toPyDateTime()

        if saida <= entrada:
            self.data_saida.setDateTime(self.data_entrada.dateTime())
            dias = 1
            self.dias.setValue(dias)
        else:
            diff = saida - entrada
            dias = int(diff.days)

        return dias

    def get_preco(self, cod):
        if cod == "":
            return

        sql = """SELECT preco from quartos WHERE cod={}""".format(int(cod))
        self.cur.execute(sql)

        data = self.cur.fetchall()

        if len(data) > 0:
            preco = float(data[0][0])
            self.valor_do_quarto = Decimal(preco)

        return self.valor_do_quarto

    def accoes(self):
        self.tool = QToolBar()
        self.tool.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.tool.setContextMenuPolicy(Qt.PreventContextMenu)

        gravar = QAction(QIcon("./images/ok.png"), "Gravar\nDados", self)
        eliminar = QAction(QIcon("./icons/new.ico"), "Limpar\nCampos", self)

        fechar = QAction(QIcon("./images/filequit.png"), "&Fechar", self)

        self.tool.addAction(gravar)
        self.tool.addAction(eliminar)

        self.tool.addSeparator()
        self.tool.addAction(fechar)

        gravar.triggered.connect(self.add_record)
        fechar.triggered.connect(self.fechar)

    def closeEvent(self, evt):
        parent = self.parent()
        try:
            if parent is not None:
                parent.fill_table()
                parent.enchecheck_in()
        except Exception as e:
            return

    def fechar(self):
        self.close()


    def validacao(self):

        if str(self.nome.text()) == "":
            QMessageBox.information(self, "Erro", "Nome do Check_in inválido")
            self.nome.setFocus()
            return False
        else:
            return True

    def mostrar_registo(self, cod):

        sql = """SELECT * FROM check_in WHERE cod="{}" """.format(cod)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            self.data_entrada.setDateTime(data[0][1])
            self.data_saida.setDateTime(data[0][2])
            self.nome_hospede.setCurrentText(self.get_nome_cliente(data[0][3]))
            self.quarto_numero.setCurrentText(str(data[0][4]))
            self.total_a_pagar.setValue(data[0][5])
            self.total_pago.setValue(data[0][6])
            self.total_divida.setValue(data[0][7])
            self.obs.setPlainText(data[0][8])
            self.vouncher.setText(data[0][15])
            self.forma_pagamento.setCurrentText(data[0][16])
            self.moeda.setText(data[0][17])
            self.codfacturacao = data[0][18]

    def existe(self, codigo):

        sql = """SELECT cod from check_in WHERE cod = "{codigo}" """.format(codigo=str(codigo))

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            self.codigo = codigo
            return False
        else:
            codigo = int(data[0][0])
            self.codigo = codigo
            return True

    def get_cod_cliente(self, nome):

        sql = """SELECT cod from hospedes WHERE nome="{}" """.format(nome)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        cliente = ""

        if len(data) > 0:
            cliente = data[0][0]

        return cliente

    def get_nome_cliente(self, cod):

        sql = """SELECT nome from hospedes WHERE cod="{}" """.format(cod)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        cliente = ""

        if len(data) > 0:
            cliente = data[0][0]

        return cliente

    def add_record(self):

        if self.quarto_numero.currentText() == "":
            QMessageBox.warning(self, "Quarto Indesponível", "Nenhum quarto Desponível do momento")
            return False

        if self.nome_hospede.currentText() == "":
            QMessageBox.warning(self, "Sem Hóspedes", "Cadastre Hóspedes Primeiro")
            return False

        if self.parent() is not None:
            created_by = self.parent().user
            modified_by = self.parent().user
        else:
            created_by = "User"
            modified_by = "User"

        created = QDateTime.currentDateTime().toString("yyyy-MM-dd H:mm:ss")
        modified = created

        code = self.codigo
        entrada = self.data_entrada.dateTime().toString("yyyy-MM-dd H:mm:ss")
        saida = self.data_saida.dateTime().toString("yyyy-MM-dd H:mm:ss")
        cliente = self.get_cod_cliente(self.nome_hospede.currentText())
        quarto = self.quarto_numero.currentText()
        total  = self.total_a_pagar.value()
        pago = self.total_pago.value()
        divida = self.total_divida.value()
        obs = self.obs.toPlainText()
        estado = 1
        hospede = ""
        voucher = self.vouncher.text()
        pagamento = self.forma_pagamento.currentText()
        moeda = self.moeda.text()
        codfacturacao = self.codfacturacao

        if self.existe(code) is True:

            sql = """UPDATE check_in set cod="{cod}", data_entrada="{entrada}", data_saida="{saida}", 
            cod_cliente="{cliente}", cod_quarto={quarto}, total={total}, pago={pago}, divida={divida}, 
            obs="{obs}", modified="{modified}", modified_by="{modified_by}", hospede="{hospede}", voucher="{voucher}",
            pagamento="{pagamento}", moeda="{moeda}", codfacturacao="{codfacturacao}" WHERE cod="{cod}"
            """.format(cod=code, entrada=entrada, saida=saida, cliente=cliente, quarto=quarto,
                       total=total, pago=pago, divida=divida, obs=obs
                       , modified=modified, modified_by=modified_by, hospede=hospede, voucher=voucher,
                       pagamento=pagamento, moeda=moeda, codfacturacao=codfacturacao)
        else:
            values = """ "{entrada}", "{saida}", "{cliente}", {quarto}, {total}, {pago}, {divida}, "{obs}", 
            "{created}", "{modified}", "{modified_by}", "{created_by}", {estado}, "{hospede}", "{voucher}", 
            "{pagamento}", "{moeda}", "{codfacturacao}" 
            """.format(entrada=entrada, saida=saida, cliente=cliente,
                       quarto=quarto, total=total, pago=pago, divida=divida, obs=obs,
                       created=created, modified=modified,
                       modified_by=modified_by, created_by=created_by, estado=estado,
                       hospede=hospede, voucher=voucher,
                       pagamento=pagamento, moeda=moeda, codfacturacao=codfacturacao
                       )

            sql = """INSERT INTO check_in (data_entrada, data_saida, cod_cliente, cod_quarto, total, pago, 
            divida, obs, created, modified, modified_by, created_by, estado,
            hospede, voucher, pagamento, moeda, codfacturacao) values({value})""".format(value=values)


        print("Ocupando o quarto <b>{}</b>".format(quarto))
        sql_quartos = """UPDATE quartos SET ocupado = 1 WHERE cod={} """.format(quarto)
        # Ocupa o Cliente
        sql_hospedes = """UPDATE hospedes SET estado = 0 WHERE cod="{}" """.format(cliente)

        try:
            self.cur.execute(sql_quartos)
            self.cur.execute(sql_hospedes)

            if self.parent().quarto != quarto:
                print("Desocupando o quarto <b>{}</b>".format(self.parent().quarto))
                sql_quartos_0 = """UPDATE quartos SET ocupado = 0 WHERE cod={} """.format(self.parent().quarto)

                self.cur.execute(sql_quartos_0)

            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Erro", "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
            return False

        QMessageBox.information(self, "Informação", "Registo Gravado com sucesso!")
        self.impreme_entrada(self.get_cod_checkin(), self.nome_hospede.currentText())
        self.close()
        # self.parent().fill_table()
        return True

    def get_cod_checkin(self):
        sql = "SELECT MAX(cod) from check_in"
        self.cur.execute(sql)
        data = self.cur.fetchall()
        if len(data) == 0:
            return 1

        return data[0][0]

    def detalhes_do_cliente(self, codcliente):
        sql = """SELECT * from hospedes WHERE cod="{}" """.format(codcliente)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        return data[0]

    def impreme_entrada(self, codcheckin, nome_cliente):
        sql = """SELECT * from check_in WHERE cod={} """.format(codcheckin)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        html = self.cabecalho()

        cliente = self.detalhes_do_cliente(self.get_cod_cliente(nome_cliente))

        if len(data) > 0:
            for item in data:
                html += "<p align='left'>Exmo Sr(a).:</p>"
                html += "<p align='left'><b>{} {}</b></p>".format(cliente[1], cliente[2])
                html += "<p align='left'>Género: <b>{}</b></p>".format(cliente[4])
                html += "<p align='left'><b>{}: {}</b>, validade: <b>{}</b></p>".format(cliente[9], cliente[10], cliente[11])
                html += "<p align='left'>Nacionalidade:<b>{}</b></p>".format(cliente[12])
                html += "<p align='left'>Contactos:<b>{}</b></p>".format(cliente[7])
                html += "<p align='left'>Emergência:<b>{}</b></p>".format(cliente[8])

                html += "<br>"
                html += "<p align='left'>Detalhes da Hospedagem</p>"
                html += "<hr>"
                html += "<p align='left'>Data de Entrada: <b>{}</b></p>".format(item[1])
                html += "<p align='left'>Data de Saída: <b>{}</b></p>".format(item[2])
                html += "<p align='left'>Quarto: <b>{}</b></p>".format(item[4])
                # html += "<p align='left'>Total: <b>{}</b></p>".format(item[5])
                # html += "<p align='left'>Pago: <b>{}</b></p>".format(item[6])
                # html += "<p align='left'>Saldo: <b>{}</b></p>".format(item[7])
                # html += "<p align='left'>Moeda: <b>{}</b></p>".format(item[17])
                # html += "<p align='left'>Forma de Pagamento: <b>{}</b></p>".format(item[16])
                html += "<br>"
                html += "<p><b>{}</b></p>".format(item[8])
                html += "<hr>"
                html += "<p align='left'>Atendido por: <b>{}</b></p>".format(item[11])

        document = QTextDocument()

        document.setHtml(html)

        dlg = QPrintPreviewDialog(self)
        dlg.paintRequested.connect(document.print_)
        dlg.showMaximized()
        dlg.exec_()

    def cabecalho(self):
        html = "<p align='left'><b>{}</b></p>".format(self.empresa_logo)
        html += "<p align='left'><b>{}</b></p>".format(self.empresa)
        html += "<p align='left'><b>{}</b></p>".format(self.empresa_endereco)
        html += "<p align='left'>NUIT: <b>{}</b></p>".format(self.empresa_nuit)
        html += "<p align='left'>Contactos: <b>{}</b></p>".format(self.empresa_contactos)
        html += "<p align='left'>Email: <b>{}</b></p>".format(self.empresa_email)
        html += "<p align='left'>Website: <b>{}</b></p>".format(self.empresa_web)
        html += "<hr>".format(self.empresa_web)

        return html

    def connect_db(self):
        # Connect to database and retrieves data
        try:
            self.conn = lite.connect(DB_FILENAME)
            self.cur = self.conn.cursor()

        except Exception as e:
            QMessageBox.critical(self, "Erro ao conectar a Base de Dados",
                                 "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
            sys.exit(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    helloPythonWidget = Check_in()
    helloPythonWidget.show()

    sys.exit(app.exec_())