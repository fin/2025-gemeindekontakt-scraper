"""Spider for scraping Wien municipality data."""

import scrapy
from datetime import datetime
from gemeindekontakt.items import MunicipalityItem


class WienSpider(scrapy.Spider):
    """
    Scrapes Wien (Vienna) municipality contact information.

    Source: TBD - Source URL needs to be determined

    Note: Wien is both a Bundesland and a municipality (Stadtgemeinde).
    It has 23 districts (Bezirke) but functions as a single municipality
    at the state level.
    """

    name = "wien"
    allowed_domains = ["wien.gv.at"]
    # TODO: Update with actual source URL once determined
    start_urls = ["https://www.wien.gv.at/"]

    custom_settings = {
        'LOG_LEVEL': 'INFO'
    }

    def parse(self, response):
        """
        Parse Wien municipality data.

        TODO: This spider needs to be implemented once the data source is identified.
        Possible sources:
        - https://www.wien.gv.at/amtshelfer/
        - https://www.wien.gv.at/kontakt/
        - Vienna Open Data Portal
        """
        self.logger.warning(
            "Wien spider not yet implemented. Source URL needs to be determined. "
            "Wien is a special case as it is both a Bundesland and a municipality."
        )

        # For now, return a single entry for Wien as a whole
        item = MunicipalityItem()
        item['bundesland'] = 'Wien'
        item['name'] = 'Wien'
        item['scraped_at'] = datetime.now().isoformat()
        item['source_url'] = response.url

        # TODO: Add actual contact information once source is determined

        yield item
