import Link from "next/link"

const navItems = [
  { href: "/", label: "Years" },
  { href: "/about", label: "About" },
  {
    href: "https://github.com/harshalmad/Letterboxd-Scraper",
    label: "GitHub",
    external: true,
  },
]

export default function SiteHeader() {
  return (
    <header className="border-b border-[var(--border)] bg-[var(--surface)]">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
        <Link
          href="/"
          className="group flex flex-col focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)]"
          aria-label="Letterboxd Popular Films home"
        >
          <span className="text-lg font-semibold tracking-tight text-[var(--foreground)] group-hover:text-[var(--accent)]">
            Letterboxd Popular Films
          </span>
          <span className="text-xs text-[var(--muted)]">
            Top 50 by release year · year-to-date popularity
          </span>
        </Link>

        <nav aria-label="Main navigation">
          <ul className="flex items-center gap-1 sm:gap-2">
            {navItems.map((item) => (
              <li key={item.href}>
                {item.external ? (
                  <a
                    href={item.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="rounded-md px-3 py-2 text-sm text-[var(--muted)] transition hover:bg-[var(--surface-hover)] hover:text-[var(--foreground)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)]"
                  >
                    {item.label}
                  </a>
                ) : (
                  <Link
                    href={item.href}
                    className="rounded-md px-3 py-2 text-sm text-[var(--muted)] transition hover:bg-[var(--surface-hover)] hover:text-[var(--foreground)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)]"
                  >
                    {item.label}
                  </Link>
                )}
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </header>
  )
}
