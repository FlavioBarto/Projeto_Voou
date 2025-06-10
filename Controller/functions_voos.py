import sqlite3

conn = sqlite3.connect('voos_database.db')

def faturamento_passagens_passageiros(data_hoje, data_fim):
    passagens = conn.execute("")
    