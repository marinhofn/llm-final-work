"""
Flask API for the Climate Assistant RAG system
Compatible with the existing frontend
"""
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

from config import API_HOST, API_PORT, DEBUG
from document_processor import DocumentProcessor
from agents import ClimateAssistantAgents

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global variables for the RAG system
document_processor = None
climate_agents = None

def initialize_system():
    """Initialize the RAG system components"""
    global document_processor, climate_agents
    
    try:
        logger.info("Initializing document processor...")
        document_processor = DocumentProcessor()
        
        # Try to load existing vector store
        if not document_processor.load_vector_store():
            logger.warning("Vector store not found. Please run document processing first.")
            return False
        
        logger.info("Initializing climate agents...")
        climate_agents = ClimateAssistantAgents(document_processor)
        
        logger.info("System initialized successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing system: {str(e)}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "system_initialized": climate_agents is not None
    })

@app.route('/get_response', methods=['POST'])
def get_response():
    """
    Main endpoint for chat responses
    Compatible with existing frontend
    """
    try:
        data = request.get_json()
        
        if not data or 'messages' not in data:
            return jsonify({
                "response": "Erro: Formato de dados inválido. Envie uma lista de mensagens.",
                "error": "Invalid data format"
            }), 400
        
        messages = data['messages']
        
        # Extract the last user message
        user_message = None
        for message in reversed(messages):
            if message.get('role') == 'user':
                user_message = message.get('content', '')
                break
        
        if not user_message:
            return jsonify({
                "response": "Não foi possível identificar sua pergunta. Por favor, tente novamente.",
                "error": "No user message found"
            }), 400
        
        # Check if system is initialized
        if not climate_agents:
            return jsonify({
                "response": "Sistema ainda não foi inicializado. Aguarde alguns momentos e tente novamente.",
                "error": "System not initialized"
            }), 503
        
        # Process the query through the agent system
        logger.info(f"Processing query: {user_message[:100]}...")
        result = climate_agents.process_query(user_message)
        
        if result["success"]:
            return jsonify({
                "response": result["response"],
                "response_html": result.get("response_html", result["response"]),
                "metadata": {
                    "citations_count": len(result["citations"]),
                    "retrieved_docs_count": result["retrieved_docs_count"],
                    "citations": result["citations"][:3]  # Limit citations in response
                }
            })
        else:
            return jsonify({
                "response": result["response"],
                "error": "Processing failed"
            }), 500
            
    except Exception as e:
        logger.error(f"Error in get_response: {str(e)}")
        return jsonify({
            "response": "Desculpe, ocorreu um erro interno. Tente novamente em alguns momentos.",
            "error": str(e)
        }), 500

@app.route('/search', methods=['POST'])
def search_documents():
    """Search documents directly (for testing/debugging)"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({"error": "Query parameter required"}), 400
        
        if not document_processor:
            return jsonify({"error": "Document processor not initialized"}), 503
        
        # Search documents
        docs_with_scores = document_processor.search_with_scores(query, k=5)
        
        results = []
        for doc, score in docs_with_scores:
            results.append({
                "content": doc.page_content[:500] + "...",
                "metadata": doc.metadata,
                "score": float(score)
            })
        
        return jsonify({
            "query": query,
            "results": results,
            "count": len(results)
        })
        
    except Exception as e:
        logger.error(f"Error in search: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'])
def system_status():
    """Get system status and statistics"""
    try:
        status = {
            "system_initialized": climate_agents is not None,
            "document_processor_ready": document_processor is not None,
            "vector_store_loaded": document_processor.vector_store is not None if document_processor else False
        }
        
        if document_processor and document_processor.vector_store:
            # Get some basic stats about the vector store
            try:
                # This is a simple way to get document count
                test_docs = document_processor.search_documents("climate change", k=1)
                status["vector_store_working"] = len(test_docs) > 0
            except:
                status["vector_store_working"] = False
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error in status: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/reload', methods=['POST'])
def reload_system():
    """Reload the system (useful for development)"""
    try:
        global document_processor, climate_agents
        
        logger.info("Reloading system...")
        success = initialize_system()
        
        if success:
            return jsonify({"message": "System reloaded successfully"})
        else:
            return jsonify({"error": "Failed to reload system"}), 500
            
    except Exception as e:
        logger.error(f"Error reloading system: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    """Serve the main HTML file"""
    return send_from_directory('static', 'pln.html')

@app.route('/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

if __name__ == "__main__":
    logger.info("Starting Climate Assistant API...")
    
    # Initialize the system
    if initialize_system():
        logger.info(f"Starting server on {API_HOST}:{API_PORT}")
        app.run(host=API_HOST, port=API_PORT, debug=DEBUG)
    else:
        logger.error("Failed to initialize system. Please check your configuration.")
        logger.info("Make sure to:")
        logger.info("1. Run document processing first: python document_processor.py")
        logger.info("2. Have Ollama running with the specified model")
        logger.info("3. Check your configuration in config.py")
