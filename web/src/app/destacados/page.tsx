"use client"

import { useMemo } from "react"
import { useDashboard, DashboardGate } from "@/components/DashboardProvider"
import { PageHeader } from "@/components/PageHeader"
import {
  formatDateHuman,
  mapStageNumeric,
  mapStageLabel,
  categorizeCommission,
  SUCCESS_PATTERN,
} from "@/lib/legislative"
import { getCoauthorsForBoletines } from "@/lib/queries"
import { normalizeParty, getPartyColor } from "@/lib/parties"
import { motion } from "framer-motion"
import type { MocionEnriquecida, Coautor, Diputado } from "@/lib/types"

/**
 * IDs de las 5 mociones destacadas.
 * Criterio de selección: mezcla de proyectos que se convirtieron en ley
 * y proyectos emblemáticos de alto impacto público.
 * Se pueden editar para cambiar la selección.
 */
const FEATURED_IDS = [
  "3515-07", // Ley de responsabilidad penal adolescente
  "3992-07", // Establece sistema de responsabilidad penal
  "4724-07", // Delitos sexuales contra menores
  "4843-03", // Pena de muerte
  "3876-07", // Violencia intrafamiliar
]

/** Colores de acento por tipo de iniciativa IA */
function getTypeColor(tipo: string | null): string {
  if (!tipo) return "#95A5A6"
  const t = tipo.toLowerCase()
  if (t.includes("punitiva")) return "#c0392b"
  if (t.includes("propositiva")) return "#2ecc71"
  if (t.includes("administrativa")) return "#3498db"
  return "#95A5A6"
}

/** Icono SVG del tipo de iniciativa */
function TypeIcon({ tipo }: { tipo: string | null }) {
  const color = getTypeColor(tipo)
  const t = (tipo || "").toLowerCase()

  if (t.includes("punitiva")) {
    return (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
      </svg>
    )
  }
  if (t.includes("propositiva")) {
    return (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M9 18l6-6-6-6" />
      </svg>
    )
  }
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="8" x2="12" y2="16" />
      <line x1="8" y1="12" x2="16" y2="12" />
    </svg>
  )
}

/** Parsea tags_temas que puede venir como string JSON o array */
function parseTags(tags: string | string[] | null | undefined): string[] {
  if (!tags) return []
  if (Array.isArray(tags)) return tags
  try {
    const parsed = JSON.parse(tags)
    return Array.isArray(parsed) ? parsed : [String(parsed)]
  } catch {
    return tags.split(",").map(t => t.trim()).filter(Boolean)
  }
}

/** Componente de gauge circular compacto */
function MiniGauge({ value, max = 4 }: { value: number; max?: number }) {
  const pct = value === 0 ? 5 : (value / max) * 100
  const color = value >= 4 ? "#2ecc71" : value === 0 ? "#c0392b" : "#3498db"
  const circumference = 2 * Math.PI * 28
  const dashLength = (pct / 100) * circumference

  return (
    <div className="relative w-20 h-20 flex-shrink-0">
      <svg viewBox="0 0 64 64" className="w-full h-full -rotate-90">
        <circle cx="32" cy="32" r="28" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="5" />
        <circle
          cx="32" cy="32" r="28"
          fill="none"
          stroke={color}
          strokeWidth="5"
          strokeDasharray={`${dashLength} ${circumference - dashLength}`}
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-sm font-serif font-bold">{Math.round(pct)}%</span>
      </div>
    </div>
  )
}

