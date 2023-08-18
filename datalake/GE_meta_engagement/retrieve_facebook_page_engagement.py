from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.page import Page
from facebook_business.adobjects.user import User
from configparser import ConfigParser
import utils
import os

FOLDER = f'./FB/page'
if not os.path.exists(FOLDER):
    os.makedirs(FOLDER)


def get_insights(page: Page):

    # # for debugging
    # if page.get_id() != '467903366616024':
    #     return

    FacebookAdsApi.init(access_token=page["access_token"], debug=True)

    # https://developers.facebook.com/docs/graph-api/reference/v17.0/insights
    fields = []
    params = {"date_preset": "maximum", "period": "day", "metric": ["page_fans", "page_fan_adds_unique", "page_impressions_unique", "page_views_total", "page_engaged_users"]}
    page_insights = Page(page.get_id()).get_insights(fields=fields, params=params)

    insights_data = []
    if page_insights:
        for item in page_insights:
            insights_data.append(item._json)

    filename = f"{FOLDER}/FB-{page['id']}-{page['name']}-page_insights.json"
    utils.save_json_file(filename, json_content=insights_data)


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
