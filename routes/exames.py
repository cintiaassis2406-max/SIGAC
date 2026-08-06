from flask import render_template, request, redirect
from database.database import conectar


def registrar_rotas(app):

    @app.route("/exames", methods=["GET", "POST"])
    def exames():

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
                INSERT INTO exames
                (
                    nome,
                    valor,
                    situacao
                )
                VALUES (%s, %s, %s)
            """, (
                nome,
                valor,
                situacao
            ))


            conexao.commit()

            conexao.close()

            return redirect("/exames")


        pesquisa = request.args.get("pesquisa", "")


        if pesquisa:

            cursor.execute("""
                SELECT *
                FROM exames
                WHERE nome LIKE %s
                ORDER BY nome
            """, (
                f"%{pesquisa}%",
            ))

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
                    nome=%s,
                    valor=%s,
                    situacao=%s
                WHERE id=%s
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
            WHERE id=%s
        """, (
            id,
        ))


        exame = cursor.fetchone()


        conexao.close()


        return render_template(
            "editar_exame.html",
            exame=exame
        )



    @app.route("/excluir_exame/<int:id>")
    def excluir_exame(id):

        conexao = conectar()
        cursor = conexao.cursor()


        cursor.execute("""
            SELECT COUNT(*)
            FROM atendimento_exames
            WHERE exame_id=%s
        """, (
            id,
        ))


        total = cursor.fetchone()["count"]


        if total > 0:

            conexao.close()

            return """
            <script>
                alert('Não é possível excluir. Este exame já foi utilizado em atendimentos.');
                window.location='/exames';
            </script>
            """



        cursor.execute("""
            DELETE FROM exames
            WHERE id=%s
        """, (
            id,
        ))


        conexao.commit()

        conexao.close()


        return redirect("/exames")



    @app.route("/alterar_situacao_exame/<int:id>")
    def alterar_situacao_exame(id):

        conexao = conectar()
        cursor = conexao.cursor()


        cursor.execute("""
            SELECT situacao
            FROM exames
            WHERE id=%s
        """, (
            id,
        ))


        exame = cursor.fetchone()


        if exame:

            if exame["situacao"] == "Ativo":

                nova_situacao = "Inativo"

            else:

                nova_situacao = "Ativo"



            cursor.execute("""
                UPDATE exames
                SET situacao=%s
                WHERE id=%s
            """, (
                nova_situacao,
                id
            ))


            conexao.commit()


        conexao.close()


        return redirect("/exames")