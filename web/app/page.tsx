import Link from "next/link"
import YearSelector from "@/components/YearSelector"
import { getAllYears, getManifest } from "@/lib/data"

export default function HomePage() {
  const years = getAllYears()
  const manifest = getManifest()

  return (
    <div>
      <section className="mb-10 rounded-2xl border border-[var(--border)] bg-[var(--surface)] px-6 py-8 sm:px-8">
        <p className="mb-2 text-sm font-medium uppercase tracking-[0.2em] text-[var(--accent)]">
          Year-to-date popularity
        </p>
        <h1 className="max-w-3xl text-3xl font-semibold tracking-tight text-[var(--foreground)] sm:text-4xl">
          The 50 most popular Letterboxd films for every release year
        </h1>
        <p className="mt-4 max-w-2xl text-base leading-7 text-[var(--muted)]">
          Explore {manifest.filmCount.toLocaleString()} films across{" "}
          {manifest.years.length} release years ({manifest.startYear}–
          {manifest.endYear}). Rankings reflect Letterboxd&apos;s{" "}
          <strong className="font-medium text-[var(--foreground)]">this year</strong>{" "}
          popularity window, filtered by release year.
        </p>
        <div className="mt-6">
          <Link
            href="/about"
            className="inline-flex rounded-lg bg-[var(--accent)] px-4 py-2 text-sm font-medium text-[#041018] transition hover:brightness-110 focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--surface)]"
          >
            How this data works
          </Link>
        </div>
      </section>

      <YearSelector years={years} />
    </div>
  )
}
