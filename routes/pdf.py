from flask import send_file, request
from database.database import conectar

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
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
                AND a.credenciada_id = %s
            """

            parametros.append(
                credenciada_id
            )


        if mes:

            sql += """
                AND TO_CHAR(
                    a.data_atendimento,
                    'MM'
                ) = %s
            """

            parametros.append(
                f"{int(mes):02}"
            )


        if ano:

            sql += """
                AND TO_CHAR(
                    a.data_atendimento,
                    'YYYY'
                ) = %s
            """

            parametros.append(
                str(ano)
            )


        if tipo:

            sql += """
                AND a.tipo_atendimento = %s
            """

            parametros.append(
                tipo
            )


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

            pagesize=(
                29.7 * cm,
                21 * cm
            ),

            rightMargin=0.7 * cm,
            leftMargin=0.7 * cm,
            topMargin=0.8 * cm,
            bottomMargin=0.8 * cm
        )


        estilos = getSampleStyleSheet()


        elementos = []


        estilo_titulo = ParagraphStyle(
            "TituloRelatorio",
            parent=estilos["Title"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=17,
            alignment=1,
            spaceAfter=10
        )


        estilo_celula = ParagraphStyle(
            "Celula",
            parent=estilos["Normal"],
            fontName="Helvetica",
            fontSize=6.5,
            leading=8,
            spaceAfter=0,
            spaceBefore=0,
            wordWrap="CJK"
        )


        estilo_cabecalho = ParagraphStyle(
            "Cabecalho",
            parent=estilos["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7,
            leading=8,
            alignment=1,
            spaceAfter=0,
            spaceBefore=0,
            wordWrap="CJK"
        )


        elementos.append(
            Paragraph(
                f"""
                SIGAC - RELATÓRIO DE FATURAMENTO<br/>
                Credenciada: {nome_credenciada}<br/>
                Período: {mes or ''}/{ano or ''}
                """,
                estilo_titulo
            )
        )


        tabela = [

            [
                Paragraph(
                    "Colaborador",
                    estilo_cabecalho
                ),

                Paragraph(
                    "Empresa",
                    estilo_cabecalho
                ),

                Paragraph(
                    "Data",
                    estilo_cabecalho
                ),

                Paragraph(
                    "Tipo",
                    estilo_cabecalho
                ),

                Paragraph(
                    "Exames",
                    estilo_cabecalho
                ),

                Paragraph(
                    "Valor",
                    estilo_cabecalho
                )
            ]

        ]


        total_geral = 0


        for item in dados:

            colaborador = (
                item["colaborador"]
                or ""
            )

            empresa = (
                item["empresa"]
                or ""
            )

            tipo_atendimento = (
                item["tipo_atendimento"]
                or ""
            )

            exames = (
                item["exames"]
                or ""
            )


            if hasattr(
                item["data_atendimento"],
                "strftime"
            ):

                data_atendimento = (
                    item["data_atendimento"]
                    .strftime("%d/%m/%Y")
                )

            else:

                data_atendimento = str(
                    item["data_atendimento"]
                )


            valor = item["valor"] or 0


            tabela.append(
                [

                    Paragraph(
                        str(colaborador),
                        estilo_celula
                    ),

                    Paragraph(
                        str(empresa),
                        estilo_celula
                    ),

                    Paragraph(
                        str(data_atendimento),
                        estilo_celula
                    ),

                    Paragraph(
                        str(tipo_atendimento),
                        estilo_celula
                    ),

                    Paragraph(
                        str(exames),
                        estilo_celula
                    ),

                    Paragraph(
                        f"R$ {float(valor):.2f}",
                        estilo_celula
                    )

                ]
            )


            total_geral += float(valor)


        tabela.append(
            [

                "",

                "",

                "",

                "",

                Paragraph(
                    "<b>TOTAL</b>",
                    estilo_cabecalho
                ),

                Paragraph(
                    f"<b>R$ {total_geral:.2f}</b>",
                    estilo_cabecalho
                )

            ]
        )


        # ==================================================
        # LARGURA DAS COLUNAS
        # ==================================================

        larguras_colunas = [

            4.5 * cm,

            4.5 * cm,

            2.2 * cm,

            2.3 * cm,

            9.0 * cm,

            2.3 * cm

        ]


        tabela_pdf = Table(
            tabela,

            colWidths=larguras_colunas,

            repeatRows=1,

            splitByRow=1
        )


        tabela_pdf.setStyle(
            TableStyle(
                [

                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey
                    ),

                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey
                    ),

                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP"
                    ),

                    (
                        "ALIGN",
                        (2, 1),
                        (3, -1),
                        "CENTER"
                    ),

                    (
                        "ALIGN",
                        (5, 1),
                        (5, -1),
                        "RIGHT"
                    ),

                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        3
                    ),

                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        3
                    ),

                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        3
                    ),

                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        3
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

            download_name=(
                "Relatorio_Faturamento.pdf"
            ),

            mimetype="application/pdf"
        )