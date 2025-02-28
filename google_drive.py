import io
import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import datetime
import hashlib
from pathlib import Path
import mimetypes


class GoogleDrive:

    def __init__(self, config):
        self.config = config
        self.authenticate()
        if os.path.exists(self.config.metadata_file):
            os.remove(self.config.metadata_file)
        self.metadata = {}

    def authenticate(self):
        # If modifying these scopes, delete the file token.json.
        SCOPES = self.config.GOOGLE_DRIVE_SCOPES
        # Authenticate
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0, open_browser=False)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        self.service = build('drive', 'v3', credentials=creds)


    def list_all_files(self, folder_id='root', path='', indent=0):
        """List all files and folders recursively from the specified folder."""
        # Get all files and folders in the current folder
        results = []
        page_token = None
        
        while True:
            response = self.service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                spaces='drive',
                fields='nextPageToken, files(id, name, mimeType)',
                pageToken=page_token
            ).execute()
            
            results.extend(response.get('files', []))
            page_token = response.get('nextPageToken')
            
            if not page_token:
                break
        
        # Print the current path
        print(f"{' ' * indent}📂 {path or 'My Drive'}")
        
        # Process files and folders
        folders = []
        files = []
        
        for item in results:
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                folders.append(item)
            else:
                files.append(item)
        
        # First list all folders
        for folder in folders:
            new_path = os.path.join(path, folder['name'])
            self.list_all_files(folder['id'], new_path, indent + 2)
        
        # Then list all files
        for file in files:
            print(f"{' ' * (indent + 2)}📄 {file['name']}")

    def map_drive_structure(self, folder_id='root', path=''):
        """Map the structure of Google Drive and return a dictionary of all files and folders."""
        drive_map = {'files': [], 'folders': []}
        
        # Get all files and folders in the current folder
        results = []
        page_token = None
        
        while True:
            response = self.service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                spaces='drive',
                fields='nextPageToken, files(id, name, mimeType, size, modifiedTime)',
                pageToken=page_token
            ).execute()

            results.extend(response.get('files', []))
            page_token = response.get('nextPageToken')
            
            if not page_token:
                break
        
        # Process files and folders
        for item in results:
            item_path = os.path.join(path, item['name'])
            
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                # Add folder to the map
                drive_map['folders'].append({
                    'id': item['id'],
                    'name': item['name'],
                    'path': item_path
                })
                
                # Recursively map files from this folder
                sub_map = self.map_drive_structure(item['id'], item_path)
                drive_map['files'].extend(sub_map['files'])
                drive_map['folders'].extend(sub_map['folders'])
            else:
                # Add file to the map
                drive_map['files'].append({
                    'id': item['id'],
                    'name': item['name'],
                    'google_drive_url': f"https://drive.google.com/file/d/{item['id']}/view",
                    'path': item_path,
                    'mime_type': item['mimeType'],
                    'size': item.get('size'),
                    'modified_time': item.get('modifiedTime')
                })
        
        return drive_map
    
    def download_files(self, drive_map, local_base_path):
        """Download all files from Google Drive and remove local files that no longer exist in Drive."""
        # Create a set of all remote file paths
        remote_paths = {item['path'] for item in drive_map['files']}
        local_files_to_delete = []
        
        # First, create all folders
        print("\nCreating folder structure...")
        for folder in drive_map['folders']:
            folder_path = os.path.join(local_base_path, folder['path'])
            if not os.path.exists(folder_path):
                os.makedirs(folder_path, exist_ok=True)
                print(f"Created directory: {folder_path}")
        
        # Find local files that don't exist in remote
        print("\nChecking for files to delete...")
        for root, dirs, files in os.walk(local_base_path):
            for file in files:
                local_path = os.path.join(root, file)
                rel_path = os.path.relpath(local_path, local_base_path)
                
                if rel_path not in remote_paths:
                    local_files_to_delete.append(local_path)
        
        # Delete local files that don't exist in Google Drive
        if local_files_to_delete:
            print(f"Found {len(local_files_to_delete)} files to delete.")
            for file_path in local_files_to_delete:
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {str(e)}")
        else:
            print("No files to delete.")
        
        # Download all files
        print("\nDownloading files...")
        total_files = len(drive_map['files'])
        for index, file_item in enumerate(drive_map['files']):
            file_id = file_item['id']
            file_name = file_item['name']
            file_path = os.path.join(local_base_path, file_item['path'])
            progress = f"[{index+1}/{total_files}]"
            
            # Check if file is a Google Workspace file
            if file_item['mime_type'].startswith('application/vnd.google-apps'):
                self.handle_google_workspace_file(file_item, file_path)
            else:
                # Regular file download
                try:
                    request = self.service.files().get_media(fileId=file_id)
                    file_size = int(file_item.get('size', 0)) if file_item.get('size') else 'unknown'
                    file_size_str = f"{file_size / 1024 / 1024:.2f} MB" if isinstance(file_size, int) else file_size
                    
                    print(f"{progress} Downloading: {file_item['path']} ({file_size_str})")
                    
                    # Create directory if it doesn't exist
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    with open(file_path, 'wb') as f:                        
                        downloader = MediaIoBaseDownload(f, request)
                        done = False
                        while not done:
                            status, done = downloader.next_chunk()
                            print(f"\r{progress} Download {int(status.progress() * 100)}%", end="")
                        print()  # New line after download completes

                    #--------Extract rich metadata from a file-------
                    file_path = Path(file_path)
                    directory_path = Path(self.config.downloaded_files_path)
                    stat_info = file_path.stat()
                    
                    # Get file information
                    #file_size = stat_info.st_size
                    created_time = datetime.datetime.fromtimestamp(stat_info.st_ctime)
                    modified_time = datetime.datetime.fromtimestamp(stat_info.st_mtime)
                    
                    # Get relative path from the base directory
                    rel_path = file_path.relative_to(directory_path)
                    
                    # Generate file hash for unique identification
                    file_hash = ""
                    try:
                        with open(file_path, "rb") as f:
                            content = f.read()
                            file_hash = hashlib.md5(content).hexdigest()
                    except Exception as e:
                        print(f"Could not generate hash for {file_path}: {e}")
                    
                    # Get mime type
                    mime_type, _ = mimetypes.guess_type(str(file_path))
                    
                    # Build metadata dict                    
                    self.metadata[file_hash] = {
                        "source": str(file_path),
                        "filename": file_path.name,
                        "extension": file_path.suffix.lower(),
                        "created_date": created_time.isoformat(),
                        "modified_date": modified_time.isoformat(),
                        "relative_path": str(rel_path),
                        "parent_directory": str(rel_path.parent),
                        "file_hash": file_hash,
                        "mime_type": mime_type or "unknown",
                        "processing_date": datetime.datetime.now().isoformat(),
                        "google_drive_url": file_item['google_drive_url'],
                        "google_drive_id": file_item['id']
                    }
                    
                except Exception as e:
                    print(f"Error downloading {file_name}: {str(e)}")

        # Clean up empty directories
        self.clean_empty_directories(local_base_path)

    def handle_google_workspace_file(self, file_item, file_path):
        """Handle Google Workspace files (Docs, Sheets, Slides, etc.) by exporting them."""
        file_id = file_item['id']
        mime_type = file_item['mime_type']
        file_name = file_item['name']
        
        # Define export formats for Google Workspace files
        export_formats = {
            'application/vnd.google-apps.document': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.google-apps.presentation': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'application/vnd.google-apps.drawing': 'application/pdf',
            'application/vnd.google-apps.script': 'application/vnd.google-apps.script+json'
        }
        
        # Set file extensions
        extensions = {
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
            'application/pdf': '.pdf',
            'application/vnd.google-apps.script+json': '.json'
        }
        
        if mime_type in export_formats:
            export_mime = export_formats[mime_type]
            file_extension = extensions.get(export_mime, '')
            
            # Make sure we add the right extension if it's not already there
            if not file_path.endswith(file_extension):
                file_path = f"{file_path}{file_extension}"
            
            try:
                request = self.service.files().export_media(fileId=file_id, mimeType=export_mime)
                
                print(f"Exporting Google Workspace file: {file_name} as {file_extension}")
                
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                with open(file_path, 'wb') as f:
                    downloader = MediaIoBaseDownload(f, request)
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                        print(f"\rExport {int(status.progress() * 100)}%", end="")
                    print()  # New line after export completes
                
                #--------Extract rich metadata from a file-------
                file_path = Path(file_path)
                directory_path = Path(self.config.downloaded_files_path)
                stat_info = file_path.stat()
                
                # Get file information
                #file_size = stat_info.st_size
                created_time = datetime.datetime.fromtimestamp(stat_info.st_ctime)
                modified_time = datetime.datetime.fromtimestamp(stat_info.st_mtime)
                
                # Get relative path from the base directory
                rel_path = file_path.relative_to(directory_path)
                
                # Generate file hash for unique identification
                file_hash = ""
                try:
                    with open(file_path, "rb") as f:
                        content = f.read()
                        file_hash = hashlib.md5(content).hexdigest()
                except Exception as e:
                    print(f"Could not generate hash for {file_path}: {e}")
                
                # Get mime type
                mime_type, _ = mimetypes.guess_type(str(file_path))

                # Build metadata dict                    
                self.metadata[file_hash] = {
                    "source": str(file_path),
                    "filename": file_path.name,
                    "extension": file_path.suffix.lower(),
                    "created_date": created_time.isoformat(),
                    "modified_date": modified_time.isoformat(),
                    "relative_path": str(rel_path),
                    "parent_directory": str(rel_path.parent),
                    "file_hash": file_hash,
                    "mime_type": mime_type or "unknown",
                    "processing_date": datetime.datetime.now().isoformat(),
                    "google_drive_url": file_item['google_drive_url'],
                    "google_drive_id": file_item['id']
                }
                
                print(f"Exported: {file_path}")
            except Exception as e:
                print(f"Error exporting {file_name}: {str(e)}")
        else:
            print(f"Unsupported Google Workspace format: {mime_type} for file: {file_name}")

    def save_metadata(self):
         # Serializing json
        json_object = json.dumps(self.metadata, indent=4)
        
        # Writing to sample.json
        with open(self.config.metadata_file, "w") as outfile:
            outfile.write(json_object)

    def clean_empty_directories(self, path):
        """Recursively remove empty directories."""
        for root, dirs, files in os.walk(path, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):  # Check if directory is empty
                        os.rmdir(dir_path)
                        print(f"Removed empty directory: {dir_path}")
                except Exception as e:
                    print(f"Error removing directory {dir_path}: {str(e)}")