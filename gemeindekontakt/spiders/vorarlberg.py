"""Spider for scraping Vorarlberg municipalities."""

import scrapy
from datetime import datetime
from gemeindekontakt.items import MunicipalityItem
import re


class VorarlbergSpider(scrapy.Spider):
    """
    Scrapes Vorarlberg municipalities from simple text list.

    Source: https://vorarlberg.at/-/auflistung-aller-vorarlberger-staedte-gemeinden-und-ihrer-e-mail-kontaktadresse

    HTML structure:
    Simple list with municipality names and email links:
    Municipality Name [email@domain.at](mailto:email@domain.at)
    """

    name = "vorarlberg"
    allowed_domains = ["vorarlberg.at"]
    start_urls = ["https://vorarlberg.at/-/auflistung-aller-vorarlberger-staedte-gemeinden-und-ihrer-e-mail-kontaktadresse"]

    # Use wget-style user agent since the site rejects curl/scrapy default
    custom_settings = {
        'USER_AGENT': 'Wget/1.21.3'
    }

    def parse(self, response):
        """Parse text list and extract municipality data."""
        # Find all text nodes that contain municipality information
        # The page has a simple structure: Municipality name followed by email link

        # Get all text content from the main content area
        content_area = response.css('article.article-content, .content, main')

        if not content_area:
            # Fallback to body if no specific content area found
            content_area = response.css('body')

        # Extract all mailto links (emails)
        email_links = content_area.css('a[href^="mailto:"]')

        for email_link in email_links:
            email = email_link.css('::attr(href)').get()
            if email:
                email = email.replace('mailto:', '').strip()

                # Get the text before the email link as municipality name
                # We need to navigate backwards from the email link
                text_before = email_link.xpath('preceding-sibling::text()[1]').get()

                if text_before:
                    # Clean up the municipality name
                    name = text_before.strip()

                    # Remove any leading/trailing whitespace or special characters
                    name = re.sub(r'^\s*[-–]\s*', '', name)
                    name = re.sub(r'\s+', ' ', name)

                    if name:  # Only yield if we have a valid name
                        item = MunicipalityItem()
                        item['bundesland'] = 'Vorarlberg'
                        item['name'] = name
                        item['email'] = email
                        item['scraped_at'] = datetime.now().isoformat()
                        item['source_url'] = response.url

                        yield item
