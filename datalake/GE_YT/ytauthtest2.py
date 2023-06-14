#!/usr/bin/python

# Create a reporting job for the authenticated user's channel or
# for a content owner that the user's account is linked to.
# Usage example:
# python create_reporting_job.py --name='<name>'
# python create_reporting_job.py --content-owner='<CONTENT OWNER ID>'
# python create_reporting_job.py --content-owner='<CONTENT_OWNER_ID>' --report-type='<REPORT_TYPE_ID>' --name='<REPORT_NAME>'

import argparse
import os
import pickle

import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
from io import FileIO

credentials = None

# token.pickle stores the user's credentials from previously successful logins
if os.path.exists('token.pickle'):
    print('Loading Credentials From File...')
    with open('token.pickle', 'rb') as token:
        credentials = pickle.load(token)

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains

# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = 'client_secret_web.json'

# This OAuth 2.0 access scope allows for read access to the YouTube Analytics monetary reports for
# authenticated user's account. Any request that retrieves earnings or ad performance metrics must
# use this scope.
SCOPES = ['https://www.googleapis.com/auth/yt-analytics-monetary.readonly']
API_SERVICE_NAME = 'youtubereporting'
API_VERSION = 'v1'

print('validity of credentials: ', credentials.valid)

if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        print('Refreshing Access Token...')
        credentials.refresh(Request())
    else:
        print("CREDENTIALS ARE EMPTY")


### BUILDS THE YOUTUBE API WE WILL BE USING WITH CREDENTIALS ###
youtube_reporting = build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

### NEED TO DEFINE THE TYPE OF REPORT TO CREATE A REPORTING JOB; THIS LISTS THE TYPES OF REPORTS AVAILABLE ###
# print(youtube_reporting.reportTypes)
reporttypesList = youtube_reporting.reportTypes().list().execute()
# print(type(reporttypesList))
print('Listing the types of reports available...')
if isinstance(reporttypesList, dict):
    for key,value in reporttypesList.items():
        print(key, value)

## links below 
# channel reports: https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-playback-locations
# content owner reports: https://developers.google.com/youtube/reporting/v1/reports/content_owner_reports

# try:
#     reporting_job = youtube_reporting.jobs().create(
#         body=dict(
#             reportTypeId='channel_basic_a2',
#             name = 'youtube report test'
#         )
#     ).execute()
# except Exception as e:
#     print(e)

print('Listing the jobs created...')
print(youtube_reporting.jobs().list().execute())

print('Listing reports in job...')
results = youtube_reporting.jobs().reports().list(jobId='7b374d57-b771-4922-984f-d5264c71fc4a').execute()



if 'reports' in results and results['reports']:
  reports = results['reports']
  for report in reports:
    print ('Report dates: %s to %s\n       download URL: %s\n'
      % (report['startTime'], report['endTime'], report['downloadUrl']))

request = youtube_reporting.media().download(
  resourceName=' '
)

# define local file to be used in next step
local_file = 'yt_report.txt'

# edit download url here?
request.uri = 'https://youtubereporting.googleapis.com/v1/media/CHANNEL/tFXX6FvFUxJBfvPxr7hgpg/jobs/7b374d57-b771-4922-984f-d5264c71fc4a/reports/7756597014?alt=media'
fh = FileIO(local_file, mode='wb')
# Stream/download the report in a single request.
downloader = MediaIoBaseDownload(fh, request, chunksize=-1)

done = False
while done is False:
  status, done = downloader.next_chunk()
  if status:
    print('Download %d%%.' % int(status.progress() * 100))
print('Download Complete!')