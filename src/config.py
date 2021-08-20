import os
from dotenv import load_dotenv
from pathlib import Path  # python3 only

# load enviorment variables
env_path = 'src/.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """
    Set Flask configuration vars from .env file
    """

    # Load in environment variables
    LOG_DIR = os.getenv('LOG_DIR')
    LOG_FILE = os.getenv('LOG_FILE')
    LOG_FORMAT = os.getenv('LOG_FORMAT')
    STORAGE_ACCOUNT_NAME = os.getenv('STORAGE_ACCOUNT_NAME')
    STORAGE_ACCOUNT_KEY = os.getenv('STORAGE_ACCOUNT_KEY')
    CONTANINER_NAME = os.getenv('CONTANINER_NAME')
    OUTPUT = os.getenv('OUTPUT')
    DECOMPRESS_OUTPUT = os.getenv('DECOMPRESS_OUTPUT')
    BLOB_PREFIX = os.getenv('BLOB_PREFIX')
    LAST_LOG_HOURS = int(os.getenv('LAST_LOG_HOURS'))
    MAXRETY = int(os.getenv('MAXRETY'))
    


