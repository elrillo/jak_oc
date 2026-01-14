
import psycopg2
from psycopg2 import sql
import pandas as pd
import json
import re
import unicodedata

# Connection string
DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

# --- NLP HEURISTICS ---

def clean_text(text):
    if not text: return ""
    # Normalize
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    return text.lower()

def get_summary(text):
    """
    Extractive summary: Grab the first significant paragraph or sentences containing 'objetivo', 'fundamento'.
    Since these are PDF texts, they might be messy. We'll take the first 400 chars as a rough preview 
    or look for specific markers.
    """
    if not text: return "Sin texto disponible."
    
    # Try to find "Idea Matriz" or "Antecedentes"
    markers = ['idea matriz', 'antecedentes', 'fundamentos', 'considerando']
    lower_text = text.lower()
    
    start_idx = 0
    for m in markers:
        idx = lower_text.find(m)
        if idx != -1:
            start_idx = idx
            break
            
    # Take a chunk from there
    snippet = text[start_idx:start_idx+500]
    return snippet.strip() + "..."

def classify_initiative(text):
    text = clean_text(text)
    
    # Keywords
    punitiva_kw = ['penal', 'delito', 'crimen', 'sancion', 'multa', 'carcel', 'presidio', 'reclusion', 'aumenta penas', 'codigo penal']
    administrativa_kw = ['declara', 'solicita', 'homenaje', 'monumento', 'nacionalidad', 'procedimiento', 'reglamento', 'fecha']
    
    # Check Punitiva
    if any(kw in text for kw in punitiva_kw):
        return 'Punitiva'
    
    # Check Administrativa
    if any(kw in text for kw in administrativa_kw):
        return 'Administrativa'
        
    return 'Propositiva'

def calculate_sentiment(initiative_type, text):
    """
    Heuristic sentiment.
    Punitiva -> negative lean (dealing with bad things).
    Propositiva (beneficios) -> positive.
    """
    base_score = 0.0
    text = clean_text(text)
    
    if initiative_type == 'Punitiva':
        base_score = -0.4
    elif initiative_type == 'Administrativa':
        base_score = 0.1
    else:
        base_score = 0.3
        
    # Adjust based on specific words
    pos_words = ['mejorar', 'beneficio', 'fomentar', 'proteger', 'derecho', 'aumento', 'subsidio']
    neg_words = ['prohibir', 'restringir', 'sancionar', 'eliminar', 'daño', 'perjuicio']
    
    for w in pos_words:
        if w in text: base_score += 0.05
    for w in neg_words:
        if w in text: base_score -= 0.05
        
    return max(min(base_score, 1.0), -1.0)

def extract_tags(text):
    text = clean_text(text)
    tags = []
    
    categories = {
        'Seguridad': ['seguridad', 'policia', 'carabineros', 'delincuencia', 'robo', 'armas'],
        'Salud': ['salud', 'medico', 'hospital', 'enfermedad', 'paciente', 'sanitario'],
        'Educación': ['educacion', 'escolar', 'universidad', 'profesor', 'alumno', 'docente'],
        'Economía': ['impuesto', 'tributario', 'economia', 'pyme', 'fomento', 'inversion', 'presupuesto'],
        'Medio Ambiente': ['ambiente', 'agua', 'contaminacion', 'bosque', 'animal', 'residuos'],
        'Familia': ['familia', 'niño', 'mujer', 'matrimonio', 'pension', 'adulto mayor'],
        'Constitucional': ['constitucion', 'reforma', 'ley organica', 'estado'],
        'Transporte': ['transporte', 'transito', 'vehiculo', 'licencia', 'vial']
    }
    
    for cat, keywords in categories.items():
        if any(w in text for w in keywords):
            tags.append(cat)
            
    # Sort by relevance? Just take top 3 found
    return tags[:3]

# --- MAIN PROCESS ---

