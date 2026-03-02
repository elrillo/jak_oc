import json
import unicodedata
import re
import psycopg2
from psycopg2 import sql

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def sanitize_name(name):
    if not name: return name
    clean = name.strip()
    clean = " ".join(clean.split())
    clean = clean.replace("´", "'").replace("`", "'")
    clean = clean.replace("D' Albora", "D'Albora")
    clean = clean.replace("Dalbora", "D'Albora")
    return clean

# Mapping from base (no accents, lower) to the best written version
OFFICIAL_NAMES = {
    "adriana munoz d'albora": "Adriana Muñoz D'Albora",
    "alberto cardemil herrera": "Alberto Cardemil Herrera",
    "aldo cornejo gonzalez": "Aldo Cornejo González",
    "alejandra sepulveda orbenes": "Alejandra Sepúlveda Orbenes",
    "alejandro garcia-huidobro sanfuentes": "Alejandro García-Huidobro Sanfuentes",
    "alfonso de urresti longton": "Alfonso de Urresti Longton",
    "alfonso vargas lyng": "Alfonso Vargas Lyng",
    "andres aylwin azocar": "Andrés Aylwin Azócar",
    "andres egana respaldiza": "Andrés Egaña Respaldiza",
    "andres palma irarrazaval": "Andrés Palma Irarrázaval",
    "angel fantuzzi hernandez": "Angel Fantuzzi Hernández",
    "antonio leal labrin": "Antonio Leal Labrin",
    "armando arancibia calderon": "Armando Arancibia Calderón",
    "carlos caminondo saez": "Carlos Caminondo Sáez",
    "carlos dupre silva": "Carlos Dupré Silva",
    "carlos valcarce medina": "Carlos Valcarce Medina",
    "carlos vilches guzman": "Carlos Vilches Guzmán",
    "carolina toha morales": "Carolina Tohá Morales",
    "claudia nogueira fernandez": "Claudia Nogueira Fernández",
    "claudio rodriguez cataldo": "Claudio Rodríguez Cataldo",
    "cristian monckeberg bruner": "Cristián Monckeberg Bruner",
    "cristina girardi lavin": "Cristina Girardi Lavín",
    "dario paya mira": "Darío Paya Mira",
    "eduardo diaz del rio": "Eduardo Díaz Del Río",
    "eduardo saffirio suarez": "Eduardo Saffirio Suárez",
    "eliana caraball martinez": "Eliana Caraball Martínez",
    "ernesto silva mendez": "Ernesto Silva Méndez",
    "esteban valenzuela van treek": "Esteban Valenzuela Van Treek",
    "eugenio munizaga rodriguez": "Eugenio Munizaga Rodríguez",
    "evelyn matthei fornet": "Evelyn Matthei Fornet",
    "felipe harboe bascunan": "Felipe Harboe Bascuñán",
    "felipe valenzuela herrera": "Felipe Valenzuela Herrera",
    "francisco bartolucci johnston": "Francisco Bartolucci Johnston",
    "frank sauerbaum munoz": "Frank Sauerbaum Muñoz",
    "fuad chahin valenzuela": "Fuad Chahín Valenzuela",
    "fulvio rossi ciocca": "Fulvio Rossi Ciocca",
    "gabriel silber romo": "Gabriel Silber Romo",
    "gaspar rivas sanchez": "Gaspar Rivas Sánchez",
    "gaston von muhlenbrock zamora": "Gastón Von Mühlenbrock Zamora",
    "german becker alvear": "Germán Becker Alvear",
    "gonzalo ibanez santa maria": "Gonzalo Ibañez Santa Maria",
    "guillermo teillier del valle": "Guillermo Teillier del Valle",
    "gutenberg martinez ocamica": "Gutenberg Martínez Ocamica",
    "isabel allende bussi": "Isabel Allende Bussi",
    "isidoro toha gonzalez": "Isidoro Tohá González",
    "issa kort garriga": "Issa Kort Garriga",
    "ivan flores garcia": "Iván Flores García",
    "ivan moreira barros": "Iván Moreira Barros",
    "ivan norambuena farias": "Iván Norambuena Farías",
    "ivan paredes fierro": "Iván Paredes Fierro",
    "jaime mulet martinez": "Jaime Mulet Martínez",
    "jaime naranjo ortiz": "Jaime Naranjo Ortiz",
    "javier hernandez hernandez": "Javier Hernández Hernández",
    "javier macaya danus": "Javier Macaya Danús",
    "jenny alvarez vera": "Jenny Álvarez Vera",
    "joaquin godoy ibanez": "Joaquín Godoy Ibáñez",
    "joaquin lavin leon": "Joaquín Lavín León",
    "joaquin palma irarrazaval": "Joaquín Palma Irarrázaval",
    "joaquin tuma zedan": "Joaquín Tuma Zedán",
    "jorge pizarro soto": "Jorge Pizarro Soto",
    "jorge rathgeb schifferli": "Jorge Rathgeb Schifferli",
    "jorge ulloa aguillon": "Jorge Ulloa Aguillón",
    "jose antonio galilea vidaurre": "José Antonio Galilea Vidaurre",
    "jose antonio kast rist": "José Antonio Kast Rist",
    "jose antonio viera-gallo quesney": "José Antonio Viera-Gallo Quesney",
    "jose garcia ruminot": "José García Ruminot",
    "jose miguel ortiz novoa": "José Miguel Ortiz Novoa",
    "jose perez arriagada": "José Pérez Arriagada",
    "juan antonio coloma alamos": "Juan Antonio Coloma Álamos",
    "juan antonio coloma correa": "Juan Antonio Coloma Correa",
    "juan bustos ramirez": "Juan Bustos Ramírez",
    "juan luis castro gonzalez": "Juan Luis Castro González",
    "laura soto gonzalez": "Laura Soto González",
    "manuel matta aragay": "Manuel Matta Aragay",
    "manuel rojas molina": "Manuel Rojas Molina",
    "marcela sabat fernandez": "Marcela Sabat Fernández",
    "marcelo schilling rodriguez": "Marcelo Schilling Rodríguez",
    "marco antonio nunez lozano": "Marco Antonio Núñez Lozano",
    "maria angelica cristi marfil": "María Angélica Cristi Marfil",
    "maria antonieta saa diaz": "María Antonieta Saa Díaz",
    "mario venegas cardenas": "Mario Venegas Cárdenas",
    "nicolas monckeberg diaz": "Nicolás Monckeberg Díaz",
    "nino baltolu rasera": "Nino Baltolú Rasera",
    "pablo prieto lorca": "Pablo Prieto Lorca",
    "patricio melero abaroa": "Patricio Melero Abaroa",
    "patricio vallespin lopez": "Patricio Vallespín López",
    "patricio walker prieto": "Patricio Walker Prieto",
    "paulina nunez urrutia": "Paulina Núñez Urrutia",
    "pedro araya guerrero": "Pedro Araya Guerrero",
    "pedro munoz aburto": "Pedro Muñoz Aburto",
    "pedro pablo alvarez-salamanca buchi": "Pedro Pablo Álvarez-Salamanca Buchi",
    "pedro pablo alvarez-salamanca ramirez": "Pedro Pablo Álvarez-Salamanca Ramírez",
    "ramon elizalde hevia": "Ramón Elizalde Hevia",
    "ramon farias ponce": "Ramón Farías Ponce",
    "raul saldivar auger": "Raúl Saldívar Auger",
    "raul urrutia avila": "Raúl Urrutia Avila",
    "rene alinco bustos": "René Alinco Bustos",
    "rene manuel garcia garcia": "René Manuel García García",
    "renzo trisotti martinez": "Renzo Trisotti Martínez",
    "ricardo rincon gonzalez": "Ricardo Rincón González",
    "roberto leon ramirez": "Roberto León Ramírez",
    "rodrigo gonzalez torres": "Rodrigo González Torres",
    "rosauro martinez labbe": "Rosauro Martínez Labbé",
    "sergio aguilo melo": "Sergio Aguiló Melo",
    "sergio correa de la cerda": "Sergio Correa De La Cerda",
    "victor manuel rebolledo gonzalez": "Victor Manuel Rebolledo González",
    "victor perez varela": "Víctor Pérez Varela",
    "waldo mora longa": "Waldo Mora Longa",
    "ximena vidal lazaro": "Ximena Vidal Lázaro"
}

