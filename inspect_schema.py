
import psycopg2
from psycopg2 import sql

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def get_table_schema(table_name):
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        query = f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = '{table_name}';
        """
        cursor.execute(query)
        columns = cursor.fetchall()
        print(f"\nSchema for {table_name}:")
        for col in columns:
            print(f"- {col[0]} ({col[1]})")
        conn.close()
    except Exception as e:
        print(f"Error inspecting {table_name}: {e}")

if __name__ == "__main__":
    get_table_schema("dim_diputados")
    get_table_schema("coautores")
