import type { Metadata } from "next"
import { Geist, Geist_Mono } from "next/font/google"
import SiteHeader from "@/components/SiteHeader"
import LastUpdatedFooter from "@/components/LastUpdatedFooter"
import { getManifest } from "@/lib/data"
import "./globals.css"

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
})

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
})

export const metadata: Metadata = {
  title: {
    default: "Letterboxd Popular Films",
    template: "%s · Letterboxd Popular Films",
  },
  description:
    "Top 50 most popular Letterboxd films for each release year (1977–2026), ranked by year-to-date popularity.",
  openGraph: {
    title: "Letterboxd Popular Films",
    description:
      "Browse the 50 most popular Letterboxd films for every release year from 1977 to 2026.",
    type: "website",
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  const manifest = getManifest()

  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col bg-[var(--background)] text-[var(--foreground)]">
        <SiteHeader />
        <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8 sm:px-6 sm:py-10">
          {children}
        </main>
        <LastUpdatedFooter lastUpdatedUtc={manifest.lastUpdatedUtc} />
      </body>
    </html>
  )
}
