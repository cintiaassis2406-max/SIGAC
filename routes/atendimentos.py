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
            VALUES (%s, %s)
        """, (
            credenciada_id,
            nome
        ))

        conexao.commit()

        cursor.execute("SELECT LASTVAL() AS id")
        novo_id = cursor.fetchone()["id"]

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
            VALUES (%s, %s, %s)
        """, (
            nome,
            valor,
            situacao
        ))

        conexao.commit()

        cursor.execute("SELECT LASTVAL() AS id")
        novo_id = cursor.fetchone()["id"]

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
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                data_atendimento,
                credenciada_id,
                empresa_id,
                colaborador,
                tipo_atendimento,
                situacao_financeira,
                observacoes
            ))


            cursor.execute("SELECT LASTVAL() AS id")
            atendimento_id = cursor.fetchone()["id"]


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
                    WHERE id = %s
                """, (
                    exame_id,
                ))

                exame = cursor.fetchone()


                cursor.execute("""
                    SELECT valor
                    FROM precos_credenciada
                    WHERE credenciada_id = %s
                    AND exame_id = %s
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
                    VALUES (%s, %s, %s, %s)
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
    ).strip()

    data_pesquisa = request.args.get(
        "data_pesquisa",
        ""
    ).strip()

    pagina = request.args.get(
        "pagina",
        1,
        type=int
    )

    if pagina < 1:
        pagina = 1

    por_pagina = 10

    offset = (pagina - 1) * por_pagina

    # ==================================================
    # CONTAR ATENDIMENTOS
    # ==================================================

    filtros = []
    parametros = []

    if pesquisa:

        filtros.append("""
            (
                a.colaborador ILIKE %s
                OR e.nome ILIKE %s
                OR c.nome ILIKE %s
            )
        """)

        termo = f"%{pesquisa}%"

        parametros.extend([
            termo,
            termo,
            termo
        ])

    if data_pesquisa:

        filtros.append("""
            a.data_atendimento = %s
        """)

        parametros.append(data_pesquisa)

    where = ""

    if filtros:

        where = "WHERE " + " AND ".join(filtros)

    cursor.execute(f"""
        SELECT
            COUNT(*) AS total

        FROM atendimentos a

        INNER JOIN credenciadas c
            ON c.id = a.credenciada_id

        INNER JOIN empresas e
            ON e.id = a.empresa_id

        {where}
    """, parametros)

    total = cursor.fetchone()["total"]

    total_paginas = (total + por_pagina - 1) // por_pagina

    # ==================================================
    # LISTAR ATENDIMENTOS
    # ==================================================

    cursor.execute(f"""
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

        {where}

        ORDER BY a.id DESC

        LIMIT %s
        OFFSET %s
    """, parametros + [
        por_pagina,
        offset
    ])

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
            data_pesquisa=data_pesquisa,
            pagina=pagina,
            total=total,
            total_paginas=total_paginas,
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

            WHERE credenciada_id = %s

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
            colaborador = request.form["colaborador"].strip()
            tipo_atendimento = request.form["tipo_atendimento"]

            situacao_financeira = request.form.get(
                "situacao_financeira",
                "FATURAR"
            )

            observacoes = request.form.get(
                "observacoes",
                ""
            )

            cursor.execute("""
                UPDATE atendimentos
                SET
                    data_atendimento = %s,
                    credenciada_id = %s,
                    empresa_id = %s,
                    colaborador = %s,
                    tipo_atendimento = %s,
                    situacao_financeira = %s,
                    observacoes = %s
                WHERE id = %s
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

            cursor.execute("""
                DELETE FROM atendimento_exames
                WHERE atendimento_id = %s
            """, (id,))

            exames = request.form.getlist("exames")

            for exame_id in exames:

                cursor.execute("""
                    SELECT
                        nome,
                        valor
                    FROM exames
                    WHERE id = %s
                """, (exame_id,))

                exame = cursor.fetchone()

                if not exame:
                    continue

                cursor.execute("""
                    SELECT valor
                    FROM precos_credenciada
                    WHERE credenciada_id = %s
                    AND exame_id = %s
                """, (
                    credenciada_id,
                    exame_id
                ))

                preco = cursor.fetchone()

                if preco:
                    valor = preco["valor"]
                else:
                    valor = exame["valor"]

                cursor.execute("""
                    INSERT INTO atendimento_exames
                    (
                        atendimento_id,
                        exame_id,
                        nome_exame,
                        valor_exame
                    )
                    VALUES (%s, %s, %s, %s)
                """, (
                    id,
                    exame_id,
                    exame["nome"],
                    valor
                ))

                conexao.commit()
                return redirect("/atendimentos")
            
        cursor.execute("""
            SELECT *
            FROM atendimentos
            WHERE id = %s
        """, (id,))

        atendimento = cursor.fetchone()

        if not atendimento:
            conexao.close()
            return redirect("/atendimentos")

        cursor.execute("""
            SELECT exame_id
            FROM atendimento_exames
            WHERE atendimento_id = %s
        """, (id,))

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
                nome,
                valor
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

            WHERE atendimento_id = %s

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

            WHERE atendimento_id = %s

        """, (
            id,
        ))



        cursor.execute("""
            DELETE FROM atendimentos

            WHERE id = %s

        """, (
            id,
        ))



        conexao.commit()

        conexao.close()


        return redirect(
            "/atendimentos"
        )
