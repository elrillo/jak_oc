# Observatorio Congreso JAK

## Descripción
Dashboard interactivo de inteligencia de datos para auditar y visualizar la actividad parlamentaria del ex-diputado José Antonio Kast (255 mociones, 2002-2018, Congreso Nacional de Chile). Versión Beta 0.9.

## Stack Tecnológico

### Versión actual (Streamlit - `/app.py`)
- **Framework:** Streamlit (Python 3.11)
- **Base de Datos:** SQLite (local: `database/jak_observatorio.db`) + Supabase PostgreSQL (producción)
- **Visualización:** Plotly Express + Plotly Graph Objects
- **NLP:** Análisis heurístico basado en keywords (clasificación temática, sentimiento, resúmenes extractivos)
- **Dependencias:** streamlit, pandas, plotly, psycopg2-binary, supabase

### Versión nueva (Next.js - `/web/`)
- **Framework:** Next.js 14+ (App Router, TypeScript)
- **Styling:** Tailwind CSS (dark mode nativo)
- **UI Components:** shadcn/ui
- **Charts:** Recharts
- **Animaciones:** Framer Motion
- **Backend:** Supabase directo (@supabase/supabase-js)
- **Deploy:** Vercel

## Estructura del Proyecto
```
├── app.py                       # App Streamlit original (NO modificar)
├── requirements.txt             # Dependencias Python
├── CLAUDE.md                    # Este archivo
├── database/
│   └── jak_observatorio.db      # SQLite local (908 KB)
├── data/
│   ├── archivos_csv/            # Excel fuente (mociones + diputados)
│   ├── archivos_json/           # Documentos de DocumentCloud (37+ JSON)
│   └── archivos_pdf/            # PDFs originales de boletines
├── build_dw.py                  # ETL: Excel/PDF → SQLite
├── enrich_sqlite.py             # Normalización y carga dim_diputados
├── build_intelligence_layer.py  # Pipeline NLP (clasificación, sentimiento)
├── analyze_texts_local.py       # NLP local alternativo
├── migrate_to_supabase.py       # Sincronización SQLite → Supabase
├── analyze_alliances.py         # Análisis de red de coautorías
├── [scripts de validación]      # QA: final_qa.py, validate_data.py, etc.
│
└── web/                         # NUEVO: Frontend Next.js
    ├── src/
    │   ├── app/                 # Páginas (App Router)
    │   ├── components/          # Componentes React reutilizables
    │   └── lib/                 # Lógica de negocio, tipos, queries
    ├── .env.local               # Credenciales Supabase (NO en git)
    ├── package.json
    └── tailwind.config.ts
```

## Esquema de Base de Datos (Supabase PostgreSQL)

### mociones (tabla principal)
- `n_boletin` (PK): Identificador del boletín, formato "3064-06"
- `nombre_iniciativa`: Título completo del proyecto de ley
- `fecha_de_ingreso`: Fecha de ingreso al Congreso
- `estado_del_proyecto_de_ley`: Estado actual (En Tramitación, Ley, Archivado, etc.)
- `tipo_de_proyecto`: Tipo (Moción o Mensaje)
- `comision_inicial`: Comisión que recibió el proyecto
- `publicado_en_diario_oficial`: Fecha de publicación (si aplica)
- `etapa_del_proyecto`: Etapa procesal actual

### coautores (relación N:M)
- `n_boletin` (FK): Referencia al boletín
- `diputado`: Nombre completo del diputado coautor

### dim_diputados (tabla dimensión)
- `diputado` (PK): Nombre normalizado
- `partido` / `partido_politico`: Partido político
- `sexo`: Género
- `region`: Región electoral
- `distrito`: Distrito electoral

### textos_pdf (texto extraído)
- `n_boletin`: Referencia al boletín
- `texto_mocion`: Texto completo extraído del PDF

### analisis_ia (resultados NLP)
- `id_boletin` (PK, FK): Referencia al boletín
- `resumen_ejecutivo`: Resumen de 2 oraciones
- `tipo_iniciativa`: Clasificación (Punitiva, Propositiva, Administrativa)
- `sentimiento_score`: Score de sentimiento (-1.0 a 1.0)
- `tags_temas`: Array JSON de temas detectados

## Pipeline de Datos
1. `build_dw.py` → Extrae datos de Excel + texto de PDFs → SQLite
2. `enrich_sqlite.py` → Normaliza columnas, carga dim_diputados
3. `build_intelligence_layer.py` / `analyze_texts_local.py` → Análisis NLP → tabla analisis_ia
4. `migrate_to_supabase.py` → Sincroniza SQLite a PostgreSQL
5. `web/` (Next.js) → Consume datos directamente de Supabase

## Lógica de Negocio Clave

### Clasificación de Comisiones → Temas (10 categorías)
- Constitución y Justicia, Economía y Hacienda, Seguridad y Defensa
- Familia y Social, Educación y Cultura, Salud
- Trabajo y Previsión, Medio Ambiente y Recursos, Vivienda e Infraestructura
- DD.HH. y Nacionalidad, Gobierno Interior, Otras

### Progreso Legislativo (escala 0-4)
- 0: Archivado/Retirado
- 1: Primer Trámite
- 2: Segundo Trámite
- 3: Tercer Trámite/Mixta/Veto
- 4: Tramitación Terminada/Ley

### Periodos Legislativos
- 2002-2006, 2006-2010, 2010-2014, 2014-2018 (corte en marzo de cada año)

### Diputado Objetivo
- José Antonio Kast Rist (variantes: "Jose Antonio Kast Rist", "José Antonio Kast Rist", "Kast Rist Jose Antonio")

### Partidos Políticos (normalización)
- UDI, RN, DC, PS, PPD, PRSD, PC, Evópoli, Republicanos, IND

## Convenciones
- **Idioma:** Español (código, UI, comentarios)
- **Tema visual:** Dark mode, fuentes serif (Playfair Display para títulos, Merriweather para cuerpo)
- **Colores:** Fondo #0c0d0e, acento #c0392b (rojo), éxito #2ecc71 (verde)
- **Charts:** Template oscuro con fondos transparentes
- **Nombres de columnas en Supabase:** snake_case (n_boletin, fecha_de_ingreso, etc.)
- **Nombres en el app:** Normalizados (id_boletin, fecha_ingreso, etc.)

## Comandos de Desarrollo

### Streamlit (versión original)
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Next.js (versión nueva)
```bash
cd web
npm install
npm run dev    # http://localhost:3000
npm run build  # Build de producción
```

## Variables de Entorno (web/.env.local)
```
NEXT_PUBLIC_SUPABASE_URL=https://tbniuckpxxzphturwnaj.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon_key>
```
