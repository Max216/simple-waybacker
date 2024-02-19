import json
import logging
from datetime import datetime
from typing import List, Iterable, Optional

import requests
from bs4 import BeautifulSoup, Tag
from waybacker.util.requester import get_with_retry


class UrlEntry:
    """
    Result class of the URLCollector.
    """

    def __init__(self, url: str, page: int, collected_from: str):
        self.url: str = url
        self.page: int = page
        self.collected_from: str = collected_from

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {
            'url': self.url, 'page': self.page, 'collected_from': self.collected_from
        }


class LiveURLCollector:
    """
    Collects URLs from a live webpage by iterating over the pagination menu.
    """

    PAGE_PLACEHOLDER: str = '@@PAGE@@'

    def __init__(
            self,
            link_query: str,
            overview_iterator: str,
            start_page_index: int = 1,
            sleep_time: int = 1
    ):

        """
        Parameters
        -----------
            link_query: string
                HTML selector to locate the <a></a> links that refer to the URLs to be collected.

            overview_iterator: string
                URL used for pagination. Must include the placeholder "@@PAGE@@".

            start_page_index: int
                First page index to be used (will replace "@@PAGE@@").

            sleep_time: int
                Sleep time in seconds before increasing the start_page_index.
        """
        self.link_query: str = link_query
        self.overview_iterator: str = overview_iterator
        self.start_page_index: int = start_page_index
        self.sleep_time: int = sleep_time

        if LiveURLCollector.PAGE_PLACEHOLDER not in self.overview_iterator:
            raise ValueError(
                f'You must include "{LiveURLCollector.PAGE_PLACEHOLDER}" in "overview_iterator" to iterate over overview pages'
            )

    def collect_urls(self, max_links: Optional[int] = None) -> Iterable[UrlEntry]:
        """
        Collect URLs of the provided webpage via pagination.

        Parameters
        -----------
            max_links: int (optional)
                If provided, pagination stops after "max_links" links have been found.

        Return
        -------
            result: List
                The collected links.
        """
        found_urls: bool = True
        current_page_index: int = self.start_page_index
        current_page_count: int = 0
        while found_urls:
            current_overview_page_url: str = self.overview_iterator.replace('@@PAGE@@', str(current_page_index))

            logging.info(f'[{datetime.now()}] request {current_overview_page_url}')
            result: requests.Response = get_with_retry(current_overview_page_url, num_retries=5, num_delay=60*5)

            soup = BeautifulSoup(result.text, features='html.parser')
            link_entries: List[Tag] = soup.select(self.link_query)

            urls_on_page: Iterable[str] = map(lambda a: a['href'].strip(), link_entries)
            urls_on_page: List[str] = list(filter(lambda a: len(a) > 0, urls_on_page))

            found_urls = len(urls_on_page) > 0

            for url in urls_on_page:
                current_page_count += 1
                if current_page_count <= max_links:
                    yield UrlEntry(url, current_page_index, current_overview_page_url)

            current_page_index += 1

