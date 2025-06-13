import pandas as pd
import plotly.express as px
import streamlit as st

def exibir_dados_total_viagens(conn_voo, data_inicio, data_fim):
    query = f"""
    SELECT 
        a.pais AS pais_destino,
        COUNT(v.voo_id) AS total_voos,
        SUM(v.passageiros_pagos + v.passageiros_gratis) AS total_passageiros 
    FROM voo v
    JOIN AEROPORTO a ON a.aeroporto_id = v.aeroporto_destino_id
    JOIN TEMPO t ON t.tempo_id = v.tempo_id
    WHERE t.ano BETWEEN {data_inicio.year} AND {data_fim.year}
    AND t.mes BETWEEN {data_inicio.month} AND {data_fim.month}
    GROUP BY a.pais
    ORDER BY total_passageiros DESC
    """
    return pd.read_sql_query(query, conn_voo)

def plot_pizza_paises_mais_visitados(df_paises, top_n=10):
    # 1. Filtrar para excluir o Brasil
    df_sem_brasil = df_paises[df_paises['pais_destino'] != 'BRASIL'].copy()
    
    # 2. Selecionar top N e agrupar o restante como "Outros"
    df_top = df_sem_brasil.head(top_n)
    df_top.loc[df_top["pais_destino"] == "ESTADOS UNIDOS DA AMÉRICA", "pais_destino"] = "EUA"

    # 3. Criar gráfico sem legenda
    fig = px.pie(
        df_top,
        names='pais_destino',
        values='total_passageiros',
        title=f'Top {top_n} Países Mais Visitados',
        labels={'pais_destino': 'País'},
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    # 4. Remover legenda e ajustar labels
    fig.update_traces(
        textposition='outside',
        textinfo='percent+label',
        textfont_size=16,
        marker=dict(line=dict(color='white', width=1)),
        hovertemplate="<b>%{label}</b><br>%{percent:.1%}<br>%{value:,.0f} passageiros",
        showlegend=False  # Isso remove a legenda
    )
    
    # 5. Centralizar título
    fig.update_layout(
        title_x=0,
        height=500,
        uniformtext_minsize=12,
        uniformtext_mode='hide',
        title_font=dict(size=24)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
