import psycopg2
import pandas as pd
import json

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def run_analysis():
    conn = psycopg2.connect(DB_URL)
    
    queries = {
        "top_coautores": """
            SELECT c.diputado_normalizado, COUNT(DISTINCT c.n_boletin) as total_leyes
            FROM coautores c
            WHERE c.diputado_normalizado NOT ILIKE '%Kast Rist%'
            GROUP BY c.diputado_normalizado
            ORDER BY total_leyes DESC
            LIMIT 10;
        """,
        "partidos_vinculados": """
            SELECT 
                COALESCE(d.partido_politico_normalizado, 'Desconocido/Sin Partido') as partido,
                COUNT(c.n_boletin) as total_firmas
            FROM coautores c
            JOIN mociones m ON c.n_boletin = m.n_boletin
            LEFT JOIN dim_diputados d 
              ON c.diputado_normalizado = d.diputado_normalizado 
             AND m.periodo_legislativo = d.periodo
            WHERE c.diputado_normalizado NOT ILIKE '%Kast Rist%'
            GROUP BY 1
            ORDER BY 2 DESC;
        """,
        "coaliciones": """
            SELECT 
                COALESCE(d.coalicion_normalizada, 'Independiente/Otras') as coalicion,
                COUNT(c.n_boletin) as total_firmas
            FROM coautores c
            JOIN mociones m ON c.n_boletin = m.n_boletin
            LEFT JOIN dim_diputados d 
              ON c.diputado_normalizado = d.diputado_normalizado 
             AND m.periodo_legislativo = d.periodo
            WHERE c.diputado_normalizado NOT ILIKE '%Kast Rist%'
            GROUP BY 1
            ORDER BY 2 DESC;
        """,
        "sexo": """
            SELECT 
                COALESCE(d.sexo, 'Desconocido') as sexo,
                COUNT(c.n_boletin) as total_firmas
            FROM coautores c
            JOIN mociones m ON c.n_boletin = m.n_boletin
            LEFT JOIN dim_diputados d 
              ON c.diputado_normalizado = d.diputado_normalizado 
             AND m.periodo_legislativo = d.periodo
            WHERE c.diputado_normalizado NOT ILIKE '%Kast Rist%'
            GROUP BY 1
            ORDER BY 2 DESC;
        """,
        "tematicas_mociones": """
            SELECT tematica_asociada, count(*) as cantidad 
            FROM mociones 
            GROUP BY tematica_asociada 
            ORDER BY cantidad DESC;
        """,
        "periodos": """
            SELECT periodo_legislativo, count(*) as cantidad 
            FROM mociones 
            GROUP BY periodo_legislativo 
            ORDER BY periodo_legislativo;
        """
    }

    results = {}
    
    for key, sql in queries.items():
        try:
            df = pd.read_sql(sql, conn)
            results[key] = df.to_dict(orient='records')
        except Exception as e:
            print(f"Error in {key}: {e}")
            
    conn.close()
    
    with open('analisis_datos_actualizado.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
        print("Analysis generated: analisis_datos_actualizado.json")

if __name__ == '__main__':
    run_analysis()