/** Tarjeta de una moción destacada */
function FeaturedCard({
  mocion,
  coauthors,
  dipMap,
  index,
}: {
  mocion: MocionEnriquecida
  coauthors: Coautor[]
  dipMap: Map<string, string | null>
  index: number
}) {
  const progressVal = mapStageNumeric(mocion.etapa_del_proyecto, mocion.estado_del_proyecto_de_ley)
  const tema = categorizeCommission(mocion.comision_inicial)
  const tags = parseTags(mocion.tags_temas)
  const isLey = SUCCESS_PATTERN.test(mocion.estado_del_proyecto_de_ley || "")

  return (
    <motion.article
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.12 }}
      className="relative bg-[#141414] border border-white/10 rounded-xl overflow-hidden hover:border-white/20 transition-all duration-300 group"
    >
      {/* Barra superior de acento */}
      <div
        className="h-1 w-full"
        style={{ background: isLey ? "#2ecc71" : getTypeColor(mocion.tipo_iniciativa_ia || null) }}
      />

      <div className="p-6 lg:p-8">
        {/* Header: número + estado */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <span className="text-xs font-mono text-white/40 bg-white/5 px-2.5 py-1 rounded">
              Boletín {mocion.n_boletin}
            </span>
            {isLey && (
              <span className="text-xs font-semibold text-[#2ecc71] bg-[#2ecc71]/10 px-2.5 py-1 rounded-full flex items-center gap-1">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                Ley
              </span>
            )}
          </div>
          <MiniGauge value={progressVal} />
        </div>

        {/* Título */}
        <h3 className="font-serif text-lg lg:text-xl leading-snug mb-3 group-hover:text-white/95 transition-colors">
          {mocion.nombre_iniciativa}
        </h3>

        {/* Resumen ejecutivo */}
        <p className="text-white/50 text-sm leading-relaxed mb-5 line-clamp-3">
          {mocion.resumen_ejecutivo || "Resumen ejecutivo no disponible para esta moción."}
        </p>

        {/* Metadatos en grid compacto */}
        <div className="grid grid-cols-2 gap-x-6 gap-y-3 mb-5 text-sm">
          <div>
            <span className="text-white/30 text-xs uppercase tracking-wider block mb-0.5">Fecha Ingreso</span>
            <span className="text-white/70">{formatDateHuman(mocion.fecha_de_ingreso)}</span>
          </div>
          <div>
            <span className="text-white/30 text-xs uppercase tracking-wider block mb-0.5">Temática</span>
            <span className="text-white/70">{tema}</span>
          </div>
          <div>
            <span className="text-white/30 text-xs uppercase tracking-wider block mb-0.5">Estado</span>
            <span className="text-white/70">{mocion.estado_del_proyecto_de_ley}</span>
          </div>
          <div>
            <span className="text-white/30 text-xs uppercase tracking-wider block mb-0.5">Progreso</span>
            <span className="text-white/70">{mapStageLabel(progressVal)}</span>
          </div>
          {mocion.tipo_iniciativa_ia && (
            <div>
              <span className="text-white/30 text-xs uppercase tracking-wider block mb-0.5">Tipo IA</span>
              <span className="flex items-center gap-1.5 text-white/70">
                <TypeIcon tipo={mocion.tipo_iniciativa_ia} />
                {mocion.tipo_iniciativa_ia}
              </span>
            </div>
          )}
          {mocion.publicado_en_diario_oficial && (
            <div>
              <span className="text-white/30 text-xs uppercase tracking-wider block mb-0.5">Publicado</span>
              <span className="text-[#2ecc71]">{formatDateHuman(mocion.publicado_en_diario_oficial)}</span>
            </div>
          )}
        </div>

        {/* Coautores */}
        <div className="mb-5">
          <span className="text-white/30 text-xs uppercase tracking-wider block mb-2">
            Coautores ({coauthors.length})
          </span>
          <div className="flex flex-wrap gap-1.5">
            {coauthors.length > 0 ? (
              coauthors.map(c => {
                const party = normalizeParty(dipMap.get(c.diputado) || null)
                const color = getPartyColor(party)
                return (
                  <span
                    key={c.diputado}
                    className="text-xs px-2.5 py-1 rounded-full border transition-colors hover:bg-white/5"
                    style={{ borderColor: `${color}60`, color }}
                  >
                    {c.diputado.split(" ").slice(0, 2).join(" ")}
                    <span className="opacity-60 ml-1">({party})</span>
                  </span>
                )
              })
            ) : (
              <span className="text-white/30 text-xs">Sin coautores registrados</span>
            )}
          </div>
        </div>

        {/* Tags temáticos */}
        {tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {tags.map((tag, i) => (
              <span
                key={i}
                className="text-[11px] px-2 py-0.5 rounded bg-white/5 text-white/40 border border-white/5"
              >
                #{tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </motion.article>
  )
}

function DestacadosContent() {
  const { data, coautores, diputados } = useDashboard()

  // Mapa de diputados para resolver partidos
  const dipMap = useMemo(() => {
    return new Map(diputados.map(d => [d.diputado, d.partido || d.partido_politico || null]))
  }, [diputados])

  // Resolver las 5 mociones destacadas
  const featured = useMemo(() => {
    if (!data) return []

    // Buscar por los IDs predefinidos
    const byId = FEATURED_IDS
      .map(id => data.jakMociones.find(m => m.n_boletin === id))
      .filter((m): m is MocionEnriquecida => m !== undefined)

    // Si no encontramos todas (ej. por datos faltantes), rellenar con las más relevantes
    if (byId.length < 5) {
      const usedIds = new Set(byId.map(m => m.n_boletin))
      const extras = data.jakMociones
        .filter(m => !usedIds.has(m.n_boletin))
        .sort((a, b) => {
          // Priorizar: leyes > con resumen > por fecha más reciente
          const aLey = SUCCESS_PATTERN.test(a.estado_del_proyecto_de_ley) ? 10 : 0
          const bLey = SUCCESS_PATTERN.test(b.estado_del_proyecto_de_ley) ? 10 : 0
          const aRes = a.resumen_ejecutivo ? 5 : 0
          const bRes = b.resumen_ejecutivo ? 5 : 0
          const aDate = a.fecha_de_ingreso ? new Date(a.fecha_de_ingreso).getTime() : 0
          const bDate = b.fecha_de_ingreso ? new Date(b.fecha_de_ingreso).getTime() : 0
          return (bLey + bRes) - (aLey + aRes) || bDate - aDate
        })
        .slice(0, 5 - byId.length)
      return [...byId, ...extras]
    }

    return byId
  }, [data])

  if (!data) return null

  // Estadísticas de las destacadas
  const leyesCount = featured.filter(m => SUCCESS_PATTERN.test(m.estado_del_proyecto_de_ley || "")).length
  const avgProgress = featured.length > 0
    ? featured.reduce((sum, m) => sum + mapStageNumeric(m.etapa_del_proyecto, m.estado_del_proyecto_de_ley), 0) / featured.length
    : 0

  return (
    <>
      <PageHeader
        title="Mociones Destacadas"
        subtitle="Cinco proyectos de ley emblemáticos seleccionados por su relevancia legislativa e impacto público."
      />

      {/* KPIs de las destacadas */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10"
      >
        <div className="bg-[#141414] border border-white/10 rounded-lg p-4 text-center">
          <p className="text-white/30 text-xs uppercase tracking-wider mb-1">Selección</p>
          <p className="font-serif text-2xl font-bold">{featured.length}</p>
          <p className="text-white/40 text-xs">mociones</p>
        </div>
        <div className="bg-[#141414] border border-white/10 rounded-lg p-4 text-center">
          <p className="text-white/30 text-xs uppercase tracking-wider mb-1">Convertidas en Ley</p>
          <p className="font-serif text-2xl font-bold text-[#2ecc71]">{leyesCount}</p>
          <p className="text-white/40 text-xs">de {featured.length}</p>
        </div>
        <div className="bg-[#141414] border border-white/10 rounded-lg p-4 text-center">
          <p className="text-white/30 text-xs uppercase tracking-wider mb-1">Progreso Promedio</p>
          <p className="font-serif text-2xl font-bold">{Math.round((avgProgress / 4) * 100)}%</p>
          <p className="text-white/40 text-xs">escala 0-4</p>
        </div>
        <div className="bg-[#141414] border border-white/10 rounded-lg p-4 text-center">
          <p className="text-white/30 text-xs uppercase tracking-wider mb-1">Temáticas</p>
          <p className="font-serif text-2xl font-bold">
            {new Set(featured.map(m => categorizeCommission(m.comision_inicial))).size}
          </p>
          <p className="text-white/40 text-xs">áreas distintas</p>
        </div>
      </motion.div>

      {/* Tarjetas de mociones destacadas */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {featured.map((mocion, i) => {
          const mocionCoauthors = getCoauthorsForBoletines(coautores, [mocion.n_boletin], data.foundName)
          return (
            <FeaturedCard
              key={mocion.n_boletin}
              mocion={mocion}
              coauthors={mocionCoauthors}
              dipMap={dipMap}
              index={i}
            />
          )
        })}
      </div>

      {/* Nota al pie */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="text-center text-white/25 text-xs mt-10 italic"
      >
        Selección editorial. Las mociones pueden ser modificadas por el equipo de investigación.
      </motion.p>
    </>
  )
}

export default function DestacadosPage() {
  return (
    <DashboardGate>
      <DestacadosContent />
    </DashboardGate>
  )
}
