import psycopg2
import unicodedata

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

def remove_accents(input_str):
    if not input_str: return ""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def check_accents():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    cur.execute("SELECT DISTINCT diputado_normalizado FROM dim_diputados")
    dim_names = [r[0] for r in cur.fetchall() if r[0]]
    
    dim_names_clean = {remove_accents(name).upper().strip(): name for name in dim_names}
    
    with open("accent_matches.txt", "w", encoding="utf-8") as f:
        f.write("Found Matches by ignoring accents:\n")
        
        matches = {}
        for orphan in orphans:
            orphan_clean = remove_accents(orphan).upper().strip()
            if orphan_clean in dim_names_clean:
                matches[orphan] = dim_names_clean[orphan_clean]
                f.write(f"Orphan: '{orphan}' -> Matches: '{dim_names_clean[orphan_clean]}'\n")
            else:
                f.write(f"Orphan: '{orphan}' -> NO MATCH EVEN WITHOUT ACCENTS\n")
                
    with open("fixing_accents.sql", "w", encoding="utf-8") as f:
        for coautor_name, dim_name in matches.items():
            f.write(f"UPDATE coautores SET diputado_normalizado = '{dim_name}' WHERE diputado_normalizado = '{coautor_name}';\n")

if __name__ == '__main__':
    check_accents()
