"use client"

import { createContext, useContext, useEffect, useState, ReactNode } from "react"
import type { DashboardData, ProcessedData, Coautor, Diputado } from "@/lib/types"
import { loadDashboardData, processData } from "@/lib/queries"

interface DashboardContextValue {
  raw: DashboardData | null
  data: ProcessedData | null
  coautores: Coautor[]
  diputados: Diputado[]
  loading: boolean
  error: string | null
}

const DashboardContext = createContext<DashboardContextValue>({
  raw: null,
  data: null,
  coautores: [],
  diputados: [],
  loading: true,
  error: null,
})

export function useDashboard() {
  return useContext(DashboardContext)
}

export function DashboardProvider({ children }: { children: ReactNode }) {
  const [raw, setRaw] = useState<DashboardData | null>(null)
  const [data, setData] = useState<ProcessedData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadDashboardData()
      .then((rawData) => {
        setRaw(rawData)
        setData(processData(rawData))
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Error cargando datos")
      })
      .finally(() => setLoading(false))
  }, [])

  return (
    <DashboardContext.Provider
      value={{
        raw,
        data,
        coautores: raw?.coautores || [],
        diputados: raw?.diputados || [],
        loading,
        error,
      }}
    >
      {children}
    </DashboardContext.Provider>
  )
}

/** Componente de carga y error para envolver páginas */
export function DashboardGate({ children }: { children: ReactNode }) {
  const { loading, error } = useDashboard()

  if (loading) {
    return (
      <div className="flex items-center justify-center py-32">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-white/20 border-t-white rounded-full animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground text-sm uppercase tracking-wider">
            Cargando datos legislativos...
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-32">
        <p className="text-[#c0392b] font-serif text-xl mb-2">Error</p>
        <p className="text-muted-foreground">{error}</p>
      </div>
    )
  }

  return <>{children}</>
}
