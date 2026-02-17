import type { Metadata } from "next"
import { Playfair_Display, Merriweather } from "next/font/google"
import "./globals.css"
import { Navigation } from "@/components/Navigation"
import { ClientProviders } from "@/components/ClientProviders"

const playfair = Playfair_Display({
  variable: "--font-playfair",
  subsets: ["latin"],
  weight: ["400", "600", "700"],
  style: ["normal", "italic"],
})

const merriweather = Merriweather({
  variable: "--font-merriweather",
  subsets: ["latin"],
  weight: ["300", "400", "700"],
})

export const metadata: Metadata = {
  title: "Observatorio Congreso | José Antonio Kast",
  description:
    "Plataforma de análisis legislativo: 255 mociones parlamentarias de José Antonio Kast (2002-2018). Visualización interactiva de datos del Congreso Nacional de Chile.",
  keywords: [
    "Kast",
    "legislativo",
    "Chile",
    "Congreso",
    "mociones",
    "análisis parlamentario",
  ],
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="es" className="dark">
      <body
        className={`${playfair.variable} ${merriweather.variable} antialiased min-h-screen`}
      >
        {/* Hero Banner */}
        <header className="text-center py-16 px-4">
          <p className="text-muted-foreground text-sm uppercase tracking-[3px] font-serif italic mb-4">
            Observatorio Congreso
          </p>
          <h1 className="text-5xl md:text-6xl font-bold tracking-wide font-serif text-white drop-shadow-lg">
            JOSE ANTONIO KAST
          </h1>
          <div className="flex justify-center gap-3 mt-4">
            <span className="bg-white/10 px-4 py-1.5 rounded-full text-xs tracking-wider border border-white/20">
              DIPUTADO 2002-2018
            </span>
          </div>
        </header>

        {/* Navegación */}
        <Navigation />

        {/* Contenido principal */}
        <main className="max-w-7xl mx-auto px-4 pb-20">
          <ClientProviders>
            {children}
          </ClientProviders>
        </main>

        {/* Footer completo - 3 columnas como el original de app.py */}
        <footer className="border-t border-white/5 mt-20 bg-[#0F0F0F]">
          <div className="max-w-7xl mx-auto flex flex-wrap justify-between gap-10 px-8 py-14">
            {/* Columna 1: Conecta */}
            <div className="min-w-[280px] flex-1">
              <h4 className="font-serif text-lg mb-5 border-b-2 border-[#c0392b] inline-block pb-1">
                Conecta
              </h4>
              <p className="text-muted-foreground text-sm mb-5">
                Mantente informado con nuestros análisis exclusivos.
              </p>
              {/* Iconos RRSS */}
              <div className="flex gap-3 mb-5">
                {[
                  { href: "https://twitter.com", icon: "M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" },
                  { href: "https://linkedin.com", icon: "M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" },
                  { href: "https://instagram.com", icon: "M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z" },
                  { href: "mailto:contacto@observatoriocongreso.cl", icon: "M1.5 8.67v8.58a3 3 0 003 3h15a3 3 0 003-3V8.67l-8.928 5.493a3 3 0 01-3.144 0L1.5 8.67z M22.5 6.908V6.75a3 3 0 00-3-3h-15a3 3 0 00-3 3v.158l9.714 5.978a1.5 1.5 0 001.572 0L22.5 6.908z" },
                ].map(({ href, icon }, i) => (
                  <a
                    key={i}
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center hover:bg-[#c0392b] hover:-translate-y-0.5 transition-all duration-300"
                  >
                    <svg className="w-4 h-4 fill-white" viewBox="0 0 24 24"><path d={icon} /></svg>
                  </a>
                ))}
              </div>
              <a href="#" className="inline-block bg-white text-black px-5 py-2.5 rounded-full text-sm font-bold hover:bg-gray-200 transition-colors">
                Suscribirse al Bolet&iacute;n
              </a>
            </div>

            {/* Columna 2: Explora */}
            <div className="min-w-[200px]">
              <h4 className="font-serif text-lg mb-5 border-b-2 border-[#c0392b] inline-block pb-1">
                Explora
              </h4>
              <div className="flex flex-col gap-3">
                {["Sobre Nosotros", "Metodología de Datos", "Términos de Uso", "Política de Privacidad"].map((link) => (
                  <a
                    key={link}
                    href="#"
                    className="text-muted-foreground text-sm hover:text-white hover:translate-x-1 transition-all duration-300"
                  >
                    {link}
                  </a>
                ))}
              </div>
            </div>

            {/* Columna 3: Observatorio Congreso */}
            <div className="min-w-[280px] flex-1">
              <h4 className="font-serif text-lg mb-5 border-b-2 border-[#c0392b] inline-block pb-1">
                Observatorio Congreso
              </h4>
              <p className="text-muted-foreground text-sm leading-relaxed">
                &copy; 2026 Reservados todos los derechos.
                <br /><br />
                Plataforma de an&aacute;lisis ciudadano basada en datos p&uacute;blicos de la
                Biblioteca del Congreso Nacional de Chile.
                <br />
                Dise&ntilde;ado con rigor y transparencia.
              </p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  )
}
