#!/usr/bin/python
"""writers module"""
import os
import json
from pathlib import Path
from typing import Union, Dict, Any
import yaml

import pandas as pd


def save_csv_file(filename, json_content, extra_columns):
    """method to save to csv"""
    full_path: str = filename.rsplit("/", maxsplit=1)[0]
    Path(f"{full_path}").mkdir(parents=True, exist_ok=True)
    column_headers = [h["name"] for h in json_content["columnHeaders"]]
    df = pd.DataFrame(json_content["rows"], columns=column_headers)

    # Added manually channel name and channel id
    for col, val in extra_columns.items():
        df.insert(loc=0, column=col, value=val)

    df.to_csv(f"{filename}.csv", index=False)
    print(f"Saved file {filename}")


def save_json_file(filename, json_content):
    """method to save to json"""
    full_path: str = filename.rsplit("/", maxsplit=1)[0]
    Path(f"{full_path}").mkdir(parents=True, exist_ok=True)
    with open(f"{filename}.json", "w", encoding="utf8") as outfile:
        json.dump(json_content, outfile, indent=4, sort_keys=True, ensure_ascii=False)
        print(f"Saved file {filename}")


def load_file(file_location: str, fmt: Union[str, None] = None) -> Dict[Any, Any]:
    """
    Gathers file data from json or yaml.
    """
    config: dict = {}
    if file_location.strip().rsplit(".", maxsplit=1)[-1] not in ["json", "yml", "yaml"]:
        raise TypeError("Wrong file type provided! Expecting only json and yaml files")

    file_location = str(file_location).strip()
    if file_location.endswith("yml"):
        with open(file_location, mode="r", encoding="utf8") as yaml_file:
            config = yaml.safe_load(yaml_file)
    if file_location.endswith("json"):
        with open(file_location, mode="r", encoding="utf8") as json_file:
            config = json.load(json_file)

    return config
