/** Proyecto de ley / moción parlamentaria */
export interface Mocion {
  n_boletin: string
  nombre_iniciativa: string
  fecha_de_ingreso: string | null
  estado_del_proyecto_de_ley: string
  tipo_de_proyecto: string | null
  comision_inicial: string | null
  publicado_en_diario_oficial: string | null
  etapa_del_proyecto: string | null
  // Campos calculados en el frontend
  anio?: number
  periodo?: string
}

/** Relación diputado-boletín (coautorías) */
export interface Coautor {
  n_boletin: string
  diputado: string
}

/** Tabla dimensión de diputados */
export interface Diputado {
  diputado: string
  partido: string | null
  partido_politico?: string | null
  sexo: string | null
  region: string | null
  distrito: string | null
}

/** Resultados del análisis NLP */
export interface AnalisisIA {
  id_boletin: string
  /** Campo normalizado - puede venir de id_boletin o num_boletin */
  n_boletin?: string
  resumen_ejecutivo: string | null
  tipo_iniciativa: string | null
  sentimiento_score: number | null
  tags_temas: string | string[] | null
}

/** Moción enriquecida con análisis IA (merge de mociones + analisis_ia) */
export interface MocionEnriquecida extends Mocion {
  resumen_ejecutivo?: string | null
  tipo_iniciativa_ia?: string | null
  sentimiento_score?: number | null
  tags_temas?: string | string[] | null
}

/** Datos del dashboard cargados desde Supabase */
export interface DashboardData {
  mociones: Mocion[]
  coautores: Coautor[]
  diputados: Diputado[]
  analisisIA: AnalisisIA[]
}

/** Datos procesados para las visualizaciones del dashboard */
export interface ProcessedData {
  /** Mociones filtradas solo para JAK */
  jakMociones: MocionEnriquecida[]
  /** IDs de boletines de JAK */
  jakBoletinIds: string[]
  /** Nombre encontrado de JAK en la BD */
  foundName: string
  /** Total de mociones */
  total: number
  /** Mociones aprobadas como ley */
  leyesCount: number
  /** Tasa de éxito (%) */
  tasaExito: number
  /** Promedio anual */
  promedioAnual: number
  /** Aliado top */
  topAlly: string
}
