import sqlite3
import os

PASTA_DB = "database"
ARQUIVO_DB = os.path.join(PASTA_DB, "controle_horas.db")


def conectar():

    if not os.path.exists(PASTA_DB):
        os.makedirs(PASTA_DB)

    conexao = sqlite3.connect(ARQUIVO_DB)
    conexao.row_factory = sqlite3.Row

    return conexao


def criar_tabelas():

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS registros(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        nome TEXT NOT NULL,

        data TEXT NOT NULL,

        entrada TEXT,

        saida TEXT,

        total TEXT

    )
    """)

    conn.commit()

    conn.close()
