#!/usr/bin/env python3
"""Scrape Letterboxd top popular films by release year and export to CSV/JSON."""

from __future__ import annotations

import argparse
import csv
import json
import logging
import re
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup

BASE_URL = "https://letterboxd.com"
PAGE_URL_TEMPLATE = (
    "https://letterboxd.com/films/popular/this/year/year/{year}/size/large/page/{page}/"
)
SOURCE_URL_TEMPLATE = (
    "https://letterboxd.com/films/popular/this/year/year/{year}/size/large/page/1/"
)
DEFAULT_START_YEAR = 1977
DEFAULT_END_YEAR = 2026
DEFAULT_MAX_FILMS = 50
DEFAULT_DELAY = 1.5
DEFAULT_FILM_DELAY = 0.75
DEFAULT_MAX_ACTORS = 3
DEFAULT_RETRIES = 3
DEFAULT_RETRY_BASE_DELAY = 2.0
DEFAULT_PAGE_DELAY = 0.0
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "output"
DEFAULT_JSON_DIR = Path(__file__).resolve().parent.parent / "web" / "public" / "data"
MAX_PAGES_PER_YEAR = 10
MAX_RATE_LIMIT_RETRY_DELAY = 90.0

logger = logging.getLogger(__name__)

_curl_session = None
_cloudscraper = None


@dataclass(frozen=True)
class Film:
    rank: int
    title: str
    url: str
    director: str = ""
    actors: tuple[str, ...] = ()
    genres: str = ""


CSV_FIELDNAMES = ["rank", "title", "director", "actors", "genres", "url"]


def slug_from_url(url: str) -> str:
    match = re.search(r"/film/([^/]+)/?", url)
    if not match:
        raise ValueError(f"Could not extract film slug from URL: {url}")
    return match.group(1)


def parse_film_details_from_html(html: str, max_actors: int = DEFAULT_MAX_ACTORS) -> dict[str, str | tuple[str, ...]]:
    soup = BeautifulSoup(html, "lxml")
    script = soup.find("script", type="application/ld+json")
    if not script:
        return {"director": "", "actors": (), "genres": ""}

    raw = script.string or script.get_text()
    raw = re.sub(r"/\*.*?\*/", "", raw, flags=re.DOTALL).strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {"director": "", "actors": (), "genres": ""}

    directors = data.get("director") or []
    if isinstance(directors, dict):
        directors = [directors]
    director = ", ".join(
        person.get("name", "")
        for person in directors
        if isinstance(person, dict) and person.get("name")
    )

    actors_data = data.get("actors") or data.get("actor") or []
    if isinstance(actors_data, dict):
        actors_data = [actors_data]
    actors: list[str] = []
    for person in actors_data:
        if not isinstance(person, dict):
            continue
        name = person.get("name")
        if name:
            actors.append(name)
        if len(actors) >= max_actors:
            break

    genres = data.get("genre") or []
    if isinstance(genres, str):
        genres = [genres]
    genre = ", ".join(str(item) for item in genres if item)

    return {"director": director, "actors": tuple(actors), "genres": genre}


def _is_rate_limited(exc: Exception) -> bool:
    message = str(exc).lower()
    return any(
        token in message
        for token in ("403", "429", "forbidden", "too many requests")
    )


def _retry_delay_seconds(
    attempt: int,
    exc: Exception | None,
    base_delay: float,
) -> float:
    """Return seconds to wait before the next retry (attempt is 1-based)."""
    if exc and _is_rate_limited(exc):
        return min(MAX_RATE_LIMIT_RETRY_DELAY, base_delay * (2**attempt))
    return base_delay * attempt


def fetch_film_details(
    film: Film,
    retries: int,
    timeout: int,
    max_actors: int,
    retry_base_delay: float,
) -> Film:
    slug = slug_from_url(film.url)
    page_url = urljoin(BASE_URL, f"/film/{slug}/")

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            html = fetch_page(page_url, referer=f"{BASE_URL}/films/popular/", timeout=timeout)
            details = parse_film_details_from_html(html, max_actors=max_actors)
            return Film(
                rank=film.rank,
                title=film.title,
                url=film.url,
                director=str(details["director"]),
                actors=tuple(details["actors"]),
                genres=str(details["genres"]),
            )
        except Exception as exc:
            last_error = exc
            if attempt < retries:
                backoff = _retry_delay_seconds(attempt, exc, retry_base_delay)
                logger.warning(
                    "Film %s attempt %s/%s failed: %s. Retrying in %ss...",
                    film.title,
                    attempt,
                    retries,
                    exc,
                    backoff,
                )
                time.sleep(backoff)

    logger.warning("Could not enrich %s: %s", film.title, last_error)
    return film


