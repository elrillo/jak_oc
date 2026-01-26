
import psycopg2
from psycopg2 import sql

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def inspect_all():
    tables = ["mociones", "coautores", "dim_diputados", "analisis_ia"]
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        for t in tables:
            print(f"--- {t} ---")
            cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{t}'")
            for c in cursor.fetchall():
                print(f"{c[0]} ({c[1]})")
            print("\n")
            
            # Also preview 1 row to see data format
            try:
                cursor.execute(f"SELECT * FROM {t} LIMIT 1")
                row = cursor.fetchone()
                print(f"Sample row: {row}")
            except Exception as e:
                print(f"Could not fetch row: {e}")
            print("\n")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_all()
