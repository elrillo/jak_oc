
import sqlite3
import pandas as pd

DB_PATH = "database/jak_observatorio.db"

def inspect_sqlite():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # List tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables in SQLite DB:", [t[0] for t in tables])
        
        # Check columns for potential tables
        for table in tables:
            t_name = table[0]
            print(f"\nColumns in {t_name}:")
            # method 1: pragma
            cursor.execute(f"PRAGMA table_info({t_name})")
            cols = cursor.fetchall()
            for c in cols:
                print(f" - {c[1]} (Type: {c[2]})")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_sqlite()