def enrich_films(
    films: list[Film],
    film_delay: float,
    retries: int,
    timeout: int,
    max_actors: int,
    retry_base_delay: float,
) -> list[Film]:
    enriched: list[Film] = []
    for index, film in enumerate(films):
        enriched_film = fetch_film_details(
            film,
            retries=retries,
            timeout=timeout,
            max_actors=max_actors,
            retry_base_delay=retry_base_delay,
        )
        enriched.append(enriched_film)
        if index < len(films) - 1 and film_delay > 0:
            time.sleep(film_delay)
    return enriched


def build_page_url(year: int, page: int) -> str:
    return PAGE_URL_TEMPLATE.format(year=year, page=page)


def build_fetch_url(year: int, page: int) -> str:
    """Convert the public discovery URL to Letterboxd's CSI browser-list endpoint."""
    page_url = build_page_url(year, page)
    return page_url.replace(
        "https://letterboxd.com/films",
        "https://letterboxd.com/csi/films/films-browser-list",
    )


def build_referer_url(year: int) -> str:
    return f"https://letterboxd.com/films/popular/this/year/year/{year}/size/large/"


def _looks_like_cloudflare(html: str) -> bool:
    lowered = html.lower()
    return "just a moment" in lowered or "cf-browser-verification" in lowered


def _get_curl_session():
    global _curl_session
    if _curl_session is None:
        from curl_cffi import requests as curl_requests

        _curl_session = curl_requests.Session()
    return _curl_session


def _get_cloudscraper():
    global _cloudscraper
    if _cloudscraper is None:
        import cloudscraper

        _cloudscraper = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "mobile": False}
        )
    return _cloudscraper


def _fetch_with_curl_cffi(url: str, referer: str, timeout: int) -> str:
    response = _get_curl_session().get(
        url,
        impersonate="chrome120",
        timeout=timeout,
        headers={
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": referer,
            "X-Requested-With": "XMLHttpRequest",
        },
    )
    response.raise_for_status()
    return response.text


def _fetch_with_cloudscraper(url: str, referer: str, timeout: int) -> str:
    response = _get_cloudscraper().get(
        url,
        timeout=timeout,
        headers={
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": referer,
            "X-Requested-With": "XMLHttpRequest",
        },
    )
    response.raise_for_status()
    return response.text


def fetch_page(url: str, referer: str, timeout: int = 30) -> str:
    """Fetch HTML, trying curl_cffi first then cloudscraper."""
    errors: list[str] = []

    try:
        html = _fetch_with_curl_cffi(url, referer, timeout)
        if not _looks_like_cloudflare(html):
            return html
        errors.append("curl_cffi returned a Cloudflare challenge page")
    except Exception as exc:
        errors.append(f"curl_cffi failed: {exc}")

    try:
        html = _fetch_with_cloudscraper(url, referer, timeout)
        if _looks_like_cloudflare(html):
            raise RuntimeError("cloudscraper returned a Cloudflare challenge page")
        return html
    except Exception as exc:
        errors.append(f"cloudscraper failed: {exc}")

    raise RuntimeError("; ".join(errors))


def _clean_title(raw_name: str) -> str:
    title = re.sub(r"\s+\(\d{4}\)\s*$", "", raw_name.strip())
    return title or raw_name.strip()


def _extract_from_item(item) -> Film | None:
    data_div = item.find("div", class_="react-component") or item.find(
        "div", attrs={"data-component-class": "LazyPoster"}
    )
    if not data_div:
        data_div = item

    slug = data_div.get("data-item-slug") or data_div.get("data-film-slug")
    raw_name = (
        data_div.get("data-item-name")
        or data_div.get("data-film-name")
        or data_div.get("data-item-full-display-name")
        or (data_div.img.get("alt") if data_div.img else None)
        or (item.img.get("alt") if item.img else None)
    )

    if not raw_name:
        return None

    if not slug:
        item_link = data_div.get("data-item-link")
        if item_link and item_link.startswith("/film/"):
            slug = item_link.strip("/").removeprefix("film/").rstrip("/")

    if not slug:
        link = item.find("a", href=True)
        if link and link["href"].startswith("/film/"):
            slug = link["href"].strip("/").removeprefix("film/").rstrip("/")

    if not slug:
        return None

    return Film(
        rank=0,
        title=_clean_title(raw_name),
        url=urljoin(BASE_URL, f"/film/{slug}/"),
    )


