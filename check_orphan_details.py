import psycopg2

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

orphans = [
    'Gabriel Sandoval Plaza',
    'Maximiano Errázuriz Eguiguren',
    'German Verdugo Soto',
    'Darío Molina Sanhueza',
    'Rosa González Román',
    'María Eugenia Mella Gajardo',
    'Renán Fuentealba Vildósola',
    'Cristian Campos Jara',
    'Patricio Cornejo Vidaurrázaga',
    'Rodrigo Álvarez Zenteno',
    'Cristián Leay Morán',
    'Ramón Pérez Opazo',
    'Romilio Gutierrez Pino'
]

def check_orphans():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    print(f"{'Orphan Name (coautores)':<35} | {'dim_diputados Match':<35} | {'Period coautores':<15} | {'Period dim_diputados'}")
    print("-" * 115)
    
    for orphan in orphans:
        # Get periods in coautores
        cur.execute("SELECT m.periodo_legislativo FROM coautores c JOIN mociones m ON c.n_boletin = m.n_boletin WHERE c.diputado_normalizado = %s LIMIT 1", (orphan,))
        c_res = cur.fetchone()
        c_period = c_res[0] if c_res else "N/A"
        
        # Try to find him in dim_diputados by first and first-last name
        parts = orphan.split()
        if len(parts) >= 2:
            search_str = f"%{parts[0]}%{parts[1]}%"
        else:
            search_str = f"%{orphan}%"
            
        cur.execute("SELECT diputado_normalizado, periodo FROM dim_diputados WHERE diputado_normalizado ILIKE %s LIMIT 3", (search_str,))
        d_res = cur.fetchall()
        
        if not d_res:
            print(f"{orphan:<35} | {'NOT FOUND IN DIM_DIPUTADOS':<35} | {c_period:<15} | N/A")
        else:
            for i, (d_name, d_period) in enumerate(d_res):
                if i == 0:
                    print(f"{orphan:<35} | {d_name:<35} | {c_period:<15} | {d_period}")
                else:
                    print(f"{'':<35} | {d_name:<35} | {'':<15} | {d_period}")
                    
if __name__ == '__main__':
    check_orphans()
