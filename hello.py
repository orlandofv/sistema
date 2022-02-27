import sys
from PyQt5.QtWidgets import QWidget, QPushButton, QButtonGroup, QApplication, QMessageBox, QScrollArea, QVBoxLayout, \
    QHBoxLayout, QScrollBar

from flowlayout import FlowLayout
import sqlite3 as lite

DB_FILENAME = "dados.tsdb"

class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(30, 30, 400, 200)
        self.connect_db()
        self.initUI()

    def initUI(self):
        sql = """ select nome from familia order by nome desc"""

        self.cur.execute(sql)
        data = self.cur.fetchall()

        self.btn_grp = QButtonGroup()
        self.btn_grp.setExclusive(True)

        layout = FlowLayout()
        for x in data:
            self.btn = QPushButton(self)
            self.btn.setFixedSize(100, 50)
            self.btn.setText(str(x[0]))
            self.btn.setObjectName(str(x[0]))
            self.btn.setToolTip(str(x[0]))
            layout.addWidget(self.btn)

            self.btn_grp.addButton(self.btn)

        self.btn_grp.buttonClicked.connect(self.on_click)

        self.scr = QScrollArea(self)
        self.scr.setLayout(layout)

        vscrl = QScrollBar()
        vscrl.setMinimum(0)
        vscrl.setMaximum(100)
        vscrl.setSliderPosition(5)
        self.scr.setVerticalScrollBar(vscrl)

        mainlayout = QVBoxLayout()
        mainlayout.addWidget(self.scr)
        self.setLayout(mainlayout)
        self.show()

    def on_click(self, btn):
        print("Hhahahahahahahaaaaaaaaaaaaaaa")


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
    ex = Example()
    sys.exit(app.exec_())
