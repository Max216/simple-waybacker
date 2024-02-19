import os
from os.path import join
from pathlib import Path
from typing import Dict

from waybacker.db.sqlite_wayback_db import SqliteWaybackDB
from waybacker.db.wayback_db import WaybackDB


def get_default_initialization() -> Dict:
    """
    Get the dfault parameters for the Waybacker. Environment variables are considered.

        Return
        -------

        initialization_dict: dict
            Initialization parameters about the database and sleep timeouts.
    """

    directory: str = os.getenv('WAYBACKER_DIR') or join(Path.home(), 'waybacker')
    db_backend: str = os.getenv('WAYBACKER_DB') or 'sqlite'
    sleep_time_seconds: int = int(os.getenv('WAYBACKER_SLEEP') or 1)
    return {
        'directory': directory,
        'db_backend': db_backend,
        'sleep_time_seconds': sleep_time_seconds
    }


def get_wayback_db(db_backend: str, directory: str) -> WaybackDB:
    if db_backend == 'sqlite':
        return SqliteWaybackDB(directory)
    else:
        raise ValueError(f'"db_backend" must be one of: "sqlite"!')
