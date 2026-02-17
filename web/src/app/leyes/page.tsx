"use client"

import { useMemo } from "react"
import { useDashboard, DashboardGate } from "@/components/DashboardProvider"
import { PageHeader } from "@/components/PageHeader"
import { StorySection } from "@/components/StorySection"
import { SUCCESS_PATTERN, valueCounts, formatDateHuman } from "@/lib/legislative"
import { motion } from "framer-motion"
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip,
} from "recharts"

function LeyesContent() {
  const { data } = useDashboard()

  const leyes = useMemo(() => {
    if (!data) return []
    return data.jakMociones.filter(m => SUCCESS_PATTERN.test(m.estado_del_proyecto_de_ley))
  }, [data])

  if (!data) return null

  if (leyes.length === 0) {
    return (
      <>
        <PageHeader title="Leyes y Proyectos Terminados" />
        <p className="text-center text-muted-foreground">No se encontraron leyes o proyectos terminados.</p>
      </>
    )
  }

  const leyesPorAnio = valueCounts(
    leyes.map(m => String(m.anio || "")).filter(s => s !== "")
  ).sort((a, b) => Number(a.name) - Number(b.name))

  const leyesPorComision = valueCounts(
    leyes.map(m => m.comision_inicial || "Desconocida")
  ).slice(0, 10).reverse()

  return (
    <>
      <PageHeader
        title="Leyes y Proyectos Terminados"
        subtitle="Análisis de proyectos que finalizaron su tramitación exitosamente."
      />

      {/* Productividad por año */}
      <StorySection
        title="Productividad Legislativa"
        description={`Se han consolidado ${leyes.length} leyes a lo largo de los años. Este gráfico muestra en qué años se originaron los proyectos que finalmente tuvieron éxito.`}
        chart={
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={leyesPorAnio}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" tick={{ fill: "#b0b0b0", fontSize: 12 }} />
              <YAxis tick={{ fill: "#b0b0b0", fontSize: 12 }} />
              <Tooltip contentStyle={{ backgroundColor: "#1a1a1a", border: "1px solid #333", borderRadius: 8 }} itemStyle={{ color: "#fff" }} />
              <Bar dataKey="count" name="Leyes" fill="#2ecc71" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        }
        textLeft
      />

      {/* Por comisión */}
      <StorySection
        title="Áreas de Éxito"
        description="Las comisiones listadas representan los nichos donde el trabajo legislativo ha sido más efectivo, logrando la aprobación final de las leyes."
        chart={
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={leyesPorComision} layout="vertical" margin={{ left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis type="number" tick={{ fill: "#b0b0b0", fontSize: 12 }} />
              <YAxis dataKey="name" type="category" tick={{ fill: "#b0b0b0", fontSize: 11 }} width={200} />
              <Tooltip contentStyle={{ backgroundColor: "#1a1a1a", border: "1px solid #333", borderRadius: 8 }} itemStyle={{ color: "#fff" }} />
              <Bar dataKey="count" name="Leyes" fill="#f39c12" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        }
        textLeft={false}
      />

      <div className="border-t border-white/5 my-8" />

      {/* Listado detallado */}
      <h3 className="font-serif text-xl mb-6">Listado Detallado</h3>
      <div className="space-y-3">
        {leyes.map((ley, i) => (
          <motion.details
            key={ley.n_boletin}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: i * 0.02 }}
            className="bg-[#141414] border border-white/5 rounded-lg group"
          >
            <summary className="px-5 py-4 cursor-pointer flex items-center gap-3 hover:bg-white/5 rounded-lg">
              <span className="text-[#2ecc71] text-lg">&#9878;</span>
              <span className="text-[#c0392b] font-mono text-xs">{ley.n_boletin}</span>
              <span className="text-sm flex-1">{ley.nombre_iniciativa}</span>
            </summary>
            <div className="px-5 pb-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Fecha Ingreso: <span className="text-white">{formatDateHuman(ley.fecha_de_ingreso)}</span></p>
                <p className="text-muted-foreground">Tipo: <span className="text-white">{ley.tipo_de_proyecto || "N/A"}</span></p>
              </div>
              <div>
                <p className="text-muted-foreground">Estado: <span className="text-white">{ley.estado_del_proyecto_de_ley}</span></p>
                {ley.publicado_en_diario_oficial && (
                  <p className="text-[#2ecc71]">Publicado: {formatDateHuman(ley.publicado_en_diario_oficial)}</p>
                )}
              </div>
            </div>
          </motion.details>
        ))}
      </div>
    </>
  )
}

export default function LeyesPage() {
  return (
    <DashboardGate>
      <LeyesContent />
    </DashboardGate>
  )
}
