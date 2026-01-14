
# Manual Técnico - Observatorio Congreso JAK

Este documento describe la estructura de datos y el flujo de información del proyecto "Observatorio Congreso: Análisis JAK".

## 1. Arquitectura de Datos
El proyecto utiliza una base de datos **SQLite** local (`database/jak_observatorio.db`) para almacenar toda la información legislativa. Esta base de datos alimenta la aplicación web construida en **Streamlit**.

## 2. Descripción de Tablas

### `mociones`
Contiene la metadata administrativa de los proyectos de ley.
- **id_boletin** (PK): Identificador único del proyecto (ej. 2897-07).
- **nombre_iniciativa**: Título oficial del proyecto.
- **fecha_ingreso**: Fecha de presentación.
- **estado_del_proyecto_de_ley**: Estado actual (ej. Publicado, En tramitación, Archivado).
- **tipo_iniciativa**: Moción o Mensaje (aunque filtramos por Moción).
- **legislatura**: Periodo legislativo.

### `coautores`
Tabla de relación N:M que vincula diputados con proyectos.
- **id_boletin**: FK hacia `mociones`.
- **diputado**: Nombre del diputado coautor.
- **Participa**: Flag (siempre 1 en esta vista filtrada de autores).

### `dim_diputados`
Tabla de dimensión con información biográfica y política de los parlamentarios.
- **diputado** (PK): Nombre completo normalizado.
- **partido**: Partido político al momento del periodo.
- **sexo**: Género.
- **region**, **distrito**: Zona de representación.

### `textos_pdf`
Almacena el contenido crudo extraído de los documentos PDF de las mociones.
- **N° Boletín**: Identificador del proyecto.
- **texto_mocion**: Texto completo extraído mediante OCR/Librerías PDF.

### `analisis_ia`
Capa de inteligencia generada mediante procesamiento de lenguaje natural (NLP).
- **id_boletin** (PK): FK hacia `mociones`.
- **resumen_ejecutivo**: Resumen generado de 2 oraciones (NLP extractivo).
- **tags_temas**: Lista de etiquetas temáticas detectadas (ej. Seguridad, Familia).
- **tipo_iniciativa**: Clasificación (Punitiva, Propositiva, Administrativa).
- **sentimiento_score**: Puntaje de tono (-1 a 1).
- **alcance_territorial**: Clasificación (Nacional vs Distrital).

## 3. Flujo de Actualización

1. **Extracción**: Scripts (`build_dw.py`) leen Excels y PDFs de la carpeta `data/`.
2. **Carga**: `enrich_sqlite.py` normaliza y carga datos base a SQLite.
3. **Análisis Muestra/IA**: `analyze_texts_local.py` procesa los textos en `textos_pdf` y popula `analisis_ia`.
4. **Visualización**: `app.py` lee de SQLite y muestra el dashboard.

## 4. Mantenimiento
Para recalcular métricas o actualizar análisis de textos después de añadir nuevos PDFs:
```bash
python analyze_texts_local.py
```
Para reiniciar la base de datos desde cero (si se actualizan los Excel):
```bash
python enrich_sqlite.py
python analyze_texts_local.py
```
