from PyQt5 import QtCore, QtGui, QtWidgets, QtPrintSupport

textMargins = 12
borderMargins = 10


def mmToPixels(printer, mm):
    return mm * 0.039370147 * printer.resolution()


def paintPage(pageNumber, pageCount, painter, doc, textRect, footerHeight):
    painter.save()
    textPageRect = QtCore.QRectF(QtCore.QPointF(0, pageNumber*doc.pageSize().height()), doc.pageSize())
    painter.setClipRect(textRect)
    painter.translate(0, -textPageRect.top())
    painter.translate(textRect.left(), textRect.top())
    doc.drawContents(painter)

    painter.restore()
    footerRect = QtCore.QRectF(textRect)
    footerRect.setTop(textRect.bottom())
    footerRect.setHeight(footerHeight)

    # draw footer
    painter.save()
    pen = painter.pen()
    pen.setColor(QtCore.Qt.blue)
    painter.setPen(pen)
    rect = QtCore.QRectF(footerRect.x(), footerRect.y() - 90, footerRect.width(), footerRect.height())
    painter.drawLine(1000, 1000, 1000, 1000)
    painter.drawText(footerRect, QtCore.Qt.AlignRight, "Page {} of {}".format(pageNumber+1, pageCount))
    painter.drawText(footerRect, QtCore.Qt.AlignLeft, "Processado por Computador")
    painter.restore()

def printDocument(printer, doc):
    painter = QtGui.QPainter(printer)
    doc.documentLayout().setPaintDevice(printer)
    doc.setPageSize(QtCore.QSizeF(printer.pageRect().size()))
    pageSize = printer.pageRect().size()
    tm = mmToPixels(printer, textMargins)
    footerHeight = painter.fontMetrics().height()
    textRect = QtCore.QRectF(tm, tm, pageSize.width() - 2 * tm, pageSize.height() - 2 * tm - footerHeight)
    doc.setPageSize(textRect.size())
    pageCount = doc.pageCount()

    for pageIndex in range(pageCount):
        if pageIndex != 0:
            printer.newPage()
        paintPage(pageIndex, pageCount, painter, doc, textRect, footerHeight)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    document = QtGui.QTextDocument()
    cursor = QtGui.QTextCursor(document)
    blockFormat = QtGui.QTextBlockFormat()

    for i in range(10):
        cursor.insertBlock(blockFormat)
        cursor.insertHtml("<h1>This is the {} page</h1>".format(i+1))
        blockFormat.setPageBreakPolicy(QtGui.QTextFormat.PageBreak_AlwaysBefore)

    printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
    printer.setPageSize(QtPrintSupport.QPrinter.B4)
    printer.setOutputFormat(QtPrintSupport.QPrinter.PdfFormat)

    dialog = QtPrintSupport.QPrintPreviewDialog(printer)
    doc = document
    dialog.paintRequested.connect(lambda print, doc=document: printDocument(printer, doc))

    sys.exit(dialog.exec_())

