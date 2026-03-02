import psycopg2
import csv

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def export_to_csv():
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    
    cursor.execute("SELECT n_boletin, texto_mocion FROM textos_pdf")
    rows = cursor.fetchall()
    
    with open("mociones_textos_export.csv", "w", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["n_boletin", "texto_mocion", "prompt_sugerido"])
        for r in rows:
            boletin = r[0]
            texto = str(r[1]).replace("\n", " ").replace("\r", " ")
            # Optional: We could truncate if it's too large, but CSV handles it fine
            prompt = f"Resume la siguiente moción legislativa (Boletín {boletin}) en máximo 150 palabras. Céntrate exclusivamente en el contenido y objetivo de la propuesta. No incluyas nombres de diputados, fechas, links u otros metadatos. Texto: "
            writer.writerow([boletin, texto, prompt])
            
    print(f"Exportados {len(rows)} registros a mociones_textos_export.csv")
    conn.close()

if __name__ == "__main__":
    export_to_csv()
