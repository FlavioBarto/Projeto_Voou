import streamlit as st
import pandas as pd
import plotly.express as px

def evolucao_mensal_demanda_e_ocupacao(conn_voo, data_inicio, data_fim):
    query = f"""
    SELECT 
        t.ano AS ano,
        t.mes AS mes,
        SUM(v.rpk) AS total_rpk
    FROM voo v
    JOIN tempo t ON v.tempo_id = t.tempo_id
    WHERE 
        (t.ano > ? OR (t.ano = ? AND t.mes >= ?))
        AND
        (t.ano < ? OR (t.ano = ? AND t.mes <= ?))
    GROUP BY t.ano, t.mes
    ORDER BY t.ano, t.mes
    """

    params = (
        data_inicio.year, data_inicio.year, data_inicio.month,
        data_fim.year, data_fim.year, data_fim.month
    )

    df = pd.read_sql_query(query, conn_voo, params=params)

    df['data'] = pd.to_datetime(df['ano'].astype(str) + '-' + df['mes'].astype(str).str.zfill(2) + '-01')
    df["total_rpk_bilhoes"] = df["total_rpk"] / 1e9

    fig = px.line(
        df, 
        x="data", 
        y="total_rpk_bilhoes",
        title="Evolução Mensal da Demanda (RPK)",
        labels={'data': 'Mês', 'total_rpk_bilhoes': 'Demanda (Bilhões de RPK)'},
        markers=True
    )

    fig.update_layout(
        title_font=dict(size=24),
        
        xaxis=dict(
            tickformat="%b %Y",
            title_font=dict(size=20),
            tickfont=dict(size=16)
        ),

        yaxis=dict(
            title_font=dict(size=20),
            tickfont=dict(size=16)
        )
    )
    
    return df, fig

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

def exibir_dados_volume_passageiros_rota(conn_voo, data_inicio, data_fim):
    query_volume_passageiros = f"""SELECT v.voo_id, t.ano, t.mes, v.passageiros_pagos, v.decolagens, v.rpk, v.ask FROM voo v
                                    JOIN tempo t ON t.tempo_id = v.tempo_id
                                    WHERE t.ano BETWEEN {data_inicio.year} AND {data_fim.year}
                                    AND t.mes BETWEEN {data_inicio.month} AND {data_fim.month}
                                """
    
    df_porcentagem_assentos_ocupados = pd.read_sql_query(query_volume_passageiros, conn_voo)

    df_sazonal = df_porcentagem_assentos_ocupados.groupby(["ano", "mes"]).agg({
        "passageiros_pagos": "sum",
        "decolagens": "count",
        "rpk": "sum",
        "ask": "sum"
    }).reset_index()

    df_sazonal["ocupacao"] = df_sazonal["rpk"] / df_sazonal["ask"]
    
    return df_sazonal

def plot_barras_sazonalidade(df_sazonal, metrica="passageiros_pagos"):
    names = {
        'passageiros_pagos': 'Passageiros Pagos',
        'ocupacao': 'Taxa de Ocupação (%)',
        'decolagens': 'Número de Decolagens'
    }
    
    df_sazonal['texto_formatado'] = (df_sazonal[metrica] / 1e6).map("{:.1f}M".format)

    # Criar o gráfico
    fig = px.bar(
        df_sazonal,
        x='mes',
        y=metrica,
        text='texto_formatado',
        barmode='group',
        labels={
            'mes': 'Mês',
            metrica: names.get(metrica, metrica),
        },
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    fig.update_traces(
        textfont=dict(
            family='Impact',
            size=16,
            color='black'
        ),
        textposition='inside'
    )
    
    fig.update_layout(
        title=f'{names.get(metrica)} por Mês',
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        width=400,
        height=500,
        title_font=dict(size=24),

        xaxis=dict(
            {'type': 'category'},
            title_font=dict(size=20),
            tickfont=dict(size=16)
        ),

        yaxis=dict(
            title_font=dict(size=20),
            tickfont=dict(size=16)
        ),

        legend=dict(
            font=dict(
                family="Impact", 
                size=14, 
                color="black"
            )
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)