def build_intelligence_layer():
    conn = None
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        print("Conectado a Supabase.")
        
        # 1. CREATE TABLE
        print("Creando tabla 'analisis_ia'...")
        create_sql = """
        CREATE TABLE IF NOT EXISTS analisis_ia (
            id_boletin TEXT PRIMARY KEY,
            resumen_ejecutivo TEXT,
            tipo_iniciativa VARCHAR(50),
            sentimiento_score FLOAT,
            tags_temas JSONB,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            FOREIGN KEY (id_boletin) REFERENCES mociones(n_boletin)
        );
        """
        cursor.execute(create_sql)
        conn.commit()
        print("Tabla creada/verificada.")
        
        # 2. FETCH DATA TO ANALYZE
        # We need text from textos_pdf. 
        # Note: textos_pdf might use 'n_boletin' or 'boletin' as col name. 
        # previous steps showed 'n_boletin' in coautores/mociones. Let's assume consistent key.
        # We'll check column name via a quick safe query if needed, but assuming 'n_boletin' based on previous context.
        query_fetch = """
        SELECT t.n_boletin, t.texto_mocion
        FROM textos_pdf t
        LEFT JOIN analisis_ia a ON t.n_boletin = a.id_boletin
        WHERE a.id_boletin IS NULL AND t.texto_mocion IS NOT NULL;
        """
        # If 'texto_mocion' was the col name in sqlite, let's hope it's same in Postgres or we check schema.
        # In previous 'inspect_sqlite' output: 'texto_mocion' was confirmed.
        
        cursor.execute(query_fetch)
        rows = cursor.fetchall()
        print(f"Encontrados {len(rows)} documentos pendientes de análisis.")
        
        if not rows:
            print("Nada nuevo que analizar.")
            return

        # 3. PROCESS BATCH
        records_to_insert = []
        for row in rows:
            bol_id, raw_pdf_text = row
            
            # NLP Tasks
            resumen = get_summary(raw_pdf_text)
            tipo = classify_initiative(raw_pdf_text)
            sentimiento = calculate_sentiment(tipo, raw_pdf_text)
            tags = extract_tags(raw_pdf_text)
            
            # Serialize tags for JSONB
            tags_json = json.dumps(tags, ensure_ascii=False)
            
            records_to_insert.append((bol_id, resumen, tipo, sentimiento, tags_json))
            
        # 4. INSERT RESULTS
        insert_query = """
        INSERT INTO analisis_ia (id_boletin, resumen_ejecutivo, tipo_iniciativa, sentimiento_score, tags_temas)
        VALUES %s
        ON CONFLICT (id_boletin) DO UPDATE 
        SET resumen_ejecutivo = EXCLUDED.resumen_ejecutivo,
            tipo_iniciativa = EXCLUDED.tipo_iniciativa,
            sentimiento_score = EXCLUDED.sentimiento_score,
            tags_temas = EXCLUDED.tags_temas;
        """
        
        from psycopg2.extras import execute_values
        execute_values(cursor, insert_query, records_to_insert)
        conn.commit()
        print(f"Insertados/Actualizados {len(records_to_insert)} registros en 'analisis_ia'.")
        
        # 5. VERIFICATION
        print("\n--- Verificación (Top 5) ---")
        verify_query = """
        SELECT a.id_boletin, m.titulo, a.tipo_iniciativa, a.tags_temas
        FROM analisis_ia a
        JOIN mociones m ON a.id_boletin = m.n_boletin
        LIMIT 5;
        """
        # Note: 'titulo' column in mociones might be named differently? 
        # In sqlite inspect: didn't see mociones cols fully listed in my reading, but likely 'titulo', 'nombre', or 'materia'.
        # I'll try 'materia' as it's common in congress data, fallback to 'titulo'.
        # Actually I can query information_schema for mociones first to be safe, but I'll try a safe approach:
        # Just select * from Analysis first.
        
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'mociones'")
        moc_cols = [c[0] for c in cursor.fetchall()]
        title_col = 'titulo' if 'titulo' in moc_cols else 'materia' if 'materia' in moc_cols else moc_cols[1] # fallback
        
        print(f"Usando columna '{title_col}' para verificación de título.")
        
        verify_query = f"""
        SELECT a.id_boletin, m.{title_col}, a.tipo_iniciativa, a.tags_temas, a.resumen_ejecutivo
        FROM analisis_ia a
        JOIN mociones m ON a.id_boletin = m.n_boletin
        LIMIT 5;
        """
        
        cursor.execute(verify_query)
        ver_rows = cursor.fetchall()
        for r in ver_rows:
            print("-" * 50)
            print(f"Boletín: {r[0]}")
            print(f"Título: {r[1][:100]}...")
            print(f"Tipo IA: {r[2]}")
            print(f"Tags: {r[3]}")
            print(f"Resumen Snippet: {r[4][:100]}...")

    except Exception as e:
        print(f"Error: {e}")
        if conn: conn.rollback()
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    build_intelligence_layer()
