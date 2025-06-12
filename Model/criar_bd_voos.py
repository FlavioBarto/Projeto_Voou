import pandas as pd
import sqlite3
import os

def criar_banco_dados(conn, cursor):    
    # Criar tabela EMPRESA_AEREA
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS EMPRESA_AEREA (
        empresa_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sigla TEXT NOT NULL,
        nome TEXT NOT NULL,
        nacionalidade TEXT NOT NULL,
        UNIQUE(sigla, nome)
    )
    ''')
    
    # Criar tabela AEROPORTO
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS AEROPORTO (
        aeroporto_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sigla TEXT NOT NULL UNIQUE,
        nome TEXT NOT NULL,
        uf TEXT,
        regiao TEXT,
        pais TEXT NOT NULL,
        continente TEXT NOT NULL
    )
    ''')
    
    # Criar tabela TEMPO
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS TEMPO (
        tempo_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ano INTEGER NOT NULL,
        mes INTEGER NOT NULL,
        UNIQUE(ano, mes)
    )
    ''')
    
    # Criar tabela VOO
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS VOO (
        voo_id INTEGER PRIMARY KEY AUTOINCREMENT,
        empresa_id INTEGER NOT NULL,
        tempo_id INTEGER NOT NULL,
        aeroporto_origem_id INTEGER NOT NULL,
        aeroporto_destino_id INTEGER NOT NULL,
        natureza TEXT NOT NULL,
        grupo_voo TEXT NOT NULL,
        passageiros_pagos INTEGER DEFAULT 0,
        passageiros_gratis INTEGER DEFAULT 0,
        carga_paga_kg REAL DEFAULT 0,
        carga_gratis_kg REAL DEFAULT 0,
        correio_kg REAL DEFAULT 0,
        ask REAL DEFAULT 0,
        rpk REAL DEFAULT 0,
        atk REAL DEFAULT 0,
        rtk REAL DEFAULT 0,
        combustivel_litros REAL DEFAULT 0,
        distancia_voada_km REAL DEFAULT 0,
        decolagens INTEGER DEFAULT 0,
        carga_paga_km REAL DEFAULT 0,
        carga_gratis_km REAL DEFAULT 0,
        correio_km REAL DEFAULT 0,
        assentos INTEGER DEFAULT 0,
        payload REAL DEFAULT 0,
        horas_voadas REAL DEFAULT 0,
        bagagem_kg REAL DEFAULT 0,
        FOREIGN KEY (empresa_id) REFERENCES EMPRESA_AEREA(empresa_id),
        FOREIGN KEY (tempo_id) REFERENCES TEMPO(tempo_id),
        FOREIGN KEY (aeroporto_origem_id) REFERENCES AEROPORTO(aeroporto_id),
        FOREIGN KEY (aeroporto_destino_id) REFERENCES AEROPORTO(aeroporto_id)
    )
    ''')
    
    # Criar índices para melhorar performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_empresa_sigla ON EMPRESA_AEREA(sigla)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_aeroporto_sigla ON AEROPORTO(sigla)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_voo_empresa ON VOO(empresa_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_voo_tempo ON VOO(tempo_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_voo_origem ON VOO(aeroporto_origem_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_voo_destino ON VOO(aeroporto_destino_id)')
    
    # Salvar as alterações e fechar a conexão
    conn.commit()


