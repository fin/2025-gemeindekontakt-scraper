# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MunicipalityItem(scrapy.Item):
    """Item for Austrian municipality contact information."""

    # Basic information
    name = scrapy.Field()              # Municipality name
    bundesland = scrapy.Field()        # Federal state (Burgenland, Kärnten, etc.)
    bezirk = scrapy.Field()            # District (optional)
    plz = scrapy.Field()               # Postal code

    # Contact information
    address = scrapy.Field()           # Street address
    phone = scrapy.Field()             # Phone number
    fax = scrapy.Field()               # Fax number
    email = scrapy.Field()             # Email address
    website = scrapy.Field()           # Official website

    # Additional metadata
    source_url = scrapy.Field()        # URL where data was scraped from
    scraped_at = scrapy.Field()        # Timestamp of scraping
