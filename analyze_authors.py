import sqlite3
import pandas as pd
import unicodedata

def normalize_text(text):
    if not isinstance(text, str):
        return ""
    # Quitar tildes y pasar a minúsculas
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    return text.lower()

def analyze_matches():
    conn = sqlite3.connect("database/jak_observatorio.db")
    
    # Cargar datos
    df_coautores = pd.read_sql("SELECT * FROM coautores", conn)
    df_textos = pd.read_sql("SELECT * FROM textos_pdf", conn)
    conn.close()
    
    # Filtrar solo los que tienen texto PDF válido
    df_textos_validos = df_textos[
        (df_textos['texto_mocion'].notnull()) & 
        (df_textos['texto_mocion'] != "PDF no encontrado") &
        (df_textos['texto_mocion'] != "")
    ].copy()
    
    print(f"Total Boletines con PDF y Texto extraído: {len(df_textos_validos)}")
    
    results = []
    
    for _, row in df_textos_validos.iterrows():
        boletin = row['N° Boletín']
        texto_pdf_raw = row['texto_mocion']
        texto_pdf_norm = normalize_text(texto_pdf_raw)
        
        # Obtener coautores según Excel
        autores_excel = df_coautores[df_coautores['N° Boletín'] == boletin]['Diputado'].unique()
        
        found_count = 0
        missing_authors = []
        
        if len(autores_excel) == 0:
            continue

        for autor in autores_excel:
            autor_norm = normalize_text(autor)
            # Estrategia simple: dividir nombre y buscar apellidos
            # Asumimos que las palabras más largas suelen ser apellidos
            parts = [p for p in autor_norm.split() if len(p) > 2]
            
            # Buscamos si AL MENOS una de las partes importantes (probable apellido) está en el texto
            # Ojo: esto puede dar falsos positivos, pero es una primera aproximación
            match = False
            for part in parts:
                if part in texto_pdf_norm:
                    match = True
                    break
            
            if match:
                found_count += 1
            else:
                missing_authors.append(autor)
        
        results.append({
            'Boletin': boletin,
            'Total_Autores_Excel': len(autores_excel),
            'Encontrados_en_PDF': found_count,
            'No_Encontrados': missing_authors
        })
    
    # Convertir a DataFrame para resumen
    df_res = pd.DataFrame(results)
    
    if df_res.empty:
        print("No se encontraron coincidencias suficientes para analizar.")
        return

    # Métricas Globales
    total_autores_esperados = df_res['Total_Autores_Excel'].sum()
    total_encontrados = df_res['Encontrados_en_PDF'].sum()
    pct_match = (total_encontrados / total_autores_esperados) * 100 if total_autores_esperados > 0 else 0
    
    with open("analysis_final.txt", "w", encoding="utf-8") as f:
        f.write("\n--- Resultados del Análisis de Coincidencia (Excel vs PDF) ---\n")
        f.write(f"Boletines Analizados: {len(df_res)}\n")
        f.write(f"Total Autores esperados (Excel): {total_autores_esperados}\n")
        f.write(f"Total Autores encontrados en texto PDF (Aprox): {total_encontrados}\n")
        f.write(f"Tasa de Coincidencia Global: {pct_match:.2f}%\n")
        
        f.write("\n--- Detalle de Discrepancias (Ejemplos) ---\n")
        discrepancias = df_res[df_res['Encontrados_en_PDF'] < df_res['Total_Autores_Excel']]
        
        if not discrepancias.empty:
            f.write(f"Boletines con autores no detectados en PDF: {len(discrepancias)}\n")
            for i, row in discrepancias.head(10).iterrows():
                f.write(f"Boletín {row['Boletin']}: Faltaron {len(row['No_Encontrados'])} de {row['Total_Autores_Excel']}\n")
                f.write(f"   -> No vistos en PDF: {', '.join(row['No_Encontrados'])}\n")
        else:
            f.write("¡Increíble! Todos los autores del Excel fueron encontrados en los textos de los PDFs.\n")
            
    print("Análisis listo en analysis_final.txt")

if __name__ == "__main__":
    analyze_matches()
