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