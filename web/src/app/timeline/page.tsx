"use client"

import { useState, useMemo } from "react"
import { useDashboard, DashboardGate } from "@/components/DashboardProvider"
import { PageHeader } from "@/components/PageHeader"
import { PERIODOS, SUCCESS_PATTERN, formatDateHuman } from "@/lib/legislative"
import type { MocionEnriquecida } from "@/lib/types"
import { motion, AnimatePresence } from "framer-motion"

const TEMA_COLORS: Record<string, string> = {
  "Constitución y Justicia": "#c0392b",
  "Economía y Hacienda": "#f39c12",
  "Seguridad y Defensa Nacional": "#2c3e50",
  "Vivienda e Infraestructura": "#d35400",
  "Educación, Ciencia, Cultura y Deporte": "#3498db",
  "Salud": "#2ecc71",
  "Desarrollo Social y Familia": "#9b59b6",
  "Gobierno Interior": "#95a5a6",
  "Medio Ambiente y Recursos Naturales": "#1abc9c",
  "Ciudadanía y DD.HH.": "#e74c3c",
  "Otras": "#7f8c8d",
}

function getColor(tema: string | null): string {
  if (!tema) return "#7f8c8d"
  for (const [key, color] of Object.entries(TEMA_COLORS)) {
    if (tema.includes(key) || key.includes(tema)) return color
  }
  return TEMA_COLORS[tema] || "#7f8c8d"
}

function TimelineContent() {
  const { data } = useDashboard()
  const [selectedPeriod, setSelectedPeriod] = useState<string>("Todos")
  const [selectedMocion, setSelectedMocion] = useState<MocionEnriquecida | null>(null)
  const [filterTema, setFilterTema] = useState<string>("Todos")

  const sortedMociones = useMemo(() => {
    if (!data) return []
    let filtered = [...data.jakMociones]
      .filter(m => m.fecha_de_ingreso)
      .sort((a, b) => (a.fecha_de_ingreso || "").localeCompare(b.fecha_de_ingreso || ""))

    if (selectedPeriod !== "Todos") {
      filtered = filtered.filter(m => m.periodo === selectedPeriod)
    }
    if (filterTema !== "Todos") {
      filtered = filtered.filter(m => (m.tematica_asociada || "Otras") === filterTema)
    }
    return filtered
  }, [data, selectedPeriod, filterTema])

  const temas = useMemo(() => {
    if (!data) return []
    const set = new Set(data.jakMociones.map(m => m.tematica_asociada || "Otras"))
    return Array.from(set).sort()
  }, [data])

  // Agrupar por año para el timeline
  const yearGroups = useMemo(() => {
    const groups: Record<number, MocionEnriquecida[]> = {}
    for (const m of sortedMociones) {
      const year = m.anio || new Date(m.fecha_de_ingreso!).getFullYear()
      if (!groups[year]) groups[year] = []
      groups[year].push(m)
    }
    return Object.entries(groups)
      .map(([year, mociones]) => ({ year: Number(year), mociones }))
      .sort((a, b) => a.year - b.year)
  }, [sortedMociones])

  if (!data) return null

  const isLey = (m: MocionEnriquecida) => SUCCESS_PATTERN.test(m.estado_del_proyecto_de_ley)

  return (
    <>
      <PageHeader
        title="Timeline Legislativo"
        subtitle={`Recorrido cronológico por las ${data.total} mociones parlamentarias.`}
      />

      {/* Filtros */}
      <div className="mb-8 space-y-4">
        {/* Periodos */}
        <div className="flex flex-wrap justify-center gap-2">
          <button
            onClick={() => setSelectedPeriod("Todos")}
            className={`px-3 sm:px-4 py-1.5 rounded-full text-[10px] sm:text-xs uppercase tracking-wider transition-all
              ${selectedPeriod === "Todos" ? "bg-white text-black" : "bg-white/5 text-white/50 hover:bg-white/10 border border-white/10"}`}
          >
            Todos ({data.total})
          </button>
          {PERIODOS.map(p => {
            const count = data.jakMociones.filter(m => m.periodo === p).length
            return (
              <button
                key={p}
                onClick={() => setSelectedPeriod(p)}
                className={`px-3 sm:px-4 py-1.5 rounded-full text-[10px] sm:text-xs uppercase tracking-wider transition-all
                  ${selectedPeriod === p ? "bg-white text-black" : "bg-white/5 text-white/50 hover:bg-white/10 border border-white/10"}`}
              >
                {p} ({count})
              </button>
            )
          })}
        </div>

        {/* Filtro por tema */}
        <div className="flex justify-center">
          <select
            value={filterTema}
            onChange={e => setFilterTema(e.target.value)}
            className="bg-[#141414] border border-white/10 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-white/30 max-w-xs w-full"
          >
            <option value="Todos">Todas las temáticas</option>
            {temas.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
      </div>

      <p className="text-center text-muted-foreground text-sm mb-8">
        Mostrando {sortedMociones.length} mociones
      </p>

      {/* Timeline vertical (mobile-first) */}
      <div className="relative max-w-3xl mx-auto">
        {/* Línea central */}
        <div className="absolute left-4 sm:left-1/2 top-0 bottom-0 w-px bg-white/10 sm:-translate-x-px" />

        {yearGroups.map(({ year, mociones }, gi) => (
          <div key={year} className="mb-8">
            {/* Year marker */}
            <div className="relative flex items-center mb-4">
              <div className="absolute left-4 sm:left-1/2 w-3 h-3 rounded-full bg-[#c0392b] border-2 border-[#0c0d0e] -translate-x-1/2 z-10" />
              <div className="ml-10 sm:ml-0 sm:text-center sm:w-full">
                <span className="bg-[#c0392b]/20 text-[#c0392b] px-3 py-1 rounded-full text-sm font-mono font-bold">
                  {year}
                </span>
                <span className="text-muted-foreground text-xs ml-2">
                  ({mociones.length} {mociones.length === 1 ? "moción" : "mociones"})
                </span>
              </div>
            </div>

            {/* Events */}
            {mociones.map((m, i) => {
              const esLey = isLey(m)
              const isSelected = selectedMocion?.n_boletin === m.n_boletin
              return (
                <div
                  key={m.n_boletin}
                  className={`relative flex mb-3 ${gi % 2 === 0 || true ? "sm:flex-row" : "sm:flex-row-reverse"}`}
                >
                  {/* Dot on line */}
                  <div className="absolute left-4 sm:left-1/2 w-2 h-2 rounded-full -translate-x-1/2 mt-3 z-10"
                    style={{ backgroundColor: esLey ? "#2ecc71" : getColor(m.tematica_asociada) }}
                  />

                  {/* Card */}
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.3, delay: i * 0.02 }}
                    onClick={() => setSelectedMocion(isSelected ? null : m)}
                    className={`ml-10 sm:ml-0 ${i % 2 === 0 ? "sm:mr-[52%] sm:pr-6" : "sm:ml-[52%] sm:pl-6"} w-full cursor-pointer`}
                  >
                    <div className={`p-3 sm:p-4 rounded-lg border transition-all duration-200
                      ${isSelected
                        ? "bg-white/[0.06] border-white/20"
                        : "bg-white/[0.02] border-white/5 hover:bg-white/[0.04] hover:border-white/10"
                      }
                      ${esLey ? "ring-1 ring-[#2ecc71]/30" : ""}`}
                    >
                      <div className="flex items-start justify-between gap-2 mb-1">
                        <span className="text-[#c0392b] font-mono text-[10px] sm:text-xs shrink-0">{m.n_boletin}</span>
                        <span className="text-muted-foreground text-[10px]">{formatDateHuman(m.fecha_de_ingreso)}</span>
                      </div>
                      <p className="text-xs sm:text-sm leading-relaxed line-clamp-2">
                        {m.nombre_iniciativa}
                      </p>

                      {/* Tags */}
                      <div className="flex flex-wrap gap-1 mt-2">
                        {esLey && (
                          <span className="text-[9px] px-1.5 py-0.5 rounded bg-[#2ecc71]/20 text-[#2ecc71]">
                            Ley
                          </span>
                        )}
                        <span
                          className="text-[9px] px-1.5 py-0.5 rounded"
                          style={{
                            backgroundColor: getColor(m.tematica_asociada) + "20",
                            color: getColor(m.tematica_asociada),
                          }}
                        >
                          {m.tematica_asociada || "Otras"}
                        </span>
                      </div>

                      {/* Expanded detail */}
                      <AnimatePresence>
                        {isSelected && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: "auto", opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="overflow-hidden"
                          >
                            <div className="mt-3 pt-3 border-t border-white/5 space-y-2">
                              <div className="flex justify-between text-[10px]">
                                <span className="text-muted-foreground">Estado</span>
                                <span>{m.estado_del_proyecto_de_ley}</span>
                              </div>
                              <div className="flex justify-between text-[10px]">
                                <span className="text-muted-foreground">Comisión</span>
                                <span className="text-right max-w-[60%]">{m.comision_inicial || "N/A"}</span>
                              </div>
                              {m.resumen_ejecutivo && (
                                <p className="text-[10px] text-muted-foreground italic mt-2 leading-relaxed">
                                  {m.resumen_ejecutivo}
                                </p>
                              )}
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  </motion.div>
                </div>
              )
            })}
          </div>
        ))}
      </div>
    </>
  )
}

export default function TimelinePage() {
  return (
    <DashboardGate>
      <TimelineContent />
    </DashboardGate>
  )
}
