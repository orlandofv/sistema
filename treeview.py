# coding: utf-8
import os
import sys
import codecs
import bisect
from PyQt5.QtWidgets import QTreeView, QMessageBox, QMainWindow, QApplication
from PyQt5.QtCore import QModelIndex, Qt, QVariant, QAbstractItemModel
from PyQt5.QtGui import QPixmap


class MainForm(QMainWindow):
    def __init__(self, filename, nesting, separator, parent=None):
        super(MainForm, self).__init__(parent)
        headers = ["Country/State (US)/City/Provider", "Server", "IP"]
        self.treeWidget = TreeOfTableWidget(filename, nesting,
        separator)
        self.treeWidget.model().headers = headers
        self.setCentralWidget(self.treeWidget)
        self.treeWidget.activated.connect(self.activated)
        self.setWindowTitle("Server Info")

    def activated(self, fields):
        self.statusBar().showMessage("*".join(fields), 60000)


class TreeOfTableWidget(QTreeView):
    def __init__(self, filename, nesting, separator, parent=None):
        super(TreeOfTableWidget, self).__init__(parent)
        self.setSelectionBehavior(QTreeView.SelectItems)
        self.setUniformRowHeights(True)
        model = ServerModel(self)
        self.setModel(model)
        try:
            model.load(filename, nesting, separator)
        except IOError as e:
            QMessageBox.warning(self, "Server Info - Error", str(e))

        self.activated.connect(self.activated)

    def expanded(self):
        for column in range(self.model().columnCount(QModelIndex())):
            self.resizeColumnToContents(column)

    def activated(self, index):
        self.emit(PYQT_SIGNAL("activated"), self.model().asRecord(index))

    def currentFields(self):
        return self.model().asRecord(self.currentIndex())


class TreeOfTableModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(TreeOfTableModel, self).__init__(parent)
        self.columns = 0
        self.root = BranchNode("")
        self.headers = []

    def load(self, filename, nesting, separator):
        assert nesting > 0

        self.nesting = nesting
        self.root = BranchNode("")
        exception = None
        fh = None
        try:
            for line in codecs.open(str(filename), "rU", "utf8"):
                if not line:
                    continue
                self.addRecord(line.split(separator), False)
        except IOError as e:
            exception = e
        finally:
            if fh is not None:
                fh.close()
            self.reset()

            for i in range(self.columns):
                self.headers.append("Column #%d" % i)
            if exception is not None:
                raise exception

    def addRecord(self, fields, callReset=True):
        assert len(fields) > self.nesting

        root = self.root
        branch = None
        for i in range(self.nesting):
            key = fields[i].lower()
            branch = root.childWithKey(key)

            if branch is not None:
                root = branch
            else:
                branch = BranchNode(fields[i])
            root.insertChild(branch)
            root = branch

        assert branch is not None
        items = fields[self.nesting:]

        self.columns = max(self.columns, len(items))
        branch.insertChild(LeafNode(items, branch))
        if callReset:
            self.reset()

    def asRecord(self, index):
        leaf = self.nodeFromIndex(index)
        if leaf is not None and isinstance(leaf, LeafNode):
            return leaf.asRecord()
        return []

    def rowCount(self, parent):
        node = self.nodeFromIndex(parent)

        if node is None or isinstance(node, LeafNode):
            return 0

        return len(node)

    def columnCount(self, parent):
        return self.columns

    def data(self, index, role):
        if role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignTop | Qt.AlignLeft))

        if role != Qt.DisplayRole:
            return QVariant()
        node = self.nodeFromIndex(index)
        assert node is not None
        if isinstance(node, BranchNode):
            return QVariant(node.toString()) \
                if index.column() == 0 else QVariant(str(""))

        return QVariant(node.field(index.column()))

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and \
                role == Qt.DisplayRole:
            assert 0 <= section <= len(self.headers)

            return QVariant(self.headers[section])
        return QVariant()

    def index(self, row, column, parent):
        assert self.root

        branch = self.nodeFromIndex(parent)
        assert branch is not None

        return self.createIndex(row, column,
                                branch.childAtRow(row))

    def parent(self, child):
        node = self.nodeFromIndex(child)

        if node is None:
            return QModelIndex()
        parent = node.parent
        if parent is None:
            return QModelIndex()
        grandparent = parent.parent
        if grandparent is None:
            return QModelIndex()
        row = grandparent.rowOfChild(parent)
        assert row != -1
        return self.createIndex(row, 0, parent)

    def nodeFromIndex(self, index):
        return index.internalPointer() \
            if index.isValid() else self.root


class ServerModel(TreeOfTableModel):
    def __init__(self, parent=None):
        super(ServerModel, self).__init__(parent)

    def data(self, index, role):

        if role == Qt.DecorationRole:
            node = self.nodeFromIndex(index)

            if node is None:
                return QVariant()

            if isinstance(node, BranchNode):

                if index.column() != 0:
                    return QVariant()
                filename = node.toString().replace(" ", "_")
                parent = node.parent.toString()
                if parent and parent != "USA":
                    return QVariant()
                if parent == "USA":
                    filename = "USA_" + filename
                filename = os.path.join(os.path.dirname(__file__),
                                        "flags", filename + ".png")
                pixmap = QPixmap(filename)
                if pixmap.isNull():
                    return QVariant()
                return QVariant(pixmap)

        return TreeOfTableModel.data(self, index, role)


class BranchNode(object):
    def __init__(self, name, parent=None):
        super(BranchNode, self).__init__(parent)
        self.name = name
        self.parent = parent
        self.children = []

    def orderKey(self):
        return self.name.lower()

    def toString(self):
        return self.name

    def __len__(self):
        return len(self.children)

    def childAtRow(self, row):
        assert 0 <= row < len(self.children)

        return self.children[row][NODE]

    def rowOfChild(self, child):
        for i, item in enumerate(self.children):
            if item[NODE] == child:
                return i

        return -1

    def childWithKey(self, key):
        if not self.children:
            return None

        i = bisect.bisect_left(self.children, (key, None))
        if i < 0 or i >= len(self.children):
            return None
        if self.children[i][KEY] == key:
            return self.children[i][NODE]
        return None

    def insertChild(self, child):
        child.parent = self

        bisect.insort(self.children, (child.orderKey(), child))

    def hasLeaves(self):
        if not self.children:
            return False

        return isinstance(self.children[0], LeafNode)


class LeafNode(object):
    def __init__(self, fields, parent=None):
        super(LeafNode, self).__init__(parent)
        self.parent = parent
        self.fields = fields

    def orderKey(self):
        return u"\t".join(self.fields).lower()

    def toString(self, separator="\t"):
        return separator.join(self.fields)

    def __len__(self):
        return len(self.fields)

    def field(self, column):
        assert 0 <= column <= len(self.fields)

        return self.fields[column]

    def asRecord(self):
        record = []

        branch = self.parent
        while branch is not None:
            record.insert(0, branch.toString())
            branch = branch.parent
        assert record and not record[0]
        record = record[1:]
        return record + self.fields


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = TreeOfTableWidget()