# ===================================================================
# CLIMATE ASSISTANT - COMANDOS EM ORDEM PARA EXECUÇÃO
# ===================================================================

## 📋 MÉTODO 1: Script Automático (Recomendado)

```bash
# Executar script completo
cd /home/marinhofn/tributouro/tributouro
bash start_system.sh
```

## 📋 MÉTODO 2: Comandos Manuais (Passo a Passo)

### ETAPA 1: Preparação
```bash
# 1. Navegar para o diretório
cd /home/marinhofn/tributouro/tributouro/backend

# 2. Verificar dependências (opcional)
pip install -r requirements.txt
```

### ETAPA 2: Ollama
```bash
# 3. Verificar se Ollama está instalado
ollama --version

# 4. Iniciar Ollama (se não estiver rodando)
ollama serve

# 5. Em outro terminal, baixar modelo (se necessário)
ollama pull llama3.1:8b

# 6. Verificar modelos disponíveis
ollama list
```

### ETAPA 3: Documentos e Vector Store
```bash
# 7. Verificar PDFs na pasta
ls -la data/documents/

# 8. Reconstruir vector store (inclui PDFs + websites)
python process_pdfs.py rebuild

# 9. Testar carregamento de PDFs (opcional)
python process_pdfs.py test
```

### ETAPA 4: Servidor
```bash
# 10. Matar processos anteriores (se existirem)
pkill -f "python main.py app"

# 11. Iniciar servidor na porta 5001
API_PORT=5001 python main.py app
```

### ETAPA 5: Inicialização do Sistema
```bash
# 12. Em outro terminal, forçar inicialização
curl -X POST http://localhost:5001/reload

# 13. Verificar status
curl http://localhost:5001/health
```

## 🧪 COMANDOS DE TESTE

### Testar API
```bash
# Health check
curl http://localhost:5001/health

# Status detalhado
curl http://localhost:5001/status

# Busca direta
curl -X POST http://localhost:5001/search \
  -H "Content-Type: application/json" \
  -d '{"query":"climate change"}'

# Consulta completa
curl -X POST http://localhost:5001/get_response \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Quais são as principais causas das mudanças climáticas?"}]}'
```

### Testar PDFs
```bash
# Verificar PDFs carregados
python process_pdfs.py test

# Buscar no vector store
python process_pdfs.py search

# Processo completo
python process_pdfs.py full
```

## 🔧 COMANDOS DE MANUTENÇÃO

### Reiniciar Sistema
```bash
# Matar servidor
pkill -f "python main.py app"

# Reiniciar
cd /home/marinhofn/tributouro/tributouro/backend
API_PORT=5001 python main.py app

# Forçar reload
curl -X POST http://localhost:5001/reload
```

### Adicionar Novos PDFs
```bash
# 1. Copiar PDF para pasta
cp novo_documento.pdf data/documents/

# 2. Reconstruir vector store
python process_pdfs.py rebuild

# 3. Reiniciar servidor
pkill -f "python main.py app"
API_PORT=5001 python main.py app

# 4. Reload sistema
curl -X POST http://localhost:5001/reload
```

### Debug
```bash
# Ver logs do servidor
# (aparecerão no terminal onde o servidor está rodando)

# Verificar processos
ps aux | grep python

# Verificar portas
lsof -i :5001
lsof -i :11434

# Testar Ollama diretamente
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.1:8b", "prompt": "Hello", "stream": false}'
```

## 🌐 URLs Importantes

- **Frontend**: http://localhost:5001/
- **API Health**: http://localhost:5001/health
- **API Status**: http://localhost:5001/status
- **Ollama**: http://localhost:11434

## ⚠️ Troubleshooting

### Problema: Ollama não responde
```bash
# Matar processos Ollama
pkill ollama

# Reiniciar
ollama serve
```

### Problema: Porta 5001 ocupada
```bash
# Ver o que está usando a porta
lsof -i :5001

# Matar processo específico
kill [PID]

# Ou matar todos os python main.py
pkill -f "python main.py app"
```

### Problema: Sistema não inicializado
```bash
# Forçar reload
curl -X POST http://localhost:5001/reload

# Se não funcionar, reconstruir vector store
python process_pdfs.py rebuild
```

### Problema: PDFs não aparecem
```bash
# Verificar caminho
ls -la data/documents/

# Verificar configuração
python -c "from src.config import DOCUMENTS_DIR; print(DOCUMENTS_DIR)"

# Reconstruir
python process_pdfs.py rebuild
```

## 📝 Ordem Resumida (TL;DR)

```bash
cd /home/marinhofn/tributouro/tributouro/backend
ollama serve &
ollama pull llama3.1:8b
python process_pdfs.py rebuild
API_PORT=5001 python main.py app &
sleep 5
curl -X POST http://localhost:5001/reload
```

Acesse: http://localhost:5001/