from flask import send_file, request
from database.database import conectar

from openpyxl import Workbook
from openpyxl.styles import Font

import tempfile


def registrar_rotas(app):

    @app.route("/gerar_excel")
    def gerar_excel():

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

        wb = Workbook()

        ws = wb.active

        ws.title = "Faturamento"

        cabecalho = [

            "Colaborador",
            "Empresa",
            "Data",
            "Tipo Atendimento",
            "Exames",
            "Valor"

        ]

        ws.append(cabecalho)

        for celula in ws[1]:
            celula.font = Font(bold=True)

        total_geral = 0

        for item in dados:

            ws.append([

                item["colaborador"],
                item["empresa"],
                item["data_atendimento"],
                item["tipo_atendimento"],
                item["exames"] if item["exames"] else "",
                item["valor"]

            ])

            total_geral += item["valor"]

        ws.append([])

        ws.append([
            "",
            "",
            "",
            "",
            "TOTAL",
            total_geral
        ])

        arquivo = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".xlsx"
        )

        wb.save(arquivo.name)

        conexao.close()

        return send_file(

            arquivo.name,

            as_attachment=True,

            download_name="Relatorio_Faturamento.xlsx",

            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        )