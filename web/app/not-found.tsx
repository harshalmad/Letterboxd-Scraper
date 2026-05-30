import Link from "next/link"

export default function NotFound() {
  return (
    <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] px-6 py-10 text-center sm:px-10">
      <h1 className="text-2xl font-semibold text-[var(--foreground)]">Page not found</h1>
      <p className="mt-3 text-[var(--muted)]">
        That year or page doesn&apos;t exist in the dataset.
      </p>
      <Link
        href="/"
        className="mt-6 inline-flex rounded-lg bg-[var(--accent)] px-4 py-2 text-sm font-medium text-[#041018] transition hover:brightness-110 focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)]"
      >
        Back to all years
      </Link>
    </div>
  )
}
