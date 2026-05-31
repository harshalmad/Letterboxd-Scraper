# Updates GitHub repository About (homepage) and topics.
# Prerequisites: GitHub CLI installed and authenticated (`gh auth login`).

$ErrorActionPreference = "Stop"

$repo = "harshalmad/Letterboxd-Scraper"
$homepage = "https://letterboxd-scraper.vercel.app"
$topics = @("letterboxd", "nextjs", "web-scraping")

Write-Host "Updating $repo homepage to $homepage..."
gh repo edit $repo --homepage $homepage

Write-Host "Setting topics: $($topics -join ', ')..."
gh repo edit $repo --add-topic $topics

Write-Host "Done. Verify at https://github.com/$repo"
