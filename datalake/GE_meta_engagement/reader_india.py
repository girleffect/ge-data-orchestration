"""READER FOR META DATA"""

# import os
import sys
from typing import Generator, Any, Dict
from facebook_business.api import FacebookAdsApi

sys.path.append("../")


from GE_meta_engagement.post_engagement_india import PostEngagements
from GE_meta_engagement.media_engagement_india import MediaEngagements

from utils.file_handlers import load_file


class FacebookAPIAuthenticator:
    """Facebook API Authenticator"""

    def __init__(self, creds_file: str):
        self.creds = load_file(creds_file)

    def initialize(self):
        """Initialize the Facebook API with the loaded credentials"""
        FacebookAdsApi.init(access_token=self.creds["access_token"], debug=False)


class MetaReader:
    """READER CLASS FOR META ENGAGEMENTS"""

    def __init__(self, authenticator: FacebookAPIAuthenticator, configs: dict):
        self.authenticator = authenticator
        self.authenticator.initialize()
        self.configs = configs
        self.endpoint = self.get_endpoint(self.configs["endpoint"])

    def get_endpoint(self, endpoint: str):
        """method to get the endpoint to run"""
        endpoints = {
            "post_engagement": PostEngagements,
            "media_engagement": MediaEngagements,
        }
        return endpoints[endpoint](
            authenticator=self.authenticator, configs=self.configs
        )

    def query(self) -> Generator[Dict[str, Any], None, None]:
        """exist method for the reader class"""

        for result in self.endpoint.get_data():
            yield result
