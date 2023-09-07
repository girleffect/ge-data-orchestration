from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date, timedelta
import time
import utils
import os

from typing import Union, Dict, List, Any

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

def build_query(view_id: str, start_date: str, end_date: str, config: dict) -> Dict[Any, Any]:
    query = {
        "viewID": view_id,
        'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
        'metrics': [],
        'dimensions': []
    }
    for metric in config['metrics']:
        query['metrics'].append({"expression": metric})
    for dimension in config['dimensions']:
         query['dimensions'].append({"name": dimension})

    return query

def get_report(analytics, view: str, start_date: str, end_date: str, config: dict):
    """Queries the Analytics Reporting API V4.

    Args:
      analytics: An authorized Analytics Reporting API V4 service object.
      view: View ID.
      single_date: date
    Returns:
      The Analytics Reporting API V4 response.
    """

    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    query = build_query(view_id=view,start_date=start_date_str,end_date=end_date_str,config=config)

    return analytics.reports().batchGet(
        body={
            'reportRequests': [query]
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

    config = utils.load_file("configs/users.yml")
    view_ids = config['view_ids']
    m_start_date = date(2021, 11, 24)  # FIXED
    m_end_date = date.today()  # TODAY

    for view in view_ids:
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
