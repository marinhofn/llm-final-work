# Climate Assistant RAG System

Um assistente inteligente com RAG (Retrieval-Augmented Generation) + Agentes para questões de meio ambiente e mudanças climáticas, baseado em documentos do IPCC e outras fontes científicas.

## 🌍 Visão Geral

Este sistema implementa uma prova de conceito (PoC) de um assistente com:
- **RAG**: Recuperação de informações de documentos científicos
- **Agentes LangGraph**: Orquestração inteligente de múltiplos agentes especializados
- **Anti-alucinação**: Sistema de verificação e citações obrigatórias
- **Foco Ambiental**: Especializado em mudanças climáticas e meio ambiente

## 🏗️ Arquitetura

### Agentes LangGraph
1. **Supervisor**: Roteamento e gerenciamento de consultas
2. **Retriever**: Busca e recuperação de documentos relevantes
3. **Answerer**: Geração de respostas com citações obrigatórias
4. **Self-check**: Verificação de qualidade e evidências
5. **Safety**: Adição de disclaimers e verificações de segurança

### Stack Tecnológica
- **Python 3.8+**
- **LangChain + LangGraph**: Orquestração de agentes
- **Ollama**: LLM open-weights (Llama 3.1 8B, Qwen2.5 7B, etc.)
- **FAISS/Chroma**: Armazenamento vetorial
- **HuggingFace Embeddings**: Embeddings de texto
- **Flask**: API REST compatível com frontend existente

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.8 ou superior
- Ollama instalado e configurado
- 8GB+ RAM recomendado

### 1. Instalação Automática
```bash
cd backend
python setup.py
```

### 2. Instalação Manual

#### Instalar dependências Python:
```bash
pip install -r requirements.txt
```

#### Instalar e configurar Ollama:
```bash
# Instalar Ollama (https://ollama.ai/)
# Baixar modelo LLM
ollama pull llama3.1:8b
# ou
ollama pull qwen2.5:7b
```

#### Processar documentos:
```bash
python document_processor.py
```

#### Iniciar servidor:
```bash
python app.py
```

## 📊 Uso

### API Endpoints

#### `/get_response` (POST)
Endpoint principal para chat, compatível com frontend existente.

**Request:**
```json
{
  "messages": [
    {"role": "user", "content": "Quais são as principais evidências do aquecimento global?"}
  ]
}
```

**Response:**
```json
{
  "response": "Resposta com citações...",
  "metadata": {
    "citations_count": 3,
    "retrieved_docs_count": 5,
    "citations": [...]
  }
}
```

#### `/search` (POST)
Busca direta em documentos.

#### `/status` (GET)
Status do sistema.

#### `/health` (GET)
Health check.

### Exemplo de Uso
```python
import requests

# Fazer pergunta sobre mudanças climáticas
response = requests.post('http://localhost:5000/get_response', json={
    'messages': [
        {'role': 'user', 'content': 'Como o IPCC define mudanças climáticas?'}
    ]
})

print(response.json()['response'])
```

## 📈 Avaliação

### Executar Avaliação Completa
```bash
python evaluation.py
```

### Métricas Implementadas
- **RAGAS**: Faithfulness, Answer Relevancy, Context Precision/Recall
- **Latência**: Tempo médio de resposta
- **Citações**: Qualidade e presença de citações
- **Anti-alucinação**: Verificação de evidências

### Dataset de Avaliação
- 20+ perguntas sobre mudanças climáticas
- Respostas rotuladas manualmente
- Métricas automáticas de qualidade

## 🔧 Configuração

### Variáveis de Ambiente
```bash
# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.1:8b
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Vector Store
VECTOR_STORE_TYPE=faiss  # ou chroma
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# API
API_HOST=localhost
API_PORT=5000
DEBUG=False
```

### Fontes de Documentos
O sistema indexa automaticamente:
- Relatórios do IPCC AR6
- Documentos científicos sobre clima
- Bases de dados ambientais abertas

## 🏛️ Estrutura do Projeto

```
backend/
├── app.py                 # API Flask principal
├── agents.py             # Agentes LangGraph
├── config.py             # Configurações
├── document_processor.py # Processamento de documentos
├── evaluation.py         # Sistema de avaliação
├── setup.py             # Script de instalação
├── requirements.txt     # Dependências Python
├── README.md           # Esta documentação
├── data/               # Dados e documentos
│   ├── documents/      # Documentos originais
│   ├── vector_store/   # Índices vetoriais
│   └── evaluation/     # Resultados de avaliação
└── Dockerfile         # Containerização
```

## 🔒 Ética e Segurança

### Disclaimers Automáticos
- Informações apenas para fins educacionais
- Recomendação de consultar especialistas
- Aviso sobre limitações dos dados

### Limitações
- Não fornece diagnóstico médico
- Não oferece assessoria legal
- Sempre informativo, nunca prescritivo

## 🐳 Docker

### Construir e Executar
```bash
# Construir imagem
docker build -t climate-assistant .

# Executar container
docker run -p 5000:5000 climate-assistant
```

## 📊 Métricas de Performance

### Benchmarks Esperados
- **Latência**: < 5s por consulta
- **Faithfulness**: > 0.8
- **Answer Relevancy**: > 0.7
- **Context Precision**: > 0.6
- **Citações**: > 80% das respostas

### Monitoramento
- Logs detalhados de cada agente
- Métricas de latência por componente
- Qualidade das citações

## 🤝 Contribuição

### Desenvolvimento
1. Fork o repositório
2. Crie uma branch para sua feature
3. Implemente testes
4. Execute avaliação completa
5. Submeta pull request

### Melhorias Futuras
- [ ] Suporte a mais idiomas
- [ ] Integração com mais fontes de dados
- [ ] Interface web melhorada
- [ ] Métricas em tempo real
- [ ] Cache inteligente

## 📄 Licença

Este projeto é open-source e está disponível sob a licença MIT.

## 🆘 Suporte

### Problemas Comuns

#### Ollama não responde
```bash
# Verificar se está rodando
ollama list

# Reiniciar serviço
ollama serve
```

#### Erro de memória
- Reduza o tamanho do modelo LLM
- Use chunk_size menor
- Aumente RAM disponível

#### Documentos não carregam
- Verifique conexão com internet
- Confirme URLs das fontes
- Execute document_processor.py novamente

### Logs
```bash
# Ver logs detalhados
tail -f logs/climate_assistant.log
```

## 📚 Referências

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Ollama Documentation](https://ollama.ai/docs)
- [IPCC Reports](https://www.ipcc.ch/reports/)
- [RAGAS Evaluation](https://github.com/explodinggradients/ragas)

---

**Desenvolvido com ❤️ para promover conhecimento sobre mudanças climáticas**
