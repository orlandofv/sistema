import sys
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout, QFrame


class Dialog(QDialog):
    def __init__(self, parent=None, titulo="", imagem="./icons/45454.ico"):
        super(Dialog, self).__init__(parent)

        style = """
                            margin: 0;
                            padding: 0;
                            border-image:url(./images/back.PNG) 30 30 stretch;
                            background:#AFAFAF;
                            font-family: Arial, Helvetica, sans-serif;
                            font-size: 12px;
                            color: #FFFFFF;
                        """

        html = """<p > <h1 > {titulo} </h1> </p> 
        <img src="{img}" height="30" width="30" align='left'/> """.format(titulo=titulo, img=imagem)
        titulo = QLabel(html)
        titulo.setFixedHeight(30)
        titulo.setStyleSheet(style)

        vlayout = QVBoxLayout()
        vlayout.setContentsMargins(0,0,0,0)
        vlayout.addWidget(titulo)

        self.setLayout(vlayout)

    def add_line(self):
        style = '''
        QFrame.HLine, QFrame.Sunken {vertical-align: middle;}
        '''
        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setObjectName("line")
        line.setStyleSheet(style)

        return line


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = Dialog(None, 'Teste de Dialog')
    dialog.show()
    sys.exit(app.exec_())
