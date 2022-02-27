# -*- coding: utf-8 -*-
"""
Created on Fri Mar 02 23:18:43 2012

@author: lims
"""

from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QDoubleSpinBox, QFormLayout, QVBoxLayout, QToolBar, QMessageBox, \
    QTextEdit, QAction, QApplication, QComboBox, QDateTimeEdit, QCalendarWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QIcon
import sys

from utilities import codigo as cd
from pricespinbox import price

import sqlite3 as lite

DB_FILENAME = "dados.tsdb"


class caixa(QDialog):
    def __init__(self, parent=None):
        super(caixa, self).__init__(parent)

        self.accoes()
        self.ui()

        self.caixa = ""

        if self.parent() is None:
            self.db = self.connect_db()
        else:
            self.cur = self.parent().cur
            self.conn = self.parent().conn

        # verifica a existencia dos dados na base de dados
        self.existe(self.cod.text())

        # Mostraregisto caso exista
        self.mostrar_registo()

    def ui(self):
        html = """<center style= "background-image: './images/control.png'" > <h2 > Caixa </h2> </center> """

        titulo = QLabel(html)

        cod = QLabel("Código da Caixa")
        valor_inicial = QLabel("Valor Inicial")
        receitas = QLabel("Receitas")
        despesas = QLabel("Despesas")
        obs = QLabel("Observações")

        self.cod = QLineEdit()
        self.cod.setEnabled(False)
        self.valor_inicial = price()
        self.receitas = price()
        self.receitas.setDisabled(True)
        self.despesas = price()
        self.despesas.setDisabled(True)

        self.validade = QDateTimeEdit(self)

        self.validade.setDateTime(QDateTime.currentDateTime())
        cal = QCalendarWidget()
        self.validade.setCalendarPopup(True)
        self.validade.setCalendarWidget(cal)

        self.obs = QTextEdit()
        
        grid = QFormLayout()

        grid.addRow(cod, self.cod)
        grid.addRow(valor_inicial, self.valor_inicial)
        grid.addRow(receitas, self.receitas)
        grid.addRow(despesas, self.despesas)
        grid.addRow(QLabel('Data'), self.validade)
        grid.addRow(obs, self.obs)

        vLay = QVBoxLayout(self)
        vLay.setContentsMargins(0, 0, 0, 0)

        cLay = QVBoxLayout()
        cLay.setContentsMargins(10, 10, 10, 10)

        cLay.addLayout(grid)

        vLay.addWidget(titulo)
        vLay.addLayout(cLay)
        vLay.addWidget(self.tool)
        self.setLayout(vLay)

        self.setWindowTitle("Cadastro de Famílias")

        style = """
            margin: 0;
            padding: 0;
            border-image:url(./images/transferir.jpg) 30 30 stretch;
            background:#303030;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 12px;
            color: #FFFFFF;
        """

        titulo.setStyleSheet(style)

    def accoes(self):
        self.tool = QToolBar()
        self.tool.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        gravar = QAction(QIcon("./images/ok.png"), "&Gravar\nDados", self)
        # eliminar = QAction(QIcon("./icons/new.ico"), "Limpar\nCampos", self)
        fechar = QAction(QIcon("./images/filequit.png"), "&Fechar", self)

        self.tool.addAction(gravar)
        # self.tool.addAction(eliminar)
        self.tool.addSeparator()
        self.tool.addAction(fechar)

        gravar.triggered.connect(self.add_record)
        # eliminar.triggered.connect(self.limpar)
        fechar.triggered.connect(self.fechar)

    # ==============================================================================

    def closeEvent(self, evt):
        parent = self.parent()
        if parent is not None:
            try:
                parent.fill_table()
            except Exception as e:
                print(e)

    def fechar(self):
        self.close()

    def limpar(self):
        for child in (self.findChildren(QLineEdit) or self.findChildren(QTextEdit)):
            if child.objectName() not in ["cod", "cal1", "cal2"]: child.clear()

        # gera novo codigo para caixa
        self.cod.setText("CX" + cd("CX" + "abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789"))

    def validacao(self):

        if str(self.valor_inicial.text()) == "":
            QMessageBox.information(self, "Erro", "valor_inicial do Caixa inválido")
            self.valor_inicial.setFocus()
            return False
        else:
            return True

    def mostrar_registo(self):

        sql = """SELECT * from caixa WHERE cod = "{codigo}" """.format(codigo=str(self.cod.text()))
        self.cur.execute(sql)
        # lista = self.cur.fetchall()
        data = self.cur.fetchall()

        if len(data) == 0:
            self.cod.setText("CX" + cd("abcdefghijklmnopqrstuvxwzABCDEFGHIJKLMNOPQRSTUVXWZ0123456789"))
        else:
            self.valor_inicial.setValue(data[0][1])
            self.receitas.setValue(data[0][2])
            self.despesas.setValue(data[0][3])
            self.obs.setPlainText(data[0][9])

    def existe(self, codigo):

        sql = """SELECT cod from caixa WHERE cod = "{codigo}" """.format(codigo=str(self.cod.text()))

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]

        if len(data) == 0:
            codigo = self.cod.text()
            self.codigo = codigo
            return False
        else:
            codigo = ''.join(data[0])
            self.codigo = codigo
            return True

    def add_record(self):

        if self.validacao() is True:
            code = self.cod.text()
            valor_inicial = self.valor_inicial.value()
            receitas = self.receitas.value()
            despesas = self.despesas.value()
            obs = self.obs.toPlainText()
            estado = 0

            created = self.validade.dateTime().toString("yyyy-MM-dd H:mm:ss")
            created_by = self.parent().user

            print("Criado por", created_by)
            if self.caixa_existe() is True:

                sql = """UPDATE caixa set valor_inicial={valor_inicial}, 
                obs="{obs}" WHERE cod="{cod}" 
                 """.format(cod=code, valor_inicial=valor_inicial, obs=obs)

                messagem = "Dados de Caixa actualizados com sucesso!"
            else:

                if self.verifica_caixa(created, created_by) is False:
                    QMessageBox.warning(self, "Erro: Caixa já foi aberata hoje!",
                                        "Caixa só pode ser aberta mais de uma vez por um Administrador.\n"
                                        "Contacte seu Administrador.")
                    return False

                messagem = "Caixa aberta com sucesso!"
                values = """ "{cod}", {valor_inicial}, "{obs}", {estado}, 
                "{created}", "{created_by}", "{codarmazem}" 
                """.format(cod=code, valor_inicial=valor_inicial, obs=obs,
                           estado=estado, created=created, created_by=created_by, codarmazem=self.parent().codarmazem)

                sql = "INSERT INTO caixa (cod, valor_inicial, obs, estado, created," \
                      "created_by, codarmazem) values({value})".format(value=values)
            try:

                self.cur.execute(sql)
                self.conn.commit()
                QMessageBox.information(self, "Sucesso", '{}'.format(messagem))
            except Exception as e:
                QMessageBox.critical(self, "Erro", "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
                return

            try:
                self.parent().validade.setDateTime(self.validade.DateTime())
            except Exception as e:
                print(e)

            self.close()

    def verifica_caixa(self, data, user):

        sql = """SELECT c.cod FROM caixa c 
        INNER JOIN users u ON u.cod=c.modified_by
        WHERE c.modified="{}" """.format(data)

        self.cur.execute(sql)
        data = self.cur.fetchall()

        if len(data) > 0:
            sql  = """SELECT admin from users WHERE cod="{}" """.format(user)
            self.cur.execute(sql)
            data = self.cur.fetchall()

            admin = 0

            if len(data) > 0:
                admin = data[0][0]

            if admin == 0:
                return False

        return True

    def caixa_existe(self):
        sql = """select * from caixa WHERE estado=0 and codarmazem= "{}" """.format(self.parent().codarmazem)

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [tuple(str(item) for item in t) for t in lista]
        if len(data) > 0:
            self.caixa = data[0][0]
            return True

        return False

    def connect_db(self):
        # Connect to database and retrieves data
        try:
            self.conn = lite.connect(DB_FILENAME)
            self.cur = self.conn.cursor()

        except Exception as e:
            QMessageBox.critical(self, "Erro ao conectar a Base de Dados",
                                 "Os seus Dados não foram gravados. Erro: {erro} ".format(erro=e))
            sys.exit(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    helloPythonWidget = caixa()
    helloPythonWidget.show()

    sys.exit(app.exec_())