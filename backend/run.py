#!/usr/bin/env python3
"""
Main entry point for the Climate Assistant RAG System
"""
import sys
import argparse
import logging
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from document_processor import DocumentProcessor
from agents import ClimateAssistantAgents
from app import app, initialize_system
from config import API_HOST, API_PORT, DEBUG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Climate Assistant RAG System")
    parser.add_argument("command", choices=["setup", "process", "run", "test"], 
                       help="Command to execute")
    parser.add_argument("--host", default=API_HOST, help="API host")
    parser.add_argument("--port", type=int, default=API_PORT, help="API port")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    if args.command == "setup":
        logger.info("Running setup...")
        from setup import main as setup_main
        setup_main()
        
    elif args.command == "process":
        logger.info("Processing documents...")
        processor = DocumentProcessor()
        processor.load_documents()
        chunks = processor.process_documents(processor.load_documents())
        processor.create_vector_store(chunks)
        logger.info("Document processing completed!")
        
    elif args.command == "run":
        logger.info("Starting Climate Assistant API...")
        if initialize_system():
            app.run(host=args.host, port=args.port, debug=args.debug)
        else:
            logger.error("Failed to initialize system")
            sys.exit(1)
            
    elif args.command == "test":
        logger.info("Running evaluation...")
        from evaluation import main as eval_main
        eval_main()

if __name__ == "__main__":
    main()
