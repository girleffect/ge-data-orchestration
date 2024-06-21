#!/usr/bin/python
"""MODULE TO LOG ERRORS AND SEND NOTIFICATIONS"""

# pylint: disable=broad-except
import sys
from typing import Union

from utils.notification_handler import slack_helper


def main() -> None:
    """
    Function to log errors.

    Reads input from sys.stdin and logs any error messages found.
    If an error message is found, it is printed and passed to the slack_helper function.
    """
    error_message: Union[str, None] = None

    for line in sys.stdin:
        error_message = ""
        error_message = f"{error_message}\n{line}"

    if error_message:
        print(error_message)
        slack_helper(error_message)


if __name__ == "__main__":
    main()
