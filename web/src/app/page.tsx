"use client"

import { useMemo } from "react"
import { useDashboard, DashboardGate } from "@/components/DashboardProvider"
import { KpiCard } from "@/components/KpiCard"
import { PageHeader } from "@/components/PageHeader"
import { StorySection } from "@/components/StorySection"
import { Heatmap } from "@/components/charts/Heatmap"
import { DeputyRadar } from "@/components/charts/DeputyRadar"
import { valueCounts } from "@/lib/legislative"
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
} from "recharts"
import { CHART_TOOLTIP_STYLE } from "@/components/ChartContainer"

const COLORS = ["#c0392b", "#2ecc71", "#3498db", "#f39c12", "#9b59b6", "#1abc9c", "#e67e22", "#95a5a6"]

function GeneralContent() {
  const { data } = useDashboard()
  if (!data) return null

  const { jakMociones, total, leyesCount, tasaExito, promedioAnual, topAlly } = data

  // Estado de proyectos (donut)
  const statusCounts = valueCounts(
    jakMociones.map(m => m.estado_del_proyecto_de_ley).filter(Boolean)
  ).slice(0, 8)

  // Comisiones top (barras horizontales)
  const comisionCounts = valueCounts(
    jakMociones.map(m => m.comision_inicial || "Desconocida")
  ).slice(0, 10).reverse()

  // Producción anual
  const yearCounts = valueCounts(
    jakMociones.map(m => String(m.anio || "")).filter(s => s !== "")
  ).sort((a, b) => Number(a.name) - Number(b.name))

  // Radar: perfil temático
  const radarData = useMemo(() => {
    const themes = valueCounts(
      jakMociones.map(m => m.tematica_asociada || "Otras")
    )
    return themes.map(t => ({
      category: t.name,
      value: Math.round((t.count / total) * 100),
    }))
  }, [jakMociones, total])

  return (
    <>
      <PageHeader
        title="Análisis de Trayectoria Legislativa"
        subtitle="Un recorrido por la actividad y efectividad del diputado en el Congreso Nacional."
      />

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
        <KpiCard title="Total Iniciativas" value={total} subtitle="Carrera parlamentaria" />
        <KpiCard title="Aprobados / Terminados" value={leyesCount} subtitle={`Tasa: ${tasaExito.toFixed(1)}%`} />
        <KpiCard title="Promedio Anual" value={promedioAnual} subtitle="Mociones por año" />
        <KpiCard title="Aliado Histórico" value={topAlly.split(" ").slice(0, 2).join(" ")} subtitle="Mayor colaborador" />
      </div>

      <div className="border-t border-white/5 my-8" />

      {/* Sección 1: Estado - texto izq, donut der */}
      <StorySection
        title="Estado de la Gestión"
        description={`Esta sección analiza el ciclo de vida de los ${total} proyectos presentados.\n\nAproximadamente un ${tasaExito.toFixed(1)}% de las iniciativas han logrado convertirse en ley o finalizar su tramitación, lo que representa un indicador clave de efectividad legislativa.\n\nLa mayoría de los proyectos en el Congreso a menudo quedan estancados en comisiones, un desafío común en la labor parlamentaria chilena.`}
        chart={
          <ResponsiveContainer width="100%" height={350}>
            <PieChart>
              <Pie
                data={statusCounts}
                dataKey="count"
                nameKey="name"
                cx="50%"
                cy="50%"
                innerRadius={80}
                outerRadius={140}
                paddingAngle={2}
              >
                {statusCounts.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip {...CHART_TOOLTIP_STYLE} />
            </PieChart>
          </ResponsiveContainer>
        }
        textLeft
      />

      {/* Sección 2: Comisiones - barras izq, texto der */}
      <StorySection
        title="Áreas de Influencia"
        description={`El impacto legislativo se concentra principalmente en las áreas de Constitución, Seguridad y Hacienda.\n\nEste gráfico destaca las 10 comisiones donde se ha ingresado el mayor volumen de iniciativas. Una mayor cantidad de proyectos en comisiones clave sugiere un enfoque en temas de relevancia nacional y reformas estructurales.`}
        chart={
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={comisionCounts} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis type="number" tick={{ fill: "#b0b0b0", fontSize: 12 }} />
              <YAxis
                dataKey="name"
                type="category"
                tick={{ fill: "#b0b0b0", fontSize: 11 }}
                width={200}
              />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Bar dataKey="count" name="Proyectos" fill="#c0392b" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        }
        textLeft={false}
      />

      {/* Sección 3: Evolución - texto izq, barras der */}
      <StorySection
        title="Evolución Histórica"
        description={`La actividad parlamentaria no es lineal; fluctúa según los ciclos políticos y los periodos presidenciales.\n\nSe observa una intensidad variable a lo largo de los años, con picos de actividad que suelen coincidir con debates nacionales críticos o el inicio de nuevos mandatos parlamentarios.`}
        chart={
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={yearCounts}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" tick={{ fill: "#b0b0b0", fontSize: 12 }} />
              <YAxis tick={{ fill: "#b0b0b0", fontSize: 12 }} />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Bar dataKey="count" name="Proyectos" fill="#555" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        }
        textLeft
      />

      <div className="border-t border-white/5 my-8" />

      {/* NUEVA Sección 4: Heatmap de actividad */}
      <StorySection
        title="Mapa de Actividad"
        description="Este mapa de calor revela los patrones estacionales de la actividad legislativa. Cada celda representa la cantidad de mociones ingresadas en un mes y año específico.\n\nLos meses con mayor intensidad de color indican períodos de alta productividad parlamentaria."
        chart={<Heatmap dates={jakMociones.map(m => m.fecha_de_ingreso)} />}
        variant="full-width"
      />

      <div className="border-t border-white/5 my-8" />

      {/* NUEVA Sección 5: Radar temático */}
      <StorySection
        title="Huella Legislativa"
        description="El perfil temático muestra la distribución porcentual de las mociones en cada área. Este radar revela las prioridades legislativas predominantes.\n\nUn área más extendida indica una mayor concentración de proyectos en esa temática."
        chart={<DeputyRadar data={radarData} />}
        textLeft={false}
      />
    </>
  )
}

export default function GeneralPage() {
  return (
    <DashboardGate>
      <GeneralContent />
    </DashboardGate>
  )
}
