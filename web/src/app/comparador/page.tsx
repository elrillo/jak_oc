"use client"

import { useState, useMemo } from "react"
import { useDashboard, DashboardGate } from "@/components/DashboardProvider"
import { PageHeader } from "@/components/PageHeader"
import { KpiCard } from "@/components/KpiCard"
import { DeputyRadar } from "@/components/charts/DeputyRadar"
import { normalizeParty, getPartyColor } from "@/lib/parties"
import { valueCounts, SUCCESS_PATTERN, PERIODOS, getPeriod } from "@/lib/legislative"

function ComparadorContent() {
  const { data, coautores, diputados } = useDashboard()
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedDeputy, setSelectedDeputy] = useState<string | null>(null)
  const [showDropdown, setShowDropdown] = useState(false)

  // Build list of coauthors with counts
  const coauthorList = useMemo(() => {
    if (!data) return []

    const jakBoletinSet = new Set(data.jakBoletinIds)
    const foundName = data.foundName
    const counts: Record<string, number> = {}

    for (const c of coautores) {
      if (jakBoletinSet.has(c.n_boletin) && c.diputado !== foundName) {
        counts[c.diputado] = (counts[c.diputado] || 0) + 1
      }
    }

    const dipMap = new Map(diputados.map(d => [d.diputado, d]))

    return Object.entries(counts)
      .map(([name, count]) => {
        const dip = dipMap.get(name)
        return {
          name,
          count,
          party: normalizeParty(dip?.partido || dip?.partido_politico || null),
        }
      })
      .sort((a, b) => b.count - a.count)
  }, [data, coautores, diputados])

  // Filtered search results
  const filteredDeputies = useMemo(() => {
    if (!searchQuery.trim()) return coauthorList.slice(0, 15)
    const q = searchQuery.toLowerCase()
    return coauthorList.filter(d => d.name.toLowerCase().includes(q)).slice(0, 15)
  }, [coauthorList, searchQuery])

  // Comparison data
  const comparison = useMemo(() => {
    if (!data || !selectedDeputy) return null

    const jakBoletinSet = new Set(data.jakBoletinIds)
    const foundName = data.foundName

    // Shared boletines
    const sharedBoletines = coautores
      .filter(c => c.diputado === selectedDeputy && jakBoletinSet.has(c.n_boletin))
      .map(c => c.n_boletin)

    const sharedMociones = data.jakMociones.filter(m => sharedBoletines.includes(m.n_boletin))
    const sharedCount = sharedBoletines.length

    // Deputy info
    const dipMap = new Map(diputados.map(d => [d.diputado, d]))
    const depInfo = dipMap.get(selectedDeputy)
    const party = normalizeParty(depInfo?.partido || depInfo?.partido_politico || null)

    // Success rate comparison
    const kastLeyes = data.leyesCount
    const kastTotal = data.total
    const sharedLeyes = sharedMociones.filter(m => SUCCESS_PATTERN.test(m.estado_del_proyecto_de_ley)).length

    // Thematic distribution - JAK
    const jakThemes = valueCounts(data.jakMociones.map(m => m.tematica_asociada || "Otras"))
    const jakRadar = jakThemes.map(t => ({
      category: t.name,
      value: Math.round((t.count / kastTotal) * 100),
    }))

    // Thematic distribution - shared
    const sharedThemes = valueCounts(sharedMociones.map(m => m.tematica_asociada || "Otras"))
    const allCategories = jakRadar.map(r => r.category)
    const sharedRadar = allCategories.map(cat => {
      const found = sharedThemes.find(t => t.name === cat)
      return {
        category: cat,
        value: found ? Math.round((found.count / sharedCount) * 100) : 0,
      }
    })

    // Period distribution
    const sharedByPeriod = valueCounts(sharedMociones.map(m => getPeriod(m.fecha_de_ingreso)))
    const periodData = PERIODOS.map(p => ({
      period: p,
      jakCount: data.jakMociones.filter(m => getPeriod(m.fecha_de_ingreso) === p).length,
      sharedCount: sharedByPeriod.find(s => s.name === p)?.count || 0,
    }))

    // Top shared themes
    const topSharedThemes = sharedThemes.slice(0, 3)

    return {
      deputyName: selectedDeputy,
      party,
      partyColor: getPartyColor(party),
      sharedCount,
      sharedLeyes,
      sharedSuccessRate: sharedCount > 0 ? (sharedLeyes / sharedCount) * 100 : 0,
      kastTotal,
      kastLeyes,
      kastSuccessRate: data.tasaExito,
      jakRadar,
      sharedRadar,
      periodData,
      topSharedThemes,
      sharedMociones,
    }
  }, [data, selectedDeputy, coautores, diputados])

  if (!data) return null

  const shortName = (name: string) => name.split(" ").slice(0, 2).join(" ")

  return (
    <>
      <PageHeader
        title="Comparador de Diputados"
        subtitle="Compara la participación de otros diputados en las mociones de Kast."
      />

      {/* Nota explicativa */}
      <div className="bg-white/[0.02] border border-white/10 rounded-xl p-4 mb-8 max-w-2xl mx-auto">
        <p className="text-xs text-muted-foreground text-center leading-relaxed">
          Este comparador analiza únicamente la participación de otros diputados
          como coautores en las {data.total} mociones de José Antonio Kast.
          No refleja la actividad legislativa independiente de cada diputado.
        </p>
      </div>

      {/* Deputy Selector */}
      <div className="max-w-md mx-auto mb-10 relative">
        <label className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1.5 block">
          Seleccionar diputado para comparar
        </label>
        <input
          type="text"
          value={searchQuery}
          onChange={e => {
            setSearchQuery(e.target.value)
            setShowDropdown(true)
          }}
          onFocus={() => setShowDropdown(true)}
          placeholder="Buscar diputado..."
          className="w-full bg-[#141414] border border-white/10 rounded-lg px-4 py-2.5 text-sm
            focus:outline-none focus:border-white/30 placeholder:text-white/30"
        />
        {showDropdown && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-[#1a1a1a] border border-white/10
            rounded-lg max-h-64 overflow-y-auto z-50 shadow-xl">
            {filteredDeputies.map(dep => (
              <button
                key={dep.name}
                onClick={() => {
                  setSelectedDeputy(dep.name)
                  setSearchQuery(shortName(dep.name))
                  setShowDropdown(false)
                }}
                className="w-full text-left px-4 py-2.5 hover:bg-white/5 flex items-center justify-between
                  border-b border-white/5 last:border-0 transition-colors"
              >
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: getPartyColor(dep.party) }} />
                  <span className="text-sm">{shortName(dep.name)}</span>
                  <span className="text-[10px] text-muted-foreground">{dep.party}</span>
                </div>
                <span className="text-xs text-muted-foreground">{dep.count} coautorías</span>
              </button>
            ))}
            {filteredDeputies.length === 0 && (
              <p className="px-4 py-3 text-sm text-muted-foreground">Sin resultados</p>
            )}
          </div>
        )}
      </div>

      {/* Comparison Results */}
      {comparison && (
        <div className="space-y-8">
          {/* Header del diputado seleccionado */}
          <div className="text-center">
            <h3 className="font-serif text-xl font-semibold">
              {shortName(comparison.deputyName)}
            </h3>
            <div className="flex items-center justify-center gap-2 mt-1">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: comparison.partyColor }} />
              <span className="text-sm text-muted-foreground">{comparison.party}</span>
            </div>
          </div>

          {/* KPIs de comparación */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <KpiCard
              title="Coautorías"
              value={comparison.sharedCount}
              subtitle={`de ${comparison.kastTotal} mociones`}
            />
            <KpiCard
              title="Tasa Éxito Compartidas"
              value={`${comparison.sharedSuccessRate.toFixed(1)}%`}
              subtitle={`${comparison.sharedLeyes} leyes`}
            />
            <KpiCard
              title="Tasa Éxito Kast (total)"
              value={`${comparison.kastSuccessRate.toFixed(1)}%`}
              subtitle={`${comparison.kastLeyes} leyes`}
            />
            <KpiCard
              title="Tema Principal"
              value={
                comparison.topSharedThemes.length > 0
                  ? comparison.topSharedThemes[0].name.length > 18
                    ? comparison.topSharedThemes[0].name.slice(0, 18) + "..."
                    : comparison.topSharedThemes[0].name
                  : "N/A"
              }
              subtitle={
                comparison.topSharedThemes.length > 0
                  ? `${comparison.topSharedThemes[0].count} proyectos`
                  : ""
              }
            />
          </div>

          <div className="border-t border-white/5 my-6" />

          {/* Radar comparison */}
          <div>
            <h4 className="font-serif text-lg text-center mb-4">Perfil Temático Comparado</h4>
            <p className="text-center text-xs text-muted-foreground mb-6 max-w-lg mx-auto">
              Distribución porcentual de las mociones por área temática.
              <span className="text-[#c0392b]"> Rojo: todas las mociones de Kast</span> ·
              <span style={{ color: comparison.partyColor }}> Color: mociones compartidas con {shortName(comparison.deputyName)}</span>
            </p>
            <DeputyRadar
              data={comparison.jakRadar}
              dataB={comparison.sharedRadar}
              labelA="Kast (total)"
              labelB={shortName(comparison.deputyName)}
              colorB={comparison.partyColor}
            />
          </div>

          <div className="border-t border-white/5 my-6" />

          {/* Period comparison */}
          <div>
            <h4 className="font-serif text-lg text-center mb-4">Distribución por Periodo</h4>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 max-w-2xl mx-auto">
              {comparison.periodData.map(p => (
                <div key={p.period} className="bg-white/[0.02] border border-white/5 rounded-lg p-3 text-center">
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider">{p.period}</p>
                  <p className="text-xl font-serif font-bold mt-1">{p.sharedCount}</p>
                  <p className="text-[10px] text-muted-foreground">de {p.jakCount} mociones</p>
                  <div className="mt-2 bg-white/5 rounded-full h-1.5 overflow-hidden">
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${p.jakCount > 0 ? (p.sharedCount / p.jakCount) * 100 : 0}%`,
                        backgroundColor: comparison.partyColor,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="border-t border-white/5 my-6" />

          {/* Shared motions list */}
          <div>
            <h4 className="font-serif text-lg mb-4">
              Mociones Compartidas ({comparison.sharedCount})
            </h4>

            {/* Mobile: cards */}
            <div className="md:hidden space-y-3">
              {comparison.sharedMociones
                .sort((a, b) => (b.fecha_de_ingreso || "").localeCompare(a.fecha_de_ingreso || ""))
                .slice(0, 20)
                .map(m => (
                  <div key={m.n_boletin} className="bg-white/[0.02] border border-white/5 rounded-lg p-4 space-y-2">
                    <div className="flex justify-between items-start">
                      <span className="text-[#c0392b] font-mono text-xs">{m.n_boletin}</span>
                      <span className="text-muted-foreground text-[10px]">{m.tematica_asociada || "Otras"}</span>
                    </div>
                    <p className="text-sm">{m.nombre_iniciativa?.slice(0, 120)}{(m.nombre_iniciativa?.length || 0) > 120 ? "..." : ""}</p>
                    <div className="flex justify-between text-[10px] text-muted-foreground">
                      <span>{m.estado_del_proyecto_de_ley}</span>
                      <span>{m.fecha_de_ingreso?.split("T")[0]}</span>
                    </div>
                  </div>
                ))}
            </div>

            {/* Desktop: table */}
            <div className="hidden md:block overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/10 text-left text-muted-foreground uppercase text-xs tracking-wider">
                    <th className="py-3 px-2">Boletín</th>
                    <th className="py-3 px-2">Nombre</th>
                    <th className="py-3 px-2">Estado</th>
                    <th className="py-3 px-2">Tema</th>
                    <th className="py-3 px-2">Fecha</th>
                  </tr>
                </thead>
                <tbody>
                  {comparison.sharedMociones
                    .sort((a, b) => (b.fecha_de_ingreso || "").localeCompare(a.fecha_de_ingreso || ""))
                    .slice(0, 30)
                    .map(m => (
                      <tr key={m.n_boletin} className="border-b border-white/5 hover:bg-white/5">
                        <td className="py-2 px-2 text-[#c0392b] font-mono text-xs">{m.n_boletin}</td>
                        <td className="py-2 px-2">{m.nombre_iniciativa?.slice(0, 70)}{(m.nombre_iniciativa?.length || 0) > 70 ? "..." : ""}</td>
                        <td className="py-2 px-2 text-muted-foreground text-xs">{m.estado_del_proyecto_de_ley}</td>
                        <td className="py-2 px-2 text-muted-foreground text-xs">{m.tematica_asociada || "Otras"}</td>
                        <td className="py-2 px-2 text-muted-foreground text-xs whitespace-nowrap">{m.fecha_de_ingreso?.split("T")[0]}</td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Empty state */}
      {!comparison && (
        <div className="bg-white/[0.02] border border-white/5 rounded-xl p-12 text-center max-w-md mx-auto">
          <p className="text-muted-foreground text-sm">
            Selecciona un diputado del buscador para ver la comparación detallada de su colaboración legislativa con Kast.
          </p>
        </div>
      )}
    </>
  )
}

export default function ComparadorPage() {
  return (
    <DashboardGate>
      <ComparadorContent />
    </DashboardGate>
  )
}