def remove_accents(input_str):
    if not input_str: return input_str
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def normalize_diputado_name(name):
    if not name: return name
    cleaned = sanitize_name(name)
    base = remove_accents(cleaned).lower()
    if base in OFFICIAL_NAMES:
        return OFFICIAL_NAMES[base]
    return cleaned

def clean_region(region):
    if not region: return region
    clean = region.strip()
    clean = re.sub(r'\s*\(.*?\)\s*', '', clean)
    return clean

def clean_partido(partido):
    if not partido: return partido
    clean = partido.strip()
    if clean == "Partido Por La Democracia":
        return "Partido Por la Democracia"
    if clean == "Partido Regionalista Independiente (PRI)":
        return "Partido Regionalista Independiente"
    return clean

def clean_coalicion(coalicion):
    if not coalicion: return coalicion
    clean = coalicion.strip()
    if clean == "Alianza por Chile":
        return "Alianza"
    return clean

def clean_bancada(bancada):
    if not bancada: return bancada
    clean = bancada.strip()
    clean = " ".join(clean.split())
    clean = clean.replace("Cominista", "Comunista")
    return clean

def clean_etapa(etapa):
    if not etapa: return etapa
    clean = etapa.strip()
    clean = clean.replace("Primer", "1er").replace("Segundo", "2do").replace("Tercer", "3er")
    return clean

