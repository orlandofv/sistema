# -*- coding: utf-8 -*-

from pathlib import Path
import sys

import sqlite3 as lite
import main
import facturacao

import lista_de_empresas
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

EMPRESAS_DB = "lista_de_Empresa.db"

LISTA_DE_EMPRESAS = []


class Connection:

    def __init__(self, modulo):

        self.modulo = modulo

        if Path(EMPRESAS_DB).is_file():

            self.conn = lite.connect(EMPRESAS_DB)
            self.cur = self.conn.cursor()

            self.__cria_empresa()

        else:
            print("Houve um erro na Inicialização. Contacte o Técnico. (+258) 84 101 0400/ (+258) 87 011 2233")

    # funcao que lida com Empresas
    def __cria_empresa(self):

        try:
            self.cur.execute("select * from empresas")
            lista = self.cur.fetchall()
            data = [tuple(str(item) for item in t) for t in lista]

            if len(data) > 0:

                for item in data:
                    # Lista de Nomes de Empresas na Base de Dados "lista_de_empresas"
                    LISTA_DE_EMPRESAS.append(item[0])

                if self.modulo == "admin":
                    self.run_admin()
                else:
                    self.run_vendas()
            else:
                self.run_new_company()

        except Exception as e:
           print("Erro de Conexão.{}.".format(e))

        self.conn.close()

    # Exibe o modulo Empresas para a escolha da Empresa em causa
    def run_admin(self):

        app = QApplication(sys.argv)

        # Enchemos a lista de Empresas modulo main
        main.LISTA_DE_EMPRESAS = LISTA_DE_EMPRESAS

        w = main.Gestor()

        w.setWindowTitle('Microgest POS')
        sys.exit(app.exec_())

    def run_vendas(self):

        app = QApplication(sys.argv)

        # Create and display the splash screen
        splash_pix = QPixmap('luxury_hotel-wallpaper-1680x1260.jpg')
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.setMask(splash_pix.mask())
        splash.show()
        app.processEvents()

        # Enchemos a lista de Empresas modulo main
        main.LISTA_DE_EMPRESAS = LISTA_DE_EMPRESAS

        w = facturacao.Cliente()
        w.setObjectName = "facturacao"
        w.setWindowTitle('Microgest POS')
        splash.finish(w)
        app.exec_()

    # Abre o modulo Empresas para a criação de Empresas
    def run_new_company(self):
        app = QApplication(sys.argv)

        w = lista_de_empresas.MainWindow()
        w.setWindowTitle('Crie Empresa')
        w.show()
        sys.exit(app.exec_())

    # Concexão com a Base de dados Empresa
    def create_db(self):
        conn = lite.connect(EMPRESAS_DB)
        cur = conn.cursor()

