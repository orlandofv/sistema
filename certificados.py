import sys

from PyQt5.QtWidgets import (QDialog, QLabel, QVBoxLayout, QToolBar, QMessageBox, QLineEdit,
                             QAction, QApplication, QGridLayout, QComboBox, QGroupBox, QPushButton, QPlainTextEdit,
                             QCalendarWidget, QDateEdit, QFormLayout, QHBoxLayout, QWidget)

from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog, QPrinterInfo
from PyQt5.QtCore import Qt, QSizeF, QDate
from PyQt5.QtGui import QIcon, QFont, QTextDocument, QPaintDevice

from maindialog import Dialog
from pricespinbox import price

RESULTADOS = ["Comp", "N YC"]
COMPORTAMENTO = ["BOM", "MAU", "EXCELENTE"]
LISTA_DE_ESTUDANTES = []
LISTA_DE_INSTRUTOR = []
LISTA_DE_FORMACAO = []


class Certificado(Dialog):
    def __init__(self, parent=None, titulo="Certificado", imagem="icons/save.ico"):
        super(Certificado, self).__init__(parent, titulo, imagem)

        self.current_id = 0
        self.cod_estudante = ""
        self.cod_instrutor = ""
        self.cod_empresa = ""
        self.cod_curso = 0
        self.percentagem_curso = 0

        if self.parent() is None:
            self.db = self.connect_db()
        else:
            self.cur = self.parent().cur
            self.conn = self.parent().conn
            self.user = self.parent().user

        self.accoes()
        self.ui()
        self.enche_formacao()
        self.get_cod_curso(self.cod_curso)

    def enche_cursos(self, cod_formacao):

        sql = """SELECT cursos.nome from cursos INNER JOIN formacao 
        ON cursos.cod=formacao.codcurso where formacao.cod="{}" """.format(cod_formacao)

        

        self.cur.execute(sql)
        data = self.cur.fetchall()

        lista = []
        self.curso.clear()

        if len(data) > 0:
            for item in data:
                lista.append(item[0])

                self.curso.addItems(lista)

        return lista

    def enche_formacao(self):

        sql = """SELECT cod, nome from formacao order by nome"""
        self.cur.execute(sql)
        data = self.cur.fetchall()

        self.formacao.clear()

        lista = []
        LISTA_DE_FORMACAO.clear()

        if len(data) > 0:
            for item in data:
                lista.append(str(item[1]))
                LISTA_DE_FORMACAO.append(str(item[0]))

            self.formacao.addItems(lista)

            return True

        return False

    def enche_empresas(self, cod_formacao):

        sql = """SELECT clientes.nome from clientes INNER JOIN formacao ON clientes.cod=formacao.codempresa 
        WHERE formacao.cod="{}" """.format(cod_formacao)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        self.empresa.clear()
        lista = []
        if len(data) > 0:
            for item in data:
                lista.append(item[0])

        self.empresa.addItems(lista)

        return lista

    def enche_estudantes(self, empresa_cod, formacao_cod):

        sql = """SELECT estudantes.cod, estudantes.nome, estudantes.apelido from estudantes 
        INNER JOIN formacao ON estudantes.cod=formacao.codestudante 
        WHERE estudantes.empresa="{}" AND formacao.cod={} AND formacao.valor_saldo<=0 
        order by nome""".format(empresa_cod, formacao_cod)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        self.estudante.clear()
        lista = []
        LISTA_DE_ESTUDANTES.clear()

        if len(data) > 0:
            for item in data:
                lista.append(str(item[0]) + " - " + str(item[1]) + ", " + str(item[2]))
                LISTA_DE_ESTUDANTES.append(str(item[0]))

            self.estudante.addItems(lista)
            return True

        return False

    def set_empresa(self, cod_empresa):

        sql = """SELECT nome FROM clientes WHERE cod="{}" order by nome""".format(cod_empresa)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        nome = ""

        if len(data) > 0:
            for item in data:
                nome = str(item[0])

        return nome

    def set_curso(self, cod_curso):

        sql = """SELECT nome FROM cursos WHERE cod="{}" order by nome""".format(cod_curso)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        nome = ""

        if len(data) > 0:
            for item in data:
                nome = str(item[0])

        return nome

    def set_estudante(self, cod_estudante):

        sql = """SELECT cod, nome, apelido from estudantes WHERE cod="{}" order by nome""".format(cod_estudante)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        nome = ""

        if len(data) > 0:
            for item in data:
                nome = str(item[0]) + " - " + str(item[1]) + ", " + str(item[2])

        return nome

    def get_cod_estudante(self, index):
        self.cod_estudante = LISTA_DE_ESTUDANTES[index]

        return self.cod_estudante

    def get_cod_formacao(self, nome):
        sql = """SELECT cod FROM formacao WHERE nome="{}" """.format(nome)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            self.cod_formacao = data[0][0]

        self.enche_cursos(self.cod_formacao)
        self.enche_empresas(self.cod_formacao)
        self.enche_instrutor(self.cod_formacao)
        self.enche_empresas(self.cod_formacao)
        self.enche_estudantes(self.cod_empresa, self.cod_formacao)
        self.get_cod_curso(self.curso.currentText())

        return self.cod_formacao

    def set_instrutor(self, cod_instrutor):

        sql = """SELECT cod, nome, apelido from instrutores WHERE cod="{}" order by nome""".format(cod_instrutor)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        nome = ""

        if len(data) > 0:
            for item in data:
                nome = str(item[0]) + " - " + str(item[1]) + ", " + str(item[2])

        return nome

    def enche_instrutor(self, cod_formacao):

        sql = """SELECT instrutores.cod, instrutores.nome, instrutores.apelido FROM instrutores
        INNER JOIN FORMACAO ON instrutores.cod=formacao.instrutor
        WHERE formacao.cod="{}" order by instrutores.nome""".format(cod_formacao)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        self.instrutor.clear()

        lista = []
        LISTA_DE_INSTRUTOR.clear()

        if len(data) > 0:
            for item in data:
                lista.append(str(item[0]) + " - " + str(item[1]) + ", " + str(item[2]))
                LISTA_DE_INSTRUTOR.append(str(item[0]))

            self.instrutor.addItems(lista)

            return True

        return False

    def get_cod_instrutor(self, index):
        self.cod_instrutor = LISTA_DE_INSTRUTOR[index]

        return self.cod_instrutor

    def get_cod_empresa(self, nome):
        sql = """SELECT cod from clientes WHERE nome="{}" order by nome""".format(nome)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            self.cod_empresa = data[0][0]
            self.enche_estudantes(self.cod_empresa, self.cod_formacao)
            return self.cod_empresa

        return ""

    def get_cod_curso(self, nome_curso):

        sql = """SELECT cursos.cod, formacao.valor, cursos.percentagem,  formacao.valor_primeira,
        formacao.valor_segunda, formacao.valor_saldo, formacao.teoria, formacao.pratica FROM cursos 
        INNER JOIN formacao ON cursos.cod=formacao.codcurso WHERE cursos.nome="{}" AND formacao.codestudante="{}"
        order by cursos.nome asc""".format(nome_curso, self.cod_estudante)
        self.cur.execute(sql)

        data = self.cur.fetchall()

        if len(data) > 0:
            self.cod_curso = data[0][0]
            self.valor.setValue(data[0][1])
            self.valor_primeira.setValue(data[0][3])
            self.valor_segunda.setValue(data[0][4])
            self.avalicao_teorica.setValue(data[0][6])
            self.avalicao_pratica.setValue(data[0][7])
            self.percentagem_curso = data[0][2]

            self.calcula_resultado()

            return self.cod_curso

        return 0

    def calcula_resultado(self):

        if self.percentagem_curso <= (self.avalicao_teorica.value() + self.avalicao_pratica.value()):
            self.resultado.setCurrentIndex(0)
        else:
            self.resultado.setCurrentIndex(1)

    def get_preco_curso(self, codcurso):
        sql = """SELECT valor FROM formacao WHERE cod={} """.format(codcurso)
        self.cur.execute(sql)

        data = self.cur.fetchall()

        if len(data) > 0:
            return data[0][0]

        return 0

    def calcula_valor(self):

        if self.valor_primeira.hasFocus():
            self.valor_primeira.setRange(0, self.valor.value() - self.valor_segunda.value())
        elif self.valor_segunda.hasFocus():
            self.valor_segunda.setRange(0, self.valor.value() - self.valor_primeira.value())
        elif self.valor.hasFocus():
            self.valor_primeira.setValue(0)
            self.valor_segunda.setValue(0)

        return self.valor_saldo.setValue(self.valor.value() - self.valor_primeira.value() - self.valor_segunda.value())

    def verifica_afectacao(self):

        sql = """SELECT * from formacao where nome="{}" and codcurso={} and codestudante="{}" and codempresa="{}" 
        """.format(self.nome.text(), self.cod_curso, self.cod_estudante, self.cod_empresa)

        self.cur.execute(sql)

        data = self.cur.fetchall()

        if len(data) > 0:
            return True

        return False

    def validacao(self):

        if self.nome.text() == "":
            QMessageBox.warning(self, "Erro", "Designação do inválida")
            self.nome.setFocus()
            return False

        if self.estudante.currentText() == "":
            QMessageBox.warning(self, "Erro", "Cadastre Estudantes Primeiro")
            return False

        if self.curso.currentText() == "":
            QMessageBox.warning(self, "Erro", "Cadastre Cursos Primeiro")
            return False

        if self.empresa.currentText() == "":
            QMessageBox.warning(self, "Erro", "Cadastre Empresas Primeiro")
            return False

        return True

    def addRecord(self):

        if self.validacao() is True:
            nome = self.nome.text()
            cod_empresa = self.cod_empresa
            cod_curso = self.cod_formacao
            cod_estudante = self.cod_estudante
            obs = self.obs.toPlainText()
            estado = 1
            created = QDate.currentDate().toString("yyyy-MM-dd")
            modified = QDate.currentDate().toString("yyyy-MM-dd")
            modified_by = self.user
            created_by = self.user
            code = self.current_id
            instrutor = self.cod_instrutor
            data_certificado = self.data_certificado.date().toString("yyyy-MM-dd")
            validade = self.validade.date().toString("yyyy-MM-dd")

            if self.existe(code):

                sql = """UPDATE certificado SET numero="{nome}", codformacao="{cod_curso}", codempresa="{cod_empresa}",  
                codestudante="{cod_estudante}", data="{data}", validade={validade}, obs="{obs}", estado={estado}, 
                modified="{modified}", modified_by="{modified_by}" 
                WHERE cod="{cod}" """.format(nome=nome, cod_curso=cod_curso, cod_empresa=cod_empresa,
                                             cod_estudante=cod_estudante, data=data_certificado, validade=validade,
                                             obs=obs, estado=estado, modified=modified, modified_by=modified_by,
                                             instrutor=instrutor, cod=code)

            else:
                if self.verifica_afectacao() is True:
                    QMessageBox.warning(self, "Erro", "O Estudante ja está afecto na Certificado.")
                    return False

                values = """ "{nome}", {cod_curso}, "{cod_empresa}", "{cod_estudante}", "{data}", "{validade}", "{obs}", 
                {estado}, "{created}", "{modified}", "{modified_by}", "{created_by}"
                """.format(nome=nome, cod_curso=cod_curso, cod_empresa=cod_empresa,
                           cod_estudante=cod_estudante, data=data_certificado, validade=validade,
                           obs=obs, estado=estado, created=created, modified=modified, modified_by=modified_by,
                           created_by=created_by)

                sql = """INSERT INTO certificado (numero, codformacao, codempresa, codestudante, data, validade, 
                obs, estado, created, modified, modified_by, 
                created_by) VALUES ({}) """.format(values)

            try:
                self.cur.execute(sql)
                self.conn.commit()

                if QMessageBox.question(self, "Pergunta", "Registo Gravado com sucesso!\nDeseja Cadastrar outro Item?",
                                        QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
                    self.close()

                return True
            except Exception as e:
                self.conn.rollback()
                QMessageBox.warning(self, "Erro", "Erro na gravação de dados.\n{}.".format(e))
                return False

    def existe(self, codigo):

        sql = """SELECT cod from formacao WHERE cod="{codigo}" """.format(codigo=str(codigo))

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            self.current_id = codigo
            return False
        else:
            codigo = data[0][0]
            self.current_id = codigo
            return True

    def ui(self):
        self.nome = QLineEdit()
        self.nome.setMaxLength(150)
        self.formacao = QComboBox()
        self.formacao.currentIndexChanged.connect(lambda: self.get_cod_formacao(self.formacao.currentText()))
        self.curso = QComboBox()
        self.curso.currentIndexChanged.connect(lambda: self.get_cod_curso(self.curso.currentText()))
        self.empresa = QComboBox()
        self.empresa.currentIndexChanged.connect(lambda: self.get_cod_empresa(self.empresa.currentText()))
        self.estudante = QComboBox()
        self.estudante.currentIndexChanged.connect(lambda: self.get_cod_estudante(self.estudante.currentIndex()))
        self.instrutor = QComboBox()
        self.instrutor.currentIndexChanged.connect(lambda: self.get_cod_instrutor(self.instrutor.currentIndex()))
        self.valor = price()
        self.valor.valueChanged.connect(self.calcula_valor)
        self.valor_primeira = price()
        self.valor_primeira.valueChanged.connect(self.calcula_valor)
        self.valor_segunda = price()
        self.valor_segunda.valueChanged.connect(self.calcula_valor)
        self.valor_saldo = price()
        self.valor_saldo.setEnabled(False)
        self.avalicao_teorica = price()
        self.avalicao_teorica.setRange(0, 100)
        self.avalicao_teorica.valueChanged.connect(self.calcula_resultado)
        self.avalicao_pratica = price()
        self.avalicao_pratica.valueChanged.connect(self.calcula_resultado)
        self.avalicao_pratica.setRange(0, 100)
        self.comportamento = QComboBox()
        self.comportamento.addItems(COMPORTAMENTO)
        self.resultado = QComboBox()
        self.resultado.addItems(RESULTADOS)
        self.obs = QPlainTextEdit()

        cal = QCalendarWidget()
        cal2 = QCalendarWidget()

        self.data_certificado = QDateEdit()
        self.data_certificado.setDate(QDate.currentDate())
        self.data_certificado.setCalendarPopup(True)
        self.data_certificado.setCalendarWidget(cal)
        self.validade = QDateEdit()
        self.validade.setDate(QDate.currentDate())
        self.validade.setCalendarPopup(True)
        self.validade.setCalendarWidget(cal2)

        formlay = QFormLayout()
        formlay.setContentsMargins(10, 10, 10, 10)

        formlay.addRow(QLabel("Nº de Certificado"), self.nome)
        formlay.addRow(QLabel("Formação"), self.formacao)
        formlay.addRow(QLabel("Escolha o Curso"), self.curso)
        formlay.addRow(QLabel("Escolha a Empresa"), self.empresa)
        formlay.addRow(QLabel("Escolha o Estudante"), self.estudante)
        formlay.addRow(QLabel("Escolha o Instrutor"), self.instrutor)
        formlay.addRow(QLabel("Data de Certificação"), self.data_certificado)
        formlay.addRow(QLabel("Data de Validade"), self.validade)
        formlay.addRow(QLabel("Valor a Pagar"), self.valor)
        formlay.addRow(QLabel("Valor da 1ª Prestação"), self.valor_primeira)
        formlay.addRow(QLabel("Valor da 2ª Prestação"), self.valor_segunda)
        formlay.addRow(QLabel("Saldo"), self.valor_saldo)
        formlay.addRow(QLabel("Avaliação Teórica"), self.avalicao_teorica)
        formlay.addRow(QLabel("Avaliação Prática"), self.avalicao_pratica)
        formlay.addRow(QLabel("Comportamento"), self.comportamento)
        formlay.addRow(QLabel("Resultado"), self.resultado)
        formlay.addRow(QLabel("comentários"), self.obs)

        self.layout().addLayout(formlay)
        self.layout().addWidget(self.tool)

    def mostrar_registo(self):

        sql = """SELECT formacao.cod, formacao.nome, cursos.nome, clientes.nome, estudantes.nome, 
        formacao.valor, formacao.valor_primeira, formacao.valor_segunda, 
        formacao.valor_saldo, formacao.teoria, formacao.pratica,
        formacao.comportamento, formacao.resultado, formacao.obs, instrutores.cod, instrutores.nome, instrutores.apelido 
        FROM formacao
        INNER JOIN cursos ON cursos.cod=formacao.codcurso INNER JOIN clientes ON clientes.cod=formacao.codempresa
        INNER JOIN estudantes ON estudantes.cod=formacao.codestudante 
        INNER JOIN instrutores ON instrutores.cod=formacao.instrutor WHERE formacao.cod={}
        """.format(self.current_id)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                self.nome.setText(item[1])
                self.curso.setCurrentText(item[2])
                self.empresa.setCurrentText(item[3])
                self.estudante.setCurrentText(item[4])
                self.valor.setValue(item[5])
                self.valor_primeira.setValue(item[6])
                self.valor_segunda.setValue(item[7])
                self.valor_saldo.setValue(item[8])
                self.avalicao_teorica.setValue(item[9])
                self.avalicao_pratica.setValue(item[10])
                self.comportamento.setCurrentText(item[11])
                self.resultado.setCurrentText(item[12])
                self.obs.setPlainText(item[13])
                self.instrutor.setCurrentText(str(item[14]) + " - " + str(item[15]) + ", " + str(item[16]))

            return True

        return False

    def accoes(self):
        self.tool = QToolBar()
        self.tool.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.tool.setContextMenuPolicy(Qt.PreventContextMenu)

        gravar = QAction(QIcon("./images/ok.png"), "Gravar\nDados", self)
        eliminar = QAction(QIcon("icons/new.ico"), "Limpar\nCampos", self)

        fechar = QAction(QIcon("./images/filequit.png"), "&Fechar", self)

        self.tool.addAction(gravar)
        self.tool.addAction(eliminar)

        self.tool.addSeparator()
        self.tool.addAction(fechar)

        gravar.triggered.connect(self.addRecord)
        eliminar.triggered.connect(self.limpar)
        fechar.triggered.connect(self.close)

    def limpar(self):
        for child in (self.findChildren(QLineEdit) or self.findChildren(QPlainTextEdit)):
            if child.objectName() not in ["cod", "cal1", "cal2"]: child.clear()

    def connect_db(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    formacao = Certificado()
    formacao.show()
    sys.exit(app.exec_())