import psycopg2
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
    print("Las 54 firmas Huérfanas restantes pertenecen a:\n")
    for (name, period), count in sorted(summary.items(), key=lambda x: str(x[0][0])):
        print(f"[{count} firmas] - {name} (Periodo Moción: {period})")
        
        # Check if the name exists at all in dim_diputados under A DIFFERENT period
        cur.execute("SELECT periodo FROM dim_diputados WHERE diputado_normalizado = %s", (name,))
        other_periods = [r[0] for r in cur.fetchall()]
        
        if other_periods:
            print(f"    -> PERO SÍ EXISTE en la base maestra bajo estos otros periodos: {other_periods}")
        else:
            print(f"    -> NO EXISTE en toda la base maestra (Verdadero Huérfano).")

if __name__ == '__main__':
    check()
