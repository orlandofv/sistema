import pyreportjasper as pyjasper
import os

def json_to_pdf(input_f, output_f, json_file, json_query, format):

    """ jrxml file path """
    input_file = input_f

    """ Output file that will be generated after the job is done """

    output_file = output_f
    json_query = json_query
    data_file = json_file
    formatlist = []
    formatlist.append(format)

    jasper = pyjasper.JasperPy()
    jasper.process(input_file=input_file, output_file=output_file, format_list=formatlist[0],
                   parameters={}, db_connection={'data_file': data_file,
                                                 'driver': 'json', 'json_query': json_query})


    print(os.path.realpath(output + '.pdf'))
    os.startfile(os.path.realpath(output + '.pdf'))

input_file = 'C:\\Users\\MICROSOFT\\JaspersoftWorkspace\\MyReports\\factura.jrxml'
output = './relatorios/factura'
json_query = 'facturas'
data_file = 'factura.json'
format = ['pdf']
#
j = json_to_pdf(input_file, output, data_file, json_query, format)

