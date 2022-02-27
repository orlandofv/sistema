from PyQt5.QtWidgets import QItemDelegate, QDateEdit, QApplication, QStyle, QTextEdit
from PyQt5.QtCore import QDate, Qt, QVariant, QSize
from PyQt5.QtGui import QColor, QTextDocument


class GenericDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(GenericDelegate, self).__init__(parent)
        self.delegates = {}

    def insertColumnDelegate(self, column, delegate):
        delegate.setParent(self)

        self.delegates[column] = delegate

    def removeColumnDelegate(self, column):
        if column in self.delegates:
            del self.delegates[column]

    def paint(self, painter, option, index):
        delegate = self.delegates.get(index.column())

        if delegate is not None:
            delegate.paint(painter, option, index)
        else:
            QItemDelegate.paint(self, painter, option, index)

    def createEditor(self, parent, option, index):
        delegate = self.delegates.get(index.column())

        if delegate is not None:
            return delegate.createEditor(parent, option, index)
        else:
            return QItemDelegate.createEditor(self, parent, option, index)

    def setEditorData(self, editor, index):
        delegate = self.delegates.get(index.column())

        if delegate is not None:
            delegate.setEditorData(editor, index)
        else:
            QItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        delegate = self.delegates.get(index.column())

        if delegate is not None:
            delegate.setModelData(editor, model, index)
        else:
            QItemDelegate.setModelData(self, editor, model, index)


class DateColumnDelegate(QItemDelegate):
    def __init__(self, minimum=QDate(), maximum=QDate.currentDate(), format="dd-MM-yyyy", parent=None):
        super(DateColumnDelegate, self).__init__(parent)
        self.minimum = minimum
        self.maximum = maximum
        self.format = str(format)

    def createEditor(self, parent, option, index):
        dateedit = QDateEdit(parent)

        dateedit.setDateRange(self.minimum, self.maximum)
        dateedit.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        dateedit.setDisplayFormat(self.format)
        dateedit.setCalendarPopup(True)
        return dateedit

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.DisplayRole).toDate()

        editor.setDate(value)

    def setModelData(self, editor, model, index):
        model.setData(index, QVariant(editor.date()))


class RichTextColumnDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(RichTextColumnDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):

        # lineedit = richtextlineedit.RichTextLineEdit(parent)
        lineedit = QTextEdit(parent)

        return lineedit

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.DisplayRole).toString()

        editor.setHtml(value)

    def setModelData(self, editor, model, index):
        model.setData(index, QVariant(editor.toSimpleHtml()))

    def paint(self, painter, option, index):
        text = index.model().data(index, Qt.DisplayRole).toString()

        palette = QApplication.palette()
        document = QTextDocument()
        document.setDefaultFont(option.font)
        if option.state & QStyle.State_Selected:
            document.setHtml(str("<font color=%1>%2</font>") \
                             .arg(palette.highlightedText().color().name()) \
                             .arg(text))
        else:
            document.setHtml(text)
        painter.save()
        color = palette.highlight().color() \
            if option.state & QStyle.State_Selected \
            else QColor(index.model().data(index,
                                           Qt.BackgroundColorRole))
        painter.fillRect(option.rect, color)

        painter.translate(option.rect.x(), option.rect.y())
        document.drawContents(painter)
        painter.restore()

        if option.state & QStyle.State_Selected:
            if text.startsWith("<html>"):
                text = str(text).replace("<body ", str("<body bgcolor=%1 ".format(palette.highlightedText().color().name())))
            else:
                text = str("<font color=%1>%2</font>".format(palette.highlightedText().color().name(),text))
                document.setHtml(text)

    def sizeHint(self, option, index):
        text = index.model().data(index).toString()

        document = QTextDocument()
        document.setDefaultFont(option.font)
        document.setHtml(text)
        return QSize(document.idealWidth() + 5, option.fontMetrics.height())

