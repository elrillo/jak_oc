import psycopg2
import os

# Usamos la conexión Transaction Pooler que sabemos que funciona
DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def create_table():
    print("Iniciando creación de tabla dim_diputados...")
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        # Drop check (optional, but good for clean slate if schema was wrong)
        # cursor.execute("DROP TABLE IF EXISTS dim_diputados;") 
        
        create_sql = """
        CREATE TABLE IF NOT EXISTS dim_diputados (
            diputado TEXT,
            sexo TEXT,
            partido_politico TEXT,
            bancada_comite TEXT,
            coalicion TEXT,
            region TEXT,
            distrito TEXT,
            periodo TEXT,
            PRIMARY KEY (diputado, periodo)
        );
        """
        cursor.execute(create_sql)
        conn.commit()
        conn.close()
        print("¡ÉXITO! Tabla 'dim_diputados' creada/verificada.")
        
    except Exception as e:
        print(f"FALLO FATAL: No se pudo crear la tabla. Error: {e}")

if __name__ == "__main__":
    create_table()
