import sqlite3

BANCO = "controle_horas.db"


def conectar():
    conn = sqlite3.connect(BANCO)
    conn.row_factory = sqlite3.Row
    return conn


def criar_banco():

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS registros (

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
