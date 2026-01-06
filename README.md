# drive_api

Python API to for easy one-line upload/download to Google Drive.

## Requirements
- Python 3
- pip modules
	- pydrive
- Google Cloud Console credentials file (with Google Drive API enabled)


## Usage

```py
import drive_api as gdi # Import file

# Specify path to credentials file for Google Drive API
api = gdi.DriveAPI("client_secrets.json", "creds.txt")

# Authenticate 
api.authenticate_client("creds.txt") # Saves access token credentials to creds.txt. If file does not exist, one-time manual sign-in is done via browser and the file is auto-generated.

# Get id of file/folder
f_id = api.get_id("path/to/drive_folder")

# Get list of files in a folder
file_list = api.list_files(f_id)

# Upload a file
gdi.upload_file('path/to/drive_folder', "path/to/system_folder", "filename on system")

# Upload a folder
gdi.upload_folder(client, 'path/to/drive_folder',rf"path/to/system_folder")

# Download a file
gdi.download_file(client, "path/to/drive_folder", "path/to/system_folder")

# Download a folder
gdi.download_folder(client, "path/to/drive_folder", "path/to/system_folder", files_only=False) # Set files_only = True if you only want the files within, and not the folder itself
```

## How to get a `client_secrets.json` file
To be able to successfully authenticate with your Drive account, you must download a secrets file from [Google's API Console](console.developers.google.com). In the above example, it is `client_secrets.json`.