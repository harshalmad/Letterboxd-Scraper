#!/usr/bin/env python3
"""Convert existing CSV scrape output to JSON for the web app."""

from __future__ import annotations

import csv
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from scraper import Film, write_manifest, write_year_json

ROOT = Path(__file__).resolve().parent.parent
CSV_DIR = Path(__file__).resolve().parent / "output"
JSON_DIR = ROOT / "web" / "public" / "data"


def main() -> int:
    if not CSV_DIR.exists():
        print(f"No CSV directory found at {CSV_DIR}")
        return 1

    csv_files = sorted(CSV_DIR.glob("*.csv"), key=lambda p: int(p.stem))
    if not csv_files:
        print("No CSV files found.")
        return 1

    successful_years: list[int] = []
    total_films = 0

    for csv_path in csv_files:
        year = int(csv_path.stem)
        films: list[Film] = []
        with csv_path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                actors_raw = row.get("actors", "") or ""
                actors = tuple(
                    actor.strip()
                    for actor in actors_raw.split(";")
                    if actor.strip()
                )
                films.append(
                    Film(
                        rank=int(row["rank"]),
                        title=row["title"],
                        url=row["url"],
                        director=row.get("director", "") or "",
                        actors=actors,
                        genres=row.get("genres", "") or "",
                    )
                )

        write_year_json(JSON_DIR / "years" / f"{year}.json", year, films)
        shutil.copy2(csv_path, JSON_DIR / "years" / f"{year}.csv")
        successful_years.append(year)
        total_films += len(films)
        print(f"Converted {year}: {len(films)} films")

    write_manifest(
        JSON_DIR / "manifest.json",
        successful_years=successful_years,
        film_count=total_films,
        start_year=min(successful_years),
        end_year=max(successful_years),
    )
    print(f"Wrote manifest with {total_films} films across {len(successful_years)} years.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
