#!/usr/bin/env python3
# Copyright (c) 2008-9 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License, or
# version 3 of the License, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.

import math
import sys
from PyQt5.QtCore import (QDate, QRectF, Qt, QSizeF)
from PyQt5.QtGui import (QFont, QFontMetrics, QPainter, QPixmap, QTextBlockFormat, QTextCharFormat, QTextCursor,
                         QTextDocument, QTextFormat, QTextOption, QTextTableFormat)

from PyQt5.QtPrintSupport import QPrintDialog, QPrinter, QPrintPreviewDialog
from PyQt5.QtWidgets import (QApplication, QDialog, QPushButton, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QHBoxLayout)

# import qrc_resources


DATE_FORMAT = "MMM d, yyyy"


class Statement(object):

    def __init__(self, company, contact, address):
        self.company = company
        self.contact = contact
        self.address = address
        self.transactions = []  # List of (QDate, float) two-tuples

    def balance(self):
        return sum([amount for date, amount in self.transactions])


class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        self.printer = QPrinter()
        self.printer.setPageSize(QPrinter.A8)
        self.generateFakeStatements()
        self.table = QTableWidget()
        self.populateTable()

        cursorButton = QPushButton("Print via Q&Cursor")
        htmlButton = QPushButton("Print via &HTML")
        painterButton = QPushButton("Print via Q&Painter")
        quitButton = QPushButton("&Quit")

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(cursorButton)
        buttonLayout.addWidget(htmlButton)
        buttonLayout.addWidget(painterButton)
        buttonLayout.addStretch()
        buttonLayout.addWidget(quitButton)
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

        cursorButton.clicked.connect(self.printViaQCursor)
        htmlButton.clicked.connect(self.printViaHtml)
        painterButton.clicked.connect(self.printViaQPainter)
        quitButton.clicked.connect(self.accept)

        self.setWindowTitle("Printing")


    def generateFakeStatements(self):
        self.statements = []
        statement = Statement("Consality", "Ms S. Royal",
                "234 Rue Saint Hyacinthe, 750201, Paris")
        statement.transactions.append((QDate(2007, 8, 11), 2342))
        statement.transactions.append((QDate(2007, 9, 10), 2342))
        statement.transactions.append((QDate(2007, 10, 9), 2352))
        statement.transactions.append((QDate(2007, 10, 17), -1500))
        statement.transactions.append((QDate(2007, 11, 12), 2352))
        statement.transactions.append((QDate(2007, 12, 10), 2352))
        statement.transactions.append((QDate(2007, 12, 20), -7500))
        statement.transactions.append((QDate(2007, 12, 20), 250))
        statement.transactions.append((QDate(2008, 1, 10), 2362))


        self.statements.append(statement)

        statement = Statement("Demamitur Plc", "Mr G. Brown",
                "14 Tall Towers, Tower Hamlets, London, WC1 3BX")
        statement.transactions.append((QDate(2007, 5, 21), 871))
        statement.transactions.append((QDate(2007, 6, 20), 542))
        statement.transactions.append((QDate(2007, 7, 20), 1123))
        statement.transactions.append((QDate(2007, 7, 20), -1928))
        statement.transactions.append((QDate(2007, 8, 13), -214))
        statement.transactions.append((QDate(2007, 9, 15), -3924))
        statement.transactions.append((QDate(2007, 9, 15), 2712))
        statement.transactions.append((QDate(2007, 9, 15), -273))
        statement.transactions.append((QDate(2007, 11, 8), -728))
        statement.transactions.append((QDate(2008, 2, 7), 228))
        statement.transactions.append((QDate(2008, 3, 13), -508))
        statement.transactions.append((QDate(2008, 3, 22), -2481))
        statement.transactions.append((QDate(2008, 4, 5), 195))
        self.statements.append(statement)


    def populateTable(self):
        headers = ["Company", "Contact", "Address", "Balance"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(self.statements))
        for row, statement in enumerate(self.statements):
            self.table.setItem(row, 0, QTableWidgetItem(statement.company))
            self.table.setItem(row, 1, QTableWidgetItem(statement.contact))
            self.table.setItem(row, 2, QTableWidgetItem(statement.address))
            item = QTableWidgetItem("$ %L1".format(float(statement.balance())))
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 3, item)
        self.table.resizeColumnsToContents()


    def printViaHtml(self):
        document = QTextDocument()
        html = """
        <head>
            <title>Report</title>
            <style>
            </style>
        </head>
        <body>
            <table width="100%">
                <tr>
                    <td><img src="{}" width="30"></td>
                    <td><h1>REPORT</h1></td>
                </tr>
            </table>
            <hr>
            <p align=right><img src="{}" width="300"></p>
            <p align=right>Sample</p>
        </body>
        """.format('./icons/add_2.ico', './icons/add_2.ico')

        document.setHtml(html)

        printer = QPrinter()
        printer.setResolution(printer.HighResolution)
        printer.setPageSize(QPrinter.A8)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName("test.pdf")
        printer.setPageMargins(1, 1, 1, 1, QPrinter.Millimeter)
        document.setPageSize(QSizeF(printer.pageRect().size()))
        print(document.pageSize(), printer.resolution(), printer.pageRect())

        document.print_(printer)

    def printViaQCursor(self):
        dialog = QPrintDialog(self.printer, self)
        if not dialog.exec_():
            return
        logo = QPixmap(":/logo.ico")
        headFormat = QTextBlockFormat()
        headFormat.setAlignment(Qt.AlignLeft)
        headFormat.setTextIndent(
                self.printer.pageRect().width() - logo.width() - 16)
        bodyFormat = QTextBlockFormat()
        bodyFormat.setAlignment(Qt.AlignJustify)
        lastParaBodyFormat = QTextBlockFormat(bodyFormat)
        lastParaBodyFormat.setPageBreakPolicy(
                QTextFormat.PageBreak_AlwaysAfter)
        rightBodyFormat = QTextBlockFormat()
        rightBodyFormat.setAlignment(Qt.AlignRight)
        headCharFormat = QTextCharFormat()
        headCharFormat.setFont(QFont("Helvetica", 8))
        bodyCharFormat = QTextCharFormat()
        bodyCharFormat.setFont(QFont("Times", 8))
        redBodyCharFormat = QTextCharFormat(bodyCharFormat)
        redBodyCharFormat.setForeground(Qt.red)
        tableFormat = QTextTableFormat()
        tableFormat.setBorder(0)
        tableFormat.setCellPadding(2)
        document = QTextDocument()
        cursor = QTextCursor(document)
        mainFrame = cursor.currentFrame()
        page = 1
        for statement in self.statements:
            cursor.insertBlock(headFormat, headCharFormat)
            cursor.insertImage(":/logo.ico")
            for text in ("Greasy Hands Ltd.", "New Lombard Street",
                         "London", "WC13 4PX",
                         QDate.currentDate().toString(DATE_FORMAT)):
                cursor.insertBlock(headFormat, headCharFormat)
                cursor.insertText(text)
            for line in statement.address.split(", "):
                cursor.insertBlock(bodyFormat, bodyCharFormat)
                cursor.insertText(line)
            cursor.insertBlock(bodyFormat)
            cursor.insertBlock(bodyFormat, bodyCharFormat)
            cursor.insertText("Dear {0},".format(statement.contact))
            cursor.insertBlock(bodyFormat)
            cursor.insertBlock(bodyFormat, bodyCharFormat)
            balance = statement.balance()
            cursor.insertText("The balance of your account is $ %L1.".format(float(balance)))
            if balance < 0:
                cursor.insertBlock(bodyFormat, redBodyCharFormat)
                cursor.insertText("Please remit the amount owing "
                                  "immediately.")
            else:
                cursor.insertBlock(bodyFormat, bodyCharFormat)
                cursor.insertText("We are delighted to have done "
                                  "business with you.")
            cursor.insertBlock(bodyFormat, bodyCharFormat)
            cursor.insertText("Transactions:")
            table = cursor.insertTable(len(statement.transactions), 3,
                                       tableFormat)
            row = 0
            for date, amount in statement.transactions:
                cellCursor = table.cellAt(row, 0).firstCursorPosition()
                cellCursor.setBlockFormat(rightBodyFormat)
                cellCursor.insertText(date.toString(DATE_FORMAT),
                                      bodyCharFormat)
                cellCursor = table.cellAt(row, 1).firstCursorPosition()
                if amount > 0:
                    cellCursor.insertText("Credit", bodyCharFormat)
                else:
                    cellCursor.insertText("Debit", bodyCharFormat)
                cellCursor = table.cellAt(row, 2).firstCursorPosition()
                cellCursor.setBlockFormat(rightBodyFormat)
                format = bodyCharFormat
                if amount < 0:
                    format = redBodyCharFormat
                cellCursor.insertText("$ %L1".format(float(amount)), format)
                row += 1
            cursor.setPosition(mainFrame.lastPosition())
            cursor.insertBlock(bodyFormat, bodyCharFormat)
            cursor.insertText("We hope to continue doing business "
                              "with you,")
            cursor.insertBlock(bodyFormat, bodyCharFormat)
            cursor.insertText("Yours sincerely")
            cursor.insertBlock(bodyFormat)
            if page == len(self.statements):
                cursor.insertBlock(bodyFormat, bodyCharFormat)
            else:
                cursor.insertBlock(lastParaBodyFormat, bodyCharFormat)
            cursor.insertText("K. Longrey, Manager")
            page += 1

        document.setDocumentMargin(0)
        document.print_(self.printer)


    def printViaQPainter(self):
        dialog = QPrintDialog(self.printer, self)

        if not dialog.exec_():
            return
        LeftMargin = 2
        sansFont = QFont("Helvetica", 8)
        sansLineHeight = QFontMetrics(sansFont).height()
        serifFont = QFont("Times", 8)
        fm = QFontMetrics(serifFont)
        DateWidth = fm.width(" September 99, 2999 ")
        CreditWidth = fm.width(" Credit ")
        AmountWidth = fm.width(" W999999.99 ")
        serifLineHeight = fm.height()
        logo = QPixmap(":/logo.ico")
        painter = QPainter(self.printer)

        pageRect = self.printer.pageRect()
        page = 1
        for statement in self.statements:
            painter.save()
            y = 0
            x = pageRect.width() - logo.width() - LeftMargin
            painter.drawPixmap(x, 0, logo)
            y += logo.height() + sansLineHeight
            painter.setFont(sansFont)
            painter.drawText(x, y, "Greasy Hands Ltd.")
            y += sansLineHeight
            painter.drawText(x, y, "New Lombard Street")
            y += sansLineHeight
            painter.drawText(x, y, "London")
            y += sansLineHeight
            painter.drawText(x, y, "WC13 4PX")
            y += sansLineHeight
            painter.drawText(x, y,
                    QDate.currentDate().toString(DATE_FORMAT))
            y += sansLineHeight
            painter.setFont(serifFont)
            x = LeftMargin
            for line in statement.address.split(", "):
                painter.drawText(x, y, line)
                y += serifLineHeight
            y += serifLineHeight
            painter.drawText(x, y, "Dear {0},".format(statement.contact))
            y += serifLineHeight
            balance = statement.balance()
            painter.drawText(x, y, "The balance of your account is $ %L1".format(float(balance)))
            y += serifLineHeight
            if balance < 0:
                painter.setPen(Qt.red)
                text = "Please remit the amount owing immediately."
            else:
                text = ("We are delighted to have done business "
                        "with you.")
            painter.drawText(x, y, text)
            painter.setPen(Qt.black)
            y += int(serifLineHeight * 1.5)
            painter.drawText(x, y, "Transactions:")
            y += serifLineHeight
            option = QTextOption(Qt.AlignRight|
                                       Qt.AlignVCenter)
            for date, amount in statement.transactions:
                x = LeftMargin
                h = int(fm.height() * 1.3)
                painter.drawRect(x, y, DateWidth, h)
                painter.drawText(QRectF(x + 3, y + 3,
                                        DateWidth - 6, h - 6),
                                 date.toString(DATE_FORMAT), option)
                x += DateWidth
                painter.drawRect(x, y, CreditWidth, h)
                text = "Credit"
                if amount < 0:
                    text = "Debit"
                painter.drawText(QRectF(x + 3, y + 3,
                                 CreditWidth - 6, h - 6), text, option)
                x += CreditWidth
                painter.drawRect(x, y, AmountWidth, h)
                if amount < 0:
                    painter.setPen(Qt.red)
                painter.drawText(
                        QRectF(x + 3, y + 3, AmountWidth - 6, h - 6), "$ %L1".format(float(amount)), option)
                painter.setPen(Qt.black)
                y += h
            y += serifLineHeight
            x = LeftMargin
            painter.drawText(x, y, "We hope to continue doing "
                                   "business with you,")
            y += serifLineHeight
            painter.drawText(x, y, "Yours sincerely")
            y += serifLineHeight * 3
            painter.drawText(x, y, "K. Longrey, Manager")
            x = LeftMargin
            y = pageRect.height() - 54
            painter.drawLine(x, y, pageRect.width() - LeftMargin, y)
            y += 2
            font = QFont("Helvetica", 9)
            font.setItalic(True)
            painter.setFont(font)
            option = QTextOption(Qt.AlignCenter)
            option.setWrapMode(QTextOption.WordWrap)
            painter.drawText(
                    QRectF(x, y, pageRect.width() - 2 * LeftMargin, 31),
                    "The contents of this letter are for information "
                    "only and do not form part of any contract.",
                    option)
            page += 1
            if page <= len(self.statements):
                self.printer.newPage()
            painter.restore()

            dlg = QPrintPreviewDialog(self)
            dlg.paintRequested.connect(painter)
            dlg.showMaximized()
            dlg.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = Form()
    form.show()
    app.exec_()

