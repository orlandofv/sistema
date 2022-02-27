# -*- coding: utf-8 -*-

import sys
import operator
from decimal import Decimal
import os
import datetime

from PyQt5.QtWidgets import QApplication, QTableView, QAbstractItemView, QMessageBox, QToolBar, \
    QLineEdit, QLabel, QStatusBar, QAction, QMainWindow, qApp, QDateTimeEdit, QCalendarWidget

from PyQt5.QtGui import QIcon, QTextDocument
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant, QDateTime
from PyQt5.QtPrintSupport import QPrintPreviewDialog
import sqlite3 as lite
from utilities import printWordDocument, Invoice
from relatorio.templates.opendocument import Template
from utilities import codigo as cd
from reservas import Reservas


class Lista_de_Reservas(QMainWindow):

    caixa_numero = ""
    codreserva = ""

    def __init__(self, parent=None):
        super(Lista_de_Reservas, self).__init__(parent)

        # controla o codigo
        self.current_id = ""
        self.conn = self.parent().conn
        self.cur = self.parent().cur
        self.user = self.parent().user
        self.codarmazem = self.parent().codarmazem
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

        # Create the main user interface
        self.ui()

        # Search the data
        self.fill_table()
        self.find_w.textEdited.connect(self.fill_table)
        self.data_inicial.dateChanged.connect(self.fill_table)
        self.data_final.dateChanged.connect(self.fill_table)

    def ui(self):

        # create the view
        self.tv = QTableView(self)

        # set the minimum size
        self.tv.setMinimumSize(400, 300)

        # hide grid
        self.tv.setShowGrid(False)

        self.tv.setSelectionBehavior(QAbstractItemView.SelectRows)
        # set the font

        # hide vertical header
        vh = self.tv.verticalHeader()
        vh.setVisible(False)

        # set horizontal header properties and stretch last column
        hh = self.tv.horizontalHeader()
        hh.setStretchLastSection(True)

        # set column width to fit contents
        self.tv.resizeColumnsToContents()

        # enable sorting
        self.tv.setSortingEnabled(True)

        self.tv.clicked.connect(self.clickedslot)
        self.tv.setAlternatingRowColors(True)
        self.tv.setFocus()
        self.setCentralWidget(self.tv)
        self.create_toolbar()

    def focusInEvent(self, evt):
        self.fill_table()

    def fill_table(self):

        # Header for the table
        header = [qApp.tr('Código'), qApp.tr('Nome'), "Apelido", qApp.tr('Data de Entrada'), "Data de Saída",
                  "Quarto", qApp.tr('Comentários'), "cod", "cl"]

        data1 = self.data_inicial.date().toString("yyyy-MM-dd H:mm:ss")
        data2 = self.data_final.date().toString("yyyy-MM-dd H:mm:ss")

        self.sql = """select reservas.codfacturacao, hospedes.nome, hospedes.apelido, reservas.data_entrada, 
        reservas.data_saida, reservas.cod_quarto, reservas.obs, reservas.cod, reservas.hospede 
        from reservas JOIN hospedes on hospedes.cod=reservas.cod_cliente 
        WHERE (reservas.data_entrada BETWEEN "{data_inicial}" AND "{data_final}" 
        AND reservas.data_saida BETWEEN "{data_inicial}" AND "{data_final}") AND hospedes.nome like "%{nome}%"  
        """.format(nome=self.find_w.text(), data_inicial=data1, data_final=data2)

        try:
            self.cur.execute(self.sql)
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]

            nova_lista = []
            for l in data:
                l = list(l)
                l[3] = QDateTime.fromString(l[3], 'yyyy-MM-dd H:mm:ss').toString('dd-MMM-yyyy H:mm:ss')
                l[4] = QDateTime.fromString(l[4], 'yyyy-MM-dd H:mm:ss').toString('dd-MMM-yyyy H:mm:ss')

                nova_lista.append(tuple(l))

            data = nova_lista

        except Exception as e:
            print(e)
            return

        if len(data) == 0:
            self.tabledata = ["", "", "", "", "", "", "", ""]
        else:
            self.tabledata = data

        try:
            self.tm = MyTableModel(self.tabledata, header, self)
            # set the table model
            self.totalItems = self.tm.rowCount(self)
            self.tv.setModel(self.tm)
            self.tv.setColumnHidden(0, True)
            self.tv.setColumnHidden(7, True)
            self.tv.setColumnHidden(8, True)
        except Exception as e:
            return
        # # set row height
        nrows = len(self.tabledata)
        for row in range(nrows):
            self.tv.setRowHeight(row, 25)
        self.create_statusbar()

    def create_toolbar(self):
        find = QLabel(qApp.tr("Procurar") + "  ")
        self.find_w = QLineEdit(self)
        self.find_w.setMaximumWidth(200)

        self.new = QAction(QIcon('./icons/add_2.ico'), qApp.tr("Novo"), self)
        self.delete = QAction(QIcon('./images/editdelete.png'), qApp.tr("Eliminar"), self)
        self.print = QAction(QIcon('./images/fileprint.png'), qApp.tr("Imprimir"), self)
        self.update = QAction(QIcon('./images/pencil.png'), qApp.tr("Editar"), self)
        action_check_in = QAction(QIcon("icons/clientes.ico"), "Entradas (Check IN)", self)

        calendario1 = QCalendarWidget()
        calendario2 = QCalendarWidget()

        self.data_inicial = QDateTimeEdit()
        self.data_inicial.setCalendarPopup(True)
        self.data_inicial.setCalendarWidget(calendario1)
        self.data_inicial.setDateTime(QDateTime.currentDateTime().addDays(-30))

        data = QDateTime.currentDateTime().addDays(30)

        self.data_final = QDateTimeEdit()
        self.data_final.setCalendarPopup(True)
        self.data_final.setCalendarWidget(calendario2)
        self.data_final.setDateTime(data)

        tool = QToolBar()
        tool.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        tool.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        tool.setContextMenuPolicy(Qt.PreventContextMenu)

        tool.addWidget(QLabel("  Data de Entrada "))
        tool.addWidget(self.data_inicial)
        tool.addWidget(QLabel("  Data de Saída "))
        tool.addWidget(self.data_final)
        tool.addWidget(QLabel("  "))
        tool.addWidget(find)
        tool.addWidget(self.find_w)

        tool2 = QToolBar()
        tool2.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        tool2.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        tool2.setContextMenuPolicy(Qt.PreventContextMenu)

        tool2.addAction(self.new)
        tool2.addAction(self.update)
        tool2.addSeparator()
        tool2.addAction(self.delete)
        tool2.addSeparator()
        tool2.addAction(self.print)
        tool2.addSeparator()
        tool2.addAction(action_check_in)

        self.addToolBar(tool2)
        self.addToolBarBreak(Qt.TopToolBarArea)
        self.addToolBar(tool)

        ######################################################################
        self.new.triggered.connect(self.new_data)
        self.delete.triggered.connect(self.removerow)
        self.tv.doubleClicked.connect(self.update_data)
        self.update.triggered.connect(self.update_data)
        self.print.triggered.connect(self.imprime_lista)
        action_check_in.triggered.connect(self.cria_checkin)

    def verifica_estado(self, codreserva):
        sql = """SELECT estado FROM reservas WHERE cod={} """.format(codreserva)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if data[0][0] == 1:
            return True

        return False

    def cria_checkin(self):

        if self.codreserva == "":
            QMessageBox.warning(self, "Erro", "Escolha o registo para fazer Check IN na Tabela")
            return False

        if self.verifica_estado(self.codreserva) is False:
            QMessageBox.warning(self, "Erro", "Já foi criado um Check In para esta reserva")
            return False

        sql_reservas = """SELECT * FROM reservas WHERE cod="{}" """.format(self.codreserva)
        self.cur.execute(sql_reservas)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                created = QDateTime.currentDateTime().toString("yyyy-MM-dd H:mm:ss")
                modified = created
                created_by = self.user
                modified_by = self.user
                entrada = item[1]
                saida = item[2]
                cliente = item[3]
                quarto = item[4]
                pago = 0
                divida = 0
                obs = item[5]
                estado = 1
                hospede = item[11]
                voucher = item[12]
                pagamento = item[13]
                moeda = item[14]
                codfacturacao = "FT" + cd("FT" + "abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")

                dias = self.get_dias(entrada, saida)
                valor_quarto = self.get_preco(quarto)
                total = dias * valor_quarto

                if self.quarto_ocupado(quarto) is True:
                    QMessageBox.warning(self, "Ocupado", "O quarto {} encontra-se ocupado".format(quarto))
                    return False

                if self.verifica_quarto(quarto) is False:
                    QMessageBox.warning(self, "Erro", "O Quarto {} está ocupado.\nDesecupe-o primeiro.".format(quarto))
                    return

                values = """ "{entrada}", "{saida}", "{cliente}", {quarto}, {total}, {pago}, {divida}, "{obs}", 
                            "{created}", "{modified}", "{modified_by}", "{created_by}", {estado}, 
                            "{hospede}", "{voucher}", "{pagamento}", "{moeda}", "{codfacturacao}"
                            """.format(entrada=entrada, saida=saida, cliente=cliente,
                                       quarto=quarto, total=total, pago=pago, divida=divida,obs=obs, created=created, modified=modified,
                                       modified_by=modified_by, created_by=created_by, estado=estado,
                                       hospede=hospede, voucher=voucher,
                                       pagamento=pagamento, moeda=moeda, codfacturacao=codfacturacao)

                sql = """INSERT INTO check_in (data_entrada, data_saida, cod_cliente, cod_quarto, total, pago, divida,
                obs, created, modified, modified_by, created_by, estado, 
                hospede, voucher, pagamento, moeda, codfacturacao) VALUES ({})""".format(values)

                sql_quartos = """UPDATE quartos SET ocupado = 1 WHERE cod={} """.format(quarto)
                sql_hospedes = """UPDATE hospedes SET estado = 0 WHERE cod="{}" """.format(cliente)
                sql_reservas = """UPDATE reservas SET estado = 0 WHERE cod={} """.format(self.get_cod_reserva())

                try:
                    self.cur.execute(sql_quartos)
                    self.cur.execute(sql_hospedes)
                    self.cur.execute(sql_reservas)
                    self.cur.execute(sql)
                    self.conn.commit()

                except Exception as e:
                    self.conn.rollback()
                    QMessageBox.critical(self, "Erro", "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
                    return False

                from check_in import Check_in
                c = Check_in(self)
                c.impreme_entrada(self.get_cod_checkin(), self.hospede)

                QMessageBox.information(self, "Informação", "Check IN efectuado com sucesso!")
                return True

    def get_cod_reserva(self):
        sql = "SELECT MAX(cod) from reservas"
        self.cur.execute(sql)
        data = self.cur.fetchall()
        return data[0][0]

    def get_cod_checkin(self):
        sql = "SELECT MAX(cod) from check_in"
        self.cur.execute(sql)
        data = self.cur.fetchall()
        return data[0][0]

    def quarto_ocupado(self, quarto):
        sql = """SELECT estado from quartos where ocupado=1 AND cod={} """.format(quarto)
        self.cur.execute(sql)

        data = self.cur.fetchall()
        if len(data) == 0:
            return False

        return True

    def get_dias(self, d_entrada, d_saida):

        entrada = QDateTime(d_entrada).toPyDateTime()
        saida = QDateTime(d_saida).toPyDateTime()

        if saida <= entrada:
            dias = 1
        else:
            diff = saida - entrada
            dias = int(diff.days)

        return dias

    def get_preco(self, cod):

        sql = """SELECT preco from quartos WHERE cod={}""".format(int(cod))
        self.cur.execute(sql)

        data = self.cur.fetchall()

        if len(data) > 0:
            preco = float(data[0][0])
            self.valor_do_quarto = Decimal(preco)

        return self.valor_do_quarto

    def verifica_quarto(self, cod_quarto):
        sql = """SELECT ocupado from quartos WHERE cod="{}" AND ocupado=0 """.format(cod_quarto)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            # O quarto esta livre
            return True
        else:
            # O quarto esta ocupado
            return False

    def create_statusbar(self):
        estado = QStatusBar(self)

        self.items = QLabel("Total Items: %s" % self.totalItems)
        estado.addWidget(self.items)
        self.setStatusBar(estado)

    def clickedslot(self, index):

        self.row = int(index.row())

        indice = self.tm.index(self.row, 0)
        self.current_id = indice.data()

        cod = self.tm.index(self.row, 7)
        self.codreserva = cod.data()

        c = self.tm.index(self.row, 1)
        self.hospede = c.data()

        hos = self.tm.index(self.row, 8)
        self.cliente = hos.data()

        q = self.tm.index(self.row, 5)
        self.quarto = q.data()

    def new_data(self):
        cl = Reservas(self)

        if cl.enche_hospedes() is False:
            QMessageBox.warning(self, "Sem Hóspedes", "Cadastre Hóspedes antes de continuar.")
            return

        if cl.enche_quartos() is False:
            QMessageBox.warning(self, "Sem Quartos Disponíveis", "Todos os Quartos estão ocupados ou"
                                                                 " Cadastre Quartos antes de continuar.")
            return

        cl.setModal(True)
        cl.show()

    def update_data(self):

        if self.codreserva == "":
            QMessageBox.information(self, "Info", "Selecione o registo a actualizar na tabela")
            return

        from reservas import Reservas
        cl = Reservas(self)
        cl.codigo = int(self.codreserva)
        cl.mostrar_registo(self.codreserva)
        cl.nome_hospede.addItem(self.hospede)
        cl.quarto_numero.addItem(self.quarto)
        cl.enche_hospedes()
        cl.enche_quartos()
        cl.setModal(True)
        cl.show()

    def removerow(self):

        if self.codreserva == "":
            QMessageBox.information(self, "Info", "Selecione o registo a apagar na tabela")
            return

        if self.codreserva != "CL20181111111":
            if QMessageBox.question(self, "Pergunta", str("Deseja eliminar o registo %s?") % self.codreserva,
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                sql = """delete from reservas WHERE cod = "{codigo}" """.format(codigo=str(self.codreserva))

                print(sql)

                try:
                    self.cur.execute(sql)
                    self.conn.commit()
                    self.fill_table()
                    QMessageBox.information(self, "Sucesso", "Item apagado com sucesso...")
                except Exception as e:
                    QMessageBox.warning(self, "Erro", "Impossivel apagar quarto.")
        else:
            QMessageBox.warning(self, "Erro", "Reservas não pode ser apagado.")

    def imprime_lista(self):
        """Imprime no ecra a Lista geral de produtos baseado em um Critério"""
        if self.sql == "":
            return

        self.cur.execute(self.sql)
        dados = self.cur.fetchall()

        html = "<center> <h2> Lista de Reservas </h2> </center>"
        html += "<hr/>"

        html += "<br/>"

        html += "<table border=0 width = 100% style='border: thin;'>"

        # Header for the table
        header = [qApp.tr('Código'), qApp.tr('Nome'), "Apelido", qApp.tr('Data de Entrada'), "Data de Saída",
                  "Quarto", qApp.tr('Comentários')]

        html += "<tr style='background-color:#c0c0c0;'>"
        html += "<th width = 30%>Nome</th>"
        html += "<th width = 10%>Apelido</th>"
        html += "<th width = 10%>Entrada</th>"
        html += "<th width = 10%>Saída</th>"
        html += "<th width = 10%>Quarto</th>"
        html += "<th width = 20%>Comentários</th>"
        html += "</tr>"

        for cliente in dados:

            html += """<tr> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td>  
            </tr>""".format(cliente[1], cliente[2],cliente[3], cliente[4],
                            cliente[5], cliente[6])
        html += "</table>"

        html += "<hr/>"

        html += """<p style = "margin: 0 auto;
                   font-family: Arial, Helvetica, sans-serif;
                   position: absolute;
                   bottom: 10px;">processador por computador</p>"""

        document = QTextDocument()
        document.setHtml(html)

        dlg = QPrintPreviewDialog(self)
        dlg.paintRequested.connect(document.print_)
        dlg.showMaximized()
        dlg.exec_()

    def imprime_recibo_grande(self, codigo):

        if self.current_id == "":
            QMessageBox.warning(self, "Erro", "Escolha registo para imprimir na lista")
            return

        sql = """SELECT factura_geral.*, reservas_view.* FROM reservas_view 
        INNER JOIN factura_geral ON factura_geral.codfacturacao=reservas_view.codfacturacao 
        WHERE factura_geral.codfacturacao = '{}' """.format(codigo)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        print(data)

        logo = os.path.realpath(self.empresa_logo)
        empresa =  self.empresa
        endereco = self.empresa_endereco
        contactos = self.empresa_contactos
        web = '{}, {}'.format(self.empresa_email, self.empresa_web)
        nuit = self.empresa_nuit
        casas = self.empresa_casas_decimais
        licenca = self.licenca
        contas = self.contas

        if len(data) > 0:

            doc = "{}/{}{}".format(data[0][1], data[0][23], data[0][22])
            cod_reserva = "{}/{}{}".format(data[0][31], data[0][23], data[0][22])
            try:
                data_doc = datetime.datetime.strptime(str(data[0][3]), "%Y-%m-%d").strftime("%d-%m-%Y")
                data_entrada = datetime.datetime.strptime(str(data[0][32]), "%Y-%m-%d").strftime("%d-%m-%Y")
                data_saida = datetime.datetime.strptime(str(data[0][33]), "%Y-%m-%d").strftime("%d-%m-%Y")
            except ValueError:
                data_doc = ""

            try:
                vencimento = datetime.datetime.strptime(str(data[0][28]), "%Y-%m-%d").strftime("%d-%m-%Y")
            except ValueError:
                vencimento = ""

            line = []
            for item in data:
                line += [{'item': {'name': item[15], 'reference': item[16],
                                   'price': "{:20,.2f}".format(Decimal(item[19])), 'armazem': data[0][30]},
                          'quantity': "{:20,.2f}".format(Decimal(item[17])),
                          'amount': "{:20,.2f}".format(Decimal(item[20])), 'armazem': data[0][30]}, ]

            inv = Invoice(customer={'name': 'Orlando Vilanculo',
                                    'address': {'street': 'Smirnov street', 'zip': 1000, 'city': 'Montreux'}},
                          clienteweb=data[0][13],
                          clienteendereco=data[0][11],
                          clientenome=data[0][10],
                          clientenuit=data[0][12],
                          clientecontactos=data[0][27],
                          empresanome=empresa,
                          empresaendereco=endereco,
                          empresanuit=nuit,
                          empresacontactos=contactos,
                          empresaweb=web,
                          contas=contas,
                          licenca=licenca,
                          vencimento=vencimento,
                          lines=line,
                          id=doc,
                          status='late',
                          doc=data[0][2],
                          datadoc=data_doc,
                          operador=data[0][4],
                          obs=data[0][29],
                          subtotal="{:20,.2f}".format(data[0][5]),
                          desconto="{:20,.2f}".format(data[0][6]),
                          iva="{:20,.2f}".format(data[0][7]),
                          totalgeral="{:20,.2f}".format(data[0][8]),
                          armazem=data[0][30],
                          reserva=cod_reserva,
                          entrada=data_entrada,
                          saida=data_saida,
                          hospede=data[0][34],
                          quarto=data[0][35],
                          voucher=data[0][36],
                          pagamento=data[0][37],
                          moeda=data[0][38],
                          )

            # Verifica o Ficheiro de entrada Template
            filename = os.path.realpath('template.odt')
            if os.path.isfile(filename) is False:
                QMessageBox.critical(self, "Erro ao Imprimir",
                                     "O ficheiro modelo '{}'  não foi encontrado.".format(filename))
                return

            # Verifica o ficheiro de saida
            targetfile = "reservas.odt"

            if os.path.isfile(targetfile) is False:
                QMessageBox.critical(self, "Erro ao Imprimir",
                                     "O ficheiro modelo '{}'  não foi encontrado. \n "
                                     "Reponha-o para poder Imprimir".format(targetfile))
                return

            print("No basic", targetfile, filename)
            basic = Template(source='', filepath=targetfile)

            print("escrevendo no file")
            open(filename, 'wb').write(basic.generate(o=inv).render().getvalue())

            print("Criando doc out")
            doc_out = cd("0123456789") + "{}{}{}{}".format(data[0][2], data[0][1], data[0][23], data[0][22])

            print("Criando out")
            out = os.path.realpath("'{}'.pdf".format(doc_out))

            print("Criando caminho Python")
            caminho = os.path.realpath("C:\\Program Files\\LibreOffice\\program\\python-core-3.5.7\\bin\\python.exe")

            print(os.path.isfile(caminho))
            os.system(""" {} unoconv.py -f
            pdf {} """.format(caminho, targetfile))
            print("Chegui ao fim")
            printWordDocument(filename, out)


class MyTableModel(QAbstractTableModel):
    def __init__(self, datain, headerdata, parent=None, *args):
        """ datain: a list of lists
            headerdata: a list of strings
        """
        QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = datain
        self.headerdata = headerdata

    def rowCount(self, parent):
        return len(self.arraydata)

    def columnCount(self, parent):
        return len(self.arraydata[0])

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        return QVariant(self.arraydata[index.row()][index.column()])

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerdata[col])
        return QVariant()

    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        self.layoutAboutToBeChanged.emit()
        self.arraydata = sorted(self.arraydata, key=operator.itemgetter(Ncol))
        if order == Qt.DescendingOrder:
            self.arraydata.reverse()
        self.layoutChanged.emit()


if __name__ == '__main__':

    app = QApplication(sys.argv)
#
    helloPythonWidget = Lista_de_Reservas()
    helloPythonWidget.show()
#
    sys.exit(app.exec_())