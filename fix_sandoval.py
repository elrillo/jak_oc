import psycopg2

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def fix():
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("UPDATE coautores SET diputado_normalizado = 'David Sandoval Plaza' WHERE diputado_normalizado = 'Gabriel Sandoval Plaza'")
    print(f"Rows updated: {cur.rowcount}")

if __name__ == '__main__':
    fix()
