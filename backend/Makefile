# Makefile for Climate Assistant RAG System

.PHONY: help install setup run test clean docker-build docker-run docker-stop

# Default target
help:
	@echo "Climate Assistant RAG System - Available Commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  install     - Install Python dependencies"
	@echo "  setup       - Complete system setup (recommended for first time)"
	@echo ""
	@echo "Development:"
	@echo "  run         - Start the API server"
	@echo "  process     - Process documents and create vector store"
	@echo "  test        - Run evaluation tests"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with Docker Compose"
	@echo "  docker-stop  - Stop Docker containers"
	@echo ""
	@echo "Utilities:"
	@echo "  clean       - Clean temporary files"
	@echo "  status      - Check system status"

# Installation
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt

setup:
	@echo "Setting up Climate Assistant RAG System..."
	python setup.py

# Development
run:
	@echo "Starting Climate Assistant API server..."
	python app.py

process:
	@echo "Processing documents and creating vector store..."
	python document_processor.py

test:
	@echo "Running evaluation tests..."
	python evaluation.py

# Docker commands
docker-build:
	@echo "Building Docker image..."
	docker build -t climate-assistant .

docker-run:
	@echo "Starting with Docker Compose..."
	docker-compose up -d

docker-stop:
	@echo "Stopping Docker containers..."
	docker-compose down

# Utilities
clean:
	@echo "Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	rm -rf data/vector_store/*
	rm -rf data/evaluation/*

status:
	@echo "Checking system status..."
	@echo "Python version:"
	@python --version
	@echo ""
	@echo "Ollama status:"
	@ollama list || echo "Ollama not found"
	@echo ""
	@echo "Vector store status:"
	@ls -la data/vector_store/ || echo "Vector store not found"
	@echo ""
	@echo "API status:"
	@curl -s http://localhost:5000/health || echo "API not running"

# Quick start for development
dev: install process run

# Production deployment
prod: docker-build docker-run
