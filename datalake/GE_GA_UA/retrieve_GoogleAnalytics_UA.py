from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date, timedelta
import time
import utils
import os

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = 'plucky-dryad-381507-62fe588e0fec.json'


def initialize_analyticsreporting():
    """Initializes an Analytics Reporting API V4 service object.

    Returns:
      An authorized Analytics Reporting API V4 service object.
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        KEY_FILE_LOCATION, SCOPES)

    # Build the service object.
    analytics = build('analyticsreporting', 'v4', credentials=credentials)

    return analytics


def get_report(analytics, view, single_date):
    """Queries the Analytics Reporting API V4.

    Args:
      analytics: An authorized Analytics Reporting API V4 service object.
      view: View ID.
      single_date: date
    Returns:
      The Analytics Reporting API V4 response.
    """

    single_date_str = single_date.strftime("%Y-%m-%d")

    return analytics.reports().batchGet(
        body={
            'reportRequests': [{
                'viewId': view,
                'dateRanges': [{'startDate': single_date_str, 'endDate': single_date_str}],
                'metrics': [{'expression': 'ga:users'},
                            {'expression': 'ga:sessions'},
                            {'expression': 'ga:pageViews'},
                            {'expression': 'ga:newusers'},
                            {'expression': 'ga:bounces'},
                            {'expression': 'ga:avgSessionDuration'}
                            ],
                'dimensions': [{'name': 'ga:date'},
                               {'name': 'ga:medium'},
                               {'name': 'ga:source'},
                               {'name': 'ga:deviceCategory'},
                               {'name': 'ga:country'},
                               {'name': 'ga:mobileDeviceModel'},
                               {'name': 'ga:deviceCategory'},
                               {'name': 'ga:mobileDeviceBranding'}
                               ]
            }]
        }
    ).execute()


def print_response(response):
    """Parses and prints the Analytics Reporting API V4 response.

    Args:
      response: An Analytics Reporting API V4 response.
    """
    for report in response.get('reports', []):
        columnHeader = report.get('columnHeader', {})
        dimensionHeaders = columnHeader.get('dimensions', [])
        metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

        for row in report.get('data', {}).get('rows', []):
            dimensions = row.get('dimensions', [])
            dateRangeValues = row.get('metrics', [])

            for header, dimension in zip(dimensionHeaders, dimensions):
                print(header + ': ', dimension)

            for i, values in enumerate(dateRangeValues):
                print('Date range:', str(i))
                for metricHeader, value in zip(metricHeaders, values.get('values')):
                    print(metricHeader.get('name') + ':', value)


def main():
    analytics = initialize_analyticsreporting()

    views = ['198411294']  # FIXED
    m_start_date = date(2021, 11, 24)  # FIXED
    m_end_date = date.today()  # TODAY

    for view in views:
        folder = f'./GA_UA/{view}'
        if not os.path.exists(folder):
            os.makedirs(folder)

        for m_single_date in utils.daterange(m_start_date, m_end_date):
            print(f'View {view}. Running {m_single_date.strftime("%Y-%m-%d")}')
            response = get_report(analytics, view, m_single_date)
            next_day = m_single_date + timedelta(days=1)
            filename_analytics = f"{folder}/{next_day}-{view}"
            utils.save_json_file(filename_analytics + ".json", response)
            #print_response(response)
            time.sleep(1)


if __name__ == '__main__':
    main()
