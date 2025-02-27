
class Config:
    downloaded_files_path = 'downloaded_files'
    metadata_file = 'file_metadata.json'
    GOOGLE_DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

    # With thanks to CG and Jon R, students on the course, for this fix needed for some users 
    text_loader_kwargs = {'encoding': 'utf-8'}
    # If that doesn't work, some Windows users might need to uncomment the next line instead
    # text_loader_kwargs={'autodetect_encoding': True}