#!/usr/bin/env python3
"""
Verificador de dependências para coleta de métricas RAGAS
"""
import subprocess
import sys

def install_package(package):
    """Install a package using pip"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def check_and_install_dependencies():
    """Check and install required dependencies"""
    dependencies = {
        "ragas": "ragas",
        "datasets": "datasets", 
        "numpy": "numpy",
        "pandas": "pandas",
        "matplotlib": "matplotlib",
        "seaborn": "seaborn"
    }
    
    missing = []
    
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {module} já instalado")
        except ImportError:
            print(f"❌ {module} não encontrado")
            missing.append(package)
    
    if missing:
        print(f"\n📦 Instalando dependências faltantes: {', '.join(missing)}")
        for package in missing:
            try:
                install_package(package)
                print(f"✅ {package} instalado com sucesso")
            except Exception as e:
                print(f"❌ Erro ao instalar {package}: {e}")
                return False
    
    return True

if __name__ == "__main__":
    print("🔍 Verificando dependências para métricas RAGAS...")
    if check_and_install_dependencies():
        print("\n🎉 Todas as dependências estão disponíveis!")
        print("Execute: python collect_metrics.py")
    else:
        print("\n❌ Falha na instalação de dependências")