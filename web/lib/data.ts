import fs from "fs"
import path from "path"

export type Film = {
  rank: number
  title: string
  url: string
}

export type YearData = {
  year: number
  sourceUrl: string
  films: Film[]
}

export type Manifest = {
  lastUpdatedUtc: string
  startYear: number
  endYear: number
  years: number[]
  filmCount: number
  sourceUrlTemplate: string
}

const DATA_DIR = path.join(process.cwd(), "public", "data")

export function getManifest(): Manifest {
  const raw = fs.readFileSync(path.join(DATA_DIR, "manifest.json"), "utf-8")
  return JSON.parse(raw) as Manifest
}

export function getYearData(year: number): YearData | null {
  const filePath = path.join(DATA_DIR, "years", `${year}.json`)
  if (!fs.existsSync(filePath)) {
    return null
  }
  const raw = fs.readFileSync(filePath, "utf-8")
  return JSON.parse(raw) as YearData
}

export function getAllYears(): number[] {
  return getManifest().years
}

export function isValidYear(year: number): boolean {
  return getAllYears().includes(year)
}
