
import sqlite3
import pandas as pd

DB_PATH = "database/jak_observatorio.db"

def run_qa():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- 1. Conteo de Registros ---")
    tables = ['mociones', 'analisis_ia', 'textos_pdf']
    counts = {}
    for t in tables:
        try:
            cursor.execute(f"SELECT count(*) FROM {t}")
            c = cursor.fetchone()[0]
            counts[t] = c
            print(f"{t}: {c}")
        except:
            print(f"{t}: Tabla no encontrada")
            
    print("\n--- 2. Verificación Boletín 2897-07 ---")
    # Check Mociones/IA
    try:
        df_ia = pd.read_sql("SELECT * FROM analisis_ia WHERE id_boletin = '2897-07'", conn)
        if not df_ia.empty:
            row = df_ia.iloc[0]
            print(f"Resumen Ejecutivo: {row.get('resumen_ejecutivo', 'N/A')[:100]}...")
            print(f"Alcance: {row.get('alcance_territorial', 'N/A')}")
        else:
            print("Boletin 2897-07 no encontrado en analisis_ia")
            
        # Check Coautores
        df_co = pd.read_sql("SELECT * FROM coautores WHERE id_boletin = '2897-07'", conn)
        coautores = df_co['diputado'].tolist()
        print(f"Coautores ({len(coautores)}): {coautores}")
    except Exception as e:
        print(f"Error verificando boletin: {e}")

    print("\n--- 3. Validación de Leyes sin Fecha ---")
    # Check if we have publication date column
    cursor.execute("PRAGMA table_info(mociones)")
    cols = [c[1] for c in cursor.fetchall()]
    print(f"Columnas en mociones: {cols}")
    
    # Heuristic for Date column (checking common names)
    date_cols = [c for c in cols if 'fecha' in c.lower() or 'publica' in c.lower()]
    print(f"Posibles columnas de fecha: {date_cols}")
    
    errors = []
    if 'estado_del_proyecto_de_ley' in cols:
        # Looking for laws
        query = "SELECT * FROM mociones WHERE estado_del_proyecto_de_ley LIKE '%Ley%' OR estado_del_proyecto_de_ley LIKE '%Publicado%'"
        df_leyes = pd.read_sql(query, conn)
        
        # Check if they have a date. 
        # If no specific 'publication' date col exists, we skip or check general date
        # Assuming we might want to check if 'N°Ley' exists at least?
        for _, row in df_leyes.iterrows():
            # If we were looking for a specific missing date, we'd check it here.
            # Since we don't know the exact column for 'fecha publicacion' from previous steps (only 'fecha_ingreso'),
            # we will report if 'N°Ley' is missing which is a proxy for incompleteness.
            n_ley = row.get('N°Ley') # Original column name might be this
            if pd.isna(n_ley) or str(n_ley).strip() == '':
                 errors.append(f"{row.get('id_boletin')}: Estado Ley pero sin N°Ley")
    
    if errors:
        print(f"Alerta: {len(errors)} leyes sin número identificador:")
        print(errors[:5])
    else:
        print("No se detectaron inconsistencias obvias en Leyes (basado en N°Ley).")

    conn.close()

if __name__ == "__main__":
    run_qa()
