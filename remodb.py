import psycopg2 as pg

database = "vfdtvzqx"
user = "vfdtvzqx"
host = "tantor.db.elephantsql.com"
passw = "g58Ew86uW-5dhKuloZ7X8qFKRQZC1NSI"

try:
    conn = pg.connect("dbname="{}" user="{}" host="{}" password="{}"".format(database, user, host, passw))
    cursor = conn.cursor()

    sql = "drop table produtos"
    cursor.execute(sql)
    conn.commit()

    print("Success!")
except Exception as e:
    print('Erro: {} '.format(e))
