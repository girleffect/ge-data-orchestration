#!/usr/bin/python
"""YOUTUBE API READER"""
# pylint: disable=unused-import
import sys
import os
from datetime import date, timedelta
from typing import Generator, Any, Dict

sys.path.append("../")


from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

from utils.file_handlers import load_file
from utils.date_handlers import string_to_date, date_iterator
from utils.quota_handler import retry_handler, api_handler


class YouTubeException(Exception):
    """Base class exception"""


class QuotaLimitError(YouTubeException):
    """Class for QuotaLimit"""


class UncapturedError(YouTubeException):
    """Class for UncapturedError"""


class YouTubeAPIAuthenticator:
    """YoutubeAPI Authenticator"""

    def __init__(self, creds_file: str):
        self.creds = load_file(creds_file)
        self.youtube = self.get_youtube_service()
        self.youtube_analytics = self.get_youtube_analytics_service()

    def get_youtube_service(self):
        """method to get youtube service"""
        credentials = self.refresh_credentials()
        return build(serviceName="youtube", version="v3", credentials=credentials)

    def get_youtube_analytics_service(self):
        """method to get youtube abalytics service"""
        # https://developers.google.com/youtube/analytics/
        # channel_reports#basic-user-activity-statistics
        credentials = self.refresh_credentials()
        return build(
            serviceName="youtubeAnalytics", version="v2", credentials=credentials
        )

    def refresh_credentials(self):
        """method to refresh credentials"""
        credentials = Credentials(
            **self.creds,
            scopes=[
                "https://www.googleapis.com/auth/youtube.readonly",
                "https://www.googleapis.com/auth/yt-analytics.readonly",
            ],
        )

        print("Validity of credentials:", credentials.valid)
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                print("Refreshing Access Token...")
                credentials.refresh(Request())
            else:
                print("CREDENTIALS ARE EMPTY")
        return credentials


