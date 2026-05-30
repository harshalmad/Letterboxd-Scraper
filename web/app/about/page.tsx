import type { Metadata } from "next"
import Link from "next/link"

export const metadata: Metadata = {
  title: "About",
  description: "Methodology and disclaimer for the Letterboxd Popular Films dataset.",
}

export default function AboutPage() {
  return (
    <article className="max-w-3xl">
      <h1 className="text-3xl font-semibold tracking-tight text-[var(--foreground)]">
        About this project
      </h1>
      <p className="mt-4 text-base leading-7 text-[var(--muted)]">
        This site publishes the top 50 most popular Letterboxd films for each
        release year from 1977 to 2026. Data is scraped from Letterboxd&apos;s
        public discovery pages and refreshed automatically every week.
      </p>

      <section className="mt-10 space-y-4">
        <h2 className="text-xl font-semibold text-[var(--foreground)]">Methodology</h2>
        <p className="leading-7 text-[var(--muted)]">
          For each release year, films are ranked using Letterboxd&apos;s{" "}
          <strong className="font-medium text-[var(--foreground)]">this year</strong>{" "}
          popularity window. That means older releases (for example, a 1977 film)
          are ranked by how popular they are during the current calendar year—not
          how popular they were when they originally released.
        </p>
        <p className="leading-7 text-[var(--muted)]">
          Source URL pattern:{" "}
          <code className="rounded bg-[var(--surface)] px-2 py-1 text-sm text-[var(--foreground)]">
            https://letterboxd.com/films/popular/this/year/year/YEAR/size/large/page/1/
          </code>
        </p>
      </section>

      <section className="mt-10 space-y-4">
        <h2 className="text-xl font-semibold text-[var(--foreground)]">Updates</h2>
        <ul className="list-disc space-y-2 pl-5 leading-7 text-[var(--muted)]">
          <li>GitHub Actions runs the scraper every Sunday at 06:00 UTC.</li>
          <li>Developers can also run the scraper manually from the terminal.</li>
          <li>The footer on every page shows when data was last refreshed in your local timezone.</li>
        </ul>
      </section>

      <section className="mt-10 space-y-4">
        <h2 className="text-xl font-semibold text-[var(--foreground)]">Disclaimer</h2>
        <p className="leading-7 text-[var(--muted)]">
          This project is not affiliated with, endorsed by, or sponsored by
          Letterboxd. Film titles and links point to letterboxd.com. Please
          respect Letterboxd&apos;s terms of service and rate limits.
        </p>
      </section>

      <div className="mt-10 flex flex-wrap gap-3">
        <a
          href="https://github.com/harshalmad/Letterboxd-Scraper"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex rounded-lg border border-[var(--border)] px-4 py-2 text-sm text-[var(--foreground)] transition hover:border-[var(--accent)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)]"
        >
          View on GitHub
        </a>
        <Link
          href="/"
          className="inline-flex rounded-lg bg-[var(--accent)] px-4 py-2 text-sm font-medium text-[#041018] transition hover:brightness-110 focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)]"
        >
          Browse years
        </Link>
      </div>
    </article>
  )
}
