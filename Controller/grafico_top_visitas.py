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
    df_top = df_paises.head(top_n).copy()
    outros_passageiros = df_paises['total_passageiros'][top_n:].sum()
    
    if outros_passageiros > 0:
        df_top = pd.concat([
            df_top,
            pd.DataFrame([{
                'pais_destino': 'Outros',
                'total_passageiros': outros_passageiros,
                'total_voos': df_paises['total_voos'][top_n:].sum()
            }])
        ])

    # Criar o gráfico de pizza com rosca
    fig = px.pie(
        df_top,
        names='pais_destino',
        values='total_passageiros',
        hole=0.3,  # Cria o efeito de rosca
        title=f'Distribuição de Passageiros por País (Top {top_n})',
        hover_data=['total_voos'],
        labels={
            'pais_destino': 'País',
            'total_passageiros': 'Passageiros',
            'total_voos': 'Voos'
        },
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    # Ajustes de layout
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        texttemplate='%{label}<br>%{percent:.1%}',
        hovertemplate=(
            '<b>%{label}</b><br>' +
            'Passageiros: %{value:,.0f}<br>' +
            'Voos: %{customdata[0]:,.0f}<br>' +
            'Participação: %{percent:.1%}'
        ),
        marker=dict(line=dict(color='#FFFFFF', width=1)))
    
    fig.update_layout(
        uniformtext_minsize=10,
        uniformtext_mode='hide',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
