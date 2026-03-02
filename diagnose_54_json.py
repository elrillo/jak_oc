import psycopg2
import json
from collections import Counter

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def check():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT c.diputado_normalizado, m.periodo_legislativo 
        FROM coautores c 
        JOIN mociones m ON c.n_boletin = m.n_boletin 
        LEFT JOIN dim_diputados d 
          ON d.diputado_normalizado = c.diputado_normalizado 
         AND d.periodo = m.periodo_legislativo 
        WHERE d.diputado_normalizado IS NULL
    """)
    mismatches = cur.fetchall()
    
    summary = Counter(mismatches)
    out = []
    
    for (name, period), count in sorted(summary.items(), key=lambda x: str(x[0][0])):
        cur.execute("SELECT periodo FROM dim_diputados WHERE diputado_normalizado = %s", (name,))
        other_periods = [r[0] for r in cur.fetchall()]
        out.append({
            "name": name,
            "missing_period": period,
            "count": count,
            "exists_in_other_periods": other_periods
        })
        
    with open("diagnose_54_clean.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    check()
