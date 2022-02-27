import decimal
import datetime

t = datetime.datetime.now()

#CODIGO_HORA = "{}{}{}/{}".format(t.hour, t.minute, t.second, t.year)
CODIGO_HORA = t

from PyQt5.QtWidgets import QLabel, QAction, QMessageBox, QPushButton
from PyQt5.QtGui import QIcon, QTextDocument, QFont, QBrush
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtCore import QSizeF, Qt, QDateTime, QSettings

from GUI.RibbonButton import RibbonButton
from GUI.RibbonWidget import *

from vendas import Vendas
from utilities import HORA
from sortmodel import MyTableModel


class VendasRestaurante(Vendas):

    numero_da_mesa = 0

    def __init__(self, parent=None):
        super(VendasRestaurante, self).__init__(parent)

        # self.cria_tabela_contagem()

        self.imprimir_ordem = True
        self.exigir_ordem = True
        self.imprimir_items_apagados = True

        self.imprimir_ordem, self.exigir_ordem, self.imprimir_items_apagados = self.get_settings()

        self.gravardoc.setVisible(False)
        self.abrirdoc.setVisible(False)
        self.segundavia.setVisible(False)
        self.caixa.setVisible(False)
        self.trancarsistema.setVisible(False)
        self.validade.setVisible(False)
        self.recibo.setVisible(False)
        self.receitas_despesas.setEnabled(False)
        self.caixa_numero = self.parent().caixa_numero
        self.codarmazem = self.parent().codarmazem
        self.user = self.parent().user
        self.copias_pos1 = self.parent().copias_pos1
        self.copias_pos2 = self.parent().copias_pos2

        self.mesa_Label = QPushButton("mesa")

        self.mesa_Label.clicked.connect(lambda: self.mudanca_de_mesa(self.mesa_Label.text()))

        self.mesa_Label.setObjectName('mesa')

        mesa_style = """
        QPushButton {
            font-size: 36px;
            padding: 5px;    
            border: 1px solid #5e90fa;
            border-radius: 2px;
            margin: 7px;
            background-color: #5e90fa;
            color: #fff;   
        }
        
        QPushButton:hover{
            background-color: #fff;
            color: #5e90fa;
        }
        """

        self.mesa_Label.setStyleSheet(mesa_style)

        label_grid = self.home_tab.add_ribbon_pane("Mesa")
        label_grid.add_ribbon_widget(self.mesa_Label)

        self.pedidos_action = QAction(QIcon("./icons/sandes.ico"), "ORDEM", self)
        self.pedidos_action.triggered.connect(self.imprime_ordem)

        self.pedidos_feitos_action = QAction(QIcon("./icons/sandes.ico"), "ORDEM\nJá Feito", self)
        self.pedidos_feitos_action.triggered.connect(self.imprime_ordem_feito)

        cozinha = self.home_tab.add_ribbon_pane("Pedidos")
        cozinha.add_ribbon_widget(RibbonButton(self, self.pedidos_action, True))
        cozinha.add_ribbon_widget(RibbonButton(self, self.pedidos_feitos_action, True))

        self.pedidos_conta_action = QAction(QIcon("./icons/generic.ico"), "Imprimir\nResumido", self)
        self.pedidos_conta_action_detalhe = QAction(QIcon("./icons/generic.ico"), "Imprimir\nDetalhado", self)
        self.pedidos_conta_action_detalhe.triggered.connect(lambda: self.imprime_conta_mesas(1))
        self.pedidos_conta_action.triggered.connect(lambda: self.imprime_conta_mesas(0))

        self.desconto_action = QAction(QIcon("./icons/cofiguracao2.ico"), "DESCONTO", self)
        self.desconto_action.triggered.connect(self.mostrar_desconto)

        conta = self.home_tab.add_ribbon_pane("Conta")
        conta.add_ribbon_widget(RibbonButton(self, self.pedidos_conta_action, True))
        conta.add_ribbon_widget(RibbonButton(self, self.pedidos_conta_action_detalhe, True))
        conta.add_ribbon_widget(RibbonButton(self, self.desconto_action, True))

        self.accao_fechar.triggered.connect(self.close)
        self.butao_fechar.clicked.connect(self.close)

    def get_settings(self):
        settings = QSettings()
        imprimir_ordem = settings.value("MigrogestPOS/imprimir_ordem", True, bool)
        exigir_ordem = settings.value("MigrogestPOS/exigir_ordem", True, bool)
        imprimir_items_apagados = settings.value("MigrogestPOS/imprimir_items_apagados", True, bool)

        return imprimir_ordem, exigir_ordem, imprimir_items_apagados

    def mostrar_desconto(self):
        if self.admin is False:
            return

        from desconto import Desconto

        d = Desconto(self)
        d.codigogeral = self.codigogeral
        d.total_geral = self.totalgeral
        d.total_label.setText(str(self.totalgeral))

        d.setModal(True)
        d.show()

    def mudanca_de_mesa(self, mesa):
        if self.tabelavazia():
            QMessageBox.warning(self, "Sem Items", "Insira items para a Mesa {}.".format(mesa))
            return False

        from divisao_contas import Divisao
        divisao = Divisao(self, "Divisão de Conta", "./icons/generic.ico")
        divisao.mesa_1 = int(mesa)
        divisao.spin_mesa_1.setValue(int(mesa))
        divisao.setModal(True)
        divisao.show()

    def get_codfacturacao(self, codfacturacao):
        sql = """SELECT cod from cozinha WHERE codfacturacao = "{}" """.format(codfacturacao)
        print(sql)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return data[0][0]

        return ""

    def pedidos_da_cozinha(self):
        from pedidos_cozinha import Pedidos
        p = Pedidos(self, "Pedidos de Cozinha", './icons/sandes.ico')
        p.numero_da_mesa = self.numero_da_mesa
        p.user = self.user
        p.setModal(True)
        p.fill_table2()
        print("codigo: ".format(self.get_codfacturacao(self.codigogeral)))
        p.codigogeral = self.get_codfacturacao(self.codigogeral)
        p.show()

    def imprime_conta_mesas(self, tipo=1):
        sql = """SELECT ordem from facturacaodetalhe WHERE codfacturacao="{}" AND ordem=0 """.format(self.codigogeral)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if self.exigir_ordem is True:
            if len(data) > 0:
                QMessageBox.warning(self, "Crie a Ordem", "Crie a ordem antes de Imprimir a Conta")
                return False

        if tipo == 1:
            self.imprime_conta_detalhada(self.codigogeral)
        else:
            self.imprime_conta(self.codigogeral)

        return True

    def imprime_ordem(self):

        self.imprime_ordem_bar(self.codigogeral)
        self.imprime_ordem_cozinha(self.codigogeral)

        self.fill_table()

    def imprime_ordem_feito(self):
        self.imprime_ordem_bar(self.codigogeral)
        self.imprime_ordem_pedido_cozinha(self.codigogeral)

        self.fill_table()

    def imprime_conta(self, codigo):

        if self.tabelavazia() is True:
            QMessageBox.warning(self, "Sem Items", "Não pode imprimir Conta sem nenhum Item!")
            return False

        sql = """SELECT DISTINCT `codfacturacao`, `numerofactura`, `nomedocumento`, `data`, `user`, `subtotal_geral`, 
        `desconto_geral`, `taxa_geral`, `total_geral`, `extenso`, `cliente`, `endereco`, `NUIT`, `email`, `codproduto`, 
        `produto`, SUM(`quantidade`), `preco`, `desconto`, `taxa`, `subtotal`,  SUM(`total`), `ano`, `mes`, `pago`, 
        `troco`, `coddocumento`, `contactos`, `validade`, `obs`, `nome`  
        FROM factura_geral WHERE codfacturacao = '{}' GROUP BY produto""".format(codigo)

        self.cur.execute(sql)
        data = self.cur.fetchall()
        html = """
            <!DOCTYPE html>
                <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <title>Template de Recibos POS</title>
                    </head>

                    <body style="font-size:8px;">

        """

        # LOGOTIPO
        self.imprime_logotipo()

        if self.parent() is not None:
            html += "<center> {} </center>".format(self.parent().empresa)
            html += "<center> {} </center>".format(self.parent().empresa_endereco)
            if self.parent().empresa_nuit != "":
                html += "<center> NUIT: {} </center>".format(self.parent().empresa_nuit)
            html += "<center style='font-weight: bold; font-size: 10px;'> Contactos: {} </center>".format(self.parent().empresa_contactos)
        else:
            html = "<center> [Nome da Empresa] </center>"
            html += "<center> [Endereco] </center>"
            html += "<center> [NUIT] </center>"
            html += "<center> [CONTACTOS] </center>"

        html += "<br/>"
        html += "<center> CONTA A PAGAR </center>"
        html += "<hr/>"
        html += "<center> MESA: {} </center>".format(self.numero_da_mesa)
        html += "<hr/>"
        html += "<center align='left'>{}</center>".format(HORA)
        html += "<center align='left'>Usuário: {}</center>".format(data[0][4])

        html += "<center>Exmo(a) Sr.(a): {}</center>".format(data[0][10])
        html += "<center>{}</center>".format(self.label_total_items.text())
        html += "<table border='0' width = 100% style='border: thin;'>"

        html += "<tr style='border: 1px solid #000;'>"

        html += "<th width = 60%>Descrição</th>"
        html += "<th width = 10%>Qt.</th>"
        html += "<th width = 10%>Preço.</th>"
        html += "<th width = 20% align='right'>Total</th>"

        html += "</tr>"

        for cliente in data:
            if cliente[16] > 0:
                preco = cliente[21] / cliente[16]
            else:
                preco = 0

            if self.coddocumento != 'DC20185555555':
                html += """<tr style="font-size:8px;"> <td>{}</td> <td>{}</td> <td align="right">{}</td> <td align="right">{}</td> </tr>
                                   """.format(cliente[15], cliente[16], preco, cliente[21])
            else:
                html += """<tr> <td>{}</td> <td>{}</td> </tr>
                                                   """.format(cliente[15], cliente[16])

        html += "</table>"

        html += "<hr/>"

        html += "<table>"

        if self.coddocumento != 'DC20185555555':
            html += "<tr>"
            html += "<th width = 50% align='right'>TOTAL</th>"
            html += "<th width = 50% align='right'>{:20,.2f} </th>".format(cliente[8])
            html += "</tr>"

        html += "</table>"

        html += "<hr/>"
        
        html += "<center> Processado por Computador  </center>".format(self.parent().licenca)

        html += """
                    </body>
                </html>
                """
        printer = QPrinter()
        printer.setPrinterName(self.parent().pos1)

        # printer.setFullPage(True)
        # printer.setPaperSource(printer.Auto)

        printer.setResolution(72)
        printer.setPaperSize(QSizeF(self.parent().papel_1,  3276), printer.Millimeter)
        printer.setPageMargins(0, 0, 10, 0, QPrinter.Millimeter)
        document = QTextDocument()
        # # font = document.defaultFont()
        # # s = font.toString().split(",")
        # # document.setDefaultFont(QFont("{}".format(s[0]), 6))
        document.setHtml(html)
        document.setPageSize(QSizeF(printer.pageRect().size()))

        dialog = QPrintDialog()
        document.print_(printer)
        dialog.accept()

        return True
    
    def imprime_logotipo(self):
        html = ""
        if self.parent().empresa_logo:
            html += """
                      <table width = "100%">
                          <tr>
                              <td>
                               <img src = '{}'>
                              </td>
                          </tr >
                      </table>
                      """.format(self.parent().empresa_logo)

    def imprime_conta_detalhada(self, codigo):

        if self.tabelavazia() is True:
            QMessageBox.warning(self, "Sem Items", "Não pode imprimir Conta sem nenhum Item!")
            return False

        # sql = """SELECT f.*, fd.created FROM factura_geral f INNER JOIN facturacaodetalhe fd
        # ON f.codfacturacao=fd.codfacturacao WHERE f.codfacturacao = '{}' GROUP BY fd.cod""".format(codigo)
        sql = """SELECT f.nome, fd.quantidade, p.nome, fd.preco, fd.total, ft.total, c.nome, ft.created_by, fd.created,
        fd.cod
        FROM facturacaodetalhe fd
        INNER JOIN produtos p ON p.cod=fd.codproduto
        INNER JOIN familia f ON f.cod=p.codfamilia
        INNER JOIN facturacao ft ON ft.cod=fd.codfacturacao
        INNER JOIN clientes c ON c.cod=ft.codcliente
        WHERE ft.finalizado=0 AND ft.cod="{cod}" """.format(cod=codigo)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        html = """
            <!DOCTYPE html>
                <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <title>Template de Recibos POS</title>
                    </head>

                    <body style="font-size:8px;">

        """

        # LOGOTIPO
        self.imprime_logotipo()

        if self.parent() is not None:
            html += "<center> {} </center>".format(self.parent().empresa)
            html += "<center> {} </center>".format(self.parent().empresa_endereco)
            if self.parent().empresa_nuit != "":
                html += "<center> NUIT: {} </center>".format(self.parent().empresa_nuit)
            html += "<center style='font-weight: bold; font-size: 10px;'> " \
                    "Contactos: {} </center>".format(self.parent().empresa_contactos)
        else:
            html = "<center> [Nome da Empresa] </center>"
            html += "<center> [Endereco] </center>"
            html += "<center> [NUIT] </center>"
            html += "<center> [CONTACTOS] </center>"

        # html += "<center align='left'> {}: {}/{}{}</center>".format(data[0][2], data[0][1], data[0][23], data[0][22])
        html += "<br/>"
        html += "<center> CONTA A PAGAR </center>"
        html += "<hr/>"
        html += "<center> MESA: {} </center>".format(self.numero_da_mesa)
        html += "<hr/>"
        html += "<center align='left'>{}</center>".format(HORA)
        html += "<center align='left'>Usuário: {}</center>".format(self.user)

        html += "<center>Exmo(a) Sr.(a)</center>"
        html += "<center>{}</center>".format(self.label_total_items.text())
        html += "<table border='0' width = 100% style='border: thin;'>"

        html += "<tr>"

        html += "<th width = 60%>Descrição</th>"
        html += "<th width = 10%>Qt.</th>"
        html += "<th width = 10%>Preço.</th>"
        html += "<th width = 20% align='right'>HORA</th>"

        html += "</tr>"
        total = decimal.Decimal(0)

        for cliente in data:
            total +=  cliente[3] * cliente[1]
            html += """<tr style="font-size:8px;"> <td>{}</td> <td>{}</td> <td align="right">{}</td> <td align="right">{}</td> </tr>
            """.format(cliente[2], cliente[1], cliente[3],
                       QDateTime.fromString(str(cliente[8]), "yyyy-MM-dd HH:mm:ss").toString("HH:mm:ss"))

        html += "</table>"

        html += "<hr/>"

        html += "<table>"

        if self.coddocumento != 'DC20185555555':
            html += "<tr>"
            html += "<th width = 50% align='right'>TOTAL</th>"
            html += "<th width = 50% align='right'>{:20,.2f} </th>".format(total)
            html += "</tr>"

        html += "</table>"

        html += "<hr/>"
        
        html += "<center> Processado por Computador  </center>".format(self.parent().licenca)

        html += """
                    </body>
                </html>
                """

        printer = QPrinter()
        printer.setPrinterName(self.parent().pos1)

        # printer.setFullPage(True)
        # printer.setPaperSource(printer.Auto)

        printer.setResolution(72)
        printer.setPaperSize(QSizeF(self.parent().papel_1,  3276), printer.Millimeter)
        printer.setPageMargins(0, 0, 10, 0, QPrinter.Millimeter)
        document = QTextDocument()
        # # font = document.defaultFont()
        # # s = font.toString().split(",")
        # # document.setDefaultFont(QFont("{}".format(s[0]), 6))
        document.setHtml(html)
        document.setPageSize(QSizeF(printer.pageRect().size()))

        dialog = QPrintDialog()
        document.print_(printer)
        dialog.accept()

        return True

    def actualiza_cozinha(self, codfacturacao):
        sql = """UPDATE facturacaodetalhe 
        SET ordem=1 WHERE ordem=0 AND cod="{cod}"
        """.format(cod=codfacturacao)

        print(sql)
        self.cur.execute(sql)
        self.conn.commit()

    def cria_tabela_contagem(self):

        sql = """
        CREATE TABLE IF NOT EXISTS contagem (
            cod INT AUTO_INCREMENT NOT NULL PRIMARY KEY
        )ENGINE=InnoDB;
        """

        try:
            self.cur.execute(sql)
            for x in range(1, 51):
                sql2 = """ALTER TABLE contagem ADD COLUMN contagem{} INTEGER DEFAULT 1""".format(x)
                self.cur.execute(sql2)

            sql3 = """ALTER TABLE contagem ADD COLUMN codfacturacao VARCHAR(255)"""
            self.cur.execute(sql3)
            self.conn.commit()
        except Exception as e:
            print(e)

    def incrementa_pedidos(self):
        # Cria a tabela contagem caso nao exista

        sql = """SELECT contagem1 from contagem WHERE codfacturacao="{}" """.format(self.caixa_numero)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        i = 0

        if len(data) > 0:
            print("Contagem: ", data[0][0])
            if data[0][0] == 0:
                i = 1
            else:
                i += data[0][0]
        else:
            i = 1
            sql = """UPDATE contagem set codfacturacao="{}", contagem1=1""".format(self.caixa_numero)
            self.cur.execute(sql)
            self.conn.commit()
        return i

    def actualiza_icremento(self):

        sql = """UPDATE contagem SET contagem1=contagem1+1"""

        print(sql)
        self.cur.execute(sql)
        self.conn.commit()

    def imprime_ordem_pedido_cozinha(self, codigo):

        if self.tabelavazia() is True:
            QMessageBox.warning(self, "Sem Items", "Não pode imprimir Conta sem nenhum Item!")
            return False

        sql = """SELECT f.nome, fd.quantidade, p.nome, fd.preco, fd.total, ft.total, c.nome, ft.created_by, 
        fd.created, fd.cod FROM facturacaodetalhe fd
        INNER JOIN produtos p ON p.cod=fd.codproduto
        INNER JOIN familia f ON f.cod=p.codfamilia
        INNER JOIN facturacao ft ON ft.cod=fd.codfacturacao
        INNER JOIN clientes c ON c.cod=ft.codcliente
        WHERE (f.nome LIKE "%comida%" OR f.nome LIKE "%cozinha%") AND ft.finalizado=0 AND ft.cod="{cod}" AND fd.ordem=0
		ORDER BY f.nome""".format(cod=codigo)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            return False

        for x in data:
            self.actualiza_cozinha(x[9])

        if self.imprimir_ordem is False:
            return True

        html = """
            <!DOCTYPE html>
                <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <title>Template de Recibos POS</title>
                    </head>

                    <body style="font-size:8px;">

        """
        html += "<br/>"
        html += "<center style='font-size: 14px'> NOTA: NAO PREPARAR </center>"
        html += "<center>***</center>"
        html += "<center> PEDIDO DA COZINHA </center>"
        html += "<hr/>"
        html += "<center> MESA: {} </center>".format(self.numero_da_mesa)
        html += "<hr/>"
        html += "<center align='left'>{}</center>".format(HORA)
        html += "<center align='left'>Usuário: {}</center>".format(data[0][7])

        html += "<center>Exmo(a) Sr.(a): {}</center>".format(data[0][6])
        html += "<center>{}</center>".format(self.label_total_items.text())
        html += "<table border='0' width = 100% style='border: thin;'>"

        html += "<tr>"
        html += "<th width = 70%>Descrição</th>"
        html += "<th width = 10%>Qt.</th>"
        html += "<th width = 20%>Hora</th>"
        html += "</tr>"

        total = 0

        for cliente in data:
            if cliente[3] > 0:
                preco = cliente[4] / cliente[3]
            else:
                preco = 0

            total += cliente[4]
            html += """<tr> <td>{}</td> 
            <td align="right">{}</td> <td align="right">{}</td> </tr>
                               """.format(cliente[2], cliente[1],
                                          QDateTime.fromString(str(cliente[8]),
                                                               "yyyy-MM-dd HH:mm:ss").toString("HH:mm:ss"))

        html += "</table>"
        html += "<hr/>"
        html += "<center> Processado por Computador  </center>".format(self.parent().licenca)
        html += "<center style='font-size: 18px'>{}</center>".format(self.incrementa_pedidos())

        html += """
                </body>
            </html>
            """

        self.actualiza_icremento()

        printer = QPrinter()
        printer.setPrinterName(self.parent().pos2)

        # printer.setFullPage(True)
        # printer.setPaperSource(printer.Auto)

        printer.setResolution(72)
        printer.setPaperSize(QSizeF(self.parent().papel_2,  3276), printer.Millimeter)
        printer.setPageMargins(0, 0, 10, 0, QPrinter.Millimeter)
        document = QTextDocument()
        # font = document.defaultFont()
        # s = font.toString().split(",")
        # document.setDefaultFont(QFont("{}".format(s[0]), 6))
        document.setHtml(html)
        document.setPageSize(QSizeF(printer.pageRect().size()))

        dialog = QPrintDialog()
        document.print_(printer)
        dialog.accept()

        return True

    def imprime_ordem_cozinha(self, codigo):

        if self.tabelavazia() is True:
            QMessageBox.warning(self, "Sem Items", "Não pode imprimir Conta sem nenhum Item!")
            return False

        sql = """SELECT f.nome, fd.quantidade, p.nome, fd.preco, fd.total, ft.total, c.nome, ft.created_by, 
        fd.created, fd.cod FROM facturacaodetalhe fd
        INNER JOIN produtos p ON p.cod=fd.codproduto
        INNER JOIN familia f ON f.cod=p.codfamilia
        INNER JOIN facturacao ft ON ft.cod=fd.codfacturacao
        INNER JOIN clientes c ON c.cod=ft.codcliente
        WHERE (f.nome LIKE "%comida%" OR f.nome LIKE "%cozinha%") AND ft.finalizado=0 AND ft.cod="{cod}" AND fd.ordem=0
        ORDER BY f.nome""".format(cod=codigo)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            return False

        for x in data:
            self.actualiza_cozinha(x[9])

        if self.imprimir_ordem is False:
            return True

        html = """
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Template de Recibos POS</title>
            </head>

            <body style="font-size:8px;">
        """

        html += "<br/>"
        html += "<center> PEDIDO DA COZINHA </center>"
        html += "<hr/>"
        html += "<center> MESA: {} </center>".format(self.numero_da_mesa)
        html += "<hr/>"
        html += "<center align='left'>{}</center>".format(HORA)
        html += "<center align='left'>Usuário: {}</center>".format(data[0][7])

        html += "<center>Exmo(a) Sr.(a): {}</center>".format(data[0][6])
        html += "<center>{}</center>".format(self.label_total_items.text())

        html += "<table border='0' width = 100% style='border: thin;'>"
        html += "<tr>"
        html += "<th width = 70%>Descrição</th>"
        html += "<th width = 10%>Qt.</th>"
        html += "<th width = 20%>Hora</th>"

        html += "</tr>"

        total = 0

        for cliente in data:
            if cliente[3] > 0:
                preco = cliente[4] / cliente[3]
            else:
                preco = 0

            total += cliente[4]

            html += """<tr> <td>{}</td> <td align="right">{}</td> <td align="right">{}</td> </tr>
                               """.format(cliente[2], cliente[1],
                                          QDateTime.fromString(str(cliente[8]), "yyyy-MM-dd HH:mm:ss").toString(
                                              "HH:mm:ss"))
        html += "</table>"
        html += "<hr/>"
        
        html += "<center> Processado por Computador  </center>".format(self.parent().licenca)
        html += "<center style='font-size: 18px'>{}</center>".format(self.incrementa_pedidos())

        html += """
            </body>
        </html>
        """

        self.actualiza_icremento()

        printer = QPrinter()
        printer.setPrinterName(self.parent().pos2)

        # printer.setFullPage(True)
        # printer.setPaperSource(printer.Auto)

        printer.setResolution(72)
        printer.setPaperSize(QSizeF(self.parent().papel_2,  3276), printer.Millimeter)
        printer.setPageMargins(0, 0, 10, 0, QPrinter.Millimeter)
        document = QTextDocument()
        # font = document.defaultFont()
        # s = font.toString().split(",")
        # document.setDefaultFont(QFont("{}".format(s[0]), 6))
        document.setHtml(html)
        document.setPageSize(QSizeF(printer.pageRect().size()))

        dialog = QPrintDialog()
        document.print_(printer)
        dialog.accept()

        return True

    def imprime_ordem_bar(self, codigo):

        if self.tabelavazia() is True:
            QMessageBox.warning(self, "Sem Items", "Não pode imprimir Conta sem nenhum Item!")
            return False

        sql = """SELECT f.nome, fd.quantidade, p.nome, fd.preco, fd.total, ft.total, c.nome, ft.created_by, fd.created,
                fd.cod
                FROM facturacaodetalhe fd
                INNER JOIN produtos p ON p.cod=fd.codproduto
                INNER JOIN familia f ON f.cod=p.codfamilia
                INNER JOIN facturacao ft ON ft.cod=fd.codfacturacao
                INNER JOIN clientes c ON c.cod=ft.codcliente
                WHERE NOT (f.nome LIKE "%comida%" OR f.nome LIKE "%cozinha%") AND ft.finalizado=0 AND ft.cod="{cod}" AND fd.ordem=0
        		ORDER BY f.nome""".format(cod=codigo)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            return False

        for x in data:
            print(x)
            self.actualiza_cozinha(x[9])

        if self.imprimir_ordem is False:
            return True

        html = """
            <!DOCTYPE html>
                <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <title>Template de Recibos POS</title>
                    </head>

                    <body style="font-size:8px;">

        """

        html += "<br/>"
        html += "<center> PEDIDO DO BAR </center>"
        html += "<hr/>"
        html += "<center> MESA: {} </center>".format(self.numero_da_mesa)
        html += "<hr/>"
        html += "<center align='left'>{}</center>".format(HORA)
        html += "<center align='left'>Usuário: {}</center>".format(data[0][7])

        html += "<center>Exmo(a) Sr.(a): {}</center>".format(data[0][6])
        html += "<center>{}</center>".format(self.label_total_items.text())

        html += "<table border='0' width = 100% style='border: thin;'>"

        html += "<tr>"

        html += "<th width = 70%>Descrição</th>"
        html += "<th width = 10%>Qt.</th>"
        html += "<th width = 20%>Hora</th>"

        html += "</tr>"

        total = 0

        for cliente in data:
            if cliente[3] > 0:
                preco = cliente[4] / cliente[3]
            else:
                preco = 0

            total += cliente[4]

            html += """<tr> <td>{}</td> <td align="right">{}</td> <td align="right">{}</td> </tr>
                                       """.format(cliente[2], cliente[1],
                                                  QDateTime.fromString(str(cliente[8]),
                                                                       "yyyy-MM-dd HH:mm:ss").toString("HH:mm:ss"))

        html += "</table>"
        html += "<hr/>"
        
        html += "<center> Processado por Computador  </center>".format(self.parent().licenca)
        html += "</div>"

        html += """
                            </body>
                        </html>
                        """

        self.actualiza_icremento()
        printer = QPrinter()
        printer.setPrinterName(self.parent().pos1)

        # printer.setFullPage(True)
        # printer.setPaperSource(printer.Auto)

        printer.setResolution(72)
        printer.setPaperSize(QSizeF(self.parent().papel_1,  3276), printer.Millimeter)
        printer.setPageMargins(0, 0, 10, 0, QPrinter.Millimeter)
        document = QTextDocument()
        # font = document.defaultFont()
        # s = font.toString().split(",")
        # document.setDefaultFont(QFont("{}".format(s[0]), 6))
        document.setHtml(html)
        document.setPageSize(QSizeF(printer.pageRect().size()))

        dialog = QPrintDialog()
        document.print_(printer)
        dialog.accept()

        return True

    def set_color_to_row(table, rowIndex, color):
        for j in range(table.columnCount()):
            table.item(rowIndex, j).setBackground(color)

    def closeEvent(self, evt):

        if self.tabelavazia() is True:

            # mSql = """DELETE from mesas WHERE numero="{}" """.format(self.numero_da_mesa)
            fSql = """DELETE from facturacao WHERE cod="{}" and finalizado=0 """.format(self.codigogeral)
            # self.cur.execute(mSql)
            self.cur.execute(fSql)
            self.conn.commit()

        # try:
        #     self.conn.cmd_refresh(1)
        # except Exception as e:
        #     QMessageBox.critical(self, "Erro na base de dados",
        #                          "Conexão com a Base de dados Perdida!!!\n{}.".format(e))
        if self.parent() is not None:
            self.parent().verificar_mesas(self.numero_da_mesa)
            self.parent().gera_codigogeral()
            self.parent().showMaximized()

    def verificar_permisao_apagar(self, user):
        sql = """SELECT apagar from users where cod="{}" AND apagar=1 """.format(user)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        apagar_item = 0

        if len(data) > 0:
            apagar_item = 1

        return apagar_item

    # Apaga a Linha na tabela facturadetalhe
    def removerow(self):

        apagar_item = self.verificar_permisao_apagar(self.user)

        if self.admin is False and apagar_item == 0:
            return False

        if self.cod_facturacaodetalhe == "" or self.cod_facturacaodetalhe is False:
            QMessageBox.information(self, "Info", "Selecione o registo a apagar na tabela")
            return False

        cod = self.get_codfacturacao(self.codigogeral)

        sql_1 = """delete from cozinhadetalhe WHERE codproduto="{codigo}" and codcozinha="{cod}"
                """.format(codigo=str(self.codproduto), cod=cod)

        sql = """delete from facturacaodetalhe WHERE cod="{codigo}" and codfacturacao="{cod}"
        """.format(codigo=self.cod_facturacaodetalhe, cod=self.codigogeral)

        if self.imprimir_items_apagados is True:
            self.imprime_removerow(self.cod_facturacaodetalhe)

        try:
            self.cur.execute(sql_1)
            self.cur.execute(sql)
            self.conn.commit()
            self.calcula_total_geral()
            self.fill_table()

            self.cod_line.setFocus()
            self.cod_line.selectAll()

            return True
        except Exception as e:
            print(e)
            return False

    def imprime_removerow_cozinha(self, codigo):
        sql = """SELECT p.nome, fd.quantidade from produtos p 
                JOIN facturacaodetalhe fd
                ON p.cod=fd.codproduto 
                JOIN familia f ON f.cod=p.codfamilia
                where (f.nome LIKE "%comida%" OR f.nome LIKE "%cozinha%") AND fd.cod={}""".format(codigo)


        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            return False


        html = """
            <!DOCTYPE html>
                <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <title>Template de Recibos POS</title>
                    </head>

                    <body style="font-size:8px;">

        """

        html += "<center> ITEM ELIMINADO </center>"
        html += "<center>***</center>"
        html += "<hr/>"
        html += "<center align='left'>{}</center>".format(HORA)
        html += "<center align='left'>Usuário: {}</center>".format(self.user)
        html += "<center align='left'>Mesa: {}</center>".format(self.numero_da_mesa)

        html += "<table border='0' width = 100% style='border: thin;'>"

        for item in data:
            html += "<tr><td>- {}</td><td>{}</td></tr>".format(item[1], item[0])
        html += "</table>"

        html += """
            </body>
        </html>
        """

        printer = QPrinter()
        printer.setPrinterName(self.parent().pos2)

        # printer.setFullPage(True)
        # printer.setPaperSource(printer.Auto)

        printer.setResolution(72)
        printer.setPaperSize(QSizeF(self.parent().papel_2,  3276), printer.Millimeter)
        printer.setPageMargins(0, 0, 10, 0, QPrinter.Millimeter)
        document = QTextDocument()
        # font = document.defaultFont()
        # s = font.toString().split(",")
        # document.setDefaultFont(QFont("{}".format(s[0]), 6))
        document.setHtml(html)
        document.setPageSize(QSizeF(printer.pageRect().size()))

        dialog = QPrintDialog()
        document.print_(printer)
        dialog.accept()

        return True

    def imprime_removerow_bar(self, codigo):
        sql = """SELECT p.nome, fd.quantidade from produtos p 
                JOIN facturacaodetalhe fd
                ON p.cod=fd.codproduto 
                JOIN familia f ON f.cod=p.codfamilia
                where NOT (f.nome LIKE "%comida%" OR f.nome LIKE "%cozinha%") AND fd.cod={}""".format(codigo)

        print(sql)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            return False

        html = """
            <!DOCTYPE html>
                <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <title>Template de Recibos POS</title>
                    </head>

                    <body style="font-size:8px;">

        """

        html += "<center> ITEM ELIMINADO </center>"
        html += "<center>***</center>"
        html += "<hr/>"
        html += "<center align='left'>{}</center>".format(HORA)
        html += "<center align='left'>Usuário: {}</center>".format(self.user)
        html += "<center align='left'>Mesa: {}</center>".format(self.numero_da_mesa)

        html += "<table border='0' width = 100% style='border: thin;'>"

        for item in data:
            html += "<tr><td>- {}</td><td>{}</td></tr>".format(item[1], item[0])
        html += "</table>"

        html += """
                    </body>
                </html>
                """
        printer = QPrinter()
        printer.setPrinterName(self.parent().pos1)

        # printer.setFullPage(True)
        # printer.setPaperSource(printer.Auto)

        printer.setResolution(72)
        printer.setPaperSize(QSizeF(self.parent().papel_1,  3276), printer.Millimeter)
        printer.setPageMargins(0, 0, 10, 0, QPrinter.Millimeter)
        document = QTextDocument()
        # font = document.defaultFont()
        # s = font.toString().split(",")
        # document.setDefaultFont(QFont("{}".format(s[0]), 6))
        document.setHtml(html)
        document.setPageSize(QSizeF(printer.pageRect().size()))

        dialog = QPrintDialog()
        document.print_(printer)
        dialog.accept()

        return True

    def imprime_removerow(self, codigo):
        self.imprime_removerow_bar(codigo)
        self.imprime_removerow_cozinha(codigo)

    # Apaga a Linha na tabela facturadetalhe
    def removeall(self):
        apagar_item = self.verificar_permisao_apagar(self.user)

        if self.admin is False and apagar_item == 0:
            return False

        cod = self.get_codfacturacao(self.codigogeral)

        if self.existe(self.codigogeral):
            sql_0 = """DELETE from cozinhadetalhe WHERE codcozinha="{}" """.format(cod)
            sql_1 = """DELETE from cozinha WHERE cod="{}" """.format(cod)
            sql = """DELETE from facturacaodetalhe WHERE codfacturacao="{}" """.format(self.codigogeral)
            sql2 = """DELETE from facturacao WHERE cod="{}" """.format(self.codigogeral)

            if self.imprimir_items_apagados is True:
                self.imprime_removeall(self.codigogeral)

            self.cur.execute(sql_0)
            self.cur.execute(sql_1)
            self.cur.execute(sql)
            self.cur.execute(sql2)
            self.conn.commit()

            self.label_total.setText("0.00")
            self.calcula_total_geral()
            self.fill_table()

            self.cod_line.setFocus()
            self.cod_line.selectAll()

            self.habilitar_butoes(False)
            self.butao_editar.setEnabled(False)

        return True

    def imprime_removeall_bar(self, codigo):
        sql = """SELECT p.nome, fd.quantidade from produtos p JOIN facturacaodetalhe fd
        ON p.cod=fd.codproduto 
        JOIN familia f ON f.cod=p.codfamilia
        where NOT (f.nome LIKE "%comida%" OR f.nome LIKE "%cozinha%") AND fd.codfacturacao="{}" """.format(codigo)

        print(sql)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            return False

        html = """
            <!DOCTYPE html>
                <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <title>Template de Recibos POS</title>
                    </head>

                    <body style="font-size:8px;">

        """

        if len(data) == 1:
            html += "<center> ITEM ELIMINADO </center>"
        else:
            html += "<center> ITEMS ELIMINADOS </center>"

        html += "<center>***</center>"
        html += "<hr/>"
        html += "<center align='left'>{}</center>".format(HORA)
        html += "<center align='left'>Usuário: {}</center>".format(self.user)
        html += "<center align='left'>Mesa: {}</center>".format(self.numero_da_mesa)

        html += "<table border='0' width = 100% style='border: thin;'>"

        for item in data:
            html += "<tr><td>- {}</td><td>{}</td></tr>".format(item[1], item[0])
        html += "</table>"

        html += """
                    </body>
                </html>
                """
        printer = QPrinter()
        printer.setPrinterName(self.parent().pos1)

        printer.setResolution(72)
        printer.setPaperSize(QSizeF(self.parent().papel_1,  3276), printer.Millimeter)
        printer.setPageMargins(0, 0, 10, 0, QPrinter.Millimeter)
        document = QTextDocument()
        # font = document.defaultFont()
        # s = font.toString().split(",")
        # document.setDefaultFont(QFont("{}".format(s[0]), 6))
        document.setHtml(html)
        document.setPageSize(QSizeF(printer.pageRect().size()))

        dialog = QPrintDialog()
        document.print_(printer)
        dialog.accept()

        return True

    def imprime_removeall_cozinha(self, codigo):
        sql = """SELECT p.nome, fd.quantidade from produtos p JOIN facturacaodetalhe fd
        ON p.cod=fd.codproduto 
        JOIN familia f ON f.cod=p.codfamilia
        where (f.nome LIKE "%comida%" OR f.nome LIKE "%cozinha%") AND fd.codfacturacao="{}" """.format(codigo)

        print(sql)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            return False

        html = """
            <!DOCTYPE html>
                <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <title>Template de Recibos POS</title>
                    </head>

                    <body style="font-size:8px;">

        """

        if len(data) == 1:
            html += "<center> ITEM ELIMINADO </center>"
        else:
            html += "<center> ITEMS ELIMINADOS </center>"

        html += "<center>***</center>"
        html += "<hr/>"
        html += "<center align='left'>{}</center>".format(HORA)
        html += "<center align='left'>Usuário: {}</center>".format(self.user)
        html += "<center align='left'>Mesa: {}</center>".format(self.numero_da_mesa)

        html += "<table border='0' width = 100% style='border: thin;'>"

        for item in data:
            html += "<tr><td>- {}</td><td>{}</td></tr>".format(item[1], item[0])
        html += "</table>"

        html += """
                    </body>
                </html>
                """
        
        printer = QPrinter()
        printer.setPrinterName(self.parent().pos2)

        # printer.setFullPage(True)
        # printer.setPaperSource(printer.Auto)

        printer.setResolution(72)
        printer.setPaperSize(QSizeF(self.parent().papel_2,  3276), printer.Millimeter)
        printer.setPageMargins(0, 0, 10, 0, QPrinter.Millimeter)
        document = QTextDocument()
        # font = document.defaultFont()
        # s = font.toString().split(",")
        # document.setDefaultFont(QFont("{}".format(s[0]), 6))
        document.setHtml(html)
        document.setPageSize(QSizeF(printer.pageRect().size()))

        dialog = QPrintDialog()
        document.print_(printer)
        dialog.accept()

        return True

    def imprime_removeall(self, codigo):
        self.imprime_removeall_bar(codigo)
        self.imprime_removeall_cozinha(codigo)

    def keyPressEvent(self, event):
        try:
            if event.key() in (Qt.Key_Enter, 16777220, Qt.Key_F10):
                if self.cod_line.text() != "":
                    self.codproduto = self.cod_line.text()
                    self.add_record()

            if event.key() == Qt.Key_F2:
                if self.gravar.isEnabled() or self.gravar.isVisible():
                    self.facturar()

            if event.key() == Qt.Key_F3:
                if self.recibo.isEnabled() or self.recibo.isVisible():
                    self.criar_recibo()

            if event.key() == Qt.Key_F4:
                if self.segundavia.isEnabled() or self.segundavia.isVisible():
                    self.segunda_via()

            if event.key() == Qt.Key_F5:
                self.fill_table()

            if event.key() == Qt.Key_F6:
                if self.receitas_despesas.isEnabled() or self.receitas_despesas.isVisible():
                    self.receitas()

            if event.key() == Qt.Key_F7:
                if self.gravardoc.isEnabled() or self.gravardoc.isVisible():
                    self.grava_transacao()

            if event.key() == Qt.Key_F8:
                if self.trancarsistema.isEnabled() or self.trancarsistema.isVisible():
                    self.trancar_sistema()

            if event.key() == Qt.Key_F10:
                if self.caixa.isEnabled() or self.caixa.isVisible():
                    self.fecho_caixa()

            if event.key() == Qt.Key_F11:
                if self.abrirdoc.isEnabled() or self.abrirdoc.isVisible():
                    self.abrir_documento()

            if event.key() == Qt.Key_Escape:
                self.close()

            if event.key() == Qt.Key_F12:
                self.removeall()

            event.ignore()

        except Exception as e:
            print(e)

    def facturar(self):

        if (self.admin or self.gestor) is False:
            return False

        if self.tabelavazia() is True:
            return False

        if self.existe(self.codigogeral) is True:

            from facturas import Cliente

            factura = Cliente(self, titulo="Facturação", imagem="./icons/Dollar.ico")

            factura.setModal(True)
            factura.gravar_grande.setVisible(False)
            self.limpar_cache()
            factura.show()

        return True

    def clickedslot(self, index):

        self.row = int(index.row())
        self.col = int(index.column())

        indice= self.tm.index(self.row, 0)
        self.current_id = indice.data()

        produto = self.tm.index(self.row, 1)
        codproduto = produto.data()
        self.codproduto = codproduto

        nome_produto = self.tm.index(self.row, 2)
        nome = nome_produto.data()
        self.nome_produto = nome

        preco = self.tm.index(self.row, 4)
        self.preco_unitario = decimal.Decimal(preco.data())

        self.butao_apagarItem.setEnabled(True)
        self.butao_editar.setEnabled(True)

        cod_facturacaodetalhe = self.tm.index(self.row, 9)
        self.cod_facturacaodetalhe = cod_facturacaodetalhe.data()
        print(self.cod_facturacaodetalhe)

        ordem = self.tm.index(self.row, 11)
        self.ordem = ordem.data()

    def editar_preco_quantidade(self):

        if self.current_id == "":
            QMessageBox.information(self, "Info", "Selecione o registo na tabela")
            return False

        if self.admin is False and self.ordem == "OK":
            QMessageBox.warning(self, "Ordem já foi emitida", "Não pode Editar depois de emitir a Ordem.")
            return False

        from editar_quantidade import EditarValores

        editar = EditarValores(self)
        editar.nome_produto.setPlainText(self.nome_produto)
        editar.preco_produto.setText(str(self.preco_unitario))
        editar.quantidade_produto.setText(str(self.quantidade_unitario))
        editar.cod_produto = self.codproduto
        editar.codigogeral = self.codigogeral
        editar.cod_facturacaodetalhe = self.cod_facturacaodetalhe
        editar.preco_produto.setEnabled(self.admin)
        editar.butao_preco.setEnabled(self.admin)

        editar.setModal(True)
        editar.show()

        return True

    def fill_table(self):

        header = ["DOC", "Artigo", "Descrição", "Qty", "Preço", "Taxa", "Desconto", "Subtotal", "Total",  "",
                  "Hora", ""]

        sql = """ select facturacao.cod, facturacaodetalhe.codproduto, produtos.nome, facturacaodetalhe.quantidade, 
           facturacaodetalhe.preco, facturacaodetalhe.taxa, facturacaodetalhe.desconto, facturacaodetalhe.subtotal,
           facturacaodetalhe.total, facturacaodetalhe.cod, facturacaodetalhe.created, facturacaodetalhe.ordem 
           FROM produtos INNER JOIN facturacaodetalhe ON produtos.cod=facturacaodetalhe.codproduto
           INNER JOIN facturacao  ON facturacao.cod=facturacaodetalhe.codfacturacao WHERE 
           (facturacao.cod="{facturacaocod}") """.format(facturacaocod=self.codigogeral)

        try:
            self.cur.execute(sql)
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]

        except Exception as e:
            print(e)
            return

        if len(data) == 0:
            self.tabledata = [('', '', '', "", "", "", "", "", "")]
        else:
            l = []
            for x in data:
                row = list(x)
                print(row)
                if row[11] == '0':
                    row[11] = "X"
                else:
                    row[11] = "OK"

                row[10] = QDateTime.fromString(row[10], "yyyy-MM-dd HH:mm:ss").toString("HH:mm:ss")

                l.append(row)

            self.tabledata = l

        try:
            # set the table model
            self.tm = MyTableModel(self.tabledata, header, self)

            i = self.tm.index(1, 1)
            self.tm.setData(i, QBrush(Qt.red), Qt.BackgroundRole)
            self.totalItems = self.tm.rowCount(self)
            self.label_total_items.setText("ITEMS: {}.".format(self.totalItems))
            self.tabela.setModel(self.tm)
            self.tabela.setColumnHidden(0, True)
            self.tabela.setColumnHidden(1, True)
            self.tabela.setColumnHidden(5, True)
            self.tabela.setColumnHidden(6, True)
            self.tabela.setColumnHidden(7, True)
            self.tabela.setColumnHidden(9, True)

            self.tabela.setColumnWidth(2, self.tabela.width() * 0.35)
            self.tabela.setColumnWidth(3, self.tabela.width() * 0.1)
            self.tabela.setColumnWidth(4, self.tabela.width() * 0.1)
            self.tabela.setColumnWidth(8, self.tabela.width() * 0.15)
            self.tabela.setColumnWidth(10, self.tabela.width() * 0.2)
            self.tabela.setColumnWidth(11, self.tabela.width() * 0.1)

        except Exception as e:
            print(e)
            return
        # # set row height
        nrows = len(self.tabledata)
        for row in range(nrows):
            self.tabela.setRowHeight(row, 30)

