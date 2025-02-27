from download import Download
from vector_store import Chroma
from config_file import Config


def main():
    
    config = Config()

    # Download file from google drive
    #dwnld = Download()
    #dwnld.google_drive()

    # Add documets to chroma
    chroma = Chroma(config=config)

    # Visualize the vector store

    # Build gradio interface



if __name__ == '__main__':
    main()