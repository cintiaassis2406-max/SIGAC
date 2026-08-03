import sqlite3


def conectar():

    conexao = sqlite3.connect("sigac.db")
    conexao.row_factory = sqlite3.Row

    return conexao


def criar_banco():

    conexao = conectar()
    cursor = conexao.cursor()

    # ==================================================
    # TABELA CREDENCIADAS
    # ==================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS credenciadas(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        nome TEXT NOT NULL,


        email TEXT,

        telefone TEXT,

        contato TEXT,

        observacoes TEXT,

        observacoes_internas TEXT,

        situacao_financeira TEXT DEFAULT NULL

    )
    """)

    # ==================================================
    # TABELA EMPRESAS
    # ==================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS empresas(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        credenciada_id INTEGER NOT NULL,

        nome TEXT NOT NULL,

        FOREIGN KEY (credenciada_id)
            REFERENCES credenciadas(id)

    )
    """)

    # ==================================================
    # TABELA EXAMES
    # ==================================================

    cursor.execute("""
CREATE TABLE IF NOT EXISTS exames(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    nome TEXT NOT NULL,

    situacao TEXT NOT NULL DEFAULT 'Ativo'

)
    """)
    # ==================================================
    # TABELA PREÇOS POR CREDENCIADA
    # ==================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS precos_credenciada(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        credenciada_id INTEGER NOT NULL,

        exame_id INTEGER NOT NULL,

        valor REAL NOT NULL,

        FOREIGN KEY (credenciada_id)
        REFERENCES credenciadas(id),

        FOREIGN KEY (exame_id)
        REFERENCES exames(id),

        UNIQUE(credenciada_id, exame_id)

)
""")
    # ==================================================
    # TABELA ATENDIMENTOS
    # ==================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS atendimentos(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        data_atendimento DATE NOT NULL,

        credenciada_id INTEGER NOT NULL,

        empresa_id INTEGER NOT NULL,

        colaborador TEXT NOT NULL,

        tipo_atendimento TEXT NOT NULL,

        situacao_financeira TEXT NOT NULL DEFAULT 'FATURAR',

        observacoes TEXT,

        FOREIGN KEY (credenciada_id)
            REFERENCES credenciadas(id),

        FOREIGN KEY (empresa_id)
            REFERENCES empresas(id)

    )
    """)

    # ==================================================
    # TABELA ATENDIMENTO_EXAMES
    # ==================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS atendimento_exames(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        atendimento_id INTEGER NOT NULL,

        exame_id INTEGER NOT NULL,

        nome_exame TEXT NOT NULL,

        valor_exame REAL,

        FOREIGN KEY (atendimento_id)
            REFERENCES atendimentos(id),

        FOREIGN KEY (exame_id)
            REFERENCES exames(id)

    )
    """)


    # ==================================================
    # TABELA FATURAMENTOS
    # ==================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS faturamentos(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        credenciada_id INTEGER NOT NULL,

        mes INTEGER NOT NULL,

        ano INTEGER NOT NULL,

        valor_total REAL DEFAULT 0,

        status TEXT DEFAULT 'Em Conferência',

        data_liberacao_recepcao TEXT,
        usuario_liberacao_recepcao TEXT,

        data_envio_credenciada TEXT,
        usuario_envio_credenciada TEXT,

        data_correcao TEXT,
        usuario_correcao TEXT,

        data_fechamento TEXT,
        usuario_fechamento TEXT,

        observacao TEXT,

        FOREIGN KEY (credenciada_id)
            REFERENCES credenciadas(id)

    )
    """)





    # ==================================================
    # TABELA FATURAMENTO_ITENS
    # ==================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS faturamento_itens(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        faturamento_id INTEGER NOT NULL,

        exame_id INTEGER,

        nome_exame TEXT,

        quantidade INTEGER,

        valor_unitario REAL,

        valor_total REAL,

        FOREIGN KEY (faturamento_id)
            REFERENCES faturamentos(id)

    )
    """)
    # ==================================================
    # TABELA USUÁRIOS
    # ==================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        nome TEXT NOT NULL,

        usuario TEXT NOT NULL UNIQUE,

        senha TEXT NOT NULL,

        perfil TEXT NOT NULL,

        ativo INTEGER DEFAULT 1

    )
    """)

    conexao.commit()
    conexao.close()