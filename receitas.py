from time import strftime, localtime
from decimal import Decimal
from PyQt5.QtWidgets import (QRadioButton, QLabel, QLineEdit, QFormLayout, QVBoxLayout, QToolBar, QMessageBox,
                             QPlainTextEdit, QAction, QApplication, QComboBox, QPushButton, QFileDialog, QHBoxLayout,
                             QGroupBox, QGridLayout, QSizePolicy, QWidget, QDialog, QStackedWidget)
from PyQt5.QtCore import Qt, QDate, QRegExp
from PyQt5.QtGui import QFont, QRegExpValidator
import sys

from teclado_numerico import Teclado
from pricespinbox import price

TRANSACOES = ["Despesas", "Receitas"]

DATA_HORA_FORMATADA = strftime("%Y-%m-%d %H:%M:%S", localtime())

class DespesasReceitas(QDialog):
    def __init__(self, parent=None):
        super(DespesasReceitas, self).__init__(parent)

        if self.parent() is not None:
            self.user = self.parent().user
            self.codarmazem = self.parent().codarmazem
            self.caixa_numero = self.parent().caixa_numero
            self.cur = self.parent().cur
            self.conn = self.parent().conn
        else:
            self.user = None
            self.codarmazem = None
            self.caixa_numero = None
            self.cur = None
            self.conn = None

        self.cod_receita = 0
        self.created = DATA_HORA_FORMATADA
        self.modified = DATA_HORA_FORMATADA

        self.tipo_de_transacao = 0  # 0 para despesa e 1 para receita
        self.descricao = ""  # Pode ser pagamento de agua, luz, outros valores, etc
        self.obs = ""  # Notas sobre a transacao
        self.valor_da_transacao = Decimal(0)
        self.valor_anterior = Decimal(0)  # Valor anterior para o caso de update

        self.ui()

    def ui(self):

        # regex = QRegExp("^(?:\d+\.?\d*|\d*\.?\d+)*$")
        # validator = QRegExpValidator(regex)

        self.combo_tipo_trasacao = QComboBox()
        self.combo_tipo_trasacao.addItems(TRANSACOES)

        self.line_descricao = QLineEdit()
        self.line_descricao.setMaxLength(255)
        self.spin_valor = price()
        self.txt_obs = QPlainTextEdit()

        boldFont = self.txt_obs.font()
        boldFont.setBold(True)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.add_record)
        cancelar_button = QPushButton("C&ancelar")
        cancelar_button.clicked.connect(self.close)

        descricao = QLabel("Descrição")
        descricao.setFont(boldFont)

        valor = QLabel("Valor")
        valor.setFont(boldFont)

        form_lay = QFormLayout()
        form_lay.addRow(QLabel("Transação:"), self.combo_tipo_trasacao)
        form_lay.addRow(descricao, self.line_descricao)
        form_lay.addRow(valor, self.spin_valor)
        form_lay.addRow(QLabel("Notas"), self.txt_obs)

        btn_lay = QHBoxLayout()
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        btn_lay.addWidget(spacer)
        btn_lay.addWidget(ok_button)
        btn_lay.addWidget(cancelar_button)

        main_lay = QVBoxLayout()
        main_lay.addLayout(form_lay)
        main_lay.addLayout(btn_lay)

        self.setLayout(main_lay)
        self.setWindowTitle("Despesas e Receitas")

    def validar_dados(self):

        if self.line_descricao.text() == "":
            QMessageBox.warning(self, "Erro de Validação",
                                "Descrição não pode estar vazia.\nExecução não pode continuar")
            self.line_descricao.setFocus()
            return False

        if Decimal(self.spin_valor.value()) == Decimal(0) :
            QMessageBox.warning(self, "Erro de Validação",
                                "Valor deve ser maior que Zero(0).\nExecução não pode continuar")
            self.spin_valor.setFocus()
            return False

        return True

    def add_record(self):

        if self.conn is None:
            QMessageBox.warning(self, "Erro de Base de dados",
                                "Nenhuma conexão com base de dados.\nExecução não pode continuar")
            return False

        if self.validar_dados() is True:

            self.tipo_de_transacao = self.combo_tipo_trasacao.currentIndex()
            self.descricao = self.line_descricao.text()
            self.obs = self.txt_obs.toPlainText()
            self.valor_da_transacao = str(self.spin_valor.value())
            self.created_by = self.modified_by = self.user

            self.tipo_de_transacao = self.combo_tipo_trasacao.currentIndex()
            estado = 1

            values = (self.descricao, self.valor_da_transacao, self.caixa_numero, self.codarmazem,
                      self.created, self.modified, self.user, self.user, self.obs, self.tipo_de_transacao, estado)

            if self.registo_existe(self.cod_receita) is True:
                sql = """UPDATE receitas set descricao="{}", valor={}, modified="{}", 
                modified_by="{}", obs="{}", tipo={} WHERE cod={} """.format(self.descricao, self.valor_da_transacao,
                                                      self.modified, self.user, self.obs, self.tipo_de_transacao,
                                                                         self.cod_receita)

            else:
                sql = """INSERT INTO receitas (descricao, valor, codcaixa, codarmazem, created, modified, 
                            modified_by, created_by, obs, tipo, estado) VALUES {} """.format(values)

            try:

                # Retira o valor anterior caso registo exista
                if self.registo_existe(self.cod_receita) is True:
                    print("Tirando o valor da transacao de {}".format(self.valor_anterior))

                    if self.tipo_de_transacao == 0:
                        anterior_sql = """UPDATE caixa SET despesas=despesas-{} 
                        WHERE cod="{}" """.format(self.valor_anterior, self.caixa_numero)
                    else:
                        anterior_sql = """UPDATE caixa SET receitas=receitas-{} 
                        WHERE cod="{}" """.format(self.valor_anterior, self.caixa_numero)

                    print(anterior_sql)
                    self.cur.execute(anterior_sql)

                # Adiciona o novo valor na transacao
                if self.combo_tipo_trasacao.currentIndex() == 0:
                    tipo = "Despesa"
                    caixa_sql = """UPDATE caixa SET despesas=despesas+{}
                    WHERE cod="{}" """.format(self.valor_da_transacao, self.caixa_numero)
                else:
                    tipo = "Receita"
                    caixa_sql = """UPDATE caixa SET receitas=receitas+{}
                    WHERE cod="{}" """.format(self.valor_da_transacao, self.caixa_numero)

                print(caixa_sql)
                self.cur.execute(caixa_sql)
                self.cur.execute(sql)
                self.conn.commit()

                QMessageBox.information(self, "Sucesso", "{} gravada com sucesso.".format(tipo))

                self.close()

                return True
            except Exception as e:
                print(e)
                QMessageBox.warning(self, "Erro", "{}".format(e))
                self.conn.rollback()
                return False

    def registo_existe(self, cod_registo):

        sql = """SELECT cod from receitas WHERE cod={} """.format(cod_registo)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) == 0:
            return  False

        return True

    def mostrar_registo(self, cod_registo):

        sql = """SELECT * from receitas WHERE cod={} """.format(cod_registo)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            for item in data:
                self.cod_receita = cod_registo
                self.line_descricao.setText(item[1])
                self.combo_tipo_trasacao.setCurrentIndex(item[10])
                self.txt_obs.setPlainText(item[9])
                self.spin_valor.setValue(Decimal(item[2]))
                self.valor_anterior = Decimal(item[2])

            return True
        else:
            return False

if __name__ == '__main__':
    app = QApplication(sys.argv)

    helloPythonWidget = DespesasReceitas()
    helloPythonWidget.show()

    sys.exit(app.exec_())

