"use client"

import { ResponsiveContainer } from "recharts"
import { Skeleton } from "@/components/ui/skeleton"

/** Estilos estándar para Tooltip de Recharts */
export const CHART_TOOLTIP_STYLE = {
  contentStyle: {
    backgroundColor: "#1a1a1a",
    border: "1px solid #333",
    borderRadius: 8,
    fontSize: 13,
  },
  itemStyle: { color: "#fff" },
}

/** Paleta de colores para charts */
export const CHART_COLORS = [
  "#c0392b", "#2ecc71", "#3498db", "#f39c12",
  "#9b59b6", "#1abc9c", "#e67e22", "#95a5a6",
]

interface ChartContainerProps {
  children: React.ReactNode
  /** Altura en desktop (default: 350) */
  height?: number
  /** Altura en mobile (default: 250) */
  mobileHeight?: number
  /** Mostrar skeleton loading */
  loading?: boolean
  /** Mensaje cuando no hay datos */
  emptyMessage?: string
  /** Si hay datos para mostrar */
  hasData?: boolean
  className?: string
}

export function ChartContainer({
  children,
  height = 350,
  mobileHeight = 250,
  loading = false,
  emptyMessage = "No hay datos disponibles.",
  hasData = true,
  className = "",
}: ChartContainerProps) {
  if (loading) {
    return (
      <div className={`w-full ${className}`} style={{ height: mobileHeight }}>
        <Skeleton className="w-full h-full rounded-lg bg-white/5" />
      </div>
    )
  }

  if (!hasData) {
    return (
      <div
        className={`w-full flex items-center justify-center text-muted-foreground text-sm ${className}`}
        style={{ height: mobileHeight }}
      >
        {emptyMessage}
      </div>
    )
  }

  return (
    <div className={`w-full ${className}`}>
      {/* Mobile height */}
      <div className="block sm:hidden">
        <ResponsiveContainer width="100%" height={mobileHeight}>
          {children as React.ReactElement}
        </ResponsiveContainer>
      </div>
      {/* Desktop height */}
      <div className="hidden sm:block">
        <ResponsiveContainer width="100%" height={height}>
          {children as React.ReactElement}
        </ResponsiveContainer>
      </div>
    </div>
  )
}
