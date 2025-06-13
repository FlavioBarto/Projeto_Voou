import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import streamlit as st
import io

# Nova Paleta Moderna
PALETA_CORES = {
    'verde_agua_claro': '#00B38E',
    'verde_agua_medio': '#21C5B5',
    'verde_escuro': '#349B90',
    'azul_petróleo': '#38706B',
    'cinza_escuro': '#2E4643',
    'preto_esverdeado': '#2B3332',
    'fundo': '#FFFFFF'
}

fig = None
pais_global = None

def setar_pais(pais):
    global pais_global
    pais_global = pais

def criar_view_dados_climaticos():
    """Cria a VIEW vw_dados_climaticos no banco de dados."""
    conn = sqlite3.connect('weather_database.db')
    cursor = conn.cursor()

    cursor.execute("DROP VIEW IF EXISTS vw_dados_climaticos")  # Garante recriação da view
    cursor.execute("""
        CREATE VIEW vw_dados_climaticos AS
        SELECT 
            wd.last_updated, 
            wd.temperature_celsius, 
            wd.precip_mm, 
            wd.humidity_percentage, 
            wd.gust_kph, 
            l.country, 
            wc.condition_text, 
            wd.wind_kph, 
            wd.pressure_mb
        FROM weather_data wd
        JOIN location l ON wd.location_id = l.location_id
        JOIN weather_condition wc ON wd.condition_id = wc.condition_id
    """)
    
    conn.commit()

def carregar_dados_climaticos():
    criar_view_dados_climaticos()
    """Carrega os dados a partir da VIEW vw_dados_climaticos."""
    conn = sqlite3.connect('weather_database.db')
    query = "SELECT * FROM vw_dados_climaticos"
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

    df['last_updated'] = pd.to_datetime(df['last_updated'], errors='coerce')
    df['year'] = df['last_updated'].dt.year
    df['month'] = df['last_updated'].dt.month_name()

    return df

def carregar_paises_disponiveis():
    df = carregar_dados_climaticos()
    return sorted(df['country'].dropna().unique())

def grafico_precipitacao_mensal(pais=None, ano=None):
    global fig, pais_global
    df = carregar_dados_climaticos()
    if pais is None:
        pais = pais_global if pais_global else df['country'].mode()[0]
    if ano is None:
        ano = df['year'].max()

    df_filtrado = df[(df['country'] == pais) & (df['year'] == ano)]
    precip_monthly = df_filtrado.groupby('month')['precip_mm'].sum().reindex([
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]).fillna(0).reset_index()

    fig, ax = plt.subplots(figsize=(8, 5.3))
    sns.barplot(data=precip_monthly, x='month', y='precip_mm',
                color=PALETA_CORES['verde_escuro'], ax=ax)
    ax.set_title(f"Precipitação Mensal (mm) - {pais} - {ano}",
                 color=PALETA_CORES['azul_petróleo'])
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    ax.set_facecolor(PALETA_CORES['fundo'])
    fig.patch.set_facecolor(PALETA_CORES['fundo'])
    st.pyplot(fig)

