import sys

from PyQt5.QtWidgets import (QDialog, QLabel, QVBoxLayout, QToolBar, QMessageBox, QLineEdit,
    QAction, QApplication, QGridLayout, QComboBox, QGroupBox, QPushButton, QPlainTextEdit,
                             QCalendarWidget, QDateEdit, QFormLayout, QHBoxLayout, QWidget)

from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog, QPrinterInfo
from PyQt5.QtCore import Qt, QSizeF, QDate
from PyQt5.QtGui import QIcon, QFont, QTextDocument, QPaintDevice

from maindialog import Dialog
from pricespinbox import price


TEMPO = ['Horas', 'Dias', 'Semanas', 'Meses', 'Anos']
class Cursos(Dialog):
    def __init__(self, parent=None, titulo="Cursos", imagem="icons/Folder.ico"):
        super(Cursos, self).__init__(parent, titulo, imagem)

        self.current_id = 0

        if self.parent() is None:
            self.db = self.connect_db()
        else:
            self.cur = self.parent().cur
            self.conn = self.parent().conn
            self.user = self.parent().user

        self.accoes()
        self.ui()

    def ui(self):

        self.nome = QLineEdit()
        self.nome.setMaxLength(255)
        calendar1 = QCalendarWidget()
        calendar2 = QCalendarWidget()
        self.data_inicial = QDateEdit()
        self.data_inicial.setCalendarPopup(True)
        self.data_inicial.setCalendarWidget(calendar1)
        self.data_inicial.setDate(QDate.currentDate().addDays(-30))
        self.data_final = QDateEdit()
        self.data_final.setCalendarPopup(True)
        self.data_final.setCalendarWidget(calendar2)
        self.data_final.setDate(QDate.currentDate())
        self.duracao = price()
        self.duracao_combo = QComboBox()
        duracaolay = QHBoxLayout()
        duracaolay.setContentsMargins(0, 0, 0, 0)
        duracaolay.addWidget(self.duracao)
        duracaolay.addWidget(self.duracao_combo)
        duracaoWidget = QWidget()
        duracaoWidget.setLayout(duracaolay)
        self.duracao_combo.addItems(TEMPO)
        self.valor = price()
        self.percentagem = price()
        self.percentagem.setRange(0, 100)
        self.obs = QPlainTextEdit()

        formlay = QFormLayout()
        formlay.setContentsMargins(10, 10, 10, 10)
        formlay.addRow(QLabel("Designação"), self.nome)
        # formlay.addRow(QLabel("Data de Início"), self.data_inicial)
        # formlay.addRow(QLabel("Data de Término"), self.data_final)
        # formlay.addRow(QLabel("Duração"), duracaoWidget)
        formlay.addRow(QLabel("Valor"), self.valor)
        formlay.addRow(QLabel("Nota Mínima (0-100)"), self.percentagem)
        formlay.addRow(QLabel("Comentários"), self.obs)

        self.layout().addLayout(formlay)
        self.layout().addWidget(self.tool)

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

    def mostrar_registo(self):

        sql = """SELECT * FROM cursos WHERE cod={} """.format(self.current_id)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                self.nome.setText(item[1])
                self.data_inicial.setDate(item[2])
                self.data_final.setDate(item[3])
                self.duracao.setValue(item[4])
                self.valor.setValue(item[5])
                self.percentagem.setValue(item[6])
                self.obs.setPlainText(item[7])

            return True

        return False

    def limpar(self):
        for child in (self.findChildren(QLineEdit) or self.findChildren(QPlainTextEdit)):
            if child.objectName() not in ["cod", "cal1", "cal2"]: child.clear()

    def connect_db(self):
        pass

    def validacao(self):

        if str(self.nome.text()) == "":
            QMessageBox.warning(self, "Erro", "Designação do Curso inválido")
            self.nome.setFocus()
            return False
        else:
            return True

    def addRecord(self):

        if self.validacao() is True:
            nome = self.nome.text()
            data_inicial = QDate.currentDate().toString("yyyy-MM-dd")
            data_final = QDate.currentDate().toString("yyyy-MM-dd")
            duracao = 0
            valor = self.valor.value()
            percentagem = self.percentagem.value()
            obs = self.obs.toPlainText()
            estado = 1
            created = QDate.currentDate().toString("yyyy-MM-dd")
            modified = QDate.currentDate().toString("yyyy-MM-dd")
            modified_by = self.user
            created_by = self.user

            code = self.current_id

            if self.existe(code):

                sql = """UPDATE cursos SET nome="{nome}", data_inicio="{data_inicio}", data_final="{data_final}", 
                duracao="{duracao}", valor="{valor}", percentagem="{percentagem}", obs="{obs}", estado={estado}, 
                modified="{modified}", modified_by="{modified_by}" 
                WHERE cod="{cod}" """.format(nome=nome, data_inicio=data_inicial, data_final=data_final,
                                             duracao=duracao, valor=valor, percentagem=percentagem,
                                             obs=obs, estado=estado, modified=modified, modified_by=modified_by,
                                             cod=code)

            else:
                values = """ "{nome}", "{data_inicio}", "{data_final}", "{duracao}", "{valor}", "{percentagem}", 
                "{obs}", {estado}, "{created}", "{modified}", "{modified_by}", "{created_by}" 
                """.format(nome=nome, data_inicio=data_inicial, data_final=data_final, duracao=duracao, valor=valor,
                           percentagem=percentagem,
                           obs=obs, estado=estado, created=created,
                           modified=modified, modified_by=modified_by,
                           created_by=created_by)

                sql = """INSERT INTO cursos (nome, data_inicio, data_final, duracao, valor, percentagem, obs, estado, 
                created, modified, modified_by, created_by) VALUES ({}) """.format(values)

            try:
                self.cur.execute(sql)
                self.conn.commit()

                if QMessageBox.question(self, "Pergunta", "Registo Gravado com sucesso!\nDeseja Cadastrar outro Item?",
                                        QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                    self.limpar()
                else:
                    self.close()

                return True
            except Exception as e:
                self.conn.rollback()
                print(e)
                return False

    def existe(self, codigo):

        sql = """SELECT cod from cursos WHERE cod="{codigo}" """.format(codigo=str(codigo))

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            self.current_id = codigo
            return False
        else:
            codigo = data[0][0]
            self.current_id = codigo
            return True

if __name__ == '__main__':
    app = QApplication(sys.argv)
    cursos = Cursos()
    cursos.show()
    sys.exit(app.exec_())
