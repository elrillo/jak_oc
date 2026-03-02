import psycopg2

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def debug():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("SELECT n_boletin FROM textos_pdf WHERE length(texto_mocion) < 50 LIMIT 5")
    rows = cur.fetchall()
    for r in rows:
        print(repr(r[0]))
        
if __name__ == '__main__':
    debug()
