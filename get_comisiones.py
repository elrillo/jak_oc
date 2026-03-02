import json
import psycopg2

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def get_comisiones():
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT comision_inicial FROM mociones WHERE comision_inicial IS NOT NULL ORDER BY comision_inicial")
    comisiones = [str(r[0]) for r in cursor.fetchall()]
    conn.close()
    
    with open("comisiones.json", "w", encoding="utf-8") as f:
        json.dump(comisiones, f, ensure_ascii=False, indent=2)
        
if __name__ == "__main__":
    get_comisiones()
