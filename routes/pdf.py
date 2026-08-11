from flask import send_file, request
from database.database import conectar

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

import tempfile
import re


def registrar_rotas(app):

    @app.route("/gerar_pdf")
    def gerar_pdf():

        conexao = conectar()
        cursor = conexao.cursor()

        credenciada_id = request.args.get("credenciada")
        mes = request.args.get("mes")
        ano = request.args.get("ano")
        tipo = request.args.get("tipo")

        situacao_financeira = request.args.get(
            "situacao_financeira",
            ""
        )

        nome_credenciada = ""

        # ==================================================
        # NOME DA CREDENCIADA
        # ==================================================

        if credenciada_id:

            cursor.execute(
                """
                SELECT nome
                FROM credenciadas
                WHERE id = %s
                """,
                (
                    credenciada_id,
                )
            )

            resultado_credenciada = cursor.fetchone()

            if resultado_credenciada:

                nome_credenciada = (
                    resultado_credenciada["nome"]
                )

        # ==================================================
        # ATENDIMENTOS
        # MESMA CONSULTA DO EXCEL
        # ==================================================

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

        # ==================================================
        # FILTRO CREDENCIADA
        # ==================================================

        if credenciada_id:

            sql += """
                AND a.credenciada_id = %s
            """

            parametros.append(
                credenciada_id
            )

        # ==================================================
        # FILTRO MÊS
        # ==================================================

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

        # ==================================================
        # FILTRO ANO
        # ==================================================

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

        # ==================================================
        # FILTRO TIPO DE ATENDIMENTO
        # ==================================================

        if tipo:

            sql += """
                AND a.tipo_atendimento = %s
            """

            parametros.append(
                tipo
            )

        # ==================================================
        # IMPORTANTE
        #
        # A CONSULTA DO EXCEL NÃO APLICA
        # situacao_financeira AQUI.
        #
        # PORTANTO O PDF TAMBÉM NÃO APLICA.
        # ==================================================

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

        # ==================================================
        # DETALHAMENTO DOS EXAMES
        # EXATAMENTE IGUAL AO EXCEL
        # ==================================================

        sql_exames = """
            SELECT
                ae.nome_exame,
                ae.valor_exame,
                COUNT(*) AS quantidade,
                SUM(ae.valor_exame) AS total

            FROM atendimento_exames ae

            INNER JOIN atendimentos a
                ON a.id = ae.atendimento_id

            WHERE 1=1
        """

        parametros_exames = []

        # ==================================================
        # FILTRO CREDENCIADA
        # ==================================================

        if credenciada_id:

            sql_exames += """
                AND a.credenciada_id = %s
            """

            parametros_exames.append(
                credenciada_id
            )

        # ==================================================
        # FILTRO MÊS
        # ==================================================

        if mes:

            sql_exames += """
                AND TO_CHAR(
                    a.data_atendimento,
                    'MM'
                ) = %s
            """

            parametros_exames.append(
                f"{int(mes):02}"
            )

        # ==================================================
        # FILTRO ANO
        # ==================================================

        if ano:

            sql_exames += """
                AND TO_CHAR(
                    a.data_atendimento,
                    'YYYY'
                ) = %s
            """

            parametros_exames.append(
                str(ano)
            )

        # ==================================================
        # FILTRO TIPO DE ATENDIMENTO
        # ==================================================

        if tipo:

            sql_exames += """
                AND a.tipo_atendimento = %s
            """

            parametros_exames.append(
                tipo
            )

        # ==================================================
        # NÃO APLICAR SITUAÇÃO FINANCEIRA
        #
        # IGUAL AO EXCEL
        # ==================================================

        sql_exames += """
            GROUP BY
                ae.nome_exame,
                ae.valor_exame

            ORDER BY
                ae.nome_exame
        """

        cursor.execute(
            sql_exames,
            parametros_exames
        )

        detalhamento_exames = cursor.fetchall()

        # ==================================================
        # CRIAR ARQUIVO PDF
        # ==================================================

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

        # ==================================================
        # ESTILOS
        # ==================================================

        estilo_titulo = ParagraphStyle(
            "TituloRelatorio",
            parent=estilos["Title"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=17,
            alignment=1,
            spaceAfter=10
        )

        estilo_secao = ParagraphStyle(
            "Secao",
            parent=estilos["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            alignment=0,
            spaceBefore=10,
            spaceAfter=6
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

        # ==================================================
        # CABEÇALHO
        # ==================================================

        elementos.append(
            Paragraph(
                f"""
                SIGAC - RELATÓRIO DE FATURAMENTO<br/>
                Credenciada: {nome_credenciada}<br/>
                Período: {mes or ''}/{ano or ''}<br/>
                Situação: {situacao_financeira or 'Todas'}
                """,
                estilo_titulo
            )
        )

        # ==================================================
        # TABELA DE ATENDIMENTOS
        # ==================================================

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

        # ==================================================
        # DADOS DOS ATENDIMENTOS
        # ==================================================

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

            # ==================================================
            # DATA
            # ==================================================

            if item["data_atendimento"]:

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

            else:

                data_atendimento = ""

            # ==================================================
            # VALOR
            # ==================================================

            valor = (
                item["valor"]
                or 0
            )

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

        # ==================================================
        # TOTAL DOS ATENDIMENTOS
        # ==================================================

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

        # ==================================================
        # DETALHAMENTO DOS EXAMES
        # ==================================================

        elementos.append(
            Spacer(
                1,
                0.5 * cm
            )
        )

        elementos.append(
            Paragraph(
                "DETALHAMENTO DOS EXAMES REALIZADOS",
                estilo_secao
            )
        )

        tabela_exames = [
            [
                Paragraph(
                    "Exame",
                    estilo_cabecalho
                ),

                Paragraph(
                    "Valor Unitário",
                    estilo_cabecalho
                ),

                Paragraph(
                    "Quantidade",
                    estilo_cabecalho
                ),

                Paragraph(
                    "Total",
                    estilo_cabecalho
                )
            ]
        ]

        total_exames = 0

        # ==================================================
        # DADOS DOS EXAMES
        # ==================================================

        for exame in detalhamento_exames:

            nome_exame = (
                exame["nome_exame"]
                or ""
            )

            # IMPORTANTE:
            # A consulta retorna valor_exame.
            # Não usar exame["valor_unitario"].

            valor_unitario = (
                exame["valor_exame"]
                or 0
            )

            quantidade = (
                exame["quantidade"]
                or 0
            )

            total = (
                exame["total"]
                or 0
            )

            tabela_exames.append(
                [
                    Paragraph(
                        str(nome_exame),
                        estilo_celula
                    ),

                    Paragraph(
                        f"R$ {float(valor_unitario):.2f}",
                        estilo_celula
                    ),

                    Paragraph(
                        str(quantidade),
                        estilo_celula
                    ),

                    Paragraph(
                        f"R$ {float(total):.2f}",
                        estilo_celula
                    )
                ]
            )

            total_exames += float(total)

        # ==================================================
        # TOTAL DOS EXAMES
        # ==================================================

        tabela_exames.append(
            [
                "",
                "",

                Paragraph(
                    "<b>TOTAL</b>",
                    estilo_cabecalho
                ),

                Paragraph(
                    f"<b>R$ {total_exames:.2f}</b>",
                    estilo_cabecalho
                )
            ]
        )

        # ==================================================
        # TABELA DE EXAMES
        # ==================================================

        tabela_exames_pdf = Table(
            tabela_exames,

            colWidths=[
                9.0 * cm,
                4.0 * cm,
                3.0 * cm,
                4.0 * cm
            ],

            repeatRows=1,
            splitByRow=1
        )

        tabela_exames_pdf.setStyle(
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
                        "MIDDLE"
                    ),

                    (
                        "ALIGN",
                        (1, 1),
                        (-1, -1),
                        "RIGHT"
                    ),

                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        4
                    ),

                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        4
                    ),

                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        4
                    ),

                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        4
                    )
                ]
            )
        )

        elementos.append(
            tabela_exames_pdf
        )

        # ==================================================
        # GERAR PDF
        # ==================================================

        pdf.build(
            elementos
        )

        conexao.close()

        # ==================================================
        # NOME DO ARQUIVO
        # ==================================================

        nome_arquivo = (
            f"{nome_credenciada} - "
            f"{mes or 'Todos'}-"
            f"{ano or ''} - "
            f"{tipo or 'Faturar'}.pdf"
        )

        nome_arquivo = re.sub(
            r'[\\/:\*?"<>|]',
            '',
            nome_arquivo
        )

        # ==================================================
        # ENVIAR PDF
        # ==================================================

        return send_file(
            arquivo.name,
            as_attachment=True,
            download_name=nome_arquivo,
            mimetype="application/pdf"
        )