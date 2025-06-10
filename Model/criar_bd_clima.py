import sqlite3

conn = sqlite3.connect('banco_clima.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS pais(
    id_pais INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_pais TEXT NOT NULL,
    nome_local_pais TEXT NOT NULL,
    latitude TEXT NOT NULL,
    longitude TEXT NOT NULL,
    fuso_horario TEXT NOT NULL,
    ultima_atualizacao DATETIME NOT NULL,
    temperatura_celsius REAL NOT NULL,
    temperatura_fahrenheit REAL NOT NULL,
    condicao TEXT NOT NULL  
)
""")