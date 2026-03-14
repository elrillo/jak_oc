"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { FileText, Scale, ArrowLeftRight, ChevronDown, ChevronUp, Info } from "lucide-react"
import { PageHeader } from "@/components/PageHeader"
import {
  PARES_DOCUMENTOS,
  type DocumentoLegislativo,
  type SeccionDocumento,
} from "@/lib/documents"

/* ─── Colores por tipo de sección ─── */
const SECCION_STYLES: Record<SeccionDocumento["tipo"], { border: string; bg: string; label: string }> = {
  encabezado: { border: "border-white/10", bg: "bg-white/[0.02]", label: "Encabezado" },
  preambulo: { border: "border-amber-500/20", bg: "bg-amber-500/[0.03]", label: "Preámbulo" },
  articulo: { border: "border-white/10", bg: "bg-transparent", label: "Artículo" },
  transitorio: { border: "border-blue-500/20", bg: "bg-blue-500/[0.03]", label: "Transitorio" },
  cierre: { border: "border-white/5", bg: "bg-white/[0.01]", label: "Cierre" },
}

/* ─── Componente de Sección ─── */
function SeccionCard({ seccion, accentColor }: { seccion: SeccionDocumento; accentColor: string }) {
  const style = SECCION_STYLES[seccion.tipo]

  return (
    <div className={`rounded-lg border ${style.border} ${style.bg} p-4`}>
      {seccion.titulo && (
        <h4
          className="font-serif font-bold text-sm mb-2"
          style={{ color: accentColor }}
        >
          {seccion.titulo}
        </h4>
      )}
      <div className="text-sm leading-relaxed text-white/80 whitespace-pre-line">
        {seccion.contenido}
      </div>
    </div>
  )
}

/* ─── Columna de Documento ─── */
function DocumentColumn({
  doc,
  accentColor,
  icon: Icon,
}: {
  doc: DocumentoLegislativo
  accentColor: string
  icon: typeof FileText
}) {
  return (
    <div className="flex flex-col">
      {/* Header del documento */}
      <div
        className="sticky top-0 z-10 border-b backdrop-blur-md px-4 py-3 rounded-t-xl"
        style={{
          borderColor: `${accentColor}33`,
          backgroundColor: `${accentColor}0D`,
        }}
      >
        <div className="flex items-center gap-2 mb-1">
          <Icon size={16} style={{ color: accentColor }} />
          <span
            className="text-xs font-bold uppercase tracking-wider"
            style={{ color: accentColor }}
          >
            {doc.tipo === "boletin" ? "Moción Original" : "Ley Aprobada"}
          </span>
        </div>
        <h3 className="font-serif font-bold text-base">{doc.titulo}</h3>
        <p className="text-[11px] text-muted-foreground mt-0.5">
          {doc.subtitulo} · {doc.fecha}
        </p>
      </div>

      {/* Secciones */}
      <div className="space-y-3 p-3 flex-1">
        {doc.secciones.map((sec, i) => (
          <SeccionCard key={i} seccion={sec} accentColor={accentColor} />
        ))}
      </div>
    </div>
  )
}

