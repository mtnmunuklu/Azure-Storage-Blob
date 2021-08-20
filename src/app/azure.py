import os
import time
import logging
from azure.storage.blob.models import Include
import requests
import gzip
import shutil
from datetime import datetime, timedelta
from src.app.logger import Logger
from src.config import Config
from azure.storage.blob import BlockBlobService
from src.app.client import ExampleRawBodyReadingClient

class AzureBlob:
    """
    Used for get blob from azure blob storage
    """
    def __init__(self):
        """
        Constructor Method
        :return: None
        """
        self.storage_account_name = Config.STORAGE_ACCOUNT_NAME
        self.storage_account_key = Config.STORAGE_ACCOUNT_KEY
        self.container_name = Config.CONTANINER_NAME
        self.output = Config.OUTPUT
        self.outputd = Config.DECOMPRESS_OUTPUT
        self.blob_prefix = Config.BLOB_PREFIX
        self.last_log_hours = Config.LAST_LOG_HOURS
        self.max_retry = Config.MAXRETY
        self.logger = Logger('File')

    def download_azure_blob(self):
        """
        Used for pull blobs from azure blob storage
        :return: None
        """
        try:
            blob_service_client = BlockBlobService(account_name=self.storage_account_name, account_key=self.storage_account_key)
            blob_service_client._httpclient = ExampleRawBodyReadingClient(session=requests.session(), protocol="https", timeout=500)
            today = datetime.now()
            #log_date = datetime.strftime(today, '%Y%m%d')
            #To go back an hour and get the log
            first_log_date = datetime.strftime(today - timedelta(hours=self.last_log_hours), '%Y%m%dT%H')
            first_log_date_directory = datetime.strftime(today - timedelta(hours=self.last_log_hours), '%Y%m%d')
            prefix = self.blob_prefix + first_log_date_directory + "/" + first_log_date
            for blob in blob_service_client.list_blobs(container_name=self.container_name, prefix=prefix):
            #List blobs in storage account
            #for blob in blob_service_client.list_blobs(container_name=self.container_name, prefix=self.blob_prefix + log_date):
                if blob_service_client.exists(container_name=self.container_name, blob_name=blob.name):
                    for retry in range(1, self.max_retry + 1):   
                        try:
                            file_date = datetime.now()
                            file_name = "cloudflare-" + datetime.strftime(file_date, '%Y%m%d%H%M%S') + '.log.gz'
                            download_path = os.path.join(self.output, file_name)
                            blob_service_client.get_blob_to_path(container_name=self.container_name, blob_name=blob.name,
                                    file_path=download_path, validate_content=True)
                            self.logger.log(logging.INFO, "Azure Blob download successful, Blob Name:{}".format(blob.name))
                            self.gunzip_file(file_name, download_path, retry)
                            self.remove_file(download_path)
                            #delete blob
                            blob_service_client.delete_blob(container_name=self.container_name, blob_name=blob.name)
                            self.logger.log(logging.INFO, "Azure Blob remove successful, Blob Name:{}".format(blob.name))
                            break
                        except Exception as e:
                            self.logger.log(logging.WARNING, "Rety:{} Azure Blog download unsuccessful, Blob Name:{}".format(retry, blob.name))
                            self.logger.log(logging.ERROR, e)
                    time.sleep(0.5)
                else:
                   self.logger.log(logging.WARNING, "Blob does not exists. Blob Name:{}".format(blob.name)) 
        except Exception as e:
            self.logger.log(logging.WARNING, "Blob downloads unsuccessful")
            self.logger.log(logging.ERROR, e)

    def gunzip_file(self, file_name, download_path, retry):
        try:
            with gzip.open(download_path, 'rb') as f_in:
                with open(self.outputd + file_name.replace('.gz',''), 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            self.logger.log(logging.INFO, "Gunzip is successful, File Name:{}".format(file_name))
        except Exception as e:
            self.logger.log(logging.WARNING, "Rety:{} Gunzip Error, File Name:{}".format(retry, file_name))
            self.logger.log(logging.ERROR, e)

    def remove_file(self, download_path):
        try:
            if os.path.exists(download_path):
                os.remove(download_path)
            self.logger.log(logging.INFO, "File remove is successful, File Path:{}".format(download_path))
        except Exception as e:
            self.logger.log(logging.WARNING, "File Remove Error, Path:{}".format(download_path))
            self.logger.log(logging.ERROR, e)
