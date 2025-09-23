#!/bin/bash

# =============================================================================
# CLIMATE ASSISTANT - GUIA DE EXECUÇÃO COMPLETO
# Comandos em ordem para executar o sistema corretamente
# =============================================================================

echo "🌍 CLIMATE ASSISTANT - GUIA DE EXECUÇÃO"
echo "========================================"

# Função para verificar se um comando foi executado com sucesso
check_status() {
    if [ $? -eq 0 ]; then
        echo "✅ $1"
    else
        echo "❌ $1 - FALHOU!"
        exit 1
    fi
}

# Função para verificar se um processo está rodando na porta
port_in_use() {
    lsof -i:$1 >/dev/null 2>&1
}

echo ""
echo "📋 ETAPA 1: PREPARAÇÃO DO AMBIENTE"
echo "----------------------------------"

echo "1.1 Navegando para o diretório correto..."
cd /home/marinhofn/tributouro/tributouro/backend
check_status "Navegação para diretório backend"

echo "1.2 Verificando dependências Python..."
if python3 -c "import flask, langchain" >/dev/null 2>&1; then
    echo "✅ Dependências básicas instaladas"
else
    echo "🔄 Instalando dependências..."
    pip install -r requirements.txt
    check_status "Instalação de dependências"
fi

echo ""
echo "📋 ETAPA 2: VERIFICAÇÃO DO OLLAMA"
echo "---------------------------------"

echo "2.1 Verificando se Ollama está instalado..."
if command -v ollama >/dev/null 2>&1; then
    echo "✅ Ollama está instalado"
else
    echo "❌ Ollama não encontrado!"
    echo "   Instale em: https://ollama.ai/"
    exit 1
fi

echo "2.2 Verificando se Ollama está rodando..."
if ollama list >/dev/null 2>&1; then
    echo "✅ Ollama está rodando"
else
    echo "🚀 Iniciando Ollama..."
    echo "   Execute em outro terminal: ollama serve"
    echo "   Aguardando 5 segundos..."
    sleep 5
fi

echo "2.3 Verificando modelo llama3.1:8b..."
if ollama list | grep -q "llama3.1:8b"; then
    echo "✅ Modelo llama3.1:8b disponível"
else
    echo "📥 Baixando modelo llama3.1:8b..."
    ollama pull llama3.1:8b
    check_status "Download do modelo"
fi

echo ""
echo "📋 ETAPA 3: PROCESSAMENTO DE DOCUMENTOS"
echo "---------------------------------------"

echo "3.1 Verificando vector store existente..."
if [ -f "data/vector_store/faiss_index/index.faiss" ]; then
    echo "✅ Vector store encontrado"
    echo "   Deseja reconstruir? (s/N)"
    read -r rebuild
    if [[ $rebuild =~ ^[Ss]$ ]]; then
        echo "🔄 Reconstruindo vector store com PDFs..."
        python process_pdfs.py rebuild
        check_status "Reconstrução do vector store"
    fi
else
    echo "🔄 Criando vector store inicial..."
    python process_pdfs.py rebuild
    check_status "Criação do vector store"
fi

echo "3.2 Testando carregamento de PDFs..."
python process_pdfs.py test
check_status "Teste de carregamento de PDFs"

echo ""
echo "📋 ETAPA 4: INICIALIZAÇÃO DO SERVIDOR"
echo "-------------------------------------"

echo "4.1 Verificando se porta 5001 está livre..."
if port_in_use 5001; then
    echo "⚠️ Porta 5001 em uso, matando processo anterior..."
    pkill -f "python main.py app" || true
    sleep 2
fi

echo "4.2 Iniciando servidor Flask..."
echo "   Servidor será iniciado na porta 5001"
echo "   Para parar: Ctrl+C"
echo "   URL do frontend: http://localhost:5001/"
echo ""

# Iniciar servidor
API_PORT=5001 python main.py app