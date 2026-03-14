"use client"

import { motion } from "framer-motion"
import { ReactNode } from "react"

type Variant = "split" | "full-width" | "card"

interface StorySectionProps {
  title: string
  description: string
  chart: ReactNode
  /** Si true, texto a la izquierda y gráfico a la derecha. Si false, al revés. */
  textLeft?: boolean
  /** Variante de layout (default: "split") */
  variant?: Variant
}

/**
 * Sección de storytelling: texto narrativo + visualización.
 * Layout alternado para crear una narrativa visual.
 * Mobile: siempre apilado verticalmente (texto arriba, chart abajo).
 */
export function StorySection({
  title,
  description,
  chart,
  textLeft = true,
  variant = "split",
}: StorySectionProps) {
  const textBlock = (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6 }}
    >
      <h3 className="text-xl sm:text-2xl font-serif font-semibold mb-3 sm:mb-4">{title}</h3>
      <p className="text-sm sm:text-base text-muted-foreground leading-relaxed whitespace-pre-line">
        {description}
      </p>
    </motion.div>
  )

  const chartBlock = (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6, delay: 0.1 }}
    >
      {chart}
    </motion.div>
  )

  if (variant === "full-width") {
    return (
      <section className="my-12 sm:my-16">
        <div className="mb-6 sm:mb-8">{textBlock}</div>
        {chartBlock}
      </section>
    )
  }

  if (variant === "card") {
    return (
      <section className="my-12 sm:my-16 bg-white/[0.02] border border-white/5 rounded-xl p-5 sm:p-8">
        <div className="mb-6">{textBlock}</div>
        {chartBlock}
      </section>
    )
  }

  // Default: split layout (stacked on mobile, side-by-side on desktop)
  return (
    <section className="grid grid-cols-1 lg:grid-cols-5 gap-6 lg:gap-12 items-center my-12 sm:my-16">
      {textLeft ? (
        <>
          <div className="lg:col-span-2">{textBlock}</div>
          <div className="lg:col-span-3">{chartBlock}</div>
        </>
      ) : (
        <>
          <div className="lg:col-span-3 order-2 lg:order-1">{chartBlock}</div>
          <div className="lg:col-span-2 order-1 lg:order-2">{textBlock}</div>
        </>
      )}
    </section>
  )
}
