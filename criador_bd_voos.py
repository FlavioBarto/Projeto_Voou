import sqlite3

conn = sqlite3.connect('banco_voos.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS aviao(
    id_aviao INTEGER PRIMARY KEY AUTOINCREMENT,
    distancia_voada TEXT NOT NULL,
    horas_voadas FLOAT NOT NULL,
    assentos INTEGER NOT NULL,
    bagagem TEXT NOT NULL,
    fk_empresa INTEGER NOT NULL
    fk_voo INTEGER NOT NULL,
    fk_informacoes INTEGER NOT NULL,
    FOREIGN KEY (fk_empresa) REFERENCES empresa(fk_aviao),
    FOREIGN KEY (fk_voo) REFERENCES voo(fk_aviao),
    FOREIGN KEY (fk_informacoes) REFERENCES informacoes(fk_informacao_aviao)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS voo(
    id_voo INTEGER PRIMARY KEY AUTOINCREMENT,
    mes INTEGER NOT NULL,
    nome_aeroporto_origem TEXT NOT NULL,
    nome_aeroporto_destino TEXT NOT NULL,
    natureza TEXT NOT NULL,
    fk_aviao INTEGER NOT NULL,
    FOREIGN KEY (fk_aviao) REFERENCES aviao(fk_voo)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS empresa(
    id_empresa INTEGER PRIMARY KEY AUTOINCREMENT,
    sigla INTEGER NOT NULL,
    nome TEXT NOT NULL,
    nacionalidade TEXT NOT NULL,
    fk_aviao INTEGER NOT NULL,
    FOREIGN KEY (fk_aviao) REFERENCES aviao(fk_empresa)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS informacoes(
    id_informacao INTEGER PRIMARY KEY AUTOINCREMENT,
    ask REAL NOT NULL,     
    rpk REAL NOT NULL,
    atk REAL NOT NULL,
    rtk REAL NOT NULL,
    fk_informacao_aviao INTEGER NOT NULL,
    FOREIGN KEY (fk_informacao_aviao) REFERENCES aviao(fk_informacoes)
)
""")