import logging
from typing import Optional, Dict, List, Iterable

import pandas as pd
from tqdm import tqdm

from waybacker.api.wayback_requester import WaybackRequester
from waybacker.components.wayback_entry import WaybackEntry
from waybacker.db.wayback_db import WaybackDB
from waybacker.init.initialization import get_default_initialization, get_wayback_db


def normalize_url(url: str) -> str:
    url = url.split('#')[0]
    if url.endswith('/'):
        url = url[:-1]
    return url.strip()


class Waybacker:
    """
    A proxy class to collect webpages from the wayback machine.
    """

    def __init__(
            self,
            directory: Optional[str] = None,
            db_backend: Optional[str] = None,
            sleep_time_seconds: Optional[int] = None
    ):
        """
        Initialize the waybacker.
        :param directory: Directory that will contain the database and all downloaded webpages.
        :param db_backend: Either 'sqlite' or 'json'.
        :param sleep_time_seconds: Seconds to wait before querying wayback.
        """
        # Setup parameters
        default_arguments: Dict = get_default_initialization()
        self.directory: str = directory or default_arguments['directory']
        self.sleep_time_seconds: int = sleep_time_seconds or default_arguments['sleep_time_seconds']

        self._validate()

        db_backend: str = db_backend or default_arguments['db_backend']
        self.wayback_db: WaybackDB = get_wayback_db(db_backend=db_backend, directory=self.directory)
        self.wayback_requester: WaybackRequester = WaybackRequester(sleep_time_seconds=sleep_time_seconds)

        logging.info(f'Waybacker initialized at "{self.directory}".')

    def lookup(self, url: str):
        url = normalize_url(url)
        wayback_entry: Optional[WaybackEntry] = self.wayback_db.get(url)
        return wayback_entry

    def get(
            self,
            url: str,
            retry_unsuccessful: bool = False,
            overwrite_entry: bool = False
    ) -> WaybackEntry:
        """
        Request a page via GET request from Wayback. By default, only new requests are forwarded to wayback. If the
        requested url was requested before, the corresponding entry (successful and unsuccessful) is returned instead.

        :param url: The url that is retrieved.
        :param retry_unsuccessful: If set to true, requested URLs are retried, if they led to errors in Wayback
            previously.
        :param overwrite_entry:
            The entry for the URL is requested rom Wayback and overwrites the previous entry. DANGER: This may affect
            the reproducibility if the new version differs from the previous version.
        """

        logging.info(f'Request for webpage: "{url}".')
        url = normalize_url(url)
        wayback_entry: Optional[WaybackEntry] = self.wayback_db.get(url)

        # In these cases the page must be requested
        if wayback_entry is None or overwrite_entry or (wayback_entry.has_error() and retry_unsuccessful):
            logging.info(f'Request webpage ("{url}") from he live Wayback Machine.')
            wayback_result: Dict = self.wayback_requester.get_from_wayback(url)
            wayback_entry = self.wayback_db.add_webpage(url, wayback_result)
            logging.info(f'Status for webpage {url}: {wayback_entry.success}')

        assert wayback_entry is not None
        return wayback_entry

    def export_csv(self, urls: List[str], dest_path: str) -> pd.DataFrame:
        entries: Iterable[WaybackEntry] = map(self.get, urls)
        df: pd.DataFrame = pd.DataFrame.from_records(map(lambda entry: entry.to_record(), entries))
        df.to_csv(dest_path, index=False)
        return df

    def get_db(self) -> WaybackDB:
        return self.wayback_db

    def absorb_wayback_db(self, db: WaybackDB):
        for entry in tqdm(list(db.entries())):
            if self.wayback_db.get(entry.url) is None:
                self.wayback_db.copy_wayback_entry(entry, db.download_directory)

    def _validate(self):
        """
        Validate the initialization parameters.
        """
        if self.directory is None:
            raise ValueError(f'No "directory" is provided!')

        if self.sleep_time_seconds < 0:
            raise ValueError(f'Values for "sleep_time_seconds" cannot be negative!')
