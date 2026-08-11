from flask import send_file, request
from database.database import conectar

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

import tempfile


def registrar_rotas(app):

    @app.route("/gerar_excel")
    def gerar_excel():

        conexao = conectar()
        cursor = conexao.cursor()

        credenciada_id = request.args.get("credenciada")
        mes = request.args.get("mes")
        ano = request.args.get("ano")
        tipo = request.args.get("tipo")

        nome_credenciada = ""

        if credenciada_id:

            cursor.execute("""
                SELECT nome
                FROM credenciadas
                WHERE id = %s
            """, (
                credenciada_id,
            ))

            resultado_credenciada = cursor.fetchone()

            if resultado_credenciada:

                nome_credenciada = (
                    resultado_credenciada["nome"]
                )


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


        # ==================================================
        # CRIAR EXCEL
        # ==================================================

        wb = Workbook()

        ws = wb.active

        ws.title = "Faturamento"


        # ==================================================
        # CABEÇALHO
        # ==================================================

        ws.append([
            "SIGAC - RELATÓRIO DE FATURAMENTO"
        ])

        ws.append([
            f"Credenciada: {nome_credenciada}"
        ])

        ws.append([
            f"Período: {mes or ''}/{ano or ''}"
        ])

        ws.append([])


        ws.append([
            "Colaborador",
            "Empresa",
            "Data",
            "Tipo Atendimento",
            "Exames",
            "Valor"
        ])


        # ==================================================
        # FORMATAÇÃO DO CABEÇALHO
        # ==================================================

        for celula in ws[5]:

            celula.font = Font(
                bold=True
            )

            celula.alignment = Alignment(
                horizontal="center",
                vertical="center",
                wrap_text=True
            )


        # ==================================================
        # DADOS
        # ==================================================

        total_geral = 0


        for item in dados:

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


            valor = item["valor"] or 0


            ws.append([

                item["colaborador"] or "",

                item["empresa"] or "",

                data_atendimento,

                item["tipo_atendimento"] or "",

                item["exames"] or "",

                float(valor)

            ])


            total_geral += float(valor)


        # ==================================================
        # TOTAL
        # ==================================================

        ws.append([])

        ws.append([

            "",

            "",

            "",

            "",

            "TOTAL",

            total_geral

        ])


        # ==================================================
        # FORMATAÇÃO DAS CÉLULAS
        # ==================================================

        for linha in ws.iter_rows():

            for celula in linha:

                celula.alignment = Alignment(
                    vertical="top",
                    wrap_text=True
                )


        # ==================================================
        # FORMATAÇÃO DO TOTAL
        # ==================================================

        ultima_linha = ws.max_row

        ws.cell(
            row=ultima_linha,
            column=5
        ).font = Font(
            bold=True
        )

        ws.cell(
            row=ultima_linha,
            column=6
        ).font = Font(
            bold=True
        )


        # ==================================================
        # FORMATO DOS VALORES
        # ==================================================

        for linha in range(
            6,
            ultima_linha + 1
        ):

            ws.cell(
                row=linha,
                column=6
            ).number_format = (
                'R$ #,##0.00'
            )


        # ==================================================
        # LARGURA DAS COLUNAS
        # ==================================================

        larguras = {

            "A": 32,

            "B": 35,

            "C": 14,

            "D": 20,

            "E": 60,

            "F": 18

        }


        for coluna, largura in larguras.items():

            ws.column_dimensions[
                coluna
            ].width = largura


        # ==================================================
        # ALTURA DAS LINHAS
        # ==================================================

        for linha in range(
            6,
            ultima_linha + 1
        ):

            ws.row_dimensions[
                linha
            ].height = 30


        # ==================================================
        # CONGELAR CABEÇALHO
        # ==================================================

        ws.freeze_panes = "A6"


        # ==================================================
        # FILTRO NO CABEÇALHO
        # ==================================================

        if ws.max_row >= 5:

            ws.auto_filter.ref = (
                f"A5:F{ws.max_row}"
            )


        # ==================================================
        # CRIAR ARQUIVO
        # ==================================================

        arquivo = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".xlsx"
        )


        wb.save(
            arquivo.name
        )


        conexao.close()


        return send_file(

            arquivo.name,

            as_attachment=True,

            download_name=(
                "Relatorio_Faturamento.xlsx"
            ),

            mimetype=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )

        )