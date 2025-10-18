"""Spider for scraping Tirol municipalities."""

import scrapy
from datetime import datetime
from gemeindekontakt.items import MunicipalityItem
import re


class TirolSpider(scrapy.Spider):
    """
    Scrapes Tirol municipalities from list page.

    Source: https://www.tirol.gv.at/gemeinden/

    HTML structure (277 municipalities):
    - Municipality name with link to detail page
    - Address (hyperlinked to map)
    - Phone (tel: link)
    - Fax (plain text)
    - Email (mailto: link)
    - Website (http link)
    """

    name = "tirol"
    allowed_domains = ["tirol.gv.at"]
    start_urls = ["https://www.tirol.gv.at/gemeinden/"]

    def parse(self, response):
        """Parse municipality list and extract contact data."""
        # Find all municipality links
        muni_links = response.css('a[href*="/gemeinden/gemeinde/"]')

        for link in muni_links:
            # Municipality name
            name = link.css('::text').get()
            if not name:
                continue

            item = MunicipalityItem()
            item['bundesland'] = 'Tirol'
            item['name'] = name.strip()
            item['scraped_at'] = datetime.now().isoformat()
            item['source_url'] = response.url

            # Get the parent <li> element which contains all the contact info
            parent = link.xpath('./parent::div/parent::li')

            if parent:
                # Extract all text nodes from the parent
                all_text = [t.strip() for t in parent.css('::text').getall() if t.strip()]

                # Extract address (usually contains ", " and 4-digit PLZ)
                for text in all_text:
                    if re.search(r'\d{4}\s+\w+', text) and ',' in text:
                        item['address'] = text
                        # Extract PLZ
                        plz_match = re.search(r'\b(\d{4})\b', text)
                        if plz_match:
                            item['plz'] = plz_match.group(1)
                        break

                # Extract phone (tel: link)
                phone_link = parent.css('a[href^="tel:"]::attr(href)').get()
                if phone_link:
                    item['phone'] = phone_link.replace('tel:', '').replace('+43', '+43 ').strip()

                # Extract fax (plain text, starts with +43, different from phone)
                phone_clean = item.get('phone', '').replace(' ', '').replace('-', '')
                for text in all_text:
                    text_clean = text.replace(' ', '').replace('-', '')
                    if text.startswith('+43') and text_clean != phone_clean:
                        item['fax'] = text
                        break

                # Extract email (mailto: link)
                email_link = parent.css('a[href^="mailto:"]::attr(href)').get()
                if email_link:
                    item['email'] = email_link.replace('mailto:', '').strip()

                # Extract website (http/https link, not maps)
                website_link = parent.css('a[href^="http"]:not([href*="maps"])::attr(href)').get()
                if not website_link:
                    # Try to find URL in text nodes
                    for text in all_text:
                        if text.startswith('http'):
                            item['website'] = text
                            break

            yield item
