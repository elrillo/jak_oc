
import psycopg2
import pandas as pd
import json

# Connection string (from user's previous files)
DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def analyze_alliances():
    try:
        conn = psycopg2.connect(DB_URL)
        print("Connected to Supabase.")
        
        # 1. Identify JAK's name variations or exact match in the DB
        # We start by finding the exact name string for JAK.
        cursor = conn.cursor()
        
        # DEBUG: Check columns
        cursor.execute("SELECT * FROM coautores LIMIT 1;")
        colnames = [desc[0] for desc in cursor.description]
        print(f"Columns in coautores: {colnames}")

        cursor.execute("SELECT DISTINCT diputado FROM coautores WHERE diputado ILIKE '%Jose Antonio Kast%' OR diputado ILIKE '%José Antonio Kast%';")
        jak_names = [row[0] for row in cursor.fetchall()]
        
        if not jak_names:
            print("Could not find José Antonio Kast in coautores table.")
            return

        print(f"Identified JAK as: {jak_names}")
        
        # 2. Get all projects (boletines) co-authored by JAK
        jak_names_placeholder = ', '.join([f"'{name}'" for name in jak_names])
        query_projects = f"""
        SELECT DISTINCT n_boletin 
        FROM coautores 
        WHERE diputado IN ({jak_names_placeholder});
        """
        df_projects = pd.read_sql(query_projects, conn)
        print(f"JAK has co-authored {len(df_projects)} projects.")
        
        if df_projects.empty:
            return

        # 3. Find other deputies in these projects
        boletines = tuple(df_projects['n_boletin'].tolist())
        # Handling single element tuple for SQL syntax
        if len(boletines) == 1:
            boletines_str = f"('{boletines[0]}')"
        else:
            boletines_str = str(boletines)

        query_alliances = f"""
        SELECT 
            c.diputado as coauthor_name,
            c.n_boletin
        FROM coautores c
        WHERE c.n_boletin IN {boletines_str}
        AND c.diputado NOT IN ({jak_names_placeholder});
        """
        df_alliances_raw = pd.read_sql(query_alliances, conn)
        
        # 4. Join with dim_diputados to get attributes
        # Since dim_diputados has (diputado, periodo) as PK, we might have duplicates for the same person.
        # We will fetch all dim_diputados and dedup by keeping the latest period or random if unchanged.
        query_dims = "SELECT * FROM dim_diputados;"
        df_dims = pd.read_sql(query_dims, conn)
        
        # De-duplicate dim_diputados: keep entries with latest period or just drop duplicates on name
        # Assuming 'periodo' is comparable or we don't care too much about historical changes for this general analysis
        # We will sort by period (descending) if possible to keep latest info
        df_dims = df_dims.sort_values(by='periodo', ascending=False).drop_duplicates(subset=['diputado'])
        
        # Merge
        df_merged = pd.merge(df_alliances_raw, df_dims, left_on='coauthor_name', right_on='diputado', how='left')
        
        # CLEANING DATA FOR REPORT
        # Normalize strings to avoid "Hombre " vs "Hombre"
        for col in ['partido_politico', 'sexo', 'coalicion']:
            if col in df_merged.columns:
                df_merged[col] = df_merged[col].astype(str).str.strip().str.title()
                # Handle 'None' or 'Nan' strings result
                df_merged[col] = df_merged[col].replace({'Nan': None, 'None': None})

        # Specific Party Normalization (Tildes handling simplified)
        # Using unidecode-style simple replacement if needed, 
        # but title() + strip() covers trailing spaces and casing.
        # We can also handle simple spelling variants if obvious.
        if 'partido_politico' in df_merged.columns:
             df_merged['partido_politico'] = df_merged['partido_politico'].str.replace('Union ', 'Unión ', regex=False)
             df_merged['partido_politico'] = df_merged['partido_politico'].str.replace('Renovacion', 'Renovación', regex=False)
             df_merged['partido_politico'] = df_merged['partido_politico'].str.replace('Democrata', 'Demócrata', regex=False)

        # 5. Ranking Top 10
        top_10 = df_merged['coauthor_name'].value_counts().head(10).reset_index()
        top_10.columns = ['Diputado', 'Coautorias']
        print("\n--- Top 10 Alianzas (Coautorías) ---")
        print(top_10)
        
        # 6. Distribution by Party
        # Count unique co-authorships (project + deputy) per party
        # Or do we want 'number of unique deputies per party' or 'number of signatures per party'?
        # "distribución de estas alianzas" usually means number of signatures.
        dist_party = df_merged['partido_politico'].value_counts().reset_index()
        dist_party.columns = ['Partido', 'Cantidad']
        print("\n--- Distribución por Partido ---")
        print(dist_party.head())
        
        top_party = dist_party.iloc[0]['Partido'] if not dist_party.empty else "N/A"
        print(f"\nPartido con mayor afinidad: {top_party}")

        # 7. Distribution by Sex
        dist_sex = df_merged['sexo'].value_counts().reset_index()
        dist_sex.columns = ['Sexo', 'Cantidad']
        print("\n--- Distribución por Sexo ---")
        print(dist_sex)
        
        # 8. Transversality (refined based on Party)
        # JAK is associated with the Right-wing coalition (UDI/Republicanos). 
        # Coalition names change over time (Alianza -> Chile Vamos), so we map by Party for consistency.
        
        right_wing_parties = [
            'Unión Demócrata Independiente', 
            'Renovación Nacional', 
            'Partido Republicano', 
            'Evópoli', 
            'Partido Regionalista Independiente (Pri)',
            'Chile Vamos'
        ]
        
        def classify_transversality_by_party(party):
            if not party: return "Desconocido"
            if any(p in party for p in right_wing_parties):
                return "Misma Coalición (Derecha)"
            if "Independiente" in party and "Ilb" not in party: # Basic indie check
                return "Independiente"
            return "Oposición (Centro/Izquierda)"

        df_merged['transversality'] = df_merged['partido_politico'].apply(classify_transversality_by_party)
        dist_trans = df_merged['transversality'].value_counts().reset_index()
        dist_trans.columns = ['Tipo', 'Cantidad']
        print("\n--- Transversalidad (Basado en Partidos) ---")
        print(dist_trans)
        
        # 9. Generate JSON for Network Graph
        # Nodes: JAK + All coauthors
        # Links: JAK -> Coauthor (weight = count)
        
        # Central Node
        nodes = [{"id": name, "group": "Central"} for name in jak_names]
        
        # Other Nodes
        # Unique coauthors
        unique_coauthors = df_merged[['coauthor_name', 'partido_politico']].drop_duplicates()
        for _, row in unique_coauthors.iterrows():
            nodes.append({
                "id": row['coauthor_name'],
                "group": row['partido_politico'] if row['partido_politico'] else "Unknown"
            })
            
        # Links
        # We aggregate counts first
        alliance_counts = df_merged['coauthor_name'].value_counts().reset_index()
        alliance_counts.columns = ['target', 'weight']
        
        links = []
        source_name = jak_names[0] # picking the first one as distinct source
        for _, row in alliance_counts.iterrows():
            links.append({
                "source": source_name,
                "target": row['target'],
                "weight": int(row['weight'])
            })
            
        graph_data = {
            "nodes": nodes,
            "links": links
        }
        
        with open("jak_alliances_graph.json", "w", encoding='utf-8') as f:
            json.dump(graph_data, f, ensure_ascii=False, indent=2)
        print("\nGraph data saved to jak_alliances_graph.json")
        
        # Save summaries to text file for easy reading
        with open("analysis_summary.txt", "w", encoding='utf-8') as f:
            f.write("--- Top 10 Alianzas ---\n")
            f.write(top_10.to_string())
            f.write("\n\n--- Distribución por Partido ---\n")
            f.write(dist_party.to_string())
            f.write("\n\n--- Distribución por Sexo ---\n")
            f.write(dist_sex.to_string())
            f.write(f"\n\n--- Transversalidad (Basado en bloques ideológicos) ---\n")
            f.write(dist_trans.to_string())

    except Exception as e:
        print(f"Error during analysis: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    analyze_alliances()
