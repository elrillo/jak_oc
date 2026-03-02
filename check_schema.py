import pandas as pd
import psycopg2

def run():
    df = pd.read_excel('data/archivos_csv/diputados_historicos.xlsx')
    print("Excel columns:", df.columns.tolist())
    print("Sample:\n", df.head(1).to_dict(orient='records'))

    conn = psycopg2.connect("postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres")
    cur = conn.cursor()
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'dim_diputados'")
    print("dim_diputados columns:", [r[0] for r in cur.fetchall()])
    
    cur.execute("SELECT * FROM dim_diputados LIMIT 1")
    cols = [desc[0] for desc in cur.description]
    row = cur.fetchone()
    print("dim_diputados sample:", dict(zip(cols, row)))
    
if __name__ == '__main__':
    run()
