from PyQt5.QtWidgets import QLabel, QSizePolicy
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class FotoFrame(QLabel):
    def __init__(self, parent=None, foto="", largura=64, altura=64):
        super(FotoFrame, self).__init__(parent)
        self.foto = foto
        self.largura = largura
        self.altura = altura

    def mostrar_foto(self, foto):
        self.foto = foto
        pixmap = QPixmap(foto)
        pixmap.scaled(self.largura, self.altura, Qt.KeepAspectRatio)
        self.setPixmap(pixmap)
        self.setScaledContents(True)
        # self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

    def get_foto(self):
        return self.foto
