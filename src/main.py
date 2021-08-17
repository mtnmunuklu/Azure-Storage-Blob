import sys
sys.path.append("../")
from src.app.azure import AzureBlob

if __name__ == "__main__":
    azureBlob = AzureBlob()
    azureBlob.download_azure_blob()