from database.postgres import conectar_postgres


def criar_tabelas():

    conexao = conectar_postgres()
    cursor = conexao.cursor()


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS credenciadas(

        id SERIAL PRIMARY KEY,

        nome TEXT NOT NULL,

        tipo_cobranca TEXT,

        email TEXT,

        telefone TEXT,

        contato TEXT,

        observacoes TEXT,

        observacoes_internas TEXT,

        situacao_financeira TEXT

    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS empresas(

        id SERIAL PRIMARY KEY,

        credenciada_id INTEGER NOT NULL,

        nome TEXT NOT NULL,

        FOREIGN KEY (credenciada_id)
        REFERENCES credenciadas(id)

    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exames(

        id SERIAL PRIMARY KEY,

        nome TEXT NOT NULL,

        valor REAL DEFAULT 0,

        situacao TEXT DEFAULT 'Ativo'

    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS precos_credenciada(

        id SERIAL PRIMARY KEY,

        credenciada_id INTEGER NOT NULL,

        exame_id INTEGER NOT NULL,

        valor REAL NOT NULL,

        UNIQUE(credenciada_id, exame_id),

        FOREIGN KEY (credenciada_id)
        REFERENCES credenciadas(id),

        FOREIGN KEY (exame_id)
        REFERENCES exames(id)

    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS atendimentos(

        id SERIAL PRIMARY KEY,

        data_atendimento DATE NOT NULL,

        credenciada_id INTEGER NOT NULL,

        empresa_id INTEGER NOT NULL,

        colaborador TEXT NOT NULL,

        tipo_atendimento TEXT NOT NULL,

        situacao_financeira TEXT DEFAULT 'FATURAR',

        observacoes TEXT,

        FOREIGN KEY (credenciada_id)
        REFERENCES credenciadas(id),

        FOREIGN KEY (empresa_id)
        REFERENCES empresas(id)

    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS atendimento_exames(

        id SERIAL PRIMARY KEY,

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


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS faturamentos(

        id SERIAL PRIMARY KEY,

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


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS faturamento_itens(

        id SERIAL PRIMARY KEY,

        faturamento_id INTEGER NOT NULL,

        exame_id INTEGER,

        nome_exame TEXT,

        quantidade INTEGER,

        valor_unitario REAL,

        valor_total REAL

    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(

        id SERIAL PRIMARY KEY,

        nome TEXT NOT NULL,

        usuario TEXT UNIQUE NOT NULL,

        senha TEXT NOT NULL,

        perfil TEXT NOT NULL,

        ativo INTEGER DEFAULT 1

    )
    """)

    cursor.execute("""
    ALTER TABLE credenciadas
    ADD COLUMN IF NOT EXISTS tipo_cobranca TEXT
    """)


    conexao.commit()

    conexao.close()


    print("Tabelas PostgreSQL criadas com sucesso!")


if __name__ == "__main__":

    criar_tabelas()