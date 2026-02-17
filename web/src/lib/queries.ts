import type { Mocion, Coautor, Diputado, AnalisisIA, DashboardData, ProcessedData, MocionEnriquecida } from './types'
import { TARGET_VARIANTS, SUCCESS_PATTERN, getPeriod } from './legislative'

/**
 * Normaliza los nombres de columnas de un registro de PostgreSQL.
 * Maneja las inconsistencias entre num_boletin / n_boletin / id_boletin
 * que existen por la función clean_column_name() en migrate_to_supabase.py.
 *
 * Equivalente a los mappings de app.py líneas 242-298.
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function normalizeRow(row: Record<string, any>): Record<string, any> {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const result: Record<string, any> = { ...row }

  // Normalizar variantes de boletín → n_boletin
  for (const key of ['num_boletin', 'id_boletin', 'n°_boletin', 'n_boletin']) {
    if (key in row && row[key] != null) {
      result['n_boletin'] = row[key]
      break
    }
  }

  // Normalizar partido_politico → partido (dim_diputados)
  if ('partido_politico' in row && !('partido' in row)) {
    result['partido'] = row['partido_politico']
  }

  // Normalizar fecha_ingreso → fecha_de_ingreso
  if ('fecha_ingreso' in row && !('fecha_de_ingreso' in row)) {
    result['fecha_de_ingreso'] = row['fecha_ingreso']
  }

  // Normalizar fecha de ingreso (variante sin acento de migrate_to_supabase)
  if ('fecha_de_ingreso' in row && !row['fecha_de_ingreso'] && 'fecha_ingreso' in row) {
    result['fecha_de_ingreso'] = row['fecha_ingreso']
  }

  // Normalizar tipo_iniciativa → tipo_de_proyecto
  if ('tipo_iniciativa' in row && !('tipo_de_proyecto' in row)) {
    result['tipo_de_proyecto'] = row['tipo_iniciativa']
  }

  // Normalizar tipo_de_proyecto (variante de clean_column_name)
  if ('tipo_proyecto' in row && !('tipo_de_proyecto' in row)) {
    result['tipo_de_proyecto'] = row['tipo_proyecto']
  }

  // Normalizar etapa → etapa_del_proyecto
  if ('etapa' in row && !('etapa_del_proyecto' in row)) {
    result['etapa_del_proyecto'] = row['etapa']
  }

  // Normalizar estado
  if ('estado_proyecto_ley' in row && !('estado_del_proyecto_de_ley' in row)) {
    result['estado_del_proyecto_de_ley'] = row['estado_proyecto_ley']
  }

  // Normalizar comision
  if ('comision' in row && !('comision_inicial' in row)) {
    result['comision_inicial'] = row['comision']
  }

  return result
}

/**
 * Carga todos los datos del dashboard desde la API Route (/api/data).
 * La API Route se conecta directamente a PostgreSQL, igual que la versión Python.
 * Esto evita problemas con RLS y API keys de Supabase.
 */
export async function loadDashboardData(): Promise<DashboardData> {
  console.log('[Queries] Cargando datos desde /api/data...')

  const res = await fetch('/api/data')

  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({}))
    const msg = errorBody.error || `Error HTTP ${res.status}`
    console.error('[Queries] Error de API:', msg)
    throw new Error(msg)
  }

  const raw = await res.json()

  // --- Logging diagnóstico ---
  console.log('[Queries] mociones:', raw.mociones?.length ?? 0, 'rows')
  console.log('[Queries] coautores:', raw.coautores?.length ?? 0, 'rows')
  console.log('[Queries] diputados:', raw.diputados?.length ?? 0, 'rows')
  console.log('[Queries] analisisIA:', raw.analisisIA?.length ?? 0, 'rows')

  // Log de muestra: primera fila para ver nombres de columnas reales
  if (raw.mociones?.[0]) console.log('[Queries] mociones columns:', Object.keys(raw.mociones[0]))
  if (raw.coautores?.[0]) console.log('[Queries] coautores columns:', Object.keys(raw.coautores[0]))
  if (raw.diputados?.[0]) console.log('[Queries] diputados columns:', Object.keys(raw.diputados[0]))
  if (raw.analisisIA?.[0]) console.log('[Queries] analisis_ia columns:', Object.keys(raw.analisisIA[0]))

  // Normalizar columnas de cada tabla
  const mociones = (raw.mociones || []).map(normalizeRow) as Mocion[]
  const coautores = (raw.coautores || []).map(normalizeRow) as Coautor[]
  const diputados = (raw.diputados || []).map(normalizeRow) as Diputado[]
  const analisisIA = (raw.analisisIA || []).map(normalizeRow) as AnalisisIA[]

  console.log('[Queries] Datos normalizados OK')

  return { mociones, coautores, diputados, analisisIA }
}

