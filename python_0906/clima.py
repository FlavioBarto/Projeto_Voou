import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

df = pd.read_csv('GlobalWeatherRepository.csv', sep=',', encoding='utf-8')
df_Colunas = df[['country', 'location_name', 'latitude', 'longitude', 'last_updated', 'temperature_celsius', 'temperature_fahrenheit', 'timezone', 'condition_text']]
st.dataframe(df_Colunas)

# Converter data para datetime
df['last_updated'] = pd.to_datetime(df['last_updated'])

#filtro e telas

Telas = st.sidebar.selectbox("Telas: ", ["🌍 Mapa-Mundi","🌤️ Clima dos Paises","📊 DashBoard"])

#Tela Bignumbers e Mapa-mundi
if(Telas == "🌍 Mapa-Mundi"):
        Temp = st.sidebar.selectbox("Temperatura: ", ['temperature_celsius', 'temperature_fahrenheit'])
        tempMedia = df[Temp].mean()

        col1, col2, col3 = st.columns(3)

        col1.metric(label=f"Média da {Temp.replace('_', ' ')}", value=f"{tempMedia:.2f}")

#Tela filtro para mostrar o clima por pais

#Tela dashboard


