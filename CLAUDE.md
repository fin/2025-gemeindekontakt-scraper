# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project scrapes contact information for all municipalities (Gemeinden) across Austria's 9 federal states (Bundesländer). Each state publishes municipality data in different formats and structures, requiring state-specific scraping approaches.

## Data Sources

The README.md contains authoritative source URLs for each state:

- **Burgenland**: Excel file from state government
- **Kärnten**: HTML list from state website
- **Niederösterreich**: Navigation-based site with detail pages per municipality
- **Oberösterreich**: Plain text file (ooeGem.txt)
- **Salzburg**: HTML page listing municipalities
- **Steiermark**: Government portal with municipality data
- **Tirol**: State government municipality directory
- **Vorarlberg**: List with names and emails only (may need Wikidata augmentation)
- **Wien**: TBD

## Development Environment

- **Python**: Python 3.12 managed with uv package manager
- **Virtual Environment**: `.venv/` directory (created by uv)
- **Package Manager**: uv (astral.sh/uv) - modern Python package manager
- **Framework**: Scrapy 2.13.3 for web scraping
- **Container**: DevContainer with Python 3 and Node.js 24

## Development Commands

### Environment Setup
```bash
# uv is installed in /home/vscode/.local/bin
export PATH="/home/vscode/.local/bin:$PATH"

# Activate virtual environment
source .venv/bin/activate

# Install/update dependencies
uv add <package-name>
```

### Running Scrapers
```bash
# Run a specific state scraper
scrapy crawl burgenland -o output/burgenland.json
scrapy crawl oberoesterreich -o output/oberoesterreich.json

# Run with custom settings
scrapy crawl burgenland -s DOWNLOAD_DELAY=2

# List all available spiders
scrapy list
```

### Testing with Fixtures
Test data files are stored in `test/fixtures/`:
- `burgenland.xlsx` - Excel file with Burgenland municipalities
- `oberoesterreich.txt` - Semicolon-separated text file with Oberösterreich municipalities

## Architecture

### Scrapy Project Structure
```
gemeindekontakt/               # Main Scrapy project package
├── items.py                   # Data item definitions (MunicipalityItem)
├── middlewares.py             # Spider and downloader middlewares
├── pipelines.py               # Item processing pipelines
├── settings.py                # Scrapy settings
└── spiders/                   # Spider implementations
    ├── burgenland.py          # Excel-based scraper (IMPLEMENTED)
    ├── oberoesterreich.py     # Text file scraper (IMPLEMENTED)
    └── [other states].py      # TODO: Implement remaining states
```

### Data Model (MunicipalityItem)

Defined in `gemeindekontakt/items.py`:
- `name` - Municipality name
- `bundesland` - Federal state (Burgenland, Kärnten, etc.)
- `bezirk` - District (optional)
- `plz` - Postal code
- `address` - Street address
- `phone` - Phone number
- `fax` - Fax number
- `email` - Email address
- `website` - Official website
- `source_url` - URL where data was scraped from
- `scraped_at` - ISO timestamp of scraping

### Implemented Spiders

1. **Burgenland** (`burgenland.py`) ✅ TESTED
   - Parses Excel file (.xlsx) using openpyxl
   - Columns: Bezirk, GKZ, PLZ, Gemeindestatus, Gemeinde, Straße, Gemeinde_Mail, Gemeinde_Telefon, Gemeinde_Webseite, etc.
   - Data starts at row 3 (row 1 is merged header, row 2 is column names)
   - **Result**: 171 municipalities successfully scraped

2. **Oberösterreich** (`oberoesterreich.py`) ✅ TESTED
   - Parses semicolon-separated text file with quoted values
   - Fields: GemKZ, GemArt, GemeindeName, Adresse, PLZ, Ort, Telefon, Fax, E_Mail, Internet, Bezirk, etc.
   - Header in line 1, data starts at line 2
   - **Result**: 438 municipalities successfully scraped

3. **Kärnten** (`kaernten.py`) ✅ IMPLEMENTED
   - Parses HTML table structure
   - Table columns: Gemeinde name link, PLZ Ort/Straße, Telefon/Fax, Homepage/E-Mail
   - CSS selectors: `table.table tbody tr` for rows, `td:nth-child(n)` for columns
   - **Status**: Implementation complete, not yet tested

### Remaining State Scrapers

The following spiders need to be implemented (HTML structure inspection required):

- **Kärnten**: HTML list parsing
- **Niederösterreich**: Two-step scraper (list page → detail pages)
- **Salzburg**: HTML page parsing
- **Steiermark**: Government portal parsing
- **Tirol**: State directory parsing
- **Vorarlberg**: Simple name + email list (consider Wikidata enrichment)
- **Wien**: Source TBD

### Scrapy Settings

Key settings in `gemeindekontakt/settings.py`:
- `ROBOTSTXT_OBEY = True` - Respects robots.txt
- `CONCURRENT_REQUESTS_PER_DOMAIN = 1` - Polite crawling
- `DOWNLOAD_DELAY = 1` - 1 second delay between requests
- `FEED_EXPORT_ENCODING = "utf-8"` - UTF-8 output for German characters

### Output Formats

Scrapy supports multiple output formats via `-o` flag:
- JSON: `-o output.json`
- JSON Lines: `-o output.jsonl`
- CSV: `-o output.csv`
- XML: `-o output.xml`