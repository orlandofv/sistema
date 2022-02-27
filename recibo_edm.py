import sys

from PyQt5.QtPrintSupport import QPrintDialog, QPrinter, QPrintPreviewDialog
from PyQt5.QtGui import QTextDocument
from PyQt5.QtWidgets import QApplication, QDialog, QPushButton, QVBoxLayout, QLineEdit, \
    QLabel, QFormLayout, QComboBox, QDoubleSpinBox, QHBoxLayout, QWidget, QSizePolicy, QTabWidget, QStackedWidget
from PyQt5.QtCore import QSizeF

TIPOS_DE_PAGAMENTO = ["Dinheiro", "Cheque", "POS", "Transferencia"]


class Factura(QDialog):

    html = ""

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.ui()

    def ui(self):

        self.setWindowTitle("Mola Semanal")

        self.data = QLineEdit()
        self.nome = QLineEdit()
        self.apelido = QLineEdit()
        self.conta = QLineEdit()
        self.referencia = QLineEdit()
        self.nuit = QLineEdit()
        self.tarifa = QLineEdit()
        self.endereco = QLineEdit()
        self.contador = QLineEdit()
        self.pagamento = QComboBox()
        self.pagamento.addItems(TIPOS_DE_PAGAMENTO)
        self.energia = QDoubleSpinBox()
        self.energia.setRange(0, 999999999)
        self.iva = QDoubleSpinBox()
        self.iva.setRange(0, 999999999)
        self.divida = QDoubleSpinBox()
        self.divida.setRange(0, 999999999)
        self.radio = QDoubleSpinBox()
        self.radio.setRange(0, 999999999)
        self.lixo = QDoubleSpinBox()
        self.lixo.setRange(0, 999999999)
        self.total = QDoubleSpinBox()
        self.total.setRange(0, 999999999)
        self.kw = QDoubleSpinBox()
        self.kw.setRange(0, 999999999)
        self.recarga1 = QLineEdit()
        self.recarga2 = QLineEdit()
        self.recibo = QLineEdit()
        self.operador = QLineEdit()
        self.identidade_estacao = QLineEdit()
        self.nome_estacao = QLineEdit()
        self.indice_tarifa = QLineEdit()
        # Fim da EDM

        form = QFormLayout()
        form2 = QFormLayout()

        form.addRow(QLabel("Data"), self.data)
        form.addRow(QLabel("Nome"), self.nome)
        form.addRow(QLabel("Apelido"), self.apelido)
        form.addRow(QLabel("Número de Conta"), self.conta)
        form.addRow(QLabel("Ref. do Local"), self.referencia)
        form.addRow(QLabel("NUIT do Cliente"), self.nuit)
        form.addRow(QLabel("Tarifa do Cliente"), self.tarifa)
        form.addRow(QLabel("Detalhes do Endereço"), self.endereco)
        form.addRow(QLabel("Contador"), self.contador)
        form.addRow(QLabel("Tipo de Pagamento"), self.pagamento)
        form_widget = QWidget()
        form_widget.setLayout(form)

        form2.addRow(QLabel("Valor de energia"), self.energia)
        form2.addRow(QLabel("IVA"), self.iva)
        form2.addRow(QLabel("Dívida"), self.divida)
        form2.addRow(QLabel("Taxa de Rádio"), self.radio)
        form2.addRow(QLabel("Taxa de Lixo"), self.lixo)
        form2.addRow(QLabel("Total Pago"), self.total)
        form2.addRow(QLabel("Unidades de Energia"), self.kw)
        form2.addRow(QLabel("Código de Recarga (3 pares)"), self.recarga1)
        form2.addRow(QLabel("Código de Recarga (2 Pares)"), self.recarga2)
        form2.addRow(QLabel("Número de Recibo"), self.recibo)
        form2.addRow(QLabel("Nome do Operador"), self.operador)
        form2.addRow(QLabel("Identidade da Estação"), self.identidade_estacao)
        form2.addRow(QLabel("Nome da Estação"), self.nome_estacao)
        form2.addRow(QLabel("GA/Indice da Tarifa"), self.indice_tarifa)

        form2_widget = QWidget()
        form2_widget.setLayout(form2)

        self.stack = QStackedWidget()
        self.stack.addWidget(form_widget)
        self.stack.addWidget(form2_widget)

        self.stack_btn = QPushButton("+")
        self.stack_btn.setMaximumSize(40, 40)
        self.stack_btn.clicked.connect(self.mudar_stack)

        stack_lay = QVBoxLayout()
        stack_lay.addWidget(self.stack)
        stack_lay.addWidget(self.stack_btn)

        # DSTV

        self.data_ds = QLineEdit()
        self.vendedor = QLineEdit()
        self.numero = QLineEdit()
        self.trans = QLineEdit()
        self.periodo = QLineEdit()
        self.numero_cliente = QLineEdit()
        self.valor_pago = QDoubleSpinBox()
        self.valor_pago.setRange(0, 999999999999)
        self.user = QLineEdit()
        self.estacao = QLineEdit()

        ds_form = QFormLayout()

        ds_form.addRow(QLabel("Data:"), self.data_ds)
        ds_form.addRow(QLabel("Vendedor:"), self.vendedor)
        ds_form.addRow(QLabel("Numero:"), self.numero)
        ds_form.addRow(QLabel("Trans:"), self.trans)
        ds_form.addRow(QLabel("Periodo:"), self.periodo)
        ds_form.addRow(QLabel("Numero Cliente:"), self.numero_cliente)
        ds_form.addRow(QLabel("Valor_pago"), self.valor_pago)
        ds_form.addRow(QLabel("Usuário"), self.user )
        ds_form.addRow(QLabel("Estação"), self.estacao)

        edm_widget = QWidget()
        edm_widget.setLayout(stack_lay)

        ds_widget = QWidget()
        ds_widget.setLayout(ds_form)

        tabulador = QTabWidget()
        tabulador.addTab(edm_widget, "ED")
        tabulador.addTab(ds_widget, "DS")

        print_btn = QPushButton("Imprimir")
        print_btn.clicked.connect(self.final_print)
        print_dstv_btn = QPushButton("Imprimir ds")
        print_dstv_btn.clicked.connect(self.dstv_print)

        stretch = QWidget()
        stretch.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(self.close)

        btn_box = QHBoxLayout()
        btn_box.addWidget(print_btn)
        btn_box.addWidget(print_dstv_btn)
        btn_box.addWidget(stretch)
        btn_box.addWidget(close_btn)

        vl = QVBoxLayout()
        vl.addWidget(tabulador)
        vl.addLayout(btn_box)
        self.setLayout(vl)

    def mudar_stack(self):
        if self.stack.currentIndex() == 1:
            self.stack.setCurrentIndex(0)
            self.stack_btn.setText("+")
        else:
            self.stack.setCurrentIndex(1)
            self.stack_btn.setText("-")

    def print(self):

        html = """<!DOCTYPE html>
                    <html lang="en">
                    <head>
                    <meta charset="UTF-8">
                    <title>Title</title>

                    <style type="text">
                        table, th, td {
                        border: 0px solid red;
                        border-collapse: collapse;
                        }
                    </style>

                    </head>
            <body>"""

        # Detalhes EDM
        html += "<center style='font-weight: bold;'> EDM EP </center>"
        html += "<center style='font-weight: bold;'> MAPUTO CIDADE </center>"
        html += "<center> EDM NUIT: 600000063 </center>"

        html += "<p><center> Av. Agostinho Neto no. 70 </center></p>"

        html += "<p style='font-weight: bold;'><center> Talão de Energia - VD </center></p>"

        html += "<p style='font-size: 10px;'>09 Agosto 2019 01:35 PM</p>"

        # Detalhes do Cliente
        html += "<table width=100% style='font-size: 10px;'>"
        html += "<tr>"
        html += """<td width=45% style="text-align: left;">Nome & Apelido:</td>"""
        html += """<td width=55% style="text-align: left;">DANTEQUELE JAIME A.</td>"""
        html += "</tr>"
        html += "<tr>"
        html += """<td>PANGUENE</td>"""
        html += """<td></td>"""
        html += "</tr>"
        html += "<tr>"
        html += "<td>Número de Conta:</td>"
        html += "<td>202321914 01</td>"
        html += "</tr>"
        html += "<tr>"
        html += "<td>Número de Referência do Local:</td>"
        html += "<td valign='bottom'>202321914 01</td>"
        html += "</tr>"
        html += "<tr>"
        html += "<td>NUIT do Cliente:</td>"
        html += "<td></td>"
        html += "</tr>"
        html += "<tr>"
        html += "<td>Tarifa do Cliente:</td>"
        html += "<td>EDM DOMESTICONEW</td>"
        html += "</tr>"
        html += "<tr>"
        html += "<td>Detalhes do Endereço:</td>"
        html += "<td>S/N ALBAZINE   ALBAZINE 4390</td>"
        html += "</tr>"
        html += "</table>"

        html += "</br>"

        # Contador e Tipo de Pagamento
        html += "<table width=100% style='font-size: 10px;'>"
        html += "<tr>"
        html += "<td width=45% style='text-align: left'>Contador:</td>"
        html += "<td width=55% style='text-align: left'>04241057258</td>"
        html += "</tr>"
        html += "<tr>"
        html += "<td width=45% style='text-align: left'>Tipo de Pagamento:</td>"
        html += "<td width=55% style='text-align: left'>Dinheiro</td>"
        html += "</tr>"
        html += "</table>"
        html += "<br/>"

        # Detalhes de Valores
        html += "<table width=100% style='font-size: 10px;'>"
        html += "<tr>"
        html += """<th width = 45%" style="text-align: left;" >Descrição</th>"""
        html += """<th width = 55% style="text-align: left;">Valor (MT)</th>"""
        html += "</tr>"
        html += "<tr>"
        html += "<td>Valor de Energia</td>"
        html += "<td>143 00M T</td>"
        html += "</tr>"
        html += "<tr>"
        html += "<td>IVA</td>"
        html += "<td>13 63 MT</td>"
        html += "</tr>"
        html += "<tr>"
        html += "<td>Total da Divida</td>"
        html += "<td>0 00 MT</td>"
        html += "</tr>"
        html += "<tr>"
        html += "<td>Taxa de Radio</td>"
        html += "<td>12 00 MT</td>"
        html += "</tr>"
        html += "<tr>"
        html += "<td>Taxa de Lixo</td>"
        html += "<td>45 00 MT</td>"
        html += "</tr>"
        html += "</table>"

        html += "<hr/>"

        # Totais
        html += "<table width=100% style='font-size: 10px;'>"
        html += "<tr>"
        html += "<td width = 45% >Total Pago</td>"
        html += "<td width = 55% >200.00 MT</td>"
        html += "</tr>"
        html += "</table>"
        html += "<center style='text-align: left; font-size: 10px;'>Unidades de Energia:17.0 kWh</center>"
        html += "<hr/>"

        # Dados da Recarga
        html += "<center> Código da Recarga </center>"
        html += """<center style="font-size: 18px;"> 4564 4564 4564 </center>"""
        html += """<center style="font-size: 18px;"> 4564 4564 </center>"""

        html += "<hr/>"

        # Dados do Sistema
        html += "<table width=100% style='font-size: 10px;'>"
        html += "<tr>"
        html += "<td width=45%>Número do Recibo:</td>"
        html += "<td width=55%>EDMDDMPDB3626546</td>"
        html += "</tr>"
        html += "<tr>"
        html += "<td>Nome do Operador:</td>"
        html += "<td>NEJANUARIO</td>"
        html += "</tr>"
        html += "<tr>"
        html += "<td>Identidade da estação de vendas:</td>"
        html += "<td></td>"
        html += "</tr>"
        html += "<tr>"
        html += "<td>Nome da estação de vendas:</td>"
        html += "<td>DDM 3E</td>"
        html += "</tr>"
        html += "<tr>"
        html += "<td>GA/Indice de Tarifa:</td>"
        html += "<td>60059771</td>"
        html += "</tr>"
        html += "</table>"

        # Rodape
        html += "<p>Processado por computador 3E</p>"
        html += "<p><center>Central de Atendimento de Maputo</center></p>"
        html += "<center>800145145/821455/841455</center>"
        html += """</body>
        </html>"""

        printer = QPrinter()
        #

        # printer.setFullPage(True)
        # printer.setPaperSource(printer.Auto)

        printer.setResolution(72)
        printer.setPaperSize(QSizeF(self.parent().papel_1,  3276), printer.Millimeter)
        printer.setPageMargins(0, 0, 0, 0, printer.Millimeter)
        #
        document = QTextDocument()
        document.setHtml(html)
        document.setPageSize(QSizeF(printer.pageRect().size()))

        dialog = QPrintDialog()
        document.print_(printer)
        dialog.accept()

    def dstv_print(self):

        html = """<!DOCTYPE html>
                    <html lang="en">
                    <head>
                    <meta charset="UTF-8">
                    <title>Title</title>

                    <style type="text">
                        table, th, td {
                        border: 0px solid red;
                        border-collapse: collapse;
                        }
                    </style>

                    </head>
            <body>"""

        html += "<center style='font-weight: bold; font-size: 12px;'>PAGAMENTO DSTV</center>"
        html += "<br/>"

        # Detalhes do Cliente
        html += "<table width=100% style='font-size: 10px;'>"
        html += "<tr>"
        html += """<td width=40% style="text-align: left;">Data:</td>"""
        html += """<td width=60% style="text-align: left;">{}</td>""".format(self.data_ds.text())
        html += "</tr>"
        html += "<tr>"
        html += """<td>Vendendor:</td>"""
        html += """<td>{}</td>""".format(self.vendedor.text())
        html += "</tr>"
        html += "<tr>"
        html += "<td>Número:</td>"
        html += "<td>{}</td>".format(self.numero.text())
        html += "</tr>"
        html += "<tr>"
        html += "<td>Trans:</td>"
        html += "<td>{}</td>".format(self.trans.text())
        html += "</tr>"
        html += "<tr>"
        html += "<td>Periodo:</td>"
        html += "<td>{}</td>".format(self.periodo.text())
        html += "</tr>"

        html += "<tr>"
        html += "<td text-decoration: underline;></td>"
        html += "<td></td>"
        html += "</tr>"

        html += "<tr>"
        html += "<td style='text-decoration: underline;'>Numero Cliente</td>"
        html += "<td></td>"
        html += "</tr>"
        html += "<tr>"
        html += "<td>{}</td>".format(self.numero_cliente.text())
        html += "<td></td>"
        html += "</tr>"
        html += "</table>"

        html += "<br/>"

        html += "<p style='font-weight: bold; font-size: 12px;'>VALOR PAGO: {}</p>".format(self.valor_pago.value())

        html += "<center style='font-size: 10px; text-decoration: underline; text-align: left;'> Nome Operador </center>"
        html += "<center style='font-size: 10px; text-align: left;'> {} </center>".format(self.user.text())

        html += "<center style='font-size: 10px; text-decoration: underline; text-align: left;'> Nome Loja e Codigo :</center>"
        html += "<center style='font-size: 10px; text-align: left;'> {} </center>".format(self.estacao.text())

        html += "<br/>"

        html += "<center style='font-size: 10px; text-align: left;'> Para Assistencia Contacte </center>"
        html += "<center style='font-size: 10px; text-align: left;'> www.dstv.com </center>"
        html += "<center style='font-size: 10px; text-align: left;'> Tel : 843 788 </center>"
        html += "<center style='font-size: 10px; text-align: left;'> Tel : 823 788 </center>"
        html += "<center style='font-size: 10px; text-align: left;'> mozcallcenter@mz.multichioce.com </center>"

        printer = QPrinter()
        #

        # printer.setFullPage(True)
        # printer.setPaperSource(printer.Auto)

        printer.setResolution(72)
        printer.setPaperSize(QSizeF(self.parent().papel_1,  3276), printer.Millimeter)
        printer.setPageMargins(0, 0, 0, 0, printer.Millimeter)
        #
        document = QTextDocument()
        document.setHtml(html)
        document.setPageSize(QSizeF(printer.pageRect().size()))

        dialog = QPrintDialog()
        document.print_(printer)
        dialog.accept()

    def dstv_print2(self):

        html = """<!DOCTYPE html>
                    <html lang="en">
                    <head>
                    <meta charset="UTF-8">
                    <title>Title</title>

                    <style type="text">
                        table, th, td {
                        border: 0px solid red;
                        border-collapse: collapse;
                        }
                    </style>

                    </head>
            <body>"""

        html += "<center style='font-weight: bold; font-size: 12px;'>PAGAMENTO DSTV</center>"
        html += "<br/>"

        # Detalhes do Cliente
        html += "<table width=100% style='font-size: 10px;'>"
        html += "<tr>"
        html += """<td width=40% style="text-align: left;">Data:</td>"""
        html += """<td width=60% style="text-align: left;">2019-09-13 12:45:13</td>"""
        html += "</tr>"
        html += "<tr>"
        html += """<td>Vendendor:</td>"""
        html += """<td>TOPUPDStv</td>"""
        html += "</tr>"
        html += "<tr>"
        html += "<td>Número:</td>"
        html += "<td>7390767</td>"
        html += "</tr>"
        html += "<tr>"
        html += "<td>Trans:</td>"
        html += "<td>113685422</td>"
        html += "</tr>"
        html += "<tr>"
        html += "<td>Periodo:</td>"
        html += "<td>1</td>"
        html += "</tr>"

        html += "<tr>"
        html += "<td text-decoration: underline;></td>"
        html += "<td></td>"
        html += "</tr>"

        html += "<tr>"
        html += "<td style='text-decoration: underline;'>Numero Cliente</td>"
        html += "<td></td>"
        html += "</tr>"
        html += "<tr>"
        html += "<td>42437595</td>"
        html += "<td></td>"
        html += "</tr>"
        html += "</table>"

        html += "<br/>"

        html += "<p style='font-weight: bold; font-size: 12px;'>VALOR PAGO: 17000.00</p>"

        html += "<center style='font-size: 10px; text-decoration: underline; text-align: left;'> Nome Operador </center>"
        html += "<center style='font-size: 10px; text-align: left;'> USER-USER2 </center>"

        html += "<center style='font-size: 10px; text-decoration: underline; text-align: left;'> Nome Loja e Codigo :</center>"
        html += "<center style='font-size: 10px; text-align: left;'> Estacao de Servicos Mafangue MC0168 </center>"

        html += "<br/>"

        html += "<center style='font-size: 10px; text-align: left;'> Para Assistencia Contacte </center>"
        html += "<center style='font-size: 10px; text-align: left;'> www.dstv.com </center>"
        html += "<center style='font-size: 10px; text-align: left;'> Tel : 843 788 </center>"
        html += "<center style='font-size: 10px; text-align: left;'> Tel : 823 788 </center>"
        html += "<center style='font-size: 10px; text-align: left;'> mozcallcenter@mz.multichioce.com </center>"

        printer = QPrinter()
        #

        # printer.setFullPage(True)
        # printer.setPaperSource(printer.Auto)

        printer.setResolution(72)
        printer.setPaperSize(QSizeF(self.parent().papel_1,  3276), printer.Millimeter)
        printer.setPageMargins(0, 0, 0, 0, printer.Millimeter)
        #
        document = QTextDocument()
        document.setHtml(html)
        document.setPageSize(QSizeF(printer.pageRect().size()))

        dialog = QPrintDialog()
        document.print_(printer)
        dialog.accept()


    def final_print(self):

        html = """<!DOCTYPE html>
                    <html lang="en">
                    <head>
                    <meta charset="UTF-8">
                    <title>Title</title>

                    <style type="text">
                        table, th, td {
                        border: 0px solid red;
                        border-collapse: collapse;
                        }
                    </style>

                    </head>
            <body>"""

        # Detalhes EDM
        html += "<center style='font-weight: bold;'> EDM EP </center>"
        html += "<center style='font-weight: bold;'> MAPUTO CIDADE </center>"
        html += "<center> EDM NUIT: 600000063 </center>"

        html += "<p><center> Av. Agostinho Neto no. 70 </center></p>"

        html += "<p style='font-weight: bold;'><center> Talão de Energia - VD </center></p>"

        html += "<p style='font-size: 10px;'>{}</p>".format(self.data.text())

        # Detalhes do Cliente
        html += "<table width=100% style='font-size: 10px;'>"
        html += "<tr>"
        html += """<td width=45% style="text-align: left;">Nome & Apelido:</td>"""
        html += """<td width=55% style="text-align: left;">{}</td>""".format(self.nome.text())
        html += "</tr>"
        html += "<tr>"
        html += """<td>{}</td>""".format(self.apelido.text())
        html += """<td></td>"""
        html += "</tr>"
        html += "<tr>"
        html += "<td>Número de Conta:</td>"
        html += "<td>{}</td>".format(self.conta.text())
        html += "</tr>"
        html += "<tr>"
        html += "<td>Número de Referência do Local:</td>"
        html += "<td valign='bottom'>{}</td>".format(self.referencia.text())
        html += "</tr>"
        html += "<tr>"
        html += "<td>NUIT do Cliente:</td>"
        html += "<td>{}</td>".format(self.nuit.text())
        html += "</tr>"
        html += "<tr>"
        html += "<td>Tarifa do Cliente:</td>"
        html += "<td>{}</td>".format(self.tarifa.text())
        html += "</tr>"
        html += "<tr>"
        html += "<td>Detalhes do Endereço:</td>"
        html += "<td>{}</td>".format(self.endereco.text())
        html += "</tr>"
        html += "</table>"

        html += "</br>"

        # Contador e Tipo de Pagamento
        html += "<table width=100% style='font-size: 10px;'>"
        html += "<tr>"
        html += "<td width=45% style='text-align: left'>Contador:</td>"
        html += "<td width=55% style='text-align: left'>{}</td>".format(self.contador.text())
        html += "</tr>"
        html += "<tr>"
        html += "<td width=45% style='text-align: left'>Tipo de Pagamento:</td>"
        html += "<td width=55% style='text-align: left'>{}</td>".format(self.pagamento.currentText())
        html += "</tr>"
        html += "</table>"
        html += "<br/>"

        # Detalhes de Valores
        html += "<table width=100% style='font-size: 10px;'>"
        html += "<tr>"
        html += """<th width = 45%" style="text-align: left;" >Descrição</th>"""
        html += """<th width = 55% style="text-align: left;">Valor (MT)</th>"""
        html += "</tr>"
        html += "<tr>"
        html += "<td>Valor de Energia</td>"
        html += "<td>{} MT</td>".format(self.energia.value())
        html += "</tr>"
        html += "<tr>"
        html += "<td>IVA</td>"
        html += "<td>{} MT</td>".format(self.iva.value())
        html += "</tr>"
        html += "<tr>"
        html += "<td>Total da Divida</td>"
        html += "<td>{} MT</td>".format(self.divida.value())
        html += "</tr>"
        html += "<tr>"
        html += "<td>Taxa de Radio</td>"
        html += "<td>{} MT</td>".format(self.radio.value())
        html += "</tr>"
        html += "<tr>"
        html += "<td>Taxa de Lixo</td>"
        html += "<td>{} MT</td>".format(self.lixo.value())
        html += "</tr>"
        html += "</table>"

        html += "<hr/>"

        # Totais
        html += "<table width=100% style='font-size: 10px;'>"
        html += "<tr>"
        html += "<td width = 45% >Total Pago</td>"
        html += "<td width = 55% >{} MT</td>".format(self.total.value())
        html += "</tr>"
        html += "</table>"
        html += "<center style='text-align: left; font-size: 10px;'>Unidades de Energia:{} kWh</center>".format(self.kw.value())
        html += "<hr/>"

        # Dados da Recarga
        html += "<center> Código da Recarga </center>"
        html += """<center style="font-size: 18px;"> {} </center>""".format(self.recarga1.text())
        html += """<center style="font-size: 18px;"> {} </center>""".format(self.recarga2.text())

        html += "<hr/>"

        # Dados do Sistema
        html += "<table width=100% style='font-size: 10px;'>"
        html += "<tr>"
        html += "<td width=45%>Número do Recibo:</td>"
        html += "<td width=55%>{}</td>".format(self.recibo.text())
        html += "</tr>"
        html += "<tr>"
        html += "<td>Nome do Operador:</td>"
        html += "<td>{}</td>".format(self.operador.text())
        html += "</tr>"
        html += "<tr>"
        html += "<td>Identidade da estação de vendas:</td>"
        html += "<td>{}</td>".format(self.identidade_estacao.text())
        html += "</tr>"
        html += "<tr>"
        html += "<td>Nome da estação de vendas:</td>"
        html += "<td>{}</td>".format(self.nome_estacao.text())
        html += "</tr>"
        html += "<tr>"
        html += "<td>GA/Indice de Tarifa:</td>"
        html += "<td>{}</td>".format(self.indice_tarifa.text())
        html += "</tr>"
        html += "</table>"

        # Rodape
        html += "<p>Processado por computador 3E</p>"
        html += "<p><center>Central de Atendimento de Maputo</center></p>"
        html += "<center>800145145/821455/841455</center>"
        html += """</body>
        </html>"""

        printer = QPrinter()
        #

        # printer.setFullPage(True)
        # printer.setPaperSource(printer.Auto)

        printer.setResolution(72)
        printer.setPaperSize(QSizeF(self.parent().papel_1,  3276), printer.Millimeter)
        printer.setPageMargins(0, 0, 0, 0, printer.Millimeter)
        #
        document = QTextDocument()
        document.setHtml(html)
        document.setPageSize(QSizeF(printer.pageRect().size()))

        dialog = QPrintDialog()
        document.print_(printer)
        dialog.accept()


if __name__ == '__main__':

    app = QApplication(sys.argv)

    helloPythonWidget = Factura()
    helloPythonWidget.show()

    sys.exit(app.exec_())