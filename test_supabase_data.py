import psycopg2

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

try:
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    print("Conexión exitosa a Supabase!")
    
    tablas = ['mociones', 'dim_diputados', 'coautores']
    
    for t in tablas:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {t}")
            cnt = cursor.fetchone()[0]
            print(f"Tabla {t}: {cnt} registros")
        except Exception as e:
            print(f"Error evaluando tabla {t}: {e}")
            conn.rollback()
            
    # Valores extraños en estado/etapa de mociones
    try:
        cursor.execute("SELECT DISTINCT estado FROM mociones LIMIT 50")
        estados = [str(x[0]) for x in cursor.fetchall()]
        print(f"\nEstados distintos en mociones: {estados}")
        
        cursor.execute("SELECT DISTINCT etapa FROM mociones LIMIT 50")
        etapas = [str(x[0]) for x in cursor.fetchall()]
        print(f"Etapas distintas en mociones: {etapas}")
    except Exception as e:
        print("No se pudo obtener estados/etapas.")
        conn.rollback()
        
    conn.close()
except Exception as e:
    print(f"Error conectando: {e}")
