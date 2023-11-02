- Each channel has its own credentials
- YouTube Analytics API only returns JSON (alt parameter in https://developers.google.com/youtube/analytics/reference/reports/query )

## Readers and Writers
### datapipeline.py
- This is the entry script to run the data pipeline. It imports the modules as shown below
```PYTHON
import time
import argparse

from yt_reader import YouTubeAPIAuthenticator, YouTubeReader
from yt_writer import YouTubeWriter

from utils import load_file
```
- To run the script locally you need to pass in args as shown below:

```YAML
    python GE_YT/datapipeline.py \
      --secrets_file=GE_YT/secrets/chora.json \
      --config_file=GE_YT/configs/youtube.yml \
      --storage_account="cloud storage" \
      --container="container name"
```

### yt_reader
- This is a module used to read the data from the yotube api.
```PYTHON
    youtube_authenticator = YouTubeAPIAuthenticator(creds_file=secrets_file)
    reader = YouTubeReader(authenticator=youtube_authenticator)
```
- From the above the youtube_authenticator is a class instance for authenticating into youtube service.
- To authenticate to youtube we pass in the path to the creds file (json/yml) object that has the below contents.
```JSON
{
    "token": "token here",
    "refresh_token": "refresh token here",
    "token_uri": "https://www.googleapis.com/oauth2/v3/token",
    "client_id": "sample_client_id here",
    "client_secret": "client secret here"
}

```
- The `reader` is an instance of `YouTubeReader` that takes as input the authenticated Youtube service.
- It has different methods to get the data you want which will be shown in the sections that follow.

### yt_writer
```PYTHON
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
        },
        clear_destination=False,
    )

```
- The writer class allows for writting to local folder (testing) and azure for prod or even testing the difference is what you supply as the `destination` parameter.
- Currently we have these destination options:
  - `azure_json` : write the results as a json object to azure
  - `local_json` : write the results as json object to local directory
  - `local_csv` : write results as csv to local directory
- See the base_writers module for more details.
- We also pass in the `container` parameter to denote the container to write to.
- We pass in the `configs` with the main expected key being `storage_account` indicating the storage account to use for writting.

### Writting the data
#### channels
```PYTHON
  for result in reader.get_channels(configs=configs["channels"]):
          local_writer.sink(payload=result, folder_path="channels")
          azure_writer.sink(payload=result, folder_path="channels")
```
- Above calls the reader method `get_channels` which gets channel data and then write the data.
- Write format `container_name/channels/Chhaa Jaa/2023/11/01/2023-11-01-UCtFXX6FvFUxJBfvPxr7hgpg.json`

#### Basic stats and Source Stats
```PYTHON
    for result in reader.get_other_stats(other_endpoints):
        endpoint = result["endpoint"]
        local_writer.sink(payload=result, folder_path=endpoint)
        azure_writer.sink(payload=result, folder_path=endpoint)
```
- The above is used to fetch data for basic stats and source stats for the channels and write then to respective folder paths
- Write format:
  - basic_stats: `container_name/basic_stats/Chhaa Jaa/2023/11/01/2023-11-01-channel_id.json`
  - source_stats: `container_name/source_stats/Chhaa Jaa/2023/11/01/2023-11-01-channel_id.json`

#### channel videos
```PYTHON
    for channel_video in reader.get_channel_videos():
        local_writer.sink(payload=channel_video, folder_path="channel_videos")
        azure_writer.sink(payload=channel_video, folder_path="channel_videos")
```
- The above code snippet is used to get the channel_videos (not video stats!).
- it write the data to a folder called `channel_videos`
- Write format `container_name/channel_videos/Chhaa Jaa/2023/11/01/2023-11-01-channel_id.json`

#### Video stats
```PYTHON
    for video in reader.get_videos(configs=configs["video_stats"]):
        local_writer.sink(payload=video, folder_path="video_stats")
        azure_writer.sink(payload=video, folder_path="video_stats")
```
- The above code snippet is used to get data for video stats
- It will write the data to a top folder called `video_stats`.
- Write format `container_name/video_stats/Chhaa Jaa/2023/11/01/2023-11-01-channel_id_videoid_jhjhjhjhj.json`

