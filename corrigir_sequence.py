import sqlite3

conexao = sqlite3.connect("sigac.db")
cursor = conexao.cursor()

tabelas = [
    "credenciadas",
    "empresas",
    "exames",
    "atendimentos",
    "atendimento_exames",
    "faturamentos"
]

for tabela in tabelas:
    try:
        cursor.execute(f"SELECT MAX(id) FROM {tabela}")
        resultado = cursor.fetchone()

        ultimo_id = resultado[0] or 0

        cursor.execute(
            "DELETE FROM sqlite_sequence WHERE name = ?",
            (tabela,)
        )

        cursor.execute(
            "INSERT INTO sqlite_sequence(name, seq) VALUES (?, ?)",
            (tabela, ultimo_id)
        )

        print(
            f"{tabela}: sequência corrigida para {ultimo_id}"
        )

    except Exception as e:
        print(
            f"{tabela}: {e}"
        )

conexao.commit()
conexao.close()

print("Correção concluída.")