import pandas as pd
import streamlit as st

def exibir_kpi_media_assentos(conn_voo, data_inicio, data_fim):
    query_porcentagem = f"""SELECT 
                            v.voo_id,
                            (v.passageiros_pagos + v.passageiros_gratis) AS total_passageiros,
                            v.assentos,
                            ROUND(
                                CASE 
                                    WHEN v.assentos IS NULL OR v.assentos = 0 THEN 0
                                    ELSE (v.passageiros_pagos + v.passageiros_gratis) * 100.0 / v.assentos
                                END,
                                2
                            ) AS percentual_ocupado
                        FROM voo v
                        JOIN tempo t ON t.tempo_id = v.tempo_id
                        WHERE t.ano BETWEEN {data_inicio.year} AND {data_fim.year}
                        AND t.mes BETWEEN {data_inicio.month} AND {data_fim.month}
                        """
    
    df_porcentagem_assentos_ocupados = pd.read_sql_query(query_porcentagem, conn_voo)

    media_porcentagem_assentos_ocupados_periodo = df_porcentagem_assentos_ocupados["percentual_ocupado"].mean()
    
    st.metric(label="Porcentagem", value=f"{media_porcentagem_assentos_ocupados_periodo:.2f}%", help="Porcentagem da média de ocupação de voos")
