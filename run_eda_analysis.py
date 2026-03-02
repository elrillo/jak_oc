import psycopg2
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def run_eda():
    conn = psycopg2.connect(DB_URL)
    
    with open('eda_results2.txt', 'w', encoding='utf-8') as out:
        out.write("====== EXPLORATORIO DATA ANALYSIS (EDA) PART 2 ======\n\n")

        # 2. LONGITUD Y COMPLEJIDAD (Texto original vs Éxito)
        out.write("--- 2. LONGITUD DE TEXTO ORIGINAL VS ÉXITO ---\n")
        q2 = """
        SELECT m.n_boletin, m.estado_del_proyecto_de_ley, m.etapa_normalizada, t.texto_mocion
        FROM mociones m
        JOIN textos_pdf t ON m.n_boletin = t.n_boletin
        WHERE t.texto_mocion IS NOT NULL;
        """
        df_len = pd.read_sql(q2, conn)
        df_len['char_length'] = df_len['texto_mocion'].str.len()
        
        # Categorizar éxito
        def es_exito(estado):
            estado = str(estado).lower()
            if 'ley' in estado or 'publicado' in estado: return 'Ley (Éxito)'
            if 'archivad' in estado or 'retirad' in estado or 'rechazad' in estado: return 'Archivado/Rechazado (Fracaso)'
            return 'En Tramitación/Otro'
        
        df_len['categoria_exito'] = df_len['estado_del_proyecto_de_ley'].apply(es_exito)
        promedios_len = df_len.groupby('categoria_exito')[['char_length']].mean()
        
        out.write("Promedios de Longitud de TEXTO ORIGINAL según Éxito:\n")
        out.write(promedios_len.to_string() + "\n\n")


        # 4. VELOCIDAD DE TRAMITACIÓN (Check states)
        out.write("--- 4. ESTADOS EXISTENTES ---\n")
        q_estados = "SELECT DISTINCT estado_del_proyecto_de_ley, etapa_normalizada FROM mociones;"
        df_est = pd.read_sql(q_estados, conn)
        out.write(df_est.to_string() + "\n\n")

        # Now get speed for all that have both dates
        q4 = """
        SELECT n_boletin, nombre_iniciativa, fecha_de_ingreso, publicado_en_diario_oficial, fecha_de_promulgacion, estado_del_proyecto_de_ley, etapa_normalizada
        FROM mociones
        WHERE publicado_en_diario_oficial IS NOT NULL AND publicado_en_diario_oficial != ''
           OR fecha_de_promulgacion IS NOT NULL AND fecha_de_promulgacion != '';
        """
        df_speed = pd.read_sql(q4, conn)
        
        # Convert to datetime handling possible chilean formats DD/MM/YYYY or similar
        try:
            df_speed['ingreso_dt'] = pd.to_datetime(df_speed['fecha_de_ingreso'], dayfirst=True, errors='coerce')
            
            # Use publicacion if exists, else promulgacion
            df_speed['fin_dt'] = pd.to_datetime(df_speed['publicado_en_diario_oficial'], dayfirst=True, errors='coerce')
            df_speed['fin_dt'] = df_speed['fin_dt'].fillna(pd.to_datetime(df_speed['fecha_de_promulgacion'], dayfirst=True, errors='coerce'))
            
            df_speed['dias_tramitacion'] = (df_speed['fin_dt'] - df_speed['ingreso_dt']).dt.days
            df_speed = df_speed.dropna(subset=['dias_tramitacion'])
            df_speed = df_speed.sort_values('dias_tramitacion', ascending=True)
            
            out.write("Top 5 Proyectos Convertidos en Ley Más Rápidos:\n")
            top_5 = df_speed[['n_boletin', 'dias_tramitacion', 'estado_del_proyecto_de_ley', 'nombre_iniciativa']].head(5)
            out.write(top_5.to_string() + "\n\n")
            
            out.write(f"Tiempo Promedio de proyectos exitosos: {df_speed['dias_tramitacion'].mean():.2f} días\n")
            out.write(f"Cantidad de proyectos convertidos en ley: {len(df_speed)}\n")
            
        except Exception as e:
            out.write(f"Error parseando fechas: {e}\n")

    conn.close()
    print("EDA Result 2 Saved!")

if __name__ == "__main__":
    run_eda()
