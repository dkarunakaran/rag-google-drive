from download import Download
from vector_store import Chroma
from config_file import Config
from dotenv import load_dotenv


def main():

    load_dotenv()  
    config = Config()
    # Download file from google drive
    #dwnld = Download(config=config)
    #dwnld.google_drive()

    # Add documets to chroma
    #chroma = Chroma(config=config)
    #chroma.process_and_store()

    # Visualize the vector store

    # Build gradio interface



if __name__ == '__main__':
    main()