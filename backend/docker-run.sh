#!/bin/bash

# Docker Run Script for Climate Assistant RAG System
# This script builds and runs the Docker container

set -e

echo "🌍 Climate Assistant RAG - Docker Setup"
echo "========================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado!"
    echo "💡 Instale Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado!"
    echo "💡 Instale Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker e Docker Compose encontrados"

# Check if PDF exists
if [ ! -f "data/documents/IPCC_AR6_SYR_FullVolume.pdf" ]; then
    echo "❌ PDF não encontrado!"
    echo "💡 Verifique se o arquivo está em data/documents/IPCC_AR6_SYR_FullVolume.pdf"
    exit 1
fi

echo "✅ PDF encontrado"

# Build and run with Docker Compose
echo "🔨 Construindo e executando container..."
echo "⏳ Isso pode levar alguns minutos na primeira execução..."

docker-compose up --build

echo "🎉 Container executado com sucesso!"
echo "🌐 Acesse: http://localhost:5000"
echo "⏹️ Para parar: Ctrl+C ou 'docker-compose down'"
