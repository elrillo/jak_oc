import psycopg2

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def check():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    cur.execute("SELECT diputado_normalizado, periodo FROM dim_diputados WHERE diputado_normalizado ILIKE '%urrutia%' LIMIT 2")
    print("dim_diputados:")
    for r in cur.fetchall():
        name, period = r[0], r[1]
        print(f"Name: '{name}' | len_name={len(name)} | period={period} | len_p={len(period)}")
        
    cur.execute("""
        SELECT c.diputado_normalizado, m.periodo_legislativo 
        FROM coautores c 
        JOIN mociones m ON c.n_boletin = m.n_boletin 
        WHERE c.diputado_normalizado ILIKE '%urrutia%' LIMIT 2
    """)
    print("\ncoautores:")
    for r in cur.fetchall():
        name, period = r[0], r[1]
        print(f"Name: '{name}' | len_name={len(name)} | period={period} | len_p={len(period)}")    
if __name__ == '__main__':
    check()
