"use client"

type LastUpdatedFooterProps = {
  lastUpdatedUtc: string
}

export default function LastUpdatedFooter({ lastUpdatedUtc }: LastUpdatedFooterProps) {
  const formatted = new Intl.DateTimeFormat(undefined, {
    dateStyle: "long",
    timeStyle: "short",
  }).format(new Date(lastUpdatedUtc))

  return (
    <footer
      className="mt-auto border-t border-[var(--border)] bg-[var(--surface)] px-4 py-6 sm:px-6"
      aria-live="polite"
    >
      <div className="mx-auto flex max-w-6xl flex-col gap-2 text-sm text-[var(--muted)] sm:flex-row sm:items-center sm:justify-between">
        <p>Last updated {formatted}</p>
        <p className="text-xs sm:text-sm">
          Not affiliated with Letterboxd. Data sourced from public Letterboxd pages.
        </p>
      </div>
    </footer>
  )
}
