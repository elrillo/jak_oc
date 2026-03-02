import psycopg2

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def fix_whitespace():
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    
    # Trim whitespace in mociones
    cursor.execute("UPDATE mociones SET estado_del_proyecto_de_ley = BTRIM(estado_del_proyecto_de_ley)")
    print(f"Mociones (estado) actualizadas: {cursor.rowcount}")
    
    cursor.execute("UPDATE mociones SET etapa = BTRIM(etapa)")
    print(f"Mociones (etapa) actualizadas: {cursor.rowcount}")
    
    # Trim whitespace in dim_diputados
    cursor.execute("UPDATE dim_diputados SET partido_politico = BTRIM(partido_politico)")
    print(f"Dim_diputados (partido_politico) actualizadas: {cursor.rowcount}")
    
    cursor.execute("UPDATE dim_diputados SET region = BTRIM(region)")
    print(f"Dim_diputados (region) actualizadas: {cursor.rowcount}")
    
    # Some obvious standardizations
    replacements_partido = {
        "Renovacion Nacional": "Renovación Nacional",
        "Renovación Nacional ": "Renovación Nacional",
        "Union Democrata Independiente": "Unión Demócrata Independiente",
        "Unión Democrata Independiente": "Unión Demócrata Independiente",
        "Union De Centro Centro": "Unión de Centro Centro",
        "Revolucion Democratica": "Revolución Democrática",
        "Revolución Democratica": "Revolución Democrática",
        "Evolucion Politica": "Evolución Política",
        "Evolución Politica": "Evolución Política",
        "Partido Democrata Cristiano": "Partido Demócrata Cristiano",
        "Partido Convergencia Social": "Convergencia Social",
        "Independiente ": "Independiente"
    }

    for old_val, new_val in replacements_partido.items():
        cursor.execute("UPDATE dim_diputados SET partido_politico = %s WHERE partido_politico = %s", (new_val, old_val))

    replacements_region = {
        "Araucania": "Araucanía",
        "Bio Bio": "Biobío",
        "BioBio": "Biobío",
        "Valparaiso": "Valparaíso",
        "Los Rios": "Los Ríos",
        "Libertador General Bernardo O' Higgins": "O'Higgins",
        "Libertador General Bernardo O'Higgins": "O'Higgins"
    }
    
    for old_val, new_val in replacements_region.items():
        cursor.execute("UPDATE dim_diputados SET region = %s WHERE region = %s", (new_val, old_val))

    conn.commit()
    conn.close()
    print("Correcciones aplicadas con éxito.")

if __name__ == "__main__":
    fix_whitespace()
