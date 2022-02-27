"""
Reworked code based on
http://trevorius.com/scrapbook/uncategorized/pyqt-custom-abstractitemmodel/

Adapted to Qt5 and fixed column/row bug.

TODO: handle changing data.
"""

import sys
from PyQt5 import QtCore, QtWidgets


class CustomNode(object):
    def __init__(self, data):
        self._data = data
        if type(data) == tuple:
            self._data = list(data)
        if type(data) is str or not hasattr(data, '__getitem__'):
            self._data = [data]

        self._columncount = len(self._data)
        self._children = []
        self._parent = None
        self._row = 0

    def data(self, column):
        if 0 <= column < len(self._data):
            return self._data[column]

    def columnCount(self):
        return self._columncount

    def childCount(self):
        return len(self._children)

    def child(self, row):
        if row >= 0 and row < self.childCount():
            return self._children[row]

    def parent(self):
        return self._parent

    def row(self):
        return self._row

    def addChild(self, child):
        child._parent = self
        child._row = len(self._children)
        self._children.append(child)
        self._columncount = max(child.columnCount(), self._columncount)


class CustomModel(QtCore.QAbstractItemModel):
    def __init__(self, nodes):
        QtCore.QAbstractItemModel.__init__(self)
        self._root = CustomNode(None)
        for node in nodes:
            self._root.addChild(node)

    def rowCount(self, index):
        if index.isValid():
            return index.internalPointer().childCount()
        return self._root.childCount()

    def addChild(self, node, _parent):
        if not _parent or not _parent.isValid():
            parent = self._root
        else:
            parent = _parent.internalPointer()
        parent.addChild(node)

    def index(self, row, column, _parent=None):
        if not _parent or not _parent.isValid():
            parent = self._root
        else:
            parent = _parent.internalPointer()

        if not QtCore.QAbstractItemModel.hasIndex(self, row, column, _parent):
            return QtCore.QModelIndex()

        child = parent.child(row)
        if child:
            return QtCore.QAbstractItemModel.createIndex(self, row, column, child)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if index.isValid():
            p = index.internalPointer().parent()
            if p:
                return QtCore.QAbstractItemModel.createIndex(self, p.row(), 0, p)
        return QtCore.QModelIndex()

    def columnCount(self, index):
        if index.isValid():
            return index.internalPointer().columnCount()
        return self._root.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return node.data(index.column())
        return None


class MyTree():
    """
    TreeView Example
    """

    def __init__(self):
        self.items = []
        self.subitems = []

        self.products = ['CP154545', 'Sabrinas Grandes', '45']

        for x in range(10):
            print(list(str(x)))
            self.subitems.append(CustomNode(list(str(x))))
            for y in range(9999, 10010):
                if x > 0:
                    self.subitems[-1].addChild(CustomNode(list(str(y))))

        self.add_data(self.subitems)

    def add_data(self, data):
        """
        TODO: how to insert data, and update tree.
        """

        self.tw = QtWidgets.QTreeView()
        h = self.tw.header()
        # h.setHidden(True)
        self.tw.setModel(CustomModel(data))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mytree = MyTree()
    mytree.tw.show()
    sys.exit(app.exec_())