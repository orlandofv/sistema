import sys
import subprocess
import csv
import os

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog, QProgressDialog, QLabel, QAction
from PyQt5.QtPrintSupport import QPrintPreviewDialog
from PyQt5.QtGui import QTextDocument, QIcon
from lista_de_estudantes import ListaDeEstudantes
from formacao import Formacao
from sortmodel import MyTableModel


class ListaDeFormacao(ListaDeEstudantes):
    def __init__(self, parent=None):
        super(ListaDeEstudantes, self).__init__(parent)

        if self.parent() is None:
            self.db = self.connect_db()
        else:
            self.cur = self.parent().cur
            self.conn = self.parent().conn
            self.user = self.parent().user

        self.ui()
        self.find_w.textChanged.connect(self.fill_table)
        export_csv = QAction(QIcon('./images/icons8-export-csv-50.png'), "Exportar para CSV", self)
        export_csv.triggered.connect(self.exportar_csv)
        self.tool.addAction(export_csv)
        self.setWindowTitle("Lista de Formações")

    def fill_table(self):

        header = ("cod", "Nome & Apelido ", "Empresa", "Formação", "Curso", "Instrutor", "Valor a Pagar", "1ª Prestação", "2ª Prestação",
                  "Saldo", "Res. Teórico", "Res. Prático", "Comportamento", "Resultado", "Comentários")

        self.sql = """SELECT formacao.cod,  concat(estudantes.nome, " ", estudantes.apelido), clientes.nome, 
        formacao.nome, cursos.nome, concat(instrutores.nome, " ", instrutores.apelido), formacao.valor, 
        formacao.valor_primeira, formacao.valor_segunda, 
        formacao.valor_saldo, formacao.teoria, formacao.pratica,
        formacao.comportamento, formacao.resultado, formacao.obs FROM formacao
        INNER JOIN cursos ON cursos.cod=formacao.codcurso INNER JOIN clientes ON clientes.cod=formacao.codempresa
        INNER JOIN estudantes ON estudantes.cod=formacao.codestudante 
        INNER JOIN instrutores ON instrutores.cod=formacao.instrutor
        WHERE formacao.nome LIKE "%{nome}%" OR estudantes.nome LIKE "%{nome}%"  OR estudantes.apelido LIKE "%{nome}%"
        OR clientes.nome LIKE "%{nome}%" OR cursos.nome LIKE "%{nome}%" 
        OR instrutores.nome LIKE "%{nome}%" """.format(nome=self.find_w.text())

        print(self.sql)

        try:
            self.cur.execute(self.sql)
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]
        except Exception as e:
            return

        if len(data) == 0:
            self.tabledata = ["", "", "", "", "", "", ""]
        else:
            self.tabledata = data

        try:
            self.tm = MyTableModel(self.tabledata, header, self)
            # set the table model
            self.totalItems = self.tm.rowCount(self)
            self.tv.setModel(self.tm)
            self.tv.setColumnHidden(0, True)
        except Exception as e:
            return
        # # set row height
        nrows = len(self.tabledata)
        for row in range(nrows):
            self.tv.setRowHeight(row, 25)
        self.create_statusbar()

    def new_data(self):

        f = Formacao(self)
        cursos = f.enche_cursos()
        empresas = f.enche_empresas()
        f.curso.addItems(cursos)
        f.empresa.addItems(empresas)
        f.show()

    def update_data(self):
        if self.current_id == "":
            QMessageBox.warning(self, "Erro", "Escolha registo que deseja actualizar na tabela")
            return

        f = Formacao(self)
        f.current_id = self.current_id
        cursos = f.enche_cursos()
        empresas = f.enche_empresas()
        f.curso.addItems(cursos)
        f.empresa.addItems(empresas)
        f.mostrar_registo()
        f.show()

    def enterEvent(self, *args, **kwargs):
        self.fill_table()

    def exportar_csv(self):

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

        self.cur.execute(self.sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        csv_header = ("cod", "Nome & Apelido ", "Empresa", "Formação", "Curso", "Instrutor",
                      "Valor a Pagar", "1ª Prestação", "2ª Prestação", "Saldo", "Res. Teórico",
                      "Res. Prático", "Comportamento", "Resultado", "Comentários")

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
                csv_write = csv.writer(lista_produtos, delimiter=',', quotechar='"',
                                       quoting=csv.QUOTE_MINIMAL, dialect='excel')
                csv_write.writerow(csv_header)
                progressbar.show()
                progressbar.setValue(1)

                if len(data) > 0:
                    progressbar.setMaximum(len(data))
                    for x in data:
                        count += 1
                        progressbar.setValue(count)
                        lista = list(x)
                        csv_write.writerow(lista)

                        action_label.setText("Exportando: {}. {}".format(count, lista[1]))
                progressbar.close()
                lista_produtos.close()

                subprocess.Popen(caminho, shell=True)

                QMessageBox.information(self, "Successo!", "Processo terminado com Sucesso!!!")
        except Exception as e:
            QMessageBox.warning(self, "Erro", "Erro: {}.\nVeja se o Ficheiro em causa não está aberto.".format(e))

    def imprime_lista(self):
        """Imprime no ecra a Lista geral de produtos baseado em um Critério"""
        if self.sql == "":
            return

        self.cur.execute(self.sql)
        dados = self.cur.fetchall()

        html = "<center> <h2> Lista de Estudantes </h2> </center>"
        html += "<hr/>"

        html += "<br/>"

        html += "<table border=0 width='100%' style='border: thin;'>"
        html += "<tr style='background-color:#c0c0c0;'>"
        html += "<th width = 10%>Nome</th>"
        html += "<th width = 10%>Empresa</th>"
        html += "<th width = 10%>Formação</th>"
        html += "<th width = 10%>Curso</th>"
        html += "<th width = 10%>Valor</th>"
        html += "<th width = 10%>1ª Prest.</th>"
        html += "<th width = 10%>2ª Prest.</th>"
        html += "<th width = 10%>Saldo</th>"
        html += "<th width = 5%>Teoria</th>"
        html += "<th width = 5%>Prática</th>"
        html += "<th width = 5%>Comp.</th>"
        html += "<th width = 10%>Res.</th>"
        html += "<th width = 10%>Comentários</th>"
        html += "</tr>"

        for cliente in dados:
            html += """<tr> <td>{}</td><td>{}</td><td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td>
                            <td>{}</td><td>{}</td><td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td>   
                    </tr>""".format(cliente[1], cliente[2], cliente[3], cliente[4], cliente[5], cliente[6], cliente[7],
                                    cliente[8], cliente[9], cliente[10], cliente[11], cliente[12], cliente[13])
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    lista = ListaDeFormacao()
    lista.show()
    sys.exit(app.exec_())