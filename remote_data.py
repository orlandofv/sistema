# -*- coding: utf-8 -*-

from PyQt5.QtCore import QDate, QDateTime
import mysql.connector as mc
import sqlite3 as lite


EMPRESAS_DB = 'lista_de_Empresa.db'
conn = lite.connect('dadoscopia.tsdb')
cur = conn.cursor()
conn1 = mc.connect(host="localhost",
                   user="root",
                   passwd="abc123@123",
                   db="microgest")
cur1 = conn1.cursor()

lista_de_tabelas = ['armazem', 'familia', 'subfamilia', 'produtos', 'stock', 'facturacao',
                    'documentos', 'taxas', 'caixa', 'clientes', 'fornecedores', 'users', 'recibos']

lista_de_tabelas_completa = ['clientes', 'fornecedores', 'documentos','taxas', 'caixa','armazem', 'users', 'familia',
                             'subfamilia', 'produtos', 'stock', 'stockdetalhe', 'facturacao', 'facturacaodetalhe',
                             'recibos', 'recibosdetalhe']

def cria_lista_de_produtos(self):

    if connect_db() is False:
        return

    # Lista total de produtos Locais
    sql = "select cod, nome, preco, quantidade from produtos"

    self.parent_cur.execute(sql)
    self.data_list = self.parent_cur.fetchall()
    # Fim da lista de produtos

    # Obtemos o nome da Empresa
    empresa = self.empresa

    # Se a Lista de produtos nao for vazia
    if len(self.data_list) > 0:

        # Para cada tupla. Nota: A tupla representa a linha de dados na tabela produtos
        for x in self.data_list:

            # transformamos a tupla em lista
            lista = list(x)

            # Inserimos o nome da Empresa na Lista
            lista.insert(0, empresa)

            # Transformamos a Lista numa tupla
            tupla = tuple(lista)

            # Verificamos se a existe o produtom mesmo codigo e Empresa na tabela remota
            sql = "Select * from produtos_2 WHERE cod = '{codigo}' and " \
                  "empresa='{empresa}'".format(empresa=tupla[0], codigo=tupla[1])

            self.cur.execute(sql)
            data = self.cur.fetchall()

            # Se nao existir algum produto remoto igual
            if len(data) == 0:

                # Inserimos novos dados
                sql = """ Insert into produtos_2 (empresa, cod, nome, preco, quantidade)
                values ('{empresa}', '{codigo}', '{nome}', {preco}, {qty}) 
                """.format(empresa=tupla[0], codigo=tupla[1], nome=str(tupla[2]).replace("'", ""), preco=tupla[3],
                           qty=tupla[4])
            else:

                # Actualizamos os dados
                sql = """ update produtos_2  set quantidade={qty}, preco = {preco}  WHERE cod='{codigo}' 
                and empresa='{empresa}' """.format(empresa=tupla[0], codigo=tupla[1], nome=tupla[2],
                                                   preco=tupla[3], qty=tupla[4])

            self.cur.execute(sql)

        self.conn.commit()

        self.fill_table()

    return self.data_list


def connect_db(self):
    database = "postgres"
    user = "postgres"
    host = "127.0.0.1"
    passw = "abc123@123"

    database = "vfdtvzqx"
    user = "vfdtvzqx"
    host = "tantor.db.elephantsql.com"
    passw = "g58Ew86uW-5dhKuloZ7X8qFKRQZC1NSI"

    try:
        self.conn = pg.connect("dbname="{}" user="{}" host="{}" password="{}"".format(database, user, host, passw))
        self.cur = self.conn.cursor()

        sql = """create table if not exists produtos_2
        (id serial not null primary key,
        empresa varchar not null,
        cod varchar not null unique,
        nome varchar not null,
        preco real,
        quantidade real
        )"""

        # sql = "drop table if exists produtos"

        self.cur.execute(sql)
        self.conn.commit()

        print("Success!")
        return True
    except Exception as e:

        print('Erro: {} '.format(e))
        return False

def update_fact(tabela='facturacao'):

    sql = "update {} set data = '2018-08-23' ".format(tabela)
    cur.execute(sql)

    conn.commit()

def update_fact2(tabela='facturacao'):

    sql = "update {} set extenso = '' ".format(tabela)
    cur.execute(sql)

    conn.commit()

def update_users(tabela='users'):

    sql = "update {} set nascimento = '1980-01-01' ".format(tabela)
    cur.execute(sql)

    conn.commit()

def update_data(tabela):

    sql = 'select cod, created, modified from {}'.format(tabela)
    cur.execute(sql)
    data = cur.fetchall()

    if len(data) > 0:
        for item in data:
            data = QDate.fromString(item[1]).toString("yyyy-MM-dd")
            data1 = QDate.fromString(item[1]).toString("yyyy-MM-dd")

            sql = """update {} set created= '{}', modified="{}" WHERE cod="{}" """.format(tabela, data,
                                                                                      data1, item[0])

            cur.execute(sql)


        conn.commit()

def insert_on_db(tabela):

    sql = "select * from {}".format(tabela)

    cur.execute(sql)
    data = cur.fetchall()

    count = 0
    if len(data) > 0:
        for item in data:
            count += 1
            print(count, item[1])

            sql2 = """INSERT INTO {tabela} VALUES {values} """.format(tabela=tabela, values=item)


            print(sql2)
            cur1.execute(sql2)
        conn1.commit()

update_users()
update_fact()
update_fact2()

for tabela in lista_de_tabelas:
    print('actualizando Tabela: {}'.format(tabela))
    data = update_data(tabela)

for tabela in lista_de_tabelas_completa:
    data = insert_on_db(tabela)

# self.limpar()
