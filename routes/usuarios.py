from flask import render_template, request, redirect
from database.database import conectar
import bcrypt


def registrar_rotas(app):

    @app.route("/usuarios", methods=["GET", "POST"])
    def usuarios():

        conexao = conectar()
        cursor = conexao.cursor()


        if request.method == "POST":

            nome = request.form["nome"]
            usuario = request.form["usuario"]
            senha = request.form["senha"]
            perfil = request.form["perfil"]


            senha = bcrypt.hashpw(
                senha.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")


            cursor.execute("""
                INSERT INTO usuarios
                (
                    nome,
                    usuario,
                    senha,
                    perfil,
                    ativo
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (
                nome,
                usuario,
                senha,
                perfil,
                1
            ))


            conexao.commit()

            conexao.close()

            return redirect("/usuarios")



        cursor.execute("""
            SELECT *
            FROM usuarios
            ORDER BY nome
        """)


        lista = cursor.fetchall()


        conexao.close()


        return render_template(
            "usuarios.html",
            usuarios=lista
        )



    @app.route("/editar_usuario/<int:id>", methods=["GET", "POST"])
    def editar_usuario(id):

        conexao = conectar()
        cursor = conexao.cursor()


        if request.method == "POST":

            nome = request.form["nome"]
            usuario = request.form["usuario"]
            perfil = request.form["perfil"]


            cursor.execute("""
                UPDATE usuarios
                SET
                    nome=%s,
                    usuario=%s,
                    perfil=%s
                WHERE id=%s
            """, (
                nome,
                usuario,
                perfil,
                id
            ))


            conexao.commit()

            conexao.close()

            return redirect("/usuarios")



        cursor.execute("""
            SELECT *
            FROM usuarios
            WHERE id=%s
        """, (
            id,
        ))


        usuario = cursor.fetchone()


        conexao.close()


        return render_template(
            "editar_usuario.html",
            usuario=usuario
        )



    @app.route("/alterar_status_usuario/<int:id>")
    def alterar_status_usuario(id):

        conexao = conectar()
        cursor = conexao.cursor()


        cursor.execute("""
            SELECT ativo
            FROM usuarios
            WHERE id=%s
        """, (
            id,
        ))


        usuario = cursor.fetchone()


        if usuario:

            novo_status = 0 if usuario["ativo"] == 1 else 1


            cursor.execute("""
                UPDATE usuarios
                SET ativo=%s
                WHERE id=%s
            """, (
                novo_status,
                id
            ))


            conexao.commit()


        conexao.close()


        return redirect("/usuarios")



    @app.route("/alterar_senha/<int:id>", methods=["GET", "POST"])
    def alterar_senha(id):

        conexao = conectar()
        cursor = conexao.cursor()


        if request.method == "POST":

            senha = request.form["senha"]


            senha = bcrypt.hashpw(
                senha.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")


            cursor.execute("""
                UPDATE usuarios
                SET senha=%s
                WHERE id=%s
            """, (
                senha,
                id
            ))


            conexao.commit()

            conexao.close()

            return redirect("/usuarios")



        cursor.execute("""
            SELECT
                id,
                nome,
                usuario
            FROM usuarios
            WHERE id=%s
        """, (
            id,
        ))


        usuario = cursor.fetchone()


        conexao.close()


        return render_template(
            "alterar_senha.html",
            usuario=usuario
        )



    @app.route("/excluir_usuario/<int:id>")
    def excluir_usuario(id):

        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute("""
            DELETE FROM usuarios
            WHERE id=%s
        """, (
            id,
        ))

        conexao.commit()

        conexao.close()

        return redirect("/usuarios")