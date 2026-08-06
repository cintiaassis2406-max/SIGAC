from flask import render_template, request, redirect, jsonify
from database.database import conectar


def registrar_rotas(app):

    @app.route("/credenciadas", methods=["GET", "POST"])
    def credenciadas():

        conexao = conectar()
        cursor = conexao.cursor()

        if request.method == "POST":

            nome = request.form["nome"]

            cursor.execute(
                "SELECT id FROM credenciadas WHERE UPPER(nome)=UPPER(%s)",
                (nome,)
            )

            if cursor.fetchone():

                conexao.close()

                return """
                <script>
                    alert('Esta credenciada já está cadastrada!');
                    window.location='/credenciadas';
                </script>
                """


            email = request.form["email"]
            telefone = request.form["telefone"]
            contato = request.form["contato"]
            observacoes = request.form["observacoes"]
            observacoes_internas = request.form["observacoes_internas"]


            cursor.execute("""
                INSERT INTO credenciadas
                (
                    nome,
                    email,
                    telefone,
                    contato,
                    observacoes,
                    observacoes_internas,
                    situacao_financeira
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (
                nome,
                email,
                telefone,
                contato,
                observacoes,
                observacoes_internas,
                None
            ))


            conexao.commit()

            return redirect("/credenciadas")


        pesquisa = request.args.get("pesquisa", "")


        if pesquisa:

            cursor.execute("""
                SELECT *
                FROM credenciadas
                WHERE nome LIKE %s
                ORDER BY nome
            """, (
                f"%{pesquisa}%",
            ))

        else:

            cursor.execute("""
                SELECT *
                FROM credenciadas
                ORDER BY nome
            """)


        lista = cursor.fetchall()

        conexao.close()


        return render_template(
            "credenciadas.html",
            credenciadas=lista,
            pesquisa=pesquisa
        )



    @app.route("/nova_credenciada", methods=["POST"])
    def nova_credenciada():

        conexao = conectar()
        cursor = conexao.cursor()


        nome = request.form.get("nome")


        if not nome:

            conexao.close()

            return jsonify({
                "erro": "Informe o nome."
            }), 400



        cursor.execute("""
            SELECT id
            FROM credenciadas
            WHERE UPPER(nome)=UPPER(%s)
        """, (
            nome,
        ))


        existente = cursor.fetchone()


        if existente:

            conexao.close()

            return jsonify({
                "id": existente["id"],
                "nome": nome
            })



        cursor.execute("""
            INSERT INTO credenciadas
            (
                nome,
                email,
                telefone,
                contato,
                observacoes,
                observacoes_internas,
                situacao_financeira
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            nome,
            "",
            "",
            "",
            "",
            "",
            None
        ))


        conexao.commit()


        cursor.execute("""
            SELECT id
            FROM credenciadas
            WHERE nome=%s
            ORDER BY id DESC
            LIMIT 1
        """, (
            nome,
        ))


        novo_id = cursor.fetchone()["id"]


        conexao.close()


        return jsonify({
            "id": novo_id,
            "nome": nome
        })



    @app.route("/excluir_credenciada/<int:id>")
    def excluir_credenciada(id):

        conexao = conectar()
        cursor = conexao.cursor()


        cursor.execute(
            "DELETE FROM credenciadas WHERE id=%s",
            (id,)
        )


        conexao.commit()

        conexao.close()


        return redirect("/credenciadas")



    @app.route("/editar_credenciada/<int:id>", methods=["GET", "POST"])
    def editar_credenciada(id):

        conexao = conectar()
        cursor = conexao.cursor()


        if request.method == "POST":

            cursor.execute("""
                UPDATE credenciadas
                SET
                    nome=%s,
                    email=%s,
                    telefone=%s,
                    contato=%s,
                    observacoes=%s,
                    observacoes_internas=%s,
                    situacao_financeira=%s
                WHERE id=%s
            """, (
                request.form["nome"],
                request.form["email"],
                request.form["telefone"],
                request.form["contato"],
                request.form["observacoes"],
                request.form["observacoes_internas"],
                request.form["situacao_financeira"],
                id
            ))


            conexao.commit()

            conexao.close()


            return redirect("/credenciadas")



        cursor.execute(
            "SELECT * FROM credenciadas WHERE id=%s",
            (id,)
        )


        credenciada = cursor.fetchone()


        conexao.close()


        return render_template(
            "editar_credenciada.html",
            credenciada=credenciada
        )