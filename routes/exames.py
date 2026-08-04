from flask import render_template, request, redirect, jsonify
from database.database import conectar


def registrar_rotas(app):

    @app.route("/exames", methods=["GET", "POST"])
    def exames():

        conexao = conectar()
        cursor = conexao.cursor()

        # ==========================
        # SALVAR EXAME
        # ==========================

        if request.method == "POST":

            nome = request.form["nome"].strip()

            valor = request.form.get(
                "valor",
                "0"
            )

            valor = valor.replace(",", ".")

            situacao = request.form["situacao"]

            cursor.execute("""
                INSERT INTO exames
                (
                    nome,
                    valor,
                    situacao
                )
                VALUES (?, ?, ?)
            """, (
                nome,
                valor,
                situacao
            ))

            conexao.commit()

            return redirect("/exames")

        # ==========================
        # PESQUISA
        # ==========================

        pesquisa = request.args.get("pesquisa", "")

        if pesquisa:

            cursor.execute("""
                SELECT *
                FROM exames
                WHERE nome LIKE ?
                ORDER BY nome
            """, (f"%{pesquisa}%",))

        else:

            cursor.execute("""
                SELECT *
                FROM exames
                ORDER BY nome
            """)

        lista = cursor.fetchall()

        conexao.close()

        return render_template(
            "exames.html",
            exames=lista,
            pesquisa=pesquisa
        )
        # ==================================================
    # EDITAR EXAME
    # ==================================================

    @app.route("/editar_exame/<int:id>", methods=["GET", "POST"])
    def editar_exame(id):

        conexao = conectar()
        cursor = conexao.cursor()

        if request.method == "POST":

            nome = request.form["nome"].strip()

            valor = request.form.get(
                "valor",
                "0"
            )

            valor = valor.replace(",", ".")

            situacao = request.form["situacao"]

            cursor.execute("""
                UPDATE exames
                SET
                    nome = ?,
                    valor = ?,
                    situacao = ?
                WHERE id = ?
            """, (
                nome,
                valor,
                situacao,
                id
            ))

            conexao.commit()

            conexao.close()

            return redirect("/exames")

        cursor.execute("""
            SELECT *
            FROM exames
            WHERE id = ?
        """, (id,))

        exame = cursor.fetchone()

        conexao.close()

        return render_template(
            "editar_exame.html",
            exame=exame
        )
        # ==================================================
    # EXCLUIR EXAME
    # ==================================================

    @app.route("/excluir_exame/<int:id>")
    def excluir_exame(id):

        conexao = conectar()
        cursor = conexao.cursor()

        # Verifica se o exame já foi utilizado
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM atendimento_exames
            WHERE exame_id = ?
        """, (id,))

        total = cursor.fetchone()["total"]

        if total == 0:

            cursor.execute("""
                DELETE FROM exames
                WHERE id = ?
            """, (id,))

            conexao.commit()

        conexao.close()

        return redirect("/exames")
        # ==================================================
    # ALTERAR SITUAÇÃO
    # ==================================================

    @app.route("/alterar_situacao_exame/<int:id>")
    def alterar_situacao_exame(id):

        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT situacao
            FROM exames
            WHERE id = ?
        """, (id,))

        exame = cursor.fetchone()

        if exame:

            if exame["situacao"] == "Ativo":
                nova_situacao = "Inativo"
            else:
                nova_situacao = "Ativo"

            cursor.execute("""
                UPDATE exames
                SET situacao = ?
                WHERE id = ?
            """, (
                nova_situacao,
                id
            ))

            conexao.commit()

        conexao.close()

        return redirect("/exames")
