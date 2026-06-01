# Updates GitHub repository About (homepage) and topics.
# Prerequisites: GitHub CLI installed and authenticated (`gh auth login`).

$ErrorActionPreference = "Stop"

function Get-GhExecutable {
    $gh = Get-Command gh -ErrorAction SilentlyContinue
    if ($gh) {
        return $gh.Source
    }

    $candidates = @(
        "${env:ProgramFiles}\GitHub CLI\gh.exe",
        "${env:ProgramFiles(x86)}\GitHub CLI\gh.exe",
        "${env:LocalAppData}\Programs\GitHub CLI\gh.exe"
    )

    foreach ($path in $candidates) {
        if (Test-Path $path) {
            return $path
        }
    }

    throw @"
GitHub CLI (gh) was not found.

Install it with:
  winget install --id GitHub.cli

Then close and reopen PowerShell (or restart Cursor) so PATH updates, and run:
  gh auth login
  ./scripts/update-github-about.ps1
"@
}

$gh = Get-GhExecutable
$repo = "harshalmad/Letterboxd-Scraper"
$homepage = "https://letterboxd-scraper.vercel.app"
$topics = @("letterboxd", "nextjs", "web-scraping")

Write-Host "Using GitHub CLI at: $gh"
Write-Host "Updating $repo homepage to $homepage..."
& $gh repo edit $repo --homepage $homepage

Write-Host "Setting topics: $($topics -join ', ')..."
& $gh repo edit $repo --add-topic $topics

Write-Host "Done. Verify at https://github.com/$repo"
