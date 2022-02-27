import decimal
import sys
import datetime
import os
from time import localtime, strftime, localtime
from utilities import printWordDocument, Invoice
from relatorio.templates.opendocument import Template
from utilities import codigo as cd

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtPrintSupport import QPrintPreviewDialog
from PyQt5.QtGui import QTextDocument
from lista_de_estudantes import ListaDeEstudantes
from certificados import Certificado
from sortmodel import MyTableModel


class ListaDeCertificados(ListaDeEstudantes):
    def __init__(self, parent=None):
        super(ListaDeCertificados, self).__init__(parent)

        if self.parent() is None:
            self.db = self.connect_db()
        else:
            self.cur = self.parent().cur
            self.conn = self.parent().conn
            self.user = self.parent().user

        self.ui()
        self.find_w.textChanged.connect(self.fill_table)
        self.setWindowTitle("Lista de Formações")

    def fill_table(self):

        header = ("No. Certificado", "Formacao", "Teoria", "Pratica", "Comportamento", "Data", "Validade", "OPERADOR", "Empresa", "Comentários")

        self.sql = """SELECT certificado.numero, formacao.nome, formacao.teoria, formacao.pratica, 
        formacao.resultado, certificado.data, certificado.validade, 
        concat(estudantes.nome, " ", estudantes.apelido), clientes.nome, certificado.obs FROM certificado
        INNER JOIN clientes ON clientes.cod=certificado.codempresa
        INNER JOIN estudantes ON estudantes.cod=certificado.codestudante
        INNER JOIN formacao ON formacao.cod=certificado.codformacao 
        WHERE certificado.numero LIKE "%{nome}%" 
        OR estudantes.nome LIKE "%{nome}%"  
        OR estudantes.apelido LIKE "%{nome}%"
        OR clientes.nome LIKE "%{nome}%" """.format(nome=self.find_w.text())

        try:
            self.cur.execute(self.sql)
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]
        except Exception as e:
            print(e)
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

        f = Certificado(self)
        # cursos = f.enche_cursos()
        # empresas = f.enche_empresas()
        # f.curso.addItems(cursos)
        # f.empresa.addItems(empresas)
        f.show()

    def update_data(self):
        if self.current_id == "":
            QMessageBox.warning(self, "Erro", "Escolha registo que deseja actualizar na tabela")
            return

        f = Certificado(self)
        f.current_id = self.current_id
        # f.mostrar_registo()
        f.show()

    def imprime_recibo_grande2(self, codigo):

        sql = """SELECT * FROM factura_geral WHERE codfacturacao = '{}' """.format(codigo)
        data = ["Carlos", "Formacao", "Blala"]
        inv = Invoice(customer={'name': 'Orlando Vilanculo',
                                'address': {'street': 'Smirnov street', 'zip': 1000, 'city': 'Montreux'}},
                      nome=data[0],
                      clienteendereco=data[1],
                      clientenome=data[2]
                      )

        # Verifica o Ficheiro de entrada Template
        filename = os.path.realpath('template.odt')
        if os.path.isfile(filename) is False:
            QMessageBox.critical(self, "Erro ao Imprimir",
                                 "O ficheiro modelo '{}'  não foi encontrado.".format(filename))
            return


        targetfile = "certificado.odt"

        if os.path.isfile(targetfile) is False:
            QMessageBox.critical(self, "Erro ao Imprimir",
                                 "O ficheiro modelo '{}'  não foi encontrado. \n "
                                 "Reponha-o para poder Imprimir".format(targetfile))
            return

        basic = Template(source='', filepath=targetfile)
        open(filename, 'wb').write(basic.generate(o=inv).render().getvalue())

        doc_out = cd("0123456789") + "{}{}{}{}".format(data[0][2], data[0][1], data[0][23], data[0][22])
        out = os.path.realpath("'{}'.pdf".format(doc_out))

        printWordDocument(filename, out)

    def enterEvent(self, *args, **kwargs):
        self.fill_table()

    def imprime_lista(self):
        """Imprime no ecra a Lista geral de produtos baseado em um Critério"""
        if self.sql == "":
            return

        self.cur.execute(self.sql)
        dados = self.cur.fetchall()

        html = "<center> <h2> Lista de Certificados </h2> </center>"
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
    lista = ListaDeCertificados()
    lista.show()
    sys.exit(app.exec_())