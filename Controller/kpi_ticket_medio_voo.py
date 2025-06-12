import pandas as pd

def exibir_ticket_medio_voo(conn_voo, data_inicio, data_fim):
    query_ticket_medio = f"""SELECT ROUND(AVG(total_preco_passagem_por_passageiro), 2) AS ticket_medio_passagem
                            FROM (
                                SELECT 
                                    v.voo_id,
                                    ROUND(
                                        CASE 
                                            WHEN v.distancia_voada_km IS NULL OR v.distancia_voada_km = 0 THEN 0
                                            ELSE (v.rpk / v.distancia_voada_km)
                                        END,
                                        2
                                    ) AS total_preco_passagem_por_passageiro
                                FROM voo v
                                JOIN tempo t ON t.tempo_id = v.tempo_id
                                WHERE t.ano BETWEEN {data_inicio.year} AND {data_fim.year}
                                AND t.mes BETWEEN {data_inicio.month} AND {data_fim.month}
                            )
                        """
    
    df_ticket_medio = pd.read_sql_query(query_ticket_medio, conn_voo)

    valor_ticket_medio = df_ticket_medio.iloc[0, 0]
    
    return valor_ticket_medio

