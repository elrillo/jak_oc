"use client"

import { ReactNode } from "react"
import { DashboardProvider } from "./DashboardProvider"

export function ClientProviders({ children }: { children: ReactNode }) {
  return <DashboardProvider>{children}</DashboardProvider>
}
