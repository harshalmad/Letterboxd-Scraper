import Link from "next/link"

type YearSelectorProps = {
  years: number[]
}

export default function YearSelector({ years }: YearSelectorProps) {
  return (
    <section aria-labelledby="years-heading">
      <div className="mb-6 flex items-end justify-between gap-4">
        <div>
          <h2 id="years-heading" className="text-2xl font-semibold text-[var(--foreground)]">
            Browse by year
          </h2>
          <p className="mt-1 text-sm text-[var(--muted)]">
            {years.length} release years · 50 films each
          </p>
        </div>
      </div>

      <ul className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
        {years.map((year) => (
          <li key={year}>
            <Link
              href={`/year/${year}`}
              className="group flex flex-col rounded-xl border border-[var(--border)] bg-[var(--surface)] px-4 py-5 transition hover:border-[var(--accent)] hover:bg-[var(--surface-hover)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)]"
              aria-label={`View top films from ${year}`}
            >
              <span className="text-2xl font-semibold text-[var(--foreground)] group-hover:text-[var(--accent)]">
                {year}
              </span>
              <span className="mt-1 text-xs text-[var(--muted)]">50 films</span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  )
}
