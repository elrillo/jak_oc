import pandas as pd
import sqlite3
import os
import glob
import PyPDF2 # Asegúrate de que esté instalada o pídela a Antigravity

def extract_pdf_text(pdf_path):
    """Extrae texto de un PDF."""
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        return None

def build_database():
    print("Iniciando procesamiento...")
    
    # 1. Cargar la Síntesis (Metadata principal)
    excel_path = "data/archivos_csv/listado_mociones.xlsx"
    xls = pd.ExcelFile(excel_path)
    
    # Intentamos leer la hoja 'Sintesis' (a veces puede tener tilde o no, ajustamos si falla)
    try:
        df_sintesis = pd.read_excel(xls, 'Sintesis')
    except ValueError:
        # Fallback por si se llama diferente
        possible_sheets = [s for s in xls.sheet_names if 'sintesis' in s.lower()]
        if possible_sheets:
            df_sintesis = pd.read_excel(xls, possible_sheets[0])
        else:
            raise ValueError("No se encontró la hoja de Síntesis")
    
    # 2. Procesar Periodos para obtener Coautores
    periodo_sheets = [s for s in xls.sheet_names if s.startswith("Periodo")]
    coautores_list = []
    
    for sheet_name in periodo_sheets:
        temp_df = pd.read_excel(xls, sheet_name)
        # Identificamos dónde terminan las columnas de metadata y empiezan los diputados
        # Según tus archivos, la metadata termina en 'N°Ley'
        if 'N°Ley' in temp_df.columns:
            idx_metadata = list(temp_df.columns).index('N°Ley') + 1
        else:
            # Fallback trivial si la estructura cambia un poco
            idx_metadata = 10 
            
        # 'Melt' para pasar de formato ancho (columnas de nombres) a formato largo
        # A veces N° Boletín puede estar escrito distinto
        id_col = 'N° Boletín' if 'N° Boletín' in temp_df.columns else temp_df.columns[0]
        
        df_long = temp_df.melt(
            id_vars=[id_col], 
            value_vars=temp_df.columns[idx_metadata:],
            var_name='Diputado', 
            value_name='Participa'
        )
        # Solo nos quedamos con los que tienen 1 (son autores)
        coautores_list.append(df_long[df_long['Participa'] == 1])

    if coautores_list:
        df_coautores = pd.concat(coautores_list)
    else:
        df_coautores = pd.DataFrame(columns=['N° Boletín', 'Diputado'])

    # 3. Vincular con PDFs
    print("Extrayendo textos de PDFs...")
    textos = []
    for boletin in df_sintesis['N° Boletín']:
        pdf_name = f"Boletín {boletin}.pdf"
        pdf_path = os.path.join("data/archivos_pdf", pdf_name)
        
        content = extract_pdf_text(pdf_path) if os.path.exists(pdf_path) else "PDF no encontrado"
        textos.append({'N° Boletín': boletin, 'texto_mocion': content})
    
    df_textos = pd.DataFrame(textos)

    # 4. Guardar en SQLite
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect("database/jak_observatorio.db")
    
    df_sintesis.to_sql('mociones', conn, if_exists='replace', index=False)
    df_coautores[['N° Boletín', 'Diputado']].to_sql('coautores', conn, if_exists='replace', index=False)
    df_textos.to_sql('textos_pdf', conn, if_exists='replace', index=False)
    
    conn.close()
    print("¡Base de datos lista en database/jak_observatorio.db!")

if __name__ == "__main__":
    build_database()