#!/usr/bin/python

import os
from datetime import date, timedelta
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import json
import pandas as pd


def save_csv_file(filename, json_content, extra_columns):
    column_headers = [h["name"] for h in json_content["columnHeaders"]]
    df = pd.DataFrame(json_content['rows'], columns=column_headers)

    # Added manually channel name and channel id
    for col, val in extra_columns.items():
        df.insert(loc=0, column=col, value=val)

    df.to_csv(filename, index=False)
    print(f"Saved file {filename}")


def save_json_file(filename, json_content):
    with open(filename, 'w', encoding='utf8') as outfile:
        json.dump(json_content, outfile, indent=4, sort_keys=True, ensure_ascii=False)
        print(f"Saved file {filename}")


def get_service(api_service_name, api_version, credentials):
    return build(serviceName=api_service_name, version=api_version, credentials=credentials)


if __name__ == '__main__':

    # updated credentials for chhaajaa
    creds_cj = Credentials(
        token='TOKEN_HERE',
        refresh_token='REFRESH_TOKEN_HERE',
        token_uri="https://www.googleapis.com/oauth2/v3/token",
        client_id='CLIENT_ID',
        client_secret='CLIENT_SECRET',
        scopes=[
            'https://www.googleapis.com/auth/youtube.readonly', 'https://www.googleapis.com/auth/yt-analytics.readonly'
        ]
    )

    # updated credentials for chora journey
    creds_chora = Credentials(
        token='TOKEN_HERE',
        refresh_token='REFRESH_TOKEN_HERE',
        token_uri="https://www.googleapis.com/oauth2/v3/token",
        client_id='CLIENT_ID',
        client_secret='CLIENT_SECRET',
        scopes=[
            'https://www.googleapis.com/auth/youtube.readonly', 'https://www.googleapis.com/auth/yt-analytics.readonly'
        ]
    )

    # updated credentials for yegna
    creds_yegna = Credentials(
        token='TOKEN_HERE',
        refresh_token='REFRESH_TOKEN_HERE',
        token_uri="https://www.googleapis.com/oauth2/v3/token",
        client_id='CLIENT_ID',
        client_secret='CLIENT_SECRET',
        scopes=[
            'https://www.googleapis.com/auth/youtube.readonly', 'https://www.googleapis.com/auth/yt-analytics.readonly'
        ]
    )

    _all_credentials = [creds_cj, creds_chora, creds_yegna]

    for _credentials in _all_credentials:
        print('validity of credentials: ', _credentials.valid)
        if not _credentials or not _credentials.valid:
            if _credentials and _credentials.expired and _credentials.refresh_token:
                print('Refreshing Access Token...')
                _credentials.refresh(Request())
            else:
                print("CREDENTIALS ARE EMPTY")

        # Disable OAuthlib's HTTPs verification when running locally.
        # *DO NOT* leave this option enabled when running in production.
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

        TODAY = date.today()
        YESTERDAY = TODAY - timedelta(days=1)

        print(f"Querying YouTube Data API for getting channels")
        API_SERVICE_NAME = 'youtube'
        API_VERSION = 'v3'
        youtube = get_service(API_SERVICE_NAME, API_VERSION, _credentials)
        request = youtube.channels().list(
            # auditDetails is out of the scope
            part="brandingSettings,contentDetails,contentOwnerDetails,id,localizations,snippet,statistics,status,topicDetails",
            mine=True
        )
        response = request.execute()

        # https://developers.google.com/youtube/analytics/channel_reports#basic-user-activity-statistics
        API_SERVICE_NAME = 'youtubeAnalytics'
        API_VERSION = 'v2'
        youtube_analytics = get_service(API_SERVICE_NAME, API_VERSION, _credentials)

        for channel in response["items"]:
            channel_name = channel["snippet"]["title"]
            channel_id = channel["id"]
            channel_start_date = channel["snippet"]["publishedAt"][:10]
            channel_playlist_upload = channel["contentDetails"]["relatedPlaylists"]["uploads"]

            # Saving channel details
            channel_filename = f"{TODAY}_channel_{channel_name}_{channel_id}_details"
            save_json_file(channel_filename+".json", channel)

            # Get channel stats
            print(f"Querying YouTube Analytics API for channel basic stats. Channel '{channel_name}' ({channel_id})")
            request = youtube_analytics.reports().query(
                ids=f'channel=={channel_id}',
                startDate=channel_start_date,
                endDate=YESTERDAY.strftime("%Y-%m-%d"),
                metrics='views,estimatedMinutesWatched,averageViewDuration,likes,dislikes,comments,subscribersGained,subscribersLost',
                dimensions='day',
                sort='day'
            )

            channel_analytics = request.execute()

            channel_filename = f"{TODAY}_channel_{channel_name}_{channel_id}_analytics"
            save_json_file(channel_filename+".json", channel_analytics)
            save_csv_file(channel_filename+".csv", channel_analytics, extra_columns={"channel_name": channel_name, "channel_id": channel_id})

    ####################################################################################################################

            # https://developers.google.com/youtube/analytics/channel_reports#traffic-source
            # Get channel traffic source stats
            print(f"Querying YouTube Analytics API for channel traffic source stats. Channel '{channel_name}' ({channel_id})")
            request = youtube_analytics.reports().query(
                ids=f'channel=={channel_id}',
                startDate=channel_start_date,
                endDate=YESTERDAY.strftime("%Y-%m-%d"),
                dimensions="day,insightTrafficSourceType",
                metrics="views"
            )

            channel_analytics = request.execute()

            channel_filename = f"{TODAY}_channel_{channel_name}_{channel_id}_analytics_traffic_source"
            save_json_file(channel_filename+".json", channel_analytics)
            save_csv_file(channel_filename+".csv", channel_analytics, extra_columns={"channel_name": channel_name, "channel_id": channel_id})

    ####################################################################################################################

            # Get channel stats
            print(f"Querying YouTube Data API for retrieving videos uploaded. Channel '{channel_name}' ({channel_id})")
            request = youtube.playlistItems().list(
                part="snippet,contentDetails,id,status",
                maxResults=50,
                playlistId=channel_playlist_upload
            )
            channel_all_videos = []

            while request:
                response = request.execute()
                if response.items:
                    # print(f"Num items {len(response['items'])}")
                    channel_all_videos += response["items"]
                    # print(f"Num channel_all_videos {len(channel_all_videos)}")
                request = youtube.playlistItems().list_next(request, response)

            print(f"{len(channel_all_videos)} videos uploaded (public and private) in channel '{channel_name}' ({channel_id})")
            channel_videos_filename = f"{TODAY}_channel_{channel_name}_{channel_id}_videos"
            save_json_file(channel_videos_filename+".json", channel_all_videos)

            # Get stats by video
            for video in channel_all_videos:
                video_id = video["snippet"]["resourceId"]["videoId"]
                video_name = video["snippet"]["title"]
                video_start_date = video["snippet"]["publishedAt"][:10]
                print(f"Querying YouTube Analytics API for video stats. Channel '{channel_name}' ({channel_id}). Video ({video_id})")
                request = youtube_analytics.reports().query(
                    ids=f'channel=={channel_id}',
                    startDate=video_start_date,
                    endDate=YESTERDAY.strftime("%Y-%m-%d"),
                    metrics='views,estimatedMinutesWatched,averageViewDuration,likes,dislikes,comments,subscribersGained,subscribersLost',
                    dimensions='day',
                    sort='day',
                    filters=f'video=={video_id}'
                )

                video_analytics = request.execute()

                folder = f'./videos/{channel_name.lower()}'
                if not os.path.exists(folder):
                    os.makedirs(folder)
                video_filename = f"{folder}/{TODAY}_{channel_name}_{channel_id}_video_{video_id}_analytics_video"
                save_json_file(video_filename+".json", video_analytics)
                save_csv_file(video_filename+".csv", video_analytics, extra_columns={"video_name": video_name, "video_id": video_id, "channel_name": channel_name, "channel_id": channel_id})
