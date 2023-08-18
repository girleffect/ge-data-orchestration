from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.page import Page
from facebook_business.adobjects.user import User
from facebook_business.adobjects.iguser import IGUser
from configparser import ConfigParser
import utils
import os

FOLDER = f'./IG/user'
if not os.path.exists(FOLDER):
    os.makedirs(FOLDER)


def get_ig_insights(page: Page):
    # # for debugging
    # if page.get_id() != '467903366616024':
    #     return

    FacebookAdsApi.init(access_token=page["access_token"], debug=True)

    # # https://developers.facebook.com/docs/instagram-api/getting-started/
    # ig_account = Page(page.get_id()).get_instagram_accounts()
    # if not ig_account:
    #     print("NO INSTAGRAM ACCOUNT LINKED")
    #     return
    # ig_account_id = ig_account.get_one()["id"]

    # USE ONLY UGUSER
    # GET IG User: Represents an Instagram Business Account or an Instagram Creator Account.
    # https://developers.facebook.com/docs/instagram-api/reference/ig-user
    ig_business_account = Page(page.get_id()).api_get(fields=["instagram_business_account"])
    if "instagram_business_account" not in ig_business_account:
        print(f"NO INSTAGRAM BUSINESS ACCOUNT LINKED TO PAGE {page.get_id()}")
        return
    ig_business_account_id = ig_business_account["instagram_business_account"]["id"]

    # Get IG User details
    fields = ["username", "followers_count", "media_count"]
    params = {}
    ig_user = IGUser(ig_business_account_id).api_get(fields=fields, params=params)
    ig_account_username = ig_user["username"]

    # # Stories
    # fields=[]
    # params = {}
    # ig_user_stories = IGUser(ig_business_account_id).get_stories(fields=fields, params=params)
    # print(ig_user_stories)

    # https://developers.facebook.com/docs/instagram-api/reference/ig-user/insights

    # # TODO: Use since-until for playing with dates
    # # https://developers.facebook.com/docs/instagram-api/reference/ig-user/insights#range
    # fields = []
    # params = {"period": "day", "metric": ["follower_count"]}
    # ig_user_insights = IGUser(ig_business_account_id).get_insights(fields=fields, params=params)

    # TODO: Use since-until for playing with dates
    # https://developers.facebook.com/docs/instagram-api/reference/ig-user/insights#range-2
    fields=[]
    params = {"since": "2023-08-01", "until": "2023-08-07", "period": "day", "metric": ["follows_and_unfollows", "reach", "profile_views", "accounts_engaged"], "metric_type": "total_value"}
    ig_user_insights = IGUser(ig_business_account_id).get_insights(fields=fields, params=params)

    insights_data = []
    if ig_user_insights:
        for item in ig_user_insights:
            insights_data.append(item._json)

    # Create file_content
    file_content = ig_user._json
    file_content["insights"] = insights_data

    filename = f"{FOLDER}/IG-{ig_business_account_id}-{ig_account_username}-page_insights.json"
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
