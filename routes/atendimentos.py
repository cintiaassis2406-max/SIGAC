from flask import render_template, request, redirect, jsonify
from database.database import conectar
from datetime import date


def registrar_rotas(app):

    # ==================================================
    # NOVA EMPRESA (AJAX)
    # ==================================================

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
            VALUES (?, ?)
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


    # ==================================================
    # NOVO EXAME (AJAX)
    # ==================================================

    @app.route("/novo_exame", methods=["POST"])
    def novo_exame():

        conexao = conectar()
        cursor = conexao.cursor()

        nome = request.form["nome"].strip()
        valor = request.form.get(
            "valor",
            "0"
        )

        valor = valor.replace(",", ".")

        situacao = request.form.get(
            "situacao",
            "Ativo"
        )

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

        novo_id = cursor.lastrowid

        conexao.close()

        return jsonify({
            "id": novo_id,
            "nome": nome
        })


    # ==================================================
    # LISTAR / CADASTRAR ATENDIMENTOS
    # ==================================================

    @app.route("/atendimentos", methods=["GET", "POST"])
    def atendimentos():

        conexao = conectar()
        cursor = conexao.cursor()


        if request.method == "POST":

            data_atendimento = request.form["data_atendimento"]

            credenciada_id = request.form["credenciada"]

            empresa_id = request.form["empresa"]

            colaborador = request.form["colaborador"].strip()

            tipo_atendimento = request.form["tipo_atendimento"]

            situacao_financeira = request.form[
                "situacao_financeira"
            ]

            observacoes = request.form.get(
                "observacoes",
                ""
            )


            cursor.execute("""
                INSERT INTO atendimentos
                (
                    data_atendimento,
                    credenciada_id,
                    empresa_id,
                    colaborador,
                    tipo_atendimento,
                    situacao_financeira,
                    observacoes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                data_atendimento,
                credenciada_id,
                empresa_id,
                colaborador,
                tipo_atendimento,
                situacao_financeira,
                observacoes
            ))


            atendimento_id = cursor.lastrowid


            exames = request.form.getlist(
                "exames"
            )

            print("EXAMES RECEBIDOS:", exames)

            for exame_id in exames:

                cursor.execute("""
                    SELECT
                        nome,
                        valor
                    FROM exames
                    WHERE id = ?
                """, (
                    exame_id,
                ))

                exame = cursor.fetchone()


                cursor.execute("""
                    SELECT valor
                    FROM precos_credenciada
                    WHERE credenciada_id = ?
                    AND exame_id = ?
                """, (
                    credenciada_id,
                    exame_id
                ))

                preco = cursor.fetchone()

                if preco:

                    valor = preco["valor"]

                else:

                    valor = exame["valor"]

                print(
                    "Exame:",
                    exame["nome"],
                    "| Valor:",
                    valor
                )


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
                    valor
                ))


            conexao.commit()

            conexao.close()

            return redirect("/atendimentos")

        # ==================================================
        # FILTROS / LISTAGEM
        # ==================================================

        pesquisa = request.args.get(
            "pesquisa",
            ""
        )

        if pesquisa:

            cursor.execute("""
                SELECT
                    a.id,
                    a.data_atendimento,
                    c.nome AS credenciada,
                    e.nome AS empresa,
                    a.colaborador,
                    a.tipo_atendimento,
                    a.situacao_financeira

                FROM atendimentos a

                INNER JOIN credenciadas c
                    ON c.id = a.credenciada_id

                INNER JOIN empresas e
                    ON e.id = a.empresa_id

                WHERE a.colaborador LIKE ?

                ORDER BY a.colaborador
            """, (
                f"%{pesquisa}%",
            ))

        else:

            cursor.execute("""
                SELECT
                    a.id,
                    a.data_atendimento,
                    c.nome AS credenciada,
                    e.nome AS empresa,
                    a.colaborador,
                    a.tipo_atendimento,
                    a.situacao_financeira

                FROM atendimentos a

                INNER JOIN credenciadas c
                    ON c.id = a.credenciada_id

                INNER JOIN empresas e
                    ON e.id = a.empresa_id

                ORDER BY
                    a.colaborador
            """)


        lista = cursor.fetchall()


        # ==================================================
        # DADOS PARA CADASTRO
        # ==================================================

        cursor.execute("""
            SELECT
                id,
                nome

            FROM credenciadas

            ORDER BY nome
        """)

        credenciadas = cursor.fetchall()



        cursor.execute("""
            SELECT
                id,
                nome

            FROM exames

            WHERE situacao = 'Ativo'

            ORDER BY nome
        """)

        exames = cursor.fetchall()

        cursor.execute("""
            SELECT
                id,
                nome,
                credenciada_id
            FROM empresas
            ORDER BY nome
        """)

        empresas = cursor.fetchall()

        conexao.close()


        return render_template(
            "atendimentos.html",
            atendimentos=lista,
            credenciadas=credenciadas,
            empresas=empresas,
            exames=exames,
            pesquisa=pesquisa,
            data_hoje=date.today().strftime("%Y-%m-%d")
        )



    # ==================================================
    # BUSCAR EMPRESAS DA CREDENCIADA (AJAX)
    # ==================================================

    @app.route(
        "/buscar_empresas/<int:credenciada_id>"
    )
    def buscar_empresas(credenciada_id):

        conexao = conectar()
        cursor = conexao.cursor()


        cursor.execute("""
            SELECT
                id,
                nome

            FROM empresas

            WHERE credenciada_id = ?

            ORDER BY nome
        """, (
            credenciada_id,
        ))


        empresas = cursor.fetchall()


        conexao.close()


        return jsonify([
            {
                "id": empresa["id"],
                "nome": empresa["nome"]
            }

            for empresa in empresas
        ])
    # ==================================================
    # EDITAR ATENDIMENTO
    # ==================================================

    @app.route(
        "/editar_atendimento/<int:id>",
        methods=["GET", "POST"]
    )
    def editar_atendimento(id):

        conexao = conectar()
        cursor = conexao.cursor()


        if request.method == "POST":

            data_atendimento = request.form["data_atendimento"]

            credenciada_id = request.form["credenciada"]

            empresa_id = request.form["empresa"]

            colaborador = request.form["colaborador"]

            tipo_atendimento = request.form["tipo_atendimento"]

            situacao_financeira = request.form[
                "situacao_financeira"
            ]

            observacoes = request.form.get(
                "observacoes",
                ""
            )


            cursor.execute("""
                UPDATE atendimentos

                SET
                    data_atendimento = ?,
                    credenciada_id = ?,
                    empresa_id = ?,
                    colaborador = ?,
                    tipo_atendimento = ?,
                    situacao_financeira = ?,
                    observacoes = ?

                WHERE id = ?

            """, (
                data_atendimento,
                credenciada_id,
                empresa_id,
                colaborador,
                tipo_atendimento,
                situacao_financeira,
                observacoes,
                id
            ))


            # Remove exames antigos

            cursor.execute("""
                DELETE FROM atendimento_exames

                WHERE atendimento_id = ?

            """, (
                id,
            ))


            exames = request.form.getlist(
                "exames"
            )


            for exame_id in exames:

                cursor.execute("""
                    SELECT nome
                    FROM exames
                    WHERE id = ?
                """, (
                    exame_id,
                ))

                exame = cursor.fetchone()


                cursor.execute("""
                    SELECT valor
                    FROM precos_credenciada

                    WHERE credenciada_id = ?
                    AND exame_id = ?

                """, (
                    credenciada_id,
                    exame_id
                ))


                preco = cursor.fetchone()


                valor = 0

                if preco:

                    valor = preco["valor"]



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
                    id,
                    exame_id,
                    exame["nome"],
                    valor
                ))



            conexao.commit()

            conexao.close()


            return redirect(
                "/atendimentos"
            )



        # Buscar atendimento

        cursor.execute("""
            SELECT *

            FROM atendimentos

            WHERE id = ?

        """, (
            id,
        ))


        atendimento = cursor.fetchone()



        # Buscar exames selecionados

        cursor.execute("""
            SELECT exame_id

            FROM atendimento_exames

            WHERE atendimento_id = ?

        """, (
            id,
        ))


        exames_selecionados = [
            item["exame_id"]
            for item in cursor.fetchall()
        ]



        cursor.execute("""
            SELECT
                id,
                nome

            FROM credenciadas

            ORDER BY nome

        """)

        credenciadas = cursor.fetchall()



        cursor.execute("""
            SELECT
                id,
                nome

            FROM exames

            ORDER BY nome

        """)

        exames = cursor.fetchall()



        cursor.execute("""
            SELECT
                id,
                nome

            FROM empresas

            WHERE credenciada_id = ?

            ORDER BY nome

        """, (
            atendimento["credenciada_id"],
        ))

        empresas = cursor.fetchall()



        conexao.close()



        return render_template(
            "editar_atendimento.html",
            atendimento=atendimento,
            credenciadas=credenciadas,
            empresas=empresas,
            exames=exames,
            exames_selecionados=exames_selecionados
        )
    # ==================================================
    # VISUALIZAR EXAMES DO ATENDIMENTO
    # ==================================================

    @app.route(
        "/exames_atendimento/<int:id>"
    )
    def exames_atendimento(id):

        conexao = conectar()
        cursor = conexao.cursor()


        cursor.execute("""
            SELECT
                nome_exame,
                valor_exame

            FROM atendimento_exames

            WHERE atendimento_id = ?

            ORDER BY nome_exame

        """, (
            id,
        ))


        exames = cursor.fetchall()


        conexao.close()


        return jsonify([
            {
                "nome": exame["nome_exame"],
                "valor": exame["valor_exame"]
            }

            for exame in exames
        ])



    # ==================================================
    # EXCLUIR ATENDIMENTO
    # ==================================================

    @app.route(
        "/excluir_atendimento/<int:id>"
    )
    def excluir_atendimento(id):

        conexao = conectar()
        cursor = conexao.cursor()



        cursor.execute("""
            DELETE FROM atendimento_exames

            WHERE atendimento_id = ?

        """, (
            id,
        ))



        cursor.execute("""
            DELETE FROM atendimentos

            WHERE id = ?

        """, (
            id,
        ))



        conexao.commit()

        conexao.close()


        return redirect(
            "/atendimentos"
        )
