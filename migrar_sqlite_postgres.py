import sqlite3
from database.postgres import conectar_postgres


def migrar_tabela(nome_tabela):

    sqlite = sqlite3.connect("sigac.db")
    sqlite.row_factory = sqlite3.Row

    cursor_sqlite = sqlite.cursor()

    postgres = conectar_postgres()
    cursor_postgres = postgres.cursor()


    cursor_sqlite.execute(
        f"SELECT * FROM {nome_tabela}"
    )

    registros = cursor_sqlite.fetchall()


    for registro in registros:

        colunas = registro.keys()

        valores = [
            registro[coluna]
            for coluna in colunas
        ]

        campos = ",".join(colunas)

        marcadores = ",".join(
            ["%s"] * len(valores)
        )


        comando = f"""
            INSERT INTO {nome_tabela}
            ({campos})
            VALUES ({marcadores})
            ON CONFLICT DO NOTHING
        """


        cursor_postgres.execute(
            comando,
            valores
        )


    postgres.commit()

    postgres.close()

    sqlite.close()


    print(
        f"Tabela {nome_tabela} migrada: {len(registros)} registros"
    )



def iniciar_migracao():

    postgres = conectar_postgres()
    cursor = postgres.cursor()

    cursor.execute("""
        TRUNCATE TABLE
        faturamento_itens,
        faturamentos,
        atendimento_exames,
        atendimentos,
        precos_credenciada,
        empresas,
        exames,
        credenciadas,
        usuarios
        RESTART IDENTITY CASCADE
    """)

    postgres.commit()

    postgres.close()


    tabelas = [

        "credenciadas",

        "empresas",

        "exames",

        "precos_credenciada",

        "atendimentos",

        "atendimento_exames",

        "faturamentos",

        "faturamento_itens",

        "usuarios"

    ]


    for tabela in tabelas:

        migrar_tabela(tabela)



if __name__ == "__main__":
    print("INICIANDO MIGRAÇÃO DO SIGAC...")

    iniciar_migracao()

    print("MIGRAÇÃO FINALIZADA COM SUCESSO!")