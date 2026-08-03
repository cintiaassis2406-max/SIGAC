from database.database import conectar


def executar_migrations():

    conexao = conectar()
    cursor = conexao.cursor()


    # ===============================
    # ATUALIZA TABELA FATURAMENTOS
    # ===============================

    cursor.execute("PRAGMA table_info(faturamentos)")
    colunas = [c[1] for c in cursor.fetchall()]

    novas_colunas = [

        ("data_liberacao_recepcao", "TEXT"),
        ("usuario_liberacao_recepcao", "TEXT"),

        ("data_envio_credenciada", "TEXT"),
        ("usuario_envio_credenciada", "TEXT"),

        ("data_correcao", "TEXT"),
        ("usuario_correcao", "TEXT"),

        ("usuario_fechamento", "TEXT"),

        ("observacao", "TEXT")

    ]

    for nome, tipo in novas_colunas:

        if nome not in colunas:

            cursor.execute(
                f"ALTER TABLE faturamentos ADD COLUMN {nome} {tipo}"
            )


    # ===============================
    # ATUALIZA TABELA ATENDIMENTOS
    # ===============================

    cursor.execute("PRAGMA table_info(atendimentos)")
    colunas_atendimentos = [
        c[1]
        for c in cursor.fetchall()
    ]


    if "situacao_financeira" not in colunas_atendimentos:

        cursor.execute("""
            ALTER TABLE atendimentos
            ADD COLUMN situacao_financeira TEXT
            DEFAULT 'FATURAR'
        """)


    conexao.commit()
    conexao.close()