import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import geopandas as gpd

st.set_page_config(layout="wide")
st.title("✈️ Dashboard ANAC - Voos Brasileiros")

# Conexão com banco
conn = sqlite3.connect("voos_database.db")

@st.cache_data
def carregar_voos():
    query = """
    SELECT v.voo_id, ea.nome AS empresa, ea.nacionalidade, ao.nome AS origem, 
    ao.pais AS pais_origem, ao.uf AS uf_origem, ad.nome AS destino,
    ad.pais AS pais_destino, ad.uf AS uf_destino, t.ano, t.mes, 
    v.natureza, v.grupo_voo, v.ask, v.rpk, v.atk, v.rtk,
    v.distancia_voada_km, v.horas_voadas, v.assentos, v.bagagem_kg,
    v.passageiros_pagos, v.passageiros_gratis, v.carga_paga_kg,
    v.carga_gratis_kg, v.combustivel_litros FROM VOO v
    JOIN EMPRESA_AEREA ea ON v.empresa_id = ea.empresa_id
    JOIN AEROPORTO ao ON v.aeroporto_origem_id = ao.aeroporto_id
    JOIN AEROPORTO ad ON v.aeroporto_destino_id = ad.aeroporto_id
    JOIN TEMPO t ON v.tempo_id = t.tempo_id
    """
    return pd.read_sql_query(query, conn)

df = carregar_voos()

# Filtros
st.sidebar.header("Filtros")
empresas = st.sidebar.multiselect("Empresa", df['empresa'].unique())
anos = st.sidebar.multiselect("Ano", sorted(df['ano'].unique()))
meses = st.sidebar.multiselect("Mês", sorted(df['mes'].unique()))

if empresas:
    df = df[df['empresa'].isin(empresas)]
if anos:
    df = df[df['ano'].isin(anos)]
if meses:
    df = df[df['mes'].isin(meses)]

# Métricas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Voos", len(df))
col2.metric("Distância Total Voada (km)", f"{df['distancia_voada_km'].sum():,.0f}")
col3.metric("Assentos Disponibilizados", f"{df['assentos'].sum():,}")
col4.metric("Bagagem Transportada (kg)", f"{df['bagagem_kg'].sum():,.0f}")

st.markdown("---")

# Tabela
st.subheader(":bar_chart: Tabela de Dados Filtrados")
st.dataframe(df, use_container_width=True)

st.markdown("---")

# Gráfico de barras com matplotlib
st.subheader(":airplane: Assentos por Empresa")
assentos_empresa = df.groupby("empresa")["assentos"].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(10, 5))
assentos_empresa.plot(kind="bar", ax=ax, color="skyblue")
ax.set_title("Assentos Oferecidos por Empresa")
ax.set_ylabel("Assentos")
ax.set_xlabel("Empresa")
plt.xticks(rotation=45, ha="right")
st.pyplot(fig)

# Mapa com rotas simuladas usando GeoPandas (sem coordenadas reais)
st.subheader(":earth_africa: Mapa Simulado de Rotas (sem coordenadas reais)")

# Mapa base
world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
fig2, ax2 = plt.subplots(figsize=(12, 6))
world.plot(ax=ax2, color="lightgrey", edgecolor="black")

# Simulando rotas com códigos fictícios
rotas = df[['origem', 'destino']].drop_duplicates()
for _, row in rotas.iterrows():
    x = [hash(row['origem']) % 360 - 180, hash(row['destino']) % 360 - 180]
    y = [hash(row['origem']) % 180 - 90, hash(row['destino']) % 180 - 90]
    ax2.plot(x, y, color="blue", alpha=0.3)

ax2.set_title("Rotas Aéreas Simuladas (sem coordenadas reais)")
st.pyplot(fig2)

conn.close()