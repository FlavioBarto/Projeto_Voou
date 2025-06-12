import streamlit as st
import sqlite3
import os
import datetime
from Model.criar_bd_clima import csv_to_sqlite_clima
from Model.criar_bd_voos import csv_to_sqlite_voo
from Controller.functions_voos import total_passageiros_pagos
from Controller.kpi_media_assentos import exibir_kpi_media_assentos
from Controller.functions_voos import taxa_media_ocupacao
from Controller.kpi_ticket_medio_voo import exibir_ticket_medio_voo
from Controller.functions_clima import detalhe_paises
from View.clima import grafico_poluentes_mensal_com_selectbox
from Controller.functions_clima import mes_temp

from Controller.grafico_sazonalidade import exibir_dados_volume_passageiros_rota
from Controller.grafico_sazonalidade import plot_barras_sazonalidade
from Controller.grafico_top_visitas import exibir_dados_total_viagens
from Controller.grafico_top_visitas import plot_pizza_paises_mais_visitados
from View.voos import evolucao_mensal_demanda_e_ocupacao
from View.clima import grafico_precipitacao_mensal
from View.clima import grafico_umidade_pizza
from View.clima import grafico_vento_pressao
from View.clima import setar_pais
from View.clima import carregar_paises_disponiveis

def set_page_config():
    st.set_page_config(
        page_title="Sistema de Controle",
        page_icon="💾",
        layout="wide"
    )

def load_css():
    try:
        with open("assets/style.css", "r", encoding='utf-8') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Arquivo CSS não encontrado")
    except Exception as e:
        st.error(f"Erro ao carregar CSS: {str(e)}")

try:
    conn_voo = sqlite3.connect("voos_database.db")
    cursor_voo = conn_voo.cursor()

    conn_clima = sqlite3.connect("weather_database.db")
    cursor_clima = conn_clima.cursor()
except Exception as e:
    st.error(f"Erro ao conectar aos bancos de dados: {str(e)}")
    st.stop()

def init_db():
    db_files = ["voos_database.db", "weather_database.db"]

    if not all(os.path.exists(db_file) for db_file in db_files) or "db_initialized" not in st.session_state:
        try:
            with st.spinner("Inicializando banco de dados..."):
                csv_to_sqlite_clima(conn_clima, cursor_clima)
                csv_to_sqlite_voo(conn_voo, cursor_voo)
                st.session_state.db_initialized = True
                st.toast("Bancos de dados inicializados com sucesso!", icon="✅")
        except Exception as e:
            st.error(f"Erro ao inicializar bancos de dados: {str(e)}")
            st.stop()

def formatar_numero(numero):
    if numero >= 1_000_000:
        return f"{numero / 1_000_000:.1f}M"
    elif numero >= 1_000:
        return f"{numero / 1_000:.1f}K"
    else:
        return str(numero)

