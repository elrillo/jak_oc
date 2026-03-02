import psycopg2
from datetime import datetime

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def get_period(date_str):
    # Depending on format: "2002-06-05 00:00:00"
    if not date_str:
        return None
        
    try:
        d = datetime.strptime(str(date_str), '%Y-%m-%d %H:%M:%S')
    except ValueError:
        try:
            d = datetime.strptime(str(date_str), '%Y-%m-%d')
        except ValueError:
            return None
            
    year = d.year
    
    # If date is before March 11th, we treat it as the previous year for cycle calculations
    if d.month < 3 or (d.month == 3 and d.day < 11):
        effective_year = year - 1
    else:
        effective_year = year
        
    # Legislative cycles are 4 years starting from 1990
    if effective_year < 1990:
        # Pre-1990 fallback if any
        return "Pre-1990"
        
    start_year = effective_year - ((effective_year - 1990) % 4)
    end_year = start_year + 4
    
    return f"{start_year} - {end_year}"

def assign_periods():
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = True
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE mociones ADD COLUMN IF NOT EXISTS periodo_legislativo VARCHAR(20)")
    except Exception as e:
        print("Column might exist or error:", e)
        # Even with autocommit, let's rollback just in case the driver complains
        try:
            conn.rollback()
        except:
            pass
        
    cursor.execute("SELECT n_boletin, fecha_de_ingreso FROM mociones")
    rows = cursor.fetchall()
    
    updates = []
    for bol, fecha in rows:
        period = get_period(fecha)
        if period:
            updates.append((period, bol))
            
    print(f"Assigning periods to {len(updates)} records...")
    
    conn.autocommit = True
    updated = 0
    for p, b in updates:
        try:
            cursor.execute("UPDATE mociones SET periodo_legislativo = %s WHERE n_boletin = %s", (p, b))
            updated += cursor.rowcount
        except Exception as e:
            print(f"Error updating {b} with '{p}':", e)
            
    print(f"Done! {updated} records updated with their legislative period.")
    
    try:
        # Verify
        cursor.execute("SELECT periodo_legislativo, COUNT(*) FROM mociones GROUP BY periodo_legislativo ORDER BY 1")
        print("\nDistribution of periods:")
        for r in cursor.fetchall():
            print(f" - {r[0]}: {r[1]} mociones")
            
    except Exception as e:
        print("Error during verification:", e)
    
    conn.close()

if __name__ == '__main__':
    assign_periods()
