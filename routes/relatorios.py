from flask import render_template
from database.database import conectar


def registrar_rotas(app):

    @app.route("/relatorios")
    def relatorios():

        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT
                id,
                nome
            FROM credenciadas
            ORDER BY nome
        """)

        credenciadas = cursor.fetchall()

        conexao.close()

        return render_template(
            "relatorios.html",
            credenciadas=credenciadas
        )