
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os
import ast
from datetime import datetime

import locale

# Intentar configurar locale a español para fechas
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES')
    except:
        pass # Fallback to default if system doesn't support it

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Presidente Kast | Análisis Legislativo",
    page_icon="🇨🇱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Estilos CSS: Tema Serio / Dark Mode / Serif ---
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    /* Importar Fuentes Serif Premium */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Merriweather:wght@300;400;700&display=swap');
    
    /* Variables de Color - Dark Mode Serio */
    :root {
        --bg-color: #0c0d0e;
        --card-bg: transparent;
        --text-main: #ffffff;
        --text-muted: #b0b0b0;
        --accent: #c0392b;
        --border-color: rgba(255,255,255,0.1);
    }

    /* Reset y Base */
    html, body, [class*="css"] {
        font-family: 'Merriweather', serif;
        background-color: var(--bg-color);
        color: var(--text-main);
    }
    
    .stApp {
        background-color: var(--bg-color);
    }
    
    /* Títulos con Playfair Display (Estilo Presidencial) */
    h1, h2, h3, .header-title {
        font-family: 'Playfair Display', serif;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    /* HEADER PERSONALIZADO */
    .hero-banner {
        padding: 60px 20px;
        background: transparent;
        text-align: center;
        margin-bottom: 20px;
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        letter-spacing: 2px;
        margin-bottom: 10px;
        color: white;
        text-shadow: 0px 4px 10px rgba(0,0,0,0.8);
    }
    .hero-subtitle {
        font-size: 1.3rem;
        color: var(--text-muted);
        font-style: italic;
        font-family: 'Playfair Display', serif;
        text-transform: uppercase;
        letter-spacing: 3px;
    }

    /* COMPONENTES TIPO IMAGEN (Abiertos) */
    .metric-card {
        background-color: transparent;
        border: none;
        padding: 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-label {
        font-family: 'Merriweather', serif;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 2px;
        color: var(--text-muted);
        margin-bottom: 5px;
    }
    .metric-value {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        color: white;
        font-weight: 700;
        line-height: 1;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.7);
    }
    .metric-subtitle {
        font-size: 0.8rem;
        color: var(--text-muted);
        margin-top: 8px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Tabs Styling - Icon above text aesthetic */
    .stTabs [data-baseweb="tab-list"] {
        gap: 40px;
        background-color: transparent;
        padding: 40px 10px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        height: auto;
        padding: 10px 15px;
        background-color: transparent;
        color: rgba(255,255,255,0.3);
        font-family: 'Playfair Display', serif;
        font-weight: 600;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        border: none;
        border-bottom: 2px solid transparent;
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    /* FontAwesome Icons Implementation */
    .stTabs [data-baseweb="tab"]::before {
        font-family: "Font Awesome 6 Free";
        font-weight: 900;
        font-size: 1.6rem;
        margin-bottom: 12px;
        display: block;
        transition: all 0.3s ease;
    }
    
    /* Specific Icons for each Tab using robust nth-child selection */
    /* We use raw strings in python or double escape in CSS to ensure \fXXXX is passed */
    .stTabs [data-baseweb="tab"]:nth-child(1)::before { content: "\\f080"; } /* General */
    .stTabs [data-baseweb="tab"]:nth-child(2)::before { content: "\\f073"; } /* Periodos */
    .stTabs [data-baseweb="tab"]:nth-child(3)::before { content: "\\f005"; } /* Destacados */
    .stTabs [data-baseweb="tab"]:nth-child(4)::before { content: "\\f66f"; } /* Comisiones */
    .stTabs [data-baseweb="tab"]:nth-child(5)::before { content: "\\f0e8"; } /* Datos */
    .stTabs [data-baseweb="tab"]:nth-child(6)::before { content: "\\f252"; } /* Estado */
    .stTabs [data-baseweb="tab"]:nth-child(7)::before { content: "\\f70e"; } /* Leyes */
    .stTabs [data-baseweb="tab"]:nth-child(8)::before { content: "\\f002"; } /* Explorador */

    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        color: white !important;
        border-bottom: 2px solid white !important;
    }
    .stTabs [aria-selected="true"]::before {
        color: #c0392b; /* Highlight icon on selection */
        transform: scale(1.1);
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: white;
    }
    .stTabs [data-baseweb="tab"]:hover::before {
        transform: translateY(-3px);
    }
    
    /* Footer Clean */
    .footer {
        margin-top: 100px;
        padding: 50px 20px;
        background-color: transparent;
        text-align: center;
        border-top: 1px solid rgba(255,255,255,0.05);
    }
    
    /* Ajustes Graficos */
    .js-plotly-plot .plotly .main-svg {
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Backend Logica (Igual que antes) ---

# --- Backend Logica (SUPABASE) ---
import psycopg2

# Supabase Credentials (Pooler)
DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def conectar_db():
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except Exception as e:
        st.error(f"Error conectando a Supabase: {e}")
        return None

@st.cache_data
def load_data():
    conn = conectar_db()
    if conn is None: return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    try:
        # En Supabase las columnas suelen estar en minúsculas y snake_case (ej: n_boletin)
        df_m = pd.read_sql("SELECT * FROM mociones", conn)
        df_c = pd.read_sql("SELECT * FROM coautores", conn)
        df_d = pd.read_sql("SELECT * FROM dim_diputados", conn)
        # Tablas opcionales
        try: df_i = pd.read_sql("SELECT * FROM analisis_ia", conn)
        except: df_i = pd.DataFrame()
    except Exception as e:
        st.error(f"Error leyendo tablas: {e}")
        conn.close()
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    conn.close()
    
    # --- Normalización de Nombres de Columnas (Mapping Supabase -> App) ---
    # App espera: 'id_boletin', 'nombre_iniciativa', 'fecha_ingreso', 'estado_del_proyecto_de_ley', 'comision_inicial'
    
    # MOCIONES
    # Supabase probables: 'n_boletin' o 'num_boletin', 'nombre_iniciativa', 'fecha_de_ingreso', 'etapa', etc.
    cols_moc = {
        'n_boletin': 'id_boletin', 
        'num_boletin': 'id_boletin',
        'n° boletín': 'id_boletin',
        'nombre_iniciativa': 'nombre_iniciativa',
        'fecha_de_ingreso': 'fecha_ingreso',
        'estado_del_proyecto_de_ley': 'estado_del_proyecto_de_ley',
        'tipo_de_proyecto': 'tipo_iniciativa',
        'comision_inicial': 'comision_inicial'
    }
    df_m.rename(columns=cols_moc, inplace=True)
    
    # Preprocesamiento Fechas
    col_fecha = 'fecha_ingreso' if 'fecha_ingreso' in df_m.columns else None
    
    if col_fecha:
        df_m[col_fecha] = pd.to_datetime(df_m[col_fecha], errors='coerce').dt.normalize()
        df_m['anio'] = df_m[col_fecha].dt.year
        
        def get_period(date):
            if pd.isna(date): return "Desconocido"
            year = date.year
            month = date.month
            if 2002 <= year < 2006 or (year == 2006 and month < 3): return "2002 - 2006"
            if 2006 <= year < 2010 or (year == 2010 and month < 3): return "2006 - 2010"
            if 2010 <= year < 2014 or (year == 2014 and month < 3): return "2010 - 2014"
            if 2014 <= year < 2018 or (year == 2018 and month < 3): return "2014 - 2018"
            if 2018 <= year < 2022 or (year == 2022 and month < 3): return "2018 - 2022"
            return "Otros"
            
        df_m['periodo'] = df_m[col_fecha].apply(get_period)

    # Limpiar Fecha Publicación si existe
    if 'publicado_en_diario_oficial' in df_m.columns:
         df_m['publicado_en_diario_oficial'] = pd.to_datetime(df_m['publicado_en_diario_oficial'], errors='coerce').dt.normalize()

    # COAUTORES
    # Supabase probables: 'n_boletin', 'diputado'
    cols_co = {
        'n_boletin': 'id_boletin',
        'num_boletin': 'id_boletin',
        'diputado': 'diputado'
    }
    df_c.rename(columns=cols_co, inplace=True)

    # DIPUTADOS
    cols_dip = {
        'diputado': 'diputado',
        'partido_politico': 'partido'
    }
    df_d.rename(columns=cols_dip, inplace=True)

    # IA
    cols_ia = {
        'n_boletin': 'id_boletin'
    }
    df_i.rename(columns=cols_ia, inplace=True)
        
    return df_m, df_c, df_d, df_i

df_mociones, df_coautores, df_diputados, df_ia = load_data()

# Normalización Extra por si acaso (Fallback)
def ensure_cols(df, candidates, target):
    for c in candidates:
        if c in df.columns:
            df.rename(columns={c: target}, inplace=True)
            return

ensure_cols(df_mociones, ['N° Boletín', 'n_boletin'], 'id_boletin')
ensure_cols(df_coautores, ['N° Boletín', 'n_boletin'], 'id_boletin')
ensure_cols(df_coautores, ['Diputado'], 'diputado')
ensure_cols(df_diputados, ['Diputado'], 'diputado')
ensure_cols(df_diputados, ['Partido Politico', 'partido_politico', 'Partido'], 'partido')

# --- Contexto JAK ---
TARGET_DEPUTY = "Jose Antonio Kast Rist"
TARGET_VARIANTS = ["Jose Antonio Kast Rist", "José Antonio Kast Rist", "Kast Rist Jose Antonio"]
found_name = TARGET_DEPUTY
if not df_coautores.empty:
    all_deps = df_coautores['diputado'].unique()
    if found_name not in all_deps:
        for v in TARGET_VARIANTS:
            if v in all_deps:
                found_name = v
                break

jak_boletines_ids = []
if not df_coautores.empty:
    jak_boletines_ids = df_coautores[df_coautores['diputado'] == found_name]['id_boletin'].unique()

df_main = df_mociones[df_mociones['id_boletin'].isin(jak_boletines_ids)] if not df_mociones.empty else pd.DataFrame()
if not df_main.empty and not df_ia.empty:
    df_main = df_main.merge(df_ia, on='id_boletin', how='left')

# --- HEADER FIJO (Visual) ---
st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-subtitle">Observatorio Congreso</div>
        <div class="hero-title">JOSE ANTONIO KAST</div>
        <div style="display:flex; justify-content:center; gap:10px; margin-top:10px;">
            <span style="background-color:rgba(255,255,255,0.1); padding:5px 15px; border-radius:20px; font-size:0.8rem; letter-spacing:1px; border:1px solid rgba(255,255,255,0.2);">DIPUTADO 2002-2018</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- NAVEGACIÓN HORIZONTAL (TABS) ---
tabs_titles = [
    "GENERAL", 
    "PERIODOS", 
    "DESTACADOS", 
    "COMISIONES", 
    "DATOS", 
    "ESTADO", 
    "LEYES", 
    "EXPLORADOR"
]
tabs = st.tabs(tabs_titles)

# Helpers
def get_coauthors_for_boletines(boletin_list):
    if df_coautores.empty: return pd.DataFrame()
    return df_coautores[df_coautores['id_boletin'].isin(boletin_list)]

def kpi_card(title, value, subtitle="", col=None):
    html = f"""
    <div class='metric-card'>
        <div class='metric-label'>{title}</div>
        <div class='metric-value'>{value}</div>
        <div class='metric-subtitle'>{subtitle}</div>
    </div>
    """
    if col: col.markdown(html, unsafe_allow_html=True)
    else: st.markdown(html, unsafe_allow_html=True)

# Helper de Formato Fecha Global
def format_date_human(val):
    if pd.isna(val): return "N/A"
    try:
        # Si es string, intentar convertir primero
        if isinstance(val, str):
            val = pd.to_datetime(val)
        return val.strftime('%d/%m/%Y')
    except:
        return str(val)

# Dark Plotly Template
pio_template = "plotly_dark"

# helpers para lógica legislativa global
def categorize_commission(c_name):
    n = str(c_name).lower()
    if 'constituc' in n or 'legislaci' in n or 'justicia' in n: return 'Constitución y Justicia'
    if 'econom' in n or 'hacienda' in n or 'presupuesto' in n: return 'Economía y Hacienda'
    if 'seguridad' in n or 'defensa' in n or 'inteligencia' in n: return 'Security y Defensa'
    if 'familia' in n or 'mujer' in n or 'adulto mayor' in n or 'desarrollo' in n: return 'Familia y Social'
    if 'educaci' in n or 'cultura' in n or 'deportes' in n: return 'Educación y Cultura'
    if 'salud' in n: return 'Salud'
    if 'trabajo' in n or 'previsión' in n: return 'Trabajo y Previsión'
    if 'ambiente' in n or 'recursos' in n or 'pesca' in n or 'agricultura' in n or 'minería' in n: return 'Medio Ambiente y Recursos'
    if 'vivienda' in n or 'obras' in n or 'transporte' in n or 'telecomunicaciones' in n: return 'Vivienda e Infraestructura'
    if 'derechos humanos' in n or 'nacionalidad' in n: return 'DD.HH. y Nacionalidad'
    if 'gobierno' in n or 'interior' in n or 'regional' in n: return 'Gobierno Interior'
    return 'Otras'

def map_stage_numeric(etapa_txt, estado_txt):
    txt = str(etapa_txt).lower()
    est = str(estado_txt).lower()
    if "publicado" in est or "ley" in est or "tramitación terminada" in est: return 4
    if "archivado" in est or "retirado" in est: return 0
    if "tercer" in txt or "mixta" in txt or "veto" in txt: return 3
    if "segundo" in txt or "revisora" in txt: return 2
    return 1

def map_stage_label(val):
    if val == 4: return "Tramitación Terminada / Ley"
    if val == 3: return "Tercer Trámite / Mixta"
    if val == 2: return "Segundo Trámite"
    if val == 1: return "Primer Trámite"
    if val == 0: return "Archivado / Retirado"
    return "Desconocido"

# --- CONTENIDO ---

# 1. GENERAL (Ex RESUMEN)
with tabs[0]:
    st.markdown("<h2 style='text-align:center;'>Análisis de Trayectoria Legislativa</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888; margin-bottom:40px;'>Un recorrido por la actividad y efectividad del diputado en el Congreso Nacional.</p>", unsafe_allow_html=True)
    
    total = len(df_main)
    pattern_success = 'Ley|Publicado|Tramitación terminada'
    leyes_finished = len(df_main[df_main['estado_del_proyecto_de_ley'].str.contains(pattern_success, case=False, na=False)]) if 'estado_del_proyecto_de_ley' in df_main.columns else 0
    co_auth_all = get_coauthors_for_boletines(df_main['id_boletin'].unique())
    co_auth_all = co_auth_all[co_auth_all['diputado'] != found_name]
    top_ally = co_auth_all['diputado'].mode()[0] if not co_auth_all.empty else "N/A"
    unique_years = df_main['anio'].nunique() if 'anio' in df_main.columns else 1
    avg_yearly = round(total / unique_years, 1) if unique_years > 0 else 0
    
    # KPIs Top
    c1, c2, c3, c4 = st.columns(4)
    kpi_card("Total Iniciativas", total, "Carrera parlamentaria", c1)
    kpi_card("Aprobados / Terminados", leyes_finished, f"Tasa: {(leyes_finished/total*100):.1f}%", c2)
    kpi_card("Promedio Anual", avg_yearly, "Mociones por año", c3)
    kpi_card("Aliado Histórico", top_ally, "Mayor colaborador", c4)
    
    st.markdown("---")
    # --- SECCIÓN 1: ESTADO (TEXTO IZQ, GRÁFICO DER) ---
    col1_txt, col1_gr = st.columns([1, 1.5], gap="large")
    with col1_txt:
        st.markdown("### Estado de la Gestión")
        st.markdown(f"""
        Esta sección analiza el ciclo de vida de los **{total} proyectos** presentados. 
        
        Aproximadamente un **{(leyes_finished/total*100):.1f}%** de las iniciativas han logrado convertirse en ley o finalizar su tramitación, lo que representa un indicador clave de efectividad legislativa.
        
        La mayoría de los proyectos en el Congreso a menudo quedan estancados en comisiones, un desafío común en la labor parlamentaria chilena que se refleja en la alta proporción de mociones 'En Tramitación'.
        """)
    with col1_gr:
        if 'estado_del_proyecto_de_ley' in df_main.columns:
            status_counts = df_main['estado_del_proyecto_de_ley'].value_counts().reset_index()
            status_counts.columns = ['Estado', 'Cantidad']
            if len(status_counts) > 8:
                top_s = status_counts.head(7)
                others = pd.DataFrame([['Otros', status_counts.iloc[7:]['Cantidad'].sum()]], columns=['Estado', 'Cantidad'])
                status_counts = pd.concat([top_s, others])
            
            fig_pie = px.pie(status_counts, values='Cantidad', names='Estado', hole=0.5, 
                             template=pio_template, color_discrete_sequence=px.colors.sequential.RdBu)
            fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=True)
            st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # --- SECCIÓN 2: COMISIONES (GRÁFICO IZQ, TEXTO DER) ---
    col2_gr, col2_txt = st.columns([1.5, 1], gap="large")
    with col2_gr:
        if 'comision_inicial' in df_main.columns:
            com_init = df_main['comision_inicial'].fillna("Desconocida").value_counts().head(10).reset_index()
            com_init.columns = ['Comisión', 'Proyectos']
            com_init = com_init.sort_values('Proyectos', ascending=True)
            
            fig_bar_com = px.bar(com_init, x='Proyectos', y='Comisión', orientation='h',
                                 template=pio_template)
            fig_bar_com.update_traces(marker_color='#c0392b')
            fig_bar_com.update_layout(margin=dict(t=0, b=0, l=0, r=0), xaxis_title="Cantidad de Proyectos")
            st.plotly_chart(fig_bar_com, use_container_width=True)
            
    with col2_txt:
        st.markdown("### Áreas de Influencia")
        st.markdown("""
        El impacto legislativo se concentra principalmente en las áreas de **Constitución**, **Seguridad** y **Hacienda**. 
        
        Este gráfico destaca las 10 comisiones donde se ha ingresado el mayor volumen de iniciativas. Una mayor cantidad de proyectos en comisiones clave como Constitución sugiere un enfoque en temas de relevancia nacional y reformas estructurales.
        """)

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # --- SECCIÓN 3: PRODUCCIÓN ANUAL (TEXTO IZQ, GRÁFICO DER) ---
    col3_txt, col3_gr = st.columns([1, 1.5], gap="large")
    with col3_txt:
        st.markdown("### Evolución Histórica")
        st.markdown("""
        La actividad parlamentaria no es lineal; fluctúa según los ciclos políticos y los periodos presidenciales. 
        
        Se observa una intensidad variable a lo largo de los años, con picos de actividad que suelen coincidir con debates nacionales críticos o el inicio de nuevos mandatos parlamentarios.
        """)
    with col3_gr:
        if 'anio' in df_main.columns:
            yearly = df_main.groupby('anio').size().reset_index(name='Proyectos')
            fig_ev = px.bar(yearly, x='anio', y='Proyectos', template=pio_template)
            fig_ev.update_traces(marker_color='#555')
            fig_ev.update_layout(margin=dict(t=0, b=0, l=0, r=0), yaxis_title="Proyectos Ingresados")
            st.plotly_chart(fig_ev, use_container_width=True)

# 2. PERIODOS
with tabs[1]:
    st.markdown("<h2 style='text-align:center;'>Análisis por Periodo Legislativo</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888; margin-bottom:40px;'>Explora el desempeño y foco temático en cada uno de los mandatos parlamentarios.</p>", unsafe_allow_html=True)
    
    available_periods = sorted(df_main['periodo'].unique().tolist()) if 'periodo' in df_main.columns else []
    
    if available_periods:
        # Selector de Periodo destacado
        selected_period = st.pills("Seleccionando periodo para desglose:", available_periods, default=available_periods[0]) if hasattr(st, "pills") else st.selectbox("Seleccione Periodo", available_periods)
        
        if selected_period:
            df_p = df_main[df_main['periodo'] == selected_period].copy()
            p_total = len(df_p)
            pattern_success = 'Ley|Publicado|Tramitación terminada'
            p_leyes = len(df_p[df_p['estado_del_proyecto_de_ley'].str.contains(pattern_success, case=False, na=False)]) if 'estado_del_proyecto_de_ley' in df_p.columns else 0
            
            c_p1, c_p2 = st.columns(2)
            kpi_card("Iniciativas", p_total, selected_period, c_p1)
            kpi_card("Convertidas en Ley", p_leyes, f"Mandato {selected_period}", c_p2)
            
            st.markdown("---")
            
            # SECCIÓN 1: ESTADO DEL PERIODO (TEXTO IZQ, GRÁFICO DER)
            cp1_txt, cp1_gr = st.columns([1, 1.5], gap="large")
            with cp1_txt:
                st.markdown(f"### Desempeño en {selected_period}")
                st.markdown(f"""
                Durante este mandato, se presentaron **{p_total} iniciativas**. 
                
                Este análisis permite observar cómo se distribuyeron los resultados legislativos específicamente en estos años. La tasa de éxito de este periodo fue de un **{(p_leyes/p_total*100 if p_total > 0 else 0):.1f}%**.
                """)
            with cp1_gr:
                if 'estado_del_proyecto_de_ley' in df_p.columns:
                    st_counts = df_p['estado_del_proyecto_de_ley'].value_counts().reset_index()
                    st_counts.columns = ['Estado', 'Cantidad']
                    fig_st_per = px.pie(st_counts, values='Cantidad', names='Estado', hole=0.5, template=pio_template)
                    fig_st_per.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                    st.plotly_chart(fig_st_per, use_container_width=True)

            st.markdown("<br><br>", unsafe_allow_html=True)

            # SECCIÓN 2: FOCO TEMÁTICO (GRÁFICO IZQ, TEXTO DER)
            cp2_gr, cp2_txt = st.columns([1.5, 1], gap="large")
            with cp2_gr:
                if 'comision_inicial' in df_p.columns:
                    df_p['Tematica'] = df_p['comision_inicial'].apply(categorize_commission)
                    p_temas = df_p['Tematica'].value_counts().reset_index()
                    p_temas.columns = ['Tematica', 'Proyectos']
                    fig_tree_p = px.treemap(p_temas, path=['Tematica'], values='Proyectos', template=pio_template)
                    fig_tree_p.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                    st.plotly_chart(fig_tree_p, use_container_width=True)
            with cp2_txt:
                st.markdown("### Áreas de Interés")
                st.markdown(f"En el periodo **{selected_period}**, la mayoría de los proyectos se concentraron en las categorías visualizadas a la izquierda. Esto revela las prioridades políticas y legislativas de este tiempo específico.")

            st.markdown("<br><br>", unsafe_allow_html=True)

            # SECCIÓN 3: INTENSIDAD (TEXTO IZQ, GRÁFICO DER)
            cp3_txt, cp3_gr = st.columns([1, 1.5], gap="large")
            with cp3_txt:
                st.markdown("### Intensidad Anual")
                st.markdown(f"Distribución año a año de las mociones ingresadas dentro del periodo legislativo {selected_period}.")
            with cp3_gr:
                if 'anio' in df_p.columns:
                    p_yearly = df_p.groupby('anio').size().reset_index(name='Proyectos')
                    fig_bar_p = px.bar(p_yearly, x='anio', y='Proyectos', template=pio_template)
                    fig_bar_p.update_traces(marker_color='#c0392b')
                    fig_bar_p.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                    st.plotly_chart(fig_bar_p, use_container_width=True)

            with st.expander(f"Auditar: Lista completa de proyectos ({selected_period})"):
                st.dataframe(df_p[['id_boletin', 'nombre_iniciativa', 'estado_del_proyecto_de_ley', 'fecha_ingreso', 'comision_inicial']].sort_values('fecha_ingreso', ascending=False), use_container_width=True, hide_index=True)

# 3. DESTACADOS
with tabs[2]:
    st.markdown("### Boletines de Interés Público")
    
    df_featured = df_main.copy()
    if 'estado_del_proyecto_de_ley' in df_featured.columns:
        df_featured['is_ley'] = df_featured['estado_del_proyecto_de_ley'].astype(str).str.contains('Ley|Publicado', case=False).astype(int)
        df_featured.sort_values(by=['is_ley'], ascending=[False], inplace=True)
        
    opts = df_featured.apply(lambda x: f"{'★' if x.get('is_ley',0) else '•'} {x['id_boletin']} | {str(x.get('nombre_iniciativa', ''))[:80]}...", axis=1).tolist()
    
    sel = st.selectbox("Seleccionar Proyecto", opts)
    if sel:
        bid = sel.split("|")[0].replace('★','').replace('•','').strip()
        row = df_featured[df_featured['id_boletin'] == bid].iloc[0]
        
        st.markdown(f"""
        <div style='background-color:#141414; border:1px solid #333; padding:20px; border-radius:4px;'>
            <h3 style='margin-top:0'>{row.get('nombre_iniciativa')}</h3>
            <p style='color:#ccc; font-style:italic; font-family:"Merriweather"'>{row.get('resumen_ejecutivo', 'Resumen no disponible')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        c_a, c_b = st.columns(2)
        c_a.write(f"**Estado:** {row.get('estado_del_proyecto_de_ley')}")
        c_a.write(f"**Tipo:** {row.get('tipo_iniciativa')}")
        c_b.write(f"**Fecha:** {row.get('fecha_ingreso')}")
        
        st.markdown("#### Coautores")
        co = get_coauthors_for_boletines([bid])
        co = co[co['diputado'] != found_name]
        if not co.empty:
            st.write(", ".join(co['diputado'].unique()))

# 4. COMISIONES
with tabs[3]:
    st.markdown("<h2 style='text-align:center;'>Trabajo en Comisiones</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888; margin-bottom:40px;'>Análisis de la especialización temática basada en las comisiones de origen.</p>", unsafe_allow_html=True)
    
    if 'comision_inicial' in df_main.columns:
        df_com = df_main.copy()
        df_com['comision_inicial'] = df_com['comision_inicial'].fillna("Desconocida").astype(str)
        df_com['Tematica'] = df_com['comision_inicial'].apply(categorize_commission)
        
        # SECCIÓN 1: DISTRIBUCIÓN (TEXTO IZQ, TREEMAP DER)
        cc1_txt, cc1_gr = st.columns([1, 1.5], gap="large")
        with cc1_txt:
            st.markdown("### Mapa de Especialización")
            st.markdown("""
            A través de las comisiones, podemos ver dónde se concentra el esfuerzo legislativo. 
            
            Este Mapa de Calor (Treemap) agrupa las comisiones específicas en temáticas generales para facilitar la comprensión de las prioridades del diputado.
            """)
        with cc1_gr:
            import numpy as np
            theme_counts = df_com['Tematica'].value_counts().reset_index()
            theme_counts.columns = ['Tematica', 'Proyectos']
            fig_tree = px.treemap(theme_counts, path=['Tematica'], values='Proyectos', color='Proyectos', color_continuous_scale='RdBu', template=pio_template)
            fig_tree.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_tree, use_container_width=True)

        st.markdown("---")
        
        # 2. SELECCIÓN DETALLADA
        st.markdown("### 🔍 Explorar por Temática")
        
        temas_list = sorted(theme_counts['Tematica'].unique())
        if temas_list:
            sel_tema = st.pills("Seleccione una temática", temas_list, default=temas_list[0]) if hasattr(st, "pills") else st.selectbox("Seleccione Tema", temas_list)
            
            if sel_tema:
                # Filtrar
                df_t = df_com[df_com['Tematica'] == sel_tema]
                
                # Sub-KPIs
                t_total = len(df_t)
                t_leyes = len(df_t[df_t['estado_del_proyecto_de_ley'].str.contains('Ley|Publicado|Tramitación terminada', case=False, na=False)])
                
                k1, k2, k3 = st.columns(3)
                kpi_card("Proyectos en Temática", t_total, sel_tema, k1)
                kpi_card("Exitosos / Leyes", t_leyes, f"{(t_leyes/t_total*100):.1f}% efectividad", k2)
                
                # Ver sub-comisiones específicas dentro de este tema
                top_sub = df_t['comision_inicial'].mode()[0] if not df_t.empty else "N/A"
                kpi_card("Comisión Principal", str(top_sub)[:30]+"..." if len(str(top_sub))>30 else str(top_sub), "Mayor frecuencia", k3)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Tabla de Proyectos
                st.markdown(f"#### Proyectos de {sel_tema}")
                
                # Mostrar tabla con columnas relevantes
                st.dataframe(
                    df_t[['id_boletin', 'nombre_iniciativa', 'estado_del_proyecto_de_ley', 'fecha_ingreso', 'comision_inicial']]
                    .sort_values('fecha_ingreso', ascending=False)
                    .rename(columns={'comision_inicial': 'Comisión Específica'}),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info("No hay datos temáticos disponibles.")

    else:
        st.error("No se encontró columna 'comision_inicial'.")

# 5. DATOS (Deep Dive)
with tabs[4]:
    st.markdown("### Red de Influencia Política")
    st.caption("Grafo de Coautorías: JAK (Centro) → Partidos → Diputados.")
    
    coautores_jak = get_coauthors_for_boletines(df_main['id_boletin'].unique())
    coautores_jak = coautores_jak[coautores_jak['diputado'] != found_name]
    
    if not coautores_jak.empty and not df_diputados.empty and 'partido' in df_diputados.columns:
        # Preparar Datos
        df_net = coautores_jak.merge(df_diputados, on='diputado', how='left')
        
        # Limpieza y Normalización de Partidos
        df_net['partido'] = df_net['partido'].fillna("Sin Partido").astype(str).str.strip()
        
        # Mapa de normalización manual (ejemplos comunes en Chile)
        party_map = {
            'Unión Demócrata Independiente': 'UDI',
            'Renovación Nacional': 'RN',
            'Democracia Cristiana': 'DC',
            'Partido Socialista': 'PS',
            'Partido Por la Democracia': 'PPD',
            'Partido Radical Social Demócrata': 'PRSD',
            'Partido Comunista': 'PC',
            'Evolución Política': 'Evópoli',
            'Partido Republicano de Chile': 'Republicanos',
            'Independiente': 'IND',
            'Independientes': 'IND'
        }
        
        # Función para normalizar nombres similares
        def normalize_party(p_name):
            p_upper = p_name.upper()
            
            # Busqueda directa en mapa
            if p_name in party_map: return party_map[p_name]
            
            # Busqueda por substring común
            if 'UDI' in p_upper: return 'UDI'
            if 'RENOVACION' in p_upper or 'RN' == p_upper: return 'RN'
            if 'SOCIALISTA' in p_upper or 'PS' == p_upper: return 'PS'
            if 'RADICAL' in p_upper: return 'PRSD'
            if 'DEMOCRACIA' in p_upper and 'CRISTIANA' in p_upper: return 'DC'
            if 'COMUNISTA' in p_upper: return 'PC'
            if 'INDEPENDIENTE' in p_upper: return 'IND'
            if 'REPUBLICANO' in p_upper: return 'Republicanos'
            
            return p_name # Retornar original si no hay match
            
        df_net['partido_norm'] = df_net['partido'].apply(normalize_party)
        
        # Agrupar por Partido Normalizado y Diputado
        df_grouped = df_net.groupby(['partido_norm', 'diputado']).size().reset_index(name='weight')
        df_grouped.rename(columns={'partido_norm': 'partido'}, inplace=True)
        
        # Construir Nodos y Aristas (Edges)
        import numpy as np
        
        # Centro
        center_node = {'id': 'JAK', 'x': 0, 'y': 0, 'size': 40, 'color': '#ffffff', 'label': 'José Antonio Kast'}
        
        # Partidos
        partidos = sorted(df_grouped['partido'].unique().tolist())
        n_parties = len(partidos)
        party_coords = {}
        
        # Colores para partidos (Palette distintiva)
        import plotly.colors as pc
        party_colors = pc.qualitative.Bold
        
        nodes_data = [center_node]
        edges_data = [] # (x0, y0, x1, y1)
        
        # Posicionar Partidos
        radius_p = 5
        for i, p in enumerate(partidos):
            angle = (2 * np.pi * i) / n_parties
            x = radius_p * np.cos(angle)
            y = radius_p * np.sin(angle)
            party_coords[p] = (x, y)
            
            p_color = party_colors[i % len(party_colors)]
            p_weight = df_grouped[df_grouped['partido'] == p]['weight'].sum()
            
            nodes_data.append({
                'id': p, 'x': x, 'y': y, 
                'size': 20 + np.log(p_weight)*5, 
                'color': p_color, 
                'label': f"{p} ({p_weight} coautorías)"
            })
            
            # Edge JAK -> Partido
            edges_data.append((0, 0, x, y))
            
            # Posicionar Diputados del Partido
            deps = df_grouped[df_grouped['partido'] == p]
            n_deps = len(deps)
            radius_d = 2 
            
            base_angle = angle
            
            for j, row in enumerate(deps.itertuples()):
                dep_angle = base_angle + np.random.uniform(-0.5, 0.5) 
                dist = radius_d + np.random.uniform(0, 1)
                
                dx = x + (dist * np.cos(dep_angle))
                dy = y + (dist * np.sin(dep_angle))
                
                nodes_data.append({
                    'id': row.diputado, 'x': dx, 'y': dy,
                    'size': 10 + np.log(row.weight)*3,
                    'color': p_color, # Same as party
                    'label': f"{row.diputado}<br>{row.weight} proyectos"
                })
                
                # Edge Partido -> Diputado
                edges_data.append((x, y, dx, dy))

        # Crear Traces
        
        # Edges Trace
        ekt_x = []
        ekt_y = []
        for e in edges_data:
            ekt_x.extend([e[0], e[2], None])
            ekt_y.extend([e[1], e[3], None])
            
        edge_trace = go.Scatter(
            x=ekt_x, y=ekt_y,
            line=dict(width=0.5, color='#444'),
            hoverinfo='none',
            mode='lines')

        # Nodes Trace
        node_x = [n['x'] for n in nodes_data]
        node_y = [n['y'] for n in nodes_data]
        node_marker_size = [n['size'] for n in nodes_data]
        node_marker_color = [n['color'] for n in nodes_data]
        node_text = [n['label'] for n in nodes_data]
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            text=node_text,
            marker=dict(
                showscale=False,
                color=node_marker_color,
                size=node_marker_size,
                line_width=1,
                line_color='#000'))

        fig_net = go.Figure(data=[edge_trace, node_trace],
                         layout=go.Layout(
                            title=dict(text='Red de Coautorías Parlamentarias', font=dict(size=16)),
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20,l=5,r=5,t=40),
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                            )
                            
        st.plotly_chart(fig_net, use_container_width=True, height=700)
        
        st.markdown("#### Top Aliados por Partido")
        # Tabla simple
        st.dataframe(df_grouped[['partido', 'diputado', 'weight']].sort_values(['partido', 'weight'], ascending=[True, False]), hide_index=True, use_container_width=True)

    else:
        st.warning("Datos insuficientes para generar el gráfico de red. Verifique la carga de 'dim_diputados'.")

# 6. ESTADO Y TIEMPOS
with tabs[5]:
    st.markdown("<h2 style='text-align:center;'>Ciclo de Vida Legislativo</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888; margin-bottom:40px;'>Seguimiento del progreso de las iniciativas y tiempos de tramitación.</p>", unsafe_allow_html=True)
    
    if 'estado_del_proyecto_de_ley' in df_main.columns:
        df_status = df_main.copy()
        source_col = 'etapa_del_proyecto' if 'etapa_del_proyecto' in df_main.columns else 'estado_del_proyecto_de_ley'
        df_status['progress_val'] = df_status.apply(lambda x: map_stage_numeric(x.get(source_col, ''), x['estado_del_proyecto_de_ley']), axis=1)
        df_status['etapa_lbl'] = df_status['progress_val'].apply(map_stage_label)
        
        # SECCIÓN 1: TIEMPOS (TEXTO IZQ, KPI DER)
        ce1_txt, ce1_gr = st.columns([1, 1], gap="large")
        with ce1_txt:
            st.markdown("### Tramitación en Tiempo Real")
            st.markdown("""
            Uno de los mayores desafíos del proceso legislativo es la demora. 
            
            El KPI de la derecha muestra el promedio de días que han tardado las mociones de JAK en ser publicadas como ley, un dato clave sobre la agilidad del sistema.
            """)
        with ce1_gr:
            col_pub = 'publicado_en_diario_oficial'
            avg_days_val = "N/A"
            if col_pub in df_status.columns and 'fecha_ingreso' in df_status.columns:
                df_l = df_status[df_status['estado_del_proyecto_de_ley'].str.contains('Ley|Publicado', case=False, na=False)].copy()
                df_l[col_pub] = pd.to_datetime(df_l[col_pub], errors='coerce')
                df_l['fecha_ingreso'] = pd.to_datetime(df_l['fecha_ingreso'], errors='coerce')
                df_l = df_l.dropna(subset=[col_pub, 'fecha_ingreso'])
                if not df_l.empty:
                    df_l['dias'] = (df_l[col_pub] - df_l['fecha_ingreso']).dt.days
                    avg_days_val = int(df_l['dias'].mean())
            kpi_card("Tiempo Promedio (Días)", avg_days_val, "Desde ingreso a publicación")

        st.markdown("<br><br>", unsafe_allow_html=True)

        # SECCIÓN 2: ETAPAS GLOBALES (GRÁFICO IZQ, TEXTO DER)
        ce2_gr, ce2_txt = st.columns([1.5, 1], gap="large")
        with ce2_gr:
            st_counts = df_status['etapa_lbl'].value_counts().reset_index()
            st_counts.columns = ['Etapa', 'Proyectos']
            order_map = {"Primer Trámite": 1, "Segundo Trámite": 2, "Tercer Trámite / Mixta": 3, "Tramitación Terminada / Ley": 4, "Archivado / Retirado": 5}
            st_counts['order'] = st_counts['Etapa'].map(order_map)
            st_counts = st_counts.sort_values('order')
            fig_global = px.pie(st_counts, values='Proyectos', names='Etapa', hole=0.6, template=pio_template, color_discrete_sequence=px.colors.sequential.RdBu)
            fig_global.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_global, use_container_width=True)
        with ce2_txt:
            st.markdown("### Avance Legislativo")
            st.markdown("Este gráfico de dona muestra en qué fase se encuentran todos los proyectos. Ayuda a identificar cuántas mociones se encuentran en trámites avanzados frente a las que están en su etapa inicial.")

        st.markdown("---")
        
        # --- SECCION CENTRAL: TRACKER INDIVIDUAL ---
        st.markdown("### 🎯 Rastreador de Proyectos")
        st.caption("Selecciona un proyecto para visualizar su avance específico.")
        
        # Selector
        opts = df_status['nombre_iniciativa'].tolist()
        # Crear mapa nombre -> boletin para búsqueda facil
        name_to_id = dict(zip(df_status['nombre_iniciativa'], df_status['id_boletin']))
        
        sel_proj_name = st.selectbox("Buscar Proyecto", opts)
        
        if sel_proj_name:
            row = df_status[df_status['nombre_iniciativa'] == sel_proj_name].iloc[0]
            
            # Layout Detalle
            c_track_info, c_track_graph = st.columns([1, 1])
            
            with c_track_info:
                st.markdown(f"#### {row['id_boletin']}")
                st.info(f"**Estado Actual:** {row['estado_del_proyecto_de_ley']}")
                st.write(f"📅 **Fecha Ingreso:** {row.get('fecha_ingreso', 'N/A')}")
                st.write(f"🏛️ **Comisión:** {row.get('comision_inicial', 'N/A')}")
                st.write(f"📌 **Tipo:** {row.get('tipo_iniciativa', 'N/A')}")
                
                # Coautores (si hay funcion helper)
                # co_a = get_coauthors_for_boletines([row['id_boletin']]) ...
                # Por simplicidad mostraremos texto si existe columna
                
            with c_track_graph:
                # Gauge Chart (Velocimetro) o Progress Donut
                val = row['progress_val']
                # Mapear 0-4 a 0-100 para gauge
                if val == 0: gauge_val = 0 
                else: gauge_val = val * 25 # 1=25, 2=50, 3=75, 4=100
                
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = gauge_val,
                    title = {'text': "Progreso Estimado"},
                    gauge = {
                        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
                        'bar': {'color': "#3498db"},
                        'steps': [
                            {'range': [0, 25], 'color': "#333"},
                            {'range': [25, 50], 'color': "#444"},
                            {'range': [50, 75], 'color': "#555"},
                            {'range': [75, 100], 'color': "#666"}],
                        'threshold': {
                            'line': {'color': "green", 'width': 4},
                            'thickness': 0.75,
                            'value': gauge_val}
                    }
                ))
                fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig_gauge, use_container_width=True)

    else:
        st.error("Datos de estado no disponibles.")

# 7. LEYES
with tabs[6]:
    st.markdown("<h2 style='text-align:center;'>Leyes y Proyectos Terminados</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888; margin-bottom:40px;'>Análisis de proyectos que finalizaron su tramitación exitosamente.</p>", unsafe_allow_html=True)
    
    if 'estado_del_proyecto_de_ley' in df_main.columns:
        pattern_success = 'Ley|Publicado|Tramitación terminada'
        df_leyes = df_main[df_main['estado_del_proyecto_de_ley'].str.contains(pattern_success, case=False, na=False)].copy()
        
        if df_leyes.empty:
            st.info("No se encontraron leyes o proyectos terminados.")
        else:
            # SECCIÓN 1: PRODUCTIVIDAD (TEXTO IZQ, GRÁFICO DER)
            cl1_txt, cl1_gr = st.columns([1, 1.5], gap="large")
            with cl1_txt:
                st.markdown("### Productividad Judicial")
                st.markdown(f"Se han consolidado **{len(df_leyes)} leyes** a lo largo de los años. Este gráfico muestra en qué años se originaron los proyectos que finalmente tuvieron éxito.")
            with cl1_gr:
                if 'anio' in df_leyes.columns:
                    leyes_year = df_leyes.groupby('anio').size().reset_index(name='Cantidad')
                    fig_ly = px.bar(leyes_year, x='anio', y='Cantidad', template=pio_template)
                    fig_ly.update_traces(marker_color='#2ecc71')
                    fig_ly.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                    st.plotly_chart(fig_ly, use_container_width=True)

            st.markdown("<br><br>", unsafe_allow_html=True)

            # SECCIÓN 2: LEYES POR COMISIÓN (GRÁFICO IZQ, TEXTO DER)
            cl2_gr, cl2_txt = st.columns([1.5, 1], gap="large")
            with cl2_gr:
                if 'comision_inicial' in df_leyes.columns:
                    leyes_com = df_leyes['comision_inicial'].fillna("Desconocida").value_counts().head(10).reset_index()
                    leyes_com.columns = ['Comisión', 'Cantidad']
                    leyes_com = leyes_com.sort_values('Cantidad', ascending=True)
                    fig_lc = px.bar(leyes_com, x='Cantidad', y='Comisión', orientation='h', template=pio_template)
                    fig_lc.update_traces(marker_color='#f1c40f')
                    fig_lc.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                    st.plotly_chart(fig_lc, use_container_width=True)
            with cl2_txt:
                st.markdown("### Áreas de Éxito")
                st.markdown("Las comisiones listadas a la derecha representan los nichos donde el trabajo legislativo ha sido más efectivo, logrando la aprobación final de las leyes.")

            st.markdown("---")
            st.markdown("#### Listado Detallado")
            
            for i, row in df_leyes.iterrows():
                with st.expander(f"📜 {row['id_boletin']}: {row['nombre_iniciativa']}"):
                    c_a, c_b = st.columns(2)
                    c_a.write(f"**Fecha Ingreso:** {format_date_human(row.get('fecha_ingreso'))}")
                    c_a.write(f"**Tipo:** {row.get('tipo_iniciativa', 'N/A')}")
                    c_b.write(f"**Estado:** {row.get('estado_del_proyecto_de_ley', 'N/A')}")
                    
                    if 'publicado_en_diario_oficial' in row and pd.notna(row['publicado_en_diario_oficial']):
                        st.success(f"Publicado el: {format_date_human(row['publicado_en_diario_oficial'])}")
                    
                    # Link externo si existe URL
                    # st.markdown(f"[Ver en Camara](...)")

# 8. EXPLORADOR
with tabs[7]:
    st.markdown("### Buscador Avanzado")
    
    # Filtros
    c1, c2, c3 = st.columns(3)
    
    # Filtro Texto
    search = c1.text_input("Buscar en título o resumen...", placeholder="Ej: Araucanía, Impuestos")
    
    # Filtro Estado
    all_states = sorted(df_main['estado_del_proyecto_de_ley'].unique().tolist()) if 'estado_del_proyecto_de_ley' in df_main.columns else []
    sel_state = c2.selectbox("Filtrar por Estado", ["Todos"] + all_states)
    
    # Filtro Fecha
    min_date = datetime(2000, 1, 1).date()
    max_date = datetime.now().date()
    
    if 'fecha_ingreso' in df_main.columns:
        # Check for non-null/non-NaT dates
        valid_dates = df_main['fecha_ingreso'].dropna()
        if not valid_dates.empty:
            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()

    # date_input returns a tuple. If the user clears it, it might be empty. 
    # Providing a default value ensuring it's a list/tuple of 2 dates.
    date_range = c3.date_input("Rango de Fecha Ingreso", value=(min_date, max_date), format="DD/MM/YYYY")
    
    # Aplicar Filtros
    df_ex = df_main.copy()
    
    if search:
        df_ex = df_ex[df_ex.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
        
    if sel_state != "Todos":
        df_ex = df_ex[df_ex['estado_del_proyecto_de_ley'] == sel_state]
        
    if len(date_range) == 2:
        start_d, end_d = date_range
        df_ex = df_ex[(df_ex['fecha_ingreso'].dt.date >= start_d) & (df_ex['fecha_ingreso'].dt.date <= end_d)]
        
    # Limpieza de Tabla para Display
    # Seleccionar columnas relevantes que existan
    target_cols = ['id_boletin', 'nombre_iniciativa', 'fecha_ingreso', 'estado_del_proyecto_de_ley', 'tipo_iniciativa']
    disp_cols = [c for c in target_cols if c in df_ex.columns]
    df_disp = df_ex[disp_cols].copy()
    
    # Formatear fecha (quitar hora)
    if 'fecha_ingreso' in df_disp.columns:
        df_disp['fecha_ingreso'] = df_disp['fecha_ingreso'].dt.strftime('%Y-%m-%d')
        
    # Renombrar columnas (Human Readable)
    df_disp.columns = [c.replace('_', ' ').title() for c in df_disp.columns]
    
    st.dataframe(df_disp, use_container_width=True, hide_index=True)
    st.caption(f"Mostrando {len(df_disp)} proyectos.")

st.markdown(
    """<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"><style>.footer-container{display:flex;flex-wrap:wrap;justify-content:space-between;padding:50px 30px;background-color:#0F0F0F;border-top:1px solid #333;color:#a0a0a0;font-family:'Inter',sans-serif;margin-top:80px}.footer-col{flex:1;min-width:280px;margin:15px}.footer-title{color:#ffffff;font-family:'Playfair Display',serif;font-size:1.2rem;margin-bottom:20px;border-bottom:2px solid #C0392B;display:inline-block;padding-bottom:5px}/* GLOBAL FOOTER LINK RESET */.footer-container a{color:#a0a0a0 !important;text-decoration:none !important;transition:all 0.3s ease}.footer-container a:hover{color:#ffffff !important}.footer-link{display:block;margin-bottom:10px;font-size:0.95rem}.footer-link:hover{transform:translateX(5px)}.social-icons a{display:inline-flex !important;justify-content:center;align-items:center;width:40px;height:40px;background-color:#222;color:#fff !important;border-radius:50%;margin-right:10px;font-size:1.1rem}.social-icons a:hover{background-color:#C0392B !important;transform:translateY(-3px)}.btn-subscribe{display:inline-block !important;background-color:#fff !important;color:#000 !important;padding:10px 20px;border-radius:30px;font-weight:bold;font-size:0.9rem;margin-top:15px}.btn-subscribe:hover{background-color:#ddd !important}.copyright-text{font-size:0.85rem;color:#555;line-height:1.6;margin-top:15px}</style><div class="footer-container"><div class="footer-col"><div class="footer-title">Conecta</div><p style="font-size:0.95rem;margin-bottom:20px">Mantente informado con nuestros análisis exclusivos.</p><div class="social-icons"><a href="https://twitter.com" target="_blank"><i class="fab fa-twitter"></i></a><a href="https://linkedin.com" target="_blank"><i class="fab fa-linkedin-in"></i></a><a href="https://instagram.com" target="_blank"><i class="fab fa-instagram"></i></a><a href="mailto:contacto@observatoriocongreso.cl"><i class="fas fa-envelope"></i></a></div><div><a href="#" class="btn-subscribe">Suscribirse al Boletín</a></div></div><div class="footer-col"><div class="footer-title">Explora</div><a href="#" class="footer-link">Sobre Nosotros</a><a href="#" class="footer-link">Metodología de Datos</a><a href="#" class="footer-link">Términos de Uso</a><a href="#" class="footer-link">Política de Privacidad</a></div><div class="footer-col"><div class="footer-title">Observatorio Congreso</div><p class="copyright-text">&copy; 2026 Reservados todos los derechos.<br><br>Plataforma de análisis ciudadano basada en datos públicos de la Biblioteca del Congreso Nacional de Chile.<br>Diseñado con rigor y transparencia.</p></div></div>""",
    unsafe_allow_html=True
)
