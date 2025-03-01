from download import Download
from vector_store import Chroma
from config_file import Config
from gradio_interface import GradioInterface
from dotenv import load_dotenv

def main():

    load_dotenv()  
    config = Config()
    # Download file from google drive
    #dwnld = Download(config=config)
    #dwnld.google_drive()

    # Add documets to chroma
    chroma = Chroma(config=config)
    #chroma.process_and_store()

    # Visualize the vector store
    collection = chroma.db._collection
    count = collection.count()
    print(f"No. of documents in Chromadb collection: {count}")

    # Build & run gradio interface
    gradio = GradioInterface(config=config, chroma=chroma)
    gradio.run()




if __name__ == '__main__':
    main()