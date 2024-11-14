#!/usr/bin/python
"""FACEBOOK API READER"""
# import os
import sys
import warnings
import logging

# import copy
from typing import Generator, Any, Dict, List
from datetime import datetime

from facebook_business.adobjects.page import Page
from facebook_business.adobjects.iguser import IGUser
from facebook_business.adobjects.user import User
from facebook_business.adobjects.igmedia import IGMedia

sys.path.append("../")

from utils.quota_handler import retry_handler, api_handler

warnings.filterwarnings("ignore", category=UserWarning)
logger = logging.getLogger(__name__)


class ErrorHanlder:
    """Class meant to handle errors in the Facebook API Reader"""

    def __init__(self):
        self.error_list: List[Any] = []


class FacebookException(Exception):
    """Base class exception for Facebook"""


class MediaEngagements:
    """Instagram Media Insights Reader"""

    def __init__(self, authenticator, configs: dict):
        self.authenticator = authenticator
        self.configs = configs
        self.error_handler = ErrorHanlder()

    @staticmethod
    def _get_account_id(page) -> str:
        ig_business_account = Page(page.get_id()).api_get(
            fields=["instagram_business_account"]
        )
        if "instagram_business_account" not in ig_business_account:
            logger.info(f"NO INSTAGRAM BUSINESS ACCOUNT LINKED TO PAGE {page.get_id()}")
            return None
        return ig_business_account["instagram_business_account"]["id"]

    @staticmethod
    def _get_username(ig_business_account_id) -> str:
        ig_user = IGUser(ig_business_account_id).api_get(fields=["username"])
        ig_account_username: str = ig_user["username"]
        return ig_account_username

    @staticmethod
    def get_params(media, extra_params: bool = False) -> Dict[str, Any]:
        """function to automatically generate api params"""
        if extra_params:
            if (
                media["media_type"] in ["IMAGE", "VIDEO"]
                and media["media_product_type"] != "REELS"
                and "/tv/" not in media["permalink"]
            ):
                return {"metric": ["profile_activity"], "breakdown": "action_type"}

        if "/tv/" in media["permalink"] or media["media_type"] in ["CAROUSEL_ALBUM"]:
            return {"metric": ["impressions", "reach", "saved"]}
        if "/tv/" in media["permalink"] or (
            media["media_type"] in ["IMAGE", "VIDEO", "CAROUSEL_ALBUM"]
            and media["media_product_type"] == "REELS"
        ):
            return {
                "metric": ["reach", "plays", "likes", "comments", "shares", "saved"]
            }
        if (
            media["media_type"] in ["IMAGE", "VIDEO"]
            and media["media_product_type"] != "REELS"
        ):
            return {
                "metric": [
                    "impressions",
                    "reach",
                    "likes",
                    "comments",
                    "shares",
                    "saved",
                ]
            }
        logger.info("ERROR: ANOTHER MEDIA")
        logger.info(media)
        return {}

    @retry_handler(
        exceptions=ConnectionError, initial_wait=3, total_tries=3, backoff_factor=2
    )
    @api_handler(wait=1, backoff_factor=2)
    def _fetch_media_insights(self, media: dict, extra_params: bool) -> List[Any]:
        """method to call IGMedia Endpoint"""
        try:
            params = self.get_params(media, extra_params=extra_params)
            insights_data: List[Any] = []
            fields: List[str] = []
            ig_media_insights = IGMedia(media["id"]).get_insights(
                fields=fields, params=params
            )
            if not ig_media_insights:
                return insights_data
            _ = [insights_data.append(item._json) for item in ig_media_insights]
            return insights_data

        except ConnectionError as err:
            raise ConnectionError(err) from err
        except Exception as err:
            logger.info(f"ERROR: {err}")
            error_msg = f"media_id: {media['id']} params: {params} \n {err.body()['error']}"
            self.error_handler.error_list.append(error_msg)
            return []

    def _process_media(
        self, ig_business_account_id, ig_account_username, media
    ) -> Dict[str, Any]:
        insights_data = self._fetch_media_insights(media, extra_params=False)
        extra_params_data = self._fetch_media_insights(media, extra_params=True)
        insights_data += extra_params_data
        if not insights_data:
            return {}

        file_content = media._json
        file_content["insights"] = insights_data
        pull_date = datetime.today()
        date_partition: str = pull_date.strftime("%Y/%m")
        date_string: str = pull_date.strftime("%Y-%m-%d")
        file_name: str = (
            f"{ig_business_account_id}/{media['id']}/{date_partition}/{date_string}-test-{media['id']}"
        )

        return {
            "ig_business_account_id": ig_business_account_id,
            "ig_account_name": ig_account_username,
            "media_id": media["id"],
            "data": file_content,
            "date": date_string,
            "file_name": file_name,
        }

    def _get_ig_insights(
        self, page, fields: list
    ) -> Generator[Dict[str, Any], None, None]:
        ig_business_account_id = self._get_account_id(page)
        if not ig_business_account_id:
            return
        ig_account_username = self._get_username(ig_business_account_id)
        for media in IGUser(ig_business_account_id).get_media(fields=fields):
            insights_data = self._process_media(
                ig_business_account_id, ig_account_username, media
            )
            if insights_data:
                yield insights_data

    def get_data(self) -> Generator[Dict[str, Any], None, None]:
        """main exit function"""
        fields: List[str] = self.configs["fields"]
        user_id: int = self.authenticator.creds.get("user_id")
        for page in User(user_id).get_accounts(params={"limit": 10}):
            yield from self._get_ig_insights(page, fields)
        if self.error_handler.error_list:
            logger.info("ERRORS")
            logger.info("\n".join([e for e in self.error_handler.error_list]))
