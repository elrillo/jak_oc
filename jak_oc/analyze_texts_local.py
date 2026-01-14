
import sqlite3
import pandas as pd
import re
import json

DB_PATH = "database/jak_observatorio.db"

# --- NLP Resources (Lightweight) ---

TOPICS_KEYWORDS = {
    "Seguridad": ["pena", "delito", "crimen", "seguridad", "carabineros", "robo", "violencia", "terrorismo", "arma"],
    "Familia y Valores": ["familia", "matrimonio", "padres", "hijos", "niño", "vida", "concepción", "educación"],
    "Economía": ["impuesto", "tributario", "fomento", "empresa", "pyme", "económico", "presupuesto", "gasto"],
    "Constitucional": ["constitución", "reforma", "derechos", "garantías", "estado", "nacionalidad"],
    "Administrativo": ["declara", "monumento", "feriado", "homenaje", "publica", "administrativo"],
    "Salud": ["salud", "enfermedad", "hospital", "médico", "sanitario"],
}

def analyze_text(text):
    text = text.lower() if text else ""
    
    # 1. Tags
    found_tags = []
    for topic, keywords in TOPICS_KEYWORDS.items():
        if any(k in text for k in keywords):
            found_tags.append(topic)
    
    if not found_tags:
        found_tags.append("General")
        
    # 2. Iniciativa Type
    punitive_score = sum(text.count(w) for w in ["sancion", "pena", "castig", "delito", "prohib"])
    admin_score = sum(text.count(w) for w in ["declara", "establece dia", "monumento", "nacionalidad"])
    
    if punitive_score > 2:
        tipo = "Punitiva"
    elif admin_score > 0 and "ley" not in text[:50]: # Heuristic
        tipo = "Administrativa"
    else:
        tipo = "Propositiva"

    # 3. Sentiment (Simple Heuristic for Legal Text)
    # Penal/Punitive often implies negative sentiment towards the act, but "strong" tone.
    # Positive words: protege, beneficia, mejora, derecho
    # Negative words: sanciona, prohibe, elimina, restringe
    pos_words = ["protege", "beneficia", "mejora", "promueve", "garantiza"]
    neg_words = ["sanciona", "prohibe", "restringe", "castiga", "multa"]
    
    pos_count = sum(text.count(w) for w in pos_words)
    neg_count = sum(text.count(w) for w in neg_words)
    
    score = (pos_count - neg_count) / (max(pos_count + neg_count, 1))
    
    # 4. Resumen Ejecutivo (Extractive)
    # Try to find "Ideas Matrices" or just take first non-empty lines
    lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 50]
    if len(lines) > 0:
        resumen = ". ".join(lines[:2]) + "."
    else:
        resumen = (text[:300] + "...") if text else "Texto no disponible."
        
    # Limit summary length
    if len(resumen) > 400: resumen = resumen[:397] + "..."


    # 5. Alcance Territorial
    territorial_keywords = ["la reina", "peñalolén", "peñalolen", "distrito 24"]
    is_distrital = any(tk in text for tk in territorial_keywords)
    alcance = "Distrital" if is_distrital else "Nacional"

    return tipo, str(found_tags), score, resumen, alcance


def run_analysis():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Leyendo textos pdf...")
    try:
        df_textos = pd.read_sql("SELECT * FROM textos_pdf", conn)
    except Exception as e:
        print(f"Error leyendo textos_pdf: {e}")
        return

    print(f"Procesando {len(df_textos)} documentos...")
    
    results = []
    for _, row in df_textos.iterrows():
        boletin = row.get('N° Boletín', row.get('id_boletin')) # Handle naming variations
        texto = row.get('texto_mocion', row.get('texto'))
        
        if not boletin: continue
        
        tipo, tags, score, resumen, alcance = analyze_text(texto)
        
        results.append({
            'id_boletin': boletin,
            'resumen_ejecutivo': resumen,
            'tags_temas': tags,
            'tipo_iniciativa': tipo,
            'sentimiento_score': round(score, 2),
            'alcance_territorial': alcance
        })
        
    df_results = pd.DataFrame(results)
    
    # Update analisis_ia table
    # We replace the previous mock data
    print("Actualizando tabla analisis_ia...")
    df_results.to_sql("analisis_ia", conn, if_exists="replace", index=False)
    
    conn.close()
    
    # Report Frequent Tags
    all_tags = []
    for tags_str in df_results['tags_temas']:
        clean_tags = tags_str.replace("[","").replace("]","").replace("'","").split(",")
        all_tags.extend([t.strip() for t in clean_tags])
        
    tag_counts = pd.Series(all_tags).value_counts()
    print("\n--- Top 5 Temas Encontrados ---")
    print(tag_counts.head(5))

    # Report Territorial Scope
    territorial_counts = df_results['alcance_territorial'].value_counts(normalize=True) * 100
    print("\n--- Alcance Territorial (%) ---")
    print(territorial_counts)
    
    distrital_pct = territorial_counts.get("Distrital", 0)
    print(f"\nResumen: {distrital_pct:.1f}% Distrital vs {100-distrital_pct:.1f}% Nacional")


if __name__ == "__main__":
    run_analysis()
