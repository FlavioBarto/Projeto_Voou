import pandas as pd

def faturamento_passagens_passageiros(conn_voo, data_hoje, data_fim):
    passagens = pd.read_sql_query(f"""SELECT * FROM voo v
                                  JOIN tempo t ON t.tempo_id = v.tempo_id
                                  WHERE t.ano BETWEEN {data_hoje.year} AND {data_fim.year}
                                  AND t.mes BETWEEN {data_hoje.month} AND {data_fim.month}""", conn_voo)
    
    print(passagens)
    
    