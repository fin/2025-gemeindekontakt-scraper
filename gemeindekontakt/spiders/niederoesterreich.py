"""Spider for scraping Niederösterreich municipalities."""

import scrapy
from datetime import datetime
from gemeindekontakt.items import MunicipalityItem
import re


class NiederoesterreichSpider(scrapy.Spider):
    """
    Scrapes Niederösterreich municipalities using two-step approach.

    Source: https://noe.gv.at/noe/index.html

    Approach:
    1. Parse navigation menu to extract all municipality page links
    2. Visit each municipality detail page to extract contact info
    """

    name = "niederoesterreich"
    allowed_domains = ["noe.gv.at"]
    start_urls = ["https://noe.gv.at/noe/index.html"]

    # Increase timeout since this is a two-step scraper that visits 573 individual pages
    custom_settings = {
        'DOWNLOAD_TIMEOUT': 30,  # Increase from default 180 to 30 seconds per page
        'CONCURRENT_REQUESTS': 2,  # Allow 2 concurrent requests to speed up
    }

    def parse(self, response):
        """Parse navigation menu to find all municipality links."""
        # Find all links to municipality pages within div.gemeinde
        # This filters out navigation and theme pages
        muni_links = response.css(
            'div.gemeinde a[href^="/noe/"][href$=".html"]')

        for link in muni_links:
            href = link.css('::attr(href)').get()
            text = link.css('::text').get()

            if href and text:
                # Skip navigation links (index, overview pages, district pages)
                if 'index.html' in href.lower():
                    continue

                # Skip district/bezirk pages
                if 'bezirk' in href.lower() and not any(word in text.lower() for word in ['gemeinde']):
                    continue

                # Build absolute URL
                url = response.urljoin(href)

                # Pass municipality name from link text
                yield scrapy.Request(
                    url,
                    callback=self.parse_municipality,
                    meta={'name': text.strip()}
                )

    def parse_municipality(self, response):
        """Parse individual municipality page to extract contact info."""
        item = MunicipalityItem()
        item['bundesland'] = 'Niederösterreich'
        item['scraped_at'] = datetime.now().isoformat()
        item['source_url'] = response.url
        item['name'] = response.meta['name']

        # Find contact information section
        # Common patterns: "Kontakt", "Adresse", "Gemeindeamt"
        content = response.css('main, article, .content, #content')

        if not content:
            content = response

        # Extract address
        # Look for patterns like "PLZ Municipality" or "Street, PLZ Municipality"
        address_patterns = [
            r'(\d{4}\s+[A-ZÄÖÜ][a-zäöüß]+)',  # PLZ + Ort
            # Full address
            r'([A-ZÄÖÜ][a-zäöüß\s]+\d+[a-z]?,\s*\d{4}\s+[A-ZÄÖÜ][a-zäöüß]+)',
        ]

        all_text = ' '.join(content.css('::text').getall())

        for pattern in address_patterns:
            match = re.search(pattern, all_text)
            if match:
                item['address'] = match.group(1).strip()
                # Extract PLZ
                plz_match = re.search(r'\b(\d{4})\b', item['address'])
                if plz_match:
                    item['plz'] = plz_match.group(1)
                break

        # Extract phone
        phone_patterns = [
            r'Tel(?:efon)?[:\s]+(\+43[\s\d/\-()]+)',
            r'Telefon[:\s]+(\d+[\s\d/\-()]+)',
        ]

        for pattern in phone_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                item['phone'] = match.group(1).strip()
                break

        # Extract fax
        fax_patterns = [
            r'Fax[:\s]+(\+43[\s\d/\-()]+)',
            r'Fax[:\s]+(\d+[\s\d/\-()]+)',
        ]

        for pattern in fax_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                item['fax'] = match.group(1).strip()
                break

        # Extract email
        email_link = content.css('a[href^="mailto:"]::attr(href)').get()
        if email_link:
            item['email'] = email_link.replace('mailto:', '').strip()
        else:
            # Try to find email in text
            email_match = re.search(
                r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', all_text)
            if email_match:
                item['email'] = email_match.group(1)

        # Extract website
        website_link = content.css('a[href^="http"]::attr(href)').get()
        if website_link and 'noe.gv.at' not in website_link:
            item['website'] = website_link.strip()

        yield item
