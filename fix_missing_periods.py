import psycopg2
import json

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def fix_missing_periods():
    with open('diagnose_54_clean.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = True
    cur = conn.cursor()
    
    updates = 0
    for item in data:
        name = item['name']
        missing_period = item['missing_period']
        existing_periods = item['exists_in_other_periods']
        
        # Determine the source period to copy details (partido, coalicion, sexo) from
        if not existing_periods:
            continue
            
        # Try to find a period that's just a truncated version of the missing one
        # e.g., missing 2006-2010 but has 2006-2009
        source_period = existing_periods[0]
        for ep in existing_periods:
            if missing_period[:4] == ep[:4]:
                source_period = ep
                break
                
        # Copy the row from dim_diputados and insert it with the missing period
        try:
            cur.execute(f"""
                INSERT INTO dim_diputados 
                (diputado, sexo, partido_politico, periodo, distrito, region, mail, coalicion, bancada_comite, diputado_normalizado, partido_politico_normalizado, coalicion_normalizada, bancada_comite_normalizado)
                SELECT diputado, sexo, partido_politico, '{missing_period}', distrito, region, mail, coalicion, bancada_comite, diputado_normalizado, partido_politico_normalizado, coalicion_normalizada, bancada_comite_normalizado
                FROM dim_diputados
                WHERE diputado_normalizado = %s AND periodo = %s
                LIMIT 1
            """, (name, source_period))
            updates += cur.rowcount
            print(f"Inserted period {missing_period} for {name} (copied from {source_period})")
        except Exception as e:
            print(f"Error inserting for {name}: {e}")
            
    print(f"\nTotal new periods inserted: {updates}")

if __name__ == '__main__':
    fix_missing_periods()
