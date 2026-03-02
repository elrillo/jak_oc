import pandas as pd
import psycopg2
import json

def dump():
    out = {}
    
    # Excel
    df = pd.read_excel('data/archivos_csv/diputados_historicos.xlsx')
    out['excel_columns'] = list(df.columns)
    out['excel_sample'] = df.head(2).to_dict(orient='records')
    
    # DB
    conn = psycopg2.connect("postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres")
    cur = conn.cursor()
    
    for table in ['dim_diputados', 'coautores', 'mociones']:
        cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'")
        out[f'{table}_columns'] = [r[0] for r in cur.fetchall()]
        
        cur.execute(f"SELECT * FROM {table} LIMIT 1")
        cols = [desc[0] for desc in cur.description]
        row = cur.fetchone()
        out[f'{table}_sample'] = dict(zip(cols, row)) if row else None

    # Write carefully
    with open('schema_dump.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    dump()
