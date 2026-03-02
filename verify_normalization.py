import psycopg2
import json

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def verify():
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    
    report = []
    
    report.append("=== VERIFICACION DE NORMALIZACION ===\n")
    
    # 1. Diputados: Partido
    cursor.execute("SELECT DISTINCT partido_politico_normalizado FROM dim_diputados ORDER BY 1")
    partidos = [str(r[0]) for r in cursor.fetchall()]
    report.append("PARTIDOS NORMALIZADOS:")
    for p in partidos: report.append(f" - {p}")
    
    if "Partido Por La Democracia" in partidos or "Partido Regionalista Independiente (PRI)" in partidos:
        report.append("\n[ ERROR ] Aún existen partidos no homologados.")
    else:
        report.append("\n[ OK ] Partidos clave homologados correctamente.")
        
    # 2. Diputados: Región 
    cursor.execute("SELECT DISTINCT region_normalizada FROM dim_diputados ORDER BY 1")
    regiones = [str(r[0]) for r in cursor.fetchall()]
    report.append("\nREGIONES NORMALIZADAS:")
    for r in regiones: report.append(f" - {r}")
    
    has_parens = any("(" in r for r in regiones if r and r != "None")
    if has_parens:
        report.append("\n[ ERROR ] Aún existen regiones con paréntesis.")
    else:
        report.append("\n[ OK ] Regiones sin paréntesis.")
        
    # 3. Mociones: Categorización
    cursor.execute("SELECT tematica_asociada, COUNT(*) FROM mociones GROUP BY tematica_asociada ORDER BY 2 DESC")
    tematicas = cursor.fetchall()
    report.append("\nDISTRIBUCIÓN DE TEMÁTICAS ASOCIADAS:")
    for t in tematicas:
        report.append(f" - {t[0]}: {t[1]}")
        
    # 4. Nombres agrupados de prueba
    cursor.execute("SELECT DISTINCT diputado_normalizado FROM dim_diputados WHERE diputado_normalizado LIKE '%Albora%' OR diputado_normalizado LIKE '%Kast%'")
    names = [str(r[0]) for r in cursor.fetchall()]
    report.append("\nPRUEBA NOMBRES NORMALIZADOS (Albora / Kast):")
    for n in names: report.append(f" - {n}")
        
    conn.close()
    
    with open("reporte_normalizacion.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(report))
        
    print("Report completed.")

if __name__ == "__main__":
    verify()
