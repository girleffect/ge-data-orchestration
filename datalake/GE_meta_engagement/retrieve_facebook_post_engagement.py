from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.page import Page
from facebook_business.adobjects.user import User
from facebook_business.adobjects.pagepost import PagePost
from configparser import ConfigParser
import copy
import utils
import os

FOLDER = f'./FB/post'
if not os.path.exists(FOLDER):
    os.makedirs(FOLDER)


def get_insights(page: Page):

    # # For debugging
    # if page.get_id() != '467903366616024':
    #     return

    FacebookAdsApi.init(access_token=page["access_token"], debug=True)

    # https://developers.facebook.com/docs/graph-api/reference/post/
    fields = ["id", "created_time", "message", "permalink_url", "shares", "updated_time"]
    params = {}

    for post in Page(page.get_id()).get_posts(fields=fields, params=params):
        p = copy.copy(post)._json  # copy post value for adding new fields during iteration

        fields=[]
        # TODO: change since and until params
        params = {"since": "2023-08-01", "until": "2023-08-07", "metric": ["post_impressions", "post_impressions_unique", "post_video_views_organic", "page_video_views", "post_reactions_by_type_total", "post_clicks_by_type", "post_video_avg_time_watched"]}
        post_insights = PagePost(post['id']).get_insights(fields=fields, params=params)

        insights_data = []
        if post_insights:
            for item in post_insights:
                insights_data.append(item._json)
        p["insights"] = insights_data

        filename = f"{FOLDER}/FB-{page['id']}-{page['name']}-{post['id']}-posts.json"
        utils.save_json_file(filename, json_content=p)


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
    params = {}

    # If you want to retrieve also IG accounts https://developers.facebook.com/docs/instagram-api/getting-started/
    # get_account returns a collection of Facebook Pages that the current Facebook User can perform the MANAGE, CREATE_CONTENT, MODERATE, or ADVERTISE tasks on
    for page in User(USER_ID).get_accounts(fields=fields, params=params):
        get_insights(page)


if __name__ == '__main__':
    main()
