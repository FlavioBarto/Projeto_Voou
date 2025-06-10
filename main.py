import pandas as pd
import sqlite3

conn_clima = sqlite3.connect("weather_database.db")

df_clima = pd.read_sql_query("SELECT * FROM weather_data", conn_clima)

print(df_clima)

print("=" * 200)

conn_voo = sqlite3.connect("voos_database.db")

df_voos = pd.read_sql_query("SELECT * FROM voo", conn_voo)

print(df_voos)