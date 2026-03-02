import os
import pandas as pd
import psycopg2

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def upload_summaries():
    csv_path = os.path.join("data", "archivos_csv", "mociones_255_corregidas_final.csv")
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    
    if 'resumen_ia' not in df.columns or 'n_boletin' not in df.columns:
        print("CSV does not have expected columns 'n_boletin' and 'resumen_ia'. Found:", df.columns.tolist())
        return
        
    # We will only keep rows that have a non-empty summary
    df_valid = df.dropna(subset=['resumen_ia', 'n_boletin'])
    total = len(df_valid)
    print(f"Reading {total} valid summaries to upload...")
    
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    
    # Ensure column exists
    cursor.execute("ALTER TABLE textos_pdf ADD COLUMN IF NOT EXISTS resumen_ia TEXT")
    conn.commit()
    
    updated_count = 0
    errors = 0
    
    for index, row in df_valid.iterrows():
        boletin = str(row['n_boletin']).strip()
        resumen = str(row['resumen_ia']).strip()
        
        if not boletin or not resumen:
            continue
            
        try:
            cursor.execute(
                "UPDATE textos_pdf SET resumen_ia = %s WHERE n_boletin = %s",
                (resumen, boletin)
            )
            # A veces PostgreSQL no actualiza si el n_boletin está formateado diferente en el DB
            if cursor.rowcount == 0:
                cursor.execute(
                    "UPDATE textos_pdf SET resumen_ia = %s WHERE n_boletin LIKE %s",
                    (resumen, f"%{boletin}%")
                )
            updated_count += 1
        except Exception as e:
            print(f"Error procesando {boletin}: {e}")
            conn.rollback()
            errors += 1
            
    conn.commit()
    print("\n--- CARGA FINALIZADA ---")
    print(f"Resúmenes cargados con éxito: {updated_count}")
    print(f"Errores: {errors}")

    # VERIFY DB
    cursor.execute("SELECT count(*) FROM textos_pdf WHERE resumen_ia IS NOT NULL AND resumen_ia != ''")
    db_count = cursor.fetchone()[0]
    print(f"Conteo final en la base de datos de resúmenes IA: {db_count} / 255")

    conn.close()

if __name__ == "__main__":
    upload_summaries()
