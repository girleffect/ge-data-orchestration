from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange
from google.analytics.data_v1beta.types import Dimension
from google.analytics.data_v1beta.types import Metric
from google.analytics.data_v1beta.types import RunReportRequest
from google.analytics.data_v1beta.types import GetMetadataRequest

import pandas as pd
# https://developers.google.com/analytics/devguides/migration/api/reporting-ua-to-ga4


def clean_date(row):
    d = row['date']
    return f"{d[0:4]}-{d[4:6]}-{d[6:8]}"


def ga4_response_to_df(response, account_id, account_name, property_id, property_name):
    dim_len = len(response.dimension_headers)
    metric_len = len(response.metric_headers)
    all_data = []
    for row in response.rows:
        row_data = {}
        for i in range(0, dim_len):
            row_data.update({response.dimension_headers[i].name: row.dimension_values[i].value})
        for i in range(0, metric_len):
            row_data.update({response.metric_headers[i].name: row.metric_values[i].value})
        all_data.append(row_data)
    df = pd.DataFrame(all_data)

    df["date"] = df.apply(lambda row: clean_date(row), axis=1)
    df['account_id'] = account_id
    df['account_name'] = account_name
    df['property_id'] = property_id
    df['property_name'] = property_name
    return df


# It is not possible to retrieve account id, account name and property name from the property id.
ga_properties = [
    {
        "account_id": "102588170",
        "account_name": "Springster Analytics Account",
        "property_id": "345080356",
        "property_name": "SP South Africa - GA4",
        "start_date": "2022-12-01",
        "end_date": "2023-03-01"
    }, {
        "account_id": "140154819",
        "account_name": "ChaaJaa",
        "property_id": "319324465",
        "property_name": "Girl Effect - Chajaa Public Site - Live - GA4",
        "start_date": "2022-06-01",
        "end_date": "2023-03-01"
    }
]


def run_report():
    for property in ga_properties:
        property_id = property["property_id"]
        property_name = property["property_name"]

        DIMS = ["date", "country", "sessionDefaultChannelGrouping", "region", "platformDeviceCategory", "deviceModel"]
        METRICS = ["totalUsers", "newUsers", "sessions", "bounceRate", "engagementRate", "averageSessionDuration", "screenPageViews"]
        start_date = property["start_date"]
        end_date = property["end_date"]

        # Using a default constructor instructs the client to use the credentials
        # specified in GOOGLE_APPLICATION_CREDENTIALS environment variable.
        import os
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "plucky-dryad-381507-62fe588e0fec.json"
        client = BetaAnalyticsDataClient()

        #NOT WORKING
        #client = BetaAnalyticsDataClient().from_service_account_json(credentials_json_path)

        dimensions_ga4 = []
        for dimension in DIMS:
            dimensions_ga4.append(Dimension(name=dimension))

        metrics_ga4 = []
        for metric in METRICS:
            metrics_ga4.append(Metric(name=metric))

        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=dimensions_ga4,
            metrics=metrics_ga4,
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            limit=100000
        )
        response = client.run_report(request)

        df = ga4_response_to_df(response, property["account_id"], property["account_name"], property_id, property_name)

        GA4_FILENAME = f"initial-load-{property_id}.csv"
        df.to_csv(GA4_FILENAME, index=False)


if __name__ == "__main__":
    run_report()

# TODO Add log