"use client"

import { useState, useMemo } from "react"

interface Column<T> {
  key: string
  label: string
  /** Prioridad para mobile: 1 = siempre visible, 2 = oculto en mobile, 3 = solo desktop */
  priority?: 1 | 2 | 3
  render?: (row: T) => React.ReactNode
  className?: string
  sortable?: boolean
}

interface DataTableProps<T> {
  data: T[]
  columns: Column<T>[]
  /** Cuántas filas mostrar por página (default: 50) */
  pageSize?: number
  /** Usar modo card en mobile (default: true) */
  mobileCards?: boolean
  /** Key único por fila */
  rowKey: (row: T) => string
  /** Clase CSS para la fila hover */
  rowClassName?: string
}

export function DataTable<T extends Record<string, unknown>>({
  data,
  columns,
  pageSize = 50,
  mobileCards = true,
  rowKey,
  rowClassName = "hover:bg-white/5",
}: DataTableProps<T>) {
  const [page, setPage] = useState(0)
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortAsc, setSortAsc] = useState(true)

  const sorted = useMemo(() => {
    if (!sortKey) return data
    return [...data].sort((a, b) => {
      const va = a[sortKey]
      const vb = b[sortKey]
      if (va == null && vb == null) return 0
      if (va == null) return 1
      if (vb == null) return -1
      const cmp = String(va).localeCompare(String(vb), undefined, { numeric: true })
      return sortAsc ? cmp : -cmp
    })
  }, [data, sortKey, sortAsc])

  const totalPages = Math.ceil(sorted.length / pageSize)
  const paged = sorted.slice(page * pageSize, (page + 1) * pageSize)

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortAsc(!sortAsc)
    } else {
      setSortKey(key)
      setSortAsc(true)
    }
    setPage(0)
  }

  const priorityCols = (p: number) => columns.filter((c) => (c.priority || 1) <= p)

  return (
    <div>
      {/* Mobile: Card layout */}
      {mobileCards && (
        <div className="md:hidden space-y-3">
          {paged.map((row) => (
            <div
              key={rowKey(row)}
              className="bg-white/[0.02] border border-white/5 rounded-lg p-4 space-y-2"
            >
              {columns.filter((c) => (c.priority || 1) <= 2).map((col) => (
                <div key={col.key} className="flex justify-between items-start gap-2">
                  <span className="text-[10px] uppercase tracking-wider text-muted-foreground shrink-0">
                    {col.label}
                  </span>
                  <span className={`text-sm text-right ${col.className || ""}`}>
                    {col.render
                      ? col.render(row)
                      : String(row[col.key] ?? "N/A")}
                  </span>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}

      {/* Desktop: Table layout */}
      <div className={mobileCards ? "hidden md:block" : "block"}>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10 text-left text-muted-foreground uppercase text-xs tracking-wider">
                {columns.map((col) => (
                  <th
                    key={col.key}
                    className={`py-3 px-2 ${col.sortable !== false ? "cursor-pointer select-none hover:text-white transition-colors" : ""} ${
                      (col.priority || 1) >= 3 ? "hidden lg:table-cell" : ""
                    }`}
                    onClick={() => col.sortable !== false && handleSort(col.key)}
                  >
                    <span className="inline-flex items-center gap-1">
                      {col.label}
                      {sortKey === col.key && (
                        <span className="text-[#c0392b]">{sortAsc ? "↑" : "↓"}</span>
                      )}
                    </span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {paged.map((row) => (
                <tr
                  key={rowKey(row)}
                  className={`border-b border-white/5 transition-colors ${rowClassName}`}
                >
                  {columns.map((col) => (
                    <td
                      key={col.key}
                      className={`py-2.5 px-2 ${col.className || ""} ${
                        (col.priority || 1) >= 3 ? "hidden lg:table-cell" : ""
                      }`}
                    >
                      {col.render
                        ? col.render(row)
                        : String(row[col.key] ?? "N/A")}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4 px-1">
          <p className="text-muted-foreground text-xs">
            {page * pageSize + 1}-{Math.min((page + 1) * pageSize, sorted.length)} de {sorted.length}
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
              className="px-3 py-1.5 text-xs rounded-lg bg-white/5 hover:bg-white/10 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              Anterior
            </button>
            <button
              onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
              disabled={page >= totalPages - 1}
              className="px-3 py-1.5 text-xs rounded-lg bg-white/5 hover:bg-white/10 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              Siguiente
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
