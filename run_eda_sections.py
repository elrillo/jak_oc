import psycopg2
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def run_eda_sections():
    conn = psycopg2.connect(DB_URL)
    
    with open('eda_sections_results.txt', 'w', encoding='utf-8') as out:
        out.write("====== EDA POR SECCIONES ======\n\n")

        # 1. GENERAL
        out.write("--- 1. GENERAL ---\n")
        q_gen = "SELECT COUNT(*) as total FROM mociones"
        df_gen = pd.read_sql(q_gen, conn)
        out.write(f"Total Proyectos: {df_gen['total'][0]}\n\n")

        # 2. PERIODOS (Legislaturas)
        out.write("--- 2. PERIODOS ---\n")
        q_per = """
        SELECT legislatura, COUNT(n_boletin) as cantidad_proyectos
        FROM mociones
        GROUP BY legislatura
        ORDER BY legislatura;
        """
        df_per = pd.read_sql(q_per, conn)
        out.write(df_per.to_string() + "\n\n")

        # 3. DESTACADOS
        out.write("--- 3. DESTACADOS ---\n")
        # Ya tenemos la velocidad, busquemos el proyecto con más coautores
        q_dest = """
        SELECT m.n_boletin, m.nombre_iniciativa, COUNT(c.diputado) as total_firmas
        FROM mociones m
        JOIN coautores c ON m.n_boletin = c.n_boletin
        GROUP BY m.n_boletin, m.nombre_iniciativa
        ORDER BY total_firmas DESC LIMIT 3;
        """
        df_dest = pd.read_sql(q_dest, conn)
        out.write("Proyectos con mayor cantidad de firmas:\n")
        out.write(df_dest.to_string() + "\n\n")

        # 4. COMISIONES
        out.write("--- 4. COMISIONES ---\n")
        q_com = """
        SELECT tematica_normalizada, comision_inicial, COUNT(n_boletin) as cantidad
        FROM mociones
        GROUP BY tematica_normalizada, comision_inicial
        ORDER BY cantidad DESC LIMIT 10;
        """
        df_com = pd.read_sql(q_com, conn)
        out.write("Top Comisiones/Temáticas:\n")
        out.write(df_com.to_string() + "\n\n")

        # 5. ALIANZAS (Distribución transversal)
        out.write("--- 5. ALIANZAS ---\n")
        q_ali = """
        SELECT d.coalicion_normalizada, COUNT(c.n_boletin) as firmas
        FROM coautores c
        JOIN dim_diputados d ON c.diputado_normalizado = d.diputado_normalizado
        WHERE c.diputado_normalizado NOT ILIKE '%Kast Rist%'
        GROUP BY d.coalicion_normalizada
        ORDER BY firmas DESC;
        """
        df_ali = pd.read_sql(q_ali, conn)
        out.write("Firmas por Coalición:\n")
        out.write(df_ali.to_string() + "\n\n")

        # 6. ESTADO
        out.write("--- 6. ESTADO ---\n")
        q_est = """
        SELECT estado_del_proyecto_de_ley, COUNT(n_boletin) as cantidad
        FROM mociones
        GROUP BY estado_del_proyecto_de_ley
        ORDER BY cantidad DESC;
        """
        df_est = pd.read_sql(q_est, conn)
        out.write("Distribución de Estados:\n")
        out.write(df_est.to_string() + "\n\n")

        # 7. LEYES
        out.write("--- 7. LEYES ---\n")
        q_leyes = """
        SELECT n_boletin, nley, tematica_normalizada, nombre_iniciativa
        FROM mociones
        WHERE estado_del_proyecto_de_ley ILIKE '%Tramitación Terminada%' OR etapa_normalizada ILIKE '%Ley%';
        """
        df_leyes = pd.read_sql(q_leyes, conn)
        out.write("Leyes Promulgadas (Temáticas):\n")
        out.write(df_leyes['tematica_normalizada'].value_counts().to_string() + "\n")
        out.write("\nDetalle Leyes:\n")
        out.write(df_leyes[['nley', 'tematica_normalizada']].to_string() + "\n\n")

    conn.close()
    print("EDA Secciones Guardado")

if __name__ == "__main__":
    run_eda_sections()
