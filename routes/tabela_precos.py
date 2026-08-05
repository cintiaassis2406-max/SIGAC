from flask import render_template, request
from database.database import conectar


def registrar_rotas(app):

    @app.route("/tabela_precos", methods=["GET", "POST"])
    def tabela_precos():

        conexao = conectar()
        cursor = conexao.cursor()

        # ==========================
        # SALVAR PREÇOS
        # ==========================

        if request.method == "POST":

            credenciada_id = request.form["credenciada_id"]

            cursor.execute("""
                DELETE FROM precos_credenciada
                WHERE credenciada_id = %s
            """, (credenciada_id,))

            for campo in request.form:

                if campo.startswith("valor_"):

                    exame_id = campo.replace("valor_", "")
                    valor = request.form[campo]

                    if valor != "":

                        cursor.execute("""
                            INSERT INTO precos_credenciada
                            (
                                credenciada_id,
                                exame_id,
                                valor
                            )
                            VALUES (%s, %s, %s)
                        """, (
                            credenciada_id,
                            exame_id,
                            valor
                        ))

            conexao.commit()

        # ==========================
        # CONSULTA
        # ==========================

        if request.method == "POST":
            credenciada_id = request.form["credenciada_id"]
            pesquisa = request.form.get("pesquisa", "")
        else:
            credenciada_id = request.args.get("credenciada", "")
            pesquisa = request.args.get("pesquisa", "")

        cursor.execute("""
            SELECT id, nome
            FROM credenciadas
            ORDER BY nome
        """)

        credenciadas = cursor.fetchall()

        exames = []

        if credenciada_id:

            sql = """
                SELECT
                    e.id,
                    e.nome,
                    COALESCE(pc.valor, e.valor, 0) AS valor
                FROM exames e

                LEFT JOIN precos_credenciada pc
                    ON pc.exame_id = e.id
                   AND pc.credenciada_id = %s

                WHERE e.situacao = 'Ativo'
            """

            parametros = [credenciada_id]

            if pesquisa:

                sql += """
                    AND e.nome ILIKE %s
                """

                parametros.append(f"%{pesquisa}%")

            sql += """
                ORDER BY e.nome
            """

            cursor.execute(sql, parametros)

            exames = cursor.fetchall()

        conexao.close()

        return render_template(
            "tabela_precos.html",
            credenciadas=credenciadas,
            exames=exames,
            credenciada_id=credenciada_id,
            pesquisa=pesquisa
        )