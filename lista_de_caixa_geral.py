import sys
import decimal

from PyQt5.QtWidgets import (QApplication, QTableView, QAbstractItemView, QMessageBox, QToolBar, QLineEdit, QLabel,
                             QStatusBar, QAction, QMainWindow, qApp, QDateEdit, QHBoxLayout, QCalendarWidget,
                             QGroupBox, QRadioButton)

from PyQt5.QtGui import QIcon, QTextDocument
from PyQt5.QtCore import Qt, QSizeF, QDateTime, QDate
import sqlite3 as lite
from caixa import caixa
from sortmodel import MyTableModel
from datetime import datetime
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrinterInfo, QPrintPreviewDialog


agora = datetime.today()

DB_FILENAME = 'dados.tsdb'


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # controla o codigo
        self.current_id = ""

        # Connect the Database
        if self.parent() is None:
            self.db = self.connect_db()
            self.user = ""
        else:
            self.conn = self.parent().conn
            self.cur = self.parent().cur
            self.user = self.parent().user

        # Create the main user interface
        self.ui()

        # Search the data
        self.fill_table()
        self.find_w.textEdited.connect(self.fill_table)
        self.data_inicial.dateChanged.connect(self.fill_table)
        self.data_final.dateChanged.connect(self.fill_table)
        self.todas_caixas.clicked.connect(self.fill_table)
        self.todas_abertas.clicked.connect(self.fill_table)
        self.todas_fechadas.clicked.connect(self.fill_table)

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

        self.setWindowTitle("Gestão de Caixa")

    def focusInEvent(self, evt):
        self.fill_table()

    def connect_db(self):
        # Connect to database and retrieves data
        try:
            self.conn = lite.connect(DB_FILENAME)
            self.cur = self.conn.cursor()

        except Exception as e:
            return
            sys.exit(True)

    def fill_table(self):

        if QDate(self.data_inicial.date()) > QDate(self.data_final.date()):
            self.data_inicial.setDate(self.data_final.date())

        header = [qApp.tr('Código'), qApp.tr('Valor Inicial'), qApp.tr('Receitas'), qApp.tr('Despesas'),
                  qApp.tr('Estado'), qApp.tr('Data de abertura'), qApp.tr('data de fecho'),
                  qApp.tr('Fechada por'), qApp.tr('Aberta Por'), qApp.tr('Observações'), "Armazem"]

        datainicial = QDate(self.data_inicial.date()).toString('yyyy-MM-dd')
        datafinal = QDate(self.data_final.date()).toString('yyyy-MM-dd')


        self.sql = """select * from caixa WHERE (estado=0 or estado=1) and (created BETWEEN 
        '{data1}' and '{data2}') and 
        (created_by like "%{user1}%" or modified_by like "%{user1}%") """.format(user1=self.find_w.text(),
                                                                                 data1=datainicial, data2=datafinal)

        if self.todas_fechadas.isChecked() is True:
            self.sql = """select * from caixa WHERE estado=1 and (created BETWEEN '{data1}' and '{data2}') and 
            (created_by like "%{user1}%" or modified_by like "%{user1}%")""".format(user1=self.find_w.text(),
                                                                                    data1=datainicial, data2=datafinal)

        if self.todas_abertas.isChecked() is True:
            self.sql = """select * from caixa WHERE estado=0 and (created BETWEEN '{data1}' and '{data2}') and 
            (created_by like "%{user1}%" or modified_by like "%{user1}%")""".format(user1=self.find_w.text(),
                                                                                    data1=datainicial, data2=datafinal)
        self.cur.execute(self.sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        if len(data) == 0:
            self.tabledata = ["", "", "", "", "", "", "", "", "", "", ""]
        else:
            self.tabledata = data
        try:
            self.tm = MyTableModel(self.tabledata, header, self)
            # set the table model
            self.totalItems = self.tm.rowCount(self)
            self.tv.setModel(self.tm)
        except Exception as e:
            print(e)
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

        data_inicial = QLabel('De:')
        data_final = QLabel('A:')
        self.data_inicial = QDateEdit()
        self.data_inicial.setDate(QDate.currentDate().addDays(-30))
        self.data_final = QDateEdit()
        self.data_final.setDate(QDate.currentDate())
        self.todas_caixas = QRadioButton("Mostrar todas caixas")
        self.todas_fechadas = QRadioButton("Mostrar Fechadas")
        self.todas_abertas= QRadioButton("Mostrar Aberta")

        self.todas_caixas.setChecked(True)

        calendario = QCalendarWidget()
        self.data_inicial.setCalendarWidget(calendario)
        self.data_inicial.setCalendarPopup(True)
        self.data_final.setCalendarWidget(calendario)
        self.data_final.setCalendarPopup(True)

        vlay = QHBoxLayout()
        vlay.addWidget(data_inicial)
        vlay.addWidget(self.data_inicial)
        vlay.addWidget(data_final)
        vlay.addWidget(self.data_final)
        vlay.addWidget(self.todas_caixas)
        vlay.addWidget(self.todas_fechadas)
        vlay.addWidget(self.todas_abertas)
        datas = QGroupBox()
        datas.setLayout(vlay)

        self.new = QAction(QIcon('./icons/add_2.ico'), qApp.tr("Abrir/Actualizar Caixa"), self)
        self.delete = QAction(QIcon('./icons/print.ico'), qApp.tr("Ver/Imprimir Caixa anterior"), self)
        self.print = QAction(QIcon('./images/fileprint.png'), qApp.tr("Feachar Caixa currente"), self)
        self.update = QAction(QIcon('./icons/Search.ico'), qApp.tr("Imprimir/Visualizar Caixa baseando em datas"), self)

        tool = QToolBar()
        tool.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        tool.setContextMenuPolicy(Qt.PreventContextMenu)

        tool.addWidget(find)
        tool.addWidget(self.find_w)
        tool.addSeparator()
        tool.addWidget(datas)
        tool.addSeparator()
        tool.addAction(self.new)
        tool.addAction(self.update)
        tool.addSeparator()
        tool.addAction(self.delete)
        tool.addSeparator()
        tool.addAction(self.print)

        tool.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        self.addToolBarBreak(Qt.BottomToolBarArea)
        self.addToolBar(tool)

        ######################################################################
        self.new.triggered.connect(self.update_data)
        self.delete.triggered.connect(lambda: self.imprime_caixa(self.current_id))
        # self.tv.doubleClicked.connect(self.update_data)
        # self.update.triggered.connect(self.update_data)
        # self.connect(self.delete, SIGNAL("triggered()"), self.removerow)
        # # self.connect(self.update, SIGNAL("triggered()"), self.updatedata)
        self.print.triggered.connect(self.fechar_caixa)
        self.update.triggered.connect(self.imprime_lista_caixa)

    def create_statusbar(self):
        estado = QStatusBar(self)
    
        self.items = QLabel("Total Items: %s" % self.totalItems)
        estado.addWidget(self.items)
        self.setStatusBar(estado)

    def clickedslot(self, index):

        self.row = int(index.row())

        indice= self.tm.index(self.row, 0)
        self.current_id = indice.data()

    def new_data(self):

        cl = caixa(self)
        cl.setModal(True)
        cl.show()

    def update_data(self):

        sql = "select cod from caixa WHERE estado=0"
        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        if len(data) > 0:
            cl = caixa(self)
            cl.cod.setText(data[0][0])
            cl.mostrar_registo()
            cl.setModal(True)
            cl.show()

    def removerow(self):
    
        if self.current_id == "":
            QMessageBox.information(self, "Info", "Selecione o registo a apagar na tabela")
            return
        
        if QMessageBox.question(self, "Pergunta", str("Deseja eliminar o registo %s?") % self.current_id,
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            sql = """delete from caixa WHERE cod = "{codigo}" """.format(codigo=str(self.current_id))
            self.cur.execute(sql)
            self.conn.commit()
            self.fill_table()
            QMessageBox.information(self, "Sucesso", "Item apagado com sucesso...")

    def fechar_caixa_cod(self, coddigo):

        dia = QDateTime.toString()

        sql = """ UPDATE caixa set estado=1, modified="{}", modified_by="{}" WHERE cod = '{}' and estado=0 
         """.format(coddigo, dia, self.parent().user)

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        if len(data) > 0:
            self.conn.commit()
            QMessageBox.information(self, "Sucesso", "Caixa Fechada c1om sucesso!")
            return True
        else:
            QMessageBox.warning(self, "Erro", "Caixa já está Fechada.")
            return False

    def fechar_caixa(self):

        if QMessageBox.question(self, "Fecho de Caixa", "Deseja Fazer o fecho de Caixa?") == QMessageBox.No:
            return

        dia = QDate.currentDate().toString('yyyy-MM-dd')

        sql = """ UPDATE caixa set estado=1, modified="{}", modified_by="{}" WHERE estado=0 
         """.format(dia, self.parent().user)

        sql2 = "SELECT cod FROM caixa WHERE estado=0"
        self.cur.execute(sql2)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        if len(data) > 0:
            caixa = data[0][0]

            try:
                self.cur.execute(sql)
                self.conn.commit()
                QMessageBox.information(self, "Sucesso", "Caixa Fechada com sucesso!")
                self.imprime_caixa(caixa)

            except Exception as e:
                QMessageBox.critical(self, "Erro", "Aconteceu um erro no fecho da caixa. Tente mais tarde.")
        else:
            QMessageBox.warning(self, "Erro", "Nenhuma caixa aberta.")

    def imprime_caixa(self, cod_caixa):

        # sql = """SELECT * FROM FECHO_CAIXA WHERE cod = '{}' """.format(numero_caixa)

        if cod_caixa == "":
            return

        sql = """SELECT * FROM FECHO_CAIXA WHERE doc = 'DC20181111111' and caixa_numero = '{}' 
        order by numero""".format(cod_caixa)

        self.cur.execute(sql)
        data = self.cur.fetchall()
        # data = [tuple(str(item) for item in t) for t in lista]

        if len(data) == 0:
            return

        # LOGOTIPO
        html = """
                               < table
                                   width = "100%" >
                                   < tr >
                                       < td > 
                                       < img src = '{}' width = "80" > 
                                       < / td >
                                   </ tr >
                               < / table > 
                               """.format(self.parent().empresa_logo)

        if self.parent() is not None:
            html += "<center> {} </center>".format(self.parent().empresa)
            html += "<center> {} </center>".format(self.parent().empresa_endereco)
            html += "<center> NUIT: {} </center>".format(self.parent().empresa_nuit)
            html += "<center> Contactos: {} </center>".format(self.parent().empresa_contactos)
        else:
            html += "<center> [Nome da Empresa] </center>"
            html += "<center> [Endereco] </center>"
            html += "<center> [NUIT] </center>"
            html += "<center> [CONTACTOS] </center>"

        html += "<p align='right'>Data de Impressão: {}</p>".format(agora)
        html += "<p align='right'>Data de abertura: {}</p>".format(data[0][5])
        html += "<p align='right'>Data de Fecho: {}</p>".format(data[0][6])
        html += "<p align='right'>Aberta por: {}</p>".format(data[0][3])
        html += "<p align='right'>Fechada Por: {}</p>".format(data[0][4])

        html += "<hr/>"

        subtotal_geral = decimal.Decimal(0.00)
        taxa_geral = decimal.Decimal(0.00)
        desconto_geral = decimal.Decimal(0.00)
        total_geral = decimal.Decimal(0.00)

        html += "<table border='0' width = 80mm style='border: thin;'> " \
                "<tr> <td> VENDAS  A DINHEIRO </tr> </td> </table>"
        html += "<table border='0' width = 80mm style='border: thin;'>"

        html += "<tr style='background-color:#c0c0c0;'>"
        # html += "<th width = 10%>DOC</th>"
        html += "<th width = 5%>Numero</th>"
        html += "<th width = 10%>POS</th>"
        html += "<th width = 15%>Cash</th>"
        html += "<th width = 10%>Cheque</th>"
        html += "<th width = 20%>Subtotal</th>"
        html += "<th width = 10%>Desconto</th>"
        html += "<th width = 10%>IVA</th>"
        html += "<th width = 20%>TOTAL</th>"
        html += "</tr>"

        for cliente in data:
            # se o documento näo estiver cancelado / activa = 1
            if int(cliente[18]) == 1:

                subtotal_geral += decimal.Decimal(cliente[10])
                taxa_geral += decimal.Decimal(cliente[11])
                desconto_geral += decimal.Decimal(cliente[12])
                total_geral += decimal.Decimal(cliente[13])

                html += """<tr>  <td>{}</td>  <td>{}</td>  <td align="right">{}</td>
                                               <td align="right">{}</td> <td align="right">{}</td> 
                                               <td align="right">{}</td>
                                               <td align="right">{}</td> <td align="right">{}</td> 
                                               </tr>
                                               """.format(cliente[8], cliente[16], cliente[15], cliente[14],
                                                          cliente[10],
                                                          cliente[12], cliente[11], cliente[13])
            else:

                html += """<tr style="background-color:red;">  <td>{}</td>  <td>{}</td>  <td align="right">{}</td>
                                                                                        <td align="right">{}</td> <td align="right">{}</td> <td align="right">{}</td>
                                                                                        <td align="right">{}</td> <td align="right">{}</td> 
                                                                                        </tr>
                                                                                            """.format(cliente[8],
                                                                                                       cliente[16],
                                                                                                       cliente[15],
                                                                                                       cliente[14],
                                                                                                       cliente[10],
                                                                                                       cliente[12],
                                                                                                       cliente[11],
                                                                                                       cliente[13])
        html += "<tr> <td></td> <td></td> <td></td> <td></td> <td align='right'>" \
                "<b>{}</b></td> <td align='right'><b>{}</b></td> " \
                "<td align='right'><b>{}</b></td> " \
                "<td align='right'><b>{}</b></td> </tr> ".format(subtotal_geral, taxa_geral,
                                                                        desconto_geral, total_geral)
        html += "</table>"

        html += "</br>"

        ###########################################################################################################
        ###############################################ZONA DAS FACTURAS###########################################
        ###########################################################################################################
        subtotal_geral = decimal.Decimal(0.00)
        taxa_geral = decimal.Decimal(0.00)
        desconto_geral = decimal.Decimal(0.00)
        total_geral = decimal.Decimal(0.00)

        sql = """SELECT * FROM FECHO_CAIXA WHERE doc = 'DC20182222222' and caixa_numero = '{}' """.format(cod_caixa)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        html += "<table border='0' width = 80mm style='border: thin;'> " \
                "<tr> <td> FACTURAS </tr> </td> </table>"

        html += "<table border='0' width = 80mm style='border: thin;'>"

        html += "<tr style='background-color:#c0c0c0;'>"
        # html += "<th width = 10%>DOC</th>"
        html += "<th width = 5%>Numero</th>"
        html += "<th width = 10%>POS</th>"
        html += "<th width = 15%>Cash</th>"
        html += "<th width = 10%>Cheque</th>"
        html += "<th width = 20%>Subtotal</th>"
        html += "<th width = 10%>Desconto</th>"
        html += "<th width = 10%>IVA</th>"
        html += "<th width = 20%>TOTAL</th>"
        html += "</tr>"

        for cliente in data:
            # se o documento näo estiver cancelado / activa = 1
            if int(cliente[18]) == 1:

                subtotal_geral += decimal.Decimal(cliente[10])
                taxa_geral += decimal.Decimal(cliente[11])
                desconto_geral += decimal.Decimal(cliente[12])
                total_geral += decimal.Decimal(cliente[13])

                html += """<tr>  <td>{}</td>  <td>{}</td>  <td align="right">{}</td>
                                                              <td align="right">{}</td> <td align="right">{}</td> 
                                                              <td align="right">{}</td>
                                                              <td align="right">{}</td> <td align="right">{}</td> 
                                                              </tr>
                                                                  """.format(cliente[8], cliente[16], cliente[15],
                                                                             cliente[14],
                                                                             cliente[10],
                                                                             cliente[12], cliente[11], cliente[13])
            else:

                html += """<tr style="background-color:red;">  <td>{}</td>  <td>{}</td>  <td align="right">{}</td>
                                                                                                       <td align="right">{}</td> <td align="right">{}</td> <td align="right">{}</td>
                                                                                                       <td align="right">{}</td> <td align="right">{}</td> 
                                                                                                       </tr>
                                                                                                           """.format(
                    cliente[8],
                    cliente[16],
                    cliente[15],
                    cliente[14],
                    cliente[10],
                    cliente[12],
                    cliente[11],
                    cliente[13])
        html += "<tr> <td></td> <td></td> <td></td> <td></td> <td align='right'>" \
                "<b>{}</b></td> <td align='right'><b>{}</b></td> " \
                "<td align='right'><b>{}</b></td> " \
                "<td align='right'><b>{}</b></td> </tr> ".format(subtotal_geral, taxa_geral,
                                                                        desconto_geral, total_geral)
        html += "</table>"

        ###########################################################################################################
        ###############################################ZONA DOS RECIBOS############################################
        ###########################################################################################################
        html += "</br>"

        total_geral = decimal.Decimal(0.00)

        recibo_sql = """select recibos.numero, recibos.tranferencia, recibos.cash, recibos.banco, recibos.total, 
                                  recibos.estado from recibos INNER JOIN caixa on caixa.cod=recibos.caixa 
                                  WHERE caixa.cod = '{}' """.format(cod_caixa)

        self.cur.execute(recibo_sql)
        recibo_data = self.cur.fetchall()

        if len(recibo_data) > 0:

            html += "<table border='0' width = 80mm style='border: thin;'> " \
                    "<tr> <td> RECIBOS </tr> </td> </table>"

            html += "<table border='0' width = 80mm style='border: thin;'>"

            html += "<tr style='background-color:#c0c0c0;'>"
            # html += "<th width = 10%>DOC</th>"
            html += "<th width = 20%>Numero</th>"
            html += "<th width = 20%>POS</th>"
            html += "<th width = 20%>Cash</th>"
            html += "<th width = 20%>Cheque</th>"
            html += "<th width = 20%>TOTAL</th>"
            html += "</tr>"

            for cliente in recibo_data:
                # se o documento näo estiver cancelado / activa = 1
                if int(cliente[5]) == 1:

                    total_geral += decimal.Decimal(cliente[4])

                    html += """<tr>  <td>{}</td> <td align="right">{}</td> 
                                                                             <td align="right">{}</td>
                                                                             <td align="right">{}</td> <td align="right">{}</td> 
                                                                             </tr>
                                                                                 """.format(cliente[0], cliente[1],
                                                                                            cliente[2],
                                                                                            cliente[3],
                                                                                            cliente[4])
                else:

                    html += """<tr style="background-color:red;">  <td>{}</td> <td align="right">{}</td> <td align="right">{}</td>
                                                                                            <td align="right">{}</td> <td align="right">{}</td> 
                                                                                            </tr>
                                                                                                """.format(cliente[0],
                                                                                                           cliente[1],
                                                                                                           cliente[2],
                                                                                                           cliente[3],
                                                                                                           cliente[4])
        html += "<tr> <td></td> <td></td> <td></td> <td></td>" \
                "<td align='right'><b>{}</b></td>  </tr> ".format(total_geral)
        html += "</table>"

        document = QTextDocument()

        document.setHtml(html)

        dlg = QPrintPreviewDialog(self)
        dlg.paintRequested.connect(document.print_)
        dlg.showMaximized()
        dlg.exec_()

    def imprime_lista_caixa(self):

        sql = """SELECT * FROM FECHO_CAIXA WHERE abertura BETWEEN '{}' and '{}' 
        and doc = 'DC20181111111' order by numero""".format(self.data_inicial.date().toString('yyyy-MM-dd'),
                                                            self.data_final.date().toString('yyyy-MM-dd'))

        self.cur.execute(sql)
        data = self.cur.fetchall()
        # data = [tuple(str(item) for item in t) for t in lista]

        if len(data) == 0:
            return

        # LOGOTIPO
        html = """
                       < table
                           width = "100%" >
                           < tr >
                               < td > 
                               < img src = '{}' width = "80" > 
                               < / td >
                           </ tr >
                       < / table > 
                       """.format(self.parent().empresa_logo)

        if self.parent() is not None:
            html += "<center> {} </center>".format(self.parent().empresa)
            html += "<center> {} </center>".format(self.parent().empresa_endereco)
            html += "<center> NUIT: {} </center>".format(self.parent().empresa_nuit)
            html += "<center> Contactos: {} </center>".format(self.parent().empresa_contactos)
        else:
            html += "<center> [Nome da Empresa] </center>"
            html += "<center> [Endereco] </center>"
            html += "<center> [NUIT] </center>"
            html += "<center> [CONTACTOS] </center>"

        html += "<p align='right'>Data de Impressão: {}</p>".format(agora)
        html += "<p align='right'>Data de abertura: {}</p>".format(data[0][5])
        html += "<p align='right'>Data de Fecho: {}</p>".format(data[0][6])
        html += "<p align='right'>Aberta por: {}</p>".format(data[0][3])
        html += "<p align='right'>Fechada Por: {}</p>".format(data[0][4])

        html += "<hr/>"

        subtotal_geral = decimal.Decimal(0.00)
        taxa_geral = decimal.Decimal(0.00)
        desconto_geral = decimal.Decimal(0.00)
        total_geral = decimal.Decimal(0.00)

        html += "<table border='0' width = 80mm style='border: thin;'> " \
                "<tr> <td> VENDAS  A DINHEIRO </tr> </td> </table>"
        html += "<table border='0' width = 80mm style='border: thin;'>"

        html += "<tr style='background-color:#c0c0c0;'>"
        # html += "<th width = 10%>DOC</th>"
        html += "<th width = 5%>Numero</th>"
        html += "<th width = 10%>POS</th>"
        html += "<th width = 15%>Cash</th>"
        html += "<th width = 10%>Cheque</th>"
        html += "<th width = 20%>Subtotal</th>"
        html += "<th width = 10%>Desconto</th>"
        html += "<th width = 10%>IVA</th>"
        html += "<th width = 20%>TOTAL</th>"
        html += "</tr>"

        for cliente in data:
            # se o documento näo estiver cancelado / activa = 1
            if int(cliente[18]) == 1:

                subtotal_geral += decimal.Decimal(cliente[10])
                taxa_geral += decimal.Decimal(cliente[11])
                desconto_geral += decimal.Decimal(cliente[12])
                total_geral += decimal.Decimal(cliente[13])

                html += """<tr>  <td>{}</td>  <td>{}</td>  <td align="right">{}</td>
                                       <td align="right">{}</td> <td align="right">{}</td> 
                                       <td align="right">{}</td>
                                       <td align="right">{}</td> <td align="right">{}</td> 
                                       </tr>
                                       """.format(cliente[8], cliente[16], cliente[15], cliente[14], cliente[10],
                                                  cliente[12], cliente[11], cliente[13])
            else:

                html += """<tr style="background-color:red;">  <td>{}</td>  <td>{}</td>  <td align="right">{}</td>
                                                                                <td align="right">{}</td> <td align="right">{}</td> <td align="right">{}</td>
                                                                                <td align="right">{}</td> <td align="right">{}</td> 
                                                                                </tr>
                                                                                    """.format(cliente[8],
                                                                                               cliente[16],
                                                                                               cliente[15],
                                                                                               cliente[14],
                                                                                               cliente[10],
                                                                                               cliente[12],
                                                                                               cliente[11],
                                                                                               cliente[13])
        html += "<tr> <td></td> <td></td> <td></td> <td></td> <td align='right'>" \
                "<b>{}</b></td> <td align='right'><b>{}</b></td> " \
                "<td align='right'><b>{}</b></td> " \
                "<td align='right'><b>{}</b></td> </tr> ".format(subtotal_geral, taxa_geral,
                                                                        desconto_geral, total_geral)
        html += "</table>"

        html += "</br>"

        ###########################################################################################################
        ###############################################ZONA DAS FACTURAS###########################################
        ###########################################################################################################
        subtotal_geral = decimal.Decimal(0.00)
        taxa_geral = decimal.Decimal(0.00)
        desconto_geral = decimal.Decimal(0.00)
        total_geral = decimal.Decimal(0.00)

        sql = """SELECT * FROM FECHO_CAIXA WHERE abertura BETWEEN '{}' and '{}' 
                           and doc = 'DC20182222222' """.format(self.data_inicial.date().toString('yyyy-MM-dd'),
                                                                self.data_final.date().toString('yyyy-MM-dd'))

        self.cur.execute(sql)
        data = self.cur.fetchall()

        html += "<table border='0' width = 80mm style='border: thin;'> " \
                "<tr> <td> FACTURAS </tr> </td> </table>"

        html += "<table border='0' width = 80mm style='border: thin;'>"

        html += "<tr style='background-color:#c0c0c0;'>"
        # html += "<th width = 10%>DOC</th>"
        html += "<th width = 5%>Numero</th>"
        html += "<th width = 10%>POS</th>"
        html += "<th width = 15%>Cash</th>"
        html += "<th width = 10%>Cheque</th>"
        html += "<th width = 20%>Subtotal</th>"
        html += "<th width = 10%>Desconto</th>"
        html += "<th width = 10%>IVA</th>"
        html += "<th width = 20%>TOTAL</th>"
        html += "</tr>"

        for cliente in data:
            # se o documento näo estiver cancelado / activa = 1
            if int(cliente[18]) == 1:

                subtotal_geral += decimal.Decimal(cliente[10])
                taxa_geral += decimal.Decimal(cliente[11])
                desconto_geral += decimal.Decimal(cliente[12])
                total_geral += decimal.Decimal(cliente[13])

                html += """<tr>  <td>{}</td>  <td>{}</td>  <td align="right">{}</td>
                                                      <td align="right">{}</td> <td align="right">{}</td> 
                                                      <td align="right">{}</td>
                                                      <td align="right">{}</td> <td align="right">{}</td> 
                                                      </tr>
                                                          """.format(cliente[8], cliente[16], cliente[15], cliente[14],
                                                                     cliente[10],
                                                                     cliente[12], cliente[11], cliente[13])
            else:

                html += """<tr style="background-color:red;">  <td>{}</td>  <td>{}</td>  <td align="right">{}</td>
                                                                                               <td align="right">{}</td> <td align="right">{}</td> <td align="right">{}</td>
                                                                                               <td align="right">{}</td> <td align="right">{}</td> 
                                                                                               </tr>
                                                                                                   """.format(
                    cliente[8],
                    cliente[16],
                    cliente[15],
                    cliente[14],
                    cliente[10],
                    cliente[12],
                    cliente[11],
                    cliente[13])
        html += "<tr> <td></td> <td></td> <td></td> <td></td> <td align='right'>" \
                "<b>{}</b></td> <td align='right'><b>{}</b></td> " \
                "<td align='right'><b>{}</b></td> " \
                "<td align='right'><b>{}</b></td> </tr> ".format(subtotal_geral, taxa_geral,
                                                                        desconto_geral, total_geral)
        html += "</table>"

        ###########################################################################################################
        ###############################################ZONA DOS RECIBOS############################################
        ###########################################################################################################
        html += "</br>"

        total_geral = decimal.Decimal(0.00)

        recibo_sql = """select recibos.numero, recibos.tranferencia, recibos.cash, recibos.banco, recibos.total, 
                          recibos.estado from recibos INNER JOIN caixa on caixa.cod=recibos.caixa 
                          WHERE caixa.created BETWEEN '{}' and '{}' """.format(self.data_inicial.date().toString('yyyy-MM-dd'),
                                                                                     self.data_final.date().toString('yyyy-MM-dd'))

        self.cur.execute(recibo_sql)
        recibo_data = self.cur.fetchall()

        if len(recibo_data) > 0:

            html += "<table border='0' width = 80mm style='border: thin;'> " \
                    "<tr> <td> RECIBOS </tr> </td> </table>"

            html += "<table border='0' width = 80mm style='border: thin;'>"

            html += "<tr style='background-color:#c0c0c0;'>"
            # html += "<th width = 10%>DOC</th>"
            html += "<th width = 20%>Numero</th>"
            html += "<th width = 20%>POS</th>"
            html += "<th width = 20%>Cash</th>"
            html += "<th width = 20%>Cheque</th>"
            html += "<th width = 20%>TOTAL</th>"
            html += "</tr>"

            for cliente in recibo_data:
                # se o documento näo estiver cancelado / activa = 1
                if int(cliente[5]) == 1:

                    total_geral += decimal.Decimal(cliente[4])

                    html += """<tr>  <td>{}</td> <td align="right">{}</td> 
                                                                     <td align="right">{}</td>
                                                                     <td align="right">{}</td> <td align="right">{}</td> 
                                                                     </tr>
                                                                         """.format(cliente[0], cliente[1], cliente[2],
                                                                                    cliente[3],
                                                                                    cliente[4])
                else:

                    html += """<tr style="background-color:red;">  <td>{}</td> <td align="right">{}</td> <td align="right">{}</td>
                                                                                    <td align="right">{}</td> <td align="right">{}</td> 
                                                                                    </tr>
                                                                                        """.format(cliente[0],
                                                                                                   cliente[1],
                                                                                                   cliente[2],
                                                                                                   cliente[3],
                                                                                                   cliente[4])
        html += "<tr> <td></td> <td></td> <td></td> <td></td>" \
                "<td align='right'><b>{}</b></td>  </tr> ".format(total_geral)
        html += "</table>"


        document = QTextDocument()

        document.setHtml(html)

        dlg = QPrintPreviewDialog(self)
        dlg.paintRequested.connect(document.print_)
        dlg.showMaximized()
        dlg.exec_()

if __name__ == '__main__':

    app = QApplication(sys.argv)

    helloPythonWidget = MainWindow()
    helloPythonWidget.show()

    sys.exit(app.exec_())