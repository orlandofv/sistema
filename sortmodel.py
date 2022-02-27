# -*- coding: utf-8 -*-

import operator
from PyQt5.QtCore import QVariant, QAbstractTableModel, Qt
from PyQt5.QtGui import QColor


class MyTableModel(QAbstractTableModel):
    def __init__(self, datain, headerdata, parent=None, *args):
        """ datain: a list of lists
            headerdata: a list of strings
        """
        QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = datain
        self.headerdata = headerdata

    def rowCount(self, parent):
        return len(self.arraydata)

    def columnCount(self, parent):
        return len(self.arraydata[0])

    def data(self, index, role):
        colors = ['#053061', '#2166ac', '#4393c3', '#92c5de', '#d1e5f0', '#f7f7f7', '#fddbc7', '#f4a582', '#d6604d',
                  '#b2182b', '#67001f']
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()

        data = self.arraydata

        if role == Qt.BackgroundRole:
            value = data[index.row()][index.column()]
            if isinstance(value, int) or isinstance(value, float):
                value = int(value)  # Convert to integer for indexing.

                # Limit to range -5 ... +5, then convert to 0..10
                value = max(-5, value)  # values < -5 become -5
                value = min(5, value)  # valaues > +5 become +5
                value += 5  # -5 becomes 0, +5 becomes + 10

                return QColor(colors[value])

        return QVariant(self.arraydata[index.row()][index.column()])

    def headerData(self, col, orientation, role):
        try:
            if orientation == Qt.Horizontal and role == Qt.DisplayRole:
                return QVariant(self.headerdata[col])
            return QVariant()
        except IndexError:
            raise IndexError("List index out of range."
                             "\nThe number of returned columns is larger than the given header.")

    def sort(self, Ncol, order):
        """
			Sort table by given column number.
        """
		
        self.layoutAboutToBeChanged.emit()
        self.arraydata = sorted(self.arraydata, key=operator.itemgetter(Ncol))
        if order == Qt.DescendingOrder:
            self.arraydata.reverse()
        self.layoutChanged.emit()

