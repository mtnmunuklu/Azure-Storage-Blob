# Azure-Storage-Blob
This application provides downloading existing files under the specified container from Azure Storage Blob. When the application runs, it finds the current day and downloads the files under the logs/{today}/. If the md5 hash of the downloaded file is the same as the md5 hash in the azure storage blob, the relevant file in the azure storage blob is deleted. Problems experienced during the download process are logged to the azureblob.log file under the logs folder.

Don't forget to edit the .env file located in the src directory. OUTPUT in the relevant file indicates where the gz extension files will be downloaded, and DECOMPRESS_OUTPUT indicates where the downloaded gz file will be extracted after opening.

If you encounter a problem with the libraries used, You can run the _pip_install.sh script after deleting the venv file.

You can add the following line to the crontab for the application to run every night. It is necessary to arrange the time it will work and the directories it is in.
10 * * * * cd /home/clog/metin/Azure-Storage-Blob/src && /home/clog/metin/Azure-Storage-Blob/venv/bin/python3 main.py
