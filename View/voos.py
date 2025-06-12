import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def evolucao_mensal_demanda_e_ocupacao(conn_voo, data_inicio, data_fim):
    query = f"""
    SELECT SUM(v.rpk) AS total_rpk,
    ROUND((SUM(v.rpk) / NULLIF(SUM(v.ask), 0) * 100), 2) AS taxa_ocupacao,
    t.ano, t.mes
    FROM voo v
    JOIN tempo t
    WHERE t.ano BETWEEN {data_inicio.year} AND {data_fim.year}
    AND t.mes BETWEEN {data_inicio.month} AND {data_fim.month} 
    GROUP BY t.ano, t.mes
    ORDER BY t.ano, t.mes
    """

    df_evolucao_mensal_demanda_e_ocupacao = pd.read_sql_query(query, conn_voo)

    df_evolucao_mensal_demanda_e_ocupacao['data'] = pd.to_datetime(df_evolucao_mensal_demanda_e_ocupacao['ano'].astype(str) + '-' + df_evolucao_mensal_demanda_e_ocupacao['mes'].astype(str) + '-01')
    
    fig, ax1 = plt.subplots(figsize=(10,8))

    sns.lineplot(data=df_evolucao_mensal_demanda_e_ocupacao, x='data', y='total_rpk', label='Demanda (RPK)', ax=ax1, color='blue')
    ax1.set_ylabel("RPK Total", color="blue")
    ax1.tick_params(axis='y', labelcolor='blue')
    
    ax2 = ax1.twinx()
    sns.lineplot(data=df_evolucao_mensal_demanda_e_ocupacao, x='data', y='taxa_ocupacao', label='Taxa de Ocupação (%)', ax=ax2, color='green')
    ax2.set_ylabel("Taxa de Ocupação (%)", color="green")
    ax2.tick_params(axis='y', labelcolor='green')

    plt.title("Evolução Mensal da Demanda (RPK) e Taxa de Ocupação", fontsize=25)
    ax1.set_xlabel('Mês')
    plt.tight_layout()

    return fig