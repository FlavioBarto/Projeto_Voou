import pandas as pd
import streamlit as st
import plotly.express as px

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
    
    # Criar o gráfico
    fig = px.bar(
        df_sazonal,
        x='mes',
        y=metrica,
        barmode='group',
        labels={
            'mes': 'Mês',
            metrica: names.get(metrica, metrica),
        },
        text_auto=True,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig.update_layout(
        title=f'Quantidade de {names.get(metrica)} por Mês',
        xaxis={'type': 'category'},
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    st.plotly_chart(fig, use_container_width=True)

