
import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os
import ast

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Observatorio Congreso: Análisis JAK (Local)",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Estilos CSS Personalizados ---
st.markdown("""
<style>
    :root {
        --primary-blue: #0f2c4c;
        --secondary-gray: #f0f2f6;
        --accent-color: #2e86de;
    }
    .main-header {
        font-family: 'Helvetica Neue', sans-serif;
        color: var(--primary-blue);
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 5px solid var(--accent-color);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: var(--primary-blue);
    }
    .metric-label {
        font-size: 1rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #fff;
        border-radius: 4px;
        color: var(--primary-blue);
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-blue) !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Conexión a SQLite Local ---

# --- Conexión a SQLite Local ---

def conectar_db():
    # Intentar varias rutas comunes en servidores
    # __file__ gives us the path to the current script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    posibles_rutas = [
        'database/jak_observatorio.db', # Local dev, usually relative to cwd
        'jak_oc/database/jak_observatorio.db', # Sometimes useful in simple deployments
        os.path.join(base_dir, 'database', 'jak_observatorio.db'), # Absolute path based on script location
        os.path.join(base_dir, '..', 'database', 'jak_observatorio.db'), # One level up?
        # Absolute path fallback to what we know works locally
        "d:/Antigravity/jak_oc/database/jak_observatorio.db" 
    ]

    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            # st.write(f"DEBUG: Conectado a {ruta}") # Uncomment for debug
            return sqlite3.connect(ruta)

    # Si llega aquí, mostrar error con diagnóstico
    st.error("No se encontró la base de datos.")
    st.write("CWD:", os.getcwd())
    st.write("Base Dir:", base_dir)
    st.write("Directorios visibles:", os.listdir('.' if os.path.exists('.') else '/'))
    if os.path.exists('database'):
         st.write("Contenido database:", os.listdir('database'))
    return None


@st.cache_data
def load_data():
    conn = conectar_db()
    if conn is None:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        
    try:
        # Cargar Mociones
        try:
            df_mociones = pd.read_sql("SELECT * FROM mociones", conn)
        except: df_mociones = pd.DataFrame()
        
        # Cargar Coautores
        try:
            df_coautores = pd.read_sql("SELECT * FROM coautores", conn)
        except: df_coautores = pd.DataFrame()
        
        # Cargar Diputados
        try:
            df_diputados = pd.read_sql("SELECT * FROM dim_diputados", conn)
        except: df_diputados = pd.DataFrame()
        
        # Cargar Análisis IA
        try:
            df_ia = pd.read_sql("SELECT * FROM analisis_ia", conn)
        except: df_ia = pd.DataFrame()
        
        conn.close()
        return df_mociones, df_coautores, df_diputados, df_ia
    except Exception as e:
        st.error(f"Error leyendo la base de datos: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_mociones, df_coautores, df_diputados, df_ia = load_data()

# --- Normalización de Columnas (Fallback) ---
# Asegurar nombres consistentes si el renombramiento falló o varió
def ensure_cols(df, candidates, target):
    for c in candidates:
        if c in df.columns:
            df.rename(columns={c: target}, inplace=True)
            return

ensure_cols(df_mociones, ['N° Boletín', 'n_boletin'], 'id_boletin')
ensure_cols(df_coautores, ['N° Boletín', 'n_boletin'], 'id_boletin')
ensure_cols(df_coautores, ['Diputado'], 'diputado')
ensure_cols(df_diputados, ['Diputado'], 'diputado')
ensure_cols(df_diputados, ['Partido Politico', 'partido_politico'], 'partido')

# --- Procesamiento de Datos ---
TARGET_DEPUTY = "Jose Antonio Kast Rist"
TARGET_VARIANTS = ["Jose Antonio Kast Rist", "José Antonio Kast Rist", "Kast Rist Jose Antonio", "Kast Rist José Antonio"]

if not df_mociones.empty and not df_coautores.empty:
    # Identificar Key de JAK
    found_name = TARGET_DEPUTY
    # Verificar si está en coautores
    if found_name not in df_coautores['diputado'].unique():
        # Buscar variante
        for v in TARGET_VARIANTS:
            if v in df_coautores['diputado'].unique():
                found_name = v
                break
    
    # Filtrar boletines
    jak_projects = df_coautores[df_coautores['diputado'] == found_name]['id_boletin'].unique()
    
    # Filtrar Mociones
    df_main = df_mociones[df_mociones['id_boletin'].isin(jak_projects)].copy()
    
    # Merge con Analysis IA
    if not df_ia.empty and 'id_boletin' in df_ia.columns:
        df_main = df_main.merge(df_ia, on='id_boletin', how='left')
    
    # Métricas
    total_proyectos = len(df_main)
    
    # Efectividad
    col_estado = 'estado_del_proyecto_de_ley' if 'estado_del_proyecto_de_ley' in df_main.columns else 'Estado'
    if col_estado in df_main.columns:
        leyes_aprobadas = df_main[df_main[col_estado].str.contains('Ley|Publicado', case=False, na=False)]
        effectiveness = (len(leyes_aprobadas) / total_proyectos * 100) if total_proyectos > 0 else 0
    else:
        effectiveness = 0
    
    # Aliado
    coautores_jak = df_coautores[df_coautores['id_boletin'].isin(jak_projects)]
    coautores_jak = coautores_jak[coautores_jak['diputado'] != found_name]
    
    if not coautores_jak.empty:
        top_ally = coautores_jak['diputado'].mode()[0]
    else:
        top_ally = "N/A"

else:
    st.warning("Datos insuficientes para el análisis.")
    st.stop()

# --- Interfaz ---

st.markdown("<h1 class='main-header'>Observatorio Congreso: Análisis José Antonio Kast</h1>", unsafe_allow_html=True)
st.markdown("---")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_proyectos}</div><div class='metric-label'>Total Proyectos</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-card'><div class='metric-value'>{effectiveness:.1f}%</div><div class='metric-label'>Efectividad</div></div>", unsafe_allow_html=True)
with col3:
    display_ally = top_ally.split()[0] + " " + top_ally.split()[-2] if len(top_ally.split()) > 2 else top_ally
    st.markdown(f"<div class='metric-card'><div class='metric-value' style='font-size:1.8rem'>{display_ally}</div><div class='metric-label'>Aliado Principal</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 Análisis Político", "📜 Contenido Legislativo"])

with tab1:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Evolución Temporal")
        if 'fecha_ingreso' in df_main.columns:
            df_main['fecha_ingreso'] = pd.to_datetime(df_main['fecha_ingreso'], errors='coerce')
            df_time = df_main.groupby(df_main['fecha_ingreso'].dt.year).size().reset_index(name='count')
            fig = px.bar(df_time, x='fecha_ingreso', y='count', labels={'fecha_ingreso': 'Año', 'count': 'Cant.'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos de fecha.")
            
    with col_b:
        st.subheader("Red de Alianzas (Partidos)")
        # Merge coautores with diputados table to get party
        if not df_diputados.empty and 'partido' in df_diputados.columns:
            df_net = coautores_jak.merge(df_diputados, on='diputado', how='left')
            party_counts = df_net['partido'].value_counts().reset_index()
            party_counts.columns = ['Partido', 'Cantidad']
            fig_p = px.bar(party_counts, y='Partido', x='Cantidad', orientation='h', color='Cantidad')
            st.plotly_chart(fig_p, use_container_width=True)
        else:
            st.warning("No hay datos de partidos disponibles en dim_diputados.")

    st.markdown("---")
    st.subheader("Temas Recurrentes (Treemap)")
    # Parse tags
    all_tags = []
    if 'tags_temas' in df_main.columns:
        for tags in df_main['tags_temas'].dropna():
            try:
                # If it's a string representation of list
                if isinstance(tags, str) and tags.startswith('['):
                     # Safe eval or manual parse
                     import ast
                     t_list = ast.literal_eval(tags)
                     if isinstance(t_list, list): all_tags.extend(t_list)
                else: 
                     all_tags.append(str(tags))
            except: pass
            
        if all_tags:
            tag_counts = pd.Series(all_tags).value_counts().head(15).reset_index()
            tag_counts.columns = ['Tema', 'Frecuencia']
            fig_tree = px.treemap(tag_counts, path=['Tema'], values='Frecuencia', color='Frecuencia')
            st.plotly_chart(fig_tree, use_container_width=True)
        else:
            st.info("No hay tags para visualizar.")
    else:
        st.info("Columna 'tags_temas' no encontrada.")

with tab2:
    st.subheader("Buscador de Proyectos")
    search = st.text_input("Buscar:", "")
    
    view_df = df_main.copy()
    if search:
        mask = view_df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
        view_df = view_df[mask]
    
    st.write(f"Resultados: {len(view_df)}")
    
    for idx, row in view_df.iterrows():
        title = row.get('nombre_iniciativa', row.get('Nombre', 'Sin Título'))
        with st.expander(f"{row['id_boletin']} - {title[:80]}..."):
            st.markdown(f"**Resumen IA:** {row.get('resumen_ejecutivo', 'No disponible')}")
            
            # Coautores
            these_coauthors = df_coautores[df_coautores['id_boletin'] == row['id_boletin']]['diputado'].tolist()
            # Remove self
            if found_name in these_coauthors: these_coauthors.remove(found_name)
            
            st.markdown(f"**Coautores ({len(these_coauthors)}):** {', '.join(these_coauthors[:10])} {'...' if len(these_coauthors)>10 else ''}")
            st.caption(f"Tipo: {row.get('tipo_iniciativa', 'N/A')} | Estado: {row.get('estado_del_proyecto_de_ley', 'N/A')}")
