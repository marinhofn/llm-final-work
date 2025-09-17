#!/usr/bin/env python3
"""
Script principal para iniciar o Climate Assistant RAG System
"""
import sys
import os
import subprocess
from pathlib import Path

def main():
    """Script principal para iniciar o sistema"""
    print("🌍 Climate Assistant RAG System")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not Path("backend").exists():
        print("❌ Diretório 'backend' não encontrado.")
        print("Execute este script a partir do diretório raiz do projeto.")
        sys.exit(1)
    
    # Verificar se o backend está configurado
    backend_dir = Path("backend")
    if not (backend_dir / "requirements.txt").exists():
        print("❌ Backend não está configurado corretamente.")
        sys.exit(1)
    
    print("✅ Estrutura do projeto encontrada")
    
    # Perguntar ao usuário o que fazer
    print("\n📋 Opções disponíveis:")
    print("1. Setup completo (primeira vez)")
    print("2. Processar documentos")
    print("3. Iniciar servidor")
    print("4. Executar avaliação")
    print("5. Migrar frontend")
    print("6. Sair")
    
    choice = input("\nEscolha uma opção (1-6): ").strip()
    
    if choice == "1":
        print("\n🚀 Executando setup completo...")
        os.chdir("backend")
        subprocess.run([sys.executable, "setup.py"])
        
    elif choice == "2":
        print("\n📚 Processando documentos...")
        os.chdir("backend")
        subprocess.run([sys.executable, "document_processor.py"])
        
    elif choice == "3":
        print("\n🌐 Iniciando servidor...")
        os.chdir("backend")
        subprocess.run([sys.executable, "app.py"])
        
    elif choice == "4":
        print("\n📊 Executando avaliação...")
        os.chdir("backend")
        subprocess.run([sys.executable, "evaluation.py"])
        
    elif choice == "5":
        print("\n🔄 Migrando frontend...")
        os.chdir("backend")
        subprocess.run([sys.executable, "migrate_frontend.py"])
        
    elif choice == "6":
        print("\n👋 Até logo!")
        sys.exit(0)
        
    else:
        print("\n❌ Opção inválida.")
        sys.exit(1)

if __name__ == "__main__":
    main()
