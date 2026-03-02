import psycopg2

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def update_categories():
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = False
    cursor = conn.cursor()

    try:
        # Based on the implementation plan, the new mapping is:
        # 1. Constitución y Justicia -> Constitución y Justicia (Includes Régimen Interno)
        # 2. Economía y Hacienda -> Economía y Hacienda
        # 3. Desarrollo Social y Familia -> Familia y Social (Renaming)
        # 4. Educación, Ciencia, Cultura y Deporte -> Educación, Cultura y Deporte (includes Ciencias)
        # 5. Salud -> Salud
        # 6. Vivienda e Infraestructura -> Vivienda e Infraestructura
        # 7. Ciudadanía y DD.HH. -> DD.HH. y Nacionalidad (Renaming)
        # 8. Seguridad y Defensa Nacional -> Seguridad y Defensa (Renaming)
        # 9. Medio Ambiente y Recursos Naturales -> Medio Ambiente y Recursos (Renaming)
        # 10. Gobierno Interior -> Gobierno Interior

        updates = [
            # Exact Renaming of existing mapped groups
            ("UPDATE mociones SET tematica_asociada = 'Desarrollo Social y Familia' WHERE tematica_asociada = 'Familia y Social';", []),
            ("UPDATE mociones SET tematica_asociada = 'Educación, Ciencia, Cultura y Deporte' WHERE tematica_asociada = 'Educación, Cultura y Deporte';", []),
            ("UPDATE mociones SET tematica_asociada = 'Ciudadanía y DD.HH.' WHERE tematica_asociada = 'DD.HH. y Nacionalidad';", []),
            ("UPDATE mociones SET tematica_asociada = 'Seguridad y Defensa Nacional' WHERE tematica_asociada = 'Seguridad y Defensa';", []),
            ("UPDATE mociones SET tematica_asociada = 'Medio Ambiente y Recursos Naturales' WHERE tematica_asociada = 'Medio Ambiente y Recursos';", []),
            
            # Reassigning "Otras"
            ("UPDATE mociones SET tematica_asociada = 'Educación, Ciencia, Cultura y Deporte' WHERE comision_inicial = 'Ciencias y Tecnología';", []),
            ("UPDATE mociones SET tematica_asociada = 'Constitución y Justicia' WHERE comision_inicial LIKE '%%Régimen Interno%%';", [])
        ]

        print("Updating categories...")
        total_updated = 0
        for query, params in updates:
            cursor.execute(query, params)
            total_updated += cursor.rowcount
            
        # Optional: clean up any remaining "Otras" just in case they were missed, although we specifically remapped them.
        cursor.execute("SELECT n_boletin, comision_inicial FROM mociones WHERE tematica_asociada = 'Otras'")
        remaining_otras = cursor.fetchall()
        if remaining_otras:
            print(f"Warning: {len(remaining_otras)} motions still have 'Otras' as category:")
            for b, c in remaining_otras:
                print(f"  - {b}: {c}")
                
        conn.commit()
        print(f"Categories update complete. Rows affected across operations: {total_updated}")

        # Show verification summary
        cursor.execute("SELECT tematica_asociada, COUNT(*) FROM mociones GROUP BY tematica_asociada ORDER BY 2 DESC")
        print("\nNew Category Distribution:")
        for row in cursor.fetchall():
            print(f" - {row[0]}: {row[1]}")

    except Exception as e:
        print("Error updating categories:", e)
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    update_categories()
