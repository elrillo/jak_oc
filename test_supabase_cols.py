import psycopg2

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"
conn = psycopg2.connect(DB_URL)
cursor = conn.cursor()

cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'mociones'")
print("mociones columns:", [r[0] for r in cursor.fetchall()])

cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'dim_diputados'")
print("dim_diputados columns:", [r[0] for r in cursor.fetchall()])
