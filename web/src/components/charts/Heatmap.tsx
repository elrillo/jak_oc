"use client"

import { useMemo } from "react"

interface HeatmapProps {
  /** Array de fechas ISO (YYYY-MM-DD) */
  dates: (string | null)[]
  className?: string
}

const MONTH_LABELS = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

/**
 * Heatmap de actividad legislativa estilo GitHub contributions.
 * Filas = años, Columnas = meses.
 * Escala de color: transparente (0) → #c0392b (max).
 */
export function Heatmap({ dates, className = "" }: HeatmapProps) {
  const { grid, years, maxCount } = useMemo(() => {
    const counts: Record<string, number> = {}
    const yearSet = new Set<number>()

    for (const d of dates) {
      if (!d) continue
      const date = new Date(d)
      if (isNaN(date.getTime())) continue
      const y = date.getFullYear()
      const m = date.getMonth()
      yearSet.add(y)
      const key = `${y}-${m}`
      counts[key] = (counts[key] || 0) + 1
    }

    const years = Array.from(yearSet).sort()
    let maxCount = 0

    const grid = years.map((y) =>
      Array.from({ length: 12 }, (_, m) => {
        const count = counts[`${y}-${m}`] || 0
        if (count > maxCount) maxCount = count
        return count
      })
    )

    return { grid, years, maxCount }
  }, [dates])

  if (years.length === 0) return null

  const getColor = (count: number) => {
    if (count === 0) return "rgba(255,255,255,0.03)"
    const intensity = count / maxCount
    // Interpolar de oscuro a #c0392b
    const r = Math.round(26 + (192 - 26) * intensity)
    const g = Math.round(26 + (57 - 26) * intensity)
    const b = Math.round(26 + (43 - 26) * intensity)
    return `rgb(${r},${g},${b})`
  }

  return (
    <div className={`w-full ${className}`}>
      {/* Desktop: tabla completa */}
      <div className="hidden sm:block overflow-x-auto">
        <table className="mx-auto border-separate" style={{ borderSpacing: 3 }}>
          <thead>
            <tr>
              <th className="w-12" />
              {MONTH_LABELS.map((m) => (
                <th key={m} className="text-[10px] text-muted-foreground font-normal px-1 pb-1">
                  {m}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {grid.map((row, yi) => (
              <tr key={years[yi]}>
                <td className="text-[11px] text-muted-foreground font-mono pr-2 text-right">
                  {years[yi]}
                </td>
                {row.map((count, mi) => (
                  <td key={mi} className="relative group">
                    <div
                      className="w-6 h-6 lg:w-7 lg:h-7 rounded-sm transition-transform hover:scale-125 cursor-default"
                      style={{ backgroundColor: getColor(count) }}
                    />
                    {/* Tooltip */}
                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-[#1a1a1a] border border-white/20 rounded text-[10px] text-white whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-10">
                      {count} {count === 1 ? "moción" : "mociones"} — {MONTH_LABELS[mi]} {years[yi]}
                    </div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile: layout compacto */}
      <div className="sm:hidden overflow-x-auto">
        <table className="mx-auto border-separate" style={{ borderSpacing: 2 }}>
          <thead>
            <tr>
              <th className="w-8" />
              {MONTH_LABELS.map((m) => (
                <th key={m} className="text-[8px] text-muted-foreground font-normal">
                  {m.charAt(0)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {grid.map((row, yi) => (
              <tr key={years[yi]}>
                <td className="text-[9px] text-muted-foreground font-mono pr-1 text-right">
                  {String(years[yi]).slice(2)}
                </td>
                {row.map((count, mi) => (
                  <td key={mi}>
                    <div
                      className="w-4 h-4 rounded-[2px]"
                      style={{ backgroundColor: getColor(count) }}
                      title={`${count} mociones — ${MONTH_LABELS[mi]} ${years[yi]}`}
                    />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Leyenda */}
      <div className="flex items-center justify-center gap-2 mt-4 text-[10px] text-muted-foreground">
        <span>Menos</span>
        {[0, 0.25, 0.5, 0.75, 1].map((intensity) => (
          <div
            key={intensity}
            className="w-3 h-3 rounded-[2px]"
            style={{ backgroundColor: getColor(Math.round(intensity * maxCount)) }}
          />
        ))}
        <span>Más</span>
      </div>
    </div>
  )
}
