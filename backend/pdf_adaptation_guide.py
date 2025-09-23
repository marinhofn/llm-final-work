#!/usr/bin/env python3
"""
Documentação da Adaptação para PDFs Locais
Climate Assistant - Suporte a PDFs na pasta data/documents/
"""

print("""
🌍 CLIMATE ASSISTANT - ADAPTAÇÃO PARA PDFs LOCAIS
=================================================

✅ MODIFICAÇÕES IMPLEMENTADAS:

1. 📁 Correção do caminho de documentos:
   - Corrigido DOCUMENTS_DIR em src/config.py
   - Agora aponta para: backend/data/documents/

2. 🔧 Novo método _load_local_pdfs():
   - Escaneia automaticamente a pasta data/documents/
   - Carrega todos os arquivos *.pdf encontrados
   - Preserva informações de página e metadados

3. 📊 Metadados aprimorados para PDFs:
   - source: Nome do arquivo sem extensão
   - type: 'local_pdf'
   - page_number: Número da página (1-indexado)
   - file_path: Caminho completo do arquivo
   - file_name: Nome do arquivo original

4. 🔄 Vector store reconstruído:
   - Inclui documentos de websites (4 documentos)
   - Inclui PDFs locais (186 páginas do IPCC AR6 SYR)
   - Total: 902 chunks indexados

📋 COMO USAR:

1. Adicione PDFs na pasta:
   backend/data/documents/

2. Execute o reprocessamento:
   cd backend && python process_pdfs.py rebuild

3. Reinicie o servidor:
   pkill -f "python main.py app"
   API_PORT=5001 python main.py app

4. Force o reload do sistema:
   curl -X POST http://localhost:5001/reload

📊 STATUS ATUAL:
""")

# Verificar arquivos PDF
from pathlib import Path
import sys
import os

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

try:
    from src.config import DOCUMENTS_DIR, VECTOR_STORE_DIR
    
    # Check PDFs
    pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))
    print(f"📄 PDFs encontrados: {len(pdf_files)}")
    for pdf in pdf_files:
        size_mb = pdf.stat().st_size / (1024*1024)
        print(f"   - {pdf.name} ({size_mb:.1f} MB)")
    
    # Check vector store
    faiss_index = VECTOR_STORE_DIR / "faiss_index"
    if faiss_index.exists():
        index_file = faiss_index / "index.faiss"
        pkl_file = faiss_index / "index.pkl"
        if index_file.exists() and pkl_file.exists():
            index_size = index_file.stat().st_size / (1024*1024)
            pkl_size = pkl_file.stat().st_size / (1024*1024)
            print(f"✅ Vector store: {index_size:.1f} MB + {pkl_size:.1f} MB")
        else:
            print("❌ Vector store incompleto")
    else:
        print("❌ Vector store não encontrado")
        
except Exception as e:
    print(f"❌ Erro ao verificar status: {e}")

print("""
🧪 TESTES DISPONÍVEIS:

# Testar carregamento de PDFs
python process_pdfs.py test

# Reconstruir vector store
python process_pdfs.py rebuild

# Testar busca
python process_pdfs.py search

# Processo completo
python process_pdfs.py full

🔍 VERIFICAÇÃO DA API:

# Health check
curl http://localhost:5001/health

# Reload sistema
curl -X POST http://localhost:5001/reload

# Busca direta
curl -X POST http://localhost:5001/search \\
  -H "Content-Type: application/json" \\
  -d '{"query":"Synthesis Report"}'

# Consulta completa
curl -X POST http://localhost:5001/get_response \\
  -H "Content-Type: application/json" \\
  -d '{"messages":[{"role":"user","content":"IPCC AR6 principais conclusões"}]}'

📚 EXEMPLOS DE PDFs SUPORTADOS:
- Relatórios IPCC
- Documentos científicos sobre clima
- Papers acadêmicos
- Relatórios governamentais

⚠️ LIMITAÇÕES:
- PDFs devem estar em texto (não imagens escaneadas)
- Tamanho recomendado: até 50MB por PDF
- Formatos suportados: PDF padrão

🎯 PRÓXIMOS PASSOS:
1. Adicionar mais PDFs na pasta data/documents/
2. Executar rebuild quando necessário
3. Testar consultas específicas aos PDFs
4. Monitorar performance com mais documentos

""")