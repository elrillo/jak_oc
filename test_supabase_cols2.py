import psycopg2
import json

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"
conn = psycopg2.connect(DB_URL)
cursor = conn.cursor()

data = {}
cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'mociones'")
data["mociones"] = [r[0] for r in cursor.fetchall()]

cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'dim_diputados'")
data["dim_diputados"] = [r[0] for r in cursor.fetchall()]

cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'coautores'")
data["coautores"] = [r[0] for r in cursor.fetchall()]

with open("test_supabase_output.json", "w") as f:
    json.dump(data, f)
