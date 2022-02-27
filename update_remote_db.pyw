# -*- coding: utf-8 -*-

import sys

import psycopg2 as pg
import mysql.connector as mc
import sqlite3 as lite

from PyQt5.QtWidgets import QListWidget, QWidget, QLabel, QApplication, QVBoxLayout
from PyQt5.QtCore import QObject

EMPRESAS_DB = 'lista_de_Empresa.db'

# Base de dados local
local_conn = ""
local_cur = ""

database = "vfdtvzqx"
user = "vfdtvzqx"
host = "tantor.db.elephantsql.com"
passw = "g58Ew86uW-5dhKuloZ7X8qFKRQZC1NSI"

#
# self.remote_conn = pg.connect("dbname="{}" user="{}" host="{}" password="{}"".format(database, user, host, passw))
# self.remote_cur = self.remote_conn.cursor()


class RemoteDb(QObject):

    def __init__(self, parent=None):
        super(RemoteDb, self).__init__(parent)
        # self.ui()

        try:
            self.empresa_con = lite.connect(EMPRESAS_DB)
            self.empresa_cur = self.empresa_con.cursor()
            print('Base de Dados Empresas connectada com Sucesso!')

            sql = 'select nome from empresas'

            self.empresa_cur.execute(sql)
            data = self.empresa_cur.fetchall()

            if len(data) > 0:
                for x in data:
                    print(x[0])
                    self.local_db_connect(x[0])
            else:
                print("A Sair...")
                exit(True)

        except Exception as e:
            print('Erro {}'.format(e))

    def ui(self):
        self.listbox = QListWidget(self)

        label = QLabel('Actualizando a Base de dados remota')

        vbox = QVBoxLayout()
        vbox.addWidget(label)
        vbox.addWidget(self.listbox)

        self.setLayout(vbox)

    def local_db_connect(self, nome_da_empresa):

        print('Connectando a Base de dados local...')
        sql = """SELECT empresa, db_name, db, host, user, passw from connection WHERE empresa = '{}' """.format(nome_da_empresa)

        self.empresa_cur.execute(sql)
        data = self.empresa_cur.fetchall()

        if len(data) > 0:
            print('Empresa localizada, Empresa: {}, Base de dados: {}, Nome da Base de dados: {}, host: {}, '
                  'User: {}'.format(data[0][0], data[0][1], data[0][2], data[0][3], data[0][4]))

            if data[0][1] == "SQLITE":

                local_conn = lite.connect(data[0][2])
                local_cur = local_conn.cursor()

            else:
                try:
                    local_conn = mc.connect(host=data[0][3],
                                       user=data[0][4],
                                       passwd=data[0][5],
                                       db=data[0][2])
                    local_cur = local_conn.cursor()
                except mc.Error as e:
                    print(e)
                    return False
            print('Base de dados local connectada com sucesso...')
            if self.remote_db_connect() is False:
                print("Base de dados remota nao connectada...")
                return

            print('Criando a lista de Produtos...')
            # Lista total de produtos Locais
            sql = "select cod, nome, preco, quantidade from produtos"

            local_cur.execute(sql)
            data_list = local_cur.fetchall()
            # Fim da lista de produtos

            # Obtemos o nome da Empresa
            empresa = nome_da_empresa

            if len(data_list) == 0:
                print("Lista Local vazia")
                return

            lista = []
            for x in data_list:

                l = list(x)
                l.insert(0, empresa)
                lista.append(l)

            print("Verificando a existencia de dados...")
            sql = "Delete from produtos WHERE empresa='{empresa}'".format(empresa=empresa)

            self.remote_cur.execute(sql)

            z = [tuple(y) for y in lista]
            print("lista local: {}".format(z))
            print("novos produtos: {}".format(len(z)))

            values_to_insert = z
            query = "INSERT INTO produtos (empresa, cod, nome, preco, quantidade) VALUES " + \
                    ",".join("(%s, %s, %s, %s, %s)" for _ in values_to_insert)

            flattened_values = [item for sublist in values_to_insert for item in sublist]

            self.remote_cur.execute(query, flattened_values)
            self.remote_conn.commit()

            print('dados Inseridos com sucesso')

    def remote_db_connect(self, database='vfdtvzqx', user='vfdtvzqx', host='tantor.db.elephantsql.com',
                          passw='g58Ew86uW-5dhKuloZ7X8qFKRQZC1NSI'):
        # database = "postgres"
        # user = "postgres"
        # host = "127.0.0.1"
        # passw = "abc123@123"

        print('Conectando a Base de dados Remota....')
        try:
            self.remote_conn = pg.connect("dbname='{}' user='{}' host='{}' password='{}' ".format(database, user, host, passw))
            self.remote_cur = self.remote_conn.cursor()

            # sql = "drop table if exists produtos"

            sql = """create table if not exists produtos
            (empresa varchar not null,
            cod varchar not null,
            nome varchar not null,
            preco real,
            quantidade real
            )"""

            self.remote_cur.execute(sql)
            self.remote_conn.commit()

            print("Base de dados remota connectada com Successo!")
            return True
        except Exception as e:

            print('Erro: {} '.format(e))
            return False


if __name__ == '__main__':
    app = QApplication(sys.argv)

    helloPythonWidget = RemoteDb()
    sys.exit(app.exec_())