import sys
import decimal
import csv
import subprocess
import os

from PyQt5.QtWidgets import (QApplication, QTableView, QAbstractItemView, QMessageBox, QToolBar, QLabel,
                             QStatusBar, QAction, QMainWindow, qApp, QDateTimeEdit, QHBoxLayout, QVBoxLayout, QCalendarWidget,
                             QGroupBox, QRadioButton, QCheckBox, QComboBox, QFileDialog, QProgressDialog, QButtonGroup,
                             QWidget)

from PyQt5.QtGui import QIcon, QTextDocument
from PyQt5.QtCore import Qt, QSizeF,QDateTime
from caixa import caixa
from sortmodel import MyTableModel
from datetime import datetime
from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter, QPrintDialog

from striped_table import StripedTable

agora = QDateTime(datetime.today()).toString('dd-MMM-yyyy H:mm:ss')


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.detalhada_html = None
        self.resumida_html = None


        self.codarmazem = self.parent().codarmazem
        self.user = self.parent().user
        # controla o codigo
        self.current_id = ""
        self.tipo_caixa = 1
        self.lista_geral = []

        self.conn = self.parent().conn
        self.cur = self.parent().cur
        self.user = self.parent().user

        # Create the main user interface
        self.ui()

        # Search the data
        self.fill_users()
        self.fill_table()
        self.data_inicial.dateChanged.connect(self.fill_table)
        self.data_final.dateChanged.connect(self.fill_table)
        self.todas_caixas.clicked.connect(self.fill_table)
        self.todas_abertas.clicked.connect(self.fill_table)
        self.todas_fechadas.clicked.connect(self.fill_table)

        self.current_id = self.parent().caixa_numero

    def ui(self):
        # create the view
        self.tv = StripedTable(self)

        self.tv.clicked.connect(self.clickedslot)
        self.tv.setFocus()

        self.setCentralWidget(self.tv)

        self.create_toolbar()
        self.estado = QStatusBar()
        self.setStatusBar(self.estado)

        self.setWindowTitle("Gestão de Caixa")

        self.btn_layout = QHBoxLayout()

    def focusInEvent(self, evt):
        self.fill_table()

    def search(self):
        from caixa_search import Pesquisa

        p = Pesquisa(self)
        p.setModal(True)
        p.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F12:
            self.search()
        else:
            event.ignore()

    def fill_table(self):

        self.tipo_caixa = 2

        if QDateTime(self.data_inicial.dateTime()) > QDateTime(self.data_final.dateTime()):
            self.data_inicial.setDateTime(self.data_final.dateTime())

        header = [qApp.tr('Código'), qApp.tr('Valor Inicial'), qApp.tr('Receitas'), qApp.tr('Despesas'),
                  qApp.tr('Estado'), qApp.tr('Data de abertura'), qApp.tr('data de fecho'),
                  qApp.tr('Fechada Por'), qApp.tr('Aberta por'), qApp.tr('Observações'), '']

        datainicial = QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss')
        datafinal = QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss')

        self.sql = """select * from caixa WHERE created BETWEEN '{data1}' and '{data2}' 
        """.format(data1=datainicial, data2=datafinal)

        if self.todas_fechadas.isChecked() is True:
            self.sql = """select * from caixa WHERE estado=1 and created BETWEEN '{data1}' and '{data2}' 
            """.format(data1=datainicial, data2=datafinal)

        if self.todas_abertas.isChecked() is True:
            self.sql = """select * from caixa WHERE estado=0 and  created BETWEEN '{data1}' and '{data2}' 
            """.format(data1=datainicial, data2=datafinal)

        self.sql += """ AND codarmazem="{}" """.format(self.parent().codarmazem)

        self.cur.execute(self.sql)
        lista = self.cur.fetchall()
        data = [list(str(item) for item in t) for t in lista]

        # Variavel principal que vai retornar a lista de dados da caixa
        self.lista_geral = data

        lista = []
        if len(data) == 0:
            self.tabledata = ["", "", "", "", "", "", "", "", "", "", ""]
        else:
            count = 0
            for x in data:
                if x[4] == "1":
                    data[count][4] = "Fechada"
                else:
                    data[count][4] = "Aberta"

                if x[6] == "None" or x[7] == "None":
                    data[count][6] = ""
                    data[count][7] = ""
                else:
                    data[count][6] = QDateTime.fromString(data[count][6],
                                                          "yyyy-MM-dd H:mm:ss").toString("dd-MMM-yyyy H:mm:ss")

                if data[count][5] != "":
                    data[count][5] = QDateTime.fromString(data[count][5],
                                                          "yyyy-MM-dd H:mm:ss").toString("dd-MMM-yyyy H:mm:ss")

                lista.append(data[count])
                count += 1
            self.tabledata = lista
        try:
            self.tm = MyTableModel(self.tabledata, header, self)
            # set the table model
            self.totalItems = self.tm.rowCount(self)
            self.tv.setModel(self.tm)

            self.tv.setColumnHidden(10, True)
        except Exception as e:
            print(e)
            return
        # # set row height
        nrows = len(self.tabledata)
        for row in range(nrows):
            self.tv.setRowHeight(row, 25)

        self.cria_checkboxes()
        self.create_statusbar()

    def create_toolbar(self):

        data_inicial = QLabel('De:')
        data_final = QLabel('A:')
        self.data_inicial = QDateTimeEdit()
        self.data_inicial.setDateTime(QDateTime.currentDateTime().addDays(-30))
        self.data_final = QDateTimeEdit()
        self.data_final.setDateTime(QDateTime.currentDateTime())
        self.todas_caixas = QRadioButton("Mostrar todas caixas")
        self.todas_fechadas = QRadioButton("Mostrar Fechadas")
        self.todas_abertas= QRadioButton("Mostrar Aberta")

        self.todas_caixas.setChecked(True)

        calendario = QCalendarWidget()
        calendario2 = QCalendarWidget()

        self.pos_print = QRadioButton("POS")
        self.a4_print = QRadioButton("A4")
        self.a4_print.setChecked(True)

        printlay = QVBoxLayout()
        printlay.addWidget(self.a4_print)
        printlay.addWidget(self.pos_print)

        printbox = QGroupBox("Tipo de Papel")
        printbox.setLayout(printlay)

        self.list_de_produtos = QRadioButton("Lista de Produtos")
        self.list_de_produtos.setChecked(True)
        self.list_de_documentos = QRadioButton("Lista de Documentos")
        lista_layout = QVBoxLayout()
        lista_layout.addWidget(self.list_de_produtos)
        lista_layout.addWidget(self.list_de_documentos)

        lista_box = QGroupBox("Imprimir")
        lista_box.setLayout(lista_layout)

        self.data_inicial.setCalendarPopup(True)
        self.data_final.setCalendarPopup(True)
        self.data_inicial.setCalendarWidget(calendario)
        self.data_final.setCalendarWidget(calendario2)

        h_layout = QHBoxLayout()
        h_layout.addWidget(data_inicial)
        h_layout.addWidget(self.data_inicial)
        h_layout.addWidget(data_final)
        h_layout.addWidget(self.data_final)

        h_layout2 = QHBoxLayout()
        h_layout2.addWidget(self.todas_caixas)
        h_layout2.addWidget(self.todas_fechadas)
        h_layout2.addWidget(self.todas_abertas)

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout)
        v_layout.addLayout(h_layout2)

        datas = QGroupBox("Pesquisa")
        datas.setLayout(v_layout)

        actualizar_caixa = QAction(QIcon('./icons/add_2.ico'), qApp.tr("Actualizar\nCaixa"), self)
        imprimir_anterior = QAction(QIcon('./icons/print.ico'), qApp.tr("Imprimir\nCaixa anterior"), self)
        imprimir_currente = QAction(QIcon('./images/fileprint.png'), qApp.tr("Fechar\nCaixa currente"), self)
        imprimir_em_datas = QAction(QIcon('./icons/Search.ico'), qApp.tr("Imprimir Caixa\nbaseando em datas"), self)
        export_csv = QAction(QIcon('./images/icons8-export-csv-50.png'), "Exportar\npara CSV", self)
        activar_caixa = QAction(QIcon('./icons/caixa.ico'), "Activar Caixa", self)

        self.user_combo = QComboBox()

        user_group = QGroupBox("Usuários")
        v_boxlayout = QVBoxLayout()
        v_boxlayout.addWidget(QLabel("  Escolha Usuário"))
        v_boxlayout.addWidget(self.user_combo)
        user_group.setLayout(v_boxlayout)

        tool = QToolBar()
        tool.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        tool.setContextMenuPolicy(Qt.PreventContextMenu)

        tool.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        tool.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        tool.addWidget(user_group)

        tool_data = QToolBar()
        tool_data.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        tool_data.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        tool_data.setContextMenuPolicy(Qt.PreventContextMenu)
        tool_data.addWidget(datas)

        tool_tipo_papel = QToolBar()
        tool_tipo_papel.setContextMenuPolicy(Qt.PreventContextMenu)
        tool_tipo_papel.addWidget(printbox)
        tool_tipo_papel.addWidget(lista_box)
        tool_tipo_papel.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        tool_tipo_papel.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)

        tool_print = QToolBar()
        tool_print.setContextMenuPolicy(Qt.PreventContextMenu)
        tool_print.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        tool_print.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        tool_print.addAction(imprimir_anterior)
        tool_print.addAction(imprimir_em_datas)
        tool_print.addSeparator()
        tool_print.addAction(imprimir_currente)
        tool_print.addSeparator()
        tool_print.addAction(actualizar_caixa)
        tool_print.addAction(export_csv)
        tool_print.addAction(activar_caixa)

        self.addToolBarBreak(Qt.TopToolBarArea)

        self.addToolBar(tool)
        self.addToolBar(tool_tipo_papel)
        self.addToolBar(tool_data)
        self.addToolBarBreak(Qt.TopToolBarArea)
        self.addToolBar(tool_print)

        ######################################################################
        actualizar_caixa.triggered.connect(self.update_data)
        imprimir_anterior.triggered.connect(self.imprime_caixa)
        export_csv.triggered.connect(self.exportar_resumo_caixa_csv)
        # export_csv.triggered.connect(self.exportar_caixa_csv_big)
        activar_caixa.triggered.connect(self.activar_caixa)
        imprimir_currente.triggered.connect(self.fechar_caixa)
        imprimir_em_datas.triggered.connect(self.imprime_lista_caixa)

    def activar_caixa(self):
        if self.current_id == "" or self.current_id is None:
            QMessageBox.warning(self, 'erro', 'Escolha a caixa a activar na lista')
            return

        if self.current_id == self.parent().caixa_numero:
            QMessageBox.warning(self, 'erro', 'A caixa ja esta abaerta')
            return

        sql = """UPDATE  caixa set estado=1 WHERE cod="{}" """.format(self.parent().caixa_numero)
        sql_2 = """UPDATE  caixa set estado=0 WHERE cod="{}" """.format(self.current_id)

        self.cur.execute(sql)
        self.conn.commit()

        self.cur.execute(sql_2)
        self.conn.commit()
        QMessageBox.information(self, 'Sucesso', 'Caixa {} Activada com sucesso!\nReinicie o sistema'.format(self.current_id))

        sys.exit(1)

    def fill_users(self):

        sql = "SELECT cod FROM users"
        self.cur.execute(sql)
        data = self.cur.fetchall()

        self.user_combo.addItem("Todos")

        if len(data) > 0:
            for item in data:
                self.user_combo.addItem(item[0])

            self.user_combo.setCurrentIndex(0)
            return True

        return False

    def create_statusbar(self):

        # Remove as Labels para nao duplicar
        for label in self.estado.findChildren(QLabel):
            self.estado.removeWidget(label)

        # Remove as Labels para nao duplicar
        for btn in self.estado.findChildren(QWidget):
            if btn.objectName == "checkboxes":
                self.estado.removeWidget(btn)

        self.items = QLabel("Total Items: %s" % self.totalItems)
        self.estado.addWidget(self.items)
        self.estado.addWidget(self.btn_widget)

    def clickedslot(self, index):

        self.row = int(index.row())

        indice= self.tm.index(self.row, 0)
        self.current_id = indice.data()

        data_abertura = self.tm.index(self.row, 5)
        self.data_documento = data_abertura.data()


        self.tipo_caixa = 1

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

        sql = """ UPDATE caixa set estado=1, modified='{}', modified_by='{}' WHERE cod = '{}' and estado=0 
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

        dia = QDateTime.currentDateTime().toString('yyyy-MM-dd H:mm:ss')

        sql = """ UPDATE caixa set estado=1, modified='{}', modified_by='{}' WHERE estado=0 
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

                self.tipo_caixa = 1

                if self.pos_print.isChecked():
                    if self.list_de_produtos.isChecked():
                        self.imprime_caixa_detalhada_pos()
                    else:
                        self.imprime_caixa_resumida_pos()
                else:
                    if self.list_de_produtos.isChecked():
                        self.imprime_caixa_detalhada()
                    else:
                        self.imprime_caixa_resumida()

            except Exception as e:
                QMessageBox.critical(self, "Erro",
                                     "Aconteceu um erro no fecho da caixa. Tente mais tarde.\n{}.".format(e))
        else:
            QMessageBox.warning(self, "Erro", "Nenhuma caixa aberta.")

    def get_documentos(self):
        sql = """SELECT cod, nome from documentos """

        cont = 0
        for x in self.estado.findChildren(QCheckBox):

            if x.isChecked() is True:

                print(x.objectName(), " ", "Checked: ", x.isChecked())
                if cont == 0:
                    sql += " WHERE cod='{}' ".format(x.objectName())
                else:
                    sql += " OR cod='{}' ".format(x.objectName())

                cont += 1

        self.cur.execute(sql)
        data = self.cur.fetchall()

        return data

    def html_detalhado(self):
        sql = """SELECT cod, nome from documentos """

        cont = 0
        for x in self.estado.findChildren(QCheckBox):
            if x.isChecked():
                if cont == 0:
                    sql += " WHERE cod='{}' ".format(x.objectName())
                else:
                    sql += " OR cod='{}' ".format(x.objectName())

                cont += 1

        self.cur.execute(sql)
        data = self.cur.fetchall()

        subtotal_geral = decimal.Decimal(0)
        taxa_geral = decimal.Decimal(0)
        desconto_geral = decimal.Decimal(0)
        total_geral = decimal.Decimal(0)
        total_pos = decimal.Decimal(0)
        total_movel = decimal.Decimal(0)
        total_numerario = decimal.Decimal(0)
        total_lucro = decimal.Decimal(0)

        if len(data) > 0:
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
                      """.format(
                self.parent().empresa_logo)

            contar = 0
            for cod, nome in data:
                if self.tipo_caixa == 1:
                    receitas, despesas = self.calcula_receitas_despesas(self.current_id)

                    if self.current_id is None:
                        QMessageBox.warning(self, "Erro. Nenhum registo selecionado.",
                                            "Escolha a caixa a imprimir na tabela")
                        return False

                    if self.user_combo.currentText() == "Todos":
                        sql = """SELECT * FROM FECHO_CAIXA_DETALHADA WHERE doc = "{}" and caixa_numero = '{}' 
                                                        order by numero""".format(cod, self.current_id)

                        total_sql = """SELECT cash, banco, tranferencia, lucro, total, troco FROM facturacao WHERE 
                                coddocumento = "{}" and caixa = '{}' order by numero """.format(
                            cod, self.current_id)

                        recibo_sql = """select recibos.numero, recibos.tranferencia, recibos.cash, recibos.banco, 
                                                                                                recibos.total, recibos.estado, clientes.nome, recibos.created from recibos 
                                                                                                INNER JOIN caixa on caixa.cod=recibos.caixa 
                                                                                                INNER JOIN clientes on clientes.cod=recibos.codcliente 
                                                                                                WHERE caixa.cod = '{}' order by recibos.numero""".format(
                            self.current_id)

                    else:
                        sql = """SELECT * FROM FECHO_CAIXA_DETALHADA WHERE doc = "{}" and caixa_numero = '{}' 
                                                                                and user = "{}" order by numero""".format(
                            cod,
                            self.current_id,
                            self.user_combo.currentText())

                        total_sql = """SELECT cash, banco, tranferencia, lucro, total, troco FROM facturacao WHERE 
                                coddocumento = "{}" and created_by = "{}" AND caixa = "{}" order by numero """.format(
                            cod, self.user_combo.currentText(), self.current_id)

                        recibo_sql = """select recibos.numero, recibos.tranferencia, recibos.cash, recibos.banco, 
                                                recibos.total, recibos.estado, clientes.nome, recibos.created from recibos 
                                                INNER JOIN caixa on caixa.cod=recibos.caixa 
                                                INNER JOIN clientes on clientes.cod=recibos.codcliente 
                                                WHERE caixa.cod = '{}' AND recibos.created_by="{}" 
                                                order by recibos.numero""".format(
                            self.current_id, self.user_combo.currentText())

                elif self.tipo_caixa == 2:
                    receitas, despesas = self.calcula_receitas_despesas_datas(
                        QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                        QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'))

                    if self.user_combo.currentText() == "Todos":
                        sql = """SELECT * FROM FECHO_CAIXA_DETALHADA WHERE ABERTURA BETWEEN '{}' and '{}' 
                                                                            and doc = "{}" order by numero 
                                                                            """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), cod)

                        total_sql = """SELECT cash, banco, tranferencia, lucro, total, troco FROM facturacao WHERE 
                                created BETWEEN '{}' and '{}' and coddocumento = "{}" order by numero 
                                """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), cod)

                        recibo_sql = """select recibos.numero, recibos.tranferencia, recibos.cash, recibos.banco, 
                                    recibos.total, recibos.estado, clientes.nome, recibos.created from recibos 
                                    INNER JOIN caixa on caixa.cod=recibos.caixa 
                                    INNER JOIN clientes on clientes.cod=recibos.codcliente 
                                    WHERE recibos.created BETWEEN '{}' and '{}' 
                                    order by recibos.numero
                                    """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'))
                    else:
                        sql = """SELECT * FROM FECHO_CAIXA_DETALHADA WHERE ABERTURA BETWEEN '{}' and '{}' 
                                                                            and doc = "{}" and user = "{}" order by numero 
                                                                            """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), cod,
                            self.user_combo.currentText())

                        total_sql = """SELECT cash, banco, tranferencia, lucro, total, troco FROM facturacao WHERE created BETWEEN '{}' and '{}' 
                                                                                                    and coddocumento = "{}" and created_by = "{}" order by numero 
                                                                                                    """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), cod,
                            self.user_combo.currentText())

                        recibo_sql = """select recibos.numero, recibos.tranferencia, recibos.cash, recibos.banco, 
                                                                                                recibos.total, recibos.estado, clientes.nome, recibos.created from recibos 
                                                                                                INNER JOIN caixa on caixa.cod=recibos.caixa 
                                                                                                INNER JOIN clientes on clientes.cod=recibos.codcliente 
                                                                                                WHERE recibos.created BETWEEN '{}' and '{}' 
                                                                                                AND recibos.created_by="{}" order by recibos.numero
                                                                                                """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), self.user_combo.currentText())

                self.cur.execute(sql)
                data = self.cur.fetchall()

                if len(data) > 0:

                    if contar == 0:
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

                        abertura = QDateTime(data[0][5]).toString('dd-MMM-yyyy')

                        if data[0][6] is None:
                            fecho = "(Caixa Aberta)"
                        else:
                            fecho = QDateTime(data[0][6]).toString('dd-MMM-yyyy')

                        if data[0][4] is None:
                            fechada_por = "(Caixa Aberta)"
                        else:
                            fechada_por = data[0][4]

                        html += "<center align='left'>Data de Impressão: {}</center>".format(agora)
                        html += "<center align='left'>Data de abertura: {}</center>".format(abertura)
                        html += "<center align='left'>Data de Fecho: {}</center>".format(fecho)
                        html += "<center align='left'>Aberta por: {}</center>".format(data[0][3])
                        html += "<center align='left'>Fechada Por: {}</center>".format(fechada_por)

                        html += "<br/>"
                        html += "<center align='left'>VALOR INICIAL: {}</center>".format(data[0][0])
                        html += "<center align='left'>RECEITAS: {:20,.2f}</center>".format(receitas)
                        html += "<center align='left'>DESPESAS: {:20,.2f}</center>".format(despesas)

                        html += "<hr/>"
                        html += "<center align='left'>USUARIO: {}</center>".format(self.user_combo.currentText())
                        html += "<hr/>"

                    contar += 1

                    html += "<table border=0 width = 100% style='border: thin; style='font-size: 8px;''> " \
                            "<tr> <td> LISTA DE {}'s </tr> </td> </table>".format(str(nome).upper())

                    html += "<table border=0 width = 100% style='border: thin;'>"
                    html += "<tr style='background-color:#c0c0c0;'>"
                    html += "<th width = 10%>DOC</th>"
                    html += "<th width = 30%>Descrição</th>"
                    html += "<th width = 5%>Qt.</th>"
                    html += "<th width = 10%>Preço</th>"
                    html += "<th width = 15%>Subtotal</th>"
                    html += "<th width = 15%>IVA</th>"
                    html += "<th width = 15%>Total</th>"
                    html += "</tr>"

                    for cliente in data:

                        if int(cliente[18]) == 1:
                            # se o documento näo estiver cancelado / activa = 1

                            subtotal_geral += decimal.Decimal(cliente[30])
                            taxa_geral += decimal.Decimal(cliente[28])
                            desconto_geral += decimal.Decimal(cliente[29])
                            total_geral += decimal.Decimal(cliente[26])
                            total_pos += decimal.Decimal(cliente[16])
                            total_movel += decimal.Decimal(cliente[14])
                            total_numerario += decimal.Decimal(cliente[15])

                            html += """<tr> 
                                            <td>{}</td> <td>{}</td> <td>{:20,.2f}</td> <td>{:20,.2f}</td> <td align="right">{:20,.2f}</td>
                                            <td align="right">{:20,.2f}</td><td align="right">{:20,.2f}</td>   
                                            </tr> """.format(cliente[7] + " " + str(cliente[8]),  cliente[24], cliente[25], cliente[27], cliente[30],
                                                             cliente[28], cliente[26])
                        else:
                            html += """<tr style="background-color:red;"> 
                                            <td>{}</td> <td>{}</td> <td>{:20,.2f}</td> <td>{:20,.2f}</td> <td align="right">{:20,.2f}</td>
                                            <td align="right">{:20,.2f}</td><td align="right">{:20,.2f}</td></td>   
                                            </tr> """.format(cliente[7] + " " + str(cliente[8]), cliente[24],
                                                             cliente[25], cliente[27], cliente[30],
                                                             cliente[28], cliente[26])

                    html += """<tr style="font-weight:bold; font-size:10px;"> 
                                    <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td> <td align="right">{:20,.2f}</td>
                                    <td align="right">{:20,.2f}</td><td align="right">{:20,.2f}</td><td align="right">{}</td>   
                                    </tr> """.format("Total", "-", "-", "-", subtotal_geral,
                                                     taxa_geral, total_geral,
                                                     "")

                    self.cur.execute(total_sql)
                    data = self.cur.fetchall()

                    cash_geral = 0
                    pos_geral = 0
                    movel_geral = 0
                    lucro_geral = 0
                    total_geral = 0
                    troco_geral = 0

                    for geral in data:
                        cash_geral += decimal.Decimal(geral[0])
                        pos_geral += decimal.Decimal(geral[1])
                        movel_geral += decimal.Decimal(geral[2])
                        lucro_geral += decimal.Decimal(geral[3])
                        total_geral += decimal.Decimal(geral[4])
                        troco_geral += decimal.Decimal(geral[5])

                    html += "</table>"

                    subtotal_geral = decimal.Decimal(0)
                    taxa_geral = decimal.Decimal(0)
                    desconto_geral = decimal.Decimal(0)
                    total_geral = decimal.Decimal(0)
                    total_pos = decimal.Decimal(0)
                    total_movel = decimal.Decimal(0)
                    total_numerario = decimal.Decimal(0)
                    total_lucro = decimal.Decimal(0)

            self.cur.execute(recibo_sql)
            recibo_data = self.cur.fetchall()

            if len(recibo_data) > 0:

                html += "<table border=0 width = 100% style='border: thin; style='font-size: 8px;''> " \
                        "<tr> <td> RECIBOS </tr> </td> </table>"

                html += "<table border=0 width = 100% style='border: thin;'>"

                html += "<tr style='background-color:#c0c0c0;'>"
                # html += "<th width = 10%>DOC</th>"
                html += "<th width = 10%>Data</th>"
                html += "<th width = 10%>Numero</th>"
                html += "<th width = 60%>CLIENTE</th>"
                html += "<th width = 20%>TOTAL</th>"

                html += "</tr>"

                if recibo_data:
                    for cliente in recibo_data:
                        # se o documento näo estiver cancelado / activa = 1
                        if int(cliente[5]) == 1:

                            total_geral += decimal.Decimal(cliente[4])

                            html += """<tr>  <td>{}</td> <td>{}</td> <td>{}</td> <td align="right">{:20,.2f}</td> 
                                            </tr>""".format(QDateTime(cliente[7]).toString('dd-MM-yyyy'), cliente[0], cliente[6], cliente[4])
                        else:
                            html += """<tr style="background-color:red;">  
                                            <td>{}</td> <td>{}</td> <td>{}</td> <td align="right">{:20,.2f}</td> 
                                            </tr>""".format(QDateTime(cliente[7]).toString('dd-MM-yyyy'), cliente[0], cliente[6], cliente[4])

                    html += "<tr> <td></td> <td></td>" \
                            "<td></td> <td align='right'><b>{:20,.2f}</b></td>  </tr> ".format(total_geral)
                    html += "</table>"

        # Despesas e receitas
        sql = """SELECT descricao, valor, obs, tipo FROM receitas WHERE codcaixa="" AND codarmazem="{}" """.format(
            self.current_id, self.codarmazem
        )

        self.cur.execute(sql)
        receita_data = self.cur.fetchall()

        if len(receita_data) > 0:

            html += "<table border=0 width = 100% style='border: thin;'>"
            html += "<tr style='background-color:#c0c0c0;'>"
            html += "<th width = 30%>Descrição</th>"
            html += "<th width = 20%>Valor</th>"
            html += "<th width = 40%>Notas</th>"
            html += "</tr>"

            for item in receita_data:
                if item[3] == 1:
                    html += """<tr>  <td>{}</td> <td align="right">{:20,.2f}</td> <td>{}</td> </tr>""".format(
                        item[0], item[1], item[2])

            html += "<table border=0 width = 100% style='border: thin;'>"
            html += "<tr style='background-color:#c0c0c0;'>"
            html += "<th width = 30%>Descrição</th>"
            html += "<th width = 20%>Valor</th>"
            html += "<th width = 40%>Notas</th>"
            html += "</tr>"

            for item in receita_data:
                if item[3] == 0:
                    html += """<tr>  <td>{}</td> <td align="right">{:20,.2f}</td> <td>{}</td> </tr>""".format(
                        item[0], item[1], item[2])

        print(html)

        return html

    def imprime_caixa_detalhada(self):

        html = self.html_detalhado()

        if html == "" or html is None:
            return False

        self.detalhada_html = html

        document = QTextDocument()
        document.setHtml(html)
        dlg = QPrintPreviewDialog(self)
        dlg.paintRequested.connect(document.print_)
        dlg.showMaximized()
        dlg.exec_()

        return True

    def imprime_caixa_resumida(self):

        sql = """SELECT cod, nome from documentos """

        cont = 0
        for x in self.estado.findChildren(QCheckBox):
            if x.isChecked():
                if cont == 0:
                    sql += " WHERE cod='{}' ".format(x.objectName())
                else:
                    sql += " OR cod='{}' ".format(x.objectName())

                cont += 1
        print("documentos sql: ", sql)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        subtotal_geral = decimal.Decimal(0)
        taxa_geral = decimal.Decimal(0)
        desconto_geral = decimal.Decimal(0)
        total_geral = decimal.Decimal(0)
        total_pos = decimal.Decimal(0)
        total_movel = decimal.Decimal(0)
        total_numerario = decimal.Decimal(0)
        total_lucro = decimal.Decimal(0)

        if len(data) > 0:
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
              """.format(
                self.parent().empresa_logo)

            contar = 0
            for cod, nome in data:
                if self.tipo_caixa == 1:

                    receitas, despesas = self.calcula_receitas_despesas(self.current_id)

                    if self.current_id is None:
                        QMessageBox.warning(self, "Erro. Nenhum registo selecionado.",
                                            "Escolha a caixa a imprimir na tabela")
                        return False

                    if self.user_combo.currentText() == "Todos":
                        sql = """SELECT * FROM FECHO_CAIXA WHERE doc = "{}" and caixa_numero = '{}' 
                                                order by numero""".format(cod, self.current_id)

                        total_sql = """SELECT cash, banco, tranferencia, lucro, total, troco FROM facturacao WHERE 
                        coddocumento = "{}" and caixa = '{}' order by numero """.format(
                            cod, self.current_id)

                        recibo_sql = """select recibos.numero, recibos.tranferencia, recibos.cash, recibos.banco, 
                                                                                        recibos.total, recibos.estado, clientes.nome, recibos.created from recibos 
                                                                                        INNER JOIN caixa on caixa.cod=recibos.caixa 
                                                                                        INNER JOIN clientes on clientes.cod=recibos.codcliente 
                                                                                        WHERE caixa.cod = '{}' order by recibos.numero""".format(
                            self.current_id)

                    else:
                        sql = """SELECT * FROM FECHO_CAIXA WHERE doc = "{}" and caixa_numero = '{}' 
                                                                        and user = "{}" order by numero""".format(
                            cod,
                            self.current_id,
                            self.user_combo.currentText())

                        total_sql = """SELECT cash, banco, tranferencia, lucro, total, troco FROM facturacao WHERE 
                        coddocumento = "{}" and created_by = "{}" AND caixa = "{}" order by numero """.format(
                            cod, self.user_combo.currentText(), self.current_id)

                        print(total_sql)

                        recibo_sql = """select recibos.numero, recibos.tranferencia, recibos.cash, recibos.banco, 
                                                                                        recibos.total, recibos.estado, clientes.nome, recibos.created from recibos 
                                                                                        INNER JOIN caixa on caixa.cod=recibos.caixa 
                                                                                        INNER JOIN clientes on clientes.cod=recibos.codcliente 
                                                                                        WHERE caixa.cod = '{}' AND recibos.created_by="{}" 
                                                                                        order by recibos.numero""".format(
                            self.current_id, self.user_combo.currentText())

                elif self.tipo_caixa == 2:
                    receitas, despesas = self.calcula_receitas_despesas_datas(
                        QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                        QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'))

                    if self.user_combo.currentText() == "Todos":
                        sql = """SELECT * FROM FECHO_CAIXA WHERE ABERTURA BETWEEN '{}' and '{}' 
                                                                    and doc = "{}" order by numero 
                                                                    """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), cod)

                        total_sql = """SELECT cash, banco, tranferencia, lucro, total, troco FROM facturacao WHERE 
                        created BETWEEN '{}' and '{}' and coddocumento = "{}" order by numero 
                        """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), cod)

                        recibo_sql = """select recibos.numero, recibos.tranferencia, recibos.cash, recibos.banco, 
                                                                                        recibos.total, recibos.estado, clientes.nome, recibos.created from recibos 
                                                                                        INNER JOIN caixa on caixa.cod=recibos.caixa 
                                                                                        INNER JOIN clientes on clientes.cod=recibos.codcliente 
                                                                                        WHERE recibos.created BETWEEN '{}' and '{}' 
                                                                                        order by recibos.numero
                                                                                        """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'))
                    else:
                        sql = """SELECT * FROM FECHO_CAIXA WHERE ABERTURA BETWEEN '{}' and '{}' 
                                                                    and doc = "{}" and user = "{}" order by numero 
                                                                    """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), cod,
                            self.user_combo.currentText())

                        total_sql = """SELECT cash, banco, tranferencia, lucro, total, troco FROM facturacao WHERE created BETWEEN '{}' and '{}' 
                                                                                            and coddocumento = "{}" and created_by = "{}" order by numero 
                                                                                            """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), cod,
                            self.user_combo.currentText())

                        recibo_sql = """select recibos.numero, recibos.tranferencia, recibos.cash, recibos.banco, 
                                                                                        recibos.total, recibos.estado, clientes.nome, recibos.created from recibos 
                                                                                        INNER JOIN caixa on caixa.cod=recibos.caixa 
                                                                                        INNER JOIN clientes on clientes.cod=recibos.codcliente 
                                                                                        WHERE recibos.created BETWEEN '{}' and '{}' 
                                                                                        AND recibos.created_by="{}" order by recibos.numero
                                                                                        """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), self.user_combo.currentText())

                print(sql)
                self.cur.execute(sql)
                data = self.cur.fetchall()

                if len(data) > 0:

                    if contar == 0:
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

                        html += "<center align='left'>Data de Impressão: {}</center>".format(agora)
                        html += "<center align='left'>Data de abertura: {}</center>".format(data[0][5])
                        html += "<center align='left'>Data de Fecho: {}</center>".format(data[0][6])
                        html += "<center align='left'>Aberta por: {}</center>".format(data[0][3])
                        html += "<center align='left'>Fechada Por: {}</center>".format(data[0][4])

                        html += "<br/>"
                        html += "<center align='left'>VALOR INICIAL: {}</center>".format(data[0][0])
                        html += "<center align='left'>RECEITAS: {}</center>".format(receitas)
                        html += "<center align='left'>DESPESAS: {}</center>".format(despesas)

                        html += "<hr/>"
                        html += "<center align='left'>USUARIO: {}</center>".format(self.user_combo.currentText())
                        html += "<hr/>"

                    contar += 1

                    html += "<table border=0 width = 100% style='border: thin; style='font-size: 8px;''> " \
                            "<tr> <td> LISTA DE {}'s </tr> </td> </table>".format(str(nome).upper())

                    html += "<table border=0 width = 100% style='border: thin;'>"
                    html += "<tr style='background-color:#c0c0c0;'>"
                    html += "<th width = 10%>DOC.</th>"
                    html += "<th width = 15%>NO.</th>"
                    html += "<th width = 25%>Cliente</th>"
                    html += "<th width = 10%>Desconto</th>"
                    html += "<th width = 15%>Subtotal</th>"
                    html += "<th width = 10%>IVA</th>"
                    html += "<th width = 15%>TOTAL</th>"
                    # html += "<th width = 15%>Lucro</th>"
                    html += "</tr>"

                    print("Data sql: ", sql)

                    for cliente in data:
                        # se o documento näo estiver cancelado / activa = 1
                        if int(cliente[18]) == 1:

                            subtotal_geral += decimal.Decimal(cliente[10])
                            taxa_geral += decimal.Decimal(cliente[12])
                            desconto_geral += decimal.Decimal(cliente[11])
                            total_geral += decimal.Decimal(cliente[13])
                            total_pos += decimal.Decimal(cliente[16])
                            total_movel += decimal.Decimal(cliente[14])
                            total_numerario += decimal.Decimal(cliente[15])

                            total_lucro += decimal.Decimal(cliente[23])

                            html += """<tr style="font-size:8px;"> 
                                    <td>{}</td> <td>{}</td> <td>{}</td> <td align="right">{:20,.2f}</td>
                                    <td align="right">{:20,.2f}</td>  
                                    <td align="right">{:20,.2f}</td><td align="right">{:20,.2f}</td>   
                                    </tr> """.format(cliente[7], "{}/{}".format(cliente[8], cliente[24]),
                                                     cliente[9], cliente[11],
                                                     cliente[10], cliente[12], cliente[13])
                        else:
                            html += """<tr style="background-color:red;font-size:8px;"> 
                                    <td>{}</td> <td>{}</td> <td>{}</td> <td align="right">{:20,.2f}</td>    
                                    <td align="right">{:20,.2f}</td>
                                    <td align="right">{:20,.2f}</td><td align="right">{:20,.2f}</td>
                                    </tr> """.format(cliente[7], "{}/{}".format(cliente[8], cliente[24]),
                                                     cliente[9], cliente[11],
                                                     cliente[10], cliente[12], cliente[13])


                    # Totais Gerais

                    html += """<tr> <td>CASH</td> <td></td> <td></td> <td></td> <td></td> <td></td>
                                                            <td align='right'><b>{:20,.2f}</b></td> </tr>""".format(
                        decimal.Decimal(total_numerario))

                    html += """<tr> <td>POS</td> <td></td> <td></td> <td></td> <td></td> <td></td>
                                                            <td align='right'><b>{:20,.2f}</b></td> </tr>""".format(
                        decimal.Decimal(total_pos))

                    html += """<tr> <td>MOVEL</td> <td></td> <td></td> <td></td> <td></td> <td></td>
                                                            <td align='right'><b>{:20,.2f}</b></td> </tr>""".format(
                        decimal.Decimal(total_movel))

                    html += """<tr> <td>DESCONTO</td> <td></td> <td></td> <td></td> <td></td> <td></td>
                                                            <td align='right'><b>{:20,.2f}</b></td> </tr>""".format(
                        decimal.Decimal(desconto_geral))

                    html += """<tr> <td>SUBTOTAL</td> <td></td> <td></td> <td></td> <td></td> <td></td>
                                                                                <td align='right'><b>{:20,.2f}</b></td></tr>""".format(
                        decimal.Decimal(subtotal_geral))

                    html += """<tr> <td>IVA</td> <td></td> <td></td> <td></td> <td></td> <td></td>
                                                            <td align='right'><b>{:20,.2f}</b></td></tr>""".format(
                        decimal.Decimal(taxa_geral))


                    html += """<tr> <td>TOTAL GERAL</td> <td></td> <td></td> <td></td> <td></td> <td></td>
                                                            <td align='right'><b>{:20,.2f}</b></td> </tr>""".format(
                        decimal.Decimal(total_geral))

                    html += "</table>"

                    subtotal_geral = decimal.Decimal(0)
                    taxa_geral = decimal.Decimal(0)
                    desconto_geral = decimal.Decimal(0)
                    total_geral = decimal.Decimal(0)
                    total_pos = decimal.Decimal(0)
                    total_movel = decimal.Decimal(0)
                    total_numerario = decimal.Decimal(0)
                    total_lucro = decimal.Decimal(0)

            self.cur.execute(recibo_sql)
            recibo_data = self.cur.fetchall()

            if len(recibo_data) > 0:

                html += "<table border=0 width = 100% style='border: thin; style='font-size: 8px;''> " \
                        "<tr> <td> RECIBOS </tr> </td> </table>"

                html += "<table border=0 width = 100% style='border: thin;'>"

                html += "<tr style='background-color:#c0c0c0;'>"
                # html += "<th width = 10%>DOC</th>"
                html += "<th width = 10%>Data</th>"
                html += "<th width = 10%>Numero</th>"
                html += "<th width = 60%>CLIENTE</th>"
                html += "<th width = 20%>TOTAL</th>"

                html += "</tr>"

                if recibo_data:
                    for cliente in recibo_data:
                        # se o documento näo estiver cancelado / activa = 1
                        if int(cliente[5]) == 1:

                            total_geral += decimal.Decimal(cliente[4])

                            html += """<tr style="font-size:8px;">  <td>{}</td> <td>{}</td> <td>{}</td> <td align="right">{:20,.2f}</td> 
                                    </tr>""".format(QDateTime(cliente[7]).toString('dd-MM-yyyy'), cliente[0], cliente[6], cliente[4])
                        else:
                            html += """<tr style="background-color:red;font-size:8px;">  
                                    <td>{}</td> <td>{}</td> <td>{}</td> <td align="right">{:20,.2f}</td> 
                                    </tr>""".format(QDateTime(cliente[7]).toString('dd-MM-yyyy'), cliente[0], cliente[6], cliente[4])

                    html += "<tr> <td></td> <td></td>" \
                            "<td></td> <td align='right'><b>{:20,.2f}</b></td>  </tr> ".format(total_geral)
                    html += "</table>"

        self.resumida_html = html

        document = QTextDocument()
        document.setHtml(html)
        dlg = QPrintPreviewDialog(self)
        dlg.paintRequested.connect(document.print_)
        dlg.showMaximized()
        dlg.exec_()

    def calcula_receitas_despesas(self, codcaixa):
        """
        Calcula as receitas e despesas para o fecho de cada caixa
        :return: [receitas, despesas]
        """

        sql = """SELECT valor, tipo FROM receitas WHERE codcaixa="{}" AND estado=1 """.format(codcaixa)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        receitas = 0
        despesas = 0

        if len(data) > 0:
            for tipo in data:
                if tipo[1] == 1:
                    receitas += tipo[0]
                else:
                    despesas += tipo[0]

        return receitas, despesas

    def calcula_receitas_despesas_datas(self, data_inicial, data_final):
        """
        Calcula as receitas e despesas para o fecho de cada caixa baseando em datas
        :return: [receitas, despesas]
        """

        sql = """SELECT valor, tipo FROM receitas WHERE (modified BETWEEN "{}" AND "{}") AND estado=1 """.format(
            data_inicial, data_final)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        receitas = 0
        despesas = 0

        if len(data) > 0:
            for tipo in data:
                if tipo[1] == 1:
                    receitas += tipo[0]
                else:
                    despesas += tipo[0]

        return receitas, despesas

    def imprime_caixa_detalhada_pos(self):

        sql = """SELECT cod, nome from documentos """

        cont = 0
        for x in self.estado.findChildren(QCheckBox):
            if x.isChecked():
                if cont == 0:
                    sql += " WHERE cod='{}' ".format(x.objectName())
                else:
                    sql += " OR cod='{}' ".format(x.objectName())

                cont += 1

        self.cur.execute(sql)
        data = self.cur.fetchall()

        subtotal_geral = decimal.Decimal(0)
        taxa_geral = decimal.Decimal(0)
        desconto_geral = decimal.Decimal(0)
        total_geral = decimal.Decimal(0)

        if len(data) > 0:
            if self.parent().empresa_logo != "":
                html = """
                          < table
                              width = "100%" >
                              < tr >
                                  < td > 
                                  < img src = '{}' width = "80" > 
                                  < / td >
                              </ tr >
                          < / table > 
                          """.format(
                self.parent().empresa_logo)

            else:
                html = ""

            contar = 0

            for cod, nome in data:

                if self.tipo_caixa == 1:

                    receitas, despesas = self.calcula_receitas_despesas(self.current_id)

                    if self.user_combo.currentText() == "Todos":
                        sql = """SELECT DISTINCT `valor_inicial`, `receitas`, `despesas`, `CRIADA_POR`, `FECHADA_POR`, `ABERTURA`, `FECHO`, `DOCUMENTO`, 
                        `numero`, `CLIENTE`, `subtotal`, `desconto`, `taxa`, SUM(`total`), `CHEQUE`, `NUMERARIO`, `POS`, `estado_caixa`,
                        `estado_factura`, `caixa_numero`, `doc`, `comissao`, `pagamento`, `lucro`, `nome`, SUM(`quantidade`),
                        `total_geral`, `preco_unitario`, `iva_produto`, `desconto_unitario`, `subtotal_produto`, `user`,
                        `prod_cod`, `custo` FROM FECHO_CAIXA_DETALHADA WHERE doc = "{}" and caixa_numero = '{}' 
                        GROUP BY nome order by numero""".format(cod, self.current_id)

                        total_sql = """SELECT cash, banco, tranferencia, lucro, total, troco FROM facturacao WHERE 
                        coddocumento = "{}" and caixa = '{}' order by numero """.format(
                            cod, self.current_id)

                        recibo_sql = """select recibos.numero, recibos.tranferencia, recibos.cash, recibos.banco, 
                                                                                        recibos.total, recibos.estado, clientes.nome, recibos.created from recibos 
                                                                                        INNER JOIN caixa on caixa.cod=recibos.caixa 
                                                                                        INNER JOIN clientes on clientes.cod=recibos.codcliente 
                                                                                        WHERE caixa.cod = '{}' order by recibos.numero""".format(
                            self.current_id)

                    else:
                        sql = """SELECT DISTINCT `valor_inicial`, `receitas`, `despesas`, `CRIADA_POR`, `FECHADA_POR`, `ABERTURA`, `FECHO`, `DOCUMENTO`, 
                        `numero`, `CLIENTE`, `subtotal`, `desconto`, `taxa`, SUM(`total`), `CHEQUE`, `NUMERARIO`, `POS`, `estado_caixa`,
                        `estado_factura`, `caixa_numero`, `doc`, `comissao`, `pagamento`, `lucro`, `nome`, SUM(`quantidade`),
                        `total_geral`, `preco_unitario`, `iva_produto`, `desconto_unitario`, `subtotal_produto`, `user`,
                        `prod_cod`, `custo` FROM FECHO_CAIXA_DETALHADA WHERE doc = "{}" and caixa_numero = '{}' 
                                                                        and user = "{}" GROUP BY nome order by numero""".format(
                            cod,
                            self.current_id,
                            self.user_combo.currentText())

                        total_sql = """SELECT cash, banco, tranferencia, lucro, total, troco FROM facturacao WHERE 
                        coddocumento = "{}" and created_by = "{}" AND caixa = '{}' order by numero """.format(
                            cod, self.user_combo.currentText(), self.current_id)

                        recibo_sql = """select recibos.numero, recibos.tranferencia, recibos.cash, recibos.banco, 
                                                                                        recibos.total, recibos.estado, clientes.nome, recibos.created from recibos 
                                                                                        INNER JOIN caixa on caixa.cod=recibos.caixa 
                                                                                        INNER JOIN clientes on clientes.cod=recibos.codcliente 
                                                                                        WHERE caixa.cod = '{}' AND recibos.created_by="{}" 
                                                                                        order by recibos.numero""".format(
                            self.current_id, self.user_combo.currentText())

                elif self.tipo_caixa == 2:

                    receitas, despesas = self.calcula_receitas_despesas_datas(
                        QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                        QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'))

                    if self.user_combo.currentText() == "Todos":
                        sql = """SELECT DISTINCT `valor_inicial`, `receitas`, `despesas`, `CRIADA_POR`, `FECHADA_POR`, `ABERTURA`, `FECHO`, `DOCUMENTO`, 
                        `numero`, `CLIENTE`, `subtotal`, `desconto`, `taxa`, SUM(`total`), `CHEQUE`, `NUMERARIO`, `POS`, `estado_caixa`,
                        `estado_factura`, `caixa_numero`, `doc`, `comissao`, `pagamento`, `lucro`, `nome`, SUM(`quantidade`),
                        `total_geral`, `preco_unitario`, `iva_produto`, `desconto_unitario`, `subtotal_produto`, `user`,
                        `prod_cod`, `custo` FROM FECHO_CAIXA_DETALHADA WHERE ABERTURA BETWEEN '{}' and '{}' 
                                                                    and doc = "{}" GROUP BY nome order by numero 
                                                                    """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), cod)

                        total_sql = """SELECT cash, banco, tranferencia, lucro, total, troco FROM facturacao WHERE 
                        created BETWEEN '{}' and '{}' and coddocumento = "{}" order by numero 
                        """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), cod)

                        recibo_sql = """select recibos.numero, recibos.tranferencia, recibos.cash, recibos.banco, 
                                                                                        recibos.total, recibos.estado, clientes.nome, recibos.created from recibos 
                                                                                        INNER JOIN caixa on caixa.cod=recibos.caixa 
                                                                                        INNER JOIN clientes on clientes.cod=recibos.codcliente 
                                                                                        WHERE recibos.created BETWEEN '{}' and '{}' 
                                                                                        order by recibos.numero
                                                                                        """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'))

                    else:
                        sql = """SELECT DISTINCT `valor_inicial`, `receitas`, `despesas`, `CRIADA_POR`, `FECHADA_POR`, `ABERTURA`, `FECHO`, `DOCUMENTO`, 
                        `numero`, `CLIENTE`, `subtotal`, `desconto`, `taxa`, SUM(`total`), `CHEQUE`, `NUMERARIO`, `POS`, `estado_caixa`,
                        `estado_factura`, `caixa_numero`, `doc`, `comissao`, `pagamento`, `lucro`, `nome`, SUM(`quantidade`),
                        `total_geral`, `preco_unitario`, `iva_produto`, `desconto_unitario`, `subtotal_produto`, `user`,
                        `prod_cod`, `custo` FROM FECHO_CAIXA_DETALHADA WHERE ABERTURA BETWEEN '{}' and '{}' 
                                                                    and doc = "{}" and user = "{}" GROUP BY nome order by numero 
                                                                    """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), cod,
                            self.user_combo.currentText())

                        total_sql = """SELECT cash, banco, tranferencia, lucro, total, troco FROM facturacao WHERE created BETWEEN '{}' and '{}' 
                                                                                            and coddocumento = "{}" and created_by = "{}" order by numero 
                                                                                            """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), cod,
                            self.user_combo.currentText())

                        recibo_sql = """select recibos.numero, recibos.tranferencia, recibos.cash, recibos.banco, 
                                                                                        recibos.total, recibos.estado, clientes.nome, recibos.created from recibos 
                                                                                        INNER JOIN caixa on caixa.cod=recibos.caixa 
                                                                                        INNER JOIN clientes on clientes.cod=recibos.codcliente 
                                                                                        WHERE recibos.created BETWEEN '{}' and '{}' 
                                                                                        AND recibos.created_by="{}" order by recibos.numero
                                                                                        """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), self.user_combo.currentText())


                self.cur.execute(sql)
                data = self.cur.fetchall()

                if len(data) > 0:

                    if contar == 0:
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

                        html += "<center align='left'>Data de Impressão: {}</center>".format(agora)
                        html += "<center align='left'>Data de abertura: {}</center>".format(data[0][5])
                        html += "<center align='left'>Data de Fecho: {}</center>".format(data[0][6])
                        html += "<center align='left'>Aberta por: {}</center>".format(data[0][3])
                        html += "<center align='left'>Fechada Por: {}</center>".format(data[0][4])

                        html += "<br/>"
                        html += "<center align='left'>VALOR INICIAL: {}</center>".format(data[0][0])
                        html += "<center align='left'>RECEITAS: {}</center>".format(receitas)
                        html += "<center align='left'>DESPESAS: {}</center>".format(despesas)
                        html += "<center align='left'>DESPESAS: {}</center>".format(despesas)

                        html += "<hr/>"
                        html += "<center align='left'>USUARIO: {}</center>".format(self.user_combo.currentText())
                        html += "<hr/>"

                    contar += 1

                    html += "<table border=0 width = 100% style='border: thin; style='font-size: 8px;''> " \
                            "<tr> <td> LISTA DE {}'s </tr> </td> </table>".format(str(nome).upper())

                    html += "<table border=0 width = 100% style='border: thin;'>"

                    html += "<tr style='background-color:#c0c0c0;'>"
                    html += "<th width = 10%>Qt. </th>"
                    html += "<th width = 70%>Descrição </th>"
                    html += "<th width = 20%>TOTAL </th>"
                    html += "</tr>"

                    for cliente in data:
                        # se o documento näo estiver cancelado / activa = 1
                        if int(cliente[18]) == 1:

                            subtotal_geral += decimal.Decimal(cliente[30])
                            taxa_geral += decimal.Decimal(cliente[28])
                            desconto_geral += decimal.Decimal(cliente[29])
                            total_geral += decimal.Decimal(cliente[26])

                            # Totais Gerais

                            html += """<tr style="font-size:8px;"> 
                            <td>{}</td> <td>{}</td> <td align="right">{:20,.2f}</td>    
                            </tr> """.format(cliente[25], cliente[24], cliente[25] *  cliente[26])
                        else:
                            html += """<tr style="background-color:red;font-size:8px;""> 
                            <td>{}</td> <td>{}</td> <td align="right">{:20,.2f}</td>    
                            </tr> """.format(cliente[25], cliente[24], cliente[25] * cliente[26])

                    self.cur.execute(total_sql)
                    data = self.cur.fetchall()

                    html += "</table>"

                    html += "<hr/>"

                    html += "<table border=0 width = 100% style='border: thin;'>"

                    cash_geral = 0
                    pos_geral = 0
                    movel_geral = 0
                    lucro_geral = 0
                    total_geral = 0
                    troco_geral = 0

                    for geral in data:

                        cash_geral += decimal.Decimal(geral[0])
                        pos_geral += decimal.Decimal(geral[1])
                        movel_geral += decimal.Decimal(geral[2])
                        lucro_geral += decimal.Decimal(geral[3])
                        total_geral += decimal.Decimal(geral[4])
                        troco_geral += decimal.Decimal(geral[5])

                        # Totais Gerais

                    html += """<tr> <td>TOTAL GERAL</td>
                                        <td align='right'><b>{:20,.2f}</b></td> </tr>""".format(
                        decimal.Decimal(total_geral))

                    html += """<tr> <td>CASH</td>
                                        <td align='right'><b>{:20,.2f}</b></td> </tr>""".format(
                        decimal.Decimal(cash_geral))

                    html += """<tr> <td>POS</td> 
                                        <td align='right'><b>{:20,.2f}</b></td> </tr>""".format(
                        decimal.Decimal(pos_geral))

                    html += """<tr> <td>MOVEL</td>
                                        <td align='right'><b>{:20,.2f}</b></td> </tr>""".format(
                        decimal.Decimal(movel_geral))

                    html += """<tr> <td>TROCOS</td>
                                        <td align='right'><b>{:20,.2f}</b></td></tr>""".format(
                        decimal.Decimal(troco_geral))

                    html += "</table>"

                    subtotal_geral = decimal.Decimal(0)
                    taxa_geral = decimal.Decimal(0)
                    desconto_geral = decimal.Decimal(0)
                    total_geral = decimal.Decimal(0)
                    total_pos = decimal.Decimal(0)
                    total_movel = decimal.Decimal(0)
                    total_numerario = decimal.Decimal(0)
                    total_lucro = decimal.Decimal(0)

            self.cur.execute(recibo_sql)
            recibo_data = self.cur.fetchall()

            if len(recibo_data) > 0:

                html += "<table border=0 width = 100% style='border: thin; style='font-size: 8px;''> " \
                        "<tr> <td> RECIBOS </tr> </td> </table>"

                html += "<table border=0 width = 100% style='border: thin;'>"

                html += "<tr style='background-color:#c0c0c0;'>"
                # html += "<th width = 10%>DOC</th>"
                html += "<th width = 10%>Data</th>"
                html += "<th width = 10%>Numero</th>"
                html += "<th width = 60%>CLIENTE</th>"
                html += "<th width = 20%>TOTAL</th>"

                html += "</tr>"

                for cliente in recibo_data:
                    # se o documento näo estiver cancelado / activa = 1
                    if int(cliente[5]) == 1:

                        total_geral += decimal.Decimal(cliente[4])

                        html += """<tr>  <td>{}</td> <td>{}</td> <td>{}</td> <td align="right">{:20,.2f}</td> 
                        </tr>""".format(QDateTime(cliente[7]).toString('dd-MM-yyyy'), cliente[0], cliente[6], cliente[4])
                    else:

                        html += """<tr style="background-color:red;">  
                        <td>{}</td> <td>{}</td> <td>{}</td> <td align="right">{:20,.2f}</td> 
                        </tr>""".format(QDateTime(cliente[7]).toString('dd-MM-yyyy'), cliente[0], cliente[6], cliente[4])

                html += "<tr> <td></td> <td></td>" \
                        "<td></td> <td align='right'><b>{:20,.2f}</b></td>  </tr> ".format(total_geral)
                html += "</table>"

            print(html)

            total_geral += decimal.Decimal(0)

            printer = QPrinter()
            printer.setPrinterName(self.parent().pos1)
            
            printer.setResolution(72)
            printer.setPaperSize(QSizeF(self.parent().papel_1,  3276), printer.Millimeter)
            printer.setPageMargins(0, 0, 10, 0, QPrinter.Millimeter)

            document = QTextDocument()
            document.setHtml(html)
            document.setPageSize(QSizeF(printer.pageRect().size()))

            dialog = QPrintDialog()
            document.print_(printer)
            dialog.accept()

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

    def imprime_caixa_resumida_pos(self):

        sql = """SELECT cod, nome from documentos """

        cont = 0
        for x in self.estado.findChildren(QCheckBox):
            if x.isChecked():
                if cont == 0:
                    sql += " WHERE cod='{}' ".format(x.objectName())
                else:
                    sql += " OR cod='{}' ".format(x.objectName())

                cont += 1

        self.cur.execute(sql)
        data = self.cur.fetchall()

        subtotal_geral = decimal.Decimal(0)
        taxa_geral = decimal.Decimal(0)
        desconto_geral = decimal.Decimal(0)
        total_geral = decimal.Decimal(0)
        total_pos = decimal.Decimal(0)
        total_movel = decimal.Decimal(0)
        total_numerario = decimal.Decimal(0)
        total_lucro = decimal.Decimal(0)

        html = """
                   <!DOCTYPE html>
                       <html lang="en">
                           <head>
                               <meta charset="UTF-8">
                               <title>Template de Recibos POS</title>
                           </head>

                           <body style="font-size:8px;">

               """

        if len(data) > 0:
            contar = 0
            for cod, nome in data:

                if self.tipo_caixa == 1:
                    receitas, despesas = self.calcula_receitas_despesas(self.current_id)

                    if self.user_combo.currentText() == "Todos":
                        sql = """SELECT * FROM FECHO_CAIXA WHERE doc = "{}" and caixa_numero = '{}' 
                                                order by numero""".format(cod, self.current_id)

                        total_sql = """SELECT cash, banco, tranferencia, lucro, total, troco FROM facturacao WHERE 
                        coddocumento = "{}" and caixa = '{}' order by numero """.format(
                            cod, self.current_id)

                        recibo_sql = """select recibos.numero, recibos.tranferencia, recibos.cash, recibos.banco, 
                                                                                        recibos.total, recibos.estado, clientes.nome, recibos.created from recibos 
                                                                                        INNER JOIN caixa on caixa.cod=recibos.caixa 
                                                                                        INNER JOIN clientes on clientes.cod=recibos.codcliente 
                                                                                        WHERE caixa.cod = '{}' order by recibos.numero""".format(
                            self.current_id)

                    else:
                        sql = """SELECT * FROM FECHO_CAIXA WHERE doc = "{}" and caixa_numero = '{}' 
                                                                        and user = "{}" order by numero""".format(
                            cod,
                            self.current_id,
                            self.user_combo.currentText())


                        total_sql = """SELECT cash, banco, tranferencia, lucro, total, troco FROM facturacao WHERE 
                        coddocumento = "{}" and created_by = "{}" AND caixa = '{}' order by numero """.format(
                            cod, self.user_combo.currentText(), self.current_id)

                        recibo_sql = """select recibos.numero, recibos.tranferencia, recibos.cash, recibos.banco, 
                                                                                        recibos.total, recibos.estado, clientes.nome, recibos.created from recibos 
                                                                                        INNER JOIN caixa on caixa.cod=recibos.caixa 
                                                                                        INNER JOIN clientes on clientes.cod=recibos.codcliente 
                                                                                        WHERE caixa.cod = '{}' AND recibos.created_by="{}" 
                                                                                        order by recibos.numero""".format(
                            self.current_id, self.user_combo.currentText())

                elif self.tipo_caixa == 2:
                    receitas, despesas = self.calcula_receitas_despesas_datas(
                        QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                        QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'))

                    if self.user_combo.currentText() == "Todos":
                        sql = """SELECT * FROM FECHO_CAIXA WHERE ABERTURA BETWEEN '{}' and '{}' 
                                                                    and doc = "{}" order by numero 
                                                                    """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), cod)

                        total_sql = """SELECT cash, banco, tranferencia, lucro, total, troco FROM facturacao WHERE 
                        created BETWEEN '{}' and '{}' and coddocumento = "{}" order by numero 
                        """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), cod)

                        recibo_sql = """select recibos.numero, recibos.tranferencia, recibos.cash, recibos.banco, 
                                                                                        recibos.total, recibos.estado, clientes.nome, recibos.created from recibos 
                                                                                        INNER JOIN caixa on caixa.cod=recibos.caixa 
                                                                                        INNER JOIN clientes on clientes.cod=recibos.codcliente 
                                                                                        WHERE recibos.created BETWEEN '{}' and '{}' 
                                                                                        order by recibos.numero
                                                                                        """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'))

                    else:
                        sql = """SELECT * FROM FECHO_CAIXA WHERE ABERTURA BETWEEN '{}' and '{}' 
                                                                    and doc = "{}" and user = "{}" order by numero 
                                                                    """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), cod,
                            self.user_combo.currentText())

                        total_sql = """SELECT cash, banco, tranferencia, lucro, total, troco FROM facturacao WHERE created BETWEEN '{}' and '{}' 
                                                                                            and coddocumento = "{}" and created_by = "{}" order by numero 
                                                                                            """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), cod,
                            self.user_combo.currentText())

                        recibo_sql = """select recibos.numero, recibos.tranferencia, recibos.cash, recibos.banco, 
                                                                                        recibos.total, recibos.estado, clientes.nome, recibos.created from recibos 
                                                                                        INNER JOIN caixa on caixa.cod=recibos.caixa 
                                                                                        INNER JOIN clientes on clientes.cod=recibos.codcliente 
                                                                                        WHERE recibos.created BETWEEN '{}' and '{}' 
                                                                                        AND recibos.created_by="{}" order by recibos.numero
                                                                                        """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), self.user_combo.currentText())

                self.cur.execute(sql)
                data = self.cur.fetchall()

                if len(data) > 0:

                    if contar == 0:
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

                        html += "<center align='left'>Data de Impressão: {}</center>".format(agora)
                        html += "<center align='left'>Data de abertura: {}</center>".format(data[0][5])
                        html += "<center align='left'>Data de Fecho: {}</center>".format(data[0][6])
                        html += "<center align='left'>Aberta por: {}</center>".format(data[0][3])
                        html += "<center align='left'>Fechada Por: {}</center>".format(data[0][4])

                        html += "<br/>"
                        html += "<center align='left'>VALOR INICIAL: {}</center>".format(data[0][0])
                        html += "<center align='left'>RECEITAS: {}</center>".format(receitas)
                        html += "<center align='left'>DESPESAS: {}</center>".format(despesas)

                        html += "<hr/>"
                        html += "<center align='left'>USUARIO: {}</center>".format(self.user_combo.currentText())
                        html += "<hr/>"

                    contar += 1

                    html += "<table border=0 width = 100% style='border: thin;'> " \
                            "<tr> <td> LISTA DE {}'s </tr> </td> </table>".format(str(nome).upper())

                    html += "<table border=0 width = 100% style='border: thin;'>"

                    html += "<tr style='background-color:#c0c0c0;'>"
                    html += "<th width = 10%>DOC </th>"
                    html += "<th width = 30%>NO. </th>"
                    html += "<th width = 60%>TOTAL </th>"
                    html += "</tr>"

                    for cliente in data:
                        # se o documento näo estiver cancelado / activa = 1
                        if int(cliente[18]) == 1:

                            subtotal_geral += decimal.Decimal(cliente[10])
                            taxa_geral += decimal.Decimal(cliente[12])
                            desconto_geral += decimal.Decimal(cliente[11])
                            total_geral += decimal.Decimal(cliente[13])
                            total_numerario += decimal.Decimal(cliente[15])
                            total_movel += decimal.Decimal(cliente[14])
                            total_pos += decimal.Decimal(cliente[16])

                            # Totais Gerais

                            html += """<tr> 
                            <td>{}</td> <td>{}</td> <td align="right">{:20,.2f}</td>    
                            </tr> """.format(cliente[7],"{}/{}".format(cliente[8], cliente[24]), cliente[13])
                        else:
                            html += """<tr style="background-color:red;"> 
                            <td>{}</td> <td>{}</td> <td align="right">{:20,.2f}</td>    
                            </tr> """.format(cliente[7],"{}/{}".format(cliente[8], cliente[24]), cliente[13])


                    html += "</table>"

                    html += "<hr/>"

                    html += "<table border=0 width = 100% style='border: thin;'>"

                    html += """<tr> <td>TOTAL GERAL</td>
                                        <td align='right'><b>{:20,.2f}</b></td> </tr>""".format(
                        decimal.Decimal(total_geral))

                    html += """<tr> <td>CASH</td>
                                        <td align='right'><b>{:20,.2f}</b></td> </tr>""".format(
                        decimal.Decimal(total_numerario))

                    html += """<tr> <td>POS</td> 
                                        <td align='right'><b>{:20,.2f}</b></td> </tr>""".format(
                        decimal.Decimal(total_pos))

                    html += """<tr> <td>MOVEL</td>
                                        <td align='right'><b>{:20,.2f}</b></td> </tr>""".format(
                        decimal.Decimal(total_movel))

                    html += "</table>"

                    subtotal_geral = decimal.Decimal(0)
                    taxa_geral = decimal.Decimal(0)
                    desconto_geral = decimal.Decimal(0)
                    total_geral = decimal.Decimal(0)
                    total_pos = decimal.Decimal(0)
                    total_movel = decimal.Decimal(0)
                    total_numerario = decimal.Decimal(0)

            self.cur.execute(recibo_sql)
            recibo_data = self.cur.fetchall()

            if len(recibo_data) > 0:

                html += "<table border=0 width = 100% style='border: thin; style='font-size: 8px;''> " \
                        "<tr> <td> RECIBOS </tr> </td> </table>"

                html += "<table border=0 width = 100% style='border: thin;'>"

                html += "<tr style='background-color:#c0c0c0;'>"
                # html += "<th width = 10%>DOC</th>"
                html += "<th width = 10%>Data</th>"
                html += "<th width = 10%>Numero</th>"
                html += "<th width = 60%>CLIENTE</th>"
                html += "<th width = 20%>TOTAL</th>"

                html += "</tr>"

                for cliente in recibo_data:
                    # se o documento näo estiver cancelado / activa = 1
                    if int(cliente[5]) == 1:

                        total_geral += decimal.Decimal(cliente[4])

                        html += """<tr>  <td>{}</td> <td>{}</td> <td>{}</td> <td align="right">{:20,.2f}</td> 
                        </tr>""".format(QDateTime(cliente[7]).toString('dd-MM-yyyy'), cliente[0], cliente[6], cliente[4])
                    else:

                        html += """<tr style="background-color:red;">  
                        <td>{}</td> <td>{}</td> <td>{}</td> <td align="right">{:20,.2f}</td> 
                        </tr>""".format(QDateTime(cliente[7]).toString('dd-MM-yyyy'), cliente[0], cliente[6], cliente[4])

                html += "<tr> <td></td> <td></td>" \
                        "<td></td> <td align='right'><b>{:20,.2f}</b></td>  </tr> ".format(total_geral)
                html += "</table>"

            html += """
                                </body>
                            </html>
                            """

            print(html)

            total_geral += decimal.Decimal(0)

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
            # font = QFont("Arial", 6)
            # document.setDefaultFont(font)
            # # document.setDefaultFont(QFont("{}".format(s[0]), 6))
            # # document.setDefaultFont(QFont("{}".format(s[0]), 6))
            document.setHtml(html)
            document.setPageSize(QSizeF(printer.pageRect().size()))

            dialog = QPrintDialog()
            document.print_(printer)
            dialog.accept()

    def exportar_caixa_csv(self):

        sql = """SELECT cod, nome from documentos """
        cont = 0
        for x in self.estado.findChildren(QCheckBox):
            if x.isChecked():
                if cont == 0:
                    sql += " WHERE cod='{}' ".format(x.objectName())
                else:
                    sql += " OR cod='{}' ".format(x.objectName())

                cont += 1

        self.cur.execute(sql)
        data = self.cur.fetchall()

        documentos = []

        list_data = []

        if len(data) > 0:
            for cod, nome in data:
                documentos.append(nome)
                if self.tipo_caixa == 1:

                    receitas, despesas = self.calcula_receitas_despesas(self.current_id)

                    if self.current_id is None:
                        QMessageBox.warning(self, "Erro. Nenhum registo selecionado.",
                                            "Escolha a caixa a imprimir na tabela")
                        return False

                    if self.user_combo.currentText() == "Todos":
                        sql = """SELECT prod_cod, nome, quantidade, preco_unitario, (quantidade * preco_unitario) as total, custo, (quantidade * preco_unitario - custo) AS lucro, documento, numero, cliente 
                        FROM fecho_caixa_detalhada WHERE doc = "{}" and caixa_numero = '{}' AND estado_factura = 1 
                        order by numero""".format(cod, self.current_id)

                        total_sql = """SELECT SUM(total), SUM(custo), SUM((total - custo)) AS lucro 
                        FROM fecho_caixa_detalhada WHERE caixa_numero = '{}' AND estado_factura = 1 
                        order by numero""".format(self.current_id)

                        recibo_sql = """select recibos.numero, recibos.tranferencia, 
                        recibos.cash, recibos.banco, 
                        recibos.total, recibos.estado, clientes.nome, recibos.created from recibos 
                        INNER JOIN caixa on caixa.cod=recibos.caixa 
                        INNER JOIN clientes on clientes.cod=recibos.codcliente 
                        WHERE caixa.cod = '{}' order by recibos.numero""".format(
                            self.current_id)

                    else:
                        sql = """SELECT prod_cod, nome, quantidade, preco_unitario, (quantidade * preco_unitario) as total, custo, (quantidade * preco_unitario - custo) AS lucro, documento, numero, cliente 
                        FROM fecho_caixa_detalhada WHERE doc = "{}" 
                        and caixa_numero = '{}' AND estado_factura = 1
                        and user = "{}" order by numero""".format(
                            cod,
                            self.current_id,
                            self.user_combo.currentText())

                        total_sql = """SELECT SUM(total), SUM(custo), SUM((total - custo)) AS lucro 
                        FROM fecho_caixa_detalhada WHERE caixa_numero = '{}' AND estado_factura = 1 
                        and user = "{}" order by numero""".format(
                            self.current_id,
                            self.user_combo.currentText())

                        recibo_sql = """select recibos.numero, recibos.tranferencia, recibos.cash, recibos.banco, 
                                        recibos.total, recibos.estado, clientes.nome, recibos.created from recibos 
                                        INNER JOIN caixa on caixa.cod=recibos.caixa 
                                        INNER JOIN clientes on clientes.cod=recibos.codcliente 
                                        WHERE caixa.cod = '{}' AND recibos.created_by="{}" 
                                        order by recibos.numero""".format(
                            self.current_id, self.user_combo.currentText())

                elif self.tipo_caixa == 2:
                    receitas, despesas = self.calcula_receitas_despesas_datas(
                        QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                        QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'))

                    if self.user_combo.currentText() == "Todos":
                        sql = """SELECT prod_cod, nome, quantidade, preco_unitario, (quantidade * preco_unitario) as total, custo, (quantidade * preco_unitario - custo) AS lucro, documento, numero, cliente 
                        FROM fecho_caixa_detalhada WHERE ABERTURA BETWEEN '{}' and '{}' 
                                                                    and doc = "{}" AND estado_factura = 1 
                                                                    order by numero 
                                                                    """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), cod)

                        total_sql = """SELECT SUM(total), SUM(custo), SUM((total - custo)) AS lucro 
                        FROM fecho_caixa_detalhada WHERE ABERTURA BETWEEN '{}' and '{}' 
                                                                    AND estado_factura = 1
                                                                     order by numero 
                                                                    """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'))

                        recibo_sql = """select recibos.numero, recibos.tranferencia, recibos.cash, recibos.banco, 
                            recibos.total, recibos.estado, clientes.nome, recibos.created from recibos 
                            INNER JOIN caixa on caixa.cod=recibos.caixa 
                            INNER JOIN clientes on clientes.cod=recibos.codcliente 
                            WHERE recibos.created BETWEEN '{}' and '{}' 
                            order by recibos.numero
                            """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'))
                    else:
                        sql = """SELECT prod_cod, nome, quantidade, preco_unitario, (quantidade * preco_unitario) as total, custo, (quantidade * preco_unitario - custo) AS lucro, documento, numero, cliente 
                        FROM fecho_caixa_detalhada WHERE ABERTURA BETWEEN '{}' and '{}' 
                                                                    and doc = "{}" and user = "{}" AND estado_factura = 1
                                                                     order by numero 
                                                                    """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), cod,
                            self.user_combo.currentText())

                        total_sql = """SELECT SUM(total), SUM(custo), SUM((total - custo)) AS lucro 
                        FROM fecho_caixa_detalhada WHERE ABERTURA BETWEEN '{}' and '{}' 
                                                                    AND user = "{}" AND estado_factura = 1
                                                                     order by numero 
                                                                    """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            self.user_combo.currentText())

                        recibo_sql = """select recibos.numero, recibos.tranferencia, recibos.cash, recibos.banco, 
                                                                                        recibos.total, recibos.estado, clientes.nome, recibos.created from recibos 
                                                                                        INNER JOIN caixa on caixa.cod=recibos.caixa 
                                                                                        INNER JOIN clientes on clientes.cod=recibos.codcliente 
                                                                                        WHERE recibos.created BETWEEN '{}' and '{}' 
                                                                                        AND recibos.created_by="{}" order by recibos.numero
                                                                                        """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), self.user_combo.currentText())

                self.cur.execute(sql)
                lista = self.cur.fetchall()
                data = [tuple(str(item) for item in t) for t in lista]

                self.cur.execute(total_sql)
                total = self.cur.fetchall()
                ttl = ['TOTAL', '', '', total[0][0], total[0][1], total[0][2]]

                for x in data:
                    list_data.append(x)

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(self, 'Guardar Ficheiro', '.', filter='Ficheiros CSV(*.csv)')

        if filename:
            ficheiro = filename
        else:
            QMessageBox.warning(self, 'Gravar Ficheiro', 'Ficheiro não foi gravado')
            return

        if ficheiro.endswith('.csv') is False:
            ficheiro += '.csv'

        caminho = os.path.realpath(ficheiro)

        csv_header = ["Codigo", "Item", "Qty", "Preço", "Total", "Custo", "Lucro"]

        action_label = QLabel("Exportando produtos. Aguarde.....")

        progressbar = QProgressDialog()
        progressbar.setLabel(action_label)
        progressbar.setMinimum(0)
        progressbar.setModal(True)
        progressbar.setCancelButtonText("Aguarde....")
        progressbar.setWindowTitle("Exportando para CSV")

        self.cur.execute(recibo_sql)
        recibo_lista = self.cur.fetchall()
        recibo_data = [tuple(str(item) for item in t) for t in recibo_lista]
        print(recibo_data)
        recibo_header = ["Data", "Documento","Cliente", "Total"]

        count = 0
        try:
            with open(ficheiro, 'w', newline='', encoding='utf8') as lista_produtos:
                csv_write = csv.writer(lista_produtos, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_write.writerow([self.parent().empresa])
                if self.tipo_caixa == 1:
                    csv_write.writerow(['Vendas do dia {}'.format(self.data_documento)])
                else:
                    csv_write.writerow(['Vendas de {} a {}'.format(self.data_inicial.dateTime().toString('dd-MM-yyyy'),
                                                                     self.data_final.dateTime().toString('dd-MM-yyyy'))])

                csv_write.writerow("")
                # csv_write.writerow(["Lista de Facturas"])

                progressbar.show()
                progressbar.setValue(1)

                # Variavel que controla o tipo de documento (Ex. Factura, VD) para diferenciar
                doc = None
                total = 0
                total_custo = 0
                total_lucro = 0

                if len(list_data) > 0:

                    progressbar.setMaximum(len(list_data) + len(recibo_data))
                    for y in documentos:
                        for x in list_data:
                            count += 1
                            progressbar.setValue(count)
                            lista = list(x)

                            if doc != y:
                                csv_write.writerow(["Lista de {}'s".format(y)])
                                header = csv_header + ['Documento', 'Número', 'Cliente']
                                csv_write.writerow(header)

                            doc = y

                            if lista[7] == y:
                                total += float(x[4])
                                total_custo += float(x[5])
                                total_lucro += float(x[6])

                                csv_write.writerow(lista)


                            action_label.setText("Exportando: {}. {}".format(count, lista[1]))
                        csv_write.writerow(["Total", "", "", "", total, total_custo, total_lucro])
                        csv_write.writerow([])
                        total = total_custo = total_lucro = 0

                csv_write.writerow([])

                total = 0
                if len(recibo_data) > 0:

                    csv_write.writerow([])
                    csv_write.writerow(["Lista de Recibos"])
                    csv_write.writerow(recibo_header)

                    for x in recibo_data:
                        #lista_nova = [QDateTime(x[7]).toString('dd-MM-yyyy'), x[0], x[6], x[4]]
                        lista_nova = [QDateTime.fromString(str(x[7]), 'yyyy-MM-dd H:mm:ss').toString('dd-MM-yyyy'), x[0], x[6], x[4]]
                        # lista = list(x)
                        total += float(x[4])
                        csv_write.writerow(lista_nova)
                        # action_label.setText("Exportando: {}. {}".format(count, lista[1]))

                    csv_write.writerow(['Total', '', '',total])

                progressbar.close()
                lista_produtos.close()

                subprocess.Popen(caminho, shell=True)

                QMessageBox.information(self, "Successo!", "Processo terminado com Sucesso!!!")
        except Exception as e:
            QMessageBox.warning(self, "Erro", "Erro: {}.\nVeja se o Ficheiro em causa não está aberto.".format(e))

    def exportar_caixa_csv_big(self):

        sql = """SELECT cod, nome from documentos """
        cont = 0
        for x in self.estado.findChildren(QCheckBox):
            if x.isChecked():
                if cont == 0:
                    sql += " WHERE cod='{}' ".format(x.objectName())
                else:
                    sql += " OR cod='{}' ".format(x.objectName())

                cont += 1

        print(sql)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        documentos = []
        lista_final = []

        if len(data) > 0:
            for cod, nome in data:
                documentos.append(nome)
                if self.tipo_caixa == 1:

                    receitas, despesas = self.calcula_receitas_despesas(self.current_id)

                    if self.current_id is None:
                        QMessageBox.warning(self, "Erro. Nenhum registo selecionado.",
                                            "Escolha a caixa a imprimir na tabela")
                        return False

                    if self.user_combo.currentText() == "Todos":
                        sql = """SELECT prod_cod, preco_unitario, quantidade 
                        FROM fecho_caixa_detalhada WHERE caixa_numero = '{}' AND doc="{}" AND estado_factura = 1 
                        order by numero""".format(self.current_id, cod)

                    else:
                        sql = """SELECT prod_cod, preco_unitario, quantidade 
                        FROM fecho_caixa_detalhada WHEREcaixa_numero = '{}' AND doc="{}" AND estado_factura = 1
                        and user = "{}" order by numero""".format(self.current_id,
                            self.user_combo.currentText(), cod)

                elif self.tipo_caixa == 2:

                    if self.user_combo.currentText() == "Todos":
                        sql = """SELECT prod_cod, preco_unitario, quantidade 
                        FROM fecho_caixa_detalhada WHERE ABERTURA BETWEEN '{}' and '{}' 
                                                                    AND doc="{}" AND estado_factura = 1 
                                                                    order by numero 
                                                                    """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), cod)

                    else:
                        sql = """SELECT prod_cod, preco_unitario, quantidade 
                        FROM fecho_caixa_detalhada WHERE ABERTURA BETWEEN '{}' and '{}' 
                                                                    and user = "{}" AND doc="{}" AND estado_factura = 1
                                                                     order by numero 
                                                                    """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            self.user_combo.currentText(), cod)

                print(sql)
                self.cur.execute(sql)
                lista = self.cur.fetchall()
                list_data = [tuple(str(item) for item in t) for t in lista]

                lista_final.append(list_data)

            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            filename, _ = QFileDialog.getSaveFileName(self, 'Guardar Ficheiro', '.', filter='Ficheiros CSV(*.csv)')

            if filename:
                ficheiro = filename
            else:
                QMessageBox.warning(self, 'Gravar Ficheiro', 'Ficheiro não foi gravado')
                return

            if ficheiro.endswith('.csv') is False:
                ficheiro += '.csv'

            caminho = os.path.realpath(ficheiro)

            csv_header = ["Codigo", "price", "Qty", "Product Variant", "tax rate", "discount", "sno"]

            action_label = QLabel("Exportando produtos. Aguarde.....")

            progressbar = QProgressDialog()
            progressbar.setLabel(action_label)
            progressbar.setMinimum(0)
            progressbar.setModal(True)
            progressbar.setCancelButtonText("Aguarde....")
            progressbar.setWindowTitle("Exportando para CSV")

            count = 0
            try:
                with open(ficheiro, 'w', newline='', encoding='utf8') as lista_produtos:
                    csv_write = csv.writer(lista_produtos, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    csv_write.writerow(csv_header)

                    if len(lista_final) > 0:

                        progressbar.setMaximum(len(lista_final))
                        progressbar.show()

                        for x in lista_final:
                            for y in x:
                                count += 1
                                progressbar.setValue(count)
                                action_label.setText("Exportando: {}. {}".format(count, lista_final[1]))
                                csv_write.writerow(y)

                progressbar.close()
                subprocess.Popen(caminho, shell=True)

                QMessageBox.information(self, "Sucesso", "Ficheiro esportado com Sucesso!")
            except Exception as e:
                QMessageBox.warning(self, "Erro", e)

    def exportar_resumo_caixa_csv(self):

        sql = """SELECT cod, nome from documentos """

        cont = 0
        for x in self.estado.findChildren(QCheckBox):
            if x.isChecked():
                if cont == 0:
                    sql += " WHERE cod='{}' ".format(x.objectName())
                else:
                    sql += " OR cod='{}' ".format(x.objectName())

                cont += 1

        self.cur.execute(sql)
        data = self.cur.fetchall()

        documentos = []

        list_data = []

        if len(data) > 0:
            for cod, nome in data:
                documentos.append(nome)
                if self.tipo_caixa == 1:

                    receitas, despesas = self.calcula_receitas_despesas(self.current_id)

                    if self.current_id is None:
                        QMessageBox.warning(self, "Erro. Nenhum registo selecionado.",
                                            "Escolha a caixa a imprimir na tabela")
                        return False

                    if self.user_combo.currentText() == "Todos":
                        sql = """SELECT distinct prod_cod, nome, sum(quantidade), preco_unitario, (sum(quantidade) * preco_unitario) as total, 
                        sum(quantidade) * custo, (sum(quantidade) * preco_unitario - sum(quantidade) * custo) AS lucro, documento, numero, cliente 
                        FROM fecho_caixa_detalhada WHERE doc = "{}" and caixa_numero = '{}' AND estado_factura = 1 
                        GROUP BY nome
                        order by numero""".format(cod, self.current_id)

                        total_sql = """SELECT SUM(total), SUM(custo), SUM((total - custo)) AS lucro 
                        FROM fecho_caixa_detalhada WHERE caixa_numero = '{}' AND estado_factura = 1 
                        order by numero""".format(self.current_id)

                        recibo_sql = """select recibos.numero, recibos.tranferencia, 
                        recibos.cash, recibos.banco, 
                        recibos.total, recibos.estado, clientes.nome, recibos.created from recibos 
                        INNER JOIN caixa on caixa.cod=recibos.caixa 
                        INNER JOIN clientes on clientes.cod=recibos.codcliente 
                        WHERE caixa.cod = '{}' order by recibos.numero""".format(
                            self.current_id)

                    else:
                        sql = """SELECT distinct prod_cod, nome, sum(quantidade), preco_unitario, (sum(quantidade) * preco_unitario) as total, 
                        sum(quantidade) * custo, (sum(quantidade) * preco_unitario - sum(quantidade) * custo) AS lucro, 
                        documento, numero, cliente 
                        FROM fecho_caixa_detalhada WHERE doc = "{}" 
                        and caixa_numero = '{}' AND estado_factura = 1
                        and user = "{}" 
                        GROUP BY nome
                        order by numero""".format(
                            cod,
                            self.current_id,
                            self.user_combo.currentText())

                        total_sql = """SELECT SUM(total), SUM(custo), SUM((total - custo)) AS lucro 
                        FROM fecho_caixa_detalhada WHERE caixa_numero = '{}' AND estado_factura = 1 
                        and user = "{}" order by numero""".format(
                            self.current_id,
                            self.user_combo.currentText())

                        recibo_sql = """select recibos.numero, recibos.tranferencia, recibos.cash, recibos.banco, 
                                        recibos.total, recibos.estado, clientes.nome, recibos.created from recibos 
                                        INNER JOIN caixa on caixa.cod=recibos.caixa 
                                        INNER JOIN clientes on clientes.cod=recibos.codcliente 
                                        WHERE caixa.cod = '{}' AND recibos.created_by="{}" 
                                        order by recibos.numero""".format(
                            self.current_id, self.user_combo.currentText())

                elif self.tipo_caixa == 2:
                    receitas, despesas = self.calcula_receitas_despesas_datas(
                        QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                        QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'))

                    if self.user_combo.currentText() == "Todos":
                        sql = """SELECT distinct prod_cod, nome, sum(quantidade), preco_unitario, (sum(quantidade) * preco_unitario) as total, 
                        sum(quantidade) * custo, (sum(quantidade) * preco_unitario - sum(quantidade) * custo) AS lucro, 
                        documento, numero, cliente 
                        FROM fecho_caixa_detalhada WHERE ABERTURA BETWEEN '{}' and '{}' 
                                                                    and doc = "{}" AND estado_factura = 1 
                                                                    GROUP BY nome
                                                                    order by numero 
                                                                    """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), cod)

                        total_sql = """SELECT SUM(total), SUM(custo), SUM((total - custo)) AS lucro 
                        FROM fecho_caixa_detalhada WHERE ABERTURA BETWEEN '{}' and '{}' 
                                                                    AND estado_factura = 1
                                                                     order by numero 
                                                                    """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'))

                        recibo_sql = """select recibos.numero, recibos.tranferencia, recibos.cash, recibos.banco, 
                            recibos.total, recibos.estado, clientes.nome, recibos.created from recibos 
                            INNER JOIN caixa on caixa.cod=recibos.caixa 
                            INNER JOIN clientes on clientes.cod=recibos.codcliente 
                            WHERE recibos.created BETWEEN '{}' and '{}' 
                            order by recibos.numero
                            """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'))
                    else:
                        sql = """SELECT distinct prod_cod, nome, sum(quantidade), preco_unitario, (sum(quantidade) * preco_unitario) as total, 
                        sum(quantidade) * custo, (sum(quantidade) * preco_unitario - sum(quantidade) *custo) AS lucro, documento, numero, cliente 
                        FROM fecho_caixa_detalhada WHERE ABERTURA BETWEEN '{}' and '{}' 
                                                                    and doc = "{}" and user = "{}" AND estado_factura = 1
                                                                    GROUP BY nome
                                                                    order by numero 
                                                                    """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), cod,
                            self.user_combo.currentText())

                        total_sql = """SELECT SUM(total), SUM(custo), SUM((total - custo)) AS lucro 
                        FROM fecho_caixa_detalhada WHERE ABERTURA BETWEEN '{}' and '{}' 
                                                                    AND user = "{}" AND estado_factura = 1
                                                                     order by numero 
                                                                    """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                            self.user_combo.currentText())

                        recibo_sql = """select recibos.numero, recibos.tranferencia, recibos.cash, recibos.banco, 
                                                                                        recibos.total, recibos.estado, clientes.nome, recibos.created from recibos 
                                                                                        INNER JOIN caixa on caixa.cod=recibos.caixa 
                                                                                        INNER JOIN clientes on clientes.cod=recibos.codcliente 
                                                                                        WHERE recibos.created BETWEEN '{}' and '{}' 
                                                                                        AND recibos.created_by="{}" order by recibos.numero
                                                                                        """.format(
                            QDateTime(self.data_inicial.dateTime()).toString('yyyy-MM-dd H:mm:ss'),
                QDateTime(self.data_final.dateTime()).toString('yyyy-MM-dd H:mm:ss'), self.user_combo.currentText())

                self.cur.execute(sql)
                lista = self.cur.fetchall()
                data = [tuple(str(item) for item in t) for t in lista]

                self.cur.execute(total_sql)
                total = self.cur.fetchall()
                ttl = ['TOTAL', '', '', total[0][0], total[0][1], total[0][2]]

                for x in data:
                    list_data.append(x)

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(self, 'Guardar Ficheiro', '.', filter='Ficheiros CSV(*.csv)')

        if filename:
            ficheiro = filename
        else:
            QMessageBox.warning(self, 'Gravar Ficheiro', 'Ficheiro não foi gravado')
            return

        if ficheiro.endswith('.csv') is False:
            ficheiro += '.csv'

        caminho = os.path.realpath(ficheiro)

        csv_header = ["Item", "Qty", "Preço", "Total", "Custo", "Lucro"]

        action_label = QLabel("Exportando produtos. Aguarde.....")

        progressbar = QProgressDialog()
        progressbar.setLabel(action_label)
        progressbar.setMinimum(0)
        progressbar.setModal(True)
        progressbar.setCancelButtonText("Aguarde....")
        progressbar.setWindowTitle("Exportando para CSV")

        self.cur.execute(recibo_sql)
        recibo_lista = self.cur.fetchall()
        recibo_data = [tuple(str(item) for item in t) for t in recibo_lista]
        print(recibo_data)
        recibo_header = ["Data", "Documento","Cliente", "Total"]

        count = 0
        try:
            with open(ficheiro, 'w', newline='', encoding='utf8') as lista_produtos:
                csv_write = csv.writer(lista_produtos, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_write.writerow([self.parent().empresa])
                if self.tipo_caixa == 1:
                    csv_write.writerow(['Vendas do dia {}'.format(self.data_documento)])
                else:
                    csv_write.writerow(['Vendas de {} a {}'.format(self.data_inicial.dateTime().toString('dd-MM-yyyy'),
                                                                     self.data_final.dateTime().toString('dd-MM-yyyy'))])

                csv_write.writerow("")
                # csv_write.writerow(["Lista de Facturas"])

                progressbar.show()
                progressbar.setValue(1)

                # Variavel que controla o tipo de documento (Ex. Factura, VD) para diferenciar
                doc = None
                total = 0
                total_custo = 0
                total_lucro = 0

                if len(list_data) > 0:

                    progressbar.setMaximum(len(list_data) + len(recibo_data))
                    for y in documentos:
                        for x in list_data:
                            count += 1
                            progressbar.setValue(count)
                            lista = list(x)

                            if doc != y:
                                csv_write.writerow(["Lista de {}'s".format(y)])
                                header = csv_header + ['Documento', 'Número', 'Cliente']
                                csv_write.writerow(header)

                            doc = y

                            if lista[6] == y:
                                total += float(x[3])
                                total_custo += float(x[4])
                                total_lucro += float(x[5])

                                csv_write.writerow(lista)


                            action_label.setText("Exportando: {}. {}".format(count, lista[1]))
                        csv_write.writerow(["Total", "", "", total, total_custo, total_lucro])
                        csv_write.writerow([])
                        total = total_custo = total_lucro = 0

                csv_write.writerow([])

                total = 0
                if len(recibo_data) > 0:

                    csv_write.writerow([])
                    csv_write.writerow(["Lista de Recibos"])
                    csv_write.writerow(recibo_header)

                    for x in recibo_data:
                        #lista_nova = [QDateTime(x[7]).toString('dd-MM-yyyy'), x[0], x[6], x[4]]
                        lista_nova = [QDateTime.fromString(str(x[7]), 'yyyy-MM-dd H:mm:ss').toString('dd-MM-yyyy'), x[0], x[6], x[4]]
                        # lista = list(x)
                        total += float(x[4])
                        csv_write.writerow(lista_nova)
                        # action_label.setText("Exportando: {}. {}".format(count, lista[1]))

                    csv_write.writerow(['Total', '', '',total])

                progressbar.close()
                lista_produtos.close()

                subprocess.Popen(caminho, shell=True)

                QMessageBox.information(self, "Successo!", "Processo terminado com Sucesso!!!")
        except Exception as e:
            QMessageBox.warning(self, "Erro", "Erro: {}.\nVeja se o Ficheiro em causa não está aberto.".format(e))

    def imprime_caixa(self):

        if self.current_id == "":
            return

        self.tipo_caixa = 1

        #try:
        if self.pos_print.isChecked():
            if self.list_de_produtos.isChecked():
                self.imprime_caixa_detalhada_pos()
            else:
                self.imprime_caixa_resumida_pos()
        else:
            if self.list_de_produtos.isChecked():
                self.imprime_caixa_detalhada()
            else:
                self.imprime_caixa_resumida()

        # except Exception as e:
        #     QMessageBox.warning(self, "Erro de Visualização", "Erro de visualização do relatório.\n{}.".format(e))

    def cria_checkboxes(self):

        # Retira as checkboxes para evitar duplicacao
        for check  in self.estado.findChildren(QCheckBox):
            self.estado.removeWidget(check)

        sql = """SELECT documentos.cod, documentos.nome, documentos.stock FROM documentos 
        JOIN facturacao on documentos.cod=facturacao.coddocumento GROUP BY documentos.cod"""
        self.cur.execute(sql)
        data = self.cur.fetchall()

        self.btn_documentos = QButtonGroup()
        self.btn_documentos.setExclusive(False)

        self.unfill(self.btn_layout)
        self.btn_widget = QWidget()
        self.btn_widget.setObjectName("checkboxes")

        try:
            self.estado.removeWidget(self.btn_widget)
        except Exception as e:
            print("Estou Livre")

        if len(data) > 0:
            for cod, nome, stock in data:
                butao = QCheckBox(str(nome), self)
                butao.setObjectName(str(cod))
                butao.setChecked(int(stock))
                butao.setToolTip(str(cod))

                self.btn_documentos.addButton(butao)

                self.btn_layout.addWidget(butao)

            self.btn_widget.setLayout(self.btn_layout)

    def unfill(self, lay):
        def deleteItems(layout):
            if layout is not None:
                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
                    else:
                        deleteItems(item.layout())

        deleteItems(lay)

    def imprime_lista_caixa(self):

        try:
            if self.pos_print.isChecked():
                if self.list_de_produtos.isChecked():
                    self.imprime_caixa_detalhada_pos()
                else:
                    self.imprime_caixa_resumida_pos()
            else:
                if self.list_de_produtos.isChecked():
                    self.imprime_caixa_detalhada()
                else:
                    self.imprime_caixa_resumida()
        except Exception as e:
            QMessageBox.warning(self, "Erro de Visualização", "Erro de visualização do relatório.\n{}.".format(e))


if __name__ == '__main__':

    app = QApplication(sys.argv)

    helloPythonWidget = MainWindow()
    helloPythonWidget.show()

    sys.exit(app.exec_())