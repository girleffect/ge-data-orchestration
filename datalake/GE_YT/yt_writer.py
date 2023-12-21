#!/usr/bin/python
"""YOUTUBE API WRITER"""
import sys

sys.path.append("../")

from typing import List, Tuple, Union, Dict, Any
from base_writers import BaseWriter


class YouTubeWriter(BaseWriter):
    """Writer Class for Youtube"""

    def __init__(
        self,
        container: str,
        destination: str,
        configs: Dict[str, Any],
        clear_destination: bool = False,
    ):
        self.current_destination: Union[str, None] = None
        super().__init__(
            container=container,
            destination=destination,
            configs=configs,
            clear_destination=clear_destination,
        )

    def verify_data(
        self,
        payload: Union[Dict[Any, Any], Any],
        folder_path: Union[str, None] = None,
        folder_name: Union[str, None] = None,
    ) -> Tuple[str, Union[List[Dict[Any, Any]], Dict[Any, Any], Any]]:
        """
        Args:
            payload (Dict[str, Any]): expecting a dictionary having data, date and dimension
        Raises:
            KeyError: if we do not find the exact keys we expect from the payload
            TypeError: if provided data object is not a list
        Returns:
            Tuple[str, Union[List[Dict[Any, Any]], Dict[Any, Any], Any]]: full destination path and
        """
        if not {"data", "date", "channel_data"}.issubset(set(payload.keys())):
            raise KeyError("invalid payload expecting: data, date, channel_data")

        date: str = payload["date"]
        date_split: list = date.split("-")
        channel_data: dict = payload["channel_data"]
        channel_name, channel_id = (
            channel_data["channel_name"],
            channel_data["channel_id"],
        )
        data = payload["data"]
        year, month, day = date_split[0], date_split[1], date_split[2]

        file_name = f"{file_name}" if (file_name := payload.get("file_name")) else date
        file_name = (
            f"{file_name}{file_suffix}"
            if (file_suffix := payload.get("file_suffix"))
            else file_name
        )
        data_path = f"{channel_name}/{year}/{month}/{day}"

        data_path = f"{fpath}/{data_path}" if (fpath := folder_path) else data_path
        data_path = f"{data_path}/{fname}" if (fname := folder_name) else data_path

        data_path = f"{data_path}/{file_name}"
        return data_path, data
