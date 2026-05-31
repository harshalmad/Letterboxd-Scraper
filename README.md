# Letterboxd Popular Films

![Scrape](https://github.com/harshalmad/Letterboxd-Scraper/actions/workflows/scrape.yml/badge.svg)

Periodically scrapes the **50 most popular Letterboxd films** for each release year (1977–2026), using Letterboxd's **year-to-date** popularity window. Results are published as a browsable website and downloadable JSON/CSV datasets.

**Live site:** [letterboxd-scraper.vercel.app](https://letterboxd-scraper.vercel.app)

**Repository:** [github.com/harshalmad/Letterboxd-Scraper](https://github.com/harshalmad/Letterboxd-Scraper)

## Architecture

```
scraper/          Python scraper (CSV + JSON output)
web/              Next.js frontend (deployed on Vercel)
.github/          Weekly GitHub Actions scrape workflow
```

1. The Python scraper fetches film lists from Letterboxd.
2. JSON data is written to `web/public/data/` for the website.
3. GitHub Actions runs the scraper every **Sunday at 06:00 UTC** (and on manual trigger).
4. Vercel redeploys the site when data changes on `main`.

## Quick start (scraper)

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r scraper/requirements.txt
python scraper/scraper.py
```

This writes:

- CSV files to `scraper/output/{year}.csv` and `web/public/data/years/{year}.csv`
- JSON files to `web/public/data/years/{year}.json`
- Manifest to `web/public/data/manifest.json`

### Scraper options

| Flag | Default | Description |
|------|---------|-------------|
| `--start-year` | 1977 | First release year |
| `--end-year` | 2026 | Last release year |
| `--year` | — | Scrape specific year(s) only |
| `--json-dir` | `web/public/data` | JSON output directory |
| `--output-dir` | `scraper/output` | CSV output directory |
| `--max-films` | 50 | Films per year |
| `--delay` | 1.5 | Seconds between years |
| `--no-json` | — | Skip JSON output |

## Web app (local)

```bash
cd web
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## GitHub repository settings

After cloning, you can set the repo homepage and topics (requires [GitHub CLI](https://cli.github.com/) auth):

```powershell
gh auth login
./scripts/update-github-about.ps1
```

This sets the homepage to `https://letterboxd-scraper.vercel.app` and topics: `letterboxd`, `nextjs`, `web-scraping`.

## Deploy to Vercel

1. Import [harshalmad/Letterboxd-Scraper](https://github.com/harshalmad/Letterboxd-Scraper) on Vercel.
2. Set **Root Directory** to `web`.
3. Deploy. Set `NEXT_PUBLIC_SITE_URL` to your production URL for the sitemap.

## Data semantics

For each release year `Y`, films are ranked by popularity during the **current calendar year** on Letterboxd—not all-time or weekly popularity:

`https://letterboxd.com/films/popular/this/year/year/{Y}/size/large/page/1/`

## Disclaimer

This project is **not affiliated with Letterboxd**. Use respectfully and review [Letterboxd's terms](https://letterboxd.com/terms) for non-personal use.

## License

MIT — see [LICENSE](LICENSE).
