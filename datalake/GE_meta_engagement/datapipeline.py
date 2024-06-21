"""DATA PIPELINE CALL FOR META FACEBOOK"""

import sys
import time
import argparse

# from typing import Generator

sys.path.append("../")

from GE_meta_engagement.reader import MetaReader, FacebookAPIAuthenticator
from GE_meta_engagement.writer import MetaWriter
from utils.file_handlers import load_file


def main():
    """main pipeline method"""

    parser = argparse.ArgumentParser(description="Data pipeline for Meta Facebook")
    parser.add_argument("--secrets_file", type=str, help="path to secrets file")
    parser.add_argument("--config_file", type=str, help="path to configs folder")
    parser.add_argument("--storage_account", type=str, default="meta_engagement")
    parser.add_argument("--container", type=str)
    parser.add_argument("--folder_path", type=str, default=None)
    parser.add_argument("--folder_name", type=str, default=None)

    args, _ = parser.parse_known_args()
    secrets_file = args.secrets_file
    config_file = args.config_file
    storage_account = args.storage_account
    container = args.container
    folder_path = args.folder_path
    folder_name = args.folder_name

    configs = load_file(config_file)
    authenticator = FacebookAPIAuthenticator(creds_file=secrets_file)
    reader: MetaReader = MetaReader(authenticator=authenticator, configs=configs)
    local_writer: MetaWriter = MetaWriter(
        container=container,
        destination="local_json",
        configs=configs,
        clear_destination=True,
    )
    azure_writer: MetaWriter = MetaWriter(
        container=container,
        destination="azure_json",
        configs={
            "storage_account": storage_account,
            "overwrite": True,
            "auth_method": "sas_token",
        },
        clear_destination=False,
    )

    for res in reader.query():
        # local_writer.sink(payload=res, folder_path=folder_path, folder_name=folder_name, indent=None)
        azure_writer.sink(
            payload=res, folder_path=folder_path, folder_name=folder_name, indent=None
        )


if __name__ == "__main__":
    start_time = time.perf_counter()
    main()
    end_time = time.perf_counter()
    print(f"Elapsed run time: {end_time - start_time} seconds.")
