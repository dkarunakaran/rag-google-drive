import os
from pathlib import Path
# Langchain imports
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_community.vectorstores import Chroma as ChromaStore
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from typing import Dict, Any
import hashlib
import re
import json
import tiktoken


class Chroma:
    def __init__(self, config):
        self.config = config
        self.pdf_count = 0
        self.docx_count = 0
        enc = tiktoken.get_encoding("cl100k_base") # get the encoding that openAI uses.
        self.embeddings = OpenAIEmbeddings(disallowed_special=(enc.special_tokens_set - {'<|endoftext|>'}))    
        self.db = ChromaStore(
            collection_name=self.config.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.config.db_persist_directory
        )
    '''
    def remove_chroma_db(self):
        try:
            shutil.rmtree(self.config.db_persist_directory)
            print(f"Directory '{self.config.db_persist_directory}' and its contents removed.")
            self.db = ChromaStore(
                collection_name=self.config.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.config.db_persist_directory
            )
        except FileNotFoundError:
            print(f"Directory '{self.config.db_persist_directory}' not found.")
        except OSError as e:
            print(f"Error removing directory '{self.config.db_persist_directory}': {e}")
    '''

    def get_documents(self):
        """
        Recursively load all PDF and DOCX documents from the directory
        """
        self.directory_path = Path(self.config.downloaded_files_path)
        all_docs = []
        
        if not self.directory_path.exists() or not self.directory_path.is_dir():
            print(f"The directory {self.directory_path} does not exist or is not a directory")
            return all_docs
        
        # Walk through all files and directories
        for root, _, files in os.walk(self.directory_path):
            for file in files:
                file_path = Path(root) / file
                file_extension = file_path.suffix.lower()
                try:    
                    # Process PDFs
                    if file_extension == '.pdf':
                        print(f"Loading PDF: {file_path}")
                        loader = PyPDFLoader(str(file_path))
                        docs = loader.load()
                        # Enhance the metadata for each document page
                        enhanced_docs = self.enhance_document_metadata(docs, file_path)
                        all_docs.extend(enhanced_docs)
                        self.pdf_count += 1
                    
                    # Process DOCX files
                    elif file_extension == '.docx':
                        print(f"Loading DOCX: {file_path}")
                        loader = Docx2txtLoader(str(file_path))
                        docs = loader.load()
                        # Enhance the metadata for each document page
                        enhanced_docs = self.enhance_document_metadata(docs, file_path)
                        all_docs.extend(enhanced_docs)
                        self.docx_count += 1
                
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

        return all_docs
    

    def enhance_document_metadata(self, docs, file_path):
        """
        Enhance document metadata by combining file metadata with document-specific metadata
        """
        enhanced_docs = []
        for doc in docs:
            # Start with the file metadata
            enhanced_metadata = self.get_metadata(file_path)
            # Add any existing metadata from the document
            #if hasattr(doc, 'metadata') and doc.metadata:
            #    enhanced_metadata.update(doc.metadata)
            
            # Check if the document content has headers/titles
            content = doc.page_content
            
            # Try to extract a title from the content (if it starts with a header-like pattern)
            title_match = re.match(r'^#+\s+(.+)$', content.strip().split('\n')[0]) if content else None
            if title_match:
                enhanced_metadata['title'] = title_match.group(1)
            
            # Create a new document with enhanced metadata
            enhanced_doc = Document(
                page_content=str(content),
                metadata=enhanced_metadata
            )
            
            enhanced_docs.append(enhanced_doc)
        
        return enhanced_docs
    
    def get_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        get metadata from the json file
        """
        # Generate file hash for unique identification
        file_hash = ""
        try:
            with open(file_path, "rb") as f:
                content = f.read()
                file_hash = hashlib.md5(content).hexdigest()
        except Exception as e:
            print(f"Could not generate hash for {file_path}: {e}")

        with open(self.config.metadata_file) as f:
            d = json.load(f)

        metadata = d[file_hash]

        return metadata

    def process_and_store(self):
        # Load all documents
        documents = self.get_documents()
        if not documents:
            print("No documents were loaded")
            return None
        
        text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=300)
        chunks = text_splitter.split_documents(documents)
        print(f"Total number of chunks: {len(chunks)}")
        # Adding documents to vector store
        print(f"Adding document to Chroma vector store")
        self.db.add_documents(documents=chunks)



        