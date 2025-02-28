from __future__ import print_function
import os
import pickle
import io
import json
from datetime import datetime
from google_drive import GoogleDrive
from config_file import Config

class Download:
    def __init__(self, config):
        self.config = config
        self.gd = GoogleDrive(config=self.config)
        
    def google_drive(self):
        print("\nStructure of your Google Drive:")
        self.gd.list_all_files()
        # Get download location
        local_base_path = self.config.downloaded_files_path
        # Make sure base directory exists
        os.makedirs(local_base_path, exist_ok=True)
        print(f"\nMapping Google Drive structure...")
        drive_map = self.gd.map_drive_structure()
        print(f"Found {len(drive_map['files'])} files in {len(drive_map['folders'])} folders.")
        print(f"Downloading all files to: {os.path.abspath(local_base_path)}")
        self.gd.download_files(drive_map, local_base_path)
        print("\nDownload complete!")
        self.gd.save_metadata()


if __name__ == '__main__':
    download = Download()
    download.google_drive()