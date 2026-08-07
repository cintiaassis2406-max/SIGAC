from flask import render_template, request, redirect, session
from database.database import conectar


def registrar_rotas(app):


    @app.route("/permissoes", methods=["GET", "POST"])
    def permissoes():

        if "usuario" not in session:
            return redirect("/")


        if session.get("perfil") != "Administrador":
            return "Acesso não permitido", 403


        conexao = conectar()
        cursor = conexao.cursor()


        if request.method == "POST":

            permissao_id = request.form["id"]

            visualizar = 1 if "visualizar" in request.form else 0
            criar = 1 if "criar" in request.form else 0
            editar = 1 if "editar" in request.form else 0
            excluir = 1 if "excluir" in request.form else 0


            cursor.execute("""
                UPDATE permissoes
                SET visualizar = %s,
                    criar = %s,
                    editar = %s,
                    excluir = %s
                WHERE id = %s
            """, (
                visualizar,
                criar,
                editar,
                excluir,
                permissao_id
            ))


            conexao.commit()


        cursor.execute("""
            SELECT *
            FROM permissoes
            ORDER BY perfil, modulo
        """)


        lista = cursor.fetchall()


        conexao.close()


        return render_template(
            "permissoes.html",
            permissoes=lista
        )