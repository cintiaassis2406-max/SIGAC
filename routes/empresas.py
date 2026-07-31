from flask import render_template, request, redirect
from database.database import conectar


def registrar_rotas(app):

    @app.route("/empresas", methods=["GET", "POST"])
    def empresas():

        conexao = conectar()
        cursor = conexao.cursor()

        if request.method == "POST":

            credenciada_id = request.form["credenciada_id"]
            nome = request.form["nome"]

            cursor.execute("""
                SELECT id
                FROM empresas
                WHERE credenciada_id = ?
                  AND UPPER(nome) = UPPER(?)
            """, (credenciada_id, nome))

            if cursor.fetchone():

                conexao.close()

                return """
                <script>
                    alert('Esta empresa já está cadastrada para esta credenciada!');
                    window.location='/empresas';
                </script>
                """

            cursor.execute("""
                INSERT INTO empresas
                (
                    credenciada_id,
                    nome
                )
                VALUES (?, ?)
            """, (
                credenciada_id,
                nome
            ))

            conexao.commit()

            return redirect("/empresas")

        # ==========================
        # PESQUISA
        # ==========================

        pesquisa = request.args.get("pesquisa", "")

        sql = """
            SELECT
                empresas.id,
                empresas.nome,
                empresas.credenciada_id,
                credenciadas.nome AS credenciada
            FROM empresas
            INNER JOIN credenciadas
                ON empresas.credenciada_id = credenciadas.id
        """

        parametros = []

        if pesquisa:

            sql += """
                WHERE empresas.nome LIKE ?
            """

            parametros.append(f"%{pesquisa}%")

        sql += """
            ORDER BY empresas.nome
        """

        cursor.execute(sql, parametros)

        empresas = cursor.fetchall()

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
            "empresas.html",
            empresas=empresas,
            credenciadas=credenciadas,
            pesquisa=pesquisa
        )
    
    @app.route("/editar_empresa/<int:id>", methods=["GET", "POST"])
    def editar_empresa(id):

        conexao = conectar()
        cursor = conexao.cursor()

        if request.method == "POST":

            cursor.execute("""
                UPDATE empresas
                SET
                    credenciada_id = ?,
                    nome = ?
                WHERE id = ?
            """, (
                request.form["credenciada_id"],
                request.form["nome"],
                id
            ))

            conexao.commit()
            conexao.close()

            return redirect("/empresas")

        cursor.execute("""
            SELECT *
            FROM empresas
            WHERE id = ?
        """, (id,))

        empresa = cursor.fetchone()

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
            "editar_empresa.html",
            empresa=empresa,
            credenciadas=credenciadas
        )


    @app.route("/excluir_empresa/<int:id>")
    def excluir_empresa(id):

        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute("""
            DELETE
            FROM empresas
            WHERE id = ?
        """, (id,))

        conexao.commit()
        conexao.close()

        return redirect("/empresas")
    
