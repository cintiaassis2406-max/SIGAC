from flask import send_file, request
from database.database import conectar

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

import tempfile


def registrar_rotas(app):

    @app.route("/gerar_pdf")
    def gerar_pdf():

        conexao = conectar()
        cursor = conexao.cursor()

        credenciada_id = request.args.get("credenciada")
        mes = request.args.get("mes")
        ano = request.args.get("ano")
        tipo = request.args.get("tipo")

        nome_credenciada = ""

        if credenciada_id:

            cursor.execute(
                """
                SELECT nome
                FROM credenciadas
                WHERE id = %s
                """,
                (credenciada_id,)
            )

            cred = cursor.fetchone()

            if cred:

                nome_credenciada = cred["nome"]


        sql = """
            SELECT
                a.colaborador,
                e.nome AS empresa,
                a.data_atendimento,
                a.tipo_atendimento,
                STRING_AGG(ae.nome_exame, ', ') AS exames,
                COALESCE(SUM(ae.valor_exame), 0) AS valor

            FROM atendimentos a

            INNER JOIN empresas e
                ON e.id = a.empresa_id

            LEFT JOIN atendimento_exames ae
                ON ae.atendimento_id = a.id

            WHERE 1=1
        """


        parametros = []


        if credenciada_id:

            sql += """
                AND a.credenciada_id=%s
            """

            parametros.append(
                credenciada_id
            )


        if mes:

            sql += """
                AND TO_CHAR(a.data_atendimento,'MM')=%s
            """

            parametros.append(
                f"{int(mes):02}"
            )


        if ano:

            sql += """
                AND TO_CHAR(a.data_atendimento,'YYYY')=%s
            """

            parametros.append(
                str(ano)
            )

        if tipo:

            sql += """
                AND a.tipo_atendimento = %s
            """

            parametros.append(tipo)

        sql += """
            GROUP BY
                a.id,
                e.nome

            ORDER BY
                a.colaborador
        """


        cursor.execute(
            sql,
            parametros
        )


        dados = cursor.fetchall()


        arquivo = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        )


        pdf = SimpleDocTemplate(
            arquivo.name,
            pagesize=(29.7 * cm, 21 * cm)
        )


        estilos = getSampleStyleSheet()

        elementos = []


        elementos.append(

    Paragraph(
        f"""
        <b>SIGAC - RELATÓRIO DE FATURAMENTO</b><br/>
        Credenciada: {nome_credenciada}<br/>
        Período: {mes}/{ano}<br/>
        """,
        estilos["Title"]
    )

)


        tabela = [

            [
                "Colaborador",
                "Empresa",
                "Data",
                "Tipo",
                "Exames",
                "Valor"
            ]

        ]


        total_geral = 0


        for item in dados:

            tabela.append(

                [

                    item["colaborador"],

                    item["empresa"],

                    str(item["data_atendimento"]),

                    item["tipo_atendimento"],

                    item["exames"] if item["exames"] else "",

                    f'R$ {item["valor"]:.2f}'

                ]

            )


            total_geral += item["valor"]



        tabela.append(

            [

                "",
                "",
                "",
                "",
                "TOTAL",
                f'R$ {total_geral:.2f}'

            ]

        )


        tabela_pdf = Table(
            tabela
        )


        tabela_pdf.setStyle(

            TableStyle(

                [

                    (
                        "GRID",
                        (0,0),
                        (-1,-1),
                        0.5,
                        colors.grey
                    ),

                    (
                        "BACKGROUND",
                        (0,0),
                        (-1,0),
                        colors.lightgrey
                    ),

                    (
                        "FONTNAME",
                        (0,0),
                        (-1,0),
                        "Helvetica-Bold"
                    )

                ]

            )

        )


        elementos.append(
            tabela_pdf
        )


        pdf.build(
            elementos
        )


        conexao.close()


        return send_file(

            arquivo.name,

            as_attachment=True,

            download_name="Relatorio_Faturamento.pdf",

            mimetype="application/pdf"

        )