/* ─── Vista Mobile: Tabs ─── */
function MobileView({
  boletin,
  ley,
}: {
  boletin: DocumentoLegislativo
  ley: DocumentoLegislativo
}) {
  const [activeTab, setActiveTab] = useState<"boletin" | "ley">("boletin")

  return (
    <div className="md:hidden">
      {/* Tabs */}
      <div className="flex border border-white/10 rounded-xl overflow-hidden mb-4">
        <button
          onClick={() => setActiveTab("boletin")}
          className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-serif font-semibold transition-all
            ${activeTab === "boletin"
              ? "bg-[#c0392b]/15 text-[#c0392b] border-b-2 border-[#c0392b]"
              : "text-white/40 hover:text-white/60"
            }`}
        >
          <FileText size={14} />
          Moción
        </button>
        <button
          onClick={() => setActiveTab("ley")}
          className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-serif font-semibold transition-all
            ${activeTab === "ley"
              ? "bg-[#2ecc71]/15 text-[#2ecc71] border-b-2 border-[#2ecc71]"
              : "text-white/40 hover:text-white/60"
            }`}
        >
          <Scale size={14} />
          Ley
        </button>
      </div>

      {/* Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.2 }}
          className="border border-white/10 rounded-xl overflow-hidden"
        >
          {activeTab === "boletin" ? (
            <DocumentColumn doc={boletin} accentColor="#c0392b" icon={FileText} />
          ) : (
            <DocumentColumn doc={ley} accentColor="#2ecc71" icon={Scale} />
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  )
}

/* ─── Vista Desktop: Side by Side ─── */
function DesktopView({
  boletin,
  ley,
}: {
  boletin: DocumentoLegislativo
  ley: DocumentoLegislativo
}) {
  return (
    <div className="hidden md:grid md:grid-cols-2 gap-4">
      <div className="border border-white/10 rounded-xl overflow-hidden">
        <DocumentColumn doc={boletin} accentColor="#c0392b" icon={FileText} />
      </div>
      <div className="border border-white/10 rounded-xl overflow-hidden">
        <DocumentColumn doc={ley} accentColor="#2ecc71" icon={Scale} />
      </div>
    </div>
  )
}

/* ─── Página Principal ─── */
export default function VisorPage() {
  const [showResumen, setShowResumen] = useState(true)
  const par = PARES_DOCUMENTOS[0]

  return (
    <div className="max-w-6xl mx-auto px-4 pb-20">
      <PageHeader
        title="Visor de Documentos"
        subtitle="Comparación lado a lado entre la moción original y la ley aprobada."
      />

      {/* Selector de documento (futuro: dropdown si hay más pares) */}
      <div className="bg-white/[0.02] border border-white/10 rounded-xl p-4 mb-6">
        <div className="flex items-start gap-3">
          <ArrowLeftRight size={20} className="text-[#c0392b] mt-0.5 shrink-0" />
          <div className="flex-1">
            <h3 className="font-serif font-semibold text-sm">
              Boletín N° {par.boletin.id} → Ley N° {par.ley.id}
            </h3>
            <p className="text-xs text-muted-foreground mt-1 leading-relaxed line-clamp-2">
              {par.boletin.secciones.find(s => s.titulo === "Materia")?.contenido}
            </p>
          </div>
        </div>
      </div>

      {/* Resumen de cambios */}
      <div className="mb-6">
        <button
          onClick={() => setShowResumen(!showResumen)}
          className="flex items-center gap-2 text-xs text-muted-foreground hover:text-white transition-colors mb-2"
        >
          <Info size={14} />
          <span className="uppercase tracking-wider font-semibold">Resumen de cambios</span>
          {showResumen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>
        <AnimatePresence>
          {showResumen && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              <div className="bg-white/[0.02] border border-white/5 rounded-lg p-4">
                <p className="text-sm text-white/70 leading-relaxed">{par.resumen}</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Leyenda */}
      <div className="flex flex-wrap gap-4 mb-6 justify-center">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-[#c0392b]" />
          <span className="text-[11px] text-muted-foreground">Moción Original (Boletín)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-[#2ecc71]" />
          <span className="text-[11px] text-muted-foreground">Ley Aprobada</span>
        </div>
      </div>

      {/* Comparación */}
      <MobileView boletin={par.boletin} ley={par.ley} />
      <DesktopView boletin={par.boletin} ley={par.ley} />

      {/* Nota al pie */}
      <div className="mt-8 text-center">
        <p className="text-[10px] text-muted-foreground max-w-xl mx-auto leading-relaxed">
          Nota: Los textos se transcriben de los documentos oficiales del Congreso Nacional de Chile.
          La moción fue presentada en {par.boletin.fecha} y la ley fue promulgada el {par.ley.fecha}.
          El texto aprobado difiere sustancialmente de la moción original tras su tramitación parlamentaria.
        </p>
      </div>
    </div>
  )
}
