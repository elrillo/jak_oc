import os
import json
import psycopg2
import re

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def debug():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("SELECT n_boletin FROM textos_pdf WHERE texto_mocion IS NULL OR length(texto_mocion) < 50")
    missing_boletines = [r[0] for r in cur.fetchall()]
    
    print(f"Missing in DB: {len(missing_boletines)}")
    
    # Let's load all JSONs
    json_dir = os.path.join("data", "archivos_json")
    files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
    
    titles = []
    for f in files:
        with open(os.path.join(json_dir, f), 'r', encoding='utf-8') as file:
            data = json.load(file)
            titles.append((f, data.get('title', ''), len(data.get('text', ''))))
            
    # Now let's try to match them
    unmatched = []
    matched = 0
    
    for mb in missing_boletines:
        # mb is like '6909-07'
        parts = mb.split('-')
        if len(parts) == 2:
            num1, num2 = parts
            found = False
            for f, t, l in titles:
                # search both parts in title
                if num1 in t and num2 in t:
                    print(f"Match found for {mb}: file={f}, title='{t}', len={l}")
                    found = True
                    matched += 1
                    break
            if not found:
                unmatched.append(mb)
        else:
            print("Weird format:", mb)
            unmatched.append(mb)
            
    print(f"\nTotal matched: {matched}")
    print(f"Still unmatched: {unmatched}")
    
if __name__ == '__main__':
    debug()
