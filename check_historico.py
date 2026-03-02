import psycopg2

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def check():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    # Let's check Ignacio Urrutia in dim_diputados
    cur.execute("SELECT diputado_normalizado, periodo, partido_politico_normalizado FROM dim_diputados WHERE diputado_normalizado ILIKE '%urrutia%'")
    print("dim_diputados Urrutia:", cur.fetchall())
    
    # Check his coauthorships and the period
    cur.execute("""
        SELECT c.n_boletin, m.periodo_legislativo, c.diputado_normalizado 
        FROM coautores c 
        JOIN mociones m ON c.n_boletin = m.n_boletin 
        WHERE c.diputado_normalizado ILIKE '%urrutia%' LIMIT 5
    """)
    print("\ncoautores (sample):", cur.fetchall())
    
    # Let's check how many coautores DO NOT have a matching dim_diputados per period
    cur.execute("""
        SELECT COUNT(*)
        FROM coautores c
        JOIN mociones m ON c.n_boletin = m.n_boletin
        LEFT JOIN dim_diputados d 
          ON d.diputado_normalizado = c.diputado_normalizado 
         AND d.periodo = m.periodo_legislativo
        WHERE d.diputado_normalizado IS NULL
    """)
    misses = cur.fetchone()[0]
    
    cur.execute("""
        SELECT COUNT(*) FROM coautores
    """)
    total = cur.fetchone()[0]
    
    print(f"\nTotal coauthors: {total}")
    print(f"Missing (no perfect match by Name + Period): {misses}")
    
    # Show some examples of the missing ones
    if misses > 0:
        cur.execute("""
            SELECT c.diputado_normalizado, m.periodo_legislativo, c.n_boletin
            FROM coautores c
            JOIN mociones m ON c.n_boletin = m.n_boletin
            LEFT JOIN dim_diputados d 
              ON d.diputado_normalizado = c.diputado_normalizado 
             AND d.periodo = m.periodo_legislativo
            WHERE d.diputado_normalizado IS NULL
            LIMIT 10
        """)
        print("\nMissing examples:")
        for r in cur.fetchall():
            print(f" - {r[0]} in {r[1]} (Boletín {r[2]})")

if __name__ == '__main__':
    check()
