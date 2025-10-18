"""Spider for scraping Kärnten municipalities."""

import scrapy
from datetime import datetime
from gemeindekontakt.items import MunicipalityItem
import re


class KaerntenSpider(scrapy.Spider):
    """
    Scrapes Kärnten municipalities from HTML table.

    Source: https://www.ktn.gv.at/Verwaltung/Gemeinden/Gemeindeliste

    HTML structure:
    <table class="table">
      <tbody>
        <tr>
          <td><a href="/Verwaltung/Gemeinden/Gemeinde?key=...">Gemeinde Name</a></td>
          <td>PLZ Ort<br />Straße</td>
          <td>Tel: ...<br />Fax: ...</td>
          <td>URL: <a href="...">...</a><br />E-Mail: <a href="mailto:...">...</a></td>
        </tr>
      </tbody>
    </table>
    """

    name = "kaernten"
    allowed_domains = ["ktn.gv.at"]
    start_urls = ["https://www.ktn.gv.at/Verwaltung/Gemeinden/Gemeindeliste"]

    def parse(self, response):
        """Parse HTML table and extract municipality data."""
        # Find all municipality rows in the table
        for row in response.css('table.table tbody tr'):
            item = MunicipalityItem()
            item['bundesland'] = 'Kärnten'
            item['scraped_at'] = datetime.now().isoformat()
            item['source_url'] = response.url

            # Column 1: Municipality name
            name_link = row.css('td:nth-child(1) a::text').get()
            if name_link:
                # Remove prefixes like "Gemeinde", "Stadtgemeinde", "Marktgemeinde"
                item['name'] = re.sub(r'^(Stadt|Markt)?gemeinde\s+', '', name_link).strip()

            # Column 2: Address (PLZ Ort<br />Straße)
            address_parts = row.css('td:nth-child(2)::text, td:nth-child(2) br::text').getall()
            address_parts = [p.strip() for p in address_parts if p.strip()]

            if len(address_parts) >= 1:
                # First part is "PLZ Ort"
                plz_ort = address_parts[0]
                plz_match = re.match(r'^(\d+)\s+(.+)$', plz_ort)
                if plz_match:
                    item['plz'] = plz_match.group(1)
                    # Full address includes street
                    if len(address_parts) >= 2:
                        item['address'] = f"{address_parts[1]}, {plz_ort}"
                    else:
                        item['address'] = plz_ort

            # Column 3: Phone and Fax
            contact_parts = row.css('td:nth-child(3)::text').getall()
            for part in contact_parts:
                part = part.strip()
                if part.startswith('Tel:'):
                    item['phone'] = part.replace('Tel:', '').strip()
                elif part.startswith('Fax:'):
                    item['fax'] = part.replace('Fax:', '').strip()

            # Column 4: Website and Email
            website_link = row.css('td:nth-child(4) a[href^="http"]::attr(href)').get()
            if website_link:
                item['website'] = website_link

            email_link = row.css('td:nth-child(4) a[href^="mailto:"]::attr(href)').get()
            if email_link:
                item['email'] = email_link.replace('mailto:', '')

            yield item
