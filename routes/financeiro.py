from flask import render_template, request, redirect
from database.database import conectar
from datetime import datetime

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
            WHERE credenciada_id = ?
              AND mes = ?
              AND ano = ?
        """, (credenciada, mes, ano))

        faturamento = cursor.fetchone()

        if faturamento:

            cursor.execute("""
                UPDATE faturamentos
                SET status = ?
                WHERE id = ?
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
                VALUES (?, ?, ?, ?)
            """, (credenciada, mes, ano, status))

        conexao.commit()
        conexao.close()

        return redirect(
            f"/financeiro?credenciada={credenciada}&mes={mes}&ano={ano}"
        )

    @app.route("/financeiro")
    def financeiro():

        conexao = conectar()
        cursor = conexao.cursor()

        # ==========================
        # FILTROS
        # ==========================

        credenciada_id = request.args.get("credenciada", "")
        mes = request.args.get("mes", "")
        ano = request.args.get("ano", str(datetime.now().year))

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
                AND a.credenciada_id = ?
            """

            parametros.append(credenciada_id)

        # ==========================
        # FILTRO MÊS
        # ==========================

        if mes:

            sql += """
                AND strftime('%m', a.data_atendimento)=?
            """

            parametros.append(f"{int(mes):02}")

        # ==========================
        # FILTRO ANO
        # ==========================

        if ano:

            sql += """
                AND strftime('%Y', a.data_atendimento)=?
            """

            parametros.append(str(ano))

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
                AND a.credenciada_id = ?
            """

            parametros_atendimentos.append(credenciada_id)

        if mes:

            sql_atendimentos += """
                AND strftime('%m', a.data_atendimento)=?
            """

            parametros_atendimentos.append(f"{int(mes):02}")

        if ano:

            sql_atendimentos += """
                AND strftime('%Y', a.data_atendimento)=?
            """

            parametros_atendimentos.append(str(ano))

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
                WHERE credenciada_id = ?
                  AND mes = ?
                  AND ano = ?
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
