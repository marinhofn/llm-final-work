"""
Setup script for the Climate Assistant RAG system
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_ollama():
    """Check if Ollama is installed and running"""
    print("\n🔍 Checking Ollama installation...")
    
    # Check if ollama command exists
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed")
            print(f"Version: {result.stdout.strip()}")
        else:
            print("❌ Ollama is not installed or not in PATH")
            return False
    except FileNotFoundError:
        print("❌ Ollama is not installed or not in PATH")
        return False
    
    # Check if Ollama service is running
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama service is running")
            models = result.stdout.strip()
            if models:
                print(f"Available models:\n{models}")
            else:
                print("⚠️  No models installed")
            return True
        else:
            print("❌ Ollama service is not running")
            return False
    except Exception as e:
        print(f"❌ Error checking Ollama service: {e}")
        return False

def install_ollama_model(model_name="llama3.1:8b"):
    """Install Ollama model if not present"""
    print(f"\n🔄 Installing Ollama model: {model_name}...")
    
    try:
        # Check if model is already installed
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if model_name in result.stdout:
            print(f"✅ Model {model_name} is already installed")
            return True
        
        # Install the model
        print(f"📥 Downloading {model_name} (this may take a while)...")
        result = subprocess.run(["ollama", "pull", model_name], check=True)
        print(f"✅ Model {model_name} installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing model {model_name}: {e}")
        return False

def setup_environment():
    """Set up the environment and dependencies"""
    print("🚀 Setting up Climate Assistant RAG System...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} detected")
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    # Check Ollama
    if not check_ollama():
        print("\n📋 Ollama Setup Instructions:")
        print("1. Install Ollama from: https://ollama.ai/")
        print("2. Start Ollama service")
        print("3. Run this setup script again")
        return False
    
    # Install required Ollama model
    model_name = os.getenv("LLM_MODEL", "llama3.1:8b")
    if not install_ollama_model(model_name):
        print(f"⚠️  Could not install model {model_name}")
        print("You can install it manually with: ollama pull llama3.1:8b")
    
    return True

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        "data",
        "data/documents", 
        "data/vector_store",
        "data/evaluation"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def main():
    """Main setup function"""
    print("🌍 Climate Assistant RAG System Setup")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Setup environment
    if not setup_environment():
        print("\n❌ Setup failed. Please check the errors above.")
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run document processing: python -m ingest.document_processor")
    print("2. Start the API server: python -m app.app")
    print("3. Open the frontend: pln.html")
    print("\n📚 For evaluation: python -m eval.evaluation")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
