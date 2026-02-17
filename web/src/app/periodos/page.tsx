"use client"

import { useState } from "react"
import { useDashboard, DashboardGate } from "@/components/DashboardProvider"
import { KpiCard } from "@/components/KpiCard"
import { PageHeader } from "@/components/PageHeader"
import { StorySection } from "@/components/StorySection"
import { PERIODOS, SUCCESS_PATTERN, categorizeCommission, valueCounts } from "@/lib/legislative"
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Treemap,
} from "recharts"

const COLORS = ["#c0392b", "#2ecc71", "#3498db", "#f39c12", "#9b59b6", "#1abc9c", "#e67e22", "#95a5a6"]

function PeriodosContent() {
  const { data } = useDashboard()
  const [selected, setSelected] = useState(PERIODOS[0])

  if (!data) return null

  const filtered = data.jakMociones.filter(m => m.periodo === selected)
  const pTotal = filtered.length
  const pLeyes = filtered.filter(m => SUCCESS_PATTERN.test(m.estado_del_proyecto_de_ley)).length
  const pTasa = pTotal > 0 ? (pLeyes / pTotal) * 100 : 0

  const statusCounts = valueCounts(
    filtered.map(m => m.estado_del_proyecto_de_ley).filter(Boolean)
  )

  const themeCounts = valueCounts(
    filtered.map(m => categorizeCommission(m.comision_inicial))
  )
  const treemapData = themeCounts.map((t, i) => ({
    name: t.name,
    size: t.count,
    fill: COLORS[i % COLORS.length],
  }))

  const yearCounts = valueCounts(
    filtered.map(m => String(m.anio || "")).filter(s => s !== "")
  ).sort((a, b) => Number(a.name) - Number(b.name))

  return (
    <>
      <PageHeader
        title="Análisis por Periodo Legislativo"
        subtitle="Explora el desempeño y foco temático en cada uno de los mandatos parlamentarios."
      />

      {/* Selector de periodo */}
      <div className="flex justify-center gap-2 mb-10 flex-wrap">
        {PERIODOS.map(p => (
          <button
            key={p}
            onClick={() => setSelected(p)}
            className={`px-5 py-2 rounded-full text-sm font-serif uppercase tracking-wider transition-all
              ${selected === p
                ? "bg-white text-black"
                : "bg-white/5 text-white/50 hover:bg-white/10 hover:text-white border border-white/10"
              }`}
          >
            {p}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-4 mb-10">
        <KpiCard title="Iniciativas" value={pTotal} subtitle={selected} />
        <KpiCard title="Convertidas en Ley" value={pLeyes} subtitle={`Tasa: ${pTasa.toFixed(1)}%`} />
      </div>

      <div className="border-t border-white/5 my-8" />

      <StorySection
        title={`Desempeño en ${selected}`}
        description={`Durante este mandato, se presentaron ${pTotal} iniciativas.\n\nLa tasa de éxito de este periodo fue de un ${pTasa.toFixed(1)}%.`}
        chart={
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={statusCounts} dataKey="count" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={120} paddingAngle={2}>
                {statusCounts.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: "#1a1a1a", border: "1px solid #333", borderRadius: 8 }} itemStyle={{ color: "#fff" }} />
            </PieChart>
          </ResponsiveContainer>
        }
        textLeft
      />

      <StorySection
        title="Áreas de Interés"
        description={`En el periodo ${selected}, la mayoría de los proyectos se concentraron en las categorías visualizadas. Esto revela las prioridades políticas y legislativas de este tiempo específico.`}
        chart={
          <ResponsiveContainer width="100%" height={300}>
            <Treemap data={treemapData} dataKey="size" nameKey="name" stroke="rgba(255,255,255,0.1)">
              <Tooltip contentStyle={{ backgroundColor: "#1a1a1a", border: "1px solid #333", borderRadius: 8 }} itemStyle={{ color: "#fff" }} />
            </Treemap>
          </ResponsiveContainer>
        }
        textLeft={false}
      />

      <StorySection
        title="Intensidad Anual"
        description={`Distribución año a año de las mociones ingresadas dentro del periodo legislativo ${selected}.`}
        chart={
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={yearCounts}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" tick={{ fill: "#b0b0b0", fontSize: 12 }} />
              <YAxis tick={{ fill: "#b0b0b0", fontSize: 12 }} />
              <Tooltip contentStyle={{ backgroundColor: "#1a1a1a", border: "1px solid #333", borderRadius: 8 }} itemStyle={{ color: "#fff" }} />
              <Bar dataKey="count" name="Proyectos" fill="#c0392b" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        }
        textLeft
      />

      {/* Tabla */}
      <div className="mt-12">
        <h3 className="font-serif text-xl mb-4">Proyectos del periodo</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10 text-left text-muted-foreground uppercase text-xs tracking-wider">
                <th className="py-3 px-2">Boletín</th>
                <th className="py-3 px-2">Nombre</th>
                <th className="py-3 px-2">Estado</th>
                <th className="py-3 px-2">Fecha</th>
              </tr>
            </thead>
            <tbody>
              {filtered.sort((a, b) => (b.fecha_de_ingreso || "").localeCompare(a.fecha_de_ingreso || "")).map(m => (
                <tr key={m.n_boletin} className="border-b border-white/5 hover:bg-white/5">
                  <td className="py-2 px-2 text-[#c0392b] font-mono text-xs">{m.n_boletin}</td>
                  <td className="py-2 px-2">{m.nombre_iniciativa?.slice(0, 80)}{(m.nombre_iniciativa?.length || 0) > 80 ? "..." : ""}</td>
                  <td className="py-2 px-2 text-muted-foreground text-xs">{m.estado_del_proyecto_de_ley}</td>
                  <td className="py-2 px-2 text-muted-foreground text-xs whitespace-nowrap">{m.fecha_de_ingreso?.slice(0, 10)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  )
}

export default function PeriodosPage() {
  return (
    <DashboardGate>
      <PeriodosContent />
    </DashboardGate>
  )
}