def main():
    set_page_config()
    load_css()

    init_db()

    with st.sidebar:
        st.title("📊 Análises")

        if "menu_ativo" not in st.session_state:
            st.session_state.menu_ativo = "Clima"
        
        if st.sidebar.button("☀️ Dashboard Clima", type="tertiary"):
            st.session_state.menu_ativo = "Clima"
        if st.sidebar.button("✈️ Dashboard Voos", type="tertiary"):
            st.session_state.menu_ativo = "Voos"
       
        if st.session_state.menu_ativo == "Voos":
            st.header("⚙️ Filtros")

            ano_mes_max = cursor_voo.execute("""
                SELECT MAX(ano), 
                    (SELECT MAX(mes) FROM tempo WHERE ano = (SELECT MAX(ano) FROM tempo))
                FROM tempo
            """).fetchone()

            ano_max_voo_int, mes_max_voo_int = ano_mes_max

            ano_mes_min = cursor_voo.execute("""
                SELECT MIN(ano), 
                    (SELECT MIN(mes) FROM tempo WHERE ano = (SELECT MIN(ano) FROM tempo))
                FROM tempo
            """).fetchone()

            ano_min_voo_int, mes_min_voo_int = ano_mes_min

            data_inicio = datetime.datetime(year=ano_min_voo_int, month=mes_min_voo_int, day=1)
            data_fim = datetime.datetime(year=ano_max_voo_int, month=mes_max_voo_int, day=1)

            if "data_inicio" not in st.session_state:
                st.session_state.data_inicio = data_inicio

            if "data_fim" not in st.session_state:
                st.session_state.data_fim = data_fim

            periodo_selecionado = st.date_input("Selecione o período desejado:", [data_inicio, data_fim], min_value=data_inicio, max_value=data_fim)

            if len(periodo_selecionado) == 2:
                st.session_state.data_inicio, st.session_state.data_fim = periodo_selecionado

    menu = st.session_state.menu_ativo

    if menu == "Clima":
        st.header("📈 Dashboard Clima - Principais Indicadores", divider="grey")
        aba_graficos, aba_detalhe_clima, aba_mapa_calor = st.tabs(["🌍 Filtro por País", "🌦️ Detalhe Clima", "🗺️ Mapa Mundi"])

        with aba_graficos:
            paises = carregar_paises_disponiveis()
            pais_selecionado = st.selectbox("Selecione o país", paises, key="selectbox_pais_graficos")
            setar_pais(pais_selecionado)
            detalhe_paises(pais_selecionado)

            cols = st.columns(3)
            with cols[0].container(border=True):
                grafico_precipitacao_mensal()
            with cols[1].container(border=True):
                grafico_umidade_pizza()
            with cols[2].container(border=True):
                grafico_vento_pressao()

        with aba_mapa_calor:
            mes_temp()

        with aba_detalhe_clima:
            
            grafico_poluentes_mensal_com_selectbox()


    if menu == "Voos":
        st.header("✈️ Dashboard ANAC - Voos Brasileiros", divider="grey")
        
        data_inicio = st.session_state.data_inicio
        data_fim = st.session_state.data_fim

        try:
            passageiros_pagos = total_passageiros_pagos(conn_voo, data_inicio, data_fim)
            porcentagem_media_assentos_cheios = exibir_kpi_media_assentos(conn_voo, data_inicio, data_fim)
            media_taxa_ocupacao = taxa_media_ocupacao(conn_voo, data_inicio, data_fim)
            ticket_medio_voo = exibir_ticket_medio_voo(conn_voo, data_inicio, data_fim)
            demanda_e_ocupacao = evolucao_mensal_demanda_e_ocupacao(conn_voo, data_inicio, data_fim)

        except Exception as e:
            st.error(f"Erro ao calcular os KPIs: {str(e)}")
            passageiros_pagos = 0

        cols = st.columns(4)
        with cols[0]:
            total_passageiros_pagos_formatado = formatar_numero(passageiros_pagos)
            st.metric(label="Total de Passageiros Pagos", value=total_passageiros_pagos_formatado)
        with cols[1]:
            st.metric(label="Assentos Ocupados Por Voo",
                      value=f"{porcentagem_media_assentos_cheios:.2f}%",
                      help="Porcentagem de Assentos Ocupados por Voos")
        with cols[2]:
            st.metric("Taxa Média Ocupação", f"{media_taxa_ocupacao:.2f}%")
        with cols[3]:
            st.metric(label="Ticket Médio dos Voos",
                      value=f"R$ {ticket_medio_voo}",
                      help="Ticket Médio de Todos os Voos")

        try:
            df_sazonal = exibir_dados_volume_passageiros_rota(conn_voo, data_inicio, data_fim)
            df_paises = exibir_dados_total_viagens(conn_voo, data_inicio, data_fim)
            demanda_e_ocupacao = evolucao_mensal_demanda_e_ocupacao(conn_voo, data_inicio, data_fim)
        except Exception as e:
            st.error(f"Erro ao calcular os gráficos: {str(e)}")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.pyplot(demanda_e_ocupacao)
        with col2:
            plot_pizza_paises_mais_visitados(df_paises)
        with col3:
            plot_barras_sazonalidade(df_sazonal)


if __name__ == "__main__":
    main()