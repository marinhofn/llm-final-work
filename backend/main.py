#!/usr/bin/env python3
"""
Main entry point for the Climate Assistant RAG System
"""
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python main.py <command>")
        print("Commands:")
        print("  app          - Start the Flask API server")
        print("  ingest       - Process documents and create vector store")
        print("  eval         - Run evaluation")
        print("  test         - Run tests")
        print("  setup        - Run setup script")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "app":
        from app.app import app
        from src.config import API_HOST, API_PORT, DEBUG
        print(f"Starting Climate Assistant API on {API_HOST}:{API_PORT}")
        app.run(host=API_HOST, port=API_PORT, debug=DEBUG)
    
    elif command == "ingest":
        from ingest.document_processor import main as ingest_main
        ingest_main()
    
    elif command == "eval":
        from eval.evaluation import main as eval_main
        eval_main()
    
    elif command == "test":
        from run_tests import run_tests
        exit_code = run_tests()
        sys.exit(exit_code)
    
    elif command == "setup":
        from setup import main as setup_main
        success = setup_main()
        sys.exit(0 if success else 1)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()
