#!/usr/bin/python
"""MODULE FOR BASE RESOURCE WRITERS"""
# pylint: disable=broad-except, unused-import, maybe-no-member
import os
import json
import csv
from pathlib import Path
from abc import ABC, abstractmethod

from typing import Union, Any, Dict, List, Tuple
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient, BlobServiceClient


class AzureDefaultAuthenticator:
    """class for authenticating using default"""

    def authenticate(self, configs: dict) -> BlobServiceClient:
        """Base CLass Method for Authentication"""
        account_url = f"https://{configs['storage_account']}.blob.core.windows.net/"
        return BlobServiceClient(
            account_url=account_url, credential=DefaultAzureCredential()
        )


class AzureConnectionStringAuthenticator:
    """class to authenticate azure using connection string"""

    def verify_details(self, configs: dict) -> str:
        """method to verify connection details"""
        connect_str: str = ""
        if not os.getenv("AZURE_STORAGE_CONNECTION_STRING") and configs.get(
            "AZURE_STORAGE_CONNECTION_STRING"
        ):
            raise KeyError("Provide AZURE STORAGE CONNECTION STRING")

        connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
        if configs.get("AZURE_STORAGE_CONNECTION_STRING"):
            connect_str = configs["AZURE_STORAGE_CONNECTION_STRING"]
        return connect_str

    def authenticate(self, configs: dict) -> BlobServiceClient:
        """method to authenticate cloud storage"""
        connect_str = self.verify_details(configs=configs)
        return BlobServiceClient.from_connection_string(connect_str)


class AzureSASTokenAuthenticator:
    """class to authenticate using SAS Token"""

    def verify_details(self, configs: dict):
        """method to verify connection details"""
        sas_token = ""
        env_token, config_token = os.getenv("SAS_TOKEN"), configs.get("SAS_TOKEN")
        if not env_token and not config_token:
            raise KeyError("Provide Azure SAS Token")
        if not configs.get("storage_account"):
            raise KeyError("storage_account required on configs")

        sas_token = config_token
        if env_token:
            sas_token = env_token
        return sas_token

    def authenticate(self, configs: dict) -> BlobServiceClient:
        """method to authenticate cloud storage"""
        sas_token = self.verify_details(configs=configs)
        account_url = f"https://{configs['storage_account']}.blob.core.windows.net/"
        return BlobServiceClient(account_url=account_url, credential=sas_token)


class AzureAuthenticator:
    """Auhthenticator for Azure"""

    def authenticate(self, configs: dict):
        """Azure Cloud Storage Authenticator"""
        authenticators = {
            "default": AzureDefaultAuthenticator,
            "connection_string": AzureConnectionStringAuthenticator,
            "sas_token": AzureSASTokenAuthenticator,
        }
        auth_method = configs.get("auth_method")
        if not auth_method:
            raise KeyError(
                "configs expecting auth_method: default| sas_token| connection_string"
            )
        print(f"authentication method is {auth_method}")

        return authenticators[auth_method]().authenticate(configs=configs)


class LocalAuthenticator:
    """Dummy class for Local File Writting"""

    def authenticate(self, configs: dict):
        """Place holder method for local authenticator"""
        return True


class DataWriter(ABC):
    """Interface class for resource writers"""

    @abstractmethod
    def write_data(self, write_path: str, data: Any) -> None:
        """Method to write data to final destination resource"""
        raise NotImplementedError


class LocalWriter(DataWriter):
    """Class for Writting Data to Azure"""

    def __init__(
        self,
        container: str,
        configs: dict,
        authenticator=LocalAuthenticator,
    ):
        self.service = authenticator().authenticate(configs=configs)
        self.container = container
        self.configs = configs

    def delete_destination(self, delete_path: str) -> None:
        """method to clear destination before writting data into it"""
        delete_path = f"{self.container}/{delete_path}"
        files = Path(f"{delete_path}").glob("*.*")
        files = list(files)
        print("deleting all records in the path\n" f"{delete_path}")
        _ = [file.unlink(missing_ok=True) for file in files]

    def check_exists(self, write_path: str):
        """method to check if container name exists"""
        try:
            full_path = write_path.rsplit("/", maxsplit=1)[0]
            Path(f"{self.container}/{full_path}").mkdir(parents=True, exist_ok=True)
            return True
        except Exception as err:
            print(f"error checking path \n{err}")
            return False


