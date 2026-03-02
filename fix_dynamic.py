import psycopg2
import json

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def fix_missing_periods():
    with open('diagnose_54_clean.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = True
    cur = conn.cursor()
    
    # Get all column names dynamically so we don't miss any
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'dim_diputados'")
    cols = [r[0] for r in cur.fetchall()]
    
    # Prepare the columns statement: 'col1, col2, col3...'
    cols_str = ", ".join(cols)
    
    # We want to select all columns EXCEPT we replace 'periodo' with our new value
    select_cols = []
    for c in cols:
        if c == 'periodo':
            select_cols.append("%s")
        else:
            select_cols.append(c)
    select_cols_str = ", ".join(select_cols)

    updates = 0
    for item in data:
        name = item['name']
        missing_period = item['missing_period']
        existing_periods = item['exists_in_other_periods']
        
        if not existing_periods: continue
            
        source_period = existing_periods[0]
        for ep in existing_periods:
            if missing_period[:4] == ep[:4]:
                source_period = ep
                break
                
        try:
            sql = f"""
                INSERT INTO dim_diputados ({cols_str})
                SELECT {select_cols_str}
                FROM dim_diputados
                WHERE diputado_normalizado = %s AND periodo = %s
                LIMIT 1
            """
            cur.execute(sql, (missing_period, name, source_period))
            updates += cur.rowcount
            print(f"Inserted period {missing_period} for {name} (copied from {source_period})")
        except Exception as e:
            print(f"Error inserting for {name}: {e}")
            
    print(f"\nTotal new periods inserted: {updates}")

if __name__ == '__main__':
    fix_missing_periods()
