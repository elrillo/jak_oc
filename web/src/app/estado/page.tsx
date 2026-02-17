"use client"

import { useState, useMemo } from "react"
import { useDashboard, DashboardGate } from "@/components/DashboardProvider"
import { KpiCard } from "@/components/KpiCard"
import { PageHeader } from "@/components/PageHeader"
import { StorySection } from "@/components/StorySection"
import { mapStageNumeric, mapStageLabel, valueCounts, formatDateHuman } from "@/lib/legislative"
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip,
} from "recharts"

const STAGE_COLORS: Record<number, string> = {
  0: "#c0392b",
  1: "#e67e22",
  2: "#f39c12",
  3: "#3498db",
  4: "#2ecc71",
}

function EstadoContent() {
  const { data } = useDashboard()
  const [selectedProject, setSelectedProject] = useState<string | null>(null)

  const stageData = useMemo(() => {
    if (!data) return { stages: [], avgDays: "N/A" as string | number }

    const withStage = data.jakMociones.map(m => ({
      ...m,
      progressVal: mapStageNumeric(m.etapa_del_proyecto, m.estado_del_proyecto_de_ley),
      stageLabel: mapStageLabel(mapStageNumeric(m.etapa_del_proyecto, m.estado_del_proyecto_de_ley)),
    }))

    const stages = valueCounts(withStage.map(m => m.stageLabel))

    // Tiempo promedio de tramitación (días entre ingreso y publicación)
    let avgDays: string | number = "N/A"
    const leyes = withStage.filter(m => m.publicado_en_diario_oficial && m.fecha_de_ingreso)
    if (leyes.length > 0) {
      const totalDays = leyes.reduce((sum, m) => {
        const pub = new Date(m.publicado_en_diario_oficial!).getTime()
        const ing = new Date(m.fecha_de_ingreso!).getTime()
        return sum + Math.round((pub - ing) / (1000 * 60 * 60 * 24))
      }, 0)
      avgDays = Math.round(totalDays / leyes.length)
    }

    return { stages, avgDays, withStage }
  }, [data])

  if (!data) return null

  const selectedMocion = selectedProject
    ? stageData.withStage?.find(m => m.n_boletin === selectedProject)
    : null

  return (
    <>
      <PageHeader
        title="Ciclo de Vida Legislativo"
        subtitle="Seguimiento del progreso de las iniciativas y tiempos de tramitación."
      />

      {/* KPI tiempo promedio */}
      <StorySection
        title="Tramitación en Tiempo Real"
        description="Uno de los mayores desafíos del proceso legislativo es la demora.\n\nEl indicador muestra el promedio de días que han tardado las mociones de JAK en ser publicadas como ley, un dato clave sobre la agilidad del sistema."
        chart={
          <KpiCard title="Tiempo Promedio (Días)" value={stageData.avgDays} subtitle="Desde ingreso a publicación" />
        }
        textLeft
      />

      {/* Etapas globales */}
      <StorySection
        title="Avance Legislativo"
        description="Este gráfico de dona muestra en qué fase se encuentran todos los proyectos. Ayuda a identificar cuántas mociones se encuentran en trámites avanzados frente a las que están en su etapa inicial."
        chart={
          <ResponsiveContainer width="100%" height={350}>
            <PieChart>
              <Pie
                data={stageData.stages}
                dataKey="count"
                nameKey="name"
                cx="50%"
                cy="50%"
                innerRadius={80}
                outerRadius={140}
                paddingAngle={2}
              >
                {stageData.stages.map((entry, i) => {
                  const stageVal = Object.entries({ 0: "Archivado / Retirado", 1: "Primer Trámite", 2: "Segundo Trámite", 3: "Tercer Trámite / Mixta", 4: "Tramitación Terminada / Ley" })
                    .find(([, label]) => label === entry.name)?.[0] || "1"
                  return <Cell key={i} fill={STAGE_COLORS[Number(stageVal)] || "#555"} />
                })}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: "#1a1a1a", border: "1px solid #333", borderRadius: 8 }} itemStyle={{ color: "#fff" }} />
            </PieChart>
          </ResponsiveContainer>
        }
        textLeft={false}
      />

      <div className="border-t border-white/5 my-8" />

      {/* Rastreador individual */}
      <h3 className="font-serif text-xl mb-4 text-center">Rastreador de Proyectos</h3>
      <p className="text-muted-foreground text-center text-sm mb-6">Selecciona un proyecto para visualizar su avance específico.</p>

      <select
        value={selectedProject || ""}
        onChange={e => setSelectedProject(e.target.value)}
        className="w-full bg-[#141414] border border-white/10 rounded-lg px-4 py-3 text-sm mb-8 focus:outline-none focus:border-white/30"
      >
        <option value="">Seleccionar proyecto...</option>
        {stageData.withStage?.map(m => (
          <option key={m.n_boletin} value={m.n_boletin}>
            {m.n_boletin} | {(m.nombre_iniciativa || "").slice(0, 80)}
          </option>
        ))}
      </select>

      {selectedMocion && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="space-y-3">
            <h4 className="font-serif text-lg">{selectedMocion.n_boletin}</h4>
            <p className="text-sm bg-[#141414] border border-white/10 rounded px-4 py-2">
              <strong>Estado:</strong> {selectedMocion.estado_del_proyecto_de_ley}
            </p>
            <p className="text-sm text-muted-foreground">Fecha Ingreso: {formatDateHuman(selectedMocion.fecha_de_ingreso)}</p>
            <p className="text-sm text-muted-foreground">Comisión: {selectedMocion.comision_inicial || "N/A"}</p>
            <p className="text-sm text-muted-foreground">Tipo: {selectedMocion.tipo_de_proyecto || "N/A"}</p>
          </div>
          <div className="flex flex-col items-center justify-center">
            <p className="text-muted-foreground text-xs uppercase tracking-wider mb-4">Progreso Estimado</p>
            {(() => {
              const val = selectedMocion.progressVal
              const pct = val === 0 ? 5 : val * 25
              return (
                <>
                  <div className="relative w-40 h-40">
                    <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                      <circle cx="50" cy="50" r="42" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="8" />
                      <circle cx="50" cy="50" r="42" fill="none" stroke={STAGE_COLORS[val] || "#555"} strokeWidth="8" strokeDasharray={`${pct * 2.64} ${264 - pct * 2.64}`} strokeLinecap="round" />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-2xl font-serif font-bold">{pct}%</span>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground mt-2">{selectedMocion.stageLabel}</p>
                </>
              )
            })()}
          </div>
        </div>
      )}
    </>
  )
}

export default function EstadoPage() {
  return (
    <DashboardGate>
      <EstadoContent />
    </DashboardGate>
  )
}
