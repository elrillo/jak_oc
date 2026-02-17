/**
 * Lógica legislativa portada de app.py (Python/Streamlit)
 * Contiene las funciones de clasificación, progreso y periodos.
 */

/** Nombre objetivo del diputado y variantes */
export const TARGET_DEPUTY = "Jose Antonio Kast Rist"
export const TARGET_VARIANTS = [
  "Jose Antonio Kast Rist",
  "José Antonio Kast Rist",
  "Kast Rist Jose Antonio",
]

/** Patrón regex para detectar mociones aprobadas como ley */
export const SUCCESS_PATTERN = /ley|publicado|tramitación terminada/i

/**
 * Clasifica una comisión en una de las 12 categorías temáticas.
 * Portada de categorize_commission() en app.py línea 392.
 */
export function categorizeCommission(cName: string | null): string {
  if (!cName) return "Otras"
  const n = cName.toLowerCase()

  if (n.includes("constituc") || n.includes("legislaci") || n.includes("justicia"))
    return "Constitución y Justicia"
  if (n.includes("econom") || n.includes("hacienda") || n.includes("presupuesto"))
    return "Economía y Hacienda"
  if (n.includes("seguridad") || n.includes("defensa") || n.includes("inteligencia"))
    return "Seguridad y Defensa"
  if (n.includes("familia") || n.includes("mujer") || n.includes("adulto mayor") || n.includes("desarrollo"))
    return "Familia y Social"
  if (n.includes("educaci") || n.includes("cultura") || n.includes("deportes"))
    return "Educación y Cultura"
  if (n.includes("salud"))
    return "Salud"
  if (n.includes("trabajo") || n.includes("previsión"))
    return "Trabajo y Previsión"
  if (n.includes("ambiente") || n.includes("recursos") || n.includes("pesca") || n.includes("agricultura") || n.includes("minería"))
    return "Medio Ambiente y Recursos"
  if (n.includes("vivienda") || n.includes("obras") || n.includes("transporte") || n.includes("telecomunicaciones"))
    return "Vivienda e Infraestructura"
  if (n.includes("derechos humanos") || n.includes("nacionalidad"))
    return "DD.HH. y Nacionalidad"
  if (n.includes("gobierno") || n.includes("interior") || n.includes("regional"))
    return "Gobierno Interior"

  return "Otras"
}

/**
 * Convierte el estado/etapa a un valor numérico de progreso (0-4).
 * Portada de map_stage_numeric() en app.py línea 407.
 */
export function mapStageNumeric(etapaTxt: string | null, estadoTxt: string | null): number {
  const txt = (etapaTxt || "").toLowerCase()
  const est = (estadoTxt || "").toLowerCase()

  if (est.includes("publicado") || est.includes("ley") || est.includes("tramitación terminada"))
    return 4
  if (est.includes("archivado") || est.includes("retirado"))
    return 0
  if (txt.includes("tercer") || txt.includes("mixta") || txt.includes("veto"))
    return 3
  if (txt.includes("segundo") || txt.includes("revisora"))
    return 2

  return 1
}

/**
 * Devuelve la etiqueta legible del progreso legislativo.
 * Portada de map_stage_label() en app.py línea 416.
 */
export function mapStageLabel(val: number): string {
  switch (val) {
    case 4: return "Tramitación Terminada / Ley"
    case 3: return "Tercer Trámite / Mixta"
    case 2: return "Segundo Trámite"
    case 1: return "Primer Trámite"
    case 0: return "Archivado / Retirado"
    default: return "Desconocido"
  }
}

/**
 * Determina el periodo legislativo a partir de una fecha.
 * Portada de get_period() en app.py línea 261.
 * Los periodos legislativos en Chile inician en marzo.
 */
export function getPeriod(dateStr: string | null): string {
  if (!dateStr) return "Desconocido"

  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return "Desconocido"

  const year = date.getFullYear()
  const month = date.getMonth() + 1 // JS months are 0-indexed

  if ((year >= 2002 && year < 2006) || (year === 2006 && month < 3)) return "2002 - 2006"
  if ((year >= 2006 && year < 2010) || (year === 2010 && month < 3)) return "2006 - 2010"
  if ((year >= 2010 && year < 2014) || (year === 2014 && month < 3)) return "2010 - 2014"
  if ((year >= 2014 && year < 2018) || (year === 2018 && month < 3)) return "2014 - 2018"
  if ((year >= 2018 && year < 2022) || (year === 2022 && month < 3)) return "2018 - 2022"

  return "Otros"
}

/** Lista ordenada de periodos legislativos */
export const PERIODOS = [
  "2002 - 2006",
  "2006 - 2010",
  "2010 - 2014",
  "2014 - 2018",
]

/**
 * Formatea una fecha ISO a formato DD/MM/YYYY legible.
 * Portada de format_date_human() en app.py línea 378.
 */
export function formatDateHuman(val: string | null): string {
  if (!val) return "N/A"
  const date = new Date(val)
  if (isNaN(date.getTime())) return "N/A"

  const day = String(date.getDate()).padStart(2, "0")
  const month = String(date.getMonth() + 1).padStart(2, "0")
  const year = date.getFullYear()
  return `${day}/${month}/${year}`
}

/**
 * Cuenta las frecuencias de valores en un array de strings.
 * Equivalente a pandas value_counts().
 */
export function valueCounts(arr: string[]): { name: string; count: number }[] {
  const counts: Record<string, number> = {}
  for (const item of arr) {
    counts[item] = (counts[item] || 0) + 1
  }
  return Object.entries(counts)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
}
