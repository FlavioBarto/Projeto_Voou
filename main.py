import streamlit as st
import sqlite3
import os
from Model.criar_bd_clima import csv_to_sqlite_clima
from Model.criar_bd_voos import csv_to_sqlite_voo

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

def init_db():
    db_files = ["voos_database.db", "weather_database.db"]

    if not all(os.path.exists(db_file) for db_file in db_files) or "db_initialized" not in st.session_state:
        try:
            with st.spinner("Inicializando banco de dados..."):
                csv_to_sqlite_clima()
                csv_to_sqlite_voo()
                st.session_state.db_initialized = True
                st.toast("Bancos de dados inicializados com sucesso!", icon="✅")
        except Exception as e:
            st.error(f"Erro ao inicializar bancos de dados: {str(e)}")
            st.stop()

def main():
    set_page_config()
    load_css()

    init_db()

    try:
        conn_voo = sqlite3.connect("voos_database.db")
        cursor_voo = conn_voo.cursor()

        conn_clima = sqlite3.connect("weather_database.db")
        cursor = conn_clima.cursor()
    except Exception as e:
        st.error(f"Erro ao conectar aos bancos de dados: {str(e)}")
        st.stop()

    with st.sidebar:
        st.title("📊 Análises")

        if "menu_ativo" not in st.session_state:
            st.session_state.menu_ativo = "Clima"
        
        if st.sidebar.button("☀️ Dashboard Clima", type="tertiary"):
            st.session_state.menu_ativo = "Clima"
        if st.sidebar.button("✈️ Dashboard Voos", type="tertiary"):
            st.session_state.menu_ativo = "Voos"
        
        # TODO: Inserir Filtros para cada Dashboard
        st.header("⚙️ Filtros")

        if 'filtros_resetados' not in st.session_state:
            st.session_state.filtros_resetados = False

        cols = st.columns(2)
        if st.session_state.filtros_resetados:
            # TODO: Inserir Filtro para Dashboard de Clima
            if st.session_state.menu_ativo == "Clima":
                cols = st.columns(2)
                with cols[0]:
                    st.write("Filtro 1 padrão")
                with cols[1]:
                    st.write("Filtro 2 padrão")

                cols = st.columns(2)
                with cols[0]:
                    st.write("Filtro 3 padrão")
                with cols[1]:
                    st.write("Filtro 4 padrão")
                    
            st.session_state.filtros_resetados = False
        else:
            if st.session_state.menu_ativo == "Clima":
                cols = st.columns(2)
                with cols[0]:
                    st.write("Filtro 1 para mexer")
                with cols[1]:
                    st.write("Filtro 2 para mexer")

                cols = st.columns(2)
                with cols[0]:
                    st.write("Filtro 3 para mexer")
                with cols[1]:
                    st.write("Filtro 4 para mexer")
        
            if st.session_state.menu_ativo == "Voos":
                cols = st.columns(2)
                with cols[0]:
                    st.write("Filtro 1 para mexer")
                with cols[1]:
                    st.write("Filtro 2 para mexer")

                cols = st.columns(2)
                with cols[0]:
                    st.write("Filtro 3 para mexer")
                with cols[1]:
                    st.write("Filtro 4 para mexer")
        
        reset_filtros = st.button(
            "🔄 Resetar Filtros", type="secondary")
        
        if reset_filtros:
            st.session_state.filtros_resetados = True
            st.toast("Filtros resetados para valores padrão!", icon="✅")
            st.rerun()
    
    menu = st.session_state.menu_ativo

    if menu == "Clima":
        st.header("📈 Dashboard Clima - Principais Indicadores", divider="grey")

        # TODO: Implementar KPIs
        cols = st.columns(4)
        with cols[0]:
            st.write("KPI 1")
        with cols[1]:
            st.write("KPI 2")
        with cols[2]:
            st.write("KPI 3")
        with cols[3]:
            st.write("KPI 4")

        cols = st.columns(3)
        with cols[0]:
            st.write("Gráfico 1")
        with cols[1]:
            st.write("Gráfico 2")
        with cols[2]:
            st.write("Gráfico 3")
        
    if menu == "Voos":
        st.header("📑 Dashboard Voos - Principais Indicadores", divider="grey")
        
        # TODO: Implementar KPIs
        cols = st.columns(4)
        with cols[0]:
            st.write("KPI 1")
        with cols[1]:
            st.write("KPI 2")
        with cols[2]:
            st.write("KPI 3")
        with cols[3]:
            st.write("KPI 4")

        cols = st.columns(3)
        with cols[0]:
            st.write("Gráfico 1")
        with cols[1]:
            st.write("Gráfico 2")
        with cols[2]:
            st.write("Gráfico 3")

if __name__ == "__main__":
    main()