def grafico_umidade_pizza(pais=None, ano=None):
    global fig, pais_global
    df = carregar_dados_climaticos()
    if pais is None:
        pais = pais_global if pais_global else df['country'].mode()[0]
    if ano is None:
        ano = df['year'].max()
        df_filtrado = df[(df['country'] == pais) & (df['year'] == ano)]
    humidity_analysis = df_filtrado.groupby('condition_text')['humidity_percentage'].mean().reset_index()

    condicoes_desejadas = [
        'Sunny', 'Blizzard', 'Heavy Snow', 'Fog', 'Clear',
        'Heavy Rain', 'Light Rain', 'Mist', 'Moderate Rain',
        'Moderate Snow', 'Partly Cloudy', 'Cloudy'
    ]

    humidity_analysis['condition_text_clean'] = humidity_analysis['condition_text'].str.strip().str.title()
    humidity_filtered = humidity_analysis[humidity_analysis['condition_text_clean'].isin(condicoes_desejadas)]
    humidity_avg = humidity_filtered.groupby('condition_text_clean')['humidity_percentage'].mean()
    humidity_avg = humidity_avg.reindex(condicoes_desejadas).dropna()

    cores_pizza = sns.color_palette([
        PALETA_CORES['verde_agua_claro'],
        PALETA_CORES['verde_agua_medio'],
        PALETA_CORES['verde_escuro'],
        PALETA_CORES['azul_petróleo'],
        PALETA_CORES['cinza_escuro'],
        PALETA_CORES['preto_esverdeado']
    ] * 2)[:len(humidity_avg)]

    fig, ax = plt.subplots(figsize=(8, 6.3))

    def func_autopct(pct):
        return f"{pct:.1f}%"

    wedges, texts, autotexts = ax.pie(
        humidity_avg,
        labels=humidity_avg.index,
        autopct=func_autopct,
        startangle=140,
        colors=cores_pizza,
        textprops={'color': 'black'}  # labels externas em preto
    )

    # Números dentro da pizza em branco
    for autotext in autotexts:
        autotext.set_color('white')

    ax.set_title(f"Distribuição da Umidade Média por Condição Climática - {pais} {ano}",
                 color=PALETA_CORES['azul_petróleo'])
    ax.axis('equal')
    fig.patch.set_facecolor(PALETA_CORES['fundo'])
    st.pyplot(fig)

def grafico_vento_pressao(pais=None, ano=None):
    global fig, pais_global
    df = carregar_dados_climaticos()
    if pais is None:
        pais = pais_global if pais_global else df['country'].mode()[0]
    if ano is None:
        ano = df['year'].max()

    df_filtrado = df[(df['country'] == pais) & (df['year'] == ano)]
    df_filtrado['strong_gust'] = df_filtrado['gust_kph'] > 30

    fig, ax = plt.subplots(figsize=(8, 6.1))
    sns.scatterplot(
        data=df_filtrado,
        x='wind_kph',
        y='pressure_mb',
        hue='strong_gust',
        palette={
            True: PALETA_CORES['verde_agua_claro'],
            False: PALETA_CORES['cinza_escuro']
        },
        size='gust_kph',
        sizes=(20, 200),
        ax=ax
    )
    ax.set_title(f"Relação entre Vento, Pressão e Rajadas Fortes - {pais} {ano}",
                 color=PALETA_CORES['azul_petróleo'])
    ax.legend(title="Rajada > 30 km/h")
    ax.set_facecolor(PALETA_CORES['fundo'])
    fig.patch.set_facecolor(PALETA_CORES['fundo'])
    st.pyplot(fig)

def grafico_poluentes_mensal_com_selectbox():
    global pais_global
    df = consultar_dados_poluentes_pais()
    paises = sorted(df['country'].unique())
    anos = sorted(df['year'].unique(), reverse=True)
    pais_selecionado = st.selectbox("Selecione o país", paises)
    setar_pais(pais_selecionado)
    df_pais = df[df['country'].str.upper() == pais_selecionado.upper()]

    if df.empty:
        st.warning("Nenhum dado disponível.")
        return

    # Obter lista única de países e anos
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
    # Selectbox para ano
    ano = st.selectbox("Selecione o ano:", anos, index=0)

    # Filtrar dados de acordo com seleção
    df_filtrado = df[(df['country'] == pais_selecionado) & (df['year'] == ano)]

    # Lista dos poluentes
    poluentes = ['carbon_monoxide', 'ozone', 'nitrogen_dioxide', 'sulphur_dioxide']

    # Média por mês
    df_mensal = df_filtrado.groupby('month')[poluentes].mean()

    # Ordenar os meses corretamente
    meses_ordenados = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
    df_mensal = df_mensal.reindex(meses_ordenados)

    # Informações dos poluentes
    poluentes_info = [
        ('carbon_monoxide', 'Monóxido de Carbono (CO)', PALETA_CORES['verde_agua_claro']),
        ('ozone', 'Ozônio (O₃)', PALETA_CORES['verde_agua_medio']),
        ('nitrogen_dioxide', 'Dióxido de Nitrogênio (NO₂)', PALETA_CORES['verde_escuro']),
        ('sulphur_dioxide', 'Dióxido de Enxofre (SO₂)', PALETA_CORES['azul_petróleo'])
    ]

    # Criar colunas 2 a 2
    cols1 = st.columns(2)
    cols2 = st.columns(2)

    # === Gráfico 1 ===
    with cols1[0]:
        fig, ax = plt.subplots(figsize=(8, 3.5))
        ax.plot(df_mensal.index, df_mensal['carbon_monoxide'], marker='o', color=PALETA_CORES['verde_agua_claro'], label='Monóxido de Carbono (CO)')
        ax.set_title(f'Monóxido de Carbono (CO) - {pais_selecionado} - {ano}', color=PALETA_CORES['azul_petróleo'])
        ax.set_xlabel('Mês', color=PALETA_CORES['preto_esverdeado'])
        ax.set_ylabel('Concentração Média', color=PALETA_CORES['preto_esverdeado'])
        ax.tick_params(axis='x', rotation=45, colors=PALETA_CORES['preto_esverdeado'])
        ax.tick_params(axis='y', colors=PALETA_CORES['preto_esverdeado'])
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend()
        fig.patch.set_facecolor(PALETA_CORES['fundo'])
        ax.set_facecolor(PALETA_CORES['fundo'])
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        st.image(buf)

    # === Gráfico 2 ===
    with cols1[1]:
        fig, ax = plt.subplots(figsize=(8, 3.5))
        ax.plot(df_mensal.index, df_mensal['ozone'], marker='o', color=PALETA_CORES['verde_agua_medio'], label='Ozônio (O₃)')
        ax.set_title(f'Ozônio (O₃) - {pais_selecionado} - {ano}', color=PALETA_CORES['azul_petróleo'])
        ax.set_xlabel('Mês', color=PALETA_CORES['preto_esverdeado'])
        ax.set_ylabel('Concentração Média', color=PALETA_CORES['preto_esverdeado'])
        ax.tick_params(axis='x', rotation=45, colors=PALETA_CORES['preto_esverdeado'])
        ax.tick_params(axis='y', colors=PALETA_CORES['preto_esverdeado'])
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend()
        fig.patch.set_facecolor(PALETA_CORES['fundo'])
        ax.set_facecolor(PALETA_CORES['fundo'])
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        st.image(buf)

    # === Gráfico 3 ===
    with cols2[0]:
        fig, ax = plt.subplots(figsize=(8, 3.5))
        ax.plot(df_mensal.index, df_mensal['nitrogen_dioxide'], marker='o', color=PALETA_CORES['verde_escuro'], label='Dióxido de Nitrogênio (NO₂)')
        ax.set_title(f'Dióxido de Nitrogênio (NO₂) - {pais_selecionado} - {ano}', color=PALETA_CORES['azul_petróleo'])
        ax.set_xlabel('Mês', color=PALETA_CORES['preto_esverdeado'])
        ax.set_ylabel('Concentração Média', color=PALETA_CORES['preto_esverdeado'])
        ax.tick_params(axis='x', rotation=45, colors=PALETA_CORES['preto_esverdeado'])
        ax.tick_params(axis='y', colors=PALETA_CORES['preto_esverdeado'])
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend()
        fig.patch.set_facecolor(PALETA_CORES['fundo'])
        ax.set_facecolor(PALETA_CORES['fundo'])
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        st.image(buf)

    # === Gráfico 4 ===
    with cols2[1]:
        fig, ax = plt.subplots(figsize=(8, 3.5))
        ax.plot(df_mensal.index, df_mensal['sulphur_dioxide'], marker='o', color=PALETA_CORES['azul_petróleo'], label='Dióxido de Enxofre (SO₂)')
        ax.set_title(f'Dióxido de Enxofre (SO₂) - {pais_selecionado} - {ano}', color=PALETA_CORES['azul_petróleo'])
        ax.set_xlabel('Mês', color=PALETA_CORES['preto_esverdeado'])
        ax.set_ylabel('Concentração Média', color=PALETA_CORES['preto_esverdeado'])
        ax.tick_params(axis='x', rotation=45, colors=PALETA_CORES['preto_esverdeado'])
        ax.tick_params(axis='y', colors=PALETA_CORES['preto_esverdeado'])
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend()
        fig.patch.set_facecolor(PALETA_CORES['fundo'])
        ax.set_facecolor(PALETA_CORES['fundo'])
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        st.image(buf)

