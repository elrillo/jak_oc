/**
 * Normalización y colores de partidos políticos chilenos.
 * Portada de normalize_party() y party_map en app.py línea 711.
 */

/** Mapa de normalización: nombre largo → abreviatura */
const PARTY_MAP: Record<string, string> = {
  "Unión Demócrata Independiente": "UDI",
  "Renovación Nacional": "RN",
  "Democracia Cristiana": "DC",
  "Partido Socialista": "PS",
  "Partido Por la Democracia": "PPD",
  "Partido Radical Social Demócrata": "PRSD",
  "Partido Comunista": "PC",
  "Evolución Política": "Evópoli",
  "Partido Republicano de Chile": "Republicanos",
  "Independiente": "IND",
  "Independientes": "IND",
}

/**
 * Normaliza el nombre de un partido a su abreviatura estándar.
 * Portada de normalize_party() en app.py línea 726.
 */
export function normalizeParty(pName: string | null): string {
  if (!pName) return "Sin Partido"
  const trimmed = pName.trim()

  // Búsqueda directa
  if (PARTY_MAP[trimmed]) return PARTY_MAP[trimmed]

  // Búsqueda por substring
  const upper = trimmed.toUpperCase()
  if (upper.includes("UDI")) return "UDI"
  if (upper.includes("RENOVACION") || upper.includes("RENOVACIÓN") || upper === "RN") return "RN"
  if (upper.includes("SOCIALISTA") || upper === "PS") return "PS"
  if (upper.includes("RADICAL")) return "PRSD"
  if ((upper.includes("DEMOCRACIA") && upper.includes("CRISTIANA")) || upper === "DC") return "DC"
  if (upper.includes("COMUNISTA") || upper === "PC") return "PC"
  if (upper.includes("INDEPENDIENTE")) return "IND"
  if (upper.includes("REPUBLICANO")) return "Republicanos"

  return trimmed
}

/** Colores asociados a cada partido (paleta distintiva) */
export const PARTY_COLORS: Record<string, string> = {
  "UDI": "#1B3A8C",       // Azul oscuro
  "RN": "#2E86C1",        // Azul medio
  "DC": "#27AE60",        // Verde
  "PS": "#E74C3C",        // Rojo
  "PPD": "#F39C12",       // Amarillo/Naranja
  "PRSD": "#8E44AD",      // Púrpura
  "PC": "#C0392B",        // Rojo oscuro
  "Evópoli": "#3498DB",   // Azul claro
  "Republicanos": "#D35400", // Naranja oscuro
  "IND": "#95A5A6",       // Gris
  "Sin Partido": "#7F8C8D", // Gris oscuro
}

/**
 * Obtiene el color hex de un partido.
 * Devuelve gris si no se encuentra.
 */
export function getPartyColor(party: string): string {
  return PARTY_COLORS[party] || "#95A5A6"
}
