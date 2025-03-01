
class Config:
    downloaded_files_path = 'downloaded_files'
    metadata_file = 'files_metadata.json'
    db_persist_directory = 'chroma_db'
    GOOGLE_DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    # With thanks to CG and Jon R, students on the course, for this fix needed for some users 
    text_loader_kwargs = {'encoding': 'utf-8'}
    # If that doesn't work, some Windows users might need to uncomment the next line instead
    # text_loader_kwargs={'autodetect_encoding': True}
    collection_name = 'google_drive_collection'
    model = "gpt-4o-mini"
    folders_ignore = ['Research papers', 'Other paper reviews', 'Thesis', 'Videos', 'IAG', 'Photos', 'photos', 'videos', 'PhD']
