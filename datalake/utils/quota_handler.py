"""RETRY HANDLER"""
# pylint: disable=inconsistent-return-statements,unused-import
import sys
import os
import time
from functools import wraps

# from random import random
from typing import Union

from utils.notification_handler import slack_helper


def retry_handler(
    exceptions,
    total_tries: int = 4,
    initial_wait: float = 0.5,
    backoff_factor: int = 2,
    should_raise: bool = False,
):
    """
    Decorator - managing API failures

    args:
        exceptions (Exception): Exception instance or list of
        Exception instances to catch & retry
        total_tries (int): Total retry attempts
        initial_wait (float): initial delay between retry attempts in seconds
        backoff_factor (int): multiplier used to further randomize back off
        should_raise (bool): Raise exception after all retires fail

    return:
        wrapped function's response
    """

    def retry_decorator(function):
        @wraps(function)
        def func_with_retries(*args, **kwargs):
            """wrapper function to decorate function with retry functionality"""
            _tries, _delay = total_tries, initial_wait
            msg: str = ""
            while _tries > 0:
                try:
                    print(f"attempt {total_tries + 1 - _tries}")
                    return function(*args, **kwargs)
                except exceptions as exception:
                    # get logger message
                    if _tries == 1:
                        slack_helper(
                            text=str(
                                f"Function: {function.__name__}\n"
                                f"Failed despite best efforts after {total_tries} tries\n"
                                f"Exception {exception}."
                            )
                        )

                        if should_raise:
                            raise exception
                    else:
                        msg = str(
                            f"Function: {function.__name__}\n"
                            f"Exception {exception}.\n"
                            f"Retrying in {_delay} seconds!"
                        )
                    # log with print
                    print(msg)
                    # decrement _tries
                    _tries -= 1
                    # pause
                    time.sleep(_delay)
                    # increase delay by backoff factor
                    _delay = _delay * backoff_factor

        return func_with_retries

    return retry_decorator


def api_handler(wait: Union[float, int] = 0, backoff_factor: Union[float, int] = 0.01):
    """Decorator - managing API failures

    Args:
        wait (Union[float, int], optional): _description_. Defaults to 0.
        backoff_factor (Union[float, int], optional): _description_. Defaults to 0.01.
    Return:
        wrapped function's response
    """

    def retry_decorator(function):
        @wraps(function)
        def func_with_retries(*args, **kwargs):
            """wrapper function to decorate function with retry functionality"""

            print(f"waiting {wait} seconds before attempt")
            time.sleep(wait)
            return function(*args, **kwargs)

        return func_with_retries

    return retry_decorator