class LocalJSONWriter(LocalWriter):
    """class for wrtting to json on local directory"""

    def write_data(self, write_path: str, data: Any) -> None:
        """method to write data"""
        self.check_exists(write_path=write_path)
        write_path = f"{write_path}.json"

        with open(
            f"{self.container}/{write_path}", mode="w", encoding="utf8"
        ) as dest_file:
            json.dump(data, dest_file, indent=4)
            print(f"done writting data to {self.container}/{write_path}")


class LocalCSVWriter(LocalWriter):
    """class for wrtting to json on local directory"""

    def write_data(self, write_path: str, data: Any) -> None:
        full_path = write_path.rsplit("/", maxsplit=1)[0]
        self.check_exists(full_path=full_path)

        write_path = f"{write_path}.csv"
        field_names = list(data[0].keys())

        with open(
            f"{self.container}/{write_path}", mode="w", encoding="utf8"
        ) as myfile:
            writer = csv.DictWriter(
                myfile, fieldnames=field_names, quoting=csv.QUOTE_ALL
            )
            writer.writeheader()
            writer.writerows(data)
            print(f"done writting data to {self.container}/{write_path}")


class AzureWriter(DataWriter):
    """Class for Writting Data to Azure"""

    def __init__(
        self,
        container: str,
        configs: dict,
        authenticator=AzureAuthenticator,
    ):
        self.service = authenticator().authenticate(configs=configs)
        self.container = container
        self.overwrite = configs.get("overwrite", True)
        self.configs = configs

    def check_exists(self, container_name: str):
        """method to check if container name exists"""
        containers = list(self.service.list_containers())
        exists = any([True for cont in containers if cont.name == container_name])
        if not exists:
            exists = self.service.create_container(name=container_name).exists()
        return exists

    def clear_destination(self, full_path: str):
        """method to clear destination"""
        container = self.service.get_container_client(container=self.container)
        # blobs = [pth for pth in container.walk_blobs() if pth == full_path]
        _ = [
            container.delete_blob(blob)
            for blob in container.walk_blobs()
            if blob.name.rsplit("/", maxsplit=1)[0] == full_path
        ]


class AzureJSONWriter(AzureWriter):
    """class to write JSON Objects to Azure"""

    def write_data(self, write_path: str, data: Union[Dict[Any, Any], List[Any]]):
        """method to write data"""

        if self.configs["auth_method"] != "sas_token":
            _ = self.check_exists(container_name=self.container)

        write_path = f"{write_path}.json"
        blob_client: BlobClient = self.service.get_blob_client(
            container=self.container, blob=write_path
        )
        blob_client.upload_blob(
            json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False),
            overwrite=self.overwrite,
        )
        print(f"done writting data to {self.container}/{write_path}")


class BaseWriter(ABC):
    """Base Writer Class"""

    def __init__(
        self,
        container: str,
        destination: str,
        configs: Dict[str, Any],
        clear_destination: bool = False,
    ):
        self.container = container
        self.destination = destination
        self.configs = configs
        self.service = self.__get_service()
        self.clear_destination = clear_destination
        self.curr_path: Union[str, None] = None

    def __get_service(self):
        services = {
            "azure_json": AzureJSONWriter,
            "local_json": LocalJSONWriter,
            "local_csv": LocalCSVWriter,
        }

        service = services[self.destination](self.container, self.configs)
        return service

    @abstractmethod
    def verify_data(
        self, payload: Union[List[Dict[Any, Any]], Dict[Any, Any], Any]
    ) -> Tuple[str, Union[List[Any], Dict[Any, Any], Any]]:
        """method to adjust data before writting to destination"""

        raise NotImplementedError

    def sink(self, payload, folder_path: str, path_prefix: Union[str, None] = None):
        """method to write data"""

        folder_path = (
            f"{prefix}/{folder_path}" if (prefix := path_prefix) else folder_path
        )
        data_path, data = self.verify_data(payload)
        write_path = f"{folder_path}/{data_path}"
        delete_path = write_path.rsplit("/", maxsplit=1)[0].strip()

        if not data:
            return

        if (self.clear_destination is True) and (self.curr_path != delete_path):
            self.service.delete_destination(delete_path=delete_path)
            self.curr_path = delete_path
        self.service.write_data(write_path, data)
