"""MODULE TO CALL DATAPIPELINE"""
import sys
import time
import argparse

sys.path.append("../")


from yt_reader import YouTubeAPIAuthenticator, YouTubeReader
from yt_writer import YouTubeWriter

from utils.file_handlers import load_file


def main():
    """main pipeline method"""
    parser = argparse.ArgumentParser(description="YouTube API Pipeline")
    parser.add_argument("--secrets_file", type=str, help="path to secrets file")
    parser.add_argument("--config_file", type=str, help="path to configs folder")
    parser.add_argument("--storage_account", type=str, default="youtube")
    parser.add_argument("--container", type=str)
    parser.add_argument("--folder_path", type=str, default=None)

    args, _ = parser.parse_known_args()
    secrets_file = args.secrets_file
    config_file = args.config_file
    storage_account = args.storage_account
    container = args.container
    folder_path = args.folder_path

    # secrets = load_file(secret_file)
    configs = load_file(config_file)

    other_endpoints = {
        "basic_stats": configs["basic_stats"],
        # "source_stats": configs["source_stats"],
    }

    youtube_authenticator = YouTubeAPIAuthenticator(creds_file=secrets_file)
    reader = YouTubeReader(authenticator=youtube_authenticator)
    local_writer = YouTubeWriter(
        container="./data",
        destination="local_json",
        configs={"overwrite": True},
        clear_destination=True,
    )
    azure_writer = YouTubeWriter(
        container=container,
        destination="azure_json",
        configs={
            "storage_account": storage_account,
            "overwrite": True,
            "auth_method": "sas_token",
        },
        clear_destination=False,
    )

    for result in reader.get_channels(configs=configs["channels"]):
        # local_writer.sink(payload=result, folder_path="channels")
        azure_writer.sink(
            payload=result, folder_path="channels", path_prefix=folder_path
        )

    for result in reader.get_other_stats(other_endpoints):
        endpoint = result["endpoint"]
        # local_writer.sink(payload=result, folder_path=endpoint)
        azure_writer.sink(payload=result, folder_path=endpoint, path_prefix=folder_path)

    for channel_video in reader.get_channel_videos():
        # local_writer.sink(payload=channel_video, folder_path="channel_videos")
        azure_writer.sink(
            payload=channel_video, folder_path="channel_videos", path_prefix=folder_path
        )

    for video in reader.get_videos(configs=configs["video_stats"]):
        # local_writer.sink(payload=video, folder_path="video_stats")
        azure_writer.sink(
            payload=video, folder_path="video_stats", path_prefix=folder_path
        )

    for video in reader.get_trafffic_source(configs=configs["traffic_source"]):
        # local_writer.sink(payload=video, folder_path="source_traffic")
        azure_writer.sink(
            payload=video, folder_path="traffic_source", path_prefix=folder_path
        )


if __name__ == "__main__":
    start_time = time.perf_counter()
    main()
    end_time = time.perf_counter()
    print(f"Elapsed run time: {end_time - start_time} seconds.")
    # 254.865641375 seconds.
