import type React from "react"
import type { Metadata } from "next"
import { Fira_Sans, Overpass } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import "./globals.css"
import { Navbar } from "@/components/navbar"
import { Footer } from "@/components/footer"
import { Suspense } from "react"

const firaSans = Fira_Sans({
  subsets: ["latin"],
  weight: ["400", "700", "900"],
  variable: "--font-heading",
  display: "swap",
})

const overpass = Overpass({
  subsets: ["latin"],
  weight: ["400", "700"],
  style: ["normal", "italic"],
  variable: "--font-sans",
  display: "swap",
})

export const metadata: Metadata = {
  title: "BREATHSAFE – Personal Air Health Assistant",
  description:
    "Know your air. Protect your health. Using NASA open data to help you stay safe from invisible air pollution.",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${firaSans.variable} ${overpass.variable} font-sans antialiased`}>
        <Suspense fallback={<div>Loading...</div>}>
          <Navbar />
          <main className="min-h-screen">{children}</main>
          <Footer />
        </Suspense>
        <Analytics />
      </body>
    </html>
  )
}
