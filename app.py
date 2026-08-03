from flask import Flask, render_template

from database.database import criar_banco, conectar

from routes.credenciadas import registrar_rotas as registrar_credenciadas
from routes.empresas import registrar_rotas as registrar_empresas
from routes.exames import registrar_rotas as registrar_exames
from routes.atendimentos import registrar_rotas as registrar_atendimentos
from routes.financeiro import registrar_rotas as registrar_financeiro
from routes.tabela_precos import registrar_rotas as registrar_tabela_precos
from routes.pdf import registrar_rotas as registrar_pdf
from routes.excel import registrar_rotas as registrar_excel
from routes.usuarios import registrar_rotas as registrar_usuarios
from routes.relatorios import registrar_rotas as registrar_relatorios
from database.migrations import executar_migrations

app = Flask(__name__)

criar_banco()
executar_migrations()

registrar_credenciadas(app)
registrar_empresas(app)
registrar_exames(app)
registrar_atendimentos(app)
registrar_financeiro(app)
registrar_tabela_precos(app)
registrar_pdf(app)
registrar_excel(app)
registrar_usuarios(app)
registrar_relatorios(app)

@app.route("/")
def login():
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("SELECT COUNT(*) AS total FROM atendimentos")
    total_atendimentos = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM credenciadas")
    total_credenciadas = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM empresas")
    total_empresas = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM exames")
    total_exames = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT
            a.data_atendimento,
            c.nome AS credenciada,
            e.nome AS empresa,
            a.colaborador,
            a.tipo_atendimento
        FROM atendimentos a
        JOIN credenciadas c
            ON c.id = a.credenciada_id
        JOIN empresas e
            ON e.id = a.empresa_id
        ORDER BY a.id DESC
        LIMIT 10
    """)

    ultimos_atendimentos = cursor.fetchall()

    conexao.close()

    return render_template(
        "dashboard.html",
        total_atendimentos=total_atendimentos,
        total_credenciadas=total_credenciadas,
        total_empresas=total_empresas,
        total_exames=total_exames,
        ultimos_atendimentos=ultimos_atendimentos
    )





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
