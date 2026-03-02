import psycopg2

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def clean_name(name):
    """Normalize a name by removing common titles and extra spaces for matching."""
    if not name: return ""
    return name.replace('H.', '').replace('DIPUTADO', '').strip().upper()

def generate_report():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    # 1. Get all unique normalized names from dim_diputados
    cur.execute("SELECT DISTINCT diputado_normalizado FROM dim_diputados")
    # Store as a dictionary mapped by their cleaned upper-case base name
    # e.g., "IGNACIO URRUTIA BONILLA" -> "Ignacio Urrutia Bonilla"
    dim_names = [r[0].strip() for r in cur.fetchall() if r[0]]
    
    # Let's map dim_names efficiently to support partial matching
    # "IGNACIO URRUTIA B." could match "IGNACIO URRUTIA BONILLA"
    
    # 2. Get all unique authors from coautores
    cur.execute("SELECT DISTINCT diputado_normalizado FROM coautores")
    coautores = [r[0].strip() for r in cur.fetchall() if r[0]]
    
    exact_matches = 0
    fuzzy_matches = {}
    ambiguous = []
    unmatched = []
    
    for c in coautores:
        c_clean = clean_name(c)
        
        # Split abbreviated name (e.g., "Ignacio Urrutia B.") -> "IGNACIO URRUTIA"
        parts = c_clean.split()
        if not parts:
            continue
            
        # Is it an exact match?
        if c in dim_names:
            exact_matches += 1
            continue
            
        # If last part is length 1 or ends with dot, it's an initial
        last_part = parts[-1]
        if len(last_part) == 1 or last_part.endswith('.'):
            base_name = " ".join(parts[:-1]) # "IGNACIO URRUTIA"
            initial = last_part[0]
        else:
            base_name = c_clean
            initial = None
            
        # Find matches in dim_names
        possible_matches = []
        for d in dim_names:
            d_clean = clean_name(d)
            if d_clean.startswith(base_name):
                # If there's an initial, ensure the last name in dim_diputados starts with that initial
                if initial:
                    # Let's check the part after the base name
                    remainder = d_clean[len(base_name):].strip()
                    if remainder and remainder[0] == initial:
                        possible_matches.append(d)
                else:
                    possible_matches.append(d)
                    
        if len(possible_matches) == 1:
            fuzzy_matches[c] = possible_matches[0]
        elif len(possible_matches) > 1:
            ambiguous.append((c, possible_matches))
        else:
            # Let's try checking reversed combinations or missing accents
            unmatched.append(c)
            
    # Write report
    with open('anomalias_diputados.log', 'w', encoding='utf-8') as f:
        f.write("=== REPORTE DE ANOMALIAS Y MAPEOS DE DIPUTADOS ===\n\n")
        f.write(f"Total únicos en coautores:     {len(coautores)}\n")
        f.write(f"Match exacto validos (Ok):     {exact_matches}\n")
        f.write(f"Match difuso único resuelto:   {len(fuzzy_matches)}\n")
        f.write(f"Ambigüedades (Varios Match):   {len(ambiguous)}\n")
        f.write(f"Sin Match Posible (Huérfanos): {len(unmatched)}\n\n")
        
        f.write("--- AMBIGUOS (Requieren decisión humana) ---\n")
        for short, matches in ambiguous:
            f.write(f"Original: '{short}' -> Opciones: {matches}\n")
            
        f.write("\n--- HUÉRFANOS (Sin coincidencia en dim_diputados) ---\n")
        for u in unmatched:
            f.write(f"Original: '{u}'\n")
            
        f.write("\n--- MUESTRA MATCH DIFUSO RESOLUBLE (Se arreglarán automáticamente) ---\n")
        for i, (short, full) in enumerate(fuzzy_matches.items()):
            if i < 20:
                f.write(f"'{short}' -> '{full}'\n")

    print(f"Reporte generado: {exact_matches} OK, {len(fuzzy_matches)} corregibles, {len(ambiguous)} ambiguos, {len(unmatched)} huerfanos.")

if __name__ == '__main__':
    generate_report()
