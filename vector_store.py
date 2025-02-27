import glob
import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader


class Chroma:
    def __init__(self, config):
        self.config = config
        self.get_docuements()

    def __add_metadata(self, doc, doc_type):
        doc.metadata["doc_type"] = doc_type
        return doc

    def get_docuements(self):
        dir = glob.glob(self.config.downloaded_files_path+"/*")
        documents = []
        for folder in dir:
            doc_type = os.path.basename(folder)
            loader = DirectoryLoader(folder, glob="**/*.md", loader_cls=TextLoader, loader_kwargs=self.config.text_loader_kwargs)
            folder_docs = loader.load()
            print(doc_type)
            documents.extend([self.__add_metadata(doc, doc_type) for doc in folder_docs])
