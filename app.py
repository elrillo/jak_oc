
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os
import ast
from datetime import datetime

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Presidente Kast | Análisis Legislativo",
    page_icon="🇨🇱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Estilos CSS: Tema Serio / Dark Mode / Serif ---
st.markdown("""
<style>
    /* Importar Fuentes Serif Premium */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Merriweather:wght@300;400;700&display=swap');
    
    /* Variables de Color - Dark Mode Serio */
    :root {
        --bg-color: #0a0a0a;
        --card-bg: #141414;
        --text-main: #e0e0e0;
        --text-muted: #a0a0a0;
        --accent: #c0392b; /* Rojo sobrio o Dorado */
        --border-color: #333;
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
    }
    
    /* HEADER PERSONALIZADO */
    .hero-banner {
        padding: 40px 20px;
        background: linear-gradient(to bottom, #000000 0%, #1a1a1a 100%);
        border-bottom: 3px solid var(--border-color);
        text-align: center;
        margin-bottom: 20px;
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        letter-spacing: 1px;
        margin-bottom: 5px;
        color: white;
    }
    .hero-subtitle {
        font-size: 1.2rem;
        color: var(--text-muted);
        font-style: italic;
        font-family: 'Playfair Display', serif;
    }
    .hero-img {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #555;
        margin-bottom: 15px;
    }

    /* COMPONENTES */
    .metric-card {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        padding: 20px;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-value {
        font-family: 'Playfair Display', serif;
        font-size: 2.2rem;
        color: white;
        font-weight: 700;
    }
    .metric-label {
        font-family: 'Merriweather', serif;
        text-transform: uppercase;
        font-size: 0.8rem;
        letter-spacing: 1px;
        color: var(--text-muted);
        margin-top: 5px;
    }

    /* Tabs Styling - Horizontal Menu overwrite */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #111;
        padding: 5px;
        border-bottom: 1px solid #333;
    }
    .stTabs [data-baseweb="tab"] {
        height: auto;
        padding: 10px 20px;
        background-color: transparent;
        color: #888;
        font-family: 'Playfair Display', serif;
        font-weight: 600;
        border: none;
        border-bottom: 2px solid transparent;
        border-radius: 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1a1a1a !important;
        color: white !important;
        border-bottom: 2px solid #fff !important;
    }
    
    /* Footer */
    .footer {
        margin-top: 50px;
        padding: 30px;
        border-top: 1px solid #333;
        text-align: center;
        font-size: 0.9rem;
        color: #666;
        background-color: #050505;
    }
    .footer a {
        color: #888;
        text-decoration: none;
        margin: 0 10px;
    }
    .footer a:hover {
        color: white;
    }
    
    /* Ajustes generales de Streamlit Containers */
    div[data-testid="stExpander"] {
        background-color: var(--card-bg);
        border: 1px solid #333;
    }
    div[data-testid="stExpander"] p {
        color: #ccc;
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
        df_m[col_fecha] = pd.to_datetime(df_m[col_fecha], errors='coerce')
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
# Usamos columnas para centrar imagen y texto
# URL Placeholder fiable de JAK para el ejemplo.
jak_image_url = "https://www.camara.cl/img.aspx?prmID=841" # Foto oficial camara baja
# Si falla, fallback a un icono.
st.markdown(f"""
<div class='hero-banner'>
    <img src='{jak_image_url}' class='hero-img' onerror="this.onerror=null; this.src='https://cdn-icons-png.flaticon.com/512/21/21104.png'">
    <div class='hero-title'>ANÁLISIS LEGISLATIVO</div>
    <div class='hero-subtitle'>Presidente José Antonio Kast</div>
</div>
""", unsafe_allow_html=True)


# --- NAVEGACIÓN HORIZONTAL (TABS) ---
tabs_titles = [
    "RESUMEN", 
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
        <div class='metric-value'>{value}</div>
        <div class='metric-label'>{title}</div>
        <div style='font-size:0.8rem; color:#666; margin-top:5px'>{subtitle}</div>
    </div>
    """
    if col: col.markdown(html, unsafe_allow_html=True)
    else: st.markdown(html, unsafe_allow_html=True)

# Dark Plotly Template
pio_template = "plotly_dark"

# --- CONTENIDO ---

# 1. RESUMEN
with tabs[0]:
    st.markdown("### Panorama General")
    st.markdown("---")
    
    total = len(df_main)
    leyes = len(df_main[df_main['estado_del_proyecto_de_ley'].str.contains('Ley|Publicado', case=False, na=False)]) if 'estado_del_proyecto_de_ley' in df_main.columns else 0
    
    co_auth_all = get_coauthors_for_boletines(df_main['id_boletin'].unique())
    co_auth_all = co_auth_all[co_auth_all['diputado'] != found_name]
    top_ally = co_auth_all['diputado'].mode()[0] if not co_auth_all.empty else "N/A"
    
    c1, c2, c3 = st.columns(3)
    kpi_card("Total Iniciativas", total, "Durante carrera parlamentaria", c1)
    kpi_card("Leyes Aprobadas", leyes, f"Tasa de éxito: {(leyes/total*100):.1f}%", c2)
    kpi_card("Aliado Histórico", top_ally, "Mayor colaborador", c3)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if 'anio' in df_main.columns:
        yearly = df_main.groupby('anio').size().reset_index(name='Proyectos')
        fig = px.bar(yearly, x='anio', y='Proyectos', title="Producción Legislativa Anual", template=pio_template)
        fig.update_traces(marker_color='#555')
        st.plotly_chart(fig, use_container_width=True)

# 2. PERIODOS
with tabs[1]:
    st.markdown("### Desglose por Periodo Legislativo")
    st.markdown("---")
    available_periods = sorted(df_main['periodo'].unique().tolist()) if 'periodo' in df_main.columns else []
    
    if available_periods:
        selected_period = st.pills("Seleccione Periodo", available_periods, default=available_periods[0]) if hasattr(st, "pills") else st.selectbox("Seleccione Periodo", available_periods)
        
        if selected_period:
            df_p = df_main[df_main['periodo'] == selected_period]
            st.write("") # Spacer
            
            p_total = len(df_p)
            p_leyes = df_p['estado_del_proyecto_de_ley'].str.contains('Ley|Publicado', case=False, na=False).sum() if 'estado_del_proyecto_de_ley' in df_p.columns else 0
            
            col_p1, col_p2 = st.columns(2)
            kpi_card("Iniciativas del Periodo", p_total, selected_period, col_p1)
            kpi_card("Leyes del Periodo", p_leyes, "Aprobadas", col_p2)
            
            st.markdown("#### Temas en este periodo")
            # Tag Cloud simple or list
            all_tags_p = []
            if 'tags_temas' in df_p.columns:
                for tags in df_p['tags_temas'].dropna():
                     try:
                        if isinstance(tags, str) and tags.startswith('['):
                            t_list = ast.literal_eval(tags)
                            if isinstance(t_list, list): all_tags_p.extend(t_list)
                     except: pass
            
            if all_tags_p:
                tags_df = pd.Series(all_tags_p).value_counts().head(10)
                st.bar_chart(tags_df)

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
    st.markdown("### Trabajo en Comisiones")
    st.caption("Análisis basado en la 'Comisión Inicial' registrada.")
    
    if 'comision_inicial' in df_main.columns:
        df_com = df_main.copy()
        
        # Limpieza básica
        df_com['comision_inicial'] = df_com['comision_inicial'].fillna("").astype(str)
        df_com = df_com[df_com['comision_inicial'] != ""] # Filtrar vacíos si los hay
        
        if not df_com.empty:
            com_counts = df_com['comision_inicial'].value_counts().reset_index()
            com_counts.columns = ['Comision', 'Frecuencia']
            
            # Treemap
            fig = px.treemap(com_counts.head(40), path=['Comision'], values='Frecuencia', title="Proyectos por Comisión Legislativa", template=pio_template, color_discrete_sequence=px.colors.sequential.Greys)
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabla reducida
            with st.expander("Ver detalle de distribución"):
                st.dataframe(com_counts, use_container_width=True, hide_index=True)
        else:
            st.warning("No hay datos de comisiones disponibles para visualizar.")
    else:
        st.error("No se encontró la columna 'comision_inicial' en la base de datos.")

# 5. DATOS (Deep Dive)
with tabs[4]:
    st.markdown("### Red de Influencia Política")
    st.caption("Visualización jerárquica: JAK (Centro) > Partidos > Diputados Coautores.")
    
    coautores_jak = get_coauthors_for_boletines(df_main['id_boletin'].unique())
    coautores_jak = coautores_jak[coautores_jak['diputado'] != found_name]
    
    if not coautores_jak.empty and not df_diputados.empty and 'partido' in df_diputados.columns:
        # Preparar Data para Sunburst
        # Estructura: Root -> Partido -> Diputado -> Tamaño (Votos/Proyectos)
        df_net = coautores_jak.merge(df_diputados, on='diputado', how='left')
        
        # Limpiar partidos nulos
        df_net['partido'] = df_net['partido'].fillna("Sin Partido Registrado")
        
        # Agrupar
        df_sunburst = df_net.groupby(['partido', 'diputado']).size().reset_index(name='proyectos_compartidos')
        df_sunburst['root'] = "J.A. Kast" # Nodo Central
        
        # Gráfico Sunburst (Nodos concéntricos)
        fig_sun = px.sunburst(df_sunburst, path=['root', 'partido', 'diputado'], values='proyectos_compartidos',
                              title="Constelación de Coautorías",
                              template=pio_template,
                              color='proyectos_compartidos',
                              color_continuous_scale='Viridis')
        
        st.plotly_chart(fig_sun, use_container_width=True, height=700)
        
        st.markdown("#### Top Aliados por Partido")
        c1, c2 = st.columns([1, 2])
        with c1:
            st.dataframe(df_sunburst[['partido', 'diputado', 'proyectos_compartidos']].sort_values('proyectos_compartidos', ascending=False).head(10), hide_index=True, use_container_width=True)
            
    else:
        st.warning("Datos insuficientes para generar el gráfico de red. Verifique la carga de 'dim_diputados'.")

# 6. ESTADO Y TIEMPOS
with tabs[5]:
    st.markdown("### Ciclo de Vida y Tiempos de Tramitación")
    
    # --- MAPPING ETAPAS ---
    def map_stage(etapa_txt, estado_txt):
        txt = str(etapa_txt).lower()
        est = str(estado_txt).lower()
        
        if "publicado" in est or "ley" in est: return "4. Publicado (Ley)"
        if "archivado" in est or "retirado" in est: return "4. Archivado/Retirado"
        
        if "segundo tr" in txt or "revisora" in txt: return "2. Segundo Trámite"
        if "tercer" in txt or "mixta" in txt or "veto" in txt or "oficio" in txt: return "3. Tercer Trámite / Final"
        
        # Default fallback
        return "1. Primer Trámite"

    if 'estado_del_proyecto_de_ley' in df_main.columns:
        # Prepare Data
        df_status = df_main.copy()
        
        # Ensure regex/columns exist
        col_etapa = 'etapa' if 'etapa' in df_status.columns else 'estado_del_proyecto_de_ley' # Fallback
        
        df_status['etapa_norm'] = df_status.apply(lambda x: map_stage(x.get(col_etapa, ''), x['estado_del_proyecto_de_ley']), axis=1)
        
        # 1. VISUALIZACIÓN DE FLUJO (Bar Chart Ordenado)
        st.markdown("#### 🔄 Flujo de Proyectos")
        stage_counts = df_status['etapa_norm'].value_counts().sort_index().reset_index()
        stage_counts.columns = ['Etapa', 'Cantidad']
        
        # Color specific for Published
        colors = {'1. Primer Trámite': '#95a5a6', '2. Segundo Trámite': '#3498db', '3. Tercer Trámite / Final': '#f39c12', '4. Publicado (Ley)': '#2ecc71', '4. Archivado/Retirado': '#e74c3c'}
        
        fig_st = px.bar(stage_counts, x='Etapa', y='Cantidad', color='Etapa', 
                       color_discrete_map=colors, 
                       text='Cantidad',
                       template=pio_template, title="Distribución por Etapa Legislativa")
        st.plotly_chart(fig_st, use_container_width=True)
        
        # 2. TABLA DETALLADA
        st.markdown("#### 📋 Detalle de Proyectos por Etapa")
        with st.expander("Ver lista de proyectos"):
            st.dataframe(df_status[['id_boletin', 'nombre_iniciativa', 'etapa_norm', 'estado_del_proyecto_de_ley', 'fecha_ingreso']].sort_values('fecha_ingreso', ascending=False), use_container_width=True)

        st.markdown("---")
        
        # 3. ANÁLISIS DE TIEMPOS (Subsección)
        st.markdown("### ⏳ Tiempos de Tramitación (Leyes Aprobadas)")
        
        # Check dates
        col_pub = 'publicado_en_diario_oficial'
        if col_pub in df_status.columns:
            df_leyes_times = df_status[df_status['etapa_norm'] == "4. Publicado (Ley)"].copy()
            df_leyes_times[col_pub] = pd.to_datetime(df_leyes_times[col_pub], errors='coerce')
            df_leyes_times['fecha_ingreso'] = pd.to_datetime(df_leyes_times['fecha_ingreso'], errors='coerce')
            
            df_leyes_times = df_leyes_times.dropna(subset=[col_pub, 'fecha_ingreso'])
            df_leyes_times['dias_tramitacion'] = (df_leyes_times[col_pub] - df_leyes_times['fecha_ingreso']).dt.days
            
            if not df_leyes_times.empty:
                avg_days = df_leyes_times['dias_tramitacion'].mean()
                max_days = df_leyes_times['dias_tramitacion'].max()
                min_days = df_leyes_times['dias_tramitacion'].min()
                
                c_t1, c_t2, c_t3 = st.columns(3)
                kpi_card("Promedio de Días", f"{int(avg_days)}", "Desde ingreso a publicación", c_t1)
                kpi_card("Más Rápido", f"{int(min_days)} días", "Tramitación express", c_t2)
                kpi_card("Más Lento", f"{int(max_days)} días", "Tramitación extensa", c_t3)
                
                # Scatter Plot Time
                fig_time = px.scatter(df_leyes_times, x='fecha_ingreso', y='dias_tramitacion', 
                                     size='dias_tramitacion', color='dias_tramitacion',
                                     hover_data=['nombre_iniciativa'],
                                     title="Tiempo de Tramitación vs Fecha de Ingreso",
                                     template=pio_template,
                                     color_continuous_scale='Viridis')
                st.plotly_chart(fig_time, use_container_width=True)
            else:
                st.info("No hay suficientes datos de fechas para calcular tiempos de leyes publicadas.")
        else:
            st.warning("No se encontró columna de fecha de publicación.")
            
    else:
        st.error("Datos de estado no disponibles.")

# 7. LEYES
with tabs[6]:
    st.markdown("### Leyes de la República")
    if 'estado_del_proyecto_de_ley' in df_main.columns:
        df_leyes = df_main[df_main['estado_del_proyecto_de_ley'].str.contains('Ley|Publicado', case=False, na=False)]
        
        if df_leyes.empty:
            st.info("No se encontraron leyes publicadas.")
        else:
            for i, row in df_leyes.iterrows():
                st.markdown(f"#### {row['id_boletin']}: {row['nombre_iniciativa']}")
                st.caption(f"Publicado: {row.get('fecha_ingreso')} - {row.get('tipo_iniciativa')}")
                st.markdown("---")

# 8. EXPLORADOR
with tabs[7]:
    st.markdown("### Buscador Avanzado")
    search = st.text_input("Buscar en título o resumen...", placeholder="Ej: Araucanía, Impuestos, Familia")
    df_ex = df_main.copy()
    if search:
        df_ex = df_ex[df_ex.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
    st.dataframe(df_ex[['id_boletin', 'nombre_iniciativa', 'fecha_ingreso', 'estado_del_proyecto_de_ley']], use_container_width=True, hide_index=True)

# --- FOOTER ---
st.markdown("""
<div class='footer'>
    <p>Observatorio Legislativo - Análisis Independiente</p>
    <p>
        <a href='#'>Metodología</a> | 
        <a href='#'>Fuente de Datos</a> | 
        <a href='#'>Contacto</a>
    </p>
    <p style='font-size:0.8rem; margin-top:20px; color:#444'>
        &copy; 2026 Reservados todos los derechos. Datos obtenidos de Biblioteca del Congreso Nacional.
    </p>
</div>
""", unsafe_allow_html=True)
