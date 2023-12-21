"""NOTIFICATION HANDLER"""
import sys
import os

sys.path.append("../")

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
