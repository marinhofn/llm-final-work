#!/usr/bin/env python3
"""
Climate Assistant - Verificação Rápida do Sistema
Executa diagnósticos e mostra o status atual
"""
import subprocess
import requests
import os
from pathlib import Path
import json

def run_command(cmd, description):
    """Execute command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)

def check_url(url, timeout=5):
    """Check if URL is accessible"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200, response.status_code
    except Exception as e:
        return False, str(e)

def main():
    print("🔍 CLIMATE ASSISTANT - DIAGNÓSTICO DO SISTEMA")
    print("=" * 50)
    
    # Current directory
    current_dir = Path.cwd()
    print(f"📁 Diretório atual: {current_dir}")
    
    # Change to backend if needed
    backend_dir = Path("/home/marinhofn/tributouro/tributouro/backend")
    if current_dir != backend_dir:
        try:
            os.chdir(backend_dir)
            print(f"📂 Mudando para: {backend_dir}")
        except Exception as e:
            print(f"❌ Erro ao mudar diretório: {e}")
            return
    
    print("\n1️⃣ VERIFICAÇÃO DE DEPENDÊNCIAS")
    print("-" * 30)
    
    # Python
    success, output, error = run_command("python3 --version", "Python")
    if success:
        print(f"✅ Python: {output.strip()}")
    else:
        print(f"❌ Python não encontrado")
    
    # Ollama
    success, output, error = run_command("ollama --version", "Ollama")
    if success:
        print(f"✅ Ollama: {output.strip()}")
    else:
        print(f"❌ Ollama não encontrado")
    
    # Flask/LangChain
    success, output, error = run_command("python3 -c 'import flask, langchain; print(\"OK\")'", "Dependências Python")
    if success:
        print("✅ Dependências Python: OK")
    else:
        print("❌ Dependências Python: Faltando")
        print("   Execute: pip install -r requirements.txt")
    
    print("\n2️⃣ VERIFICAÇÃO DO OLLAMA")
    print("-" * 25)
    
    # Ollama service
    success, output, error = run_command("ollama list", "Ollama Service")
    if success:
        print("✅ Ollama rodando")
        if "llama3.1:8b" in output:
            print("✅ Modelo llama3.1:8b disponível")
        else:
            print("⚠️ Modelo llama3.1:8b não encontrado")
            print("   Execute: ollama pull llama3.1:8b")
    else:
        print("❌ Ollama não está rodando")
        print("   Execute: ollama serve")
    
    # Ollama API
    success, status = check_url("http://localhost:11434", timeout=3)
    if success:
        print("✅ Ollama API acessível")
    else:
        print(f"❌ Ollama API não acessível: {status}")
    
    print("\n3️⃣ VERIFICAÇÃO DE DOCUMENTOS")
    print("-" * 28)
    
    # PDFs
    try:
        from src.config import DOCUMENTS_DIR
        pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))
        print(f"📄 PDFs encontrados: {len(pdf_files)}")
        for pdf in pdf_files:
            size_mb = pdf.stat().st_size / (1024*1024)
            print(f"   - {pdf.name} ({size_mb:.1f} MB)")
    except Exception as e:
        print(f"❌ Erro ao verificar PDFs: {e}")
    
    # Vector store
    try:
        from src.config import VECTOR_STORE_DIR
        faiss_index = VECTOR_STORE_DIR / "faiss_index"
        if faiss_index.exists():
            index_file = faiss_index / "index.faiss"
            if index_file.exists():
                size_mb = index_file.stat().st_size / (1024*1024)
                print(f"✅ Vector store: {size_mb:.1f} MB")
            else:
                print("❌ Vector store incompleto")
        else:
            print("❌ Vector store não encontrado")
            print("   Execute: python process_pdfs.py rebuild")
    except Exception as e:
        print(f"❌ Erro ao verificar vector store: {e}")
    
    print("\n4️⃣ VERIFICAÇÃO DA API")
    print("-" * 21)
    
    # Flask server
    success, status = check_url("http://localhost:5001/health", timeout=3)
    if success:
        print("✅ Servidor Flask rodando")
        
        # Health check
        try:
            response = requests.get("http://localhost:5001/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("system_initialized"):
                    print("✅ Sistema inicializado")
                else:
                    print("⚠️ Sistema não inicializado")
                    print("   Execute: curl -X POST http://localhost:5001/reload")
            else:
                print(f"⚠️ Health check falhou: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro no health check: {e}")
    else:
        print(f"❌ Servidor Flask não acessível: {status}")
        print("   Execute: API_PORT=5001 python main.py app")
    
    # Processes
    success, output, error = run_command("ps aux | grep 'python main.py app' | grep -v grep", "Processo Flask")
    if success and output.strip():
        print("✅ Processo Flask ativo")
    else:
        print("❌ Processo Flask não encontrado")
    
    success, output, error = run_command("ps aux | grep 'ollama serve' | grep -v grep", "Processo Ollama")
    if success and output.strip():
        print("✅ Processo Ollama ativo")
    else:
        print("⚠️ Processo Ollama não encontrado explicitamente")
    
    print("\n5️⃣ COMANDOS SUGERIDOS")
    print("-" * 22)
    
    print("🚀 Para iniciar o sistema:")
    print("   cd /home/marinhofn/tributouro/tributouro")
    print("   bash start_system.sh")
    print()
    print("🔄 Para reiniciar apenas o servidor:")
    print("   pkill -f 'python main.py app'")
    print("   cd /home/marinhofn/tributouro/tributouro/backend")
    print("   API_PORT=5001 python main.py app")
    print()
    print("🔧 Para forçar inicialização:")
    print("   curl -X POST http://localhost:5001/reload")
    print()
    print("📚 Para reconstruir documentos:")
    print("   python process_pdfs.py rebuild")

if __name__ == "__main__":
    main()