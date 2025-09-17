"""
LangGraph agents for the RAG system
"""
import json
import logging
import markdown
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from langchain_ollama import ChatOllama
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages

from config import OLLAMA_BASE_URL, LLM_MODEL, TEMPERATURE, SAFETY_DISCLAIMER
from document_processor import DocumentProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """State for the agent system"""
    messages: Annotated[List[BaseMessage], add_messages]
    query: str
    retrieved_docs: List[Dict[str, Any]]
    answer: str
    citations: List[Dict[str, Any]]
    safety_check_passed: bool
    self_check_passed: bool
    final_response: str
    iteration_count: int

class ClimateAssistantAgents:
    """Main class containing all agents for the climate assistant"""
    
    def __init__(self, document_processor: DocumentProcessor):
        self.llm = ChatOllama(
            model=LLM_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=TEMPERATURE
        )
        self.document_processor = document_processor
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("supervisor", self.supervisor_agent)
        workflow.add_node("retriever", self.retriever_agent)
        workflow.add_node("answerer", self.answerer_agent)
        workflow.add_node("self_check", self.self_check_agent)
        workflow.add_node("safety", self.safety_agent)
        workflow.add_node("finalizer", self.finalizer_agent)
        
        # Define the flow
        workflow.set_entry_point("supervisor")
        
        workflow.add_edge("supervisor", "retriever")
        workflow.add_edge("retriever", "answerer")
        workflow.add_edge("answerer", "self_check")
        
        # Conditional edges from self_check
        workflow.add_conditional_edges(
            "self_check",
            self._should_continue_after_self_check,
            {
                "continue": "safety",
                "retry": "retriever",
                "end": END
            }
        )
        
        workflow.add_edge("safety", "finalizer")
        workflow.add_edge("finalizer", END)
        
        return workflow.compile()
    
    def supervisor_agent(self, state: AgentState) -> AgentState:
        """Supervisor agent that routes and manages the conversation"""
        query = state["query"]
        
        supervisor_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""
            Você é um supervisor especializado em mudanças climáticas e meio ambiente.
            Sua função é analisar a consulta do usuário e determinar se ela está relacionada a:
            1. Mudanças climáticas e meio ambiente
            2. Documentos do IPCC
            3. Políticas ambientais
            4. Ciência climática
            
            Se a consulta NÃO estiver relacionada a esses tópicos, responda educadamente
            que você é especializado apenas em questões ambientais e climáticas.
            
            Se a consulta for relevante, prossiga com a busca de informações.
            """),
            HumanMessage(content=f"Consulta do usuário: {query}")
        ])
        
        response = self.llm.invoke(supervisor_prompt.format_messages())
        
        # Check if query is relevant
        if "não está relacionada" in response.content.lower() or "não posso ajudar" in response.content.lower():
            state["final_response"] = response.content
            return state
        
        state["messages"] = [response]
        return state
    
    def retriever_agent(self, state: AgentState) -> AgentState:
        """Retriever agent that searches for relevant documents"""
        query = state["query"]
        
        try:
            # Search for relevant documents
            docs_with_scores = self.document_processor.search_with_scores(query, k=5)
            
            retrieved_docs = []
            for doc, score in docs_with_scores:
                retrieved_docs.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                })
            
            state["retrieved_docs"] = retrieved_docs
            
            retriever_prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content="""
                Você é um agente de recuperação de informações especializado em documentos climáticos.
                Analise os documentos recuperados e determine se eles contêm informações relevantes
                para responder à consulta do usuário.
                
                Se os documentos não forem relevantes ou suficientes, indique que precisa de mais informações.
                """),
                HumanMessage(content=f"""
                Consulta: {query}
                
                Documentos recuperados:
                {json.dumps([doc['content'][:500] + '...' for doc in retrieved_docs], indent=2)}
                """)
            ])
            
            response = self.llm.invoke(retriever_prompt.format_messages())
            state["messages"].append(response)
            
        except Exception as e:
            logger.error(f"Error in retriever agent: {str(e)}")
            state["retrieved_docs"] = []
        
        return state
    
    def answerer_agent(self, state: AgentState) -> AgentState:
        """Answerer agent that generates responses with citations"""
        query = state["query"]
        retrieved_docs = state["retrieved_docs"]
        
        if not retrieved_docs:
            state["answer"] = "Não foi possível encontrar informações relevantes nos documentos disponíveis."
            state["citations"] = []
            return state
        
        # Prepare context with citations
        context = ""
        citations = []
        
        for i, doc in enumerate(retrieved_docs):
            context += f"\n[Fonte {i+1}]: {doc['content']}\n"
            citations.append({
                "id": i+1,
                "content": doc['content'][:200] + "...",
                "source": doc['metadata'].get('source', 'Desconhecido'),
                "url": doc['metadata'].get('url', ''),
                "score": doc['score']
            })
        
        answerer_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""
            Você é um especialista em mudanças climáticas e meio ambiente.
            Responda à consulta do usuário baseando-se APENAS nas informações fornecidas nos documentos.
            
            IMPORTANTE:
            1. Use APENAS as informações dos documentos fornecidos
            2. Cite as fontes usando [Fonte X] onde X é o número da fonte
            3. Se não houver informações suficientes, diga claramente
            4. Seja preciso e científico
            5. Evite especulações ou informações não presentes nos documentos
            6. **Formate sua resposta usando Markdown** para melhor legibilidade:
               - Use **negrito** para termos importantes
               - Use *itálico* para ênfase
               - Use listas com - ou números quando apropriado
               - Use ## para subtítulos quando necessário
               - Use `código` para valores específicos ou termos técnicos
            
            Formato da resposta:
            - Resposta clara e objetiva em Markdown
            - Citações obrigatórias [Fonte X]
            - Se aplicável, mencione limitações ou incertezas
            """),
            HumanMessage(content=f"""
            Consulta: {query}
            
            Documentos relevantes:
            {context}
            
            Responda baseando-se APENAS nestes documentos e cite as fontes.
            """)
        ])
        
        response = self.llm.invoke(answerer_prompt.format_messages())
        
        state["answer"] = response.content
        state["citations"] = citations
        
        return state
    
    def self_check_agent(self, state: AgentState) -> AgentState:
        """Self-check agent that validates the answer quality"""
        query = state["query"]
        answer = state["answer"]
        citations = state["citations"]
        
        self_check_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""
            Você é um agente de verificação de qualidade.
            Analise a resposta gerada e verifique:
            
            1. A resposta está baseada nas fontes fornecidas?
            2. As citações estão corretas e presentes?
            3. A resposta responde adequadamente à pergunta?
            4. Há informações não suportadas pelas fontes?
            5. A resposta é cientificamente precisa?
            
            Responda com:
            - "APPROVED" se a resposta está adequada
            - "NEEDS_IMPROVEMENT" se precisa de melhorias
            - "REJECTED" se a resposta não é adequada
            
            Justifique sua decisão.
            """),
            HumanMessage(content=f"""
            Pergunta: {query}
            
            Resposta gerada:
            {answer}
            
            Citações disponíveis: {len(citations)}
            
            Avalie a qualidade da resposta.
            """)
        ])
        
        response = self.llm.invoke(self_check_prompt.format_messages())
        
        # Parse the response to determine if it's approved
        response_text = response.content.lower()
        if "approved" in response_text:
            state["self_check_passed"] = True
        elif "needs_improvement" in response_text or "rejected" in response_text:
            state["self_check_passed"] = False
        else:
            # Default to approved if unclear
            state["self_check_passed"] = True
        
        state["messages"].append(response)
        return state
    
    def safety_agent(self, state: AgentState) -> AgentState:
        """Safety agent that adds disclaimers and checks for safety"""
        answer = state["answer"]
        
        safety_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""
            Você é um agente de segurança e políticas.
            Analise a resposta e adicione disclaimers apropriados se necessário.
            
            Adicione disclaimers para:
            - Informações sobre saúde
            - Conselhos legais
            - Políticas públicas
            - Dados que podem estar desatualizados
            
            Mantenha o tom informativo e científico.
            """),
            HumanMessage(content=f"""
            Resposta a ser revisada:
            {answer}
            
            Adicione disclaimers apropriados se necessário.
            """)
        ])
        
        response = self.llm.invoke(safety_prompt.format_messages())
        
        # Add safety disclaimer
        final_answer = response.content + "\n\n" + SAFETY_DISCLAIMER
        
        state["safety_check_passed"] = True
        state["final_response"] = final_answer
        
        return state
    
    def finalizer_agent(self, state: AgentState) -> AgentState:
        """Finalizer agent that formats the final response"""
        final_response = state["final_response"]
        citations = state["citations"]
        
        # Format citations
        if citations:
            citation_text = "\n\n**Fontes consultadas:**\n"
            for citation in citations:
                citation_text += f"- [{citation['id']}] {citation['source']}"
                if citation['url']:
                    citation_text += f" ({citation['url']})"
                citation_text += "\n"
            
            final_response += citation_text
        
        state["final_response"] = final_response
        return state
    
    def _should_continue_after_self_check(self, state: AgentState) -> str:
        """Determine next step after self-check"""
        if state["self_check_passed"]:
            return "continue"
        elif state["iteration_count"] < 3:  # Max 3 retries
            state["iteration_count"] = state.get("iteration_count", 0) + 1
            return "retry"
        else:
            return "end"
    
    def _convert_markdown_to_html(self, text: str) -> str:
        """Convert Markdown text to HTML"""
        try:
            # Configure markdown with extensions for better formatting
            md = markdown.Markdown(extensions=['nl2br', 'codehilite', 'fenced_code'])
            return md.convert(text)
        except Exception as e:
            logger.warning(f"Error converting markdown to HTML: {str(e)}")
            # Return original text if conversion fails
            return text
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a user query through the agent system"""
        initial_state = {
            "messages": [],
            "query": query,
            "retrieved_docs": [],
            "answer": "",
            "citations": [],
            "safety_check_passed": False,
            "self_check_passed": False,
            "final_response": "",
            "iteration_count": 0
        }
        
        try:
            result = self.graph.invoke(initial_state)
            response_text = result["final_response"]
            
            return {
                "response": response_text,
                "response_html": self._convert_markdown_to_html(response_text),
                "citations": result["citations"],
                "retrieved_docs_count": len(result["retrieved_docs"]),
                "success": True
            }
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "response": "Desculpe, ocorreu um erro ao processar sua consulta. Tente novamente.",
                "citations": [],
                "retrieved_docs_count": 0,
                "success": False
            }
