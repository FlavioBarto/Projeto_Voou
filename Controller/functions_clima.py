import pandas as pd
import plotly.express as px
import streamlit as st
import sqlite3

# Conectar ao banco de dados
def carregar_dados_climaticos():
    conn = sqlite3.connect('weather_database.db')
    query = """
        SELECT wd.*, l.country, wc.condition_text
        FROM weather_data wd
        JOIN location l ON wd.location_id = l.location_id
        JOIN weather_condition wc ON wd.condition_id = wc.condition_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    df['last_updated'] = pd.to_datetime(df['last_updated'], errors='coerce')
    df['year'] = df['last_updated'].dt.year
    df['month'] = df['last_updated'].dt.month_name()
    return df

def carregar_paises_disponiveis():
    df = carregar_dados_climaticos()
    return sorted(df['country'].dropna().unique())

def detalhe_paises(pais):
    df = carregar_dados_climaticos()
    df_pais = df[df['country'] == pais]

    if df_pais.empty:
        st.warning(f"Nenhum dado encontrado para o país: {pais}")
        return

    temp_media = df_pais['temperature_celsius'].mean()
    ultima_temp = df_pais.sort_values('last_updated', ascending=False).iloc[0]

    cols = st.columns(4)
    with cols[0]:
        st.metric("Temperatura Média (°C)", f"{temp_media:.2f}")
    with cols[1]:
        st.metric("Última Temperatura (°C)", f"{ultima_temp['temperature_celsius']:.2f}")
    with cols[2]:
        st.metric("Condição", ultima_temp['condition_text'])
    with cols[3]:
        st.metric("Última atualização", ultima_temp['last_updated'].strftime('%Y-%m-%d %H:%M'))
# Mapa mundi com última temperatura por país
def exibir_mapa():
    df = carregar_dados_climaticos()

    # Obter o último registro de temperatura por país
    df_last = df.sort_values('last_updated').groupby('country').tail(1)

    if df_last.empty:
        st.warning("Nenhum dado disponível para exibir o mapa.")
        return

    min_temp = df_last['temperature_celsius'].min()
    max_temp = df_last['temperature_celsius'].max()

    fig = px.choropleth(
        df_last,
        locations="country",
        locationmode="country names",
        color="temperature_celsius",
        color_continuous_scale=['#4682B4', '#87CEFA', '#FFA07A', '#FF4500', '#8B0000'],
        range_color=[min_temp, max_temp],
        title="Última Temperatura Global por País (°C)"
    )
    st.plotly_chart(fig, key="mapa_exibicao")



