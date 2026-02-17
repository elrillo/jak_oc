"use client"

import { motion } from "framer-motion"
import { ReactNode } from "react"

interface StorySectionProps {
  title: string
  description: string
  chart: ReactNode
  /** Si true, texto a la izquierda y gráfico a la derecha. Si false, al revés. */
  textLeft?: boolean
}

/**
 * Sección de storytelling: texto narrativo + visualización.
 * Layout alternado para crear una narrativa visual.
 */
export function StorySection({ title, description, chart, textLeft = true }: StorySectionProps) {
  const textBlock = (
    <motion.div
      initial={{ opacity: 0, x: textLeft ? -30 : 30 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6 }}
    >
      <h3 className="text-2xl font-serif font-semibold mb-4">{title}</h3>
      <p className="text-muted-foreground leading-relaxed whitespace-pre-line">
        {description}
      </p>
    </motion.div>
  )

  const chartBlock = (
    <motion.div
      initial={{ opacity: 0, x: textLeft ? 30 : -30 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6, delay: 0.1 }}
    >
      {chart}
    </motion.div>
  )

  return (
    <section className="grid grid-cols-1 lg:grid-cols-5 gap-8 lg:gap-12 items-center my-16">
      {textLeft ? (
        <>
          <div className="lg:col-span-2">{textBlock}</div>
          <div className="lg:col-span-3">{chartBlock}</div>
        </>
      ) : (
        <>
          <div className="lg:col-span-3">{chartBlock}</div>
          <div className="lg:col-span-2">{textBlock}</div>
        </>
      )}
    </section>
  )
}
