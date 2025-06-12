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