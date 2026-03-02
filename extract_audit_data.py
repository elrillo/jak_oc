import psycopg2
import json

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def get_unique_values(cursor, table, column):
    try:
        query = f"SELECT DISTINCT {column} FROM {table} WHERE {column} IS NOT NULL ORDER BY {column}"
        cursor.execute(query)
        return [str(r[0]) for r in cursor.fetchall()]
    except Exception as e:
        print(f"Error extracting {column} from {table}: {e}")
        return []

def main():
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    
    data = {
        "dim_diputados": {},
        "mociones": {}
    }
    
    # Extract from dim_diputados
    cols_diputados = ["diputado", "partido_politico", "region", "coalicion", "bancada_comite"]
    for col in cols_diputados:
        data["dim_diputados"][col] = get_unique_values(cursor, "dim_diputados", col)
        
    # Extract from mociones
    cols_mociones = ["estado_del_proyecto_de_ley", "etapa", "tipo_de_proyecto", "camara_de_origen", "tematica"]
    for col in cols_mociones:
        data["mociones"][col] = get_unique_values(cursor, "mociones", col)

    conn.close()
    
    # Save to JSON
    with open("unique_values_audit.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print("Unique values extracted successfully.")

if __name__ == "__main__":
    main()
