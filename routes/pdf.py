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

        sql = """

        SELECT

            a.colaborador,

            e.nome AS empresa,

            a.data_atendimento,

            a.tipo_atendimento,

            GROUP_CONCAT(ae.nome_exame, ', ') AS exames,

            COALESCE(SUM(ae.valor_exame),0) AS valor

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
                AND a.credenciada_id=?
            """

            parametros.append(credenciada_id)

        if mes:

            sql += """
                AND strftime('%m',a.data_atendimento)=?
            """

            parametros.append(f"{int(mes):02}")

        if ano:

            sql += """
                AND strftime('%Y',a.data_atendimento)=?
            """

            parametros.append(str(ano))

        sql += """

        GROUP BY

            a.id

        ORDER BY

            a.colaborador

        """

        cursor.execute(sql, parametros)

        dados = cursor.fetchall()

        arquivo = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        )

        pdf = SimpleDocTemplate(
            arquivo.name,
            pagesize=(29.7*cm,21*cm)
        )

        estilos = getSampleStyleSheet()

        elementos = []

        elementos.append(

            Paragraph(
                "<b>SIGAC - RELATÓRIO DE FATURAMENTO</b>",
                estilos["Title"]
            )

        )

        elementos.append(
            Paragraph(
                "<br/>",
                estilos["Normal"]
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

            tabela.append([

                item["colaborador"],

                item["empresa"],

                item["data_atendimento"],

                item["tipo_atendimento"],

                item["exames"] if item["exames"] else "",

                f'R$ {item["valor"]:.2f}'

            ])

            total_geral += item["valor"]

        tabela.append([

            "",

            "",

            "",

            "",

            "TOTAL",

            f'R$ {total_geral:.2f}'

        ])

        tabela_pdf = Table(tabela)

        tabela_pdf.setStyle(

            TableStyle([

                ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0d6efd")),

                ("TEXTCOLOR", (0,0), (-1,0), colors.white),

                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),

                ("GRID", (0,0), (-1,-1), 0.5, colors.grey),

                ("BACKGROUND", (0,1), (-1,-2), colors.beige),

                ("BACKGROUND", (0,-1), (-1,-1), colors.lightgrey),

                ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),

                ("ALIGN", (5,1), (5,-1), "RIGHT"),

                ("BOTTOMPADDING", (0,0), (-1,0), 10)

            ])

        )

        elementos.append(tabela_pdf)

        pdf.build(elementos)

        conexao.close()

        return send_file(

            arquivo.name,

            as_attachment=True,

            download_name="Relatorio_Faturamento.pdf",

            mimetype="application/pdf"

        )