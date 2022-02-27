import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QHeaderView
from PyQt5.Qt import QStandardItemModel, QStandardItem
from PyQt5.QtGui import QFont, QColor


class StandardItem(QStandardItem):
    def __init__(self, text='', font_size=12, set_bold=False, color=QColor(0, 0, 0)):
        super(StandardItem, self).__init__()

        fnt = QFont('Open Sans', font_size)
        fnt.setBold(set_bold)
        self.setEditable(False)
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(text)


class AppDemo(QMainWindow):
    def __init__(self, parent=None):
        super(AppDemo, self).__init__(parent)

        self.setWindowTitle('World Country Diagram')
        self.resize(500, 700)

        treeview = QTreeView()

        # treeview.setHeaderHidden(True)
        h = treeview.header()
        h.setHidden(True)

        tree_model = QStandardItemModel()
        root_node = tree_model.invisibleRootItem()

        # America
        america = StandardItem('America', 16, set_bold=True)
        california = StandardItem('California', 14)
        america.appendRow(california)

        oakland = StandardItem('Oakland', 12, color=QColor(155, 0, 0))
        sanfrancisco = StandardItem('San Francisco', 12, color=QColor(155, 0, 0))
        sanjose = StandardItem('San Jose', 12, color=QColor(155, 0, 0))

        california.appendRow(oakland)
        california.appendRow(sanfrancisco)
        california.appendRow(sanjose)

        texas = StandardItem('Texas', 14)

        america.appendRow(texas)

        austin = StandardItem('Austin', 12, color=QColor(155, 0, 0))
        hoston = StandardItem('Hoston', 12, color=QColor(155, 0, 0))
        dallas = StandardItem('Dallas', 12, color=QColor(155, 0, 0))

        texas.appendRow(austin)
        texas.appendRow(hoston)
        texas.appendRow(dallas)

        # Canada
        canada = StandardItem('Canada', 16, set_bold=True)

        alberta = StandardItem('Alberta', 14)
        bc = StandardItem('British Columbia', 14)
        ontario = StandardItem('Ontario', 14)

        canada.appendRows([alberta, bc, ontario])

        root_node.appendRow(america)
        root_node.appendRow(canada)
        treeview.setModel(tree_model)
        treeview.expandAll()
        treeview.clicked.connect(self.get_value)

        self.setCentralWidget(treeview)

    def get_value(self, val):
        print(val.data())
        print(val.row())
        print(val.column())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = AppDemo()
    demo.show()
    sys.exit(app.exec_())
