
import psycopg2

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def show_cols():
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'mociones'")
        cols = [c[0] for c in cursor.fetchall()]
        print("COLUMNS FOUND:")
        for c in cols:
            print(f"- {c}")
            
        cursor.execute("SELECT * FROM mociones LIMIT 1")
        row = cursor.fetchone()
        print("\nFIRST ROW SAMPLE:")
        desc = [d[0] for d in cursor.description]
        for k, v in zip(desc, row):
            val_str = str(v)
            if len(val_str) > 50: val_str = val_str[:50] + "..."
            print(f"{k}: {val_str}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn: conn.close()

if __name__ == "__main__":
    show_cols()
