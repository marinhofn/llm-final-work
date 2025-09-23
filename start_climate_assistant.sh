#!/bin/bash

# Script para rodar o Climate Assistant do zero
# Execute com: bash start_climate_assistant.sh

echo "🌍 Climate Assistant - Setup e Inicialização"
echo "=============================================="

# Função para verificar se um comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Função para verificar se um processo está rodando na porta
port_in_use() {
    lsof -i:$1 >/dev/null 2>&1
}

# 1. Verificar Python
echo -e "\n🔍 Verificando Python..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ $PYTHON_VERSION encontrado"
else
    echo "❌ Python 3 não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

# 2. Navegar para o diretório correto
echo -e "\n📁 Navegando para o diretório backend..."
cd "$(dirname "$0")/backend" || exit 1
pwd

# 3. Verificar se requirements.txt existe
if [ ! -f "requirements.txt" ]; then
    echo "❌ Arquivo requirements.txt não encontrado!"
    exit 1
fi

# 4. Instalar dependências (opcional, apenas se não estiverem instaladas)
echo -e "\n📦 Verificando dependências Python..."
if pip show flask langchain >/dev/null 2>&1; then
    echo "✅ Dependências já instaladas"
else
    echo "🔄 Instalando dependências..."
    pip install -r requirements.txt
fi

# 5. Verificar Ollama
echo -e "\n🤖 Verificando Ollama..."
if command_exists ollama; then
    echo "✅ Ollama encontrado"
    
    # Verificar se o serviço está rodando
    if ollama list >/dev/null 2>&1; then
        echo "✅ Serviço Ollama está rodando"
        
        # Verificar se o modelo necessário está instalado
        if ollama list | grep -q "llama3.1:8b"; then
            echo "✅ Modelo llama3.1:8b já instalado"
        else
            echo "📥 Baixando modelo llama3.1:8b (isso pode demorar)..."
            ollama pull llama3.1:8b
        fi
    else
        echo "🚀 Iniciando serviço Ollama..."
        ollama serve &
        sleep 5
        
        echo "📥 Baixando modelo llama3.1:8b..."
        ollama pull llama3.1:8b
    fi
else
    echo "❌ Ollama não encontrado!"
    echo "📋 Para instalar:"
    echo "   1. Visite: https://ollama.ai/"
    echo "   2. Baixe e instale o Ollama"
    echo "   3. Execute este script novamente"
    exit 1
fi

# 6. Verificar se há documentos processados
echo -e "\n📚 Verificando documentos processados..."
if [ -d "data/vector_store" ] && [ "$(ls -A data/vector_store)" ]; then
    echo "✅ Vector store encontrado"
else
    echo "🔄 Processando documentos (primeira execução)..."
    python -m ingest.document_processor
fi

# 7. Verificar se algum servidor já está rodando na porta 5001
echo -e "\n🌐 Verificando porta 5001..."
if port_in_use 5001; then
    echo "⚠️  Porta 5001 já está em uso. Parando processo anterior..."
    pkill -f "python main.py app" || true
    sleep 2
fi

# 8. Iniciar o servidor
echo -e "\n🚀 Iniciando Climate Assistant API na porta 5001..."
echo "📋 Para acessar: http://localhost:5001/"
echo "🛑 Para parar: Ctrl+C"
echo "=================="

API_PORT=5001 python main.py app