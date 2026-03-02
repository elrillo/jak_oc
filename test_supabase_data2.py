import psycopg2
import traceback

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def main():
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    
    print("--- mociones: estado ---")
    cursor.execute("SELECT DISTINCT estado FROM mociones")
    for r in cursor.fetchall():
        print(repr(r[0]))
        
    print("\n--- mociones: etapa ---")
    cursor.execute("SELECT DISTINCT etapa FROM mociones")
    for r in cursor.fetchall():
        print(repr(r[0]))
        
    print("\n--- dim_diputados: partido ---")
    cursor.execute("SELECT DISTINCT partido FROM dim_diputados")
    for r in cursor.fetchall():
        print(repr(r[0]))
        
    print("\n--- dim_diputados: region ---")
    cursor.execute("SELECT DISTINCT region FROM dim_diputados")
    for r in cursor.fetchall():
        print(repr(r[0]))

    conn.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        traceback.print_exc()
