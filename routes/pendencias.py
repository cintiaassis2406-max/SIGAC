from flask import render_template, session, redirect
from database.database import conectar


def registrar_rotas(app):

    @app.route("/pendencias")
    def pendencias():

        if "usuario" not in session:
            return redirect("/")

        conexao = conectar()
        cursor = conexao.cursor()

        lista_pendencias = []


        # Atendimento sem exame informado

        cursor.execute("""
            SELECT
                a.id,
                a.colaborador,
                a.data_atendimento
            FROM atendimentos a
            LEFT JOIN atendimento_exames ae
                ON ae.atendimento_id = a.id
            WHERE ae.id IS NULL
        """)

        for item in cursor.fetchall():

            lista_pendencias.append({
                "tipo": "Atendimento sem exame informado",
                "descricao": f"Atendimento de {item['colaborador']} sem exame informado",
                "data": item["data_atendimento"]
            })


        # Atendimento sem empresa vinculada

        cursor.execute("""
            SELECT
                id,
                colaborador,
                data_atendimento
            FROM atendimentos
            WHERE empresa_id IS NULL
        """)

        for item in cursor.fetchall():

            lista_pendencias.append({
                "tipo": "Atendimento sem empresa vinculada",
                "descricao": f"Atendimento de {item['colaborador']} sem empresa cadastrada",
                "data": item["data_atendimento"]
            })


        # Atendimento sem credenciada vinculada

        cursor.execute("""
            SELECT
                id,
                colaborador,
                data_atendimento
            FROM atendimentos
            WHERE credenciada_id IS NULL
        """)

        for item in cursor.fetchall():

            lista_pendencias.append({
                "tipo": "Atendimento sem credenciada vinculada",
                "descricao": f"Atendimento de {item['colaborador']} sem credenciada cadastrada",
                "data": item["data_atendimento"]
            })


        # Informações faltando sobre a credenciada

        cursor.execute("""
            SELECT
                id,
                nome
            FROM credenciadas
            WHERE email IS NULL OR email = ''
            OR telefone IS NULL OR telefone = ''
            OR contato IS NULL OR contato = ''
        """)

        credenciadas_pendentes = cursor.fetchall()

        print("CREDENCIADAS COM PENDENCIA:", credenciadas_pendentes)

        for item in credenciadas_pendentes:


            lista_pendencias.append({
                "tipo": "Informações faltando sobre a credenciada",
                "descricao": f"Credenciada {item['nome']} com cadastro incompleto",
                "data": ""
            })


        conexao.close()


        print("TOTAL DE PENDENCIAS:", len(lista_pendencias))

        return render_template(
            "pendencias.html",
            pendencias=lista_pendencias
        )