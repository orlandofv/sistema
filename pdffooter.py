import os
import pyreportjasper as pyjasper


input_file = os.path.dirname(os.path.abspath(__file__)) + \
             '/relatorios/Invoice.jrxml'

database = 'dados.tsdb'
data_file = "dados.json"

def compiling():

    jasper = pyjasper.JasperPy()
    jasper.compile(input_file)

def processing():
    con = {'data_file': data_file ,'driver': 'json'}

    output = os.path.dirname(os.path.abspath(__file__)) + '/relatorios'
    jasper = pyjasper.JasperPy()
    jasper.process(input_file, output_file=output, parameters={""}, db_connection=con, format_list=["pdf", "rtf"])

compile = compiling()
process = processing()
