# -*- coding: utf-8 -*-
import sys

from PyQt5.QtCore import lowercasebase, Qt
from PyQt5.QtGui import QIcon, QFont, QKeyEvent, QRegExpValidator, QKeySequence
from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QGridLayout, QApplication, QButtonGroup, QSizePolicy
from teclado_numerico import Teclado as Tec

LETRAS_MINUSCULAS = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s",
                     "t", "u", "v", "x", "y", "w", "z"]

LETRAS_MAUSCULAS = [x.upper() for x in LETRAS_MINUSCULAS]


class Teclado(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.btn_q = QPushButton("q")
        # self.btn_grid.addWidget(self.btn_q)

        self.ui()

    def ui(self):
        self.btn_group = QButtonGroup()
        self.btn_group.setExclusive(True)
        grid_lay = QGridLayout()
        grid_lay.setSpacing(0)
        grid_lay.setContentsMargins(0, 0, 0, 0)

        self.descricao = QLineEdit()

        # Herda a maneira de mostrar dados seja password ou normal
        self.descricao.setEchoMode(self.parent().echoMode())

        self.descricao.setMaxLength(255)

        btn_0 = QPushButton('0')
        btn_1 = QPushButton('1')
        btn_2 = QPushButton('2')
        btn_3 = QPushButton('3')
        btn_4 = QPushButton('4')
        btn_5 = QPushButton('5')
        btn_6 = QPushButton('6')
        btn_7 = QPushButton('7')
        btn_8 = QPushButton('8')
        btn_9 = QPushButton('9')

        btn_a = QPushButton(LETRAS_MINUSCULAS[0])
        btn_b = QPushButton(LETRAS_MINUSCULAS[1])
        btn_c = QPushButton(LETRAS_MINUSCULAS[2])
        btn_d = QPushButton(LETRAS_MINUSCULAS[3])
        btn_e = QPushButton(LETRAS_MINUSCULAS[4])
        btn_f = QPushButton(LETRAS_MINUSCULAS[5])
        btn_g = QPushButton(LETRAS_MINUSCULAS[6])
        btn_h = QPushButton(LETRAS_MINUSCULAS[7])
        btn_i = QPushButton(LETRAS_MINUSCULAS[8])
        btn_j = QPushButton(LETRAS_MINUSCULAS[9])
        btn_k = QPushButton(LETRAS_MINUSCULAS[10])
        btn_l = QPushButton(LETRAS_MINUSCULAS[11])
        btn_m = QPushButton(LETRAS_MINUSCULAS[12])
        btn_n = QPushButton(LETRAS_MINUSCULAS[13])
        btn_o = QPushButton(LETRAS_MINUSCULAS[14])
        btn_p = QPushButton(LETRAS_MINUSCULAS[15])
        btn_q = QPushButton(LETRAS_MINUSCULAS[16])
        btn_r = QPushButton(LETRAS_MINUSCULAS[17])
        btn_s = QPushButton(LETRAS_MINUSCULAS[18])
        btn_t = QPushButton(LETRAS_MINUSCULAS[19])
        btn_u = QPushButton(LETRAS_MINUSCULAS[20])
        btn_v = QPushButton(LETRAS_MINUSCULAS[21])
        btn_x = QPushButton(LETRAS_MINUSCULAS[22])
        btn_y = QPushButton(LETRAS_MINUSCULAS[23])
        btn_w = QPushButton(LETRAS_MINUSCULAS[24])
        btn_z = QPushButton(LETRAS_MINUSCULAS[25])

        btn_enter = QPushButton("ENTER")
        btn_ponto = QPushButton(".")
        btn_hifen = QPushButton("-")
        btn_aroba = QPushButton("@")
        btn_dolar = QPushButton("$")
        btn_cardinal = QPushButton("#")
        btn_abrir_parenteses = QPushButton("(")
        btn_fechar_parenteses = QPushButton(")")
        btn_percentagem = QPushButton("%")

        btn_back = QPushButton("BKS")
        btn_space = QPushButton("ESPACO")
        btn_space.clicked.connect(self.espaco)
        btn_enter.clicked.connect(self.enter)
        btn_back.clicked.connect(self.backspace)

        btn_clear = QPushButton("LIMPAR")
        btn_clear.clicked.connect(self.limpar_tudo)
        btn_ponto.clicked.connect(lambda: self.escrever(btn_ponto.text()))
        btn_hifen.clicked.connect(lambda: self.escrever(btn_hifen.text()))
        btn_percentagem.clicked.connect(lambda: self.escrever(btn_percentagem.text()))
        btn_aroba.clicked.connect(lambda: self.escrever(btn_aroba.text()))
        btn_dolar.clicked.connect(lambda: self.escrever(btn_dolar.text()))
        btn_cardinal.clicked.connect(lambda: self.escrever(btn_cardinal.text()))
        btn_abrir_parenteses.clicked.connect(lambda: self.escrever(btn_abrir_parenteses.text()))
        btn_fechar_parenteses.clicked.connect(lambda: self.escrever(btn_fechar_parenteses.text()))

        self.btn_cps = QPushButton("CAPS")
        self.btn_cps.setCheckable(True)
        self.btn_cps.clicked.connect(self.mudar_caps)

        grid_lay.addWidget(self.descricao, 0, 0, 1, 9)
        grid_lay.addWidget(btn_back, 0, 9)

        grid_lay.addWidget(btn_1, 1, 0)
        grid_lay.addWidget(btn_2, 1, 1)
        grid_lay.addWidget(btn_3, 1, 2)
        grid_lay.addWidget(btn_4, 1, 3)
        grid_lay.addWidget(btn_5, 1, 4)
        grid_lay.addWidget(btn_6, 1, 5)
        grid_lay.addWidget(btn_7, 1, 6)
        grid_lay.addWidget(btn_8, 1, 7)
        grid_lay.addWidget(btn_9, 1, 8)
        grid_lay.addWidget(btn_0, 1, 9)

        grid_lay.addWidget(btn_q, 2, 0)
        grid_lay.addWidget(btn_w, 2, 1)
        grid_lay.addWidget(btn_e, 2, 2)
        grid_lay.addWidget(btn_r, 2, 3)
        grid_lay.addWidget(btn_t, 2, 4)
        grid_lay.addWidget(btn_y, 2, 5)
        grid_lay.addWidget(btn_u, 2, 6)
        grid_lay.addWidget(btn_i, 2, 7)
        grid_lay.addWidget(btn_o, 2, 8)
        grid_lay.addWidget(btn_p, 2, 9)
        grid_lay.addWidget(btn_a, 3, 0)
        grid_lay.addWidget(btn_s, 3, 1)
        grid_lay.addWidget(btn_d, 3, 2)
        grid_lay.addWidget(btn_f, 3, 3)
        grid_lay.addWidget(btn_g, 3, 4)
        grid_lay.addWidget(btn_h, 3, 5)
        grid_lay.addWidget(btn_j, 3, 6)
        grid_lay.addWidget(btn_k, 3, 7)
        grid_lay.addWidget(btn_l, 3, 8)
        grid_lay.addWidget(btn_clear, 3, 9)
        grid_lay.addWidget(self.btn_cps, 4, 0)
        grid_lay.addWidget(btn_z, 4, 1)
        grid_lay.addWidget(btn_x, 4, 2)
        grid_lay.addWidget(btn_c, 4, 3)
        grid_lay.addWidget(btn_v, 4, 4)
        grid_lay.addWidget(btn_b, 4, 5)
        grid_lay.addWidget(btn_n, 4, 6)
        grid_lay.addWidget(btn_m, 4, 7)
        grid_lay.addWidget(btn_enter, 4, 8, 1, 2)
        grid_lay.addWidget(btn_abrir_parenteses, 5, 0)
        grid_lay.addWidget(btn_fechar_parenteses, 5, 1)
        grid_lay.addWidget(btn_space, 5, 2, 1, 2)
        grid_lay.addWidget(btn_aroba, 5, 4)
        grid_lay.addWidget(btn_cardinal, 5, 5)
        grid_lay.addWidget(btn_percentagem, 5, 6)
        grid_lay.addWidget(btn_dolar, 5, 7)
        grid_lay.addWidget(btn_hifen, 5, 8)
        grid_lay.addWidget(btn_ponto, 5, 9)

        btn_a.clicked.connect(lambda: self.escrever(btn_a.text()))
        btn_b.clicked.connect(lambda: self.escrever(btn_b.text()))
        btn_c.clicked.connect(lambda: self.escrever(btn_c.text()))
        btn_d.clicked.connect(lambda: self.escrever(btn_d.text()))
        btn_e.clicked.connect(lambda: self.escrever(btn_e.text()))
        btn_f.clicked.connect(lambda: self.escrever(btn_f.text()))
        btn_g.clicked.connect(lambda: self.escrever(btn_g.text()))
        btn_h.clicked.connect(lambda: self.escrever(btn_h.text()))
        btn_i.clicked.connect(lambda: self.escrever(btn_i.text()))
        btn_j.clicked.connect(lambda: self.escrever(btn_j.text()))
        btn_k.clicked.connect(lambda: self.escrever(btn_k.text()))
        btn_l.clicked.connect(lambda: self.escrever(btn_l.text()))
        btn_m.clicked.connect(lambda: self.escrever(btn_m.text()))
        btn_n.clicked.connect(lambda: self.escrever(btn_n.text()))
        btn_o.clicked.connect(lambda: self.escrever(btn_o.text()))
        btn_p.clicked.connect(lambda: self.escrever(btn_p.text()))
        btn_q.clicked.connect(lambda: self.escrever(btn_q.text()))
        btn_r.clicked.connect(lambda: self.escrever(btn_r.text()))
        btn_s.clicked.connect(lambda: self.escrever(btn_s.text()))
        btn_t.clicked.connect(lambda: self.escrever(btn_t.text()))
        btn_u.clicked.connect(lambda: self.escrever(btn_u.text()))
        btn_v.clicked.connect(lambda: self.escrever(btn_v.text()))
        btn_x.clicked.connect(lambda: self.escrever(btn_x.text()))
        btn_y.clicked.connect(lambda: self.escrever(btn_y.text()))
        btn_w.clicked.connect(lambda: self.escrever(btn_w.text()))
        btn_z.clicked.connect(lambda: self.escrever(btn_z.text()))

        btn_0.clicked.connect(lambda: self.escrever(btn_0.text()))
        btn_1.clicked.connect(lambda: self.escrever(btn_1.text()))
        btn_2.clicked.connect(lambda: self.escrever(btn_2.text()))
        btn_3.clicked.connect(lambda: self.escrever(btn_3.text()))
        btn_4.clicked.connect(lambda: self.escrever(btn_4.text()))
        btn_5.clicked.connect(lambda: self.escrever(btn_5.text()))
        btn_6.clicked.connect(lambda: self.escrever(btn_6.text()))
        btn_7.clicked.connect(lambda: self.escrever(btn_7.text()))
        btn_8.clicked.connect(lambda: self.escrever(btn_8.text()))
        btn_9.clicked.connect(lambda: self.escrever(btn_9.text()))

        self.setLayout(grid_lay)

        boldFont = QFont('Consolas', 14)
        boldFont.setBold(True)

        for child in (self.findChildren(QPushButton)):
            child.setFixedHeight(40)
            child.setFont(boldFont)

        for child in self.findChildren(QLineEdit):
            child.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred))
            child.setFont(boldFont)

        self.setWindowTitle("Teclado")

    def escrever(self, texto):
        self.descricao.setText(self.descricao.text() + texto)

    def limpar_tudo(self):
        self.descricao.setText("")

    def espaco(self):
        self.descricao.setText(self.descricao.text() + " ")

    def enter(self):
        try:
            if self.parent() is not None:
                self.parent().setText(self.descricao.text())
                self.parent().fill_table()
        except Exception as e:
            print(e)

        self.close()

    def backspace(self):
        if not self.descricao.hasFocus():
            self.descricao.setFocus()

    def mudar_caps(self):
        for child in self.findChildren(QPushButton):
            if child.text() not in ("ESPACO", "espaco", "CAPS", "caps", "LIMPAR", "limpar", "BKS", "bks", "ENTER", "enter"):
                if self.btn_cps.isChecked():
                    child.setText(str(child.text()).upper())
                else:
                    child.setText(str(child.text()).lower())

    def focusOutEvent(self, *args, **kwargs):
        print("Tenho focus")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    helloPythonWidget = Teclado()
    helloPythonWidget.show()
    sys.exit(app.exec_())