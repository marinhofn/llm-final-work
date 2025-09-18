"""
Configuration settings for the RAG + Agents system
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"
EVALUATION_DIR = DATA_DIR / "evaluation"

# Create directories if they don't exist
for directory in [DATA_DIR, DOCUMENTS_DIR, VECTOR_STORE_DIR, EVALUATION_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# LLM Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1:8b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Vector Store Configuration
VECTOR_STORE_TYPE = os.getenv("VECTOR_STORE_TYPE", "faiss")  # faiss or chroma
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# API Configuration
API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = int(os.getenv("API_PORT", "5000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Document Sources (IPCC AR6 and other environmental documents)
DOCUMENT_SOURCES = [
    {
        "name": "IPCC AR6 Synthesis Report",
        "url": "https://www.ipcc.ch/report/ar6/syr/",
        "type": "website"
    },
    {
        "name": "IPCC AR6 WG1 Report",
        "url": "https://www.ipcc.ch/report/ar6/wg1/",
        "type": "website"
    },
    {
        "name": "IPCC AR6 WG2 Report", 
        "url": "https://www.ipcc.ch/report/ar6/wg2/",
        "type": "website"
    },
    {
        "name": "IPCC AR6 WG3 Report",
        "url": "https://www.ipcc.ch/report/ar6/wg3/",
        "type": "website"
    }
]

# Agent Configuration
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "10"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))

# Safety and Policy
SAFETY_DISCLAIMER = """
⚠️ **AVISO IMPORTANTE**: Este assistente fornece informações baseadas em documentos científicos e oficiais sobre mudanças climáticas. 
As informações são apenas para fins educacionais e informativos. Para decisões importantes relacionadas a políticas, 
saúde ou segurança, consulte sempre especialistas qualificados e fontes oficiais atualizadas.
"""

# Evaluation Configuration
EVALUATION_QUESTIONS = [
    "Quais são as principais evidências do aquecimento global?",
    "Como o IPCC define mudanças climáticas?",
    "Quais são os impactos das mudanças climáticas na biodiversidade?",
    "Como podemos mitigar as mudanças climáticas?",
    "Quais são os cenários de emissões do IPCC?",
    "Como as mudanças climáticas afetam os oceanos?",
    "Quais são os riscos climáticos para a humanidade?",
    "Como adaptar-se às mudanças climáticas?",
    "Quais são as principais fontes de gases de efeito estufa?",
    "Como o IPCC avalia a confiança nas projeções climáticas?"
]
