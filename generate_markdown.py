import json

def generate_markdown(data_file, output_file):
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(output_file, "w", encoding="utf-8") as out:
        out.write("# Revisión de Datos de Observatorio Congreso\n\n")
        out.write("Este documento contiene los valores únicos extraídos de la base de datos para facilitar la identificación de errores de formato, nombres duplicados o inconsistencias.\n\n")
        
        out.write("## 1. Diputados (dim_diputados)\n\n")
        
        diputados = data.get("dim_diputados", {})
        
        # Nombres de Diputados
        nombres = diputados.get("diputado", [])
        out.write("### 1.1 Nombres de Diputados (`diputado`)\n")
        out.write(f"Total únicos: {len(nombres)}\n\n")
        for i, val in enumerate(nombres):
            out.write(f"- `{val}`\n")
        out.write("\n")
        
        # Partidos Políticos
        partidos = diputados.get("partido_politico", [])
        out.write("### 1.2 Partidos Políticos (`partido_politico`)\n")
        out.write(f"Total únicos: {len(partidos)}\n\n")
        for i, val in enumerate(partidos):
            out.write(f"- `{val}`\n")
        out.write("\n")
        
        # Regiones
        regiones = diputados.get("region", [])
        out.write("### 1.3 Regiones (`region`)\n")
        out.write(f"Total únicos: {len(regiones)}\n\n")
        for i, val in enumerate(regiones):
            out.write(f"- `{val}`\n")
        out.write("\n")
        
        # Coaliciones
        coaliciones = diputados.get("coalicion", [])
        out.write("### 1.4 Coaliciones (`coalicion`)\n")
        out.write(f"Total únicos: {len(coaliciones)}\n\n")
        for i, val in enumerate(coaliciones):
            out.write(f"- `{val}`\n")
        out.write("\n")

        # Bancadas/Comités
        bancadas = diputados.get("bancada_comite", [])
        out.write("### 1.5 Bancadas y Comités (`bancada_comite`)\n")
        out.write(f"Total únicos: {len(bancadas)}\n\n")
        for i, val in enumerate(bancadas):
            out.write(f"- `{val}`\n")
        out.write("\n")
        
        
        out.write("---\n\n## 2. Mociones (mociones)\n\n")
        
        mociones = data.get("mociones", {})
        
        # Estados
        estados = mociones.get("estado_del_proyecto_de_ley", [])
        out.write("### 2.1 Estado del Proyecto (`estado_del_proyecto_de_ley`)\n")
        out.write(f"Total únicos: {len(estados)}\n\n")
        for i, val in enumerate(estados):
            out.write(f"- `{val}`\n")
        out.write("\n")
        
        # Etapas
        etapas = mociones.get("etapa", [])
        out.write("### 2.2 Etapas (`etapa`)\n")
        out.write(f"Total únicos: {len(etapas)}\n\n")
        for i, val in enumerate(etapas):
            out.write(f"- `{val}`\n")
        out.write("\n")
        
        # Tipo de Proyecto
        tipos = mociones.get("tipo_de_proyecto", [])
        out.write("### 2.3 Tipo de Proyecto (`tipo_de_proyecto`)\n")
        out.write(f"Total únicos: {len(tipos)}\n\n")
        for i, val in enumerate(tipos):
            out.write(f"- `{val}`\n")
        out.write("\n")

        # Camara de Origen
        camaras = mociones.get("camara_de_origen", [])
        out.write("### 2.4 Cámara de Origen (`camara_de_origen`)\n")
        out.write(f"Total únicos: {len(camaras)}\n\n")
        for i, val in enumerate(camaras):
            out.write(f"- `{val}`\n")
        out.write("\n")
        
        # Tematica
        tematicas = mociones.get("tematica", [])
        out.write("### 2.5 Temáticas Principales (`tematica`)\n")
        out.write(f"Total únicos: {len(tematicas)}\n\n")
        for i, val in enumerate(tematicas):
            out.write(f"- `{val}`\n")
        out.write("\n")
        
    print(f"Report generated at {output_file}")

if __name__ == "__main__":
    generate_markdown("unique_values_audit.json", "revision_datos_observatorio.md")
