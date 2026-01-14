import sqlite3
import pandas as pd
import os

db_path = "database/jak_observatorio.db"
conn = sqlite3.connect(db_path)

# Load tables
df_mociones = pd.read_sql("SELECT * FROM mociones", conn)
df_coautores = pd.read_sql("SELECT * FROM coautores", conn)
df_textos = pd.read_sql("SELECT * FROM textos_pdf", conn)

with open("validation_report.txt", "w", encoding="utf-8") as f:
    f.write("--- Resumen Estadístico Pre-Migración ---\n")

    # 1. Coautores únicos
    unique_coautores = df_coautores['Diputado'].nunique()
    f.write(f"1. Cantidad de Coautores únicos: {unique_coautores}\n")

    # 2. Mociones con texto PDF
    df_textos['has_text'] = df_textos['texto_mocion'].apply(lambda x: False if x is None or x == "PDF no encontrado" or x.strip() == "" else True)
    valid_pdfs = df_textos['has_text'].sum()
    total_text_records = len(df_textos)
    f.write(f"2. Mociones con texto PDF válido: {valid_pdfs} de {total_text_records} registros en tabla textos_pdf.\n")

    # Cruce con tabla mociones
    merged = df_mociones.merge(df_textos, on='N° Boletín', how='left')
    missing_pdf_link = merged['texto_mocion'].isnull().sum()
    f.write(f"   (Mociones en tabla principal sin coincidencia en tabla PDF: {missing_pdf_link})\n")

    # 3. Valores nulos en columnas críticas
    f.write("\n3. Nulos en columnas críticas:\n")
    f.write(f"   - Mociones 'N° Boletín' nulos: {df_mociones['N° Boletín'].isnull().sum()}\n")
    f.write(f"   - Coautores 'Diputado' nulos: {df_coautores['Diputado'].isnull().sum()}\n")
    f.write(f"   - Coautores 'N° Boletín' nulos: {df_coautores['N° Boletín'].isnull().sum()}\n")

print("Validación completada. Resultados guardados en validation_report.txt")

conn.close()
