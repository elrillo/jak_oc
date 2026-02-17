"use client"

import { useState, useMemo } from "react"
import { useDashboard, DashboardGate } from "@/components/DashboardProvider"
import { PageHeader } from "@/components/PageHeader"
import { formatDateHuman } from "@/lib/legislative"

function ExploradorContent() {
  const { data } = useDashboard()
  const [search, setSearch] = useState("")
  const [filterState, setFilterState] = useState("Todos")
  const [dateFrom, setDateFrom] = useState("")
  const [dateTo, setDateTo] = useState("")

  const allStates = useMemo(() => {
    if (!data) return []
    const states = new Set(data.jakMociones.map(m => m.estado_del_proyecto_de_ley).filter(Boolean))
    return Array.from(states).sort()
  }, [data])

  const filtered = useMemo(() => {
    if (!data) return []
    let results = [...data.jakMociones]

    if (search) {
      const q = search.toLowerCase()
      results = results.filter(m =>
        (m.nombre_iniciativa || "").toLowerCase().includes(q) ||
        (m.n_boletin || "").toLowerCase().includes(q) ||
        (m.resumen_ejecutivo || "").toLowerCase().includes(q)
      )
    }

    if (filterState !== "Todos") {
      results = results.filter(m => m.estado_del_proyecto_de_ley === filterState)
    }

    if (dateFrom) {
      results = results.filter(m => m.fecha_de_ingreso && m.fecha_de_ingreso >= dateFrom)
    }
    if (dateTo) {
      results = results.filter(m => m.fecha_de_ingreso && m.fecha_de_ingreso <= dateTo)
    }

    return results.sort((a, b) => (b.fecha_de_ingreso || "").localeCompare(a.fecha_de_ingreso || ""))
  }, [data, search, filterState, dateFrom, dateTo])

  if (!data) return null

  return (
    <>
      <PageHeader
        title="Buscador Avanzado"
        subtitle="Filtra y busca entre todas las mociones parlamentarias."
      />

      {/* Filtros */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div>
          <label className="text-xs text-muted-foreground uppercase tracking-wider mb-1 block">Buscar</label>
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Ej: Araucanía, impuestos, seguridad..."
            className="w-full bg-[#141414] border border-white/10 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-white/30 placeholder:text-white/20"
          />
        </div>
        <div>
          <label className="text-xs text-muted-foreground uppercase tracking-wider mb-1 block">Estado</label>
          <select
            value={filterState}
            onChange={e => setFilterState(e.target.value)}
            className="w-full bg-[#141414] border border-white/10 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-white/30"
          >
            <option value="Todos">Todos</option>
            {allStates.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="text-xs text-muted-foreground uppercase tracking-wider mb-1 block">Desde</label>
            <input
              type="date"
              value={dateFrom}
              onChange={e => setDateFrom(e.target.value)}
              className="w-full bg-[#141414] border border-white/10 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-white/30"
            />
          </div>
          <div>
            <label className="text-xs text-muted-foreground uppercase tracking-wider mb-1 block">Hasta</label>
            <input
              type="date"
              value={dateTo}
              onChange={e => setDateTo(e.target.value)}
              className="w-full bg-[#141414] border border-white/10 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-white/30"
            />
          </div>
        </div>
      </div>

      {/* Resultados */}
      <p className="text-muted-foreground text-sm mb-4">Mostrando {filtered.length} proyectos.</p>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-white/10 text-left text-muted-foreground uppercase text-xs tracking-wider">
              <th className="py-3 px-2">Boletín</th>
              <th className="py-3 px-2">Nombre Iniciativa</th>
              <th className="py-3 px-2">Fecha Ingreso</th>
              <th className="py-3 px-2">Estado</th>
              <th className="py-3 px-2">Tipo</th>
            </tr>
          </thead>
          <tbody>
            {filtered.slice(0, 100).map(m => (
              <tr key={m.n_boletin} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                <td className="py-2.5 px-2 text-[#c0392b] font-mono text-xs whitespace-nowrap">{m.n_boletin}</td>
                <td className="py-2.5 px-2">{m.nombre_iniciativa}</td>
                <td className="py-2.5 px-2 text-muted-foreground text-xs whitespace-nowrap">{formatDateHuman(m.fecha_de_ingreso)}</td>
                <td className="py-2.5 px-2 text-muted-foreground text-xs">{m.estado_del_proyecto_de_ley}</td>
                <td className="py-2.5 px-2 text-muted-foreground text-xs">{m.tipo_de_proyecto || "N/A"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {filtered.length > 100 && (
        <p className="text-muted-foreground text-xs text-center mt-4">
          Mostrando los primeros 100 resultados de {filtered.length}.
        </p>
      )}
    </>
  )
}

export default function ExploradorPage() {
  return (
    <DashboardGate>
      <ExploradorContent />
    </DashboardGate>
  )
}
