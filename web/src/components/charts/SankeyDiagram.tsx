"use client"

import { useMemo, useRef, useEffect, useState } from "react"
import { sankey as d3Sankey, sankeyLinkHorizontal, SankeyNode, SankeyLink as SankeyLinkType } from "d3-sankey"

interface SNode {
  name: string
}

interface SLink {
  source: number
  target: number
  value: number
}

interface SankeyLink {
  source: string
  target: string
  value: number
}

interface SankeyDiagramProps {
  links: SankeyLink[]
  className?: string
}

const NODE_COLORS: Record<string, string> = {
  // Temas (fuente)
  "Constitución y Justicia": "#c0392b",
  "Economía y Hacienda": "#f39c12",
  "Seguridad y Defensa": "#2c3e50",
  "Familia y Social": "#9b59b6",
  "Educación y Cultura": "#3498db",
  "Salud": "#2ecc71",
  "Trabajo y Previsión": "#e67e22",
  "Medio Ambiente y Recursos": "#1abc9c",
  "DD.HH. y Nacionalidad": "#e74c3c",
  "Gobierno Interior": "#95a5a6",
  "Vivienda e Infraestructura": "#d35400",
  "Otras": "#7f8c8d",
  // Estados (destino)
  "En Tramitación": "#3498db",
  "Archivado": "#95a5a6",
  "Tramitación Terminada": "#2ecc71",
  "Retirado": "#e74c3c",
  "Publicado": "#27ae60",
}

/**
 * Diagrama Sankey: flujo de Temas → Resultado Legislativo.
 * Usa D3-sankey para el layout, React para el render SVG.
 */
export function SankeyDiagram({ links, className = "" }: SankeyDiagramProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [dimensions, setDimensions] = useState({ width: 600, height: 400 })
  const [tooltip, setTooltip] = useState<{
    x: number
    y: number
    text: string
  } | null>(null)

  // Medir contenedor
  useEffect(() => {
    if (!containerRef.current) return
    const observer = new ResizeObserver((entries) => {
      const { width } = entries[0].contentRect
      const isMobile = width < 500
      setDimensions({
        width: Math.max(width, 300),
        height: isMobile ? 350 : 450,
      })
    })
    observer.observe(containerRef.current)
    return () => observer.disconnect()
  }, [])

  const sankeyData = useMemo(() => {
    if (links.length === 0) return null

    // Construir nodos únicos
    const nodeNames = new Set<string>()
    links.forEach((l) => {
      nodeNames.add(l.source)
      nodeNames.add(l.target)
    })
    const nodes = Array.from(nodeNames).map((name) => ({ name }))
    const nodeIndex = new Map(nodes.map((n, i) => [n.name, i]))

    const sankeyLinks = links
      .filter((l) => nodeIndex.has(l.source) && nodeIndex.has(l.target))
      .map((l) => ({
        source: nodeIndex.get(l.source)!,
        target: nodeIndex.get(l.target)!,
        value: l.value,
      }))

    const isMobile = dimensions.width < 500

    const generator = d3Sankey<SNode, SLink>()
      .nodeWidth(isMobile ? 12 : 18)
      .nodePadding(isMobile ? 6 : 10)
      .extent([
        [isMobile ? 80 : 160, 5],
        [dimensions.width - (isMobile ? 80 : 140), dimensions.height - 10],
      ])

    try {
      const result = generator({
        nodes: nodes.map((d) => ({ ...d })) as SankeyNode<SNode, SLink>[],
        links: sankeyLinks.map((d) => ({ ...d })) as SankeyLinkType<SNode, SLink>[],
      })
      return { nodes: result.nodes, links: result.links, nodeNames: nodes }
    } catch {
      return null
    }
  }, [links, dimensions])

  if (!sankeyData) {
    return (
      <div className={`flex items-center justify-center h-64 text-muted-foreground text-sm ${className}`}>
        No hay datos suficientes para el diagrama.
      </div>
    )
  }

  const isMobile = dimensions.width < 500

  return (
    <div ref={containerRef} className={`w-full relative ${className}`}>
      <svg width={dimensions.width} height={dimensions.height}>
        {/* Links */}
        <g>
          {sankeyData.links.map((link, i) => {
            const sourceName =
              typeof link.source === "object" && link.source !== null
                ? (link.source as { name?: string }).name || ""
                : ""
            const color = NODE_COLORS[sourceName] || "#555"
            return (
              <path
                key={i}
                d={sankeyLinkHorizontal()(link as Parameters<ReturnType<typeof sankeyLinkHorizontal>>[0]) || ""}
                fill="none"
                stroke={color}
                strokeOpacity={0.3}
                strokeWidth={Math.max(1, (link as { width?: number }).width || 1)}
                className="hover:stroke-opacity-60 transition-all cursor-default"
                onMouseEnter={(e) => {
                  const src = typeof link.source === "object" ? (link.source as { name?: string }).name : ""
                  const tgt = typeof link.target === "object" ? (link.target as { name?: string }).name : ""
                  setTooltip({
                    x: e.nativeEvent.offsetX,
                    y: e.nativeEvent.offsetY - 10,
                    text: `${src} → ${tgt}: ${(link as { value?: number }).value || 0}`,
                  })
                }}
                onMouseLeave={() => setTooltip(null)}
              />
            )
          })}
        </g>

        {/* Nodes */}
        <g>
          {sankeyData.nodes.map((node, i) => {
            const name = (node as { name?: string }).name || ""
            const x0 = (node as { x0?: number }).x0 || 0
            const y0 = (node as { y0?: number }).y0 || 0
            const x1 = (node as { x1?: number }).x1 || 0
            const y1 = (node as { y1?: number }).y1 || 0
            const color = NODE_COLORS[name] || "#555"
            const nodeHeight = y1 - y0

            return (
              <g key={i}>
                <rect
                  x={x0}
                  y={y0}
                  width={x1 - x0}
                  height={Math.max(nodeHeight, 1)}
                  fill={color}
                  rx={2}
                  className="hover:brightness-125 transition-all"
                />
                {/* Label - solo si el nodo es suficientemente alto */}
                {nodeHeight > (isMobile ? 10 : 14) && (
                  <text
                    x={x0 < dimensions.width / 2 ? x0 - 4 : x1 + 4}
                    y={y0 + nodeHeight / 2}
                    dy="0.35em"
                    textAnchor={x0 < dimensions.width / 2 ? "end" : "start"}
                    fill="#b0b0b0"
                    fontSize={isMobile ? 8 : 11}
                    fontFamily="var(--font-merriweather), serif"
                  >
                    {isMobile && name.length > 12 ? name.slice(0, 10) + "…" : name}
                  </text>
                )}
              </g>
            )
          })}
        </g>
      </svg>

      {/* Tooltip */}
      {tooltip && (
        <div
          className="absolute px-2 py-1 bg-[#1a1a1a] border border-white/20 rounded text-[11px] text-white whitespace-nowrap pointer-events-none z-10"
          style={{ left: tooltip.x, top: tooltip.y, transform: "translate(-50%, -100%)" }}
        >
          {tooltip.text}
        </div>
      )}
    </div>
  )
}
