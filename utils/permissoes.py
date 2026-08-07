from flask import session
from database.database import conectar


def tem_permissao(modulo):

    if "perfil" not in session:
        return False


    perfil = session["perfil"]


    conexao = conectar()
    cursor = conexao.cursor()


    cursor.execute("""
        SELECT visualizar
        FROM permissoes
        WHERE perfil = %s
        AND modulo = %s
    """, (
        perfil,
        modulo
    ))


    resultado = cursor.fetchone()

    conexao.close()


    if resultado:

        return resultado["visualizar"] == 1


    return False