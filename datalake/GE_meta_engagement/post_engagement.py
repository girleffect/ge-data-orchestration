#!/usr/bin/python
"""FACEBOOK API READER"""
# import os
import sys
import copy
import warnings
import logging
from typing import Generator, Any, Dict, List
from datetime import datetime

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.page import Page
from facebook_business.adobjects.user import User
from facebook_business.adobjects.pagepost import PagePost

sys.path.append("../")

from utils.date_handlers import string_to_date
from utils.quota_handler import retry_handler, api_handler

warnings.filterwarnings('ignore', category=UserWarning) 
logger = logging.getLogger(__name__)

class FacebookException(Exception):
    """Base class exception for Facebook"""


class PostEngagements:
    """Class to read data from Facebook"""

    def __init__(self, authenticator, configs: dict):
        self.authenticator = authenticator
        self.configs = configs

    def build_query(self, configs: dict) -> Dict[str, Any]:
        """method to build a query"""
        expected_params = ["since", "until", "metric"]
        params: dict = {}
        for param in expected_params:
            if value := configs.get(param):
                if param in ["since", "until"]:
                    value = string_to_date(value).strftime("%Y-%m-%d")
                params[param] = value
        return params

    @staticmethod
    def _process_insights_data(post_insights) -> list:
        """get insights data as a list"""
        insights_data: List[Any] = []
        if post_insights:
            _ = [insights_data.append(item._json) for item in post_insights]
        return insights_data

    @retry_handler(
        exceptions=ConnectionError, initial_wait=3, total_tries=3, backoff_factor=2
    )
    @api_handler(wait=1, backoff_factor=2)
    def post_insights(self, post: dict, insights_params: dict):
        """make api call"""
        try:
            return PagePost(post["id"]).get_insights(fields=[], params=insights_params)
        except ConnectionError as err:
            raise ConnectionError(f"Connection Error: {err}") from err

    def get_insights(
        self, page: Page, configs: dict
    ) -> Generator[Dict[str, Any], None, None]:
        """Fetch insights for all posts of a page"""

        fields: List[str] = configs["fields"]
        params: Dict[str, Any] = {}
        FacebookAdsApi.init(access_token=page["access_token"], debug=False)

        for post in Page(page.get_id()).get_posts(fields=fields, params=params):
            json_data = copy.copy(post)._json
            insights_params: Dict[str, Any] = self.build_query(configs)

            post_insights = self.post_insights(post, insights_params)
            data = self._process_insights_data(post_insights)
            json_data["insights"] = data
            pull_date = datetime.today()
            date_partition: str = pull_date.strftime("%Y/%m")
            date_string: str = pull_date.strftime("%Y-%m-%d")

            file_name: str = (
                f"{page['id']}/{post['id']}/{date_partition}/{date_string}-{post['id']}"
            )
            yield {
                "page_id": page["id"],
                "page_name": page["name"],
                "post_id": post["id"],
                "data": json_data,
                "date": datetime.now().strftime("%Y-%m-d%"),
                "file_name": file_name,
            }
            logger.info(f"Post insights fetched: {post['id']}")

    def get_data(self) -> Generator[Dict[str, Any], None, None]:
        """Get insights for all pages"""
        # Retrieve insights for each page associated with the user
        user_id: int = self.authenticator.creds.get("user_id")
        for page in User(user_id).get_accounts(fields=[], params={}):
            yield from self.get_insights(page, configs=self.configs)
