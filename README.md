# Climate Assistant RAG System

Um assistente inteligente com RAG (Retrieval-Augmented Generation) + Agentes para questões de meio ambiente e mudanças climáticas, baseado em documentos do IPCC e outras fontes científicas.

## 🌍 Visão Geral

Este projeto foi **completamente refatorado** de um chatbot simples para um sistema avançado de RAG com agentes especializados em mudanças climáticas. O frontend original foi mantido, mas o backend foi completamente reconstruído.

### ✨ Principais Características

- **RAG Avançado**: Recuperação de informações de documentos científicos
- **Agentes LangGraph**: Orquestração inteligente de múltiplos agentes especializados
- **Anti-alucinação**: Sistema de verificação e citações obrigatórias
- **Foco Ambiental**: Especializado em mudanças climáticas e meio ambiente
- **Open Source**: Usando LLMs open-weights (Ollama) e tecnologias gratuitas

## 🚀 Início Rápido

### 1. Configuração Automática (Recomendado)
```bash
cd backend
python setup.py
```

### 2. Processar Documentos
```bash
python document_processor.py
```

### 3. Iniciar Servidor
```bash
python app.py
```

### 4. Usar o Sistema
Abra `http://localhost:5000/static/pln.html` no seu navegador.

## 🏗️ Arquitetura

### Agentes LangGraph
1. **Supervisor**: Roteamento e gerenciamento de consultas
2. **Retriever**: Busca e recuperação de documentos relevantes  
3. **Answerer**: Geração de respostas com citações obrigatórias
4. **Self-check**: Verificação de qualidade e evidências
5. **Safety**: Adição de disclaimers e verificações de segurança

### Stack Tecnológica
- **Frontend**: HTML, CSS, JavaScript (mantido do projeto original)
- **Backend**: Python, Flask, LangChain, LangGraph
- **LLM**: Ollama com modelos open-weights (Llama 3.1, Qwen2.5, etc.)
- **Vector Store**: FAISS/Chroma para armazenamento vetorial
- **Embeddings**: HuggingFace (sentence-transformers)

## 📊 Uso

### Interface Web
O frontend original foi mantido e adaptado. Acesse:
- `http://localhost:5000/static/pln.html`

### API REST
```python
import requests

response = requests.post('http://localhost:5000/get_response', json={
    'messages': [
        {'role': 'user', 'content': 'Quais são as principais evidências do aquecimento global?'}
    ]
})

print(response.json()['response'])
```

### Exemplos de Perguntas
- "Quais são as principais evidências do aquecimento global?"
- "Como o IPCC define mudanças climáticas?"
- "Quais são os impactos das mudanças climáticas na biodiversidade?"
- "Como podemos mitigar as mudanças climáticas?"

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

## 🐳 Docker

### Executar com Docker
```bash
# Construir e executar
make docker-build
make docker-run

# Ou usar docker-compose diretamente
docker-compose up -d
```

## 📁 Estrutura do Projeto

```
tributouro/
├── pln.html              # Frontend original (mantido)
├── styles.css            # Estilos originais (mantido)
├── seta.png              # Imagem original (mantida)
├── tributouro.ipynb      # Notebook original (mantido)
├── README.md             # Esta documentação
└── backend/              # Novo backend RAG + Agentes
    ├── app.py            # API Flask principal
    ├── agents.py         # Agentes LangGraph
    ├── config.py         # Configurações
    ├── document_processor.py # Processamento de documentos
    ├── evaluation.py     # Sistema de avaliação
    ├── setup.py         # Script de instalação
    ├── requirements.txt # Dependências Python
    ├── Dockerfile       # Containerização
    ├── docker-compose.yml
    ├── Makefile         # Comandos úteis
    └── data/            # Dados e documentos
        ├── documents/   # Documentos originais
        ├── vector_store/ # Índices vetoriais
        └── evaluation/  # Resultados de avaliação
```

## 🔧 Comandos Úteis

```bash
# Setup completo
make setup

# Desenvolvimento
make dev

# Processar documentos
make process

# Executar avaliação
make test

# Status do sistema
make status

# Limpar arquivos temporários
make clean
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

## 📚 Documentação Detalhada

Para documentação completa do backend, consulte:
- [Backend README](backend/README.md)

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
- Execute `python document_processor.py` novamente

## 📄 Licença

Este projeto é open-source e está disponível sob a licença MIT.

---

**🌍 Desenvolvido para promover conhecimento sobre mudanças climáticas**

**🔄 Migrado de chatbot simples para sistema RAG + Agentes avançado**
