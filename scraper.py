import os
import json
import slugify  # Opcional: pip install python-slugify
from documentcloud import DocumentCloud

def save_to_json(doc):
    # Definimos la ruta de destino
    output_dir = os.path.join('data', 'archivos_json')
    
    # Creamos la carpeta si no existe
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Limpiamos el título para el nombre del archivo
    # Nota: Si no tienes python-slugify, esta limpieza manual funciona, 
    # pero slugify es más robusto si deciden descomentar la importación y usarlo.
    clean_title = "".join([c for c in doc.title if c.isalnum() or c in (' ', '_')]).rstrip()
    
    # Construimos el nombre del archivo en la carpeta correcta
    filename = os.path.join(output_dir, f"{doc.id}_{clean_title.replace(' ', '_')}.json")
    
    if not os.path.exists(filename):
        data = {
            "id": doc.id,
            "title": doc.title,
            "url": doc.canonical_url,
            "created_at": str(doc.created_at),
            "text": doc.full_text
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    return False

def run_sync():
    # --- CREDENCIALES --- 
    # INSTRUCCIONES: Reemplaza "TU_CORREO" y "TU_CLAVE" con los datos de tu cuenta de DocumentCloud creada.
    # Opcionalmente, puedes usar variables de entorno para mayor seguridad.
    
    USERNAME = os.environ.get('DOCUMENTCLOUD_USERNAME') or "jose.carrillogar@gmail.com"
    PASSWORD = os.environ.get('DOCUMENTCLOUD_PASSWORD') or "vivalacones2703"
    
    # --------------------

    try:
        # Si no se ha cambiado el placeholder, intentamos conectar sin argumentos (buscando env vars por defecto)
        if "TU_CORREO" in USERNAME:
            print("Aviso: No se han configurado credenciales en el script. Intentando conexión anónima o por variables de entorno...")
            client = DocumentCloud()
        else:
            client = DocumentCloud(username=USERNAME, password=PASSWORD)
            
        project = client.projects.get(id="223805")
    except Exception as e:
        print(f"\n[ERROR] Falló la conexión: {e}")
        print("Asegúrate de haber ingresado tu correo y contraseña correctamente en el archivo 'scraper.py'.\n")
        return

    new_docs = 0
    # Iteramos sobre los documentos del proyecto
    # documentcloud a veces requiere paginación o devuelve un generador
    for doc in project.documents:
         # Para la librería python-documentcloud estándar suele ser client.documents.search o similar si no es direct project access
         # Asumiendo que la API del usuario es correcta para su versión de librería.
         # El código original usaba project.documents. Lo mantendremos pero agregando manejo de errores si falla.
        try:
            if save_to_json(doc):
                new_docs += 1
                print(f"Sincronizado: {doc.title}")
        except Exception as e:
            print(f"Error procesando documento: {e}")

    print(f"Proceso finalizado. {new_docs} documentos nuevos añadidos.")

if __name__ == "__main__":
    run_sync()