def parse_films(html: str) -> list[Film]:
    soup = BeautifulSoup(html, "lxml")
    items = soup.find_all("li", class_="posteritem")
    if not items:
        poster_list = soup.find("ul", class_="poster-list")
        items = poster_list.find_all("li") if poster_list else soup.find_all("li")

    films: list[Film] = []
    seen_urls: set[str] = set()

    for item in items:
        film = _extract_from_item(item)
        if not film or film.url in seen_urls:
            continue

        seen_urls.add(film.url)
        films.append(Film(rank=len(films) + 1, title=film.title, url=film.url))

    return films


def scrape_year(
    year: int,
    max_films: int,
    retries: int,
    timeout: int,
    page_delay: float,
    retry_base_delay: float,
) -> list[Film]:
    referer = build_referer_url(year)
    collected: list[Film] = []
    seen_urls: set[str] = set()

    for page in range(1, MAX_PAGES_PER_YEAR + 1):
        if len(collected) >= max_films:
            break

        fetch_url = build_fetch_url(year, page)
        last_error: Exception | None = None
        page_films: list[Film] = []

        for attempt in range(1, retries + 1):
            try:
                html = fetch_page(fetch_url, referer=referer, timeout=timeout)
                page_films = parse_films(html)
                if not page_films:
                    if page == 1:
                        raise RuntimeError("No films parsed from first page")
                    break
                last_error = None
                break
            except Exception as exc:
                last_error = exc
                if attempt < retries:
                    backoff = _retry_delay_seconds(attempt, exc, retry_base_delay)
                    logger.warning(
                        "Year %s page %s attempt %s/%s failed: %s. Retrying in %ss...",
                        year,
                        page,
                        attempt,
                        retries,
                        exc,
                        backoff,
                    )
                    time.sleep(backoff)

        if last_error is not None:
            raise RuntimeError(
                f"Failed to scrape year {year} page {page} after {retries} attempts"
            ) from last_error

        if not page_films:
            break

        for film in page_films:
            if film.url in seen_urls:
                continue
            seen_urls.add(film.url)
            collected.append(
                Film(rank=len(collected) + 1, title=film.title, url=film.url)
            )
            if len(collected) >= max_films:
                break

        if page_delay > 0 and len(collected) < max_films and page < MAX_PAGES_PER_YEAR:
            time.sleep(page_delay)

    if not collected:
        raise RuntimeError(f"No films found for year {year}")

    return collected


