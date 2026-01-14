import pandas as pd
from supabase import create_client, Client
import unidecode
import os
import psycopg2

# Configuración de Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://tbniuckpxxzphturwnaj.supabase.co")
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRibml1Y2tweHh6cGh0dXJ3bmFqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDUzNDUwMSwiZXhwIjoyMDgwMTEwNTAxfQ.q0Q6cxsOxOTYrVblVC1YMqMqKtKdMWVWSMXXIJR0x2A"

# Conexión Directa para crear tabla (DDL)
DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Error inicializando Supabase: {e}")
    exit(1)

def limpiar_texto(texto):
    """Limpia tildes, mayúsculas y espacios para asegurar el match de nombres."""
    if not isinstance(texto, str): return ""
    texto = unidecode.unidecode(texto).lower().strip()
    return " ".join(texto.split())

def create_dim_table():
    """Crea la tabla dim_diputados si no existe usando psycopg2"""
    print("Verificando existencia de tabla 'dim_diputados'...")
    create_sql = """
    CREATE TABLE IF NOT EXISTS dim_diputados (
        diputado TEXT,
        sexo TEXT,
        partido_politico TEXT,
        bancada_comite TEXT,
        coalicion TEXT,
        region TEXT,
        distrito TEXT,
        periodo TEXT,
        PRIMARY KEY (diputado, periodo)
    );
    """
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        cursor.execute(create_sql)
        conn.commit()
        conn.close()
        print("Tabla 'dim_diputados' verificada/creada correctamente.")
    except Exception as e:
        print(f"Error creando tabla SQL: {e}")

def cargar_historico_enriquecido():
    # Paso previo: Crear tabla
    create_dim_table()

    print("--- Cargando Diputados Históricos desde XLSX ---")
    
    # 1. Leer el archivo Excel
    path_xlsx = "data/archivos_csv/diputados_historicos.xlsx"
    if not os.path.exists(path_xlsx):
        print(f"Error: No se encuentra el archivo {path_xlsx}")
        return

    try:
        xls = pd.ExcelFile(path_xlsx)
        if "Diputados_Historico" not in xls.sheet_names:
            print(f"Error: La hoja 'Diputados_Historico' no existe.")
            return
            
        df_hist = pd.read_excel(xls, sheet_name="Diputados_Historico")
    except Exception as e:
        print(f"Error leyendo Excel: {e}")
        return
    
    # 2. Obtener los nombres de coautores que YA están en Supabase para validar
    print("Validando contra tabla de coautores existente...")
    try:
        res = supabase.table("coautores").select("diputado").execute()
        if res.data and 'diputado' in res.data[0]:
             nombres_app = {limpiar_texto(n['diputado']): n['diputado'] for n in res.data}
        else:
             nombres_app = {limpiar_texto(n.get('Diputado', '')): n.get('Diputado', '') for n in res.data}
    except Exception as e:
        print(f"Error consultando Supabase (coautores): {e}")
        return
    
    # 3. Preparar la tabla de dimensión (diputados)
    if 'Diputado' not in df_hist.columns:
        print(f"Columna 'Diputado' no encontrada.")
        return

    df_hist['nombre_limpio'] = df_hist['Diputado'].apply(limpiar_texto)
    df_hist['match_en_app'] = df_hist['nombre_limpio'].isin(nombres_app.keys())
    coincidencias = df_hist[df_hist['match_en_app'] == True]
    
    print(f"Match exitoso: {len(coincidencias['nombre_limpio'].unique())} diputados encontrados.")

    # 4. Limpieza de columnas para Supabase
    columnas_interes = [
        'Diputado', 'Sexo ', 'Partido Politico', 'Bancada/Comite', 
        'Coalicion', 'Región', 'Distrito', 'Periodo'
    ]
    
    # Filtrar columnas existentes
    columnas_interes = [c for c in columnas_interes if c in df_hist.columns]
    df_final = df_hist[columnas_interes].copy()
    
    # Normalizard nombres de columnas (ASCII, lowercase, snake)
    # Región -> region
    def clean_col(c):
        c = unidecode.unidecode(c) # Tildes fuera
        return c.strip().replace(" ", "_").replace("/", "_").lower()
    
    df_final.columns = [clean_col(c) for c in df_final.columns]

    # 5. Subir a Supabase (Tabla: dim_diputados)
    df_final = df_final.where(pd.notnull(df_final), None)
    data_upload = df_final.to_dict(orient='records')
    
    print(f"Subiendo {len(data_upload)} registros a la tabla 'dim_diputados'...")
    
    batch_size = 200
    try:
        for i in range(0, len(data_upload), batch_size):
            batch = data_upload[i:i+batch_size]
            response = supabase.table("dim_diputados").upsert(batch).execute()
        print("--- Carga de dimensiones completada ---")
    except Exception as e:
        error_msg = f"Error subiendo datos: {e}"
        print(error_msg)
        with open("upload_error_log.txt", "w", encoding="utf-8") as f:
            f.write(str(e))
            if hasattr(e, 'message'):
                f.write(f"\nMessage: {e.message}")
            if hasattr(e, 'code'):
                f.write(f"\nCode: {e.code}")
            if hasattr(e, 'details'):
                f.write(f"\nDetails: {e.details}")

if __name__ == "__main__":
    cargar_historico_enriquecido()
