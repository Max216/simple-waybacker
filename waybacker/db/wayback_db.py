from os.path import join
from typing import Optional, Dict, Any, Iterable

from waybacker.components.wayback_entry import WaybackEntry
from waybacker.util.file_utils import url_to_file_name, write_text, write_file


class WaybackDB:
    def __init__(self, directory: str):
        self.directory: str = directory
        self.download_directory: str = join(directory, 'pages')

        if not self._is_created():
            self._create_db()

    def get(self, url: str) -> Optional[WaybackEntry]:
        raise NotImplementedError()

    def add_webpage(self, url: str, result: Dict) -> WaybackEntry:
        file_name: str = ''
        if result['success']:
            file_name = self.store_webpage(url, result['content'], result['mime_type'])

        return self.add_webpage_entry(url, result, file_name)

    def add_webpage_entry(self, url: str, result: Dict, file_name: str) -> WaybackEntry:
        raise NotImplementedError()

    def _is_created(self) -> bool:
        raise NotImplementedError()

    def _create_db(self) -> None:
        raise NotImplementedError()

    def entries(self) -> Iterable[WaybackEntry]:
        raise NotImplementedError()

    def copy_wayback_entry(self, entry_other: WaybackEntry, pages_directory_other: str):
        raise NotImplementedError()

    def store_webpage(self, url: str, content: Any, mime_type: str) -> str:
        assert mime_type in {'pdf', 'html'}
        file_name: str = url_to_file_name(url, mime_type)
        file_path: str = join(self.download_directory, file_name)

        if mime_type == 'html':
            write_text(file_path, content)
        else:
            write_file(file_path, content)

        return file_name
