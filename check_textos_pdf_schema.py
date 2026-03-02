import psycopg2

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def check_cols():
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'textos_pdf'")
    col_names = [row[0] for row in cursor.fetchall()]
    print("Columnas en textos_pdf:", col_names)
    
    # Also get 1 sample to see what n_boletin looks like
    cursor.execute("SELECT * FROM textos_pdf LIMIT 1")
    row = cursor.fetchone()
    if row:
        print("Ejemplo de datos:", row[:2])  # Just first 2 columns to avoid large text
    conn.close()

if __name__ == "__main__":
    check_cols()
