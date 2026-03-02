import os
import psycopg2
import time
import google.generativeai as genai

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

# Configure Gemini
API_KEY = "AIzaSyCCWXCYaxoeVmmbWFvag6tMgRbr46_Cwec" # Provided by user
genai.configure(api_key=API_KEY)

# We use gemini-1.5-flash as it's the fastest and cheapest for this kind of processing
model = genai.GenerativeModel('gemini-1.5-flash')

def get_summary(text):
    prompt = """
    Resume la siguiente moción legislativa en máximo 150 palabras. 
    Céntrate EXCLUSIVAMENTE en el contenido, materia legislativa y objetivo de la propuesta. 
    NO incluyas nombres de diputados, firmas, fechas de presentación/publicación, links ni menciones a 'observatoriocongreso.cl'. 
    El tono debe ser objetivo y directo.
    
    Texto de la moción:
    """ + text

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error llamando a Gemini: {e}")
        return None

def process_summaries():
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = False
    cursor = conn.cursor()

    # Create the column if it doesn't exist
    cursor.execute("ALTER TABLE textos_pdf ADD COLUMN IF NOT EXISTS resumen_ia TEXT")
    conn.commit()

    # Select texts that don't have a summary yet
    cursor.execute("SELECT n_boletin, texto_mocion FROM textos_pdf WHERE resumen_ia IS NULL OR resumen_ia = ''")
    rows = cursor.fetchall()
    
    total = len(rows)
    print(f"Buscando resúmenes para {total} mociones...")

    updated_count = 0
    errors = 0

    for idx, (boletin, texto) in enumerate(rows, 1):
        print(f"[{idx}/{total}] Procesando Boletín {boletin}...")
        
        if not texto or len(texto.strip()) < 50:
            print(f"  -> Texto muy corto o nulo, omitiendo.")
            continue
            
        summary = get_summary(texto)
        
        if summary:
            try:
                cursor.execute(
                    "UPDATE textos_pdf SET resumen_ia = %s WHERE n_boletin = %s",
                    (summary, boletin)
                )
                conn.commit()
                updated_count += 1
                print(f"  -> Resumen guardado ({len(summary.split())} palabras).")
            except Exception as e:
                print(f"  -> Error guardando en BD: {e}")
                conn.rollback()
                errors += 1
        else:
            errors += 1
            
        # Free tier rate limit consideration: 15 requests per minute usually.
        # So we sleep 4-5 seconds between requests to be safe.
        time.sleep(4.5)

    print(f"\n--- PROCESO TERMINADO ---")
    print(f"Resúmenes generados y guardados: {updated_count}")
    print(f"Errores encontrados: {errors}")

    conn.close()

if __name__ == "__main__":
    process_summaries()
