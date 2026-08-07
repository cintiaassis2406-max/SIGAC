from functools import wraps
from flask import session, redirect


def exige_permissao(modulo):

    def decorador(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            if "usuario" not in session:
                return redirect("/")


            from database.database import conectar


            conexao = conectar()
            cursor = conexao.cursor()


            cursor.execute("""
                SELECT visualizar
                FROM permissoes
                WHERE perfil = %s
                AND modulo = %s
            """, (
                session["perfil"],
                modulo
            ))


            permissao = cursor.fetchone()


            conexao.close()


            if not permissao or permissao["visualizar"] != 1:
                return "Acesso não permitido", 403


            return func(*args, **kwargs)


        return wrapper

    return decorador