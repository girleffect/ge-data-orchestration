from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from configparser import ConfigParser
from datetime import date, timedelta, datetime
import utils
import os

# Obtain credentials #
parser = ConfigParser()
parser.read("credentials.ini")
facebook_items = parser.items("FACEBOOK_APP")

credentials = {}
for param in facebook_items:
    credentials[param[0]] = param[1]

my_app_id = credentials["my_app_id"]
my_app_secret = credentials["my_app_secret"]
my_access_token = credentials["my_access_token"]

FacebookAdsApi.init(my_app_id, my_app_secret, my_access_token)

# Create accounts

accounts = {}
sections_account = [s for s in parser.sections() if s.startswith("account")]
for section in sections_account:
    params = parser.items(section)
    accounts[section] = {}
    for param in params:
        accounts[section][param[0]] = param[1]
    account_id = accounts[section]["account_id"]
    accounts[account_id] = accounts.pop(section)  # rename key
    accounts[account_id]["ad_account"] = AdAccount(account_id)  # Create AdAccount
#
###########################


def run_ad_level(single_date):
    end_date = single_date

    request_date = end_date + timedelta(days=1)
    breakdowns = ['age', 'gender', 'country', 'region', 'publisher_platform', 'impression_device'] #['region', 'device_platform', 'impression_device', 'age', 'gender', 'publisher_platform', 'country']
    for my_account in accounts.values():
        for breakdown in breakdowns:
            insights_data = []

            start_date = my_account["start_date"]
            print(f'Running - account {my_account["account_id"]} - {start_date}-{end_date.strftime("%Y-%m-%d")} - {breakdown} ')
            params = {'time_range': {'since': start_date, 'until': end_date.strftime("%Y-%m-%d")},
                      'sort': ['spend_descending'],
                      'export_format': 'csv',
                      'breakdowns': breakdown,
                      'limit': 200,
                      'level': 'ad'}
            # Campaign: https://developers.facebook.com/docs/marketing-api/reference/ad-campaign-group/insights
            fields = ['account_id',
                      'account_name',
                      'campaign_id',
                      'campaign_name',
                      'adset_id',
                      'adset_name',
                      'ad_id',
                      'ad_name',
                      'objective',
                      'date_start',
                      'date_stop',

                      'spend',
                      'reach',
                      'cpm',

                      'video_thruplay_watched_actions',
                      'video_p50_watched_actions',
                      'video_p75_watched_actions',

                      'actions',
                      'unique_clicks',
                      'unique_actions',
                      'cost_per_unique_click',
                      'cost_per_unique_action_type'
            ]

            account_data = my_account["ad_account"].get_insights(fields=fields, params=params)
            if account_data:
                for item in account_data:
                    insights_data.append(item._json)

            folder = f'./ads/{my_account["account_id"]}/{request_date.year}/{request_date.month:02d}/{breakdown.lower()}'
            if not os.path.exists(folder):
                os.makedirs(folder)
            filename = f"{folder}/{request_date}-facebook-{my_account['account_id']}-ads-{breakdown.lower()}.json"
            utils.save_json_file(filename=filename, json_content=insights_data)


def run_reach(single_date, level):
    end_date = single_date

    request_date = end_date + timedelta(days=1)
    breakdowns = ['age', 'gender', 'country', 'region', 'publisher_platform', 'impression_device'] #['region', 'device_platform', 'impression_device', 'age', 'gender', 'publisher_platform', 'country']

    for my_account in accounts.values():
        for breakdown in breakdowns:
            insights_data = []
            start_date = my_account["start_date"]
            print(f'Running REACH - account {my_account["account_id"]} - level {level} - {start_date}-{end_date.strftime("%Y-%m-%d")} - {breakdown} ')
            params = {'time_range': {'since': start_date, 'until': end_date.strftime("%Y-%m-%d")},
                      'sort': ['spend_descending'],
                      'export_format': 'csv',
                      'breakdowns': breakdown,
                      'limit': 200,
                      'level': level}
            # Campaign: https://developers.facebook.com/docs/marketing-api/reference/ad-campaign-group/insights
            fields = ['account_id',
                      'account_name',
                      'campaign_id',
                      'campaign_name',
                      'adset_id',
                      'adset_name',
                      'objective',
                      'date_start',
                      'date_stop',

                      'spend',
                      'reach',
                      'cpm'

                      'unique_clicks',
                      'unique_actions',
                      'cost_per_unique_click',
                      'cost_per_unique_action_type'
            ]

            account_data = my_account["ad_account"].get_insights(fields=fields, params=params)
            if account_data:
                for item in account_data:
                    insights_data.append(item._json)

            folder = f'./{level}s/{my_account["account_id"]}/{request_date.year}/{request_date.month:02d}/{breakdown.lower()}'
            if not os.path.exists(folder):
                os.makedirs(folder)
            filename = f"{folder}/{request_date}-facebook-{my_account['account_id']}-{level}s-{breakdown.lower()}.json"
            utils.save_json_file(filename=filename, json_content=insights_data)


if __name__ == '__main__':
    FILENAME_BACKUP = "ultima_fecha.txt"

    m_start_date = date(2023, 4, 1)  # missing
    TODAY = date.today()
    #m_end_date = date(2023, 3, 1)  # missing
    m_end_date = TODAY

    if os.path.isfile(FILENAME_BACKUP):
        f = open(FILENAME_BACKUP)
        m_start_date = datetime.strptime(f.read(), '%Y-%m-%d')
        m_start_date = datetime.date(m_start_date)
        print(str(m_start_date))
        f.close()
        os.remove(FILENAME_BACKUP)

    try:
        for m_single_date in utils.daterange(m_start_date, m_end_date):
            print(f'Running Meta ads {m_single_date.strftime("%Y-%m-%d")}')
            run_ad_level(m_single_date)
            for level in ["adset", "campaign"]:
                run_reach(m_single_date, level=level)
    except Exception as e:
        print(e)
        f = open(FILENAME_BACKUP, "w")
        f.write(str(m_single_date))
        f.close
