"use client"

import { ReactNode } from "react"
import { DashboardProvider } from "./DashboardProvider"
import { ScrollToTop } from "./ScrollToTop"

export function ClientProviders({ children }: { children: ReactNode }) {
  return (
    <DashboardProvider>
      {children}
      <ScrollToTop />
    </DashboardProvider>
  )
}
