from flask import render_template, request, redirect, session
from database.database import conectar
from datetime import datetime
from utils.decoradores import exige_permissao

def registrar_rotas(app):
        
    @app.route("/alterar_status_faturamento")
    def alterar_status_faturamento():

        conexao = conectar()
        cursor = conexao.cursor()

        credenciada = request.args.get("credenciada")
        mes = request.args.get("mes")
        ano = request.args.get("ano")
        status = request.args.get("status")

        cursor.execute("""
            SELECT id
            FROM faturamentos
            WHERE credenciada_id = %s
              AND mes = %s
              AND ano = %s
        """, (credenciada, mes, ano))

        faturamento = cursor.fetchone()

        if faturamento:

            cursor.execute("""
                UPDATE faturamentos
                SET status = %s
                WHERE id = %s
            """, (status, faturamento["id"]))

        else:

            cursor.execute("""
                INSERT INTO faturamentos
                (
                    credenciada_id,
                    mes,
                    ano,
                    status
                )
                VALUES (%s, %s, %s, %s)
            """, (credenciada, mes, ano, status))

        conexao.commit()
        conexao.close()

        return redirect(
            f"/financeiro?credenciada={credenciada}&mes={mes}&ano={ano}"
        )

    @app.route("/financeiro")
    @exige_permissao("financeiro")
    def financeiro():

        conexao = conectar()
        cursor = conexao.cursor()

        # ==========================
        # FILTROS
        # ==========================

        credenciada_id = request.args.get("credenciada", "")
        mes = request.args.get("mes", "")
        ano = request.args.get("ano", str(datetime.now().year))
        situacao_financeira = request.args.get(
            "situacao_financeira",
            ""
        )

        # ==========================
        # LISTA DE CREDENCIADAS
        # ==========================

        cursor.execute("""
            SELECT
                id,
                nome
            FROM credenciadas
            ORDER BY nome
        """)

        credenciadas = cursor.fetchall()

        # ==========================
        # SQL BASE
        # ==========================

        sql = """
            SELECT

                ae.exame_id,

                ae.nome_exame,

                COUNT(ae.id) AS quantidade,

                COALESCE(AVG(ae.valor_exame),0) AS valor_unitario,

                COALESCE(SUM(ae.valor_exame),0) AS valor_total

            FROM atendimento_exames ae

            INNER JOIN atendimentos a
                ON a.id = ae.atendimento_id

            WHERE 1=1
        """

        parametros = []

        # ==========================
        # FILTRO CREDENCIADA
        # ==========================

        if credenciada_id:

            sql += """
                AND a.credenciada_id = %s
            """

            parametros.append(credenciada_id)

        # ==========================
        # FILTRO MÊS
        # ==========================

        if mes:

            sql += """
                AND EXTRACT(MONTH FROM a.data_atendimento) = %s
            """

            parametros.append(int(mes))

        # ==========================
        # FILTRO ANO
        # ==========================

        if ano:

            sql += """
                AND EXTRACT(YEAR FROM a.data_atendimento) = %s
            """

            parametros.append(
                int(ano)
            )

        # ==========================
        # FILTRO SITUAÇÃO FINANCEIRA
        # ==========================

        if situacao_financeira:

            sql += """
                AND a.situacao_financeira = %s
            """

            parametros.append(
                situacao_financeira
            )

        # ==========================
        # AGRUPAMENTO
        # ==========================

        sql += """

                GROUP BY

                    ae.exame_id,
                    ae.nome_exame

                ORDER BY

                    ae.nome_exame

            """

        cursor.execute(sql, parametros)

        resumo = cursor.fetchall()

        # ==========================
        # TOTAL GERAL
        # ==========================

        total_geral = 0

        total_exames = 0

        for item in resumo:

            total_geral += item["valor_total"]

            total_exames += item["quantidade"]

        # ==========================
        # TOTAL DE ATENDIMENTOS
        # ==========================

        sql_atendimentos = """
            SELECT
                COUNT(DISTINCT a.id) AS total
            FROM atendimentos a
            WHERE 1=1
        """

        parametros_atendimentos = []

        if credenciada_id:

            sql_atendimentos += """
                AND a.credenciada_id = %s
            """

            parametros_atendimentos.append(credenciada_id)

        if mes:

            sql_atendimentos += """
                AND EXTRACT(MONTH FROM a.data_atendimento) = %s
            """

            parametros_atendimentos.append(int(mes))

        if ano:

            sql_atendimentos += """
                AND EXTRACT(YEAR FROM a.data_atendimento) = %s
            """

            parametros_atendimentos.append(int(ano))

        cursor.execute(sql_atendimentos, parametros_atendimentos)


        resultado = cursor.fetchone()

        total_atendimentos = resultado["total"] if resultado else 0

        # ==========================
        # STATUS DO FATURAMENTO
        # ==========================

        status_faturamento = "Em Conferência"

        if credenciada_id and mes and ano:

            cursor.execute("""
                SELECT status
                FROM faturamentos
                WHERE credenciada_id = %s
                  AND mes = %s
                  AND ano = %s
            """, (credenciada_id, mes, ano))

            faturamento = cursor.fetchone()

            if faturamento:
                status_faturamento = faturamento["status"]

        conexao.close()

        return render_template(

            "financeiro.html",

            resumo=resumo,

            total_geral=total_geral,

            total_exames=total_exames,

            total_atendimentos=total_atendimentos,

            credenciadas=credenciadas,

            credenciada_id=credenciada_id,

            mes=mes,

            ano=ano,

            status_faturamento=status_faturamento

        )
