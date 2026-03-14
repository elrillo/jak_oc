"use client"

import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts"
import { CHART_TOOLTIP_STYLE } from "@/components/ChartContainer"

interface RadarDataPoint {
  category: string
  value: number
  /** Para overlay de comparación */
  valueB?: number
}

interface DeputyRadarProps {
  data: RadarDataPoint[]
  /** Segundo dataset para comparación (se mergea por category) */
  dataB?: RadarDataPoint[]
  /** Nombre del primer perfil (default: "Kast") */
  labelA?: string
  /** Nombre del segundo perfil si es comparación */
  labelB?: string
  /** Color del primer perfil */
  colorA?: string
  /** Color del segundo perfil */
  colorB?: string
  className?: string
}

/**
 * Radar Chart para perfil temático de un diputado.
 * Ejes = categorías temáticas, valores = % de mociones.
 * Soporta overlay para comparación de 2 diputados.
 */
export function DeputyRadar({
  data,
  dataB,
  labelA = "Kast",
  labelB,
  colorA = "#c0392b",
  colorB = "#3498db",
  className = "",
}: DeputyRadarProps) {
  // Merge dataB into data if provided
  const mergedData = dataB
    ? data.map(d => {
        const match = dataB.find(b => b.category === d.category)
        return { ...d, valueB: match?.value ?? d.valueB ?? 0 }
      })
    : data

  const hasComparison = labelB && mergedData.some((d) => d.valueB != null)

  // Truncar labels largos para mobile
  const truncatedData = mergedData.map((d) => ({
    ...d,
    shortCategory: d.category.length > 15 ? d.category.slice(0, 13) + "…" : d.category,
  }))

  return (
    <div className={`w-full ${className}`}>
      {/* Mobile */}
      <div className="block sm:hidden">
        <ResponsiveContainer width="100%" height={280}>
          <RadarChart data={truncatedData} cx="50%" cy="50%" outerRadius="65%">
            <PolarGrid stroke="rgba(255,255,255,0.1)" />
            <PolarAngleAxis
              dataKey="shortCategory"
              tick={{ fill: "#b0b0b0", fontSize: 8 }}
            />
            <PolarRadiusAxis
              tick={{ fill: "#666", fontSize: 8 }}
              axisLine={false}
            />
            <Radar
              name={labelA}
              dataKey="value"
              stroke={colorA}
              fill={colorA}
              fillOpacity={0.2}
              strokeWidth={2}
            />
            {hasComparison && (
              <Radar
                name={labelB}
                dataKey="valueB"
                stroke={colorB}
                fill={colorB}
                fillOpacity={0.15}
                strokeWidth={2}
              />
            )}
            <Tooltip {...CHART_TOOLTIP_STYLE} />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Desktop */}
      <div className="hidden sm:block">
        <ResponsiveContainer width="100%" height={400}>
          <RadarChart data={truncatedData} cx="50%" cy="50%" outerRadius="70%">
            <PolarGrid stroke="rgba(255,255,255,0.1)" />
            <PolarAngleAxis
              dataKey="category"
              tick={{ fill: "#b0b0b0", fontSize: 11 }}
            />
            <PolarRadiusAxis
              tick={{ fill: "#666", fontSize: 10 }}
              axisLine={false}
            />
            <Radar
              name={labelA}
              dataKey="value"
              stroke={colorA}
              fill={colorA}
              fillOpacity={0.2}
              strokeWidth={2}
            />
            {hasComparison && (
              <Radar
                name={labelB}
                dataKey="valueB"
                stroke={colorB}
                fill={colorB}
                fillOpacity={0.15}
                strokeWidth={2}
              />
            )}
            <Tooltip {...CHART_TOOLTIP_STYLE} />
            {hasComparison && (
              <Legend
                wrapperStyle={{ fontSize: 12, color: "#b0b0b0" }}
              />
            )}
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
