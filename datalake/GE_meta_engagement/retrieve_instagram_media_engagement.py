from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.page import Page
from facebook_business.adobjects.user import User
from facebook_business.adobjects.iguser import IGUser
from facebook_business.adobjects.igmedia import IGMedia
from configparser import ConfigParser
import utilss as utils
import os

FOLDER = f'./IG/media'
if not os.path.exists(FOLDER):
    os.makedirs(FOLDER)


def get_ig_insights(page: Page):
    # # for debugging
    # if page.get_id() != '467903366616024':
    #     return

    FacebookAdsApi.init(access_token=page["access_token"], debug=True)

    ig_business_account = Page(page.get_id()).api_get(fields=["instagram_business_account"])
    if "instagram_business_account" not in ig_business_account:
        print(f"NO INSTAGRAM BUSINESS ACCOUNT LINKED TO PAGE {page.get_id()}")
        return

    ig_business_account_id = ig_business_account["instagram_business_account"]["id"]

    # Get IG User details
    fields = ["username"]
    params = {}
    ig_user = IGUser(ig_business_account_id).api_get(fields=fields, params=params)
    ig_account_username = ig_user["username"]

    # media_product_type: Surface where the media is published. Can be AD, FEED, STORY or REELS.
    # media_type: Media type. Can be CAROUSEL_ALBUM, IMAGE, or VIDEO.
    # https://developers.facebook.com/docs/instagram-api/reference/ig-media
    fields = ["timestamp", "like_count", "comments_count", "permalink", "media_type", "media_product_type"]
    params = {}
    for media in IGUser(ig_business_account_id).get_media(fields=fields, params=params):
        insights_data = []
        fields = []
        # https://developers.facebook.com/docs/instagram-api/reference/ig-media/insights
        if "/tv/" in media["permalink"] or media["media_type"] in ["CAROUSEL_ALBUM"]:
            params = {"metric": ["impressions", "reach", "saved"]}
        elif media["media_type"] in ["IMAGE", "VIDEO"] and media["media_product_type"] != "REELS":
            params = {"metric": ["impressions", "reach", "likes", "comments", "shares", "saved"]}
        elif "/tv/" in media["permalink"] or (media["media_type"] in ["IMAGE", "VIDEO", "CAROUSEL_ALBUM"] and media["media_product_type"] == "REELS"):
            params = {"metric": ["reach", "plays", "likes", "comments", "shares", "saved"]}
        else:
            print("ERROR: ANOTHER MEDIA")
            print(media)

        ig_media_insights = IGMedia(media["id"]).get_insights(fields=fields, params=params)
        if ig_media_insights:
            for item in ig_media_insights:
                insights_data.append(item._json)

        if media["media_type"] in ["IMAGE", "VIDEO"] and media["media_product_type"] != "REELS" and "/tv/" not in media["permalink"]:
            params = {"metric": ["profile_activity"], "breakdown": "action_type"}
            ig_media_insights = IGMedia(media["id"]).get_insights(fields=fields, params=params)
            if ig_media_insights:
                for item in ig_media_insights:
                    insights_data.append(item._json)


        # Create file_content
        file_content = media._json
        file_content["insights"] = insights_data
        filename = f"{FOLDER}/IG-{ig_business_account_id}-{ig_account_username}-{media['id']}-media_insights.json"
        utils.save_json_file(filename, json_content=file_content)


def main():

    # Obtain credentials #
    credentials = {}
    parser = ConfigParser()
    parser.read("credentials.ini")
    params = parser.items("FACEBOOK")

    for param in params:
        credentials[param[0]] = param[1]

    USER_ID = credentials["user_id"]
    USER_ACCESS_TOKEN = credentials["user_access_token"]
    FacebookAdsApi.init(access_token=USER_ACCESS_TOKEN, debug=True)
    fields = []
    params = {"limit": 10}

    # get_account returns a collection of Facebook Pages that the current Facebook User can perform the MANAGE, CREATE_CONTENT, MODERATE, or ADVERTISE tasks on
    for page in User(USER_ID).get_accounts(fields=fields, params=params):
        get_ig_insights(page)


if __name__ == '__main__':
    main()