/**
 * Procesa los datos crudos para obtener las métricas y filtros del dashboard.
 * Equivalente a la lógica de procesamiento en app.py líneas 302-336.
 */
export function processData(data: DashboardData): ProcessedData {
  const { mociones, coautores, analisisIA } = data

  console.log('[Process] Total mociones:', mociones.length)
  console.log('[Process] Total coautores:', coautores.length)

  // Encontrar el nombre de JAK en la BD
  const allDeps = new Set(coautores.map(c => c.diputado))
  let foundName = TARGET_VARIANTS[0]
  for (const v of TARGET_VARIANTS) {
    if (allDeps.has(v)) {
      foundName = v
      break
    }
  }
  console.log('[Process] JAK found as:', foundName, '| in coautores:', allDeps.has(foundName))

  // Filtrar boletines donde JAK es coautor
  const jakBoletinIds = coautores
    .filter(c => c.diputado === foundName)
    .map(c => c.n_boletin)
  const jakBoletinSet = new Set(jakBoletinIds)

  console.log('[Process] JAK boletines:', jakBoletinIds.length)

  // Crear mapa de análisis IA por boletín
  const iaMap = new Map<string, AnalisisIA>()
  for (const ia of analisisIA) {
    // analisis_ia usa id_boletin como PK, normalizado en normalizeRow a n_boletin también
    const key = ia.id_boletin || ia.n_boletin
    if (key) iaMap.set(key, ia)
  }

  // Filtrar y enriquecer mociones de JAK
  const jakMociones: MocionEnriquecida[] = mociones
    .filter(m => jakBoletinSet.has(m.n_boletin))
    .map(m => {
      const ia = iaMap.get(m.n_boletin)
      const fecha = m.fecha_de_ingreso
      return {
        ...m,
        anio: fecha ? new Date(fecha).getFullYear() : undefined,
        periodo: getPeriod(fecha),
        resumen_ejecutivo: ia?.resumen_ejecutivo || null,
        tipo_iniciativa_ia: ia?.tipo_iniciativa || null,
        sentimiento_score: ia?.sentimiento_score || null,
        tags_temas: ia?.tags_temas || null,
      }
    })

  console.log('[Process] JAK mociones filtradas:', jakMociones.length)

  // Métricas generales
  const total = jakMociones.length
  const leyesCount = jakMociones.filter(m => SUCCESS_PATTERN.test(m.estado_del_proyecto_de_ley || '')).length
  const tasaExito = total > 0 ? (leyesCount / total) * 100 : 0
  const uniqueYears = new Set(jakMociones.map(m => m.anio).filter(Boolean)).size
  const promedioAnual = uniqueYears > 0 ? Math.round((total / uniqueYears) * 10) / 10 : 0

  // Top aliado
  const coauthorCounts: Record<string, number> = {}
  for (const c of coautores) {
    if (jakBoletinSet.has(c.n_boletin) && c.diputado !== foundName) {
      coauthorCounts[c.diputado] = (coauthorCounts[c.diputado] || 0) + 1
    }
  }
  const topAlly = Object.entries(coauthorCounts)
    .sort((a, b) => b[1] - a[1])[0]?.[0] || "N/A"

  return {
    jakMociones,
    jakBoletinIds,
    foundName,
    total,
    leyesCount,
    tasaExito,
    promedioAnual,
    topAlly,
  }
}

/**
 * Obtiene los coautores para una lista de boletines, excluyendo a JAK.
 */
export function getCoauthorsForBoletines(
  coautores: Coautor[],
  boletinIds: string[],
  foundName: string
): Coautor[] {
  const idSet = new Set(boletinIds)
  return coautores.filter(c => idSet.has(c.n_boletin) && c.diputado !== foundName)
}
