from PyQt5.QtWidgets import QTableView, QAbstractItemView


class StripedTable(QTableView):
    
    def __init__(self, parent=None):
        super(StripedTable, self).__init__(parent)

        # hide grid
        self.setShowGrid(False)

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        # set the font

        # hide vertical header
        vh = self.verticalHeader()
        vh.setVisible(False)

        # set horizontal header properties and stretch last column
        hh = self.horizontalHeader()
        hh.setStretchLastSection(True)

        # set column width to fit contents
        self.resizeColumnsToContents()

        # enable sorting
        self.setSortingEnabled(True)

        self.setAlternatingRowColors(True)
