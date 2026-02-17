"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { BarChart3, Calendar, Star, Building2, Network, Hourglass, Scale, Search } from "lucide-react"

const NAV_ITEMS = [
  { href: "/", label: "General", icon: BarChart3 },
  { href: "/periodos", label: "Periodos", icon: Calendar },
  { href: "/destacados", label: "Destacados", icon: Star },
  { href: "/comisiones", label: "Comisiones", icon: Building2 },
  { href: "/alianzas", label: "Alianzas", icon: Network },
  { href: "/estado", label: "Estado", icon: Hourglass },
  { href: "/leyes", label: "Leyes", icon: Scale },
  { href: "/explorador", label: "Explorador", icon: Search },
]

export function Navigation() {
  const pathname = usePathname()

  return (
    <nav className="flex justify-center gap-2 md:gap-8 px-4 py-6 border-b border-white/5 mb-10 overflow-x-auto">
      {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
        const isActive = pathname === href
        return (
          <Link
            key={href}
            href={href}
            className={`flex flex-col items-center gap-2 px-3 py-2 text-xs uppercase tracking-widest font-serif font-semibold transition-all duration-300 border-b-2 min-w-[70px]
              ${isActive
                ? "text-white border-white"
                : "text-white/30 border-transparent hover:text-white"
              }`}
          >
            <Icon
              size={24}
              className={`transition-all duration-300 ${isActive ? "text-[#c0392b] scale-110" : "group-hover:-translate-y-0.5"}`}
            />
            <span className="hidden sm:inline">{label}</span>
          </Link>
        )
      })}
    </nav>
  )
}
