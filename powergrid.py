# -*- coding: utf-8 -*-

import sys
import subprocess
import os
import csv
import time
import datetime

from PyQt5.QtWidgets import QApplication, QMessageBox, QToolBar, \
    QLineEdit, QLabel, QStatusBar, QAction, QMainWindow, qApp, QFileDialog, QProgressDialog, QMenu, \
    QButtonGroup, QCheckBox, QVBoxLayout, QFrame

from PyQt5.QtGui import QIcon, QTextDocument
from PyQt5.QtCore import Qt, QDate, QObject, QThread, pyqtSignal, QPoint, QSettings
from PyQt5.QtPrintSupport import QPrintPreviewDialog
from PyQt5 import QtGui

from striped_table import StripedTable
from sortmodel import MyTableModel
import send_sms


def get_contacts(lista, pos: int):
    """
    Retorna contactos da Lista de retornada pela Base de Dados
    :param lista: Lista da Base de datos
    :param pos: Posicao da coluna que contem contactos
    :return: Lista de Contactos
    """
    contacts = []
    for x in lista:
        c = x[pos]

        if c != 'None' and c != '':
            contacts.append(c)

    return contacts


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.conn = self.parent().conn
        self.cur = self.parent().cur
        self.user = self.parent().user

        self.empresa = self.parent().empresa

        self.empresa_logo = self.parent().empresa_logo
        self.empresa_slogan = self.parent().empresa_slogan
        self.empresa_endereco = self.parent().empresa_endereco
        self.empresa_contactos = self.parent().empresa_contactos
        self.empresa_email = self.parent().empresa_email
        self.empresa_web = self.parent().empresa_web
        self.empresa_nuit = self.parent().empresa_nuit

        # Dialog form new, update and delete data
        self.child_form = QObject

        # the table that we a working on
        self.table_name = None

        # The default value that cannot be deleted because it belongs to system
        self.defautl_table_id = None

        # Table Header
        self.table_header = []

        # Table Data
        self.table_data = []

        self.table_default_columns = (1,  2, 5, 10, 11, 12)
        # The id of the table, normally is the primary key
        self.current_id = None

        # Sets the User Interface
        self.ui()
        self.addToolBar(self.toolbar_2)

        self.setStyleSheet('QCheckBox {border: 1px solid blue; background-color: white;}')
        print(self.styleSheet())

    def ui(self):
        # create the view
        self.tv = StripedTable()

        headers = self.tv.horizontalHeader()
        headers.setContextMenuPolicy(Qt.CustomContextMenu)

        self.tv.enterEvent = self.get_pos

        headers.customContextMenuRequested.connect(lambda: self.header_popup(QPoint(self.m_x, self.m_y)))

        self.tv.doubleClicked.connect(lambda: self.update_data(self.current_id, self.child_form))
        self.tv.setFocus()
        self.tv.clicked.connect(self.clicked_slot)

        self.setCentralWidget(self.tv)
        self.create_toolbar()

    def get_pos(self, event):
        self.m_x = event.pos().x()
        self.m_y = event.pos().y()

    def header_popup(self, pos):
        context_menu = QMenu()
        layout = self.create_header_context(self.table_header)
        context_menu.setLayout(layout)
        context_menu.exec_(self.mapToGlobal(pos))

    def create_toolbar(self):
        find = QLabel(qApp.tr("Procurar") + "  ")
        self.search_data = QLineEdit(self)
        self.search_data.setMaximumWidth(300)

        self.new = QAction(QIcon('img/add.png'), qApp.tr("Novo (F2)"), self)
        self.new.setShortcut("Ctrl+N")
        self.new.triggered.connect(lambda: self.new_data(self.child_form))
        self.delete = QAction(QIcon('img/delete.png'), qApp.tr("Eliminar (F4)"), self)
        self.delete.setShortcut("Ctrl+D")
        self.delete.triggered.connect(lambda: self.remove_row(self.table_name, self.defautl_table_id))

        self.update = QAction(QIcon('img/edit.png'), qApp.tr("Editar (F3)"), self)
        self.update.setShortcut("Ctrl+U")
        self.update.triggered.connect(lambda: self.update_data(self.current_id, self.child_form))

        self.print = QAction(QIcon('img/print.png'), qApp.tr("Imprimir (F6)"), self)

        self.print.setShortcut("Ctrl+P")

        self.export_csv = QAction(QIcon('img/export_csv.png'),qApp.tr("Exportar para CSV (F7)"), self)
        self.export_csv.setShortcut("Ctrl+S")

        self.sms_action = QAction(QIcon("img/smartphone.png"), "&AVISAR", self)
        self.sms_action.triggered.connect(self.send_text_sms)
        self.sms_action.setToolTip('Avisar aos clientes sobre o Fim da Mensalidade')

        self.total_items = QLabel("0: Items")

        self.toolbar = QToolBar()
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toolbar.setContextMenuPolicy(Qt.PreventContextMenu)

        self.toolbar.addWidget(find)
        self.toolbar.addWidget(self.search_data)
        
        self.toolbar.addAction(self.new)
        self.toolbar.addAction(self.update)
        self.toolbar.addAction(self.delete)

        self.toolbar.setAllowedAreas(Qt.BottomToolBarArea)
        self.addToolBarBreak(Qt.TopToolBarArea)
        self.addToolBar(self.toolbar)

        self.toolbar_2 = QToolBar()
        self.toolbar_2.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toolbar_2.setContextMenuPolicy(Qt.PreventContextMenu)
        self.toolbar_2.addAction(self.print)
        self.toolbar_2.addAction(self.export_csv)
        self.toolbar_2.addAction(self.sms_action)

        self.addToolBarBreak(Qt.TopToolBarArea)

        self.statusbar = QStatusBar()
        self.statusbar.addWidget(self.total_items)
        self.setStatusBar(self.statusbar)

    def clicked_slot(self, index):

        self.row = int(index.row())
        indice = self.tm.index(self.row, 0)
        self.current_id = indice.data()

        return self.current_id

    def fill_table(self, header: list, lista: list, hidden_columns=()):

        if len(lista) == 0:
            # header = ['',  ]
            lista = ['']

        try:
            self.tm = MyTableModel(lista, header, self)
            # set the table model
            self.totalItems = self.tm.rowCount(self)
            self.tv.setModel(self.tm)
            # # set row height
            nrows = len(lista)
            for row in range(nrows):
                self.tv.setRowHeight(row, 25)

            for h in hidden_columns:
                self.tv.setColumnHidden(h, True)

            return True
        except Exception as e:
            print(e)
            return False

    def new_data(self, form):
        cl = form(self)
        cl.setModal(True)
        cl.show()

    def update_data(self, row_id, form):

        if row_id == "":
            QMessageBox.information(self, "Info", "Selecione o registo a actualizar na tabela")
            return

        cl = form(self)
        cl.cod.setText(row_id)
        cl.mostrar_registo()
        cl.setModal(True)
        cl.show()

    def remove_row(self, tablename, default_value):
        data = self.selected_rows()

        if len(data) == 0:
            QMessageBox.information(self, "Info", "Selecione o registo a apagar na tabela")
            return False

        if QMessageBox.question(self, "Pergunta",
                                str("Deseja eliminar {} registo(S) selecionado(s)?").format(len(data)),
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
            return False

        for d in data:
            if d != default_value:

                sql = """delete from {table} WHERE cod = "{codigo}" """.format(codigo=str(d), table=tablename)

                try:
                    self.cur.execute(sql)
                    self.conn.commit()
                    self.enche_items()
                    self.fill_table(self.table_header, self.table_data)
                except Exception as e:
                    QMessageBox.warning(self, "Erro", "Impossivel apagar cliente.\n{}.".format(e))
                    return False
            else:
                QMessageBox.warning(self, "Erro", "Registo não pode ser apagado.")
                return False

        QMessageBox.information(self, "Sucesso", "Item(s) apagado(s) com sucesso...")
        return True
    
    def create_header_context(self, header_list):
       
        self.btn_grp = QButtonGroup()
        self.btn_grp.setExclusive(False)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Mostrar/Ocultar Colunas'))
        layout.addWidget(self.add_line())

        for x in header_list:
            self.btn = QCheckBox(str(x), self)
            self.btn.setObjectName(str(header_list.index(str(x))))
            df = [str(x) for x in self.table_default_columns]
            if self.btn.objectName() in df:
                self.btn.setEnabled(False)
                self.btn.setChecked(True)

            self.btn.setToolTip(str(x))
            layout.addWidget(self.btn)

            self.btn_grp.addButton(self.btn)

        self.btn_grp.buttonClicked.connect(lambda: self.on_click(self.btn.text()))

        return layout

    def on_click(self, i):
        print(i)

    def enche_items(self):
       pass

    def add_line(self):

        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setObjectName("line")

        return line

    def contextMenuEvent(self, event):
        context_menu = QMenu()
        context_menu.addAction(self.new)
        context_menu.addAction(self.update)
        context_menu.addAction(self.delete)
        context_menu.addAction(self.print)
        context_menu.addAction(self.export_csv)
        context_menu.exec_(self.mapToGlobal(event.pos()))

    def export_para_csv(self):
        if len(self.table_data) == 0:
            return False

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

        action_label = QLabel("Exportando Lista. Aguarde.....")

        progressbar = QProgressDialog()
        progressbar.setLabel(action_label)
        progressbar.setMinimum(0)
        progressbar.setModal(True)
        progressbar.setCancelButtonText("Aguarde....")
        progressbar.setWindowTitle("Exportando para CSV")

        try:
            with open(ficheiro, 'w', newline='', encoding='utf8') as lista_produtos:
                csv_write = csv.writer(lista_produtos, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_write.writerow([self.empresa])
                csv_write.writerow([self.empresa_endereco])
                csv_write.writerow([f'Contato(s): {self.empresa_contactos}'])
                csv_write.writerow([f'NUIT: {self.empresa_nuit}'])
                csv_write.writerow([self.empresa_slogan])
                csv_write.writerow([])
                csv_write.writerow(['DATA: {}'.format(QDate.currentDate().toString('dd-MMM-yyyy'))])
                csv_write.writerow([])
                csv_write.writerow(self.table_header)
                progressbar.show()
                progressbar.setValue(1)

                data = self.table_data

                col = []

                if len(data) > 0:
                    progressbar.setMaximum(len(data))

                    for r in data:
                        progressbar.setValue(progressbar.value() + 1)
                        col.append(progressbar.value())
                        csv_write.writerow(r)

                progressbar.close()
                lista_produtos.close()

                subprocess.Popen(caminho, shell=True)

                QMessageBox.information(self, "Successo!", "Processo terminado com Sucesso!!!")

        except Exception as e:
            QMessageBox.warning(self, "Erro", "Erro: {}.\nVeja se o Ficheiro em causa não está aberto.".format(e))

    def imprimir_lista(self, template, data=None, header=None):

        if data is None:
            data = []

        if header is None:
            header = []

        if len(data) == 0:
            return False

        import codecs

        file = codecs.open(template, encoding="utf-8")
        content = file.read()

        progress = QProgressDialog()
        progress.setMinimum(0)
        progress.setMaximum(len(data))
        progress.show()

        count = 1

        head = "<th>#</th>"
        for h in header:
            head += "<th>{}</th>".format(h)

        colunas = len(data[0][0])

        html = ""
        for r in data:
            html += "<tr><td>{}</td>".format(count)
            for x in range(colunas):
                html += "<td>{}</td>".format(r[x])
                progress.setValue(count)

            count += 1
            html += "</tr>"
            # print(html)

        items = html

        recibo = content.format(logo=self.empresa_logo, empresa_nome=self.empresa,
        empresa_endereco=self.empresa_endereco,
        empresa_contactos=self.empresa_contactos,
        empresa_nuit=self.empresa_nuit,
        empresa_slogan=self.empresa_slogan,items=items, header=head)

        progress.close()

        return recibo

    def preview_dialog(self, html):
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker()
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(lambda: self.worker.run(html))
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

        # Final resets
        self.print.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.print.setEnabled(True)
        )

    def send_text_sms(self):
        if len(self.table_data) == 0:
            return False

        sms = send_sms.SendSMSDialog(self)
        sms.cell_serial_number = self.cell_serial_number
        sms.sms_time_sleep = self.temposms

        if sms.connect_android_devices() is False:
            return False

        ct = get_contacts(self.table_data, 8)

        contacts = ''

        for c in ct:
            contacts += str(c) + ';'

        sms.recipients.setPlainText(contacts)
        sms.message.setPlainText(self.smsmensalidade)
        sms.setModal(True)
        sms.show()

        return True

    def keyPressEvent(self, event) -> None:
        try:
            if event.key() == Qt.Key_F2:
                if self.new.isEnabled() or self.new.isVisible():
                    self.new_data(self.child_form)
            elif event.key() in (Qt.Key_F3, Qt.Key_Enter, 16777220):
                if self.update.isEnabled() or self.update.isVisible():
                    self.update_data(self.current_id, self.child_form)

            elif event.key() in  (Qt.Key_F4, Qt.Key_Delete):
                if self.delete.isEnabled() or self.delete.isVisible():
                    self.remove_row(self.table_name, self.defautl_table_id)
            elif event.key() == Qt.Key_F5:
                self.fill_table(self.table_header, self.table_data)
            elif event.key() == Qt.Key_F6:
                self.imprimir_lista('templates/admin/pessoal_template.html', self.table_data, self.table_header)
            elif event.key() == Qt.Key_F7:
                self.export_para_csv()
            else:
                event.ignore()
        except Exception as e:
            print(e)

    def selected_rows(self):
        select = self.tv.selectionModel()
        data = []

        if select.hasSelection():
            rows = select.selectedRows()

            for r in rows:
                id = self.tm.index(r.row(), 0)
                data.append(id.data())

        return data


class Worker(QObject):
    finished = pyqtSignal()

    def run(self, html):
        print(datetime.datetime.now())
        print('Running Long Task')
        print('Starting QDocument')
        document = QTextDocument()
        document.setDocumentMargin(.5)
        document.setHtml(html)
        print('Creating Print Dialog')
        dlg = QPrintPreviewDialog()
        dlg.paintRequested.connect(document.print_)
        print('Showing dialog')
        dlg.showMaximized()
        dlg.exec_()

        print('Finish')
        print(time.time())
        self.finished.emit()
        print(datetime.datetime.now())


if __name__ == '__main__':

    app = QApplication(sys.argv)

    helloPythonWidget = MainWindow()
    helloPythonWidget.show()

    sys.exit(app.exec_())