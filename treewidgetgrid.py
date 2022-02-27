import sys

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QVBoxLayout, QDialog, QApplication


class WidgeTGrid(QDialog):

    def __init__(self, parent=None):
        super(WidgeTGrid, self).__init__(parent)

        self.tree_widget = QTreeWidget()
        self.tree_widget.clicked.connect(self.clicked_row)
        th = self.tree_widget.header()
        th.setHidden(True)

        vl = QVBoxLayout()
        vl.addWidget(self.tree_widget)

        self.setLayout(vl)
        self.fill_tree()

    def fill_tree(self):
        tl = QTreeWidgetItem(["Nadad de Novo", str(1), "Olooo"], 0)
        tl.addChild(QTreeWidgetItem(["1"]))
        self.tree_widget.addTopLevelItem(tl)

    def clicked_row(self, index):
        r = index.row()
        print(r)

        current_index = self.tree_widget.currentIndex()
        print(current_index.parent().data())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = WidgeTGrid()
    mainwindow.show()
    sys.exit(app.exec_())
