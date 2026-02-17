"use client"

import { useMemo } from "react"
import { useDashboard, DashboardGate } from "@/components/DashboardProvider"
import { PageHeader } from "@/components/PageHeader"
import { getCoauthorsForBoletines } from "@/lib/queries"
import { normalizeParty, getPartyColor } from "@/lib/parties"
import { valueCounts } from "@/lib/legislative"
import { motion } from "framer-motion"
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip, Cell,
} from "recharts"

function AlianzasContent() {
  const { data, coautores, diputados } = useDashboard()

  const networkData = useMemo(() => {
    if (!data) return { partyData: [], topAllies: [] }

    const jakCoauthors = getCoauthorsForBoletines(coautores, data.jakBoletinIds, data.foundName)
    const dipMap = new Map(diputados.map(d => [d.diputado, d.partido || d.partido_politico || null]))

    // Agrupar por diputado con partido
    const allyMap: Record<string, { diputado: string; partido: string; count: number }> = {}
    for (const c of jakCoauthors) {
      if (!allyMap[c.diputado]) {
        const rawParty = dipMap.get(c.diputado) || null
        allyMap[c.diputado] = { diputado: c.diputado, partido: normalizeParty(rawParty), count: 0 }
      }
      allyMap[c.diputado].count++
    }

    const allies = Object.values(allyMap).sort((a, b) => b.count - a.count)

    // Agrupar por partido
    const partyAgg: Record<string, number> = {}
    for (const a of allies) {
      partyAgg[a.partido] = (partyAgg[a.partido] || 0) + a.count
    }
    const partyData = Object.entries(partyAgg)
      .map(([name, count]) => ({ name, count, fill: getPartyColor(name) }))
      .sort((a, b) => b.count - a.count)

    return { partyData, topAllies: allies.slice(0, 20) }
  }, [data, coautores, diputados])

  if (!data) return null

  return (
    <>
      <PageHeader
        title="Red de Influencia Política"
        subtitle="Grafo de coautorías: análisis de las alianzas parlamentarias de José Antonio Kast."
      />

      {/* Coautorías por partido */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 items-center my-12">
        <div className="lg:col-span-2">
          <h3 className="text-2xl font-serif font-semibold mb-4">Alianzas por Partido</h3>
          <p className="text-muted-foreground leading-relaxed">
            Las coautorías revelan el mapa de alianzas legislativas. Cada barra representa el total de proyectos firmados en conjunto con diputados de ese partido.
          </p>
        </div>
        <div className="lg:col-span-3">
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={networkData.partyData} layout="vertical" margin={{ left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis type="number" tick={{ fill: "#b0b0b0", fontSize: 12 }} />
              <YAxis dataKey="name" type="category" tick={{ fill: "#b0b0b0", fontSize: 12 }} width={120} />
              <Tooltip contentStyle={{ backgroundColor: "#1a1a1a", border: "1px solid #333", borderRadius: 8 }} itemStyle={{ color: "#fff" }} />
              <Bar dataKey="count" name="Coautorías" radius={[0, 4, 4, 0]}>
                {networkData.partyData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="border-t border-white/5 my-8" />

      {/* Top 20 aliados */}
      <h3 className="font-serif text-xl mb-6 text-center">Top 20 Aliados Legislativos</h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {networkData.topAllies.map((ally, i) => (
          <motion.div
            key={ally.diputado}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: i * 0.03 }}
            className="bg-[#141414] border border-white/5 rounded-lg p-4 flex items-center gap-3"
          >
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0"
              style={{ backgroundColor: getPartyColor(ally.partido) + "33", color: getPartyColor(ally.partido) }}
            >
              {i + 1}
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium truncate">{ally.diputado}</p>
              <p className="text-xs text-muted-foreground">
                {ally.partido} &middot; {ally.count} proyectos
              </p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Tabla completa */}
      <div className="mt-12">
        <h3 className="font-serif text-xl mb-4">Detalle por Partido</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10 text-left text-muted-foreground uppercase text-xs tracking-wider">
                <th className="py-3 px-2">Partido</th>
                <th className="py-3 px-2">Diputado</th>
                <th className="py-3 px-2 text-right">Proyectos</th>
              </tr>
            </thead>
            <tbody>
              {networkData.topAllies.map(a => (
                <tr key={a.diputado} className="border-b border-white/5 hover:bg-white/5">
                  <td className="py-2 px-2">
                    <span className="inline-block w-2 h-2 rounded-full mr-2" style={{ backgroundColor: getPartyColor(a.partido) }} />
                    {a.partido}
                  </td>
                  <td className="py-2 px-2">{a.diputado}</td>
                  <td className="py-2 px-2 text-right font-mono">{a.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  )
}

export default function AlianzasPage() {
  return (
    <DashboardGate>
      <AlianzasContent />
    </DashboardGate>
  )
}
