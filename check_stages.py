
import psycopg2

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def check_data():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        # Get unique Estados
        cur.execute("SELECT DISTINCT estado_del_proyecto_de_ley FROM mociones")
        estados = [row[0] for row in cur.fetchall()]
        print("--- ESTADOS ---")
        for e in estados: print(f"- {e}")
        
        # Get unique Etapas
        cur.execute("SELECT DISTINCT etapa FROM mociones")
        etapas = [row[0] for row in cur.fetchall()]
        print("\n--- ETAPAS ---")
        for e in etapas: print(f"- {e}")
        
        # Check dates presence
        cur.execute("SELECT COUNT(*) FROM mociones WHERE publicado_en_diario_oficial IS NOT NULL")
        count_pub = cur.fetchone()[0]
        print(f"\n--- Con Fecha Publicación: {count_pub} ---")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_data()
