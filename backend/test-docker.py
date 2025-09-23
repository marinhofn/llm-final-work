#!/usr/bin/env python3
"""
Test script to verify Docker setup
"""
import requests
import time
import sys

def test_docker_setup():
    """Test if Docker container is working"""
    print("🐳 Testando configuração Docker...")
    
    base_url = "http://localhost:5000"
    
    # Test health endpoint
    print("🔍 Testando health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check OK")
            data = response.json()
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Sistema inicializado: {data.get('system_initialized', False)}")
        else:
            print(f"❌ Health check falhou: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    
    # Test status endpoint
    print("🔍 Testando status...")
    try:
        response = requests.get(f"{base_url}/status", timeout=10)
        if response.status_code == 200:
            print("✅ Status OK")
            data = response.json()
            print(f"   Sistema inicializado: {data.get('system_initialized', False)}")
            print(f"   Document processor: {data.get('document_processor_ready', False)}")
            print(f"   Vector store: {data.get('vector_store_loaded', False)}")
        else:
            print(f"❌ Status falhou: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    
    # Test chat endpoint
    print("🔍 Testando chat...")
    try:
        test_message = {
            "messages": [
                {"role": "user", "content": "Olá, como você está?"}
            ]
        }
        
        response = requests.post(
            f"{base_url}/get_response",
            json=test_message,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Chat OK")
            data = response.json()
            print(f"   Resposta recebida: {len(data.get('response', ''))} caracteres")
            if 'metadata' in data:
                print(f"   Citações: {data['metadata'].get('citations_count', 0)}")
        else:
            print(f"❌ Chat falhou: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    
    print("🎉 Todos os testes passaram!")
    return True

def wait_for_container(max_wait=300):
    """Wait for container to be ready"""
    print(f"⏳ Aguardando container ficar pronto (máximo {max_wait}s)...")
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            response = requests.get("http://localhost:5000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Container está pronto!")
                return True
        except:
            pass
        
        print(".", end="", flush=True)
        time.sleep(5)
    
    print("\n❌ Timeout aguardando container")
    return False

def main():
    """Main test function"""
    print("🧪 Docker Test Suite")
    print("=" * 40)
    
    # Wait for container
    if not wait_for_container():
        print("❌ Container não ficou pronto a tempo")
        print("💡 Verifique os logs: docker-compose logs")
        sys.exit(1)
    
    # Run tests
    if test_docker_setup():
        print("\n🎉 Docker está funcionando perfeitamente!")
        print("🌐 Acesse: http://localhost:5000")
        sys.exit(0)
    else:
        print("\n❌ Docker não está funcionando corretamente")
        print("💡 Verifique os logs: docker-compose logs")
        sys.exit(1)

if __name__ == "__main__":
    main()
