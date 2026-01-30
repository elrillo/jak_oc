
import pandas as pd
import sqlite3
import os
import sys

# Import logic from build_dw if possible, but might be safer to reimplement specifically 
# to ensure column names are compatible with app.py
from build_dw import build_database as run_build_dw

DB_PATH = "database/jak_observatorio.db"

def clean_col_name(col):
    col = col.lower().strip()
    col = col.replace("n°", "n")
    col = col.replace("boletín", "boletin")
    col = col.replace(" ", "_")
    return col

def enrich_sqlite():
    print("1. Ejecutando build_dw para base...")
    # This creates 'mociones' and 'coautores' with original excel headers
    run_build_dw()
    
    conn = sqlite3.connect(DB_PATH)
    
    # 2. Rename columns in tables to match app expectations
    print("2. Normalizando columnas...")
    
    # Mociones
    try:
        df_moc = pd.read_sql("SELECT * FROM mociones", conn)
        # Rename 'N° Boletín' -> 'id_boletin'
        # Rename 'Nombre' -> 'nombre_iniciativa' (check excel cols)
        # Verify columns first
        print("Cols Mociones:", df_moc.columns)
        
        rename_map = {}
        for c in df_moc.columns:
            clean = clean_col_name(c)
            if "boletin" in clean: rename_map[c] = "id_boletin"
            elif "nombre" in clean or "materia" in clean: rename_map[c] = "nombre_iniciativa"
            elif "fecha" in clean and "ingreso" in clean: rename_map[c] = "fecha_ingreso"
            elif "estado" in clean: rename_map[c] = "estado_del_proyecto_de_ley"
            elif "comision" in clean: rename_map[c] = "comision_inicial"
        
        df_moc.rename(columns=rename_map, inplace=True)
        
        # --- NUEVO: Generar comision_inicial desde Etapa si no existe ---
        if 'comision_inicial' not in df_moc.columns and 'Etapa' in df_moc.columns:
            print("Generando columna comision_inicial desde Etapa...")
            # Regex extraction similar to app logic
            df_moc['comision_inicial'] = df_moc['Etapa'].astype(str).str.extract(r'(?i)Comisi[oó]n\s+de\s+([^/]+)', expand=False).str.strip()
        
        # Save back replacing
        df_moc.to_sql("mociones", conn, if_exists="replace", index=False)
        print("Mociones actualizadas.")
    except Exception as e:
        print(f"Error procesando mociones: {e}")

    # Coautores
    try:
        df_co = pd.read_sql("SELECT * FROM coautores", conn)
        # Rename 'N° Boletín' -> 'id_boletin', 'Diputado' -> 'diputado'
        print("Cols Coautores:", df_co.columns)
        rename_map_co = {}
        for c in df_co.columns:
            clean = clean_col_name(c)
            if "boletin" in clean: rename_map_co[c] = "id_boletin"
            elif "diputado" in clean: rename_map_co[c] = "diputado"
            
        df_co.rename(columns=rename_map_co, inplace=True)
        df_co.to_sql("coautores", conn, if_exists="replace", index=False)
        print("Coautores actualizados.")
    except Exception as e:
        print(f"Error procesando coautores: {e}")

    # 3. Populate dim_diputados
    print("3. Cargando dim_diputados...")
    path_xlsx = "data/archivos_csv/diputados_historicos.xlsx"
    if os.path.exists(path_xlsx):
        try:
            df_hist = pd.read_excel(path_xlsx, sheet_name="Diputados_Historico")
            # Rename columns
            # 'Diputado' -> 'diputado', 'Partido Politico' -> 'partido'...
            # App expects: 'diputado', 'partido'
            cols_map = {
                'Diputado': 'diputado',
                'Partido Politico': 'partido' 
            }
            # Keep only necessary or map all
            df_hist.rename(columns=cols_map, inplace=True)
            # Ensure safe col names for others
            df_hist.columns = [clean_col_name(c) for c in df_hist.columns]
            
            # Save
            df_hist.to_sql("dim_diputados", conn, if_exists="replace", index=False)
            print("dim_diputados cargada.")
        except Exception as e:
            print(f"Error leyendo diputados: {e}")
    else:
        print("NO se encontro diputados_historicos.xlsx")

    # 4. Populate analisis_ia (Mock)
    print("4. Generando analisis_ia (MOCK)...")
    try:
        # Get boletin IDs
        ids = pd.read_sql("SELECT id_boletin FROM mociones", conn)['id_boletin'].unique()
        
        # Create dummy data
        data = []
        for bid in ids:
            data.append({
                'id_boletin': bid,
                'resumen_ejecutivo': 'Resumen no disponible en modo offline (simulación local).',
                'tags_temas': "['Política', 'Legislación', 'General']", # Dummy JSON-like string
                'tipo_iniciativa': 'Moción',
                'sentimiento_score': 0.0
            })
        
        df_ia = pd.DataFrame(data)
        df_ia.to_sql("analisis_ia", conn, if_exists="replace", index=False)
        print("analisis_ia creada (mock).")
    except Exception as e:
        print(f"Error mockeando analisis_ia: {e}")

    conn.close()
    print("Enrich complete.")

if __name__ == "__main__":
    enrich_sqlite()
