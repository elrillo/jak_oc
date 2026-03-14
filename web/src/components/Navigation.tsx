"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  BarChart3,
  Calendar,
  Star,
  Building2,
  Network,
  Hourglass,
  Scale,
  Search,
  Menu,
  X,
  Clock,
  GitBranch,
  Users,
} from "lucide-react"
import {
  Sheet,
  SheetTrigger,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetClose,
} from "@/components/ui/sheet"

const NAV_GROUPS = [
  {
    label: "Análisis",
    items: [
      { href: "/", label: "General", icon: BarChart3 },
      { href: "/periodos", label: "Periodos", icon: Calendar },
      { href: "/estado", label: "Estado", icon: Hourglass },
      { href: "/comisiones", label: "Comisiones", icon: Building2 },
      { href: "/leyes", label: "Leyes", icon: Scale },
    ],
  },
  {
    label: "Red",
    items: [
      { href: "/alianzas", label: "Alianzas", icon: Network },
      { href: "/red", label: "Grafo", icon: GitBranch },
      { href: "/comparador", label: "Comparador", icon: Users },
    ],
  },
  {
    label: "Herramientas",
    items: [
      { href: "/timeline", label: "Timeline", icon: Clock },
      { href: "/explorador", label: "Explorador", icon: Search },
    ],
  },
  {
    label: "Destacados",
    items: [
      { href: "/destacados", label: "Destacados", icon: Star },
    ],
  },
]

const ALL_NAV_ITEMS = NAV_GROUPS.flatMap((g) => g.items)

export function Navigation() {
  const pathname = usePathname()
  const [open, setOpen] = useState(false)

  const currentPage = ALL_NAV_ITEMS.find((item) => item.href === pathname)

  return (
    <>
      {/* Mobile Navigation */}
      <nav className="md:hidden sticky top-0 z-40 bg-[#0c0d0e]/95 backdrop-blur-sm border-b border-white/5">
        <div className="flex items-center justify-between px-4 py-3">
          {/* Current page indicator */}
          <div className="flex items-center gap-2 text-white">
            {currentPage && (
              <>
                <currentPage.icon size={18} className="text-[#c0392b]" />
                <span className="text-sm font-serif font-semibold uppercase tracking-wider">
                  {currentPage.label}
                </span>
              </>
            )}
          </div>

          {/* Hamburger button */}
          <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger asChild>
              <button
                className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                aria-label="Abrir menú de navegación"
              >
                <Menu size={22} className="text-white" />
              </button>
            </SheetTrigger>

            <SheetContent
              side="left"
              className="w-[280px] bg-[#0c0d0e] border-white/10 p-0"
              showCloseButton={false}
            >
              <SheetHeader className="px-6 pt-6 pb-4 border-b border-white/5">
                <div className="flex items-center justify-between">
                  <SheetTitle className="font-serif text-white text-lg tracking-wide">
                    Observatorio
                  </SheetTitle>
                  <SheetClose asChild>
                    <button
                      className="p-1.5 rounded-lg hover:bg-white/10 transition-colors"
                      aria-label="Cerrar menú"
                    >
                      <X size={18} className="text-white/60" />
                    </button>
                  </SheetClose>
                </div>
              </SheetHeader>

              <div className="py-4 overflow-y-auto">
                {NAV_GROUPS.map((group) => (
                  <div key={group.label} className="mb-2">
                    <p className="px-6 py-2 text-[10px] uppercase tracking-[3px] text-white/30 font-semibold">
                      {group.label}
                    </p>
                    {group.items.map(({ href, label, icon: Icon }) => {
                      const isActive = pathname === href
                      return (
                        <Link
                          key={href}
                          href={href}
                          onClick={() => setOpen(false)}
                          className={`flex items-center gap-3 px-6 py-3 transition-all duration-200
                            ${isActive
                              ? "bg-white/5 text-white border-l-2 border-[#c0392b]"
                              : "text-white/50 hover:text-white hover:bg-white/[0.03] border-l-2 border-transparent"
                            }`}
                        >
                          <Icon
                            size={18}
                            className={isActive ? "text-[#c0392b]" : ""}
                          />
                          <span className="text-sm font-serif font-medium tracking-wide">
                            {label}
                          </span>
                        </Link>
                      )
                    })}
                  </div>
                ))}
              </div>

              {/* Footer del drawer */}
              <div className="mt-auto px-6 py-4 border-t border-white/5">
                <p className="text-[10px] text-white/20 uppercase tracking-wider">
                  Observatorio Congreso v2.0
                </p>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </nav>

      {/* Desktop Navigation */}
      <nav className="hidden md:flex justify-center gap-1 lg:gap-6 px-4 py-6 border-b border-white/5 mb-10">
        {ALL_NAV_ITEMS.map(({ href, label, icon: Icon }) => {
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
                className={`transition-all duration-300 ${isActive ? "text-[#c0392b] scale-110" : ""}`}
              />
              <span>{label}</span>
            </Link>
          )
        })}
      </nav>
    </>
  )
}
