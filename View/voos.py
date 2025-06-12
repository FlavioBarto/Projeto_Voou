import streamlit as st
import pandas as pd
import plotly.express as px

def evolucao_mensal_demanda_e_ocupacao(conn_voo, data_inicio, data_fim):
    query = f"""
    SELECT 
        t.ano || '-' || printf('%02d', t.mes) AS mes,
        SUM(v.rpk) AS total_rpk
    FROM voos v
    JOIN tempo t ON v.tempo_id = t.tempo_id
    WHERE 
        (t.ano > ? OR (t.ano = ? AND t.mes >= ?))
        AND
        (t.ano < ? OR (t.ano = ? AND t.mes <= ?))
    GROUP BY mes
    ORDER BY mes
    """

    params = (
        data_inicio.year, data_inicio.year, data_inicio.month,
        data_fim.year, data_fim.year, data_fim.month
    )

    df = pd.read_sql_query(query, conn_voo, params=params)

    df["total_rpk_bilhoes"] = df["total_rpk"] / 1e9

    fig = px.line(df, x="mes", y="total_rpk_bilhoes",
                  title="Evolução Mensal da Demanda (RPK)",
                  labels={"mes": "Mês", "total_rpk_bilhoes": "Demanda (em bilhões de RPK)"})

    return df, fig