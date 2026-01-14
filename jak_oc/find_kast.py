
import psycopg2
import pandas as pd
DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def find_kast():
    conn = psycopg2.connect(DB_URL)
    # Check column names first
    cur = conn.cursor()
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'dim_diputados'")
    cols = [c[0] for c in cur.fetchall()]
    print(f"Columns: {cols}")

    # Now select
    df = pd.read_sql("SELECT * FROM dim_diputados WHERE diputado ILIKE '%Kast%'", conn)
    for name in df['diputado'].unique():
        print(f"Found: {name}")
    conn.close()

if __name__ == "__main__":
    find_kast()
