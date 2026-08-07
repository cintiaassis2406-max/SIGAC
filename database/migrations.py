from database.database import conectar


def executar_migrations():

    conexao = conectar()
    cursor = conexao.cursor()


    # ===============================
    # ATUALIZA TABELA FATURAMENTOS
    # ===============================

    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'faturamentos'
    """)

    colunas = [c["column_name"] for c in cursor.fetchall()]

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

    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'atendimentos'
    """)

    colunas_atendimentos = [
        c["column_name"]
        for c in cursor.fetchall()
    ]


    if "situacao_financeira" not in colunas_atendimentos:

        cursor.execute("""
            ALTER TABLE atendimentos
            ADD COLUMN situacao_financeira TEXT
            DEFAULT 'FATURAR'
        """)
    # ===============================
    # ATUALIZA TABELA EXAMES
    # ===============================

    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'exames'
    """)

    colunas_exames = [
        c["column_name"]
        for c in cursor.fetchall()
    ]

    if "valor" not in colunas_exames:

        cursor.execute("""
            ALTER TABLE exames
            ADD COLUMN valor REAL DEFAULT 0
        """)

    if "situacao" not in colunas_exames:

        cursor.execute("""
            ALTER TABLE exames
            ADD COLUMN situacao TEXT DEFAULT 'Ativo'
        """)
        
    # ==========================================
    # CRIA USUÁRIO ADMIN PADRÃO
    # ==========================================

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM usuarios
    """)

    resultado = cursor.fetchone()

    if resultado["total"] == 0:

        import bcrypt

        senha = bcrypt.hashpw(
            "123456".encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        cursor.execute("""
            INSERT INTO usuarios
            (nome, usuario, senha, perfil, ativo)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            "Administrador",
            "admin",
            senha,
            "Administrador",
            1
        ))

    # ==========================================
    # CRIA TABELA DE PERMISSOES
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS permissoes (

            id SERIAL PRIMARY KEY,

            perfil TEXT NOT NULL,

            modulo TEXT NOT NULL,

            visualizar INTEGER DEFAULT 0,

            criar INTEGER DEFAULT 0,

            editar INTEGER DEFAULT 0,

            excluir INTEGER DEFAULT 0

        )
    """)


    # ==========================================
    # CRIA PERMISSOES PADRAO
    # ==========================================

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM permissoes
    """)

    resultado = cursor.fetchone()


    if resultado["total"] == 0:


        permissoes = [

            ("Recepção", "dashboard", 1, 0, 0, 0),
            ("Recepção", "atendimentos", 1, 1, 1, 0),
            ("Recepção", "credenciadas", 1, 0, 0, 0),
            ("Recepção", "empresas", 1, 0, 0, 0),
            ("Recepção", "exames", 1, 0, 0, 0),


            ("Financeiro", "dashboard", 1, 0, 0, 0),
            ("Financeiro", "atendimentos", 1, 0, 0, 0),
            ("Financeiro", "financeiro", 1, 1, 1, 0),
            ("Financeiro", "relatorios", 1, 0, 0, 0),


            ("Administrador", "dashboard", 1, 1, 1, 1),
            ("Administrador", "credenciadas", 1, 1, 1, 1),
            ("Administrador", "empresas", 1, 1, 1, 1),
            ("Administrador", "exames", 1, 1, 1, 1),
            ("Administrador", "atendimentos", 1, 1, 1, 1),
            ("Administrador", "financeiro", 1, 1, 1, 1),
            ("Administrador", "relatorios", 1, 1, 1, 1),
            ("Administrador", "usuarios", 1, 1, 1, 1),
            ("Administrador", "tabela_precos", 1, 1, 1, 1)

        ]


        cursor.executemany("""
            INSERT INTO permissoes
            (
                perfil,
                modulo,
                visualizar,
                criar,
                editar,
                excluir
            )
            VALUES (%s,%s,%s,%s,%s,%s)
        """, permissoes)
        
    conexao.commit()
    conexao.close()