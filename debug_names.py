import psycopg2

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def check():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    cur.execute("SELECT DISTINCT diputado_normalizado FROM coautores WHERE diputado_normalizado ILIKE '%urrutia%'")
    print("COAUTORES:", [r[0] for r in cur.fetchall()])
    
    cur.execute("SELECT DISTINCT diputado_normalizado FROM dim_diputados WHERE diputado_normalizado ILIKE '%urrutia%'")
    print("DIM_DIPUTADOS:", [r[0] for r in cur.fetchall()])

if __name__ == '__main__':
    check()
