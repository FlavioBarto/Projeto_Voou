import pandas as pd

def total_passageiros_pagos(conn_voo, data_inicio, data_fim):
    query = f"""
    SELECT passageiros_pagos FROM voo v
    JOIN tempo t ON t.tempo_id = v.tempo_id
    WHERE t.ano BETWEEN {data_inicio.year} AND {data_fim.year}
    AND t.mes BETWEEN {data_inicio.month} AND {data_fim.month}
    """
    
    df_passageiros_pagos = pd.read_sql_query(query, conn_voo)
    total = df_passageiros_pagos['passageiros_pagos'].sum() if 'passageiros_pagos' in df_passageiros_pagos else 0 
    return total

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
    
    return media_porcentagem_assentos_ocupados_periodo

def taxa_media_ocupacao(conn_voo, data_inicio, data_fim):
    query = f"""
    SELECT ROUND((SUM(v.rpk) / SUM(v.ask) * 100), 2) as taxa_ocupacao
    FROM voo v
    JOIN tempo t ON t.tempo_id = v.tempo_id
    WHERE t.ano BETWEEN {data_inicio.year} AND {data_fim.year}
    AND t.mes BETWEEN {data_inicio.month} AND {data_fim.month} 
    AND v.rpk IS NOT NULL
    AND v.rpk > 0
    AND v.ask IS NOT NULL
    AND v.ask > 0
    """

    df_taxa_media_ocupacao = pd.read_sql_query(query, conn_voo).iloc[0, 0]
    return df_taxa_media_ocupacao

def exibir_ticket_medio_voo(conn_voo, data_inicio, data_fim):
    query_ticket_medio = f"""SELECT ROUND(AVG(total_preco_passagem_por_passageiro), 2) AS ticket_medio_passagem
                                FROM (
                                    SELECT 
                                        v.voo_id,
                                        ROUND(
                                            CASE 
                                                WHEN v.distancia_voada_km IS NULL OR v.distancia_voada_km = 0 THEN NULL
                                                ELSE (v.rpk / v.distancia_voada_km)
                                            END,
                                            2
                                        ) AS total_preco_passagem_por_passageiro
                                    FROM voo v
                                    JOIN tempo t ON t.tempo_id = v.tempo_id
                                    WHERE t.ano BETWEEN {data_inicio.year} AND {data_fim.year}
                                    AND t.mes BETWEEN {data_inicio.month} AND {data_fim.month}
                                ) AS sub
                                WHERE total_preco_passagem_por_passageiro IS NOT NULL AND total_preco_passagem_por_passageiro != 0
                        """
    
    df_ticket_medio = pd.read_sql_query(query_ticket_medio, conn_voo)

    valor_ticket_medio = df_ticket_medio.iloc[0, 0]
    
    return valor_ticket_medio