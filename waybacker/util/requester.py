import logging
from typing import Callable, Any
import time

import requests


def retry_with_delay(fn: Callable, num_retries: int, num_delay: int) -> Any:
    """
    Retry a provided function multiple times. After each failed attempt (any error), a pause is taken.

    Parameters
    -----------
        fn: Callable
            A function that is called (without parameters) until successful, or maximum number of retries reached.
        num_retries: int
            Maximum number of attempts.
        num_delay: int
            Number of seconds to wait after a failed attempt.

    Return
    -------
        result: Any
            The result of the provided callback function.
    """
    success: bool = False
    counter = 0
    error = None
    while not success and counter < num_retries:
        try:
            return fn()
        except Exception as err:
            logging.warning(f'{err}')
            logging.warning(f'Wait for: {num_delay} seconds.')
            time.sleep(num_delay)
            counter += 1
            error = err
    raise error


def get_with_retry(url: str, num_retries: int, num_delay: int) -> requests.Response:
    """
    Send a GET request to the specified url and allow errors.

    Parameters
        url: str
            Destination of the GET request.
        num_retries: int
            Maximum number of attempts.
        num_delay: int
            Number of seconds to wait after a failed attempt.

    Return
        response: Response
            object from the GET request.

    """
    logging.info(f'GET Request: {url}')
    return retry_with_delay(
        lambda: requests.get(url), num_retries, num_delay
    )

