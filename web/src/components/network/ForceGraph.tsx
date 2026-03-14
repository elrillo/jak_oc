"use client"

import { useRef, useEffect, useState, useCallback } from "react"
import * as d3 from "d3"
import type { NetworkNode, NetworkLink } from "@/app/red/page"

interface ForceGraphProps {
  nodes: NetworkNode[]
  links: NetworkLink[]
  onNodeClick?: (id: string) => void
  selectedNode: string | null
}

interface SimNode extends NetworkNode, d3.SimulationNodeDatum {}
interface SimLink extends d3.SimulationLinkDatum<SimNode> {
  weight: number
}

export function ForceGraph({ nodes, links, onNodeClick, selectedNode }: ForceGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const svgRef = useRef<SVGSVGElement>(null)
  const simulationRef = useRef<d3.Simulation<SimNode, SimLink> | null>(null)
  const [dimensions, setDimensions] = useState({ width: 600, height: 500 })
  const [tooltip, setTooltip] = useState<{
    x: number; y: number; node: NetworkNode
  } | null>(null)

  // Responsive dimensions
  useEffect(() => {
    if (!containerRef.current) return
    const observer = new ResizeObserver((entries) => {
      const { width } = entries[0].contentRect
      const isMobile = width < 500
      setDimensions({
        width: Math.max(width, 280),
        height: isMobile ? 350 : 500,
      })
    })
    observer.observe(containerRef.current)
    return () => observer.disconnect()
  }, [])

  // D3 Force simulation
  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return

    const { width, height } = dimensions
    const isMobile = width < 500

    // Clean previous simulation
    if (simulationRef.current) {
      simulationRef.current.stop()
    }

    const svg = d3.select(svgRef.current)
    svg.selectAll("*").remove()

    // Create copies for simulation
    const simNodes: SimNode[] = nodes.map(n => ({ ...n }))
    const simLinks: SimLink[] = links.map(l => ({
      source: l.source,
      target: l.target,
      weight: l.weight,
    }))

    // Scales
    const maxWeight = d3.max(simNodes.filter(n => !n.isCenter), n => n.weight) || 1
    const nodeRadius = (n: SimNode) => {
      if (n.isCenter) return isMobile ? 18 : 24
      const base = isMobile ? 5 : 6
      const scale = isMobile ? 10 : 14
      return base + (n.weight / maxWeight) * scale
    }

    const linkOpacity = (l: SimLink) => {
      return 0.15 + (l.weight / maxWeight) * 0.45
    }

    const linkWidth = (l: SimLink) => {
      return 0.5 + (l.weight / maxWeight) * (isMobile ? 2.5 : 3.5)
    }

    // Container group with zoom
    const g = svg.append("g")

    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.3, 4])
      .on("zoom", (event) => {
        g.attr("transform", event.transform)
        setTooltip(null)
      })

    svg.call(zoom)

    // Initial centering
    svg.call(zoom.transform, d3.zoomIdentity.translate(width / 2, height / 2).scale(0.85).translate(-width / 2, -height / 2))

    // Links
    const link = g.append("g")
      .selectAll("line")
      .data(simLinks)
      .join("line")
      .attr("stroke", "#ffffff")
      .attr("stroke-opacity", l => linkOpacity(l))
      .attr("stroke-width", l => linkWidth(l))

    // Node groups
    const node = g.append("g")
      .selectAll("g")
      .data(simNodes)
      .join("g")
      .attr("cursor", "pointer")
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      .call(d3.drag<any, SimNode>()
        .on("start", (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart()
          d.fx = d.x
          d.fy = d.y
          setTooltip(null)
        })
        .on("drag", (event, d) => {
          d.fx = event.x
          d.fy = event.y
        })
        .on("end", (event, d) => {
          if (!event.active) simulation.alphaTarget(0)
          d.fx = null
          d.fy = null
        })
      )

    // Node circles
    node.append("circle")
      .attr("r", d => nodeRadius(d))
      .attr("fill", d => d.color)
      .attr("fill-opacity", 0.85)
      .attr("stroke", d => d.isCenter ? "#fff" : "rgba(255,255,255,0.2)")
      .attr("stroke-width", d => d.isCenter ? 2.5 : 1)

    // Labels for center + large nodes
    node.filter(d => d.isCenter || d.weight >= maxWeight * 0.5)
      .append("text")
      .text(d => {
        const parts = d.id.split(" ")
        return parts.length > 2 ? parts.slice(0, 2).join(" ") : d.id
      })
      .attr("text-anchor", "middle")
      .attr("dy", d => nodeRadius(d) + (isMobile ? 12 : 14))
      .attr("fill", "#ccc")
      .attr("font-size", isMobile ? "9px" : "10px")
      .attr("font-family", "var(--font-merriweather), serif")
      .attr("pointer-events", "none")

    // Events
    node.on("click", (_event, d) => {
      onNodeClick?.(d.id)
    })

    node.on("mouseenter", (event, d) => {
      if (d.isCenter) return
      const [x, y] = d3.pointer(event, containerRef.current)
      setTooltip({ x, y: y - 10, node: d })

      // Highlight connected links
      link.attr("stroke-opacity", l => {
        const src = typeof l.source === "object" ? (l.source as SimNode).id : l.source
        const tgt = typeof l.target === "object" ? (l.target as SimNode).id : l.target
        return src === d.id || tgt === d.id ? 0.8 : 0.05
      })
    })

    node.on("mouseleave", () => {
      setTooltip(null)
      link.attr("stroke-opacity", l => linkOpacity(l))
    })

    // Simulation
    const simulation = d3.forceSimulation(simNodes)
      .force("link", d3.forceLink<SimNode, SimLink>(simLinks)
        .id(d => d.id)
        .distance(d => isMobile ? 60 : 80)
        .strength(d => 0.3 + (d.weight / maxWeight) * 0.4)
      )
      .force("charge", d3.forceManyBody()
        .strength(d => (d as SimNode).isCenter ? (isMobile ? -300 : -500) : (isMobile ? -30 : -50))
      )
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide<SimNode>()
        .radius(d => nodeRadius(d) + 3)
      )
      .force("x", d3.forceX(width / 2).strength(0.05))
      .force("y", d3.forceY(height / 2).strength(0.05))
      .on("tick", () => {
        link
          .attr("x1", d => (d.source as SimNode).x!)
          .attr("y1", d => (d.source as SimNode).y!)
          .attr("x2", d => (d.target as SimNode).x!)
          .attr("y2", d => (d.target as SimNode).y!)

        node.attr("transform", d => `translate(${d.x},${d.y})`)
      })

    simulationRef.current = simulation

    return () => {
      simulation.stop()
    }
  }, [nodes, links, dimensions, onNodeClick])

  // Highlight selected node
  useEffect(() => {
    if (!svgRef.current) return
    const svg = d3.select(svgRef.current)

    svg.selectAll<SVGCircleElement, SimNode>("circle")
      .attr("stroke", d => {
        if (d.isCenter) return "#fff"
        if (d.id === selectedNode) return "#fff"
        return "rgba(255,255,255,0.2)"
      })
      .attr("stroke-width", d => {
        if (d.isCenter) return 2.5
        if (d.id === selectedNode) return 2.5
        return 1
      })
      .attr("fill-opacity", d => {
        if (!selectedNode) return 0.85
        if (d.id === selectedNode || d.isCenter) return 1
        return 0.4
      })
  }, [selectedNode])

  return (
    <div ref={containerRef} className="relative w-full">
      <div className="bg-white/[0.02] border border-white/10 rounded-xl overflow-hidden">
        <svg
          ref={svgRef}
          width={dimensions.width}
          height={dimensions.height}
          viewBox={`0 0 ${dimensions.width} ${dimensions.height}`}
          className="select-none"
        />
      </div>

      {/* Tooltip */}
      {tooltip && (
        <div
          className="absolute pointer-events-none z-50 bg-[#1a1a1a] border border-white/20 rounded-lg px-3 py-2 shadow-xl"
          style={{
            left: Math.min(tooltip.x, dimensions.width - 180),
            top: Math.max(tooltip.y - 50, 0),
            maxWidth: 200,
          }}
        >
          <p className="text-sm font-semibold truncate">{tooltip.node.id.split(" ").slice(0, 3).join(" ")}</p>
          <div className="flex items-center gap-1.5 mt-0.5">
            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: tooltip.node.color }} />
            <span className="text-xs text-muted-foreground">{tooltip.node.party}</span>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            {tooltip.node.weight} coautorías
          </p>
        </div>
      )}

      {/* Zoom hint */}
      <p className="text-center text-[10px] text-muted-foreground mt-2">
        Arrastra para mover · Scroll/pinch para zoom · Clic para seleccionar
      </p>
    </div>
  )
}
