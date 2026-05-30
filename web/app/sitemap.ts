import type { MetadataRoute } from "next"
import { getAllYears } from "@/lib/data"

export default function sitemap(): MetadataRoute.Sitemap {
  const years = getAllYears()
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "https://letterboxd-scraper.vercel.app"

  return [
    {
      url: baseUrl,
      changeFrequency: "weekly",
      priority: 1,
    },
    {
      url: `${baseUrl}/about`,
      changeFrequency: "monthly",
      priority: 0.5,
    },
    ...years.map((year) => ({
      url: `${baseUrl}/year/${year}`,
      changeFrequency: "weekly" as const,
      priority: 0.8,
    })),
  ]
}
