# -*- coding: utf-8 -*-
"""
Created on Fri Mar 02 23:18:43 2012

@author: lims
"""
import datetime
from time import localtime, strftime

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QDateTime
from PyQt5.QtGui import QTextDocument
from PyQt5.QtPrintSupport import QPrintPreviewDialog
from check_in import Check_in

DB_FILENAME = "dados.tsdb"
DATA_HORA_FORMATADA = strftime("%Y-%m-%d %H:%M:%S", localtime())
DATA_ACTUAL = datetime.date.today()
ANO_ACTUAL = DATA_ACTUAL.year
DIA = DATA_ACTUAL.day
MES = DATA_ACTUAL.month
LISTA_DE_PRECOS = []
PAGAMENTO = ["PAGAMENTO DIRECTO", "TRANSFERENCIA", "CHEQUE", "CASH", "M-PESA", "CONTA MOVEL", "M-CASH", "E-MOLA"]


class Reservas(Check_in):

    def __init__(self, parent=None):
        super(Reservas, self).__init__(parent)
        html = """<center style= "background-image: './images/control.png'" > 
                <h2 > Cadastro de Reservas </h2> </center> """

        self.titulo.setText(html)

        self.setWindowTitle("Cadastro de Reservas")

    def add_record(self):

        if self.quarto_numero.currentText() == "":
            QMessageBox.warning(self, "Quarto Indesponível", "Nenhum quarto Desponível do momento")
            return False

        if self.nome_hospede.currentText() == "":
            QMessageBox.warning(self, "Sem Hóspedes", "Cadastre Hóspedes Primeiro")
            return False

        created_by = self.parent().user
        modified_by = self.parent().user

        created = QDateTime.currentDateTime().toString("yyyy-MM-dd H:mm:ss")
        modified = created

        code = self.codigo
        entrada = self.data_entrada.dateTime().toString("yyyy-MM-dd H:mm:ss")
        saida = self.data_saida.dateTime().toString("yyyy-MM-dd H:mm:ss")
        cliente = self.get_cod_cliente(self.nome_hospede.currentText())
        quarto = self.quarto_numero.currentText()
        obs = self.obs.toPlainText()
        estado = 1
        hospede = ""
        voucher = self.vouncher.text()
        pagamento = self.forma_pagamento.currentText()
        moeda = self.moeda.text()
        codfacturacao = self.codfacturacao

        if self.existe(code) is True:

            sql = """UPDATE reservas set cod="{cod}", data_entrada="{entrada}", data_saida="{saida}", 
            cod_cliente="{cliente}", cod_quarto={quarto}, obs="{obs}", modified="{modified}", 
            modified_by="{modified_by}", hospede="{hospede}", voucher="{voucher}",
            pagamento="{pagamento}", moeda="{moeda}", codfacturacao="{codfacturacao}" WHERE cod="{cod}"
            """.format(cod=code, entrada=entrada, saida=saida, cliente=cliente, quarto=quarto, obs=obs
                      ,modified=modified, modified_by=modified_by, hospede=hospede, voucher=voucher,
                       pagamento=pagamento, moeda=moeda, codfacturacao=codfacturacao)
        else:
            values = """ "{entrada}", "{saida}", "{cliente}", {quarto}, "{obs}", 
            "{created}", "{modified}", "{modified_by}", "{created_by}", {estado}, 
            "{hospede}", "{voucher}", "{pagamento}", "{moeda}", "{codfacturacao}"
            """.format(entrada=entrada, saida=saida, cliente=cliente,
                       quarto=quarto, obs=obs, created=created, modified=modified,
                       modified_by=modified_by, created_by=created_by, estado=estado,
                       hospede=hospede, voucher=voucher,
                       pagamento=pagamento, moeda=moeda, codfacturacao=codfacturacao)

            sql = """INSERT INTO reservas (data_entrada, data_saida, cod_cliente, cod_quarto, 
            obs, created, modified, modified_by, created_by, estado, 
            hospede, voucher, pagamento, moeda, codfacturacao) values({value})""".format(value=values)

        print(sql)
        try:
            self.cur.execute(sql)
            self.conn.commit()
            print("Fim da Reserva...")
            QMessageBox.information(self, 'Sucesso', 'Reserva criada com sucesso')
            cliente = self.detalhes_do_cliente(self.get_cod_cliente(self.nome_hospede.currentText()))
            self.impreme_reserva(self.get_cod_reserva(), cliente)
            self.close()
        except Exception as e:
            QMessageBox.warning(self, "Erro", "Reserva não foi criada.\n{}.".format(e))

    def get_cod_reserva(self):
        sql = "SELECT MAX(cod) from reservas"
        self.cur.execute(sql)
        data = self.cur.fetchall()
        if len(data) == 0:
            return 1

        return data[0][0]

    def impreme_reserva(self, codreserva, cliente):
        sql = """SELECT * from reservas WHERE cod={} """.format(codreserva)
        print(sql)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        html = self.cabecalho()

        if len(data) > 0:
            for item in data:
                html += "<p align='left'>Exmo Sr(a).:</p>"
                html += "<p align='left'><b>{} {}</b></p>".format(cliente[1], cliente[2])
                html += "<p align='left'>Género: <b>{}</b></p>".format(cliente[4])
                html += "<p align='left'><b>{}: {}</b>, validade: <b>{}</b></p>".format(cliente[9], cliente[10],
                                                                                        cliente[11])
                html += "<p align='left'>Nacionalidade:<b>{}</b></p>".format(cliente[12])
                html += "<p align='left'>Contactos:<b>{}</b></p>".format(cliente[7])
                html += "<p align='left'>Emergência:<b>{}</b></p>".format(cliente[8])

                html += "<br>"
                html += "<p align='left'>Detalhes da Reserva</p>"
                html += "<hr>"
                html += "<p align='left'>Data de Entrada: <b>{}</b></p>".format(item[1])
                html += "<p align='left'>Data de Saída: <b>{}</b></p>".format(item[2])
                html += "<p align='left'>Quarto: <b>{}</b></p>".format(item[4])
                html += "<hr>"
                html += "<p align='left'>Atendido por: <b>{}</b></p>".format(item[11])

        document = QTextDocument()

        document.setHtml(html)

        dlg = QPrintPreviewDialog(self)
        dlg.paintRequested.connect(document.print_)
        dlg.showMaximized()
        dlg.exec_()

    def existe(self, codigo):
        sql = """SELECT cod from reservas WHERE cod = "{codigo}" """.format(codigo=str(codigo))

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            self.codigo = codigo
            return False
        else:
            codigo = int(data[0][0])
            self.codigo = codigo
            return True
