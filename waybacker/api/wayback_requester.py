from typing import Optional, Dict

import requests

from waybacker.util.requester import get_with_retry, retry_with_delay


def request_get_snapshot(url) -> Optional[Dict]:
    data = requests.get(f'http://archive.org/wayback/available?url={url}').json()
    if 'closest' in data['archived_snapshots']:
        snapshot = data['archived_snapshots']['closest']
        assert snapshot['available'] is True, f'Snapshot not available: {url}'
        assert snapshot['url'] is not None, f'Snapshot URL is None: {url}'
        return snapshot
    return None


class WaybackRequester:
    def __init__(
            self,
            sleep_time_seconds: int,
            delay_after_error: int = 15 * 60,
            retry_attempts: int = 3

    ):
        self.sleep_time_seconds: int = sleep_time_seconds
        self.delay_after_error: int = delay_after_error
        self.retry_attempts: int = retry_attempts

    def get_from_wayback(self, url: str) -> Optional[Dict]:

        available_page_data: Optional[Dict] = retry_with_delay(
            lambda: request_get_snapshot(url), self.retry_attempts, self.delay_after_error
        )
        print('available_page_data', available_page_data)
        if not available_page_data:
            return {
                'success': False,
                'error': 'not in wayback',
                'error_type': 'unavailable'
            }

        assert 'url' in available_page_data and available_page_data['url'] is not None
        res: requests.Response = get_with_retry(available_page_data['url'], self.retry_attempts, self.delay_after_error)
        mime_type: str = res.headers['content-type']

        if 'application/pdf' in mime_type:
            result_type: str = 'pdf'
            content = res.content
        elif 'text/html' in mime_type:
            result_type: str = 'html'
            content = res.text
        else:
            return {
                'success': False,
                'error': f'Unknown mime-type: "{mime_type}"',
                'error_type': 'mime-type'
            }

        return {
            'success': True,
            'url': url,
            'mime_type': result_type,
            'content': content,
            'wayback_data': available_page_data
        }

