"""Spider for scraping Oberösterreich municipalities from text file."""

import scrapy
from datetime import datetime
from gemeindekontakt.items import MunicipalityItem


class OberoesterreichSpider(scrapy.Spider):
    """
    Scrapes Oberösterreich municipalities from semicolon-separated text file.

    Source: https://www.land-oberoesterreich.gv.at/gemeinden/ooeGem.txt

    Text file structure (line 1 contains headers):
    "GemKZ";"GemArt";"GemeindeName";"Adresse";"PLZ";"Ort";"Telefon";"Fax";
    "E_Mail";"Internet";"EWZ1991";"EWZ2001";"Bezirk";"Gerichtsbezirk";
    "bgmFktnTitel";"bgmTitel";"bgmVorname";"bgmNachname";"bgmGeschlecht";
    "bgmPartei";"bgmKurzPartei"
    """

    name = "oberoesterreich"
    allowed_domains = ["land-oberoesterreich.gv.at"]
    start_urls = ["https://www.land-oberoesterreich.gv.at/gemeinden/ooeGem.txt"]

    def parse(self, response):
        """Parse semicolon-separated text file and extract municipality data."""
        # File is semicolon-separated with quoted values
        # First line is header
        lines = response.text.split('\n')

        for line in lines[1:]:  # Skip header line
            line = line.strip()
            if not line:
                continue

            # Split by semicolon and remove quotes
            fields = [f.strip('"') for f in line.split(';')]

            if len(fields) < 21:  # Ensure we have all expected fields
                continue

            item = MunicipalityItem()
            item['bundesland'] = 'Oberösterreich'
            item['scraped_at'] = datetime.now().isoformat()
            item['source_url'] = response.url

            # Map fields based on actual structure
            # Index 0: GemKZ (municipality code) - not in our item
            # Index 1: GemArt (municipality type) - not in our item
            item['name'] = fields[2]         # GemeindeName
            address_street = fields[3]       # Adresse
            plz = fields[4]                  # PLZ
            ort = fields[5]                  # Ort
            # Combine address fields
            item['address'] = f"{address_street}, {plz} {ort}" if address_street and plz and ort else address_street
            item['plz'] = plz
            item['phone'] = fields[6]        # Telefon
            item['fax'] = fields[7]          # Fax
            item['email'] = fields[8]        # E_Mail
            item['website'] = fields[9]      # Internet
            # Index 10-11: Population data - not in our item
            item['bezirk'] = fields[12]      # Bezirk
            # Index 13-20: Bürgermeister and other info - not in our item

            yield item
