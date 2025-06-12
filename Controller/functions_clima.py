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

def consultar_dados_poluentes_pais():
    query = '''
        SELECT wd.last_updated,
               l.country,
               wd.temperature_celsius,
               aq.sulphur_dioxide,
               aq.nitrogen_dioxide,
               aq.ozone,
               aq.carbon_monoxide
        FROM weather_data wd
        JOIN location l ON wd.location_id = l.location_id
        JOIN air_quality aq ON wd.weather_id = aq.weather_id
    '''
    conn = sqlite3.connect("weather_database.db")
    df = pd.read_sql_query(query, conn)
    conn.close()
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
    with cols[0].container(border = True):
        st.metric("Temperatura Média (°C)", f"{temp_media:.2f}")
    with cols[1].container(border = True):
        st.metric("Última Temperatura (°C)", f"{ultima_temp['temperature_celsius']:.2f}")
    with cols[2].container(border = True):
        st.metric("Condição", ultima_temp['condition_text'])
    with cols[3].container(border = True):
        st.metric("Última atualização", ultima_temp['last_updated'].strftime('%Y-%m-%d %H:%M'))


def detalhe_climatico(pais):
    # Busca todos os dados sem filtrar na SQL
    df = consultar_dados_poluentes_pais()

    # Filtra os dados pelo país passado como parâmetro
    df_pais = df[df['country'].str.upper() == pais.upper()]

    if df_pais.empty:
        st.warning(f"Nenhum dado encontrado para o país: {pais}")
        return

    # Ordena e seleciona o registro mais recente do país
    ultima_temp = df_pais.sort_values('last_updated', ascending=False).iloc[0]

    st.subheader("🧪 Níveis de Poluentes (Última Medição)")
    cols_pol = st.columns(4)

    with cols_pol[0].container(border=True):
        st.metric("Monóxido de Carbono (CO)", f"{ultima_temp['carbon_monoxide']:.2f}")
    with cols_pol[1].container(border=True):
        st.metric("Ozônio (O₃)", f"{ultima_temp['ozone']:.2f}")
    with cols_pol[2].container(border=True):
        st.metric("Dióxido de Nitrogênio (NO₂)", f"{ultima_temp['nitrogen_dioxide']:.2f}")
    with cols_pol[3].container(border=True):
        st.metric("Dióxido de Enxofre (SO₂)", f"{ultima_temp['sulphur_dioxide']:.2f}")



def mes_temp():
    df = carregar_dados_climaticos()
    df['last_updated'] = pd.to_datetime(df['last_updated'])
    df['mes_ano'] = df['last_updated'].dt.to_period('M').astype(str)

    # Obter lista única de meses disponíveis
    meses = sorted(df['mes_ano'].unique(), reverse=True)

    # Filtro para o mês
    mes = st.selectbox("Selecione o mês:", meses)

    # Filtrar os dados para o mês selecionado
    df_mes = df[df['mes_ano'] == mes]

    # Calcular a média de temperatura por país
    df_media = df_mes.groupby('country', as_index=False)['temperature_celsius'].mean()

    if df_media.empty:
        st.warning("Nenhum dado disponível para o mês selecionado.")
        return

    min_temp = df_media['temperature_celsius'].min()
    max_temp = df_media['temperature_celsius'].max()

    # Criar o mapa
    fig = px.choropleth(
        df_media,
        locations="country",
        locationmode="country names",
        color="temperature_celsius",
        color_continuous_scale=['#4682B4', '#87CEFA', '#FFA07A', '#FF4500', '#8B0000'],
        range_color=[min_temp, max_temp],
        title=f"Média de Temperatura Global por País ({mes}) (°C)"
    )

    fig.update_layout(width=1200, height=600)
    
    st.plotly_chart(fig, key="mapa_exibicao")
    

