import json
import unicodedata
from collections import defaultdict

def analyze_names(data_file):
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    nombres = data.get("dim_diputados", {}).get("diputado", [])
    
    cleaned_mapping = {}
    
    def remove_accents(input_str):
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

    for name in nombres:
        clean_name = name.strip()
        clean_name = " ".join(clean_name.split())
        clean_name = clean_name.replace("´", "'").replace("`", "'")
        
        # specific hardcoded cases
        clean_name = clean_name.replace("D' Albora", "D'Albora")
        clean_name = clean_name.replace("Dalbora", "D'Albora")
        
        if clean_name != name:
            cleaned_mapping[name] = clean_name
            
    accent_groups = defaultdict(list)
    for index, name in enumerate(nombres):
        clean_version = cleaned_mapping.get(name, name)
        base = remove_accents(clean_version).lower()
        accent_groups[base].append(name)

    # Write to a proper text file
    with open("duplicados_diputados.txt", "w", encoding="utf-8") as out:
        out.write(f"Nombres con espacios o comillas solucionables: {len(cleaned_mapping)}\n\n")
        out.write("Grupos de nombres similares que parecen ser la misma persona:\n")
        
        for base, group in sorted(accent_groups.items()):
            # Solo queremos ver grupos donde hay variaciones (por ejemplo "Jose Kast" vs "José Kast")
            # o variantes con espacios erróneos (ya detectados en el base)
            if len(set(group)) > 1:
                # El "oficial" será el que tenga tilde o comilla correcta, heurística simple: elegir el más largo
                # o el que tiene caracteres especiales correctos. Lo mostramos.
                out.write(f"\n--- Grupo: {base} ---\n")
                for orig in sorted(set(group)):
                    out.write(f" - {orig}\n")
                    
if __name__ == "__main__":
    analyze_names("unique_values_audit.json")