class YouTubeReader:
    """class to read data from youtube"""

    def __init__(self, authenticator: YouTubeAPIAuthenticator, env="dev"):
        self.authenticator = authenticator
        self.channels: list = []
        self.videos: list = []
        self.channel_videos: dict = {}
        self.set_environment(env)

    def set_environment(self, env) -> None:
        """METHOD TO DISABLE OAUTHLIB VERIFICATION"""
        # Disable OAuthlib's HTTPs verification when running locally.
        # *DO NOT* leave this option enabled when running in production.
        if env != "dev":
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    def build_query(
        self, configs: dict, endpoint: str, ids: str, startdate: str, enddate: str
    ) -> dict:
        """method for building query"""
        # _ = configs.pop("start_date", None), configs.pop("end_date", None)
        curr_configs = dict([(k, v) for k, v in configs.items()])
        extra_args = {
            "ids": f"channel=={ids}",
            "startDate": startdate,
            "endDate": enddate,
            "metrics": ",".join([metric for metric in curr_configs.pop("metrics")]),
            "dimensions": ",".join([dim for dim in curr_configs.pop("dimensions")]),
        }
        curr_configs.update(extra_args)
        if endpoint in ["video_stats", "traffic_source"]:
            curr_configs["filters"] = f"video=={curr_configs['filters']}"

        return curr_configs

    @retry_handler(
        exceptions=QuotaLimitError, initial_wait=3, total_tries=3, backoff_factor=2
    )
    @retry_handler(
        exceptions=UncapturedError, initial_wait=3, total_tries=3, backoff_factor=2
    )
    @api_handler(wait=1, backoff_factor=2)
    def get_stats(
        self, ids: str, endpoint: str, startdate: str, enddate: str, configs: dict
    ) -> dict:
        """method to fetch a channel_analytics"""
        try:
            params = self.build_query(
                configs=configs,
                endpoint=endpoint,
                ids=ids,
                startdate=startdate,
                enddate=enddate,
            )
            request = self.authenticator.youtube_analytics.reports().query(**params)

            results: dict = request.execute()
            # print(f"length of {endpoint } results: {len(results)}")

            return results
        except HttpError as err:
            if err.resp.status in [429]:
                raise QuotaLimitError(err.reason) from err
        except Exception as err:
            raise UncapturedError(err) from err

    def __unpack_channel(self, channel_obj) -> dict:
        """method to unpack channel object"""
        return {
            "channel_name": channel_obj["snippet"]["title"],
            "channel_id": channel_obj["id"],
            "channel_startdate": channel_obj["snippet"]["publishedAt"][:10],
            "channel_playlistid": channel_obj["contentDetails"]["relatedPlaylists"][
                "uploads"
            ],
            "channel": channel_obj,
        }

    def __unpack_video(self, video_obj, config_dict: dict):
        """method to unpack video object"""
        video_id = video_obj["snippet"]["resourceId"]["videoId"]
        config_dict.update({"filters": video_id})
        return {
            "video_id": video_id,
            "video_name": video_obj["snippet"]["title"],
            "video_startdate": video_obj["snippet"]["publishedAt"][:10],
            "video_config": config_dict,
        }

    def get_channels(self, configs: dict) -> Generator[Dict[Any, Any], None, None]:
        """method to get channels"""
        print("getting channels")
        start_date = string_to_date(configs.pop("start_date", "today"))
        request = self.authenticator.youtube.channels().list(
            part=",".join([val for val in configs["part"]]),
            mine=configs.get("part", True),
        )
        response = request.execute()
        for _channel in response["items"]:
            channel_data = self.__unpack_channel(channel_obj=_channel)
            yield {
                "data": channel_data,
                "date": start_date.strftime("%Y-%m-%d"),
                "channel_data": channel_data,
            }
            self.channels.append(channel_data)

    def fetch_channel_videos(self, channel: dict) -> list:
        """method to get all channel videos"""
        channel_name = channel["channel_name"]
        playlistid = channel["channel_playlistid"]
        channel_videos: list = []
        request = self.authenticator.youtube.playlistItems().list(
            part="snippet,contentDetails,id,status",
            maxResults=50,
            playlistId=playlistid,
        )

        while request:
            response = request.execute()
            if response.items:
                _videos: list = response["items"]
                channel_videos += _videos

            request = self.authenticator.youtube.playlistItems().list_next(
                request, response
            )
        self.channel_videos.setdefault(channel_name, []).extend(channel_videos)
        return channel_videos

    def get_videos(
        self, configs: dict, endpoint: str
    ) -> Generator[Dict[Any, Any], None, None]:
        """method to get video stats"""
        start_date = configs.pop("start_date", "2_days_ago")
        end_date = configs.pop("end_date", "1_day_ago")
        interval = configs.pop("interval", "1_day")

        for channel in self.channels:
            channel_name = channel["channel_name"]
            videos = self.channel_videos[channel_name]
            for start_date, end_date in date_iterator(
                start_date=start_date,
                end_date=end_date,
                interval=interval,
                end_inclusive=True,
                time_format="%Y-%m-%d",
            ):
                for video in videos:
                    video = self.__unpack_video(video, configs)
                    metadata = {
                        "channelId": channel["channel_id"],
                        "videoId": video["video_id"],
                    }
                    result = self.get_stats(
                        endpoint=endpoint,
                        ids=channel["channel_id"],
                        startdate=start_date,
                        enddate=end_date,
                        configs=video["video_config"],
                    )
                    result.update(metadata)
                    yield {
                        "data": result,
                        "date": start_date,
                        "channel_data": channel,
                        "file_suffix": f"-{video['video_id']}",
                    }

    def get_other_stats(self, configs: dict) -> Generator[Dict[Any, Any], None, None]:
        """method to get other stats"""
        for channel in self.channels:
            for endpoint, config in configs.items():
                start_date = config.pop("start_date", "2_days_ago")
                end_date = config.pop("end_date", "1_day_ago")
                interval = config.pop("interval", "1_day")
                for start_date, end_date in date_iterator(
                    start_date=start_date,
                    end_date=end_date,
                    interval=interval,
                    end_inclusive=True,
                    time_format="%Y-%m-%d",
                ):
                    result = self.get_stats(
                        endpoint=endpoint,
                        ids=channel["channel_id"],
                        startdate=start_date,
                        enddate=end_date,
                        configs=config,
                    )
                    yield {
                        "data": result,
                        "date": start_date,
                        "channel_data": channel,
                        "endpoint": endpoint,
                    }

    def get_channel_videos(self):
        """method to get back channel videos"""
        start_date = string_to_date("today")
        for channel in self.channels:
            channel_videos = self.fetch_channel_videos(channel=channel)
            yield {
                "data": channel_videos,
                "date": start_date.strftime("%Y-%m-%d"),
                "channel_data": channel,
            }