def categorize_tematica(comision):
    if not comision:
        return "Otras" 
    
    c = comision.strip()
    
    mapping = {
        "Constitución, Legislación y Justicia": "Constitución y Justicia",
        "Constitución, Legislación, Justicia y Reglamento": "Constitución y Justicia",
        
        "Economía, Fomento y Desarrollo": "Economía y Hacienda",
        "Economía, Fomento; Micro, Pequeña y Mediana Empresa, Protección de los Consumidores y Turismo.": "Economía y Hacienda",
        "Hacienda": "Economía y Hacienda",
        
        "Familia": "Familia y Social",
        "Familia y Adulto Mayor": "Familia y Social",
        "Superación de la Pobreza, Planificación y Desarrollo Social": "Familia y Social",
        "Trabajo y Seguridad Social": "Familia y Social",
        
        "Educación": "Educación, Cultura y Deporte",
        "Educación, Cultura, Deportes y Recreación": "Educación, Cultura y Deporte",
        "Educación, Deportes y Recreación": "Educación, Cultura y Deporte",
        "Cultura y las Artes": "Educación, Cultura y Deporte",
        "Cultura, Artes y Comunicaciones": "Educación, Cultura y Deporte",
        "Especial de la Cultura y las Artes": "Educación, Cultura y Deporte",
        "Deportes y Recreación": "Educación, Cultura y Deporte",
        "Especial de Deportes": "Educación, Cultura y Deporte",
        
        "Salud": "Salud",
        
        "Vivienda y Desarrollo Urbano": "Vivienda e Infraestructura",
        "Obras Públicas, Transportes y Telecomunicaciones": "Vivienda e Infraestructura",
        
        "Derechos Humanos y Pueblos Originarios": "DD.HH. y Nacionalidad",
        "Derechos Humanos, Nacionalidad y Ciudadanía": "DD.HH. y Nacionalidad",
        
        "Defensa Nacional": "Seguridad y Defensa",
        "Seguridad Ciudadana": "Seguridad y Defensa",
        "Seguridad Ciudadana y Drogas": "Seguridad y Defensa",
        "Especial de Seguridada Ciudadana y Drogas": "Seguridad y Defensa",
        
        "Medio Ambiente y Recursos Naturales": "Medio Ambiente y Recursos",
        "Recursos Naturales, Bienes Nacionales y Medio Ambiente": "Medio Ambiente y Recursos",
        "Agricultura, Silvicultura y Desarrollo Rural": "Medio Ambiente y Recursos",
        "Minería y Energía": "Medio Ambiente y Recursos",
        
        "Gobierno Interior y Regionalización": "Gobierno Interior",
        "Gobierno Interior, Nacionalidad Ciudadanía y Regionalización": "Gobierno Interior",
        "Gobierno Interior, Regionalización, Planificación y Desarrollo Social": "Gobierno Interior"
    }
    
    return mapping.get(c, "Otras")

