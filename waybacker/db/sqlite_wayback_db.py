import os
import shutil
import sqlite3
from datetime import datetime
from os.path import join, exists
from sqlite3 import Connection, Cursor
from typing import Dict, Optional, List, Tuple, Iterable

from waybacker.db.wayback_db import WaybackDB
from waybacker.components.wayback_entry import WaybackEntry


def result_to_sql_dict(result: Dict, download_file_name: Optional[str], url: str) -> Dict:
    return_dict: Dict = {
        'url': result['url'] if 'url' in result else url,
        'success': 1 if result['success'] else 0,
        'mime_type': result['mime_type'] if 'mime_type' in result else None,
        'download_file_name': download_file_name,
        'collected_at': str(datetime.now()),
        'error': result['error'] if 'error' in result else None,
        'error_type': result['error_type'] if 'error' in result else None
    }

    if 'wayback_data' in result and result['wayback_data'] is not None:
        return_dict['wayback_status'] = int(result['wayback_data']['status'])
        return_dict['wayback_available'] = 1 if result['wayback_data']['available'] else 0
        return_dict['wayback_url'] = result['wayback_data']['url']
        return_dict['wayback_timestamp'] = result['wayback_data']['timestamp']
    else:
        return_dict['wayback_status'] = 0
        return_dict['wayback_available'] = 0
        return_dict['wayback_url'] = None
        return_dict['wayback_timestamp'] = None

    return return_dict


class SqliteWaybackDB(WaybackDB):

    def entries(self) -> Iterable[WaybackEntry]:
        cursor: Cursor = self.connection.cursor()
        result: Cursor = cursor.execute(
            """
            SELECT 
            url, success, mime_type, wayback_status, wayback_available, wayback_url, wayback_timestamp,
            download_file_name, collected_at, error, error_type FROM wayback_entry
            """
        ).fetchall()
        for entry in result:
            yield self.sql_to_wayback_entry(entry)

        cursor.close()

    def copy_wayback_entry(self, entry_other: WaybackEntry, pages_directory_other: str):
        if entry_other.success:
            page_src: str = join(pages_directory_other, entry_other.file_name)
            page_dest: str = join(self.download_directory, entry_other.file_name)
            shutil.copyfile(page_src, page_dest)

        self.add_webpage_entry(entry_other.url, entry_other.to_dict(), entry_other.file_name)

    def __init__(self, directory: str):
        self.db_file_path: str = join(directory, 'wayback.db')
        if not exists(directory):
            os.makedirs(directory)
        self.connection: Connection = sqlite3.connect(self.db_file_path)

        super().__init__(directory)
        if not exists(self.download_directory):
            os.makedirs(self.download_directory)

    def get(self, url: str) -> Optional[WaybackEntry]:
        cursor: Cursor = self.connection.cursor()
        result: Cursor = cursor.execute(
            """
            SELECT
            url, success, mime_type, wayback_status, wayback_available, wayback_url, wayback_timestamp,
            download_file_name, collected_at, error, error_type 
            FROM wayback_entry
            WHERE url = ?
            """, (url, )
        )

        found = result.fetchall()
        assert len(found) < 2
        if len(found) > 0:
            wayback_entry: WaybackEntry = self.sql_to_wayback_entry(
                found[0], [
                    'url', 'success', 'mime_type', 'wayback_status', 'wayback_available', 'wayback_url', 'wayback_timestamp',
                    'download_file_name', 'collected_at', 'error', 'error_type'
                ]
            )
            cursor.close()
            return wayback_entry
        else:
            cursor.close()
            return None

    def add_webpage_entry(self, url: str, result: Dict, file_name: str) -> WaybackEntry:
        cursor: Cursor = self.connection.cursor()

        sql_dict: Dict = result_to_sql_dict(result, file_name, url)
        values: List[str] = [sql_dict[k] for k in [
            'url', 'success', 'mime_type', 'wayback_status', 'wayback_available', 'wayback_url', 'wayback_timestamp',
            'download_file_name', 'collected_at', 'error', 'error_type'
        ]]

        cursor.executemany(
            """
            INSERT OR REPLACE INTO wayback_entry (
                url, success, mime_type, wayback_status, wayback_available, wayback_url, wayback_timestamp,
                download_file_name, collected_at, error, error_type
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (values, )
        )
        cursor.close()
        self.connection.commit()

        db_entry: WaybackEntry = self.get(url)
        assert db_entry is not None
        return db_entry

    def _is_created(self) -> bool:
        cursor: Cursor = self.connection.cursor()
        result: Cursor = cursor.execute("""
            SELECT name from sqlite_master WHERE name = 'wayback_entry';
        """)

        is_created: bool = len(result.fetchall()) > 0
        cursor.close()
        return is_created

    def _create_db(self) -> None:
        cursor: Cursor = self.connection.cursor()
        cursor.execute(
            """
            CREATE TABLE wayback_entry(
            url TEXT NOT NULL PRIMARY KEY,
            success INT NOT NULL,
            mime_type TEXT,
            wayback_status INT,
            wayback_available INT,
            wayback_url TEXT,
            wayback_timestamp TEXT,
            download_file_name TEXT,
            collected_at TEXT,
            error TEXT,
            error_type TEXT
            );
            """
        )
        cursor.close()

    def sql_to_wayback_entry(self, sql_row: Tuple, field_names: Optional[List[str]] = None) -> WaybackEntry:

        if field_names is None:
            field_names = [
                'url', 'success', 'mime_type', 'wayback_status', 'wayback_available', 'wayback_url',
                'wayback_timestamp',
                'download_file_name', 'collected_at', 'error', 'error_type'
            ]

        if not len(field_names) == len(sql_row):
            raise ValueError(f'Row and fields have different size: {len(sql_row)} vs {len(field_names)}!')

        sql_dict = {
            field: sql_row[i] for i, field in enumerate(field_names)
        }

        return WaybackEntry(
            success=sql_dict['success'] == 1,
            error=sql_dict['error'],
            error_type=sql_dict['error_type'],
            mime_type=sql_dict['mime_type'],
            url=sql_dict['url'],
            file_name=sql_dict['download_file_name'],
            wayback_data={
                'status': sql_dict['wayback_status'],
                'available': sql_dict['wayback_available'] == 1,
                'url': sql_dict['wayback_url'],
                'timestamp': sql_dict['wayback_timestamp']
            },
            collected_at=sql_dict['collected_at'],
            download_directory=self.download_directory
        )