def write_csv(path: Path, films: list[Film]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        for film in films:
            writer.writerow(
                {
                    "rank": film.rank,
                    "title": film.title,
                    "director": film.director,
                    "actors": "; ".join(film.actors),
                    "genres": film.genres,
                    "url": film.url,
                }
            )


def write_year_json(path: Path, year: int, films: list[Film]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "year": year,
        "sourceUrl": SOURCE_URL_TEMPLATE.format(year=year),
        "films": [asdict(film) for film in films],
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_manifest(
    path: Path,
    successful_years: list[int],
    film_count: int,
    start_year: int,
    end_year: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "lastUpdatedUtc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "startYear": start_year,
        "endYear": end_year,
        "years": successful_years,
        "filmCount": film_count,
        "sourceUrlTemplate": SOURCE_URL_TEMPLATE,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape Letterboxd popular films by release year into CSV and JSON files."
    )
    parser.add_argument(
        "--start-year",
        type=int,
        default=DEFAULT_START_YEAR,
        help=f"First release year to scrape (default: {DEFAULT_START_YEAR})",
    )
    parser.add_argument(
        "--end-year",
        type=int,
        default=DEFAULT_END_YEAR,
        help=f"Last release year to scrape (default: {DEFAULT_END_YEAR})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory for CSV output (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--json-dir",
        type=Path,
        default=DEFAULT_JSON_DIR,
        help=f"Directory for JSON output (default: {DEFAULT_JSON_DIR})",
    )
    parser.add_argument(
        "--no-json",
        action="store_true",
        help="Skip writing JSON files for the web app",
    )
    parser.add_argument(
        "--no-details",
        action="store_true",
        help="Skip fetching director, cast, and genre from film pages",
    )
    parser.add_argument(
        "--film-delay",
        type=float,
        default=DEFAULT_FILM_DELAY,
        help=f"Seconds to wait between film detail requests (default: {DEFAULT_FILM_DELAY})",
    )
    parser.add_argument(
        "--max-actors",
        type=int,
        default=DEFAULT_MAX_ACTORS,
        help=f"Maximum billed actors to store per film (default: {DEFAULT_MAX_ACTORS})",
    )
    parser.add_argument(
        "--max-films",
        type=int,
        default=DEFAULT_MAX_FILMS,
        help=f"Maximum films per year (default: {DEFAULT_MAX_FILMS})",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY,
        help=f"Seconds to wait between years (default: {DEFAULT_DELAY})",
    )
    parser.add_argument(
        "--page-delay",
        type=float,
        default=DEFAULT_PAGE_DELAY,
        help=f"Seconds to wait between list pages within a year (default: {DEFAULT_PAGE_DELAY})",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=DEFAULT_RETRIES,
        help=f"Retry attempts per page (default: {DEFAULT_RETRIES})",
    )
    parser.add_argument(
        "--retry-base-delay",
        type=float,
        default=DEFAULT_RETRY_BASE_DELAY,
        help=(
            f"Base seconds for retry backoff; 403/429 responses use exponential backoff "
            f"(default: {DEFAULT_RETRY_BASE_DELAY})"
        ),
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="HTTP timeout in seconds (default: 30)",
    )
    parser.add_argument(
        "--year",
        type=int,
        action="append",
        dest="years",
        help="Scrape only specific year(s); can be repeated",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args(argv)


def resolve_years(args: argparse.Namespace) -> list[int]:
    if args.years:
        years = sorted(set(args.years))
    else:
        if args.start_year > args.end_year:
            raise ValueError("start-year must be less than or equal to end-year")
        years = list(range(args.start_year, args.end_year + 1))
    return years


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    try:
        years = resolve_years(args)
    except ValueError as exc:
        logger.error("%s", exc)
        return 1

    total_films = 0
    failed_years: list[int] = []
    successful_years: list[int] = []
    json_years_dir = args.json_dir / "years"

    logger.info(
        "Scraping %s year(s), up to %s films each, CSV -> %s, JSON -> %s",
        len(years),
        args.max_films,
        args.output_dir,
        "disabled" if args.no_json else args.json_dir,
    )

    for index, year in enumerate(years):
        try:
            films = scrape_year(
                year=year,
                max_films=args.max_films,
                retries=args.retries,
                timeout=args.timeout,
                page_delay=args.page_delay,
                retry_base_delay=args.retry_base_delay,
            )

            if not args.no_details:
                logger.info("Enriching %s films for %s with cast, director, and genre...", len(films), year)
                films = enrich_films(
                    films,
                    film_delay=args.film_delay,
                    retries=args.retries,
                    timeout=args.timeout,
                    max_actors=args.max_actors,
                    retry_base_delay=args.retry_base_delay,
                )
            csv_path = args.output_dir / f"{year}.csv"
            write_csv(csv_path, films)

            if not args.no_json:
                json_path = json_years_dir / f"{year}.json"
                write_year_json(json_path, year, films)
                write_csv(json_years_dir / f"{year}.csv", films)

            total_films += len(films)
            successful_years.append(year)

            if len(films) < args.max_films:
                logger.warning(
                    "Year %s: wrote %s films (expected up to %s)",
                    year,
                    len(films),
                    args.max_films,
                )
            else:
                logger.info("Year %s: wrote %s films", year, len(films))
        except Exception as exc:
            failed_years.append(year)
            logger.error("Year %s failed: %s", year, exc)

        if index < len(years) - 1 and args.delay > 0:
            time.sleep(args.delay)

    if successful_years and not args.no_json:
        write_manifest(
            args.json_dir / "manifest.json",
            successful_years=successful_years,
            film_count=total_films,
            start_year=min(successful_years),
            end_year=max(successful_years),
        )
        logger.info("Wrote manifest -> %s", args.json_dir / "manifest.json")

    logger.info(
        "Done. %s films written across %s successful year(s).",
        total_films,
        len(successful_years),
    )

    if failed_years:
        logger.error("Failed years: %s", ", ".join(str(y) for y in failed_years))
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
