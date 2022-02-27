# -*- coding: utf-8 -*-

import sys
import operator
from decimal import Decimal
import datetime
import os
from time import strftime, localtime

from PyQt5.QtWidgets import QApplication, QTableView, QAbstractItemView, QMessageBox, QToolBar, \
    QLineEdit, QLabel, QStatusBar, QAction, QMainWindow, qApp, QDateTimeEdit, QCalendarWidget, \
    QComboBox, QRadioButton, QHBoxLayout, QWidget

from PyQt5.QtGui import QIcon, QTextDocument
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant, QDate, QDateTime
from PyQt5.QtPrintSupport import QPrintPreviewDialog

from sortmodel import MyTableModel
from utilities import printWordDocument, Invoice
from relatorio.templates.opendocument import Template
from utilities import codigo as cd

DATA_HORA_FORMATADA = strftime("%Y-%m-%d %H:%M:%S", localtime())
DATA_ACTUAL = datetime.date.today()
ANO_ACTUAL = DATA_ACTUAL.year
DIA = DATA_ACTUAL.day
MES = DATA_ACTUAL.month


class ListaCheckIN(QMainWindow):
    def __init__(self, parent=None):
        super(ListaCheckIN, self).__init__(parent)

        self.empresa = self.parent().empresa
        self.empresa_cabecalho = self.parent().empresa_cabecalho
        self.empresa_logo = self.parent().empresa_logo
        self.empresa_slogan = self.parent().empresa_slogan
        self.empresa_endereco = self.parent().empresa_endereco
        self.empresa_contactos = self.parent().empresa_contactos
        self.empresa_email = self.parent().empresa_email
        self.empresa_web = self.parent().empresa_web
        self.empresa_nuit = self.parent().empresa_nuit
        self.empresa_casas_decimais = self.parent().empresa_casas_decimais
        self.licenca = self.parent().licenca
        self.contas = self.parent().contas

        # controla o codigo
        self.current_id = ""
        self.quarto = 0
        self.hospede = ""
        self.cliente = ""
        self.codfacturacao = ""
        self.entrada = QDateTime()
        self.saida = QDateTime.currentDateTime()
        self.coddocumento = "DC20181111111"

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
        self.create_toolbar()
        # Search the data
        #
        self.radio_tudo.setChecked(True)
        self.fill_table()
        self.find_w.textEdited.connect(self.fill_table)
        self.data_inicial.dateChanged.connect(self.fill_table)
        self.data_final.dateChanged.connect(self.fill_table)
        self.radio_checkin.clicked.connect(self.fill_table)
        self.radio_checkout.clicked.connect(self.fill_table)
        self.radio_tudo.clicked.connect(self.fill_table)

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

    def fill_table(self):

        entrada = self.data_inicial.dateTime().toPyDateTime()
        saida = self.data_final.dateTime().toPyDateTime()

        if saida < entrada:
            self.data_final.setDateTime(self.data_inicial.dateTime())
        
        data1 = self.data_inicial.dateTime().toString('yyyy-MM-dd H:mm:ss')
        data2 = self.data_final.dateTime().toString('yyyy-MM-dd H:mm:ss')
        
        # Header for the table
        header = [qApp.tr('Código'), qApp.tr('Hóspede'), "Quarto", "Valor/dia", "Data de Entrada", "Data de Saída",
                  qApp.tr('Estado'), qApp.tr('Comentários'), "cl", "fact"]

        if self.radio_tudo.isChecked():
            self.sql = """select check_in.cod, hospedes.nome, quartos.cod, quartos.preco, check_in.data_entrada, check_in.data_saida, 
                        check_in.estado, check_in.obs, check_in.hospede,
                        check_in.codfacturacao FROM check_in INNER JOIN hospedes
                        ON hospedes.cod=check_in.cod_cliente INNER JOIN quartos ON quartos.cod=check_in.cod_quarto WHERE
                        (hospedes.nome like "%{nome}%" or quartos.cod like "%{nome}%" or check_in.total like "%{nome}%") 
                        AND (check_in.data_entrada BETWEEN "{data_inicial}" AND "{data_final}"  
                        AND check_in.data_saida BETWEEN "{data_inicial}" AND "{data_final}" ) """.format(nome=self.find_w.text(),
                                                                              data_inicial=data1,
                                                                              data_final=data2)
        elif self.radio_checkin.isChecked():
            self.sql = """select check_in.cod, hospedes.nome, quartos.cod, quartos.preco, check_in.data_entrada, check_in.data_saida, 
                        check_in.estado, check_in.obs, check_in.hospede,
                        check_in.codfacturacao FROM check_in INNER JOIN hospedes
                        ON hospedes.cod=check_in.cod_cliente INNER JOIN quartos ON quartos.cod=check_in.cod_quarto WHERE
                        (hospedes.nome like "%{nome}%" or quartos.cod like "%{nome}%" or check_in.total like "%{nome}%") 
                        AND check_in.estado=1 AND (check_in.data_entrada BETWEEN "{data_inicial}" AND "{data_final}"  
                        AND check_in.data_saida BETWEEN "{data_inicial}" AND "{data_final}" ) """.format(nome=self.find_w.text(),
                                                                              data_inicial=data1,
                                                                              data_final=data2)
        else:
            self.sql = """select check_in.cod, hospedes.nome, quartos.cod, quartos.preco , check_in.data_entrada, check_in.data_saida, 
                        check_in.estado, check_in.obs, check_in.hospede, 
                        check_in.codfacturacao FROM check_in INNER JOIN hospedes
                        ON hospedes.cod=check_in.cod_cliente INNER JOIN quartos ON quartos.cod=check_in.cod_quarto WHERE
                        (hospedes.nome like "%{nome}%" or quartos.cod like "%{nome}%" or check_in.total like "%{nome}%") 
                        AND check_in.estado=0 AND (check_in.data_entrada BETWEEN "{data_inicial}" AND "{data_final}"  
                        AND check_in.data_saida BETWEEN "{data_inicial}" AND "{data_final}" ) """.format(nome=self.find_w.text(),
                                                                              data_inicial=data1,
                                                                              data_final=data2)
        try:
            self.cur.execute(self.sql)
            lista = self.cur.fetchall()

            data = [tuple(str(item) for item in t) for t in lista]

            print(data)

            nova_lista = []
            for item in data:

                i = list(item)

                if i[6] == '1':
                    i[6] = "IN"
                else:
                    i[6] = "OUT"

                i[4] = QDateTime.fromString(i[4], 'yyyy-MM-dd H:mm:ss').toString('dd-MMM-yyyy H:mm:ss')
                i[5] = QDateTime.fromString(i[5], 'yyyy-MM-dd H:mm:ss').toString('dd-MMM-yyyy H:mm:ss')

                nova_lista.append(i)

        except Exception as e:
            print(e)
            return

        if len(data) == 0:
            self.tabledata = ["", "", "", "", "", "", "", ""]
        else:
            self.tabledata = nova_lista

        try:
            self.tm = MyTableModel(self.tabledata, header, self)
            # set the table model
            self.totalItems = self.tm.rowCount(self)
            self.tv.setModel(self.tm)
            self.tv.setColumnHidden(0, True)
            self.tv.setColumnHidden(8, True)
            self.tv.setColumnHidden(9, True)
        except Exception as e:
            print(e)
            return

        nrows = len(self.tabledata)
        for row in range(nrows):
            self.tv.setRowHeight(row, 25)
        self.create_statusbar()

    def create_toolbar(self):
        find = QLabel(qApp.tr("Procurar") + "  ")
        self.find_w = QLineEdit(self)
        self.find_w.setMaximumWidth(200)

        calendario1 = QCalendarWidget()
        calendario2 = QCalendarWidget()

        self.data_inicial = QDateTimeEdit()
        self.data_inicial.setDateTime(QDateTime.currentDateTime().addDays(-30))
        self.data_inicial.setCalendarPopup(True)
        self.data_inicial.setCalendarWidget(calendario1)

        self.data_final = QDateTimeEdit()
        self.data_final.setDateTime(QDateTime.currentDateTime().addDays(30))
        self.data_final.setCalendarPopup(True)
        self.data_final.setCalendarWidget(calendario2)

        self.radio_checkin = QRadioButton("Check In")
        self.radio_checkin.setChecked(True)

        self.radio_checkout = QRadioButton("Check Out")
        self.radio_tudo = QRadioButton("Tudo")

        self.new = QAction(QIcon('./icons/add_2.ico'), qApp.tr("Novo"), self)
        self.delete = QAction(QIcon('./images/editdelete.png'), qApp.tr("Eliminar"), self)
        self.print = QAction(QIcon('./images/fileprint.png'), qApp.tr("Imprimir"), self)
        self.update = QAction(QIcon('./images/pencil.png'), qApp.tr("Editar"), self)
        self.checkout = QAction(QIcon("./images/log_out_32.png"), "Check Out (Saídas)")
        imprime_recibo = QAction(QIcon('./icons/printer2.ico'), qApp.tr("Reimprimir Recibo"), self)
        imprime_checkin = QAction(QIcon('/icons/printer.ico'), qApp.tr("Reimprimir Ckeck In"), self)

        self.sem_iva = QRadioButton("IVA Isento")
        self.sem_iva.setChecked(True)
        self.iva_incluso = QRadioButton("IVA Incluso no Preço")
        self.adicionar_iva = QRadioButton("Adicionar Iva no Preço")
        iva_lay = QHBoxLayout()
        iva_lay.addWidget(self.sem_iva)
        iva_lay.addWidget(self.iva_incluso)
        iva_lay.addWidget(self.adicionar_iva)
        self.iva_widget = QWidget()
        self.iva_widget.setLayout(iva_lay)

        tool = QToolBar()
        tool.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        tool2 = QToolBar()
        tool.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        tool.setContextMenuPolicy(Qt.PreventContextMenu)
        tool2.setContextMenuPolicy(Qt.PreventContextMenu)
        tool.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        tool2.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)

        tool2.addWidget(QLabel("  Data de Entrada "))
        tool2.addWidget(self.data_inicial)
        tool2.addWidget(QLabel("  Data de Saída "))
        tool2.addWidget(self.data_final)
        tool2.addWidget(QLabel("  "))
        tool2.addWidget(self.radio_checkin)
        tool2.addWidget(self.radio_checkout)
        tool2.addWidget(self.radio_tudo)
        tool2.addWidget(find)
        tool2.addWidget(self.find_w)

        tool.addAction(self.new)
        tool.addAction(self.update)
        tool.addSeparator()
        tool.addAction(self.delete)

        tool_search = QToolBar()
        tool_search.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        tool_search.setContextMenuPolicy(Qt.PreventContextMenu)
        tool_search.addAction(self.checkout)
        tool_search.addSeparator()
        tool_search.addAction(self.print)
        tool_search.addAction(imprime_recibo)
        tool_search.addAction(imprime_checkin)

        self.addToolBar(tool)
        self.addToolBar(tool_search)
        self.addToolBarBreak(Qt.TopToolBarArea)
        self.addToolBar(tool2)

        ######################################################################
        self.new.triggered.connect(self.new_data)
        self.delete.triggered.connect(self.removerow)
        self.tv.doubleClicked.connect(self.update_data)
        self.update.triggered.connect(self.update_data)
        self.checkout.triggered.connect(self.cria_check_out)
        self.print.triggered.connect(self.imprime_lista)
        imprime_recibo.triggered.connect(lambda: self.imprime_recibo_grande(self.codfacturacao))
        imprime_checkin.triggered.connect(self.imprime_check_in)

    def cria_check_out(self):

        if self.current_id == "":
            QMessageBox.information(self, "Informação", "Escolha registo para fazer Check Out")
            return

        if self.estado == "OUT":
            QMessageBox.warning(self, "Info", "Registos com Check Out não podem ser alterados.")
            return

        if QDateTime.currentDateTime().toPyDateTime() < QDateTime.fromString(self.saida,
                                                                             'yyyy-MM-dd H:mm:ss').toPyDateTime():
            pergunta = QMessageBox.question(self, "Saída Antes do tempo", """O Checkout foi efectuado Antes do Tempo {saida}.\n
                O Que deseja fazer?\n
                1. Clica Yes (Sim) para cobrar apenas o tempo que hospedou.\n
                2. Clica Cancel (Cancelar) para cancelar a transação.""".format(entrada=self.entrada, saida=self.saida)
                                            , QMessageBox.Yes | QMessageBox.Cancel)
            if pergunta == QMessageBox.Yes:
                self.saida = QDateTime.currentDateTime().toString('yyyy-MM-dd H:mm:ss')
            if pergunta == QMessageBox.Cancel:
                return False
        elif QDateTime.currentDateTime().toPyDateTime() > QDateTime.fromString(self.saida, "dd-MMM-yyyy H:mm:ss").toPyDateTime():
            pergunta = QMessageBox.question(self, "Saída Depois do tempo", """O Cliente excedeu o tempo de Hospedagem {saida}.\n
                            O Que deseja fazer?\n
                            1. Clica Yes (Sim) para Cobrar todo periodo de {entrada} para {saida1}.\n
                            2. Clica No (Não) para cobrar o tempo até {saida}.\n
                            3. Clica Cancel (Cancelar) para cancelar a transação.""".format(entrada=self.entrada,
                                                                                            saida1=QDateTime.currentDateTime().toString("dd-MM-yyyy H:mm:ss"),
                                                                                            saida=self.saida)
                                            , QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

            if pergunta == QMessageBox.Yes:
                self.saida = QDateTime.currentDateTime().toString("yyyy-MM-dd H:mm:ss")
            else:
                return False

        quarto = self.quarto

        sql = """UPDATE check_in set estado=0, data_saida="{}" where cod={} """.format(self.saida, self.current_id)
        sql_quartos = """UPDATE quartos SET ocupado=0 WHERE cod={} """.format(quarto)
        # Desocupa o cliente
        sql_hospedes = """UPDATE hospedes SET estado=1 WHERE cod="{}" """.format(self.get_cod_hospede(self.hospede))

        self.cria_produtos()
        self.cur.execute(sql_quartos)
        self.cur.execute(sql_hospedes)
        self.cur.execute(sql)
        self.conn.commit()
        self.fill_table()
        QMessageBox.information(self, "Informação", "Check Out realizado com Sucesso!!!")

    def get_cod_hospede(self, hospede):
        sql = """SELECT cod from hospedes WHERE nome="{}" """.format(hospede)
        self.cur.execute(sql)
        data = self.cur.fetchall()
        return data[0][0]

    def create_statusbar(self):
        estado = QStatusBar(self)

        self.items = QLabel("Total Items: %s" % self.totalItems)
        estado.addWidget(self.items)
        estado.addWidget(self.iva_widget)
        self.setStatusBar(estado)

    def clickedslot(self, index):

        self.row = int(index.row())

        indice = self.tm.index(self.row, 0)
        self.current_id = indice.data()

        hospede = self.tm.index(self.row, 1)
        self.hospede = hospede.data()

        q = self.tm.index(self.row, 2)
        self.quarto = q.data()

        e = self.tm.index(self.row, 4)
        self.entrada = QDateTime.fromString(e.data(), 'dd-MMM-yyyy H:mm:ss').toString('yyyy-MM-dd H:mm:ss')

        s = self.tm.index(self.row, 5)
        self.saida = QDateTime.fromString(s.data(), 'dd-MMM-yyyy H:mm:ss').toString('yyyy-MM-dd H:mm:ss')

        estado = self.tm.index(self.row, 6)
        self.estado = estado.data()

        hos = self.tm.index(self.row, 8)
        self.cliente = hos.data()

        fact = self.tm.index(self.row, 9)
        self.codfacturacao = fact.data()

    def new_data(self):

        from check_in import Check_in
        cl = Check_in(self)

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

        if self.current_id == "":
            QMessageBox.warning(self, "Info", "Selecione o registo a actualizar na tabela")
            return

        if self.estado == "OUT":
            QMessageBox.warning(self, "Info", "Registos com Check Out não podem ser alterados")
            return

        from check_in import Check_in
        cl = Check_in(self)
        cl.codigo = int(self.current_id)
        cl.mostrar_registo(self.current_id)
        cl.enche_hospedes()
        cl.enche_quartos()
        cl.nome_hospede.addItem(self.hospede)
        cl.nome_hospede.setCurrentText(self.hospede)
        cl.quarto_numero.addItem(self.quarto)
        cl.setModal(True)
        cl.show()

    def removerow(self):

        if self.current_id == "":
            QMessageBox.information(self, "Info", "Selecione o registo a apagar na tabela")
            return

        if self.current_id != "CL20181111111":
            if QMessageBox.question(self, "Pergunta", str("Deseja eliminar o registo %s?") % self.current_id,
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                sql = """delete from check_in WHERE cod = "{codigo}" """.format(codigo=str(self.current_id))

                quarto = self.quarto
                sql_quartos = """UPDATE quartos SET ocupado=0 WHERE cod={} """.format(quarto)

                try:
                    self.cur.execute(sql_quartos)
                    self.cur.execute(sql)
                    self.conn.commit()
                    self.fill_table()
                    QMessageBox.information(self, "Sucesso", "Item apagado com sucesso...")
                except Exception as e:
                    QMessageBox.warning(self, "Erro", "Impossivel apagar quarto.")
        else:
            QMessageBox.warning(self, "Erro", "Check_in não pode ser apagado.")

    def imprime_lista(self):
        """Imprime no ecra a Lista geral de produtos baseado em um Critério"""
        if self.sql == "":
            return

        self.cur.execute(self.sql)
        dados = self.cur.fetchall()

        html = "<center> <h2> Lista de Hospedagens </h2> </center>"
        html += "<hr/>"

        html += "<br/>"

        html += "<table border=0 width = 80mm style='border: thin;'>"

        html += "<tr style='background-color:#c0c0c0;'>"
        html += "<th width = 45%>Hóspede</th>"
        html += "<th width = 5%>Quarto</th>"
        html += "<th width = 5%>valor</th>"
        html += "<th width = 10%>Entrada</th>"
        html += "<th width = 10%>Saída</th>"
        html += "<th width = 10%>Estado</th>"
        html += "<th width = 15%>Obs</th>"
        html += "</tr>"

        for cliente in dados:

            if cliente[6] == 0:
                check = "OUT"
            else:
                check = "IN"

            html += """<tr><td>{}</td> <td>{}</td> <td>{}</td> 
            <td align="right">{}</td> <td align="right">{}</td> 
            <td align="right">{}</td> 
            </tr>""".format(cliente[1], cliente[2], cliente[3], cliente[4], cliente[5],
                            check, cliente[7])
        html += "</table>"
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

    def imprime_recibo_grande_2(self, codigo):

        if self.codfacturacao == "":
            QMessageBox.warning(self, "Erro", "Escolha registo para imprimir na lista")
            return

        sql = """SELECT factura_geral.*, check_in_view.* FROM check_in_view 
        INNER JOIN factura_geral ON factura_geral.codfacturacao=check_in_view.codfacturacao 
        WHERE factura_geral.codfacturacao = '{}' """.format(codigo)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        print(data)

        if len(data) == 0:
            QMessageBox.warning(self, "Saída Antiga", "A Saída foi criada nume versão Anterior do Programa "
                                                      "e não pode ser reimprimida.")
            return

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

                data_entrada = ""
                data_saida = ""

            try:
                vencimento = datetime.datetime.strptime(str(data[0][33]), "%Y-%m-%d").strftime("%d-%m-%Y")
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
            targetfile = "ckeck_out.odt"

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

    def imprime_check_in(self):
        if self.current_id is None or self.current_id == "":
            QMessageBox.warning(self, "Erro", "Escolha o registo a imprimir na Tabela")
            return False

        from check_in import Check_in

        c = Check_in(self)
        c.impreme_entrada(self.current_id, self.hospede)

        return True

    def imprime_recibo_grande(self, codigo):

        if codigo == "":
            QMessageBox.warning(self, "Erro", "Escolha registo para imprimir na lista")
            return

        sql = """SELECT factura_geral.*, check_in_view.* FROM check_in_view 
        INNER JOIN factura_geral ON factura_geral.codfacturacao=check_in_view.codfacturacao 
        WHERE factura_geral.codfacturacao = '{}' """.format(codigo)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        print(data)

        if len(data) == 0:
            QMessageBox.warning(self, "Erro", "Não existem ainda dados da factura para "
                                              "esse cliente.\nFaça checkout primeiro.")
            return False

        html = """
            <table width="100%" height=100%>
                <tr>
                    <td>
                    < img src = '{}' width = "80" >
                    </td>
                </tr>
            </table>
            """.format(self.empresa_logo)

        html += "<hr/>"

        if self.parent() is not None:

            empresa_info = """ <table width="100%" style='border-style:solid 1px;border-width:0;'>
                            <tr> <td width="50%"> <h2> {} </h2> </td> </tr> 
                            <tr> <td> {} </td> </tr>
                            <tr> <td> {} </td> </tr>
                            <tr> <td> {} </td> </tr>
                        </table> 
                        """.format(self.empresa, self.empresa_endereco, self.empresa_nuit,
                                   self.empresa_contactos)

            html += """ <table width="100%" style="decimal.Decimal: right; border: 1 solid red;">
                <tr> <td> {} </td>  <td> {} </td> </tr>
             </table>""".format(empresa_info, "")
        else:
            html += "<center align='left'> [Nome da Empresa] </center>"
            html += "<center align='left'> [Endereco] </center>"
            html += "<center align='left'> [NUIT] </center>"
            html += "<center align='left'> [CONTACTOS] </center>"

        data_factura = str(data[0][3])
        sql = """select cod from documentos WHERE nome="{}" """.format(data[0][2])
        self.cur.execute(sql)
        dados = self.cur.fetchall()
        docs = ['DC20181111111', 'DC20182222222', 'DC20183333333']
        if dados[0][0] in docs:
            html += "<center align='left'> <h2 style='color: red;'> {}: {}/{}{} </h2> </center>".format(data[0][2], data[0][1],
                                                                                               data[0][23], data[0][22])
        else:
            html += "<center align='left'> <h2> {}: {}/{}{} </h2> </center>".format(data[0][2], data[0][1], data[0][23],
                                                                           data[0][22])

        html += "<center align='left'>DATA: {}</center>".format(data_factura)
        html += "<center align='left'>Operador: {}</center>".format(data[0][4])
        html += "<center align='left'>Exmo(a) Sr.(a): {}</center>".format(data[0][35])
        html += "<hr>"
        html += "<center align='left'>Check IN: {}</center>".format(
            QDateTime.fromString(self.entrada, 'yyyy-MM-dd H:mm:ss').toString('dd-MMM-yyyy H:mm:ss'))
        html += "<center align='left'>Check OUT: {}</center>".format(
            QDateTime.fromString(self.saida, 'yyyy-MM-dd H:mm:ss').toString('dd-MMM-yyyy H:mm:ss'))

        if data[0][11] != "":
            html += "<center align='left'>{}</center> ".format(data[0][11])

        if data[0][12] != "":
            html += "<center align='left'>NUIT: {}</center>".format(data[0][12])

        if data[0][13] != "":
            html += "<center align='left'>Contactos: {}</center>".format(data[0][13])

        html += "<hr/>"

        html += "<table border='0' width = 80mm style='border: 1px;'>"
        html += "<tr style='background-color: gray;'>"
        html += "<th width = 10% align='center'>Qt.</th>"
        html += "<th width = 60%>Descrição</th>"
        html += "<th width = 10% align='right'>Preco</th>"
        html += "<th width = 20% align='right'>Total</th>"
        html += "</tr>"

        for cliente in data:
            html += """<tr> <td align='center'>{}</td>  <td>{}</td>  <td align="right">{}</td>  
            <td align="right">{}</td> </tr>
            """.format(cliente[16], cliente[15], cliente[17], cliente[21])

        html += "</table>"

        html += "<hr/>"

        html += "<table border='0' width = '100%' style='border: 1px;'>"
        html += "<tr>"
        html += "<th width = 10% align='center'></th>"
        html += "<th width = 60%></th>"
        html += "<th width = 10% >TOTAL</th>"
        html += "<th width = 20% align='right'>{:20,.{casas}f}</th>".format(cliente[8],
                                                                            casas=self.empresa_casas_decimais)
        html += "</tr>"

        html += "</table>"

        html += "<hr/>"
        html += "<center align='left'> {}</center>".format(self.contas)
        html += "<center align='left'> Processado por Computador"

        document = QTextDocument()

        document.setHtml(html)
        dlg = QPrintPreviewDialog(self)

        dlg.paintRequested.connect(document.print_)
        dlg.showMaximized()
        dlg.exec_()

    # Método que incrimenta documentos baseando no ano.
    def incrimenta(self, ano, coddocumento):
        sql = """select max(numero) from facturacao WHERE ano={ano} and 
        coddocumento="{coddoc}" """.format(ano=ano, coddoc=coddocumento)

        try:
            self.cur.execute(sql)
            data = self.cur.fetchall()
        except Exception as e:
            return

        if data[0][0] is None:
            self.numero = 1
        else:
            self.numero = data[0][0] + 1

    def grava_facturacao(self):
        
        dias = Decimal(self.get_dias(self.entrada, self.saida))
        v_quarto = self.get_preco(self.quarto)

        if self.sem_iva.isChecked():
            subtotal = Decimal(dias) * v_quarto
            total = Decimal(dias) * v_quarto
            iva = Decimal(0)
        elif self.iva_incluso.isChecked():
            total = Decimal(dias) * v_quarto
            iva = total - total / Decimal(1.17)
            subtotal = total - iva
        else:
            iva = Decimal(dias) * v_quarto * Decimal(.17)
            subtotal = Decimal(dias) * v_quarto
            total = subtotal + iva

        subtotal = str(subtotal)
        total = str(total)

        self.incrimenta(ANO_ACTUAL, self.coddocumento)
        data = QDateTime.currentDateTime().toString('yyyy-MM-dd H:mm:ss')
        custo = 0
        desconto = 0
        taxa = str(iva)
        lucro = 0
        debito = 0
        credito = 0
        saldo = 0
        troco = 0
        banco = 0
        cash = 0
        transferencia = 0
        estado = 1
        extenso = ""
        ano = ANO_ACTUAL
        mes = MES
        finalizado = 1
        caixa = self.caixa_numero
        pago = 0
        comissao = 0
        pagamento = 0
        created_by = self.user
        modified_by = self.user

        created = QDateTime.currentDateTime().toString("yyyy-MM-dd H:mm:ss")
        modified = created

        obs = "Criada pela gestao hoteleira"
        cliente = "CL20181111111"

        if self.existe_facturacao(self.codfacturacao) is True:
            sql_facturacao = """UPDATE facturacao SET codcliente="{cliente}", data="{data}", subtotal="{subtotal}",
                    taxa="{taxa}", total="{total}" WHERE cod="{cod}" """.format(cliente=cliente, data=data,
                                                                                subtotal=subtotal, taxa=taxa,
                                                                                total=total, cod=self.codfacturacao)
        else:
            facturacao_values = (self.codfacturacao, self.numero, self.coddocumento, cliente, data, custo, subtotal,
                                 desconto, taxa, total, lucro, debito, credito, saldo, troco,
                                 banco, cash, transferencia, estado, extenso, ano, mes, obs,
                                 created, modified, modified_by, created_by, finalizado, caixa,
                                 pago, comissao, pagamento)

            sql_facturacao = """INSERT INTO facturacao (cod, numero, coddocumento, codcliente, data, custo, subtotal, desconto, 
                                                   taxa, total, lucro, debito, credito, saldo, troco, banco, cash, tranferencia, estado, extenso, ano, mes, 
                                                   obs, created, modified, modified_by, created_by, finalizado, caixa, pago, comissao, pagamento) 
                                                   VALUES {} """.format(facturacao_values)

        print(sql_facturacao)
        self.cur.execute(sql_facturacao)

    def existe_facturacao(self, cod):
        sql = """SELECT cod from facturacao WHERE cod="{}" """.format(cod)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return True
        else:
            return False

    def get_cod_cliente(self, nome):

        sql = """SELECT cod from clientes WHERE nome="{}" """.format(nome)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        cliente = ""

        if len(data) > 0:
            cliente = data[0][0]

        return cliente

    def cria_produtos(self):

        print("Criando a VD/FACTURA...")
        self.grava_facturacao()
        print("Criando a produtos para a cotacao...")
        self.grava_detalhes()
        print("Gravado com sucesso")
        print("Imprimindo Recibo")
        self.imprime_recibo_grande(self.codfacturacao)

    def grava_detalhes(self):

        if self.sem_iva.isChecked():
            subtotal = self.valor_do_quarto
            total = self.valor_do_quarto
            iva = Decimal(0)
        elif self.iva_incluso.isChecked():
            total = self.valor_do_quarto
            iva = total - total / Decimal(1.17)
            subtotal = total - iva
        else:
            iva = self.valor_do_quarto * Decimal(.17)
            subtotal = self.valor_do_quarto
            total = subtotal + iva

        subtotal = str(subtotal)
        total = str(total)
        taxa = str(iva)

        dias = self.get_dias(self.entrada, self.saida)

        print("imprimido dias: ", dias)
        for x in range(int(dias)):
            data = QDateTime.fromString(self.entrada, "yyyy-MM-dd H:mm:ss").addDays(x).toString("dd-MM-yyyy")

            print("Alojamento e Pequeno Almoço do dia {}".format(data))
            self.nome_produto = "Alojamento/Hospedagem do dia {}".format(data)

            print("Armazem: ", self.codarmazem)
            if self.existe_produto(self.nome_produto) is False:
                self.grava_produto()
                print("Produto nao existe: ", self.codproduto)
            else:
                self.codproduto = self.get_cod_produto(self.nome_produto)
                print("Produto Existe: ", self.codproduto)

            detalhes_values = (self.codfacturacao, self.codproduto, 0, subtotal, 1,
                               subtotal, 0, taxa, total,
                               0, self.codarmazem)

            if self.existe_produto_facturacao(self.codfacturacao, self.codproduto) is True:
                print("Actualizando produtos na facturacaodetalhe...")
                detalhe_sql = """UPDATE facturacaodetalhe SET preco={}, subtotal={}, taxa={}, total={} 
                            WHERE codfacturacao="{}" """.format(subtotal, subtotal, taxa, total, self.codfacturacao)

            else:
                print("Inserindo produtos na facturacaodetalhe...")
                detalhe_sql = """INSERT INTO facturacaodetalhe (codfacturacao, codproduto, custo, preco, 
                                            quantidade, subtotal, desconto, taxa, total, lucro, 
                                            codarmazem) VALUES {} """.format(
                    detalhes_values)

            print(detalhe_sql)
            self.cur.execute(detalhe_sql)

    def existe_produto_facturacao(self, codfacturacao, codproduto):
        sql = """SELECT cod fro FROM facturacaodetalhe WHERE codfacturacao="{}" 
        AND codproduto="{}" """.format(codfacturacao, codproduto)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            return True
        else:
            return False

    def get_cod_produto(self, nome):
        sql = """select cod, preco, custo, foto, nome, quantidade from produtos WHERE nome = "{nome}"
        """.format(nome=nome)

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        produto = ""

        if len(data) > 0:
            produto = data[0][0]

        return produto

    def existe_produto(self, nome):

        sql = """SELECT cod from produtos WHERE nome = "{nome}" """.format(nome=nome)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            self.novo_produto = True
            return False
        else:
            self.novo_produto = False
            codigo = ''.join(data[0])
            self.codigo = codigo
            return True

    def grava_produto(self):

        self.codproduto = "PR" + cd("abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789")
        quantidade = Decimal(1)
        created = QDateTime.currentDateTime().toString('yyyy-MM-dd H:mm:ss')
        modified = QDateTime.currentDateTime().toString('yyyy-MM-dd H:mm:ss')
        foto = ""
        nome = self.nome_produto
        tipo = 1
        cod_barras = ""
        familia = "FM20181111111"
        subfamilia = "SF20181111111"
        custo = Decimal(0)
        preco = Decimal(self.valor_do_quarto)
        preco1 =  Decimal(0)
        preco2 =  Decimal(0)
        preco3 =  Decimal(0)
        preco4 =  Decimal(0)
        unidade = "un"
        quantidade_m = Decimal(0)
        quantidade_max = Decimal(0)
        estado = 1
        obs = ""
        cod_taxa = "TX20182222222"

        if self.parent() is not None:
            codarmazem = self.codarmazem
            modified_by = self.user
            created_by = self.user

            values = """ "{cod}", "{nome}", "{cod_barras}", {tipo},"{familia}", "{subfamilia}", {custo}, {preco}, 
                        preco1={preco1}, preco2={preco2}, preco3={preco3}, preco4={preco4},
                        {quantidade}, {quantidade_m}, "{unidade}", "{obs}", {estado}, "{created}", "{modified}", 
                        "{modified_by}", "{created_by}", "{foto}", "{taxa}", {quantidade_max}
                        """.format(cod=self.codproduto, nome=nome, tipo=tipo, cod_barras=cod_barras, familia=familia,
                                   subfamilia=subfamilia,
                                   custo=custo, preco=preco, preco1=preco1, preco2=preco2, preco3=preco3, preco4=preco4,
                                   quantidade=quantidade, quantidade_m=quantidade_m, unidade=unidade, obs=obs,
                                   estado=estado, created=created, modified=modified, modified_by=modified_by,
                                   created_by=created_by, foto=foto, taxa=cod_taxa, quantidade_max=quantidade_max)

            sql_detalhes = """INSERT INTO produtosdetalhe (codproduto, codarmazem, quantidade, created, modified, 
                        modified_by, created_by) VALUES ("{codproduto}", "{codarmazem}", {quantidade}, "{created}", "{modified}", 
                        "{modified_by}", "{created_by}")""".format(codproduto=self.codproduto, codarmazem=codarmazem,
                                                                   quantidade=quantidade, created=created,
                                                                   modified=modified,
                                                                   modified_by=modified_by, created_by=created_by)

            sql = """INSERT INTO produtos (cod, nome, cod_barras, tipo, codfamilia, codsubfamilia, custo, preco,  preco1, 
                        preco2,  preco3,  preco4, quantidade, quantidade_m, unidade, obs, estado, created, modified, 
                        modified_by, created_by, foto, codtaxa, quantidade_max) values({value})""".format(
                value=values)

        self.cur.execute(sql)
        self.cur.execute(sql_detalhes)

    def get_dias(self, d_entrada, d_saida):

        print(d_entrada, d_saida)
        entrada = QDateTime.fromString(d_entrada, "yyyy-MM-dd H:mm:ss" ).toPyDateTime()
        saida = QDateTime.fromString(d_saida, "yyyy-MM-dd H:mm:ss").toPyDateTime()

        diff = saida - entrada
        dias = int(diff.days)

        if dias in (0, 1) or dias < 0:
            dias = 1

        return dias

    def get_preco(self, cod):

        sql = """SELECT preco from quartos WHERE cod={}""".format(int(cod))
        self.cur.execute(sql)

        data = self.cur.fetchall()

        if len(data) > 0:
            preco = float(data[0][0])
            self.valor_do_quarto = Decimal(preco)

        return self.valor_do_quarto


if __name__ == '__main__':

    app = QApplication(sys.argv)
#
    helloPythonWidget = ListaCheckIN()
    helloPythonWidget.show()
#
    sys.exit(app.exec_())