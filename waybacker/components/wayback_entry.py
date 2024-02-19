import json
import os.path
from os.path import join
from typing import Dict, Optional


class WaybackEntry:

    def __init__(
            self,
            success: bool,
            error: str,
            error_type: str,
            mime_type: str,
            url: str,
            file_name: str,
            wayback_data: Dict,
            collected_at: str,
            download_directory: str
    ):
        self.success: bool = success
        self.error: str = error
        self.error_type: str = error_type
        self.mime_type: str = mime_type
        self.url: str = url
        self.file_name: str = file_name
        self.collected_at: str = collected_at
        self.wayback_data: Dict = wayback_data

        self.full_path: Optional[str] = None
        if self.success:
            self.full_path = os.path.abspath(join(download_directory, self.file_name))

    def to_record(self):
        return {
            "url": self.url,
            "wayback_url": self.wayback_data['url'],
            "wayback_timestamp": self.wayback_data['timestamp'],
            "exists": self.success,
            "mime": self.mime_type
        }

    def to_dict(self) -> Dict:
        return {
            'success': self.success,
            'error': self.error,
            'error_type': self.error_type,
            'mime_type': self.mime_type,
            'url': self.url,
            'file_name': self.file_name,
            'collected_at': self.collected_at,
            'wayback_data': self.wayback_data,
            'full_path': self.full_path
        }

    def has_error(self) -> bool:
        return not self.success

    def __str__(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

