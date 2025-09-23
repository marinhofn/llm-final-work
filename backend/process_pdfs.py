#!/usr/bin/env python3
"""
Test script to process local PDFs and rebuild the vector store
"""
import sys
import os
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from ingest.document_processor import DocumentProcessor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pdf_loading():
    """Test loading local PDFs"""
    processor = DocumentProcessor()
    
    logger.info("Testing local PDF loading...")
    local_docs = processor._load_local_pdfs()
    
    logger.info(f"Found {len(local_docs)} documents from local PDFs")
    
    if local_docs:
        # Show sample of what was loaded
        sample_doc = local_docs[0]
        logger.info(f"Sample document metadata: {sample_doc.metadata}")
        logger.info(f"Sample content (first 200 chars): {sample_doc.page_content[:200]}...")
    
    return local_docs

def rebuild_vector_store():
    """Rebuild vector store with local PDFs included"""
    processor = DocumentProcessor()
    
    logger.info("=== REBUILDING VECTOR STORE WITH LOCAL PDFs ===")
    
    # Load all documents (websites + local PDFs)
    logger.info("Loading all documents...")
    documents = processor.load_documents()
    
    if not documents:
        logger.warning("No documents loaded. Please check your sources.")
        return False
    
    logger.info(f"Total documents loaded: {len(documents)}")
    
    # Show breakdown by source type
    source_counts = {}
    for doc in documents:
        doc_type = doc.metadata.get('type', 'unknown')
        source_counts[doc_type] = source_counts.get(doc_type, 0) + 1
    
    logger.info("Documents by type:")
    for doc_type, count in source_counts.items():
        logger.info(f"  {doc_type}: {count} documents")
    
    # Process documents
    logger.info("Processing documents...")
    chunks = processor.process_documents(documents)
    
    logger.info(f"Created {len(chunks)} chunks")
    
    # Create new vector store
    logger.info("Creating vector store...")
    processor.create_vector_store(chunks)
    
    logger.info("✅ Vector store rebuilt successfully with local PDFs!")
    return True

def test_search():
    """Test searching in the new vector store"""
    processor = DocumentProcessor()
    
    if not processor.load_vector_store():
        logger.error("Could not load vector store")
        return
    
    logger.info("=== TESTING SEARCH ===")
    
    # Test queries
    queries = [
        "climate change",
        "global warming",
        "IPCC",
        "greenhouse gases"
    ]
    
    for query in queries:
        logger.info(f"\nSearching for: '{query}'")
        docs = processor.search_documents(query, k=3)
        
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('source', 'Unknown')
            doc_type = doc.metadata.get('type', 'unknown')
            page = doc.metadata.get('page_number', 'N/A')
            logger.info(f"  {i}. {source} ({doc_type}) - Page {page}")
            logger.info(f"     Content: {doc.page_content[:100]}...")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            test_pdf_loading()
        elif command == "rebuild":
            rebuild_vector_store()
        elif command == "search":
            test_search()
        elif command == "full":
            # Full process: test, rebuild, search
            test_pdf_loading()
            rebuild_vector_store()
            test_search()
        else:
            print("Usage: python process_pdfs.py [test|rebuild|search|full]")
    else:
        print("Usage: python process_pdfs.py [test|rebuild|search|full]")
        print("  test    - Test loading local PDFs")
        print("  rebuild - Rebuild vector store with PDFs")
        print("  search  - Test search functionality")
        print("  full    - Run all steps")