"use client"

import { motion } from "framer-motion"
import type { LucideIcon } from "lucide-react"

interface StatCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon?: LucideIcon
  accentColor?: string
  trend?: {
    value: number
    label?: string
  }
}

export function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  accentColor = "#c0392b",
  trend,
}: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="relative text-center py-4 sm:py-6 px-3 rounded-xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-colors"
    >
      {Icon && (
        <div className="flex justify-center mb-3">
          <Icon size={20} style={{ color: accentColor }} className="opacity-60" />
        </div>
      )}

      <p className="text-[10px] sm:text-xs uppercase tracking-[2px] text-muted-foreground mb-2">
        {title}
      </p>

      <p className="text-3xl sm:text-4xl lg:text-5xl font-serif font-bold text-white drop-shadow-md leading-none">
        {value}
      </p>

      {trend && (
        <div className="flex items-center justify-center gap-1 mt-2">
          <span
            className={`text-xs font-medium ${
              trend.value > 0 ? "text-[#2ecc71]" : trend.value < 0 ? "text-[#c0392b]" : "text-muted-foreground"
            }`}
          >
            {trend.value > 0 ? "+" : ""}
            {trend.value}%
          </span>
          {trend.label && (
            <span className="text-[10px] text-muted-foreground">{trend.label}</span>
          )}
        </div>
      )}

      {subtitle && (
        <p className="text-[10px] sm:text-xs text-muted-foreground mt-2 sm:mt-3 uppercase tracking-wider">
          {subtitle}
        </p>
      )}
    </motion.div>
  )
}
