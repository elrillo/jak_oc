import psycopg2
import json

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"
conn = psycopg2.connect(DB_URL)
cursor = conn.cursor()

data = {}

cursor.execute("SELECT DISTINCT estado_del_proyecto_de_ley FROM mociones")
data["estado"] = [r[0] for r in cursor.fetchall()]

cursor.execute("SELECT DISTINCT etapa FROM mociones")
data["etapa"] = [r[0] for r in cursor.fetchall()]

cursor.execute("SELECT DISTINCT partido_politico FROM dim_diputados")
data["partido"] = [r[0] for r in cursor.fetchall()]

cursor.execute("SELECT DISTINCT region FROM dim_diputados")
data["region"] = [r[0] for r in cursor.fetchall()]

with open("test_supabase_distinct.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

conn.close()
