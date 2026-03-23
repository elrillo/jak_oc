import type { Metadata } from "next"
import Script from "next/script"
import Image from "next/image"
import { Playfair_Display, Merriweather } from "next/font/google"
import "./globals.css"
import Link from "next/link"
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
      {/* Google Tag Manager */}
      <Script
        id="gtm-script"
        strategy="afterInteractive"
        dangerouslySetInnerHTML={{
          __html: `(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-TGX4SGVS');`,
        }}
      />
      {/* Google Analytics GA4 */}
      <Script
        src="https://www.googletagmanager.com/gtag/js?id=G-JPFZEFXWKZ"
        strategy="afterInteractive"
      />
      <Script
        id="ga4-config"
        strategy="afterInteractive"
        dangerouslySetInnerHTML={{
          __html: `window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-JPFZEFXWKZ');`,
        }}
      />
      <body
        className={`${playfair.variable} ${merriweather.variable} antialiased min-h-screen`}
      >
        {/* Google Tag Manager (noscript) */}
        <noscript>
          <iframe
            src="https://www.googletagmanager.com/ns.html?id=GTM-TGX4SGVS"
            height="0"
            width="0"
            style={{ display: "none", visibility: "hidden" }}
          />
        </noscript>

        {/* Hero Banner */}
        <header className="text-center py-16 px-4">
          <div className="flex justify-center mb-5">
            <Image
              src="/logo-observatorio.png"
              alt="Observatorio Congreso"
              width={180}
              height={60}
              className="h-[60px] w-auto object-contain"
              priority
            />
          </div>
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
              <h4 className="font-serif text-lg mb-5 border-b-2 border-[#6e20d3] inline-block pb-1">
                Conecta
              </h4>
              <p className="text-muted-foreground text-sm mb-5">
                Mantente informado con nuestros análisis exclusivos.
              </p>
              {/* Iconos RRSS */}
              <div className="flex gap-3 mb-5">
                {[
                  { href: "https://www.facebook.com/observatoriocongreso", icon: "M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" },
                  { href: "https://www.instagram.com/observatorio.congreso/", icon: "M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z" },
                  { href: "https://whatsapp.com/channel/0029Va9CBjgAe5VuSNawAl1c", icon: "M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" },
                  { href: "https://x.com/observacongress", icon: "M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" },
                  { href: "https://www.tiktok.com/@observatorio_congreso", icon: "M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1V9.01a6.27 6.27 0 00-.79-.05 6.34 6.34 0 00-6.34 6.34 6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.34-6.34V8.75a8.18 8.18 0 004.76 1.52V6.84a4.83 4.83 0 01-1-.15z" },
                  { href: "https://cl.linkedin.com/company/observatorio-congreso", icon: "M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" },
                  { href: "mailto:estudios@fundacionbalmaceda.cl", icon: "M1.5 8.67v8.58a3 3 0 003 3h15a3 3 0 003-3V8.67l-8.928 5.493a3 3 0 01-3.144 0L1.5 8.67z M22.5 6.908V6.75a3 3 0 00-3-3h-15a3 3 0 00-3 3v.158l9.714 5.978a1.5 1.5 0 001.572 0L22.5 6.908z" },
                ].map(({ href, icon }, i) => (
                  <a
                    key={i}
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center hover:bg-[#6e20d3] hover:-translate-y-0.5 transition-all duration-300"
                  >
                    <svg className="w-4 h-4 fill-white" viewBox="0 0 24 24"><path d={icon} /></svg>
                  </a>
                ))}
              </div>
              <a href="https://observatoriocongreso.cl/newsletter/" target="_blank" rel="noopener noreferrer" className="inline-block bg-white text-black px-5 py-2.5 rounded-full text-sm font-bold hover:bg-gray-200 transition-colors">
                Suscribirse al Bolet&iacute;n
              </a>
            </div>

            {/* Columna 2: Explora */}
            <div className="min-w-[200px]">
              <h4 className="font-serif text-lg mb-5 border-b-2 border-[#6e20d3] inline-block pb-1">
                Explora
              </h4>
              <div className="flex flex-col gap-3">
                <a
                  href="https://observatoriocongreso.cl/notas/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground text-sm hover:text-white hover:translate-x-1 transition-all duration-300"
                >
                  Notas
                </a>
                <a
                  href="https://observatoriocongreso.cl/equipo-2/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground text-sm hover:text-white hover:translate-x-1 transition-all duration-300"
                >
                  Sobre Nosotros
                </a>
                {[
                  { label: "Metodología de Datos", href: "/metodologia" },
                  { label: "Preguntas Frecuentes", href: "/preguntas-frecuentes" },
                  { label: "Términos de Uso", href: "/terminos" },
                ].map(({ label, href }) => (
                  <Link
                    key={label}
                    href={href}
                    className="text-muted-foreground text-sm hover:text-white hover:translate-x-1 transition-all duration-300"
                  >
                    {label}
                  </Link>
                ))}
                <a
                  href="https://observatoriocongreso.cl/jak/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground text-sm hover:text-white hover:translate-x-1 transition-all duration-300"
                >
                  Descarga
                </a>
              </div>
            </div>

            {/* Columna 3: Observatorio Congreso */}
            <div className="min-w-[280px] flex-1">
              <h4 className="font-serif text-lg mb-5 border-b-2 border-[#6e20d3] inline-block pb-1">
                Observatorio Congreso
              </h4>
              <p className="text-muted-foreground text-sm leading-relaxed">
                &copy; 2026 Reservados todos los derechos.
                <br /><br />
                Plataforma de an&aacute;lisis ciudadano basada en datos p&uacute;blicos del
                Sistema de Informaci&oacute;n Legislativa (SIL).
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
