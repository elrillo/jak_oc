"use client"

import { useState, useMemo } from "react"
import { useDashboard, DashboardGate } from "@/components/DashboardProvider"
import { KpiCard } from "@/components/KpiCard"
import { PageHeader } from "@/components/PageHeader"
import { StorySection } from "@/components/StorySection"
import { categorizeCommission, valueCounts, SUCCESS_PATTERN } from "@/lib/legislative"
import { Treemap, ResponsiveContainer, Tooltip } from "recharts"

const COLORS = ["#c0392b", "#2ecc71", "#3498db", "#f39c12", "#9b59b6", "#1abc9c", "#e67e22", "#95a5a6", "#e74c3c", "#16a085", "#2980b9", "#d35400"]

function ComisionesContent() {
  const { data } = useDashboard()
  const [selectedTema, setSelectedTema] = useState<string | null>(null)

  const themeCounts = useMemo(() => {
    if (!data) return []
    return valueCounts(data.jakMociones.map(m => categorizeCommission(m.comision_inicial)))
  }, [data])

  const treemapData = useMemo(() =>
    themeCounts.map((t, i) => ({ name: t.name, size: t.count, fill: COLORS[i % COLORS.length] })),
    [themeCounts]
  )

  if (!data) return null

  const activeTema = selectedTema || themeCounts[0]?.name || null
  const filtered = activeTema
    ? data.jakMociones.filter(m => categorizeCommission(m.comision_inicial) === activeTema)
    : []
  const tTotal = filtered.length
  const tLeyes = filtered.filter(m => SUCCESS_PATTERN.test(m.estado_del_proyecto_de_ley)).length
  const topSubCom = tTotal > 0
    ? valueCounts(filtered.map(m => m.comision_inicial || "Desconocida"))[0]?.name || "N/A"
    : "N/A"

  return (
    <>
      <PageHeader
        title="Trabajo en Comisiones"
        subtitle="Análisis de la especialización temática basada en las comisiones de origen."
      />

      {/* Treemap */}
      <StorySection
        title="Mapa de Especialización"
        description="A través de las comisiones, podemos ver dónde se concentra el esfuerzo legislativo.\n\nEste Mapa de Calor agrupa las comisiones específicas en temáticas generales para facilitar la comprensión de las prioridades del diputado."
        chart={
          <ResponsiveContainer width="100%" height={350}>
            <Treemap data={treemapData} dataKey="size" nameKey="name" stroke="rgba(255,255,255,0.1)">
              <Tooltip contentStyle={{ backgroundColor: "#1a1a1a", border: "1px solid #333", borderRadius: 8 }} itemStyle={{ color: "#fff" }} />
            </Treemap>
          </ResponsiveContainer>
        }
        textLeft
      />

      <div className="border-t border-white/5 my-8" />

      {/* Selector de temática */}
      <h3 className="font-serif text-xl mb-4 text-center">Explorar por Temática</h3>
      <div className="flex justify-center gap-2 mb-10 flex-wrap">
        {themeCounts.map(t => (
          <button
            key={t.name}
            onClick={() => setSelectedTema(t.name)}
            className={`px-4 py-1.5 rounded-full text-xs uppercase tracking-wider transition-all
              ${activeTema === t.name
                ? "bg-white text-black"
                : "bg-white/5 text-white/50 hover:bg-white/10 hover:text-white border border-white/10"
              }`}
          >
            {t.name} ({t.count})
          </button>
        ))}
      </div>

      {activeTema && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <KpiCard title="Proyectos en Temática" value={tTotal} subtitle={activeTema} />
            <KpiCard title="Exitosos / Leyes" value={tLeyes} subtitle={`${tTotal > 0 ? (tLeyes / tTotal * 100).toFixed(1) : 0}% efectividad`} />
            <KpiCard title="Comisión Principal" value={topSubCom.length > 25 ? topSubCom.slice(0, 25) + "..." : topSubCom} subtitle="Mayor frecuencia" />
          </div>

          <h4 className="font-serif text-lg mb-4">Proyectos de {activeTema}</h4>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10 text-left text-muted-foreground uppercase text-xs tracking-wider">
                  <th className="py-3 px-2">Boletín</th>
                  <th className="py-3 px-2">Nombre</th>
                  <th className="py-3 px-2">Estado</th>
                  <th className="py-3 px-2">Comisión</th>
                </tr>
              </thead>
              <tbody>
                {filtered.sort((a, b) => (b.fecha_de_ingreso || "").localeCompare(a.fecha_de_ingreso || "")).map(m => (
                  <tr key={m.n_boletin} className="border-b border-white/5 hover:bg-white/5">
                    <td className="py-2 px-2 text-[#c0392b] font-mono text-xs">{m.n_boletin}</td>
                    <td className="py-2 px-2">{m.nombre_iniciativa?.slice(0, 70)}{(m.nombre_iniciativa?.length || 0) > 70 ? "..." : ""}</td>
                    <td className="py-2 px-2 text-muted-foreground text-xs">{m.estado_del_proyecto_de_ley}</td>
                    <td className="py-2 px-2 text-muted-foreground text-xs">{m.comision_inicial}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </>
  )
}

export default function ComisionesPage() {
  return (
    <DashboardGate>
      <ComisionesContent />
    </DashboardGate>
  )
}
