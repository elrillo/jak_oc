import sqlite3
import pandas as pd
import unicodedata
import os

# Configuración
DB_PATH = "database/jak_observatorio.db"
REPORT_FILE = "reporte_calidad_autores.txt"

def normalize_text(text):
    """
    Elimina tildes, caracteres especiales y convierte a minúsculas para facilitar la búsqueda.
    """
    if not isinstance(text, str):
        return ""
    # Normalización NFKD descompone caracteres (ej: á -> a + ´)
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    return text.lower().strip()

def check_author_consistency():
    if not os.path.exists(DB_PATH):
        print(f"Error: No se encontró la base de datos en {DB_PATH}")
        return

    print(f"Conectando a {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    
    # Cargar datos necesarios
    try:
        df_coautores = pd.read_sql("SELECT * FROM coautores", conn)
        df_textos = pd.read_sql("SELECT * FROM textos_pdf", conn)
    except Exception as e:
        print(f"Error leyendo tablas: {e}")
        conn.close()
        return
    finally:
        conn.close()

    print("Analizando consistencia de datos...")
    
    # Filtramos solo mociones que tienen texto extraído válido
    # Asumimos que textos vacíos o mensajes de error no sirven para validar
    df_textos_validos = df_textos[
        (df_textos['texto_mocion'].notnull()) & 
        (df_textos['texto_mocion'].str.len() > 50) &  # Filtro de longitud mínima
        (df_textos['texto_mocion'] != "PDF no encontrado")
    ].copy()

    total_analizados = len(df_textos_validos)
    discrepancias = []
    
    for _, row in df_textos_validos.iterrows():
        boletin = row['N° Boletín']
        texto_pdf_raw = row['texto_mocion']
        texto_pdf_norm = normalize_text(texto_pdf_raw)
        
        # Obtener lista de autores esperados (según Excel) para este boletín
        autores_excel = df_coautores[df_coautores['N° Boletín'] == boletin]['Diputado'].unique()
        
        if len(autores_excel) == 0:
            continue

        autores_no_encontrados = []
        
        for autor in autores_excel:
            autor_norm = normalize_text(autor)
            
            # LÓGICA DE MATCHING:
            # 1. Búsqueda exacta del nombre completo normalizado
            if autor_norm in texto_pdf_norm:
                continue # Encontrado
            
            # 2. Búsqueda por partes (Apellidos)
            # Dividimos nombre en palabras. Asumimos palabras largas (>2 chars) son relevantes.
            partes_nombre = [p for p in autor_norm.split() if len(p) > 2]
            
            # Si el autor es "Juan Perez", buscamos si "Perez" y "Juan" están cerca o presentes.
            # Para ser estrictos pero justos, exigimos que al menos el APELLIDO (última palabra) esté.
            # O comprobamos si la mayoría de las partes del nombre están en el texto.
            
            coincidencias_parciales = 0
            for parte in partes_nombre:
                if parte in texto_pdf_norm:
                    coincidencias_parciales += 1
            
            # Criterio: Si menos de la mitad de las palabras del nombre aparecen, lo marcamos como NO encontrado.
            # (Ej: "Alejandro Garcia Huidobro" -> si encuentra "Garcia" y "Huidobro" (2/3) pasa.)
            if coincidencias_parciales == 0:
                 autores_no_encontrados.append(autor)
            elif coincidencias_parciales < len(partes_nombre) * 0.5:
                 # Caso gris, podría ser falso positivo, pero lo contamos como no encontrado para revisión manual
                 autores_no_encontrados.append(f"{autor} (Dudoso)")
        
        if autores_no_encontrados:
            discrepancias.append({
                'Boletin': boletin,
                'Autores_Totales': len(autores_excel),
                'Faltantes_Cantidad': len(autores_no_encontrados),
                'Nombres_No_Encontrados': autores_no_encontrados
            })

    # GENERAR REPORTE
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("REPORTE DE CONSISTENCIA DE AUTORES (EXCEL vs PDF)\n")
        f.write("=================================================\n\n")
        f.write(f"Total Boletines con PDF legible: {total_analizados}\n")
        f.write(f"Boletines con discrepancias detectadas: {len(discrepancias)}\n")
        f.write(f"Tasa de consistencia (Boletines perfectos): {((total_analizados - len(discrepancias))/total_analizados)*100:.1f}%\n\n")
        
        if discrepancias:
            f.write("DETALLE DE DISCREPANCIAS:\n")
            f.write("-------------------------\n")
            for item in discrepancias:
                f.write(f"Boletín: {item['Boletin']}\n")
                f.write(f"  - Autores en Excel: {item['Autores_Totales']}\n")
                f.write(f"  - No encontrados en PDF: {item['Faltantes_Cantidad']}\n")
                f.write(f"  - Nombres: {', '.join(item['Nombres_No_Encontrados'])}\n")
                f.write("\n")
        else:
            f.write("RESULTADO PERFECTO: No se encontraron discrepancias en los boletines analizados.\n")

    print(f"Análisis completado. Reporte guardado en: {REPORT_FILE}")
    print(f"Se encontraron discrepancias en {len(discrepancias)} de {total_analizados} boletines analizados.")

if __name__ == "__main__":
    check_author_consistency()