def process():
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = False
    cursor = conn.cursor()
    
    try:
        print("Agregando columnas a dim_diputados...")
        cursor.execute("ALTER TABLE dim_diputados ADD COLUMN IF NOT EXISTS diputado_normalizado TEXT")
        cursor.execute("ALTER TABLE dim_diputados ADD COLUMN IF NOT EXISTS partido_politico_normalizado TEXT")
        cursor.execute("ALTER TABLE dim_diputados ADD COLUMN IF NOT EXISTS region_normalizada TEXT")
        cursor.execute("ALTER TABLE dim_diputados ADD COLUMN IF NOT EXISTS coalicion_normalizada TEXT")
        cursor.execute("ALTER TABLE dim_diputados ADD COLUMN IF NOT EXISTS bancada_comite_normalizado TEXT")
        
        cursor.execute("SELECT diputado, partido_politico, region, coalicion, bancada_comite FROM dim_diputados")
        rows = cursor.fetchall()
        for r in rows:
            orig_diputado = r[0]
            dip_n = normalize_diputado_name(orig_diputado)
            part_n = clean_partido(r[1])
            reg_n = clean_region(r[2])
            coal_n = clean_coalicion(r[3])
            banc_n = clean_bancada(r[4])
            
            cursor.execute("""
                UPDATE dim_diputados 
                SET diputado_normalizado = %s, 
                    partido_politico_normalizado = %s,
                    region_normalizada = %s,
                    coalicion_normalizada = %s,
                    bancada_comite_normalizado = %s
                WHERE diputado = %s
            """, (dip_n, part_n, reg_n, coal_n, banc_n, orig_diputado))
            
        print("Columnas en dim_diputados procesadas.")
        
        print("Agregando columnas a coautores...")
        cursor.execute("ALTER TABLE coautores ADD COLUMN IF NOT EXISTS diputado_normalizado TEXT")
        cursor.execute("SELECT DISTINCT diputado FROM coautores")
        coauth_rows = cursor.fetchall()
        for r in coauth_rows:
            orig = r[0]
            norm = normalize_diputado_name(orig)
            cursor.execute("UPDATE coautores SET diputado_normalizado = %s WHERE diputado = %s", (norm, orig))
            
        print("Columnas en coautores procesadas.")
        
        print("Agregando columnas a mociones...")
        cursor.execute("ALTER TABLE mociones ADD COLUMN IF NOT EXISTS etapa_normalizada TEXT")
        cursor.execute("ALTER TABLE mociones ADD COLUMN IF NOT EXISTS tematica_normalizada TEXT")
        cursor.execute("ALTER TABLE mociones ADD COLUMN IF NOT EXISTS tematica_asociada TEXT")
        
        cursor.execute("SELECT n_boletin, etapa, tematica, comision_inicial FROM mociones")
        mociones_rows = cursor.fetchall()
        for r in mociones_rows:
            bol = r[0]
            etapa_n = clean_etapa(r[1])
            tem_n = r[2].strip() if r[2] else None
            tem_asoc = categorize_tematica(r[3])
            
            cursor.execute("""
                UPDATE mociones 
                SET etapa_normalizada = %s,
                    tematica_normalizada = %s,
                    tematica_asociada = %s
                WHERE n_boletin = %s
            """, (etapa_n, tem_n, tem_asoc, bol))
            
        print("Columnas en mociones procesadas.")
        conn.commit()
    except Exception as e:
        print("Error en transaccion:", e)
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    process()
