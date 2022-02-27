import os
from utilities import converte_para_pdf

caminho_python = os.path.realpath("c:\Program Files\LibreOffice\program\python.exe")
caminho = caminho_python.replace('\\', "/")
entrada = os.path.realpath("Tecla papelaria - Sucursal.odt")
saida = os.path.realpath("saida.pdf")

conv = converte_para_pdf(caminho, entrada, saida)

print(conv)