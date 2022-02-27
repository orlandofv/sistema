from win32com import client
import time
import subprocess

from os import path

word = client.Dispatch("Word.Application")

filename = path.realpath('bonham_basic.odt')
wdFormatPDF = 17
print(filename)

def printWordDocument(filename, out_file):
    doc = word.Documents.Open(filename)
    doc.SaveAs(out_file, FileFormat=wdFormatPDF)
    doc.Close()

    # word.Documents.Open(filename)
    # word.ActiveDocument.PrintOut()
    # time.sleep(2)
    # word.ActiveDocument.Close()

out =  path.realpath("factura003.pdf")


printout = printWordDocument(filename, out)
subprocess.Popen(out,shell=True)
word.Quit()