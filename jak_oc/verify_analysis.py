
import psycopg2

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def verify():
    conn = None
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        print("Connected for verification.")

        # Find valid title column
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'mociones'")
        cols = [c[0] for c in cursor.fetchall()]
        print(f"Columns in mociones: {cols}")
        
        # Priority list for title
        # Based on inspection: 'nombre_iniciativa'
        candidates = ['nombre_iniciativa', 'titulo', 'materia', 'nombre', 'descripcion']
        title_col = None
        for c in candidates:
            if c in cols:
                title_col = c
                break
        
        if not title_col:
            # If not found in cols list (which might be imperfect), force it based on recent finding
            title_col = 'nombre_iniciativa'
        
        print(f"Using '{title_col}' as title column.")
        
        print(f"Using '{title_col}' as title column.")

        query = f"""
        SELECT a.id_boletin, m.{title_col}, a.tipo_iniciativa, a.tags_temas, a.resumen_ejecutivo, a.sentimiento_score
        FROM analisis_ia a
        JOIN mociones m ON a.id_boletin = m.n_boletin
        LIMIT 5;
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        print(f"\n--- Verification Top 5 ({len(rows)} found) ---")
        for i, r in enumerate(rows):
            bol_id, title, tipo, tags, resumen, score = r
            
            # SAFE PRINTING
            title_str = (title[:100] + "...") if title else "NO TITLE found"
            resumen_str = (resumen[:150] + "...") if resumen else "NO SUMMARY"
            
            print(f"\nResult {i+1}:")
            print(f"  Boletín: {bol_id}")
            print(f"  Título: {title_str}")
            print(f"  Tipo: {tipo} | Sentimiento: {score}")
            print(f"  Tags: {tags}")
            print(f"  Resumen: {resumen_str}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    verify()
