import os
import sqlite3
import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
import unicodedata

# Configuración de conexión Supabase
# Se usa directamente el string proporcionado por el usuario (Transaction Pooler)
DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

INPUT_DB = "database/jak_observatorio.db"

def clean_column_name(col_name):
    # Normalizar texto (eliminar tildes simples)
    nfkd_form = unicodedata.normalize('NFKD', col_name)
    only_ascii = nfkd_form.encode('ASCII', 'ignore').decode('utf-8')
    
    # Reemplazos específicos
    clean = only_ascii.lower()
    clean = clean.replace('n°', 'num')
    clean = clean.replace(' ', '_')
    clean = clean.replace('.', '')
    return clean

def get_sqlite_data(table_name):
    conn = sqlite3.connect(INPUT_DB)
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()
    
    # Limpiar columnas
    df.columns = [clean_column_name(c) for c in df.columns]
    return df

def map_pandas_dtype_to_postgres(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return "INTEGER"
    elif pd.api.types.is_float_dtype(dtype):
        return "FLOAT"
    elif pd.api.types.is_bool_dtype(dtype):
        return "BOOLEAN"
    else:
        return "TEXT"

def create_table_if_not_exists(cursor, table_name, df, pk_columns):
    columns_def = []
    for col in df.columns:
        pg_type = map_pandas_dtype_to_postgres(df[col].dtype)
        # Forzamos TEXT para columnas críticas de texto largo
        if 'texto' in col or 'resumen' in col:
            pg_type = "TEXT"
        columns_def.append(f'"{col}" {pg_type}')
    
    columns_sql = ", ".join(columns_def)
    pk_sql = f", PRIMARY KEY ({', '.join([f'\"{c}\"' for c in pk_columns])})"
    
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {columns_sql}
        {pk_sql}
    );
    """
    cursor.execute(create_query)
    print(f"Tabla '{table_name}' verificada/creada.")

def upsert_data(cursor, table_name, df, pk_columns):
    if df.empty:
        return

    cols = list(df.columns)
    # Preparamos la query INSERT con ON CONFLICT
    columns_list = ", ".join([f'"{c}"' for c in cols])
    
    # Clausula UPDATE para el conflicto (actualizar todo excepto PK)
    update_cols = [c for c in cols if c not in pk_columns]
    if update_cols:
        update_set = ", ".join([f'"{c}" = EXCLUDED."{c}"' for c in update_cols])
        conflict_action = f"DO UPDATE SET {update_set}"
    else:
        conflict_action = "DO NOTHING"

    query = f"""
    INSERT INTO {table_name} ({columns_list})
    VALUES %s
    ON CONFLICT ({', '.join([f'\"{c}\"' for c in pk_columns])})
    {conflict_action};
    """
    
    # Convertimos DF a lista de tuplas, manejando NaNs como None para SQL
    records = df.where(pd.notnull(df), None).values.tolist()
    
    execute_values(cursor, query, records)
    print(f"Datos insertados/actualizados en '{table_name}': {len(records)} registros.")

def main():
    if not DB_URL:
        print("Error: La variable de entorno SUPABASE_DB_URL no está definida.")
        print("Por favor configúrala con tu string de conexión de Supabase.")
        print("Ej: postgres://postgres.xxxx:pass@aws-0-region.pooler.supabase.com:5432/postgres")
        return

    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        # 1. Migrar MOCIONES
        print("\n--- Migrando Mociones ---")
        df_mociones = get_sqlite_data("mociones")
        # Asumimos que 'n_boletin' es la PK (después de limpieza)
        pk_moc = ['n_boletin'] if 'n_boletin' in df_mociones.columns else [df_mociones.columns[0]]
        create_table_if_not_exists(cursor, "mociones", df_mociones, pk_moc)
        upsert_data(cursor, "mociones", df_mociones, pk_moc)
        
        # 2. Migrar COAUTORES
        print("\n--- Migrando Coautores ---")
        df_coautores = get_sqlite_data("coautores")
        # PK compuesta: boletin + diputado
        pk_coaut = ['n_boletin', 'diputado'] # Ajustar según nombres limpios
        
        # Verificamos nombres reales post-limpieza
        # 'N° Boletín' -> 'n_boletin' o 'num_boletin' según clean_column_name 
        # 'N° Boletín' clean: 'n°'->'num' => 'num_boletin'
        real_pk_coaut = [c for c in df_coautores.columns if 'boletin' in c or 'diputado' in c]
        
        create_table_if_not_exists(cursor, "coautores", df_coautores, real_pk_coaut)
        upsert_data(cursor, "coautores", df_coautores, real_pk_coaut)
        
        # 3. Migrar TEXTOS PDF
        print("\n--- Migrando Textos PDF ---")
        df_textos = get_sqlite_data("textos_pdf")
        # PK: boletin. Ajustar nombre
        real_pk_textos = [c for c in df_textos.columns if 'boletin' in c]
        
        create_table_if_not_exists(cursor, "textos_pdf", df_textos, real_pk_textos)
        upsert_data(cursor, "textos_pdf", df_textos, real_pk_textos)
        
        conn.commit()
        conn.close()
        print("\n¡Migración Completada Exitosamente!")
        
    except Exception as e:
        print(f"Ocurrió un error duranta la migración: {e}")
        if 'conn' in locals():
            conn.rollback()

if __name__ == "__main__":
    main()
