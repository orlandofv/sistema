
import sys
from PyQt5.QtWidgets import (QApplication,  QLabel, QVBoxLayout,  QPushButton, QAbstractButton)

from PyQt5.QtCore import  Qt
from PyQt5.QtGui import QIcon, QPixmap, QPicture, QImage


class Barcode(QAbstractButton):
    def __init__(self, parent=None, picture=""):
        super(Barcode, self).__init__(parent)
        self.set_picture(picture)

        self.ui()

    def ui(self):
        self.picture = QIcon(self.image)
        self.picture.setAlignment(Qt.AlignHCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.picture)

        self.setLayout(layout)

    def set_picture(self, picture=""):
        return QIcon(picture)

    def mouseMoveEvent(self, QMouseEvent):
        print("Passou")
        self.setStyleSheet("QWidget {backgroung: #FFFFFF}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    barcode_app = Barcode(None, QIcon('./icons/add.ico'))
    barcode_app.show()
    sys.exit(app.exec_())
