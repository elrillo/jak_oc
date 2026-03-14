"use client"

import { useState, useMemo } from "react"
import { useDashboard, DashboardGate } from "@/components/DashboardProvider"
import { PageHeader } from "@/components/PageHeader"
import { ForceGraph } from "@/components/network/ForceGraph"
import { normalizeParty, getPartyColor, PARTY_COLORS } from "@/lib/parties"
import { valueCounts } from "@/lib/legislative"
import type { MocionEnriquecida } from "@/lib/types"

export interface NetworkNode {
  id: string
  party: string
  color: string
  weight: number
  isCenter: boolean
}

export interface NetworkLink {
  source: string
  target: string
  weight: number
}

function RedContent() {
  const { data, coautores, diputados } = useDashboard()
  const [minWeight, setMinWeight] = useState(3)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [filterParty, setFilterParty] = useState<string>("Todos")

  const { nodes, links, parties } = useMemo(() => {
    if (!data) return { nodes: [], links: [], parties: [] }

    const jakBoletinSet = new Set(data.jakBoletinIds)
    const foundName = data.foundName

    // Contar coautorías por diputado (excluyendo a Kast)
    const coauthorCounts: Record<string, number> = {}
    for (const c of coautores) {
      if (jakBoletinSet.has(c.n_boletin) && c.diputado !== foundName) {
        coauthorCounts[c.diputado] = (coauthorCounts[c.diputado] || 0) + 1
      }
    }

    // Mapa de diputados
    const dipMap = new Map(diputados.map(d => [d.diputado, d]))

    // Obtener partidos únicos
    const partySet = new Set<string>()

    // Crear nodos
    const nodeList: NetworkNode[] = [
      { id: foundName, party: "UDI", color: "#c0392b", weight: data.total, isCenter: true },
    ]

    for (const [name, weight] of Object.entries(coauthorCounts)) {
      if (weight < minWeight) continue
      const dip = dipMap.get(name)
      const party = normalizeParty(dip?.partido || dip?.partido_politico || null)
      if (filterParty !== "Todos" && party !== filterParty) continue
      partySet.add(party)
      nodeList.push({
        id: name,
        party,
        color: getPartyColor(party),
        weight,
        isCenter: false,
      })
    }

    // Crear links
    const linkList: NetworkLink[] = nodeList
      .filter(n => !n.isCenter)
      .map(n => ({
        source: foundName,
        target: n.id,
        weight: n.weight,
      }))

    return {
      nodes: nodeList,
      links: linkList,
      parties: Array.from(partySet).sort(),
    }
  }, [data, coautores, diputados, minWeight, filterParty])

  // Info del nodo seleccionado
  const selectedInfo = useMemo(() => {
    if (!selectedNode || !data) return null
    const node = nodes.find(n => n.id === selectedNode)
    if (!node) return null

    const jakBoletinSet = new Set(data.jakBoletinIds)
    const sharedBoletines = coautores
      .filter(c => c.diputado === selectedNode && jakBoletinSet.has(c.n_boletin))
      .map(c => c.n_boletin)

    const sharedMociones = data.jakMociones.filter(m => sharedBoletines.includes(m.n_boletin))

    return { node, sharedMociones, count: sharedBoletines.length }
  }, [selectedNode, data, nodes, coautores])

  if (!data) return null

  return (
    <>
      <PageHeader
        title="Red de Coautorías"
        subtitle="Visualización interactiva de las conexiones legislativas."
      />

      {/* Controls */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6 max-w-xl mx-auto">
        <div>
          <label className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1 block">
            Mínimo coautorías: {minWeight}
          </label>
          <input
            type="range"
            min={1}
            max={20}
            value={minWeight}
            onChange={e => setMinWeight(Number(e.target.value))}
            className="w-full accent-[#c0392b]"
          />
        </div>
        <div>
          <label className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1 block">
            Filtrar por partido
          </label>
          <select
            value={filterParty}
            onChange={e => setFilterParty(e.target.value)}
            className="w-full bg-[#141414] border border-white/10 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-white/30"
          >
            <option value="Todos">Todos los partidos</option>
            {parties.map(p => <option key={p} value={p}>{p}</option>)}
          </select>
        </div>
      </div>

      <p className="text-center text-muted-foreground text-xs mb-4">
        {nodes.length - 1} diputados conectados · {links.length} vínculos
      </p>

      {/* Leyenda de partidos */}
      <div className="flex flex-wrap justify-center gap-3 mb-6">
        {Object.entries(PARTY_COLORS).slice(0, 8).map(([party, color]) => (
          <div key={party} className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />
            <span className="text-[10px] text-muted-foreground">{party}</span>
          </div>
        ))}
      </div>

      {/* Graph + Detail panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ForceGraph
            nodes={nodes}
            links={links}
            onNodeClick={(id) => setSelectedNode(id === selectedNode ? null : id)}
            selectedNode={selectedNode}
          />
        </div>

        {/* Detail sidebar / bottom sheet */}
        <div className="lg:col-span-1">
          {selectedInfo ? (
            <div className="bg-white/[0.02] border border-white/10 rounded-xl p-5 space-y-4">
              <div>
                <h3 className="font-serif text-lg font-semibold">{selectedInfo.node.id.split(" ").slice(0, 3).join(" ")}</h3>
                <div className="flex items-center gap-2 mt-1">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: selectedInfo.node.color }} />
                  <span className="text-sm text-muted-foreground">{selectedInfo.node.party}</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="text-center py-3 bg-white/[0.03] rounded-lg">
                  <p className="text-2xl font-serif font-bold">{selectedInfo.count}</p>
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Coautorías</p>
                </div>
                <div className="text-center py-3 bg-white/[0.03] rounded-lg">
                  <p className="text-2xl font-serif font-bold">
                    {selectedInfo.sharedMociones.filter(m => m.tematica_asociada).length > 0
                      ? valueCounts(selectedInfo.sharedMociones.map(m => m.tematica_asociada || "Otras"))[0].name.split(" ").slice(0, 2).join(" ")
                      : "N/A"}
                  </p>
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Tema principal</p>
                </div>
              </div>

              <div>
                <h4 className="text-xs uppercase tracking-wider text-muted-foreground mb-2">Proyectos compartidos</h4>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {selectedInfo.sharedMociones.slice(0, 15).map(m => (
                    <div key={m.n_boletin} className="text-xs p-2 bg-white/[0.02] rounded border border-white/5">
                      <span className="text-[#c0392b] font-mono">{m.n_boletin}</span>
                      <p className="text-muted-foreground mt-0.5 line-clamp-2">{m.nombre_iniciativa}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white/[0.02] border border-white/5 rounded-xl p-8 text-center">
              <p className="text-muted-foreground text-sm">
                Haz clic en un nodo del grafo para ver los detalles del diputado y sus proyectos compartidos con Kast.
              </p>
            </div>
          )}
        </div>
      </div>
    </>
  )
}

export default function RedPage() {
  return (
    <DashboardGate>
      <RedContent />
    </DashboardGate>
  )
}
