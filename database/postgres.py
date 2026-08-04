import psycopg2


DATABASE_URL = "postgresql://sigac_db_user:TSpuCA1rs7Mq9myzNIiRJgtcFiRe307c@dpg-d9ovq43m8hqs73a0pct0-a.oregon-postgres.render.com/sigac_db"


def conectar_postgres():

    conexao = psycopg2.connect(
        DATABASE_URL
    )

    return conexao