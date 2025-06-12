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

def taxa_media_ocupacao(conn_voo):
    query = """
    SELECT (v.assentos * v.distancia_voada_km) / (v.passageiros_pagos * v.distancia_voada_km)
    FROM voo v
    """

    df_taxa_media_ocupacao = pd.read_sql_query(query, conn_voo).iloc[0, 0]
    return df_taxa_media_ocupacao
    
    