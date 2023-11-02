"""MODULE TO LOG ERRORS AND SEND NOTIFICATIONS"""
# pylint: disable=broad-except
import sys
import os
from typing import Union
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def slack_helper(text: str, channel: str = "data-platform-alerts") -> None:
    """SLACK NOTIFICATION HELPER"""
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

    try:
        _ = client.chat_postMessage(channel=channel, text=text)
    except SlackApiError as err:
        # You will get a SlackApiError if "ok" is False
        error_msg = err.response["error"]
        print(f"Got an error: {error_msg}")
        if err.response["ok"] is False:
            raise Exception(error_msg) from err


def main() -> None:
    """function to log errors"""
    error_message: Union[str, None] = None

    for line in sys.stdin:
        error_message = ""
        error_message = f"{error_message}\n{line}"

    if error_message:
        print(error_message)
        slack_helper(error_message)


if __name__ == "__main__":
    main()
