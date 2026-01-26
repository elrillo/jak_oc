
import psycopg2
DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"
def get_cols(t):
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{t}'")
        cols = [c[0] for c in cur.fetchall()]
        print(f"{t}: {cols}")
        conn.close()
    except Exception as e: print(e)

for t in ["mociones", "coautores", "dim_diputados", "analisis_ia"]:
    get_cols(t)
