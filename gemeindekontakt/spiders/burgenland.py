"""Spider for scraping Burgenland municipalities from Excel file."""

import scrapy
from datetime import datetime
from openpyxl import load_workbook
from io import BytesIO
from gemeindekontakt.items import MunicipalityItem


class BurgenlandSpider(scrapy.Spider):
    """
    Scrapes Burgenland municipalities from an Excel file.

    Source: https://www.burgenland.at/fileadmin/user_upload/Downloads/Land_und_Politik/Land/Bezirke_und_Gemeinden/Liste_der_Gemeinden_des_Burgenlands_Stand_25-08-2025.xlsx

    Excel structure (row 2 contains headers):
    - Bezirk, GKZ, PLZ, Gemeindestatus, Gemeinde, Straße, Gemeinde_Mail,
      Gemeinde_Telefon, Gemeinde_Webseite, BM_Titel_vor, BM_Nachname,
      BM_Vorname, BM_Titel_nach, BM_Partei
    """

    name = "burgenland"
    allowed_domains = ["burgenland.at"]
    start_urls = [
        "https://www.burgenland.at/fileadmin/user_upload/Downloads/Land_und_Politik/Land/Bezirke_und_Gemeinden/Liste_der_Gemeinden_des_Burgenlands_Stand_25-08-2025.xlsx"
    ]

    def parse(self, response):
        """Parse Excel file and extract municipality data."""
        # Load Excel file from response body
        workbook = load_workbook(filename=BytesIO(response.body))
        sheet = workbook.active

        # Row 1 is merged header, Row 2 contains column names, data starts at Row 3
        for row in sheet.iter_rows(min_row=3, values_only=True):
            if not row[4]:  # Skip rows without municipality name (column E: Gemeinde)
                continue

            item = MunicipalityItem()
            item['bundesland'] = 'Burgenland'
            item['scraped_at'] = datetime.now().isoformat()
            item['source_url'] = response.url

            # Map Excel columns based on actual structure
            item['bezirk'] = row[0]          # A: Bezirk
            # row[1] is GKZ (municipality code) - not in our item
            item['plz'] = str(row[2]) if row[2] else None  # C: PLZ
            # row[3] is Gemeindestatus - not in our item
            item['name'] = row[4]            # E: Gemeinde
            item['address'] = row[5]         # F: Straße
            item['email'] = row[6]           # G: Gemeinde_Mail
            item['phone'] = row[7]           # H: Gemeinde_Telefon
            item['website'] = row[8]         # I: Gemeinde_Webseite
            # Columns J-M are Bürgermeister info - not in our item

            yield item
