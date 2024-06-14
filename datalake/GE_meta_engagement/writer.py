#!/usr/bin/python
"""YOUTUBE API WRITER"""
import sys

sys.path.append("../")

from typing import List, Tuple, Union, Dict, Any
from base_writers import BaseWriter


class MetaWriter(BaseWriter):
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
        if not {"data", "date"}.issubset(set(payload.keys())):
            raise KeyError("invalid payload expecting: data, date")

        date: str = payload["date"]
        date_split: list = date.split("-")
        # post_id: dict = payload["post_id"]
        data = payload["data"]

        file_name = f"{file_name}" if (file_name := payload.get("file_name")) else date
        # data_path = f"{channel_name}/{year}/{month}/{day}/"

        data_path = f"{fpath}/{file_name}" if (fpath := folder_path) else file_name
        data_path = f"{fname}/{data_path}" if (fname := folder_name) else data_path

        data_path = f"{data_path}"
        return data_path, data
