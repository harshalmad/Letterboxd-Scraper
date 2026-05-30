import type { Metadata } from "next"
import Link from "next/link"
import { notFound } from "next/navigation"
import FilmList from "@/components/FilmList"
import { getAllYears, getYearData } from "@/lib/data"

type YearPageProps = {
  params: Promise<{ year: string }>
}

export async function generateStaticParams() {
  return getAllYears().map((year) => ({ year: String(year) }))
}

export async function generateMetadata({ params }: YearPageProps): Promise<Metadata> {
  const { year } = await params
  return {
    title: `${year} Top Films`,
    description: `Top 50 most popular Letterboxd films released in ${year}.`,
  }
}

export default async function YearPage({ params }: YearPageProps) {
  const { year: yearParam } = await params
  const year = Number(yearParam)

  if (!Number.isInteger(year)) {
    notFound()
  }

  const data = getYearData(year)
  if (!data) {
    notFound()
  }

  return (
    <div>
      <div className="mb-8">
        <Link
          href="/"
          className="text-sm text-[var(--muted)] transition hover:text-[var(--accent)] focus:outline-none focus-visible:underline"
        >
          ← All years
        </Link>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-[var(--foreground)]">
          {year}
        </h1>
        <p className="mt-2 text-sm text-[var(--muted)]">
          Top {data.films.length} films released in {year}, ranked by Letterboxd
          year-to-date popularity.
        </p>
        <a
          href={data.sourceUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-3 inline-flex text-sm text-[var(--accent)] hover:underline focus:outline-none focus-visible:underline"
        >
          View source on Letterboxd
        </a>
      </div>

      <FilmList films={data.films} year={year} />
    </div>
  )
}
