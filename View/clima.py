import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def mostrar_dados(df):
    """Exibe dataframe com colunas selecionadas"""
    df_Colunas = df[['country', 'location_name', 'latitude', 'longitude', 'last_updated', 
                     'temperature_celsius', 'temperature_fahrenheit', 'timezone', 'condition_text']]
    st.dataframe(df_Colunas)
    
df = pd.read_csv('C:/Users/Aluno/Desktop/Projeto_Voou-1/arquivos_csv/GlobalWeatherRepository.csv', sep=',', encoding='utf-8')
df['last_updated'] = pd.to_datetime(df['last_updated'])
df['year'] = df['last_updated'].dt.year
df['month'] = df['last_updated'].dt.month_name()

def mapa_mundi(df, temp_col):
    """Exibe métrica da média da temperatura global"""
    tempMedia = df[temp_col].mean()
    col1, col2, col3 = st.columns(3)
    col1.metric(label=f"Média da {temp_col.replace('_', ' ')}", value=f"{tempMedia:.2f}")

def dashboard_precipitacao(df_filtrado, pais, ano):
    """Gráfico de precipitação mensal filtrado por país e ano"""
    precip_monthly = df_filtrado.groupby(['month'])['precip_mm'].sum().reset_index()

    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=precip_monthly,
        x='month',
        y='precip_mm',
        palette='Blues'
    )
    plt.title(f"Precipitação Mensal (mm) - {pais} - {ano}")
    plt.xticks(rotation=45)
    st.pyplot(plt.gcf())
    plt.close()

def dashboard_umidade_pizza(df_filtrado, pais, ano):
    """Gráfico de pizza da umidade média por condição climática filtrado"""
    humidity_analysis = df_filtrado.groupby('condition_text')['humidity'].mean().sort_values(ascending=False).reset_index()

    condicoes_desejadas = [
        'Sunny', 'Blizzard', 'Heavy Snow', 'Fog', 'Clear', 
        'Heavy Rain', 'Light Rain', 'Mist', 'Moderate Rain', 
        'Moderate Snow', 'Partly Cloudy', 'Cloudy'
    ]

    humidity_analysis['condition_text_clean'] = humidity_analysis['condition_text'].str.strip().str.title()
    humidity_filtered = humidity_analysis[humidity_analysis['condition_text_clean'].isin(condicoes_desejadas)]
    humidity_avg = humidity_filtered.groupby('condition_text_clean')['humidity'].mean()
    humidity_avg = humidity_avg.reindex(condicoes_desejadas).dropna()

    plt.figure(figsize=(8, 8))
    plt.pie(
        humidity_avg,
        labels=humidity_avg.index,
        autopct='%1.1f%%',
        startangle=140,
        colors=plt.cm.viridis(range(len(humidity_avg)))
    )
    plt.title(f"Distribuição da Umidade Média por Condição Climática (Filtrada) - {pais} {ano}")
    plt.axis('equal')
    st.pyplot(plt.gcf())
    plt.close()

def dashboard_vento_pressao_scatter(df_filtrado, pais, ano):
    """Gráfico scatter plot entre vento, pressão e rajadas fortes"""
    df_filtrado['strong_gust'] = df_filtrado['gust_kph'] > 30

    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=df_filtrado,
        x='wind_kph',
        y='pressure_mb',
        hue='strong_gust',
        palette={True: 'red', False: 'green'},
        size='gust_kph',
        sizes=(20, 200)
    )
    plt.title(f"Relação entre Vento, Pressão e Rajadas Fortes - {pais} {ano}")
    plt.legend(title="Rajada > 30 km/h")
    st.pyplot(plt.gcf())
    plt.close()

# --- BLOCO DE SELEÇÃO DE FILTROS COM STREAMLIT ---
pais = st.sidebar.selectbox("Selecione o país:", df['country'].unique())
anos_disponiveis = df[df['country'] == pais]['year'].unique()
ano = st.sidebar.selectbox("Selecione o ano:", sorted(anos_disponiveis))

# Filtrar dados para o país e ano selecionados
df_filtrado = df[(df['country'] == pais) & (df['year'] == ano)]

st.write(f"Quantidade de linhas após filtro para {pais} em {ano}: {len(df_filtrado)}")

if len(df_filtrado) == 0:
    st.warning("Nenhum dado disponível para a combinação selecionada.")
else:
    # ============================ ⬇️ BLOCO DESTACADO – CHAMADA DOS GRÁFICOS ⬇️ ============================ #
    # ⛔️ ATENÇÃO: Este bloco chama os gráficos para exibir no Streamlit.
    # ⚠️ Remova este bloco após organizar as chamadas no main.py

    dashboard_precipitacao(df_filtrado, pais, ano)
    dashboard_umidade_pizza(df_filtrado, pais, ano)
    dashboard_vento_pressao_scatter(df_filtrado, pais, ano)
    # ============================ ⬆️ FIM DO BLOCO DESTACADO – PODE REMOVER ⬆️ ============================ #


