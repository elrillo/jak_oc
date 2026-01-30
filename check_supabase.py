
import psycopg2
import pandas as pd

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def check_supabase():
    try:
        conn = psycopg2.connect(DB_URL)
        print("Connected to Supabase!")
        
        # Check tables
        cursor = conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cursor.fetchall()
        print("Tables:", tables)
        
        # Check columns in 'mociones'
        print("\n--- Columns in mociones ---")
        try:
            df = pd.read_sql("SELECT * FROM mociones LIMIT 1", conn)
            print(df.columns.tolist())
        except Exception as e:
            print(f"Error reading mociones: {e}")
            
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    check_supabase()
