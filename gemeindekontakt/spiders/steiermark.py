"""Spider for scraping Steiermark municipalities."""

import scrapy
from datetime import datetime
from gemeindekontakt.items import MunicipalityItem
import re
import io


class SteiermarkSpider(scrapy.Spider):
    """
    Scrapes Steiermark municipalities from Excel file.

    Source: https://www.verwaltung.steiermark.at/cms/beitrag/11683218/74836396/

    The page contains a link to an Excel file with municipality data.
    Excel file format: 2025_BGM_GEM_StDat_YYYYMMDD.xlsx
    """

    name = "steiermark"
    allowed_domains = ["verwaltung.steiermark.at"]
    start_urls = ["https://www.verwaltung.steiermark.at/cms/beitrag/11683218/74836396/"]

    def parse(self, response):
        """Find and download the Excel file with municipality data."""
        # Find Excel file links
        excel_links = response.css('a[href$=".xlsx"], a[href$=".xls"]')

        for link in excel_links:
            href = link.css('::attr(href)').get()
            # Look for the municipality data file (contains "GEM" or "Gemeinde")
            if href and ('GEM' in href or 'Gemeinde' in href.lower() or 'BGM' in href):
                # Make absolute URL
                excel_url = response.urljoin(href)
                yield scrapy.Request(
                    excel_url,
                    callback=self.parse_excel,
                    meta={'source_url': response.url}
                )
                break

    def parse_excel(self, response):
        """Parse Excel file with municipality data."""
        try:
            import openpyxl
        except ImportError:
            self.logger.error("openpyxl is required to parse Excel files. Install with: uv add openpyxl")
            return

        # Load Excel file from response body
        excel_file = io.BytesIO(response.body)
        workbook = openpyxl.load_workbook(excel_file, data_only=True)
        sheet = workbook.active

        # Find header row and data
        headers = []
        data_start_row = None

        # Scan first 10 rows to find headers
        for row_num in range(1, 11):
            row = sheet[row_num]
            row_values = [cell.value for cell in row if cell.value]

            # Check if this looks like a header row
            if any(keyword in str(cell.value).lower() for cell in row
                   for keyword in ['gemeinde', 'name', 'adresse', 'tel', 'email', 'plz']):
                headers = [cell.value for cell in row]
                data_start_row = row_num + 1
                break

        if not headers or not data_start_row:
            self.logger.error("Could not find header row in Excel file")
            return

        # Create column mapping
        col_map = {}
        for idx, header in enumerate(headers):
            if header:
                header_clean = str(header).replace('\n', ' ').lower()
                if 'gem_name' in header_clean or header_clean == 'gemeinde':
                    col_map['name'] = idx
                elif 'bezirk' in header_clean and 'name' not in header_clean:
                    col_map['bezirk'] = idx
                elif header_clean == 'plz' or 'postleitzahl' in header_clean:
                    col_map['plz'] = idx
                elif 'straße' in header_clean or 'strasse' in header_clean:
                    col_map['address'] = idx
                elif 'telefon' in header_clean:
                    col_map['phone'] = idx
                elif header_clean == 'fax':
                    col_map['fax'] = idx
                elif 'e-mail' in header_clean:
                    col_map['email'] = idx
                elif header_clean == 'web' or 'homepage' in header_clean:
                    col_map['website'] = idx
                elif 'postort' in header_clean or header_clean == 'ort':
                    col_map['ort'] = idx

        # Parse data rows
        for row in sheet.iter_rows(min_row=data_start_row):
            row_values = [cell.value for cell in row]

            # Skip empty rows
            if not any(row_values):
                continue

            # Skip if no municipality name
            if 'name' not in col_map or not row_values[col_map['name']]:
                continue

            item = MunicipalityItem()
            item['bundesland'] = 'Steiermark'
            item['scraped_at'] = datetime.now().isoformat()
            item['source_url'] = response.meta['source_url']

            # Extract fields
            if 'name' in col_map and row_values[col_map['name']]:
                item['name'] = str(row_values[col_map['name']]).strip()

            if 'bezirk' in col_map and row_values[col_map['bezirk']]:
                item['bezirk'] = str(row_values[col_map['bezirk']]).strip()

            if 'plz' in col_map and row_values[col_map['plz']]:
                item['plz'] = str(row_values[col_map['plz']]).strip()

            if 'address' in col_map and row_values[col_map['address']]:
                address = str(row_values[col_map['address']]).strip()
                # Combine with PLZ and Ort if available
                if 'plz' in col_map and 'ort' in col_map:
                    plz = row_values[col_map['plz']]
                    ort = row_values[col_map['ort']]
                    if plz and ort:
                        item['address'] = f"{address}, {plz} {ort}"
                    else:
                        item['address'] = address
                else:
                    item['address'] = address

            if 'phone' in col_map and row_values[col_map['phone']]:
                item['phone'] = str(row_values[col_map['phone']]).strip()

            if 'fax' in col_map and row_values[col_map['fax']]:
                item['fax'] = str(row_values[col_map['fax']]).strip()

            if 'email' in col_map and row_values[col_map['email']]:
                item['email'] = str(row_values[col_map['email']]).strip()

            if 'website' in col_map and row_values[col_map['website']]:
                item['website'] = str(row_values[col_map['website']]).strip()

            yield item
