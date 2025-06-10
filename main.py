import pandas as pd
import sqlite3

conn = sqlite3.connect("weather_database.db")
cursor = conn.cursor()

df = pd.read_sql_query("SELECT * FROM weather_data", conn)

print(df)