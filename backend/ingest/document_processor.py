"""
Document processing and indexing system for environmental documents
"""
import os
import requests
from pathlib import Path
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse
import logging

from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.vectorstores import FAISS, Chroma
from langchain_community.embeddings import OllamaEmbeddings

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import (
    DOCUMENTS_DIR, VECTOR_STORE_DIR, VECTOR_STORE_TYPE, 
    CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL, DOCUMENT_SOURCES
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles document loading, processing, and vector store creation"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )
        self.embeddings = OllamaEmbeddings(
            model="llama3.1:8b",
            base_url="http://localhost:11434"
        )
        self.vector_store = None
        
    def load_documents(self) -> List[Document]:
        """Load documents from various sources"""
        documents = []
        
        # Load documents from configured sources
        for source in DOCUMENT_SOURCES:
            try:
                if source["type"] == "website":
                    docs = self._load_website(source["url"], source["name"])
                    documents.extend(docs)
                elif source["type"] == "pdf":
                    docs = self._load_pdf(source["url"], source["name"])
                    documents.extend(docs)
                logger.info(f"Loaded {len(docs)} documents from {source['name']}")
            except Exception as e:
                logger.error(f"Error loading {source['name']}: {str(e)}")
        
        # Load local PDFs from documents directory
        local_docs = self._load_local_pdfs()
        documents.extend(local_docs)
        
        return documents
    
    def _load_website(self, url: str, name: str) -> List[Document]:
        """Load documents from a website"""
        try:
            loader = WebBaseLoader(url)
            docs = loader.load()
            
            # Add metadata
            for doc in docs:
                doc.metadata.update({
                    "source": name,
                    "url": url,
                    "type": "website"
                })
                
            return docs
        except Exception as e:
            logger.error(f"Error loading website {url}: {str(e)}")
            return []
    
    def _load_pdf(self, url: str, name: str) -> List[Document]:
        """Load PDF documents"""
        try:
            # Download PDF if it's a URL
            if url.startswith("http"):
                response = requests.get(url)
                pdf_path = DOCUMENTS_DIR / f"{name}.pdf"
                with open(pdf_path, "wb") as f:
                    f.write(response.content)
            else:
                pdf_path = Path(url)
            
            loader = PyPDFLoader(str(pdf_path))
            docs = loader.load()
            
            # Add metadata and preserve page information
            for doc in docs:
                # PyPDFLoader already includes page information in metadata
                page_number = doc.metadata.get('page', 0) + 1  # Convert 0-based to 1-based
                doc.metadata.update({
                    "source": name,
                    "url": url,
                    "type": "pdf",
                    "page_number": page_number,
                    "original_page": doc.metadata.get('page', 0)  # Keep original for reference
                })
                
            return docs
        except Exception as e:
            logger.error(f"Error loading PDF {url}: {str(e)}")
            return []
    
    def _load_local_pdfs(self) -> List[Document]:
        """Load all PDF files from the documents directory"""
        documents = []
        pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))
        
        logger.info(f"Found {len(pdf_files)} PDF files in {DOCUMENTS_DIR}")
        
        for pdf_file in pdf_files:
            try:
                # Skip hidden files and .gitkeep
                if pdf_file.name.startswith('.') or pdf_file.name == '.gitkeep':
                    continue
                    
                logger.info(f"Loading local PDF: {pdf_file.name}")
                loader = PyPDFLoader(str(pdf_file))
                docs = loader.load()
                
                # Extract document name without extension
                doc_name = pdf_file.stem
                
                # Add metadata and preserve page information
                for doc in docs:
                    page_number = doc.metadata.get('page', 0) + 1  # Convert 0-based to 1-based
                    doc.metadata.update({
                        "source": doc_name,
                        "url": str(pdf_file),
                        "type": "local_pdf",
                        "page_number": page_number,
                        "original_page": doc.metadata.get('page', 0),
                        "file_path": str(pdf_file),
                        "file_name": pdf_file.name
                    })
                    
                documents.extend(docs)
                logger.info(f"Loaded {len(docs)} pages from {pdf_file.name}")
                
            except Exception as e:
                logger.error(f"Error loading local PDF {pdf_file}: {str(e)}")
                
        logger.info(f"Total local PDF documents loaded: {len(documents)}")
        return documents
    
    def process_documents(self, documents: List[Document]) -> List[Document]:
        """Process and chunk documents"""
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Add chunk metadata and preserve page information
        for i, chunk in enumerate(chunks):
            # Preserve page information from original document
            page_number = chunk.metadata.get('page_number', 'N/A')
            original_page = chunk.metadata.get('original_page', 'N/A')
            
            chunk.metadata.update({
                "chunk_id": i,
                "chunk_size": len(chunk.page_content),
                "page_number": page_number,
                "original_page": original_page
            })
            
        logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
        return chunks
    
    def create_vector_store(self, documents: List[Document]) -> None:
        """Create and save vector store"""
        logger.info(f"Creating {VECTOR_STORE_TYPE} vector store...")
        
        if VECTOR_STORE_TYPE == "faiss":
            self.vector_store = FAISS.from_documents(
                documents, 
                self.embeddings
            )
            self.vector_store.save_local(str(VECTOR_STORE_DIR / "faiss_index"))
            
        elif VECTOR_STORE_TYPE == "chroma":
            self.vector_store = Chroma.from_documents(
                documents,
                self.embeddings,
                persist_directory=str(VECTOR_STORE_DIR / "chroma_db")
            )
            self.vector_store.persist()
            
        logger.info("Vector store created and saved successfully")
    
    def load_vector_store(self):
        """Load existing vector store"""
        try:
            if VECTOR_STORE_TYPE == "faiss":
                self.vector_store = FAISS.load_local(
                    str(VECTOR_STORE_DIR / "faiss_index"),
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
            elif VECTOR_STORE_TYPE == "chroma":
                self.vector_store = Chroma(
                    persist_directory=str(VECTOR_STORE_DIR / "chroma_db"),
                    embedding_function=self.embeddings
                )
            logger.info("Vector store loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            return False
    
    def search_documents(self, query: str, k: int = 5) -> List[Document]:
        """Search for relevant documents"""
        if self.vector_store is None:
            raise ValueError("Vector store not loaded")
            
        return self.vector_store.similarity_search(query, k=k)
    
    def search_with_scores(self, query: str, k: int = 5) -> List[tuple]:
        """Search for relevant documents with similarity scores"""
        if self.vector_store is None:
            raise ValueError("Vector store not loaded")
            
        return self.vector_store.similarity_search_with_score(query, k=k)

def main():
    """Main function to process documents and create vector store"""
    processor = DocumentProcessor()
    
    # Check if vector store already exists
    if processor.load_vector_store():
        logger.info("Vector store already exists. Skipping document processing.")
        return
    
    # Load and process documents
    logger.info("Loading documents...")
    documents = processor.load_documents()
    
    if not documents:
        logger.warning("No documents loaded. Please check your sources.")
        return
    
    # Process documents
    logger.info("Processing documents...")
    chunks = processor.process_documents(documents)
    
    # Create vector store
    logger.info("Creating vector store...")
    processor.create_vector_store(chunks)
    
    logger.info("Document processing completed successfully!")

if __name__ == "__main__":
    main()
