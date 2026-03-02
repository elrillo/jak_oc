import psycopg2
import json

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def check():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    cur.execute("SELECT diputado_normalizado, periodo FROM dim_diputados WHERE diputado_normalizado ILIKE '%entealba%'")
    dim_res = cur.fetchall()
    
    cur.execute("""
        SELECT c.diputado_normalizado, m.periodo_legislativo 
        FROM coautores c 
        JOIN mociones m ON c.n_boletin=m.n_boletin 
        WHERE c.diputado_normalizado ILIKE '%entealba%'
    """)
    coa_res = cur.fetchall()
    
    out = {
        "dim_diputados": [dict(name=r[0], period=r[1]) for r in dim_res],
        "coautores": [dict(name=r[0], period=r[1]) for r in coa_res]
    }
    
    with open('renan_check.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    check()
