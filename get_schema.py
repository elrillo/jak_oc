import psycopg2

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def get_schema():
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    
    tables = ['mociones', 'dim_diputados', 'coautores', 'textos_pdf', 'analisis_ia']
    
    with open('schema_utf8.txt', 'w', encoding='utf-8') as f:
        for table in tables:
            f.write(f"--- Schema for {table} ---\n")
            cursor.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table}';
            """)
            columns = cursor.fetchall()
            for col in columns:
                f.write(f"- {col[0]} ({col[1]})\n")
            f.write("\n")
        
    conn.close()

if __name__ == "__main__":
    get_schema()
