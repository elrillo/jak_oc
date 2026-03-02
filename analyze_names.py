import json
from collections import defaultdict

def analyze_names(data_file):
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    nombres = data.get("dim_diputados", {}).get("diputado", [])
    
    cleaned_mapping = {}
    
    for name in nombres:
        # Initial string
        clean_name = name.strip()
        # Replace multiple spaces with single
        clean_name = " ".join(clean_name.split())
        # Normalize quotes
        clean_name = clean_name.replace("´", "'").replace("`", "'")
        
        # specific hardcoded based on user observation:
        clean_name = clean_name.replace("D' Albora", "D'Albora")
        clean_name = clean_name.replace("Dalbora", "D'Albora")
        
        # specific for another one
        
        if clean_name != name:
            cleaned_mapping[name] = clean_name
            
    print(f"Encontrados {len(cleaned_mapping)} nombres con problemas de espacios o comillas.")
    
    # Let's save the mapping and also let's look for names that are identical ignoring accents
    import unicodedata
    def remove_accents(input_str):
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

    cleaned_names_list = [cleaned_mapping.get(n, n) for n in nombres]
    
    accent_groups = defaultdict(list)
    for index, name in enumerate(cleaned_names_list):
        base = remove_accents(name).lower()
        # Also clean some common words like  " Gonzalez" vs " González"
        accent_groups[base].append(nombres[index])
    
    # Display groups that have more than 1 distinct original name
    print("\nGrupos de nombres que parecen ser la misma persona (difieren en tildes, espacios, etc):")
    for base, group in accent_groups.items():
        if len(set(group)) > 1:
            print(f"- Grupo Base '{base}':")
            for orig in sorted(set(group)):
                print(f"    '{orig}'")

if __name__ == "__main__":
    analyze_names("unique_values_audit.json")
