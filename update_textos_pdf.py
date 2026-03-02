import os
import json
import re
import psycopg2

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def extract_boletin_id(title):
    # Match normally "3064-06"
    match = re.search(r'(\d+)-(\d+)', title)
    if match:
        return f"{match.group(1)}-{match.group(2)}"
        
    # Match lacking dash "690907" -> assumes last 2 digits are the second part
    match = re.search(r'(\d+)(\d{2})\b', title)
    if match:
        return f"{match.group(1)}-{match.group(2)}"
        
    return None

def update_db():
    json_dir = os.path.join("data", "archivos_json")
    if not os.path.exists(json_dir):
        print(f"Directory {json_dir} does not exist.")
        return

    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()

    files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
    updated_count = 0

    print(f"Evaluando {len(files)} archivos JSON locales...")

    for filename in files:
        filepath = os.path.join(json_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        title = data.get("title", "")
        text = data.get("text", "")
        
        # PostgreSQL cannot store \x00 characters inside a TEXT or VARCHAR field. 
        # DocumentCloud OCR frequently embeds \u0000. We must clean it.
        text = text.replace('\x00', '').replace('\u0000', '')
        
        boletin_id = extract_boletin_id(title)
        
        if boletin_id and text:
            # Explicit update
            query = """
                UPDATE textos_pdf 
                SET texto_mocion = %s 
                WHERE n_boletin = %s AND (length(texto_mocion) < 50 OR texto_mocion = 'PDF no encontrado');
            """
            try:
                cursor.execute(query, (text, boletin_id))
                updated_rows = cursor.rowcount
                if updated_rows > 0:
                    updated_count += updated_rows
                else:
                    # Let's try matching with space padding just in case
                    query2 = "UPDATE textos_pdf SET texto_mocion = %s WHERE n_boletin LIKE %s;"
                    cursor.execute(query2, (text, f"%{boletin_id}%"))
                    if cursor.rowcount > 0:
                        updated_count += cursor.rowcount
                    else:
                        print(f"Skipping {filename}: matched ID {boletin_id} but couldn't find it in DB to update")
            except Exception as e:
                print(f"Error procesando boletín {boletin_id} ({filename}): {e}")
                conn.rollback()
        else:
            print(f"Skipping {filename}, couldnt find boletín ID or text.")

    conn.commit()
    print(f"--- ¡Proceso finalizado! ---")
    print(f"Se actualizaron/insertaron exitosamente {updated_count} documentos en Supabase.")

    # GENERAR REPORTE
    cursor.execute("SELECT n_boletin FROM mociones")
    total_mociones = [str(r[0]) for r in cursor.fetchall()]
    
    cursor.execute("SELECT n_boletin FROM textos_pdf")
    con_texto = {str(r[0]) for r in cursor.fetchall()}
    
    reporte = []
    faltantes = []
    
    reporte.append("=== REPORTE DE COBERTURA DE DOCUMENTOS PDF ===")
    reporte.append(f"Total de mociones en la base: {len(total_mociones)}")
    reporte.append(f"Total de mociones con archivo descargado: {len(con_texto)}")
    
    encontrados_count = 0
    for bol in total_mociones:
        if bol in con_texto:
            encontrados_count += 1
        else:
            faltantes.append(bol)
            
    reporte.append(f"Cobertura real (Cruce): {encontrados_count} encontrados de {len(total_mociones)}.")
    reporte.append(f"Faltan por respaldar/automatizar desde la BCN: {len(faltantes)}")
    
    if faltantes:
        reporte.append("\nLISTADO BOLETINES FALTANTES:")
        for bol in sorted(faltantes):
            reporte.append(f" - {bol}")
            
    with open("reporte_cobertura_pdf.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(reporte))
        
    print("Reporte final guardado en reporte_cobertura_pdf.txt")
    
    conn.close()

if __name__ == "__main__":
    update_db()
