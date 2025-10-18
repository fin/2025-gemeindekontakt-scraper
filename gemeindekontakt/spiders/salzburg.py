"""Spider for scraping Salzburg municipalities."""

import scrapy
from datetime import datetime
from gemeindekontakt.items import MunicipalityItem
import re


class SalzburgSpider(scrapy.Spider):
    """
    Scrapes Salzburg municipalities from government website.

    Source: https://www.salzburg.gv.at/dienststellen/gemeinden

    The page may be dynamically loaded, so we'll parse whatever structure is available.
    """

    name = "salzburg"
    allowed_domains = ["salzburg.gv.at"]
    start_urls = ["https://www.salzburg.gv.at/dienststellen/gemeinden"]

    def parse(self, response):
        """Parse municipality list page."""
        # The page has municipalities in main content with alternating structure:
        # 1. Link to municipality website with municipality name
        # 2. "E-Mail" link with mailto: address
        # This pattern repeats for each municipality

        main_content = response.css('main')

        if not main_content:
            self.logger.error("Could not find main content")
            return

        # Get all links in main content
        all_links = main_content.css('a')

        i = 0
        while i < len(all_links):
            link = all_links[i]
            href = link.css('::attr(href)').get()
            text = link.css('::text').get()

            if not href or not text:
                i += 1
                continue

            text = text.strip()

            # Skip navigation/header links
            if text.lower() in ['e-mail', 'stadt salzburg'] or len(text) < 3:
                i += 1
                continue

            # Skip internal salzburg.gv.at links (these are navigation)
            if href.startswith('/') or 'salzburg.gv.at' in href:
                i += 1
                continue

            # This should be a municipality website link
            if href.startswith('http'):
                item = MunicipalityItem()
                item['bundesland'] = 'Salzburg'
                item['name'] = text
                item['website'] = href
                item['scraped_at'] = datetime.now().isoformat()
                item['source_url'] = response.url

                # Check if next link is an email
                if i + 1 < len(all_links):
                    next_link = all_links[i + 1]
                    next_href = next_link.css('::attr(href)').get()
                    next_text = next_link.css('::text').get()

                    if next_href and next_href.startswith('mailto:'):
                        item['email'] = next_href.replace('mailto:', '').strip()
                        i += 2  # Skip both current and email link
                    else:
                        i += 1
                else:
                    i += 1

                yield item
            else:
                i += 1
