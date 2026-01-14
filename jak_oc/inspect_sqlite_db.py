
import sqlite3
import pandas as pd

DB_PATH = "database/jak_observatorio.db"

def inspect_sqlite():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables:", tables)
        
        for table_name in [t[0] for t in tables]:
            print(f"\n--- {table_name} ---")
            # Get columns
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            for col in columns:
                print(f"{col[1]} ({col[2]})")
            
            # Sample data
            try:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                print("Sample:", cursor.fetchone())
            except:
                pass
                
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_sqlite()
