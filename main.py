from download import Download
from vector_store import Chroma
from config_file import Config
from gradio_interface import GradioInterface
from dotenv import load_dotenv

def main():

    load_dotenv()  
    config = Config()
    dwnld = Download(config=config)
    chroma = Chroma(config=config)
    gradio = GradioInterface(config=config, chroma=chroma)
    
    # Ask for confirmation
    confirm = input("\nDo you want to download all files and folders? (yes/no): ")
    if confirm.lower() in ['yes', 'y']:
        print("Download is started...")
        # Download file from google drive
        dwnld.google_drive()

    # Ask for confirmation
    confirm = input("\nDo you want to add all files to chroma? (yes/no): ")
    if confirm.lower() in ['yes', 'y']:
        print("chroma process is started...")
        #chroma.remove_chroma_db()
        # Add documets to chroma
        chroma.process_and_store()

    # Visualize the vector store
    collection = chroma.db._collection
    count = collection.count()
    print(f"No. of documents in Chromadb collection: {count}")

    # Build & run gradio interface
    gradio.run()




if __name__ == '__main__':
    main()