from flask import render_template, request, redirect, jsonify
from database.database import conectar
from datetime import date


def registrar_rotas(app):

    @app.route("/atendimentos", methods=["GET", "POST"])
    def atendimentos():

        conexao = conectar()
        cursor = conexao.cursor()

        if request.method == "POST":

            data_atendimento = request.form["data_atendimento"]
            credenciada_id = request.form["credenciada"]
            empresa_id = request.form["empresa"]
            colaborador = request.form["colaborador"]
            tipo_atendimento = request.form["tipo_atendimento"]
            observacoes = request.form.get("observacoes", "")
            exames = request.form.getlist("exames")

            cursor.execute("""
                INSERT INTO atendimentos
                (
                    data_atendimento,
                    credenciada_id,
                    empresa_id,
                    colaborador,
                    tipo_atendimento,
                    observacoes
                )
                VALUES (?,?,?,?,?,?)
            """, (
                data_atendimento,
                credenciada_id,
                empresa_id,
                colaborador,
                tipo_atendimento,
                observacoes
            ))

            atendimento_id = cursor.lastrowid

            for exame_id in exames:

                cursor.execute("""
                    SELECT
                        e.nome,
                        COALESCE(pc.valor, e.valor) AS valor
                    FROM exames e

                    LEFT JOIN precos_credenciada pc
                        ON pc.exame_id = e.id
                       AND pc.credenciada_id = ?

                    WHERE e.id = ?
                """, (
                    credenciada_id,
                    exame_id
                ))

                exame = cursor.fetchone()

                if exame:

                    cursor.execute("""
                        INSERT INTO atendimento_exames
                        (
                            atendimento_id,
                            exame_id,
                            nome_exame,
                            valor_exame
                        )
                        VALUES (?, ?, ?, ?)
                    """, (
                        atendimento_id,
                        exame_id,
                        exame["nome"],
                        exame["valor"]
                    ))

            conexao.commit()
            conexao.close()

            return redirect("/atendimentos")

        cursor.execute("SELECT * FROM credenciadas ORDER BY nome")
        credenciadas = cursor.fetchall()

        cursor.execute("SELECT * FROM empresas ORDER BY nome")
        empresas = cursor.fetchall()

        cursor.execute("""
            SELECT *
            FROM exames
            WHERE situacao='Ativo'
            ORDER BY nome
        """)

        exames = cursor.fetchall()

        # ==========================
        # PESQUISA DE ATENDIMENTOS
        # ==========================

        pesquisa = request.args.get("pesquisa", "")

        sql = """
            SELECT
                a.id,
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
        """

        parametros = []

        if pesquisa:

            sql += """
                WHERE
                    a.colaborador LIKE ?
                    OR e.nome LIKE ?
                    OR c.nome LIKE ?
            """

            termo = f"%{pesquisa}%"

            parametros.extend([
                termo,
                termo,
                termo
            ])

        sql += """
            ORDER BY
                a.data_atendimento DESC,
                a.id DESC
        """

        cursor.execute(sql, parametros)

        lista_atendimentos = cursor.fetchall()

        conexao.close()

        return render_template(
            "atendimentos.html",
            data_hoje=date.today().strftime("%Y-%m-%d"),
            credenciadas=credenciadas,
            empresas=empresas,
            exames=exames,
            atendimentos=lista_atendimentos,
            pesquisa=pesquisa
        )


    @app.route("/excluir_atendimento/<int:id>")
    def excluir_atendimento(id):

        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute(
            "DELETE FROM atendimento_exames WHERE atendimento_id=?",
            (id,)
        )

        cursor.execute(
            "DELETE FROM atendimentos WHERE id=?",
            (id,)
        )

        conexao.commit()
        conexao.close()

        return redirect("/atendimentos")


    @app.route("/nova_credenciada", methods=["POST"])
    def nova_credenciada():

        conexao = conectar()
        cursor = conexao.cursor()

        nome = request.form["nome"].strip()
        tipo = request.form["tipo_cobranca"]

        cursor.execute(
            "INSERT INTO credenciadas (nome, tipo_cobranca) VALUES (?, ?)",
            (nome, tipo)
        )

        conexao.commit()

        novo_id = cursor.lastrowid

        conexao.close()

        return jsonify({
            "id": novo_id,
            "nome": nome
        })
    
    @app.route("/nova_empresa", methods=["POST"])
    def nova_empresa():

        conexao = conectar()
        cursor = conexao.cursor()

        nome = request.form["nome"].strip()
        credenciada_id = request.form["credenciada_id"]

        cursor.execute("""
            INSERT INTO empresas
            (
                credenciada_id,
                nome
            )
            VALUES (?,?)
        """, (
            credenciada_id,
            nome
        ))

        conexao.commit()

        novo_id = cursor.lastrowid

        conexao.close()

        return jsonify({
            "id": novo_id,
            "nome": nome,
            "credenciada_id": credenciada_id
        })


    @app.route("/novo_exame", methods=["POST"])
    def novo_exame():

        conexao = conectar()
        cursor = conexao.cursor()

        nome = request.form["nome"].strip()
        valor = request.form["valor"]
        situacao = request.form["situacao"]

        cursor.execute("""
            INSERT INTO exames
            (
                nome,
                valor,
                situacao
            )
            VALUES (?,?,?)
        """, (
            nome,
            valor,
            situacao
        ))

        conexao.commit()

        novo_id = cursor.lastrowid

        conexao.close()

        return jsonify({
            "id": novo_id,
            "nome": nome
        })


    @app.route("/editar_atendimento/<int:id>", methods=["GET", "POST"])
    def editar_atendimento(id):

        conexao = conectar()
        cursor = conexao.cursor()

        if request.method == "POST":

            data_atendimento = request.form["data_atendimento"]
            credenciada_id = request.form["credenciada"]
            empresa_id = request.form["empresa"]
            colaborador = request.form["colaborador"]
            tipo_atendimento = request.form["tipo_atendimento"]

            cursor.execute("""
                UPDATE atendimentos
                SET
                    data_atendimento = ?,
                    credenciada_id = ?,
                    empresa_id = ?,
                    colaborador = ?,
                    tipo_atendimento = ?
                WHERE id = ?
            """, (
                data_atendimento,
                credenciada_id,
                empresa_id,
                colaborador,
                tipo_atendimento,
                id
            ))

            conexao.commit()
            conexao.close()

            return redirect("/atendimentos")
        
        cursor.execute("""
            SELECT
                a.*,
                c.nome AS credenciada,
                e.nome AS empresa
            FROM atendimentos a
            JOIN credenciadas c
                ON c.id = a.credenciada_id
            JOIN empresas e
                ON e.id = a.empresa_id
            WHERE a.id = ?
        """, (id,))

        atendimento = cursor.fetchone()

        cursor.execute("""
            SELECT *
            FROM credenciadas
            ORDER BY nome
        """)

        credenciadas = cursor.fetchall()

        cursor.execute("""
            SELECT *
            FROM empresas
            ORDER BY nome
        """)

        empresas = cursor.fetchall()

        conexao.close()

        return render_template(
            "editar_atendimento.html",
            atendimento=atendimento,
            credenciadas=credenciadas,
            empresas=empresas
        )