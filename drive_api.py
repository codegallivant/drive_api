from pydrive.drive import GoogleDrive 
from pydrive.auth import GoogleAuth 
import os 


class DriveAPI:
    def __init__(self, secrets_file_path, credentials_path):
        GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = secrets_file_path
        self.credentials_path = credentials_path
        self.gauth = None
        self.drive = None

    def authenticate_client(self):
        self.gauth = GoogleAuth()
        gauth=self.gauth

        # Try to load saved client credentials
        gauth.LoadCredentialsFile(self.credentials_path)

        if gauth.credentials is None:
            # Authenticate if they're not there
            gauth.GetFlow()
            gauth.flow.params.update({'access_type': 'offline'})
            gauth.flow.params.update({'approval_prompt': 'force'})
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            # Refresh them if expired
            gauth.Refresh()
        else:
            # Initialize the saved creds
            gauth.Authorize()

        # Save the current credentials to a file
        gauth.SaveCredentialsFile(self.credentials_path)  #Note that credentials will expire after some time and may not refresh. When this happens, delete the mycreds.txt file and run the program again. A new and valid mycreds.txt will automatically be created.
        self.drive = GoogleDrive(self.gauth)


    def list_files(self, folder_id):
        return self.drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()


    def get_id(self, folder_path):

        fileID = None

        try:

            folder_path = folder_path.split('/')
            # print(folder_path)
            for index, folder_name in enumerate(folder_path):
                if len(folder_name.strip()) == 0:
                    continue
                # print("Current",folder_name)
                if index > 0:
                    fileList = self.drive.ListFile({'q': f"'{fileID}' in parents and trashed=false"}).GetList()
                else:
                    fileList = self.drive.ListFile({'q': f"'root' in parents and trashed=false"}).GetList()
                found = False
                for file in fileList:
                    # print(folder_name)
                    if file['title']==folder_name:
                        fileID = file['id']
                        found = True
                        break
                if not found:
                    fileID = False
        except:

            fileID = False

        finally:

            return fileID


    def upload_file(self, target_folder_path , home_path, file_name):

        # authenticate_client()

        target_id = self.get_id(target_folder_path)
        if target_id == False:
            print(f"[ ERROR in gprocesses.py ] : {target_folder_path} not found.")
            return False
        home_path = rf"{home_path}"

        f = self.drive.CreateFile({
            'title': file_name, 
            'parents': [{'id': target_id}]
            }) 
        f.SetContentFile(os.path.join(home_path, file_name)) 
        f.Upload()

# Example: upload_file('<drive_folder_name>/<drive_folder_name>/.../<drive_folder_name>',rf"C:/.../<system_directory_name>", "<file_name>")


    def upload_folder(self, target_folder_path, home_path):

        target_id = self.get_id(target_folder_path)
        if target_id == False:
            print(f"[ ERROR in gprocesses.py ] : {target_folder_path} not found.")
            return False

        home_path = rf"{home_path}"
        folder_name = os.path.basename(home_path)
        f = self.drive.CreateFile({
            'title': folder_name,
            'parents': [{'id': target_id}],
            'mimeType': 'application/vnd.google-apps.folder'
            })

        folder = self.drive.CreateFile(f)

        folder.Upload()
        
        for name in os.listdir(home_path):
            path = home_path +'/'+ name
            if os.path.isfile(path):
                self.upload_file(target_folder_path+'/'+folder_name, home_path, name)
            elif os.path.isdir(path):
                self.upload_folder(target_folder_path+'/'+folder_name,  path)


# Example: upload_folder('<drive_folder_name>/<drive_folder_name>/.../<drive_folder_name>',rf"C:/.../<folder_name>")


    def download_file(self, target_file_path, home_path):

        target_id = self.get_id(target_file_path)
        if target_id == False:
            print(f"[ ERROR in gprocesses.py ] : {target_file_path} not found.")
            return False
        home_path = rf"{home_path}"

        file = self.drive.CreateFile({'id': target_id})
        working_path = os.getcwd()
        os.chdir(home_path)
        file.GetContentFile(file['title'])
        os.chdir(working_path)


# Example: download_file("<drive_folder_name>/<drive_folder_name>/.../<file_name>", "C:/.../<system_directory_name>")

    def download_folder(self, target_folder_path, home_path, files_only = True):
        #If files_only = True, only files will be downloaded. If files_only = False, parent folder containing the files will be downloaded along with its contents.
        
        working_path = os.getcwd()

        target_id = self.get_id(target_folder_path)

        if target_id == False:
            print(f"[ ERROR in gprocesses.py ] : {target_folder_path} not found.")
            return False
        home_path = rf"{home_path}"

        if files_only == False:
            home_path = os.path.join(home_path,target_folder_path.split('/')[len(target_folder_path.split('/'))-1])
            print(home_path)
            os.mkdir(home_path, 0o666)

        files=self.list_files(target_id)
        for file in files:
            file = self.drive.CreateFile({'id': file['id']})
            os.chdir(home_path)
            file.GetContentFile(file['title'])
            os.chdir(working_path)


# download_folder ("<drive_folder_name>/<drive_folder_name>/.../<drive_folder_name>", "C:/.../<system_directory_name>")

    def delete_file(self, target_file_path):

        target_id = self.get_id(target_file_path)
        if target_id == False:
            print(f"[ ERROR in gprocesses.py ] : {target_file_path} not found.")
            return False

        file = self.drive.CreateFile({'id': target_id})
        file.Trash()