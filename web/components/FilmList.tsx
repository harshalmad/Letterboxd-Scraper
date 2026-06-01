"use client"

import { useMemo, useState } from "react"
import type { Film } from "@/lib/data"

type FilmListProps = {
  films: Film[]
  year: number
}

function formatActors(actors: string[] | undefined) {
  if (!actors?.length) {
    return "—"
  }
  return actors.join(", ")
}

export default function FilmList({ films, year }: FilmListProps) {
  const [query, setQuery] = useState("")

  const filteredFilms = useMemo(() => {
    const normalized = query.trim().toLowerCase()
    if (!normalized) {
      return films
    }
    return films.filter((film) => {
      const haystack = [
        film.title,
        film.director,
        film.genres,
        ...(film.actors ?? []),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
      return haystack.includes(normalized)
    })
  }, [films, query])

  return (
    <div>
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <label className="flex w-full max-w-md flex-col gap-2 text-sm text-[var(--muted)] sm:w-auto">
          Search films
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder={`Filter ${year} by title, director, cast, or genre...`}
            className="rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-[var(--foreground)] placeholder:text-[var(--muted)] focus:border-[var(--accent)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)]/30"
            aria-label={`Search films from ${year}`}
          />
        </label>
        <div className="flex flex-wrap gap-2">
          <a
            href={`/data/years/${year}.csv`}
            download={`letterboxd-popular-${year}.csv`}
            className="inline-flex items-center justify-center rounded-lg border border-[var(--border)] px-4 py-2 text-sm text-[var(--muted)] transition hover:border-[var(--accent)] hover:text-[var(--foreground)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)]"
          >
            Download CSV
          </a>
          <a
            href={`/data/years/${year}.json`}
            download={`letterboxd-popular-${year}.json`}
            className="inline-flex items-center justify-center rounded-lg border border-[var(--border)] px-4 py-2 text-sm text-[var(--muted)] transition hover:border-[var(--accent)] hover:text-[var(--foreground)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)]"
          >
            Download JSON
          </a>
        </div>
      </div>

      <div className="overflow-x-auto rounded-xl border border-[var(--border)]">
        <table className="min-w-full divide-y divide-[var(--border)]">
          <thead className="bg-[var(--surface)]">
            <tr>
              <th scope="col" className="w-14 px-3 py-3 text-left text-xs font-medium uppercase tracking-wide text-[var(--muted)]">
                Rank
              </th>
              <th scope="col" className="min-w-[10rem] px-3 py-3 text-left text-xs font-medium uppercase tracking-wide text-[var(--muted)]">
                Title
              </th>
              <th scope="col" className="min-w-[8rem] px-3 py-3 text-left text-xs font-medium uppercase tracking-wide text-[var(--muted)]">
                Director
              </th>
              <th scope="col" className="min-w-[10rem] px-3 py-3 text-left text-xs font-medium uppercase tracking-wide text-[var(--muted)]">
                Cast
              </th>
              <th scope="col" className="min-w-[8rem] px-3 py-3 text-left text-xs font-medium uppercase tracking-wide text-[var(--muted)]">
                Genre
              </th>
              <th scope="col" className="w-14 px-3 py-3 text-right text-xs font-medium uppercase tracking-wide text-[var(--muted)]">
                Link
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--border)] bg-[var(--background)]">
            {filteredFilms.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-sm text-[var(--muted)]">
                  No films match your search.
                </td>
              </tr>
            ) : (
              filteredFilms.map((film) => (
                <tr key={film.url} className="transition hover:bg-[var(--surface-hover)]">
                  <td className="px-3 py-3 text-sm font-medium text-[var(--muted)]">
                    {film.rank}
                  </td>
                  <td className="px-3 py-3 text-sm text-[var(--foreground)]">
                    <a
                      href={film.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-medium hover:text-[var(--accent)] focus:outline-none focus-visible:underline"
                    >
                      {film.title}
                    </a>
                  </td>
                  <td className="px-3 py-3 text-sm text-[var(--muted)]">
                    {film.director || "—"}
                  </td>
                  <td className="px-3 py-3 text-sm text-[var(--muted)]">
                    {formatActors(film.actors)}
                  </td>
                  <td className="px-3 py-3 text-sm text-[var(--muted)]">
                    {film.genres || "—"}
                  </td>
                  <td className="px-3 py-3 text-right">
                    <a
                      href={film.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      aria-label={`Open ${film.title} on Letterboxd`}
                      className="inline-flex rounded-md p-2 text-[var(--muted)] hover:bg-[var(--surface)] hover:text-[var(--accent)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)]"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                        className="h-4 w-4"
                        aria-hidden="true"
                      >
                        <path
                          fillRule="evenodd"
                          d="M4.25 5.5a.75.75 0 0 0-.75.75v8.5c0 .414.336.75.75.75h8.5a.75.75 0 0 0 .75-.75v-4a.75.75 0 0 1 1.5 0v4A2.25 2.25 0 0 1 12.75 17h-8.5A2.25 2.25 0 0 1 2 14.75v-8.5A2.25 2.25 0 0 1 4.25 4h5a.75.75 0 0 1 0 1.5h-5Z"
                          clipRule="evenodd"
                        />
                        <path
                          fillRule="evenodd"
                          d="M6.194 12.753a.75.75 0 0 0 1.06.053L16.5 4.44v2.81a.75.75 0 0 0 1.5 0v-4.5a.75.75 0 0 0-.75-.75h-4.5a.75.75 0 0 0 0 1.5h2.553l-9.056 8.194a.75.75 0 0 0-.053 1.06Z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </a>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
