import psycopg2

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def check():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    names_to_check = ['fuentealba', 'errázuriz', 'leay', 'mella', 'cornejo']
    
    for name in names_to_check:
        print(f"\n--- Buscando: {name.upper()} ---")
        
        # 1. Look in dim_diputados
        cur.execute("SELECT diputado_normalizado, periodo FROM dim_diputados WHERE diputado_normalizado ILIKE %s", (f"%{name}%",))
        dim_res = cur.fetchall()
        print("En dim_diputados encontré:")
        for r in dim_res:
            d_name, d_period = r
            print(f"  Nombre: '{d_name}' | Periodo: '{d_period}'")
            
        # 2. Look in coautores (just for the exact strings in mociones)
        cur.execute("""
            SELECT c.diputado_normalizado, m.periodo_legislativo 
            FROM coautores c 
            JOIN mociones m ON c.n_boletin=m.n_boletin 
            WHERE c.diputado_normalizado ILIKE %s 
            LIMIT 5
        """, (f"%{name}%",))
        coa_res = cur.fetchall()
        print("En coautores cruzando con mociones encontré:")
        for r in coa_res:
            c_name, c_period = r
            print(f"  Nombre: '{c_name}' | Periodo: '{c_period}'")

if __name__ == '__main__':
    check()
