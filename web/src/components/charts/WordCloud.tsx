"use client"

import { useMemo, useRef, useEffect, useState } from "react"

interface WordCloudProps {
  /** Array de tags/palabras (puede tener repetidos, se cuentan) */
  words: string[]
  className?: string
  /** Máximo de palabras a mostrar (default: 40) */
  maxWords?: number
}

interface WordItem {
  text: string
  count: number
  fontSize: number
  color: string
  x: number
  y: number
  rotate: number
}

const COLORS = [
  "#c0392b", "#e74c3c", "#3498db", "#2ecc71", "#f39c12",
  "#9b59b6", "#1abc9c", "#e67e22", "#d35400", "#2c3e50",
  "#16a085", "#8e44ad", "#2980b9", "#27ae60",
]

/**
 * Word Cloud simple basado en SVG puro (sin d3-cloud para evitar
 * problemas de canvas en SSR). Usa un layout de espiral simple.
 */
export function WordCloud({ words, className = "", maxWords = 40 }: WordCloudProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [dimensions, setDimensions] = useState({ width: 500, height: 300 })

  useEffect(() => {
    if (!containerRef.current) return
    const observer = new ResizeObserver((entries) => {
      const { width } = entries[0].contentRect
      const isMobile = width < 500
      setDimensions({
        width: Math.max(width, 280),
        height: isMobile ? 250 : 350,
      })
    })
    observer.observe(containerRef.current)
    return () => observer.disconnect()
  }, [])

  const wordItems = useMemo(() => {
    // Contar frecuencias
    const counts: Record<string, number> = {}
    for (const w of words) {
      const clean = w.trim().toLowerCase()
      if (clean.length < 2) continue
      counts[clean] = (counts[clean] || 0) + 1
    }

    // Ordenar y limitar
    const sorted = Object.entries(counts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, maxWords)

    if (sorted.length === 0) return []

    const maxCount = sorted[0][1]
    const minCount = sorted[sorted.length - 1][1]
    const isMobile = dimensions.width < 500
    const minFont = isMobile ? 10 : 12
    const maxFont = isMobile ? 28 : 38

    // Generar posiciones con espiral
    const cx = dimensions.width / 2
    const cy = dimensions.height / 2
    const items: WordItem[] = []

    sorted.forEach(([text, count], i) => {
      const t = minCount === maxCount ? 1 : (count - minCount) / (maxCount - minCount)
      const fontSize = minFont + t * (maxFont - minFont)

      // Espiral para posición
      const angle = i * 0.7
      const radiusX = (dimensions.width * 0.35) * (i / sorted.length)
      const radiusY = (dimensions.height * 0.35) * (i / sorted.length)
      const x = cx + Math.cos(angle) * radiusX
      const y = cy + Math.sin(angle) * radiusY

      // Rotación leve para variedad
      const rotate = i % 5 === 0 ? -15 : i % 7 === 0 ? 10 : 0

      items.push({
        text: text.charAt(0).toUpperCase() + text.slice(1),
        count,
        fontSize,
        color: COLORS[i % COLORS.length],
        x: Math.max(fontSize * 2, Math.min(x, dimensions.width - fontSize * 2)),
        y: Math.max(fontSize, Math.min(y, dimensions.height - fontSize)),
        rotate,
      })
    })

    return items
  }, [words, maxWords, dimensions])

  if (wordItems.length === 0) {
    return (
      <div className={`flex items-center justify-center h-48 text-muted-foreground text-sm ${className}`}>
        No hay tags disponibles.
      </div>
    )
  }

  return (
    <div ref={containerRef} className={`w-full ${className}`}>
      <svg
        width={dimensions.width}
        height={dimensions.height}
        viewBox={`0 0 ${dimensions.width} ${dimensions.height}`}
        className="select-none"
      >
        {wordItems.map((item, i) => (
          <text
            key={i}
            x={item.x}
            y={item.y}
            fontSize={item.fontSize}
            fill={item.color}
            fillOpacity={0.7 + (item.fontSize / 40) * 0.3}
            textAnchor="middle"
            dominantBaseline="middle"
            fontFamily="var(--font-merriweather), serif"
            fontWeight={item.fontSize > 20 ? 700 : 400}
            transform={item.rotate ? `rotate(${item.rotate} ${item.x} ${item.y})` : undefined}
            className="hover:fill-opacity-100 transition-all cursor-default"
          >
            <title>{item.text}: {item.count}</title>
            {item.text}
          </text>
        ))}
      </svg>
    </div>
  )
}
