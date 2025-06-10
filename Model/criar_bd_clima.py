import sqlite3
import pandas as pd
from datetime import datetime

# Conectar ao banco de dados
conn = sqlite3.connect('weather_database.db')
cursor = conn.cursor()

# Carregar os dados do CSV
df = pd.read_csv("arquivos_csv/GlobalWeatherRepository.csv")

def criar_tabelas():
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS location (
            location_id INTEGER PRIMARY KEY AUTOINCREMENT,
            country TEXT NOT NULL,
            location_name TEXT NOT NULL,
            latitude REAL NOT NULL,        -- Decimal degrees (-90 to 90)
            longitude REAL NOT NULL,       -- Decimal degrees (-180 to 180)
            timezone TEXT NOT NULL,
            CONSTRAINT unique_location UNIQUE (country, location_name)
        );

        CREATE TABLE IF NOT EXISTS weather_condition (
            condition_id INTEGER PRIMARY KEY AUTOINCREMENT,
            condition_text TEXT NOT NULL UNIQUE COLLATE NOCASE
        );

        CREATE TABLE IF NOT EXISTS weather_data (
            weather_id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id INTEGER NOT NULL,
            condition_id INTEGER NOT NULL,
            last_updated_epoch INTEGER NOT NULL,    -- Unix timestamp
            last_updated TEXT NOT NULL,            -- Formatted datetime
            temperature_celsius REAL NOT NULL,     -- Degrees Celsius
            wind_kph REAL NOT NULL,                -- Wind speed in km/h
            wind_degree INTEGER,                   -- 0-360 degrees
            wind_direction TEXT,                   -- Cardinal direction (NNW, SW, etc)
            pressure_mb REAL NOT NULL,             -- Atmospheric pressure in millibars
            precip_mm REAL NOT NULL DEFAULT 0,     -- Precipitation in mm
            humidity_percentage INTEGER NOT NULL,  -- 0-100%
            cloud_percentage INTEGER NOT NULL,     -- 0-100%
            feels_like_celsius REAL NOT NULL,      -- Apparent temperature in Celsius
            visibility_km REAL NOT NULL,           -- Visibility in kilometers
            uv_index REAL NOT NULL,                -- UV Index (0-11+)
            gust_kph REAL,                         -- Wind gust in km/h
            FOREIGN KEY (location_id) REFERENCES location(location_id),
            FOREIGN KEY (condition_id) REFERENCES weather_condition(condition_id),
            CONSTRAINT valid_humidity CHECK (humidity_percentage BETWEEN 0 AND 100),
            CONSTRAINT valid_cloud CHECK (cloud_percentage BETWEEN 0 AND 100),
            CONSTRAINT valid_uv CHECK (uv_index >= 0)
        );

        CREATE TABLE IF NOT EXISTS air_quality (
            air_quality_id INTEGER PRIMARY KEY AUTOINCREMENT,
            weather_id INTEGER NOT NULL,
            carbon_monoxide REAL,          -- CO in μg/m³
            ozone REAL,                    -- O₃ in μg/m³
            nitrogen_dioxide REAL,         -- NO₂ in μg/m³
            sulphur_dioxide REAL,          -- SO₂ in μg/m³
            pm2_5 REAL,                   -- PM2.5 in μg/m³
            pm10 REAL,                    -- PM10 in μg/m³
            us_epa_index INTEGER,         -- US EPA scale (1-6)
            gb_defra_index INTEGER,       -- UK Defra scale (1-10)
            FOREIGN KEY (weather_id) REFERENCES weather_data(weather_id),
            CONSTRAINT valid_epa_index CHECK (us_epa_index BETWEEN 1 AND 6),
            CONSTRAINT valid_defra_index CHECK (gb_defra_index BETWEEN 1 AND 10)
        );

        CREATE TABLE IF NOT EXISTS astronomical_events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id INTEGER NOT NULL,
            event_date TEXT NOT NULL,      -- Date in YYYY-MM-DD format
            sunrise TEXT NOT NULL,         -- Time in HH:MM AM/PM format
            sunset TEXT NOT NULL,          -- Time in HH:MM AM/PM format
            moonrise TEXT,                 -- Time in HH:MM AM/PM format
            moonset TEXT,                  -- Time in HH:MM AM/PM format
            moon_phase TEXT,               -- Phase description
            moon_illumination INTEGER,     -- Percentage 0-100
            FOREIGN KEY (location_id) REFERENCES location(location_id),
            CONSTRAINT valid_illumination CHECK (moon_illumination BETWEEN 0 AND 100),
            CONSTRAINT unique_daily_events UNIQUE (location_id, event_date)
        );
    """)
    conn.commit()

# 1. Primeiro, popular a tabela de localizações
def insert_locations():
    # Selecionar e tratar colunas de localização
    location_cols = ['country', 'location_name', 'latitude', 'longitude', 'timezone']
    df_locations = df[location_cols].drop_duplicates()
    
    for _, row in df_locations.iterrows():
        # Verificar se a localização já existe
        cursor.execute('''
            SELECT location_id FROM location 
            WHERE country = ? AND location_name = ?
        ''', (row['country'], row['location_name']))
        
        if cursor.fetchone() is None:
            cursor.execute('''
                INSERT INTO location (country, location_name, latitude, longitude, timezone)
                VALUES (?, ?, ?, ?, ?)
            ''', (row['country'], row['location_name'], row['latitude'], 
                 row['longitude'], row['timezone']))
    
    conn.commit()

# 2. Popular a tabela de condições meteorológicas
def insert_weather_conditions():
    conditions = df['condition_text'].unique()
    
    for condition in conditions:
        if pd.notna(condition):
            normalized = condition.strip()
            
            cursor.execute('''
                SELECT condition_id FROM weather_condition WHERE condition_text = ?
            ''', (normalized,))
            
            if cursor.fetchone() is None:
                cursor.execute('''
                    INSERT INTO weather_condition (condition_text) VALUES (?)
                ''', (normalized,))
    
    conn.commit()

# 3. Popular os dados meteorológicos principais
def insert_weather_data():
    # Primeiro precisamos mapear location_name para location_id
    cursor.execute('SELECT location_id, country, location_name FROM location')
    location_map = {(country, name): id for id, country, name in cursor.fetchall()}
    
    # Mapear condition_text para condition_id
    cursor.execute('SELECT condition_id, condition_text FROM weather_condition')
    condition_map = {text: id for id, text in cursor.fetchall()}
    
    for _, row in df.iterrows():
        location_key = (row['country'], row['location_name'])
        location_id = location_map.get(location_key)
        condition_id = condition_map.get(row['condition_text'])
        
        if location_id and condition_id:
            # Converter last_updated para formato padrão se necessário
            last_updated = row['last_updated']
            if isinstance(last_updated, str):
                try:
                    # Tentar converter para formato datetime consistente
                    dt = datetime.strptime(last_updated, '%Y-%m-%d %H:%M')
                    last_updated = dt.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    pass
            
            cursor.execute('''
                INSERT INTO weather_data (
                    location_id, condition_id, last_updated_epoch, last_updated,
                    temperature_celsius, wind_kph, wind_degree, wind_direction,
                    pressure_mb, precip_mm, humidity_percentage, cloud_percentage,
                    feels_like_celsius, visibility_km, uv_index, gust_kph
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                location_id, condition_id, row['last_updated_epoch'], last_updated,
                row['temperature_celsius'], row['wind_kph'], row['wind_degree'], row['wind_direction'],
                row['pressure_mb'], row['precip_mm'], row['humidity'], row['cloud'],
                row['feels_like_celsius'], row['visibility_km'], row['uv_index'], row['gust_kph']
            ))
    
    conn.commit()

# 4. Popular dados de qualidade do ar
def insert_air_quality():
    # Primeiro, criar um dicionário para mapear local+data para weather_id
    cursor.execute('''
        SELECT w.weather_id, l.country, l.location_name, w.last_updated 
        FROM weather_data w
        JOIN location l ON w.location_id = l.location_id
    ''')
    
    # Criar chave composta: (country, location_name, last_updated)
    weather_map = {}
    for weather_id, country, location_name, last_updated in cursor.fetchall():
        # Padronizar formato da data/hora
        if isinstance(last_updated, str):
            try:
                dt = datetime.strptime(last_updated, '%Y-%m-%d %H:%M:%S')
                last_updated = dt.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass
        weather_map[(country, location_name, last_updated)] = weather_id
    
    # Agora processar os dados do CSV
    air_quality_cols = [
        'country', 'location_name', 'last_updated',
        'air_quality_Carbon_Monoxide', 'air_quality_Ozone',
        'air_quality_Nitrogen_dioxide', 'air_quality_Sulphur_dioxide',
        'air_quality_PM2.5', 'air_quality_PM10',
        'air_quality_us-epa-index', 'air_quality_gb-defra-index'
    ]
    
    # Filtrar apenas linhas com dados de qualidade do ar
    df_air = df[air_quality_cols].dropna(subset=['air_quality_PM2.5'])
    
    for _, row in df_air.iterrows():
        # Padronizar last_updated para corresponder ao formato no banco
        last_updated = row['last_updated']
        if isinstance(last_updated, str):
            try:
                dt = datetime.strptime(last_updated, '%Y-%m-%d %H:%M')
                last_updated = dt.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
        
        # Buscar o weather_id correspondente
        key = (row['country'], row['location_name'], last_updated)
        weather_id = weather_map.get(key)
        
        if weather_id:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO air_quality (
                        weather_id, carbon_monoxide, ozone, nitrogen_dioxide,
                        sulphur_dioxide, pm2_5, pm10, us_epa_index, gb_defra_index
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    weather_id,
                    row['air_quality_Carbon_Monoxide'],
                    row['air_quality_Ozone'],
                    row['air_quality_Nitrogen_dioxide'],
                    row['air_quality_Sulphur_dioxide'],
                    row['air_quality_PM2.5'],
                    row['air_quality_PM10'],
                    row['air_quality_us-epa-index'],
                    row['air_quality_gb-defra-index']
                ))
            except sqlite3.Error as e:
                print(f"Erro ao inserir qualidade do ar para {key}: {e}")
    
    conn.commit()

# 5. Popular eventos astronômicos
def insert_astronomical_events():
    # Primeiro mapear location_name para location_id
    cursor.execute('SELECT location_id, country, location_name FROM location')
    location_map = {(country, name): id for id, country, name in cursor.fetchall()}
    
    for _, row in df.iterrows():
        location_key = (row['country'], row['location_name'])
        location_id = location_map.get(location_key)
        
        if location_id and pd.notna(row['sunrise']):
            # Extrair a data do last_updated
            event_date = row['last_updated'].split()[0] if isinstance(row['last_updated'], str) else None
            
            if event_date:
                # Verificar se já existe registro para esta data e localização
                cursor.execute('''
                    SELECT event_id FROM astronomical_events
                    WHERE location_id = ? AND event_date = ?
                ''', (location_id, event_date))
                
                if cursor.fetchone() is None:
                    cursor.execute('''
                        INSERT INTO astronomical_events (
                            location_id, event_date, sunrise, sunset,
                            moonrise, moonset, moon_phase, moon_illumination
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        location_id, event_date, row['sunrise'], row['sunset'],
                        row['moonrise'], row['moonset'], row['moon_phase'], row['moon_illumination']
                    ))
    
    conn.commit()

# Executar todas as funções de inserção
try:
    criar_tabelas()
    insert_locations()
    insert_weather_conditions()
    insert_weather_data()
    insert_air_quality()
    insert_astronomical_events()
    print("Banco de dados populado com sucesso!")
except Exception as e:
    print(f"Erro ao popular o banco: {e}")
    conn.rollback()
finally:
    conn.close()
