
import os
import logging
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
        self.max_retry = Config.MAXRETY
        self.logger = Logger('File')

    def download_azure_blob(self):
        """
        Used for pull blobs from azure blob storage
        :return: None
        """
        try:
            yesterday = datetime.now() - timedelta(1)
            log_date = datetime.strftime(yesterday, '%Y%m%d')
            blob_service_client = BlockBlobService(account_name=self.storage_account_name, account_key=self.storage_account_key)
            blob_service_client._httpclient = ExampleRawBodyReadingClient(session=requests.session(), protocol="https", timeout=2000)
            #List blobs in storage account
            for blob in blob_service_client.list_blobs(container_name=self.container_name, prefix="logs/"+log_date):
                for retry in range(1, self.max_retry + 1):   
                    try:
                        # If blob_name is a path, extract the file_name
                        last_sep = blob.name.rfind('/')
                        if last_sep != -1:
                            file_name = blob.name[last_sep+1:]
                        else:
                            file_name = blob.name
                        download_path = os.path.join(self.output, file_name)
                        blob_service_client.get_blob_to_path(container_name=self.container_name, blob_name=blob.name,
                                file_path=download_path, validate_content=True)
                        self.gunzip_file(file_name, download_path, retry)
                        #delete blob
                        #blob_service_client.delete_blob(container_name=self.container_name, blob_name=blob.name)
                        self.logger.log(logging.WARNING, "Azure Blob download successful, Blob Name:{}".format(blob.name))
                        break
                    except Exception as e:
                        self.logger.log(logging.WARNING, "Rety:{} Azure Blog download unsuccessful, Blob Name:{}".format(retry, blob.name))
                        self.logger.log(logging.ERROR, e)  
        except Exception as e:
            self.logger.log(logging.WARNING, "Blob downloads unsuccessful")
            self.logger.log(logging.ERROR, e)

    def gunzip_file(self, file_name, download_path, retry):
        try:
            with gzip.open(download_path, 'rb') as f_in:
                with open(self.outputd + file_name.strip('gz'), 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        except Exception as e:
            self.logger.log(logging.WARNING, "Rety:{} Gunzip Error, File Name:{}".format(retry, file_name))
            self.logger.log(logging.ERROR, e)