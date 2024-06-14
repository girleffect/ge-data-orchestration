from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.user import User
from facebook_business.adobjects.page import Page
from facebook_business.adobjects.pagepost import PagePost
from configparser import ConfigParser
import utilss as utils
import os

FOLDER = f"./FB/post-comment"
if not os.path.exists(FOLDER):
    os.makedirs(FOLDER)


def get_comments(page: Page):

    # # for debugging
    # if page.get_id() != '467903366616024':
    #     return

    FacebookAdsApi.init(access_token=page["access_token"], debug=True)

    fields = ["id"]
    params = {}
    for post in Page(page.get_id()).get_posts(fields=fields, params=params):
        comments = []
        for comment in PagePost(post["id"]).get_comments():
            comments.append(comment._json)

        filename = f"{FOLDER}/FB-{page['id']}-{page['name']}-{post['id']}-comments.json"
        utils.save_json_file(filename, json_content=comments)


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

    for page in User(USER_ID).get_accounts(fields=fields, params=params):
        get_comments(page)


if __name__ == "__main__":
    main()