def popular_banco_dados(conn, cursor, csv_path):    
    # Ler o arquivo CSV
    df = pd.read_csv(csv_path, delimiter=';', encoding="ISO-8859-1")
    
    # 1. Popular tabela EMPRESA_AEREA
    def insert_empresas():
        empresa_cols = ['EMPRESA (SIGLA)', 'EMPRESA (NOME)', 'EMPRESA (NACIONALIDADE)']
        df_empresas = df[empresa_cols].drop_duplicates()
        df_empresas.columns = ['sigla', 'nome', 'nacionalidade']
        
        for _, row in df_empresas.iterrows():
            cursor.execute('''
                SELECT empresa_id FROM EMPRESA_AEREA 
                WHERE sigla = ? AND nome = ?
            ''', (row['sigla'], row['nome']))
            
            if cursor.fetchone() is None:
                cursor.execute('''
                    INSERT INTO EMPRESA_AEREA (sigla, nome, nacionalidade)
                    VALUES (?, ?, ?)
                ''', (row['sigla'], row['nome'], row['nacionalidade']))
        
        conn.commit()
    
    # 2. Popular tabela AEROPORTO (origem e destino)
    def insert_aeroportos():
        # Criar DataFrame combinando dados de origem e destino
        cols_origem = [c for c in df.columns if 'AEROPORTO DE ORIGEM' in c]
        cols_destino = [c for c in df.columns if 'AEROPORTO DE DESTINO' in c]
        
        df_origem = df[cols_origem].copy()
        df_destino = df[cols_destino].copy()
        
        # Renomear colunas para padrão comum
        df_origem.columns = [c.replace('AEROPORTO DE ORIGEM ', '') for c in cols_origem]
        df_destino.columns = [c.replace('AEROPORTO DE DESTINO ', '') for c in cols_destino]
        
        # Combinar e remover duplicatas
        df_aeroportos = pd.concat([df_origem, df_destino]).drop_duplicates()
        
        for _, row in df_aeroportos.iterrows():
            cursor.execute('''
                SELECT aeroporto_id FROM AEROPORTO 
                WHERE sigla = ?
            ''', (row['(SIGLA)'],))
            
            if cursor.fetchone() is None:
                cursor.execute('''
                    INSERT INTO AEROPORTO (sigla, nome, uf, regiao, pais, continente)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    row['(SIGLA)'],
                    row['(NOME)'],
                    row.get('(UF)', None),  # Pode ser None para aeroportos internacionais
                    row.get('(REGIÃO)', None),
                    row['(PAÍS)'],
                    row['(CONTINENTE)']
                ))
        
        conn.commit()
    
    # 3. Popular tabela TEMPO
    def insert_tempo():
        df_tempo = df[['ANO', 'MÊS']].drop_duplicates()
        
        for _, row in df_tempo.iterrows():
            cursor.execute('''
                SELECT tempo_id FROM TEMPO 
                WHERE ano = ? AND mes = ?
            ''', (int(row['ANO']), int(row['MÊS'])))
            
            if cursor.fetchone() is None:
                cursor.execute('''
                    INSERT INTO TEMPO (ano, mes)
                    VALUES (?, ?)
                ''', (int(row['ANO']), int(row['MÊS'])))
        
        conn.commit()
    
    # 4. Popular tabela VOO
    def insert_voos():
        for _, row in df.iterrows():
            try:
                # Obter IDs das tabelas relacionadas com verificações
                cursor.execute('SELECT empresa_id FROM EMPRESA_AEREA WHERE sigla = ?', (row['EMPRESA (SIGLA)'],))
                empresa_result = cursor.fetchone()
                if empresa_result is None:
                    continue
                empresa_id = empresa_result[0]
                
                cursor.execute('SELECT tempo_id FROM TEMPO WHERE ano = ? AND mes = ?', (row['ANO'], row['MÊS']))
                tempo_result = cursor.fetchone()
                if tempo_result is None:
                    # Se não existir, insere o novo período
                    cursor.execute('INSERT INTO TEMPO (ano, mes) VALUES (?, ?)', (row['ANO'], row['MÊS']))
                    tempo_id = cursor.lastrowid
                    conn.commit()
                else:
                    tempo_id = tempo_result[0]
                
                cursor.execute('SELECT aeroporto_id FROM AEROPORTO WHERE sigla = ?', (row['AEROPORTO DE ORIGEM (SIGLA)'],))
                origem_result = cursor.fetchone()
                if origem_result is None:
                    continue
                origem_id = origem_result[0]
                
                cursor.execute('SELECT aeroporto_id FROM AEROPORTO WHERE sigla = ?', (row['AEROPORTO DE DESTINO (SIGLA)'],))
                destino_result = cursor.fetchone()
                if destino_result is None:
                    continue
                destino_id = destino_result[0]
                
                # Inserir o voo
                cursor.execute('''
                    INSERT INTO VOO (
                        empresa_id, tempo_id, aeroporto_origem_id, aeroporto_destino_id,
                        natureza, grupo_voo, passageiros_pagos, passageiros_gratis,
                        carga_paga_kg, carga_gratis_kg, correio_kg, ask, rpk, atk, rtk,
                        combustivel_litros, distancia_voada_km, decolagens, carga_paga_km,
                        carga_gratis_km, correio_km, assentos, payload, horas_voadas, bagagem_kg
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    empresa_id, tempo_id, origem_id, destino_id,
                    row['NATUREZA'], row['GRUPO DE VOO'],
                    row['PASSAGEIROS PAGOS'] or 0, row['PASSAGEIROS GRÁTIS'] or 0,
                    row['CARGA PAGA (KG)'] or 0, row['CARGA GRÁTIS (KG)'] or 0, row['CORREIO (KG)'] or 0,
                    row['ASK'] or 0, row['RPK'] or 0, row['ATK'] or 0, row['RTK'] or 0,
                    row['COMBUSTÍVEL (LITROS)'] or 0, row['DISTÂNCIA VOADA (KM)'] or 0, row['DECOLAGENS'] or 0,
                    row['CARGA PAGA KM'] or 0, row['CARGA GRATIS KM'] or 0, row['CORREIO KM'] or 0,
                    row['ASSENTOS'] or 0, row['PAYLOAD'] or 0, row['HORAS VOADAS'] or 0, row['BAGAGEM (KG)'] or 0
                ))
                
            except Exception as e:
                conn.rollback()
                continue
        
        conn.commit()
        
    # Executar todas as funções de inserção
    insert_empresas()
    insert_aeroportos()
    insert_tempo()
    insert_voos()

def verificar_bd_existente(db_path='voos_database.db'):
    """Verifica se o banco de dados já foi criado e populado"""
    if not os.path.exists(db_path):
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verifica se a tabela VOO já contém dados
        cursor.execute("SELECT COUNT(*) FROM VOO")
        count = cursor.fetchone()[0]
        return count > 0
    except sqlite3.OperationalError:
        return False
    finally:
        conn.close()

def csv_to_sqlite_voo(conn_voo, cursor_voo):
    try:
        # Verificar se o banco já foi populado
        if verificar_bd_existente():
            # print("Banco de dados voos já existe e contém dados. Pulando a inserção.")
            return
            
        criar_banco_dados(conn_voo, cursor_voo)
        caminho_csv = "arquivos_csv/resumo_anual_2025.csv"  
        popular_banco_dados(conn=conn_voo, cursor=cursor_voo, csv_path=caminho_csv)
        # print("Banco de dados voos criado e populado com sucesso!")
    except Exception as e:
        print(f"Erro ao processar o banco de dados voos: {str(e)}")
        conn_voo.rollback()


if __name__ == "__main__":
    csv_to_sqlite_voo()
