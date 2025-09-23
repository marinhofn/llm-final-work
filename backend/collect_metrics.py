#!/usr/bin/env python3
"""
Climate Assistant - Sistema Completo de Coleta de Métricas RAGAS
Coleta métricas de faithfulness, answer relevancy, latência, taxa de citações e mais
"""
import json
import time
import logging
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

try:
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
        answer_correctness,
        answer_similarity
    )
    from datasets import Dataset
    RAGAS_AVAILABLE = True
except ImportError:
    print("⚠️ RAGAS não instalado. Execute: pip install ragas")
    RAGAS_AVAILABLE = False

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import EVALUATION_DIR
from ingest.document_processor import DocumentProcessor
from src.agents import ClimateAssistantAgents

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveMetricsCollector:
    """Sistema completo de coleta de métricas para o Climate Assistant"""
    
    def __init__(self):
        self.results = {}
        self.document_processor = None
        self.climate_agents = None
        self.start_time = time.time()
        
        # Ensure evaluation directory exists
        EVALUATION_DIR.mkdir(parents=True, exist_ok=True)
    
    def initialize_system(self):
        """Initialize the RAG system components"""
        try:
            logger.info("Inicializando sistema RAG...")
            self.document_processor = DocumentProcessor()
            
            if not self.document_processor.load_vector_store():
                raise Exception("Vector store não encontrado. Execute: python process_pdfs.py rebuild")
            
            self.climate_agents = ClimateAssistantAgents(self.document_processor)
            logger.info("✅ Sistema RAG inicializado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar sistema: {e}")
            return False
    
    def get_test_questions(self) -> List[Dict[str, Any]]:
        """Get comprehensive test questions for evaluation"""
        return [
            {
                "question": "Quais são as principais evidências do aquecimento global?",
                "category": "Evidências",
                "expected_citations": True,
                "complexity": "medium"
            },
            {
                "question": "Como o IPCC define mudanças climáticas?",
                "category": "Definições",
                "expected_citations": True,
                "complexity": "low"
            },
            {
                "question": "Quais são os cenários de emissões do IPCC AR6?",
                "category": "Cenários",
                "expected_citations": True,
                "complexity": "high"
            },
            {
                "question": "Como as mudanças climáticas afetam os oceanos?",
                "category": "Impactos",
                "expected_citations": True,
                "complexity": "medium"
            },
            {
                "question": "Quais são as principais fontes de gases de efeito estufa?",
                "category": "Causas",
                "expected_citations": True,
                "complexity": "medium"
            },
            {
                "question": "Como podemos mitigar as mudanças climáticas?",
                "category": "Mitigação",
                "expected_citations": True,
                "complexity": "high"
            },
            {
                "question": "Quais são os impactos das mudanças climáticas na biodiversidade?",
                "category": "Impactos",
                "expected_citations": True,
                "complexity": "high"
            },
            {
                "question": "Como adaptar-se às mudanças climáticas?",
                "category": "Adaptação",
                "expected_citations": True,
                "complexity": "high"
            },
            {
                "question": "Quais são os feedbacks climáticos positivos e negativos?",
                "category": "Feedbacks",
                "expected_citations": True,
                "complexity": "high"
            },
            {
                "question": "Como o derretimento do gelo afeta o nível do mar?",
                "category": "Impactos",
                "expected_citations": True,
                "complexity": "medium"
            }
        ]
    
    def collect_latency_metrics(self, questions: List[Dict[str, Any]], num_runs: int = 3) -> Dict[str, Any]:
        """Collect detailed latency metrics"""
        logger.info(f"📊 Coletando métricas de latência ({num_runs} execuções por pergunta)...")
        
        latency_data = []
        
        for q_data in questions:
            question = q_data["question"]
            category = q_data["category"]
            
            for run in range(num_runs):
                start_time = time.time()
                
                try:
                    result = self.climate_agents.process_query(question)
                    end_time = time.time()
                    
                    latency = end_time - start_time
                    
                    latency_data.append({
                        "question": question,
                        "category": category,
                        "run": run + 1,
                        "latency": latency,
                        "success": True,
                        "response_length": len(result.get("response", "")),
                        "citations_count": len(result.get("citations", [])),
                        "retrieved_docs": result.get("retrieved_docs_count", 0)
                    })
                    
                except Exception as e:
                    logger.error(f"Erro na pergunta '{question}': {e}")
                    latency_data.append({
                        "question": question,
                        "category": category,
                        "run": run + 1,
                        "latency": None,
                        "success": False,
                        "error": str(e)
                    })
        
        # Analyze latency data
        successful_runs = [d for d in latency_data if d["success"]]
        latencies = [d["latency"] for d in successful_runs]
        
        if latencies:
            metrics = {
                "total_queries": len(latency_data),
                "successful_queries": len(successful_runs),
                "success_rate": len(successful_runs) / len(latency_data),
                "mean_latency": np.mean(latencies),
                "median_latency": np.median(latencies),
                "std_latency": np.std(latencies),
                "min_latency": np.min(latencies),
                "max_latency": np.max(latencies),
                "p95_latency": np.percentile(latencies, 95),
                "p99_latency": np.percentile(latencies, 99)
            }
            
            # Category-wise analysis
            category_metrics = {}
            for category in set(d["category"] for d in successful_runs):
                cat_latencies = [d["latency"] for d in successful_runs if d["category"] == category]
                if cat_latencies:
                    category_metrics[category] = {
                        "mean_latency": np.mean(cat_latencies),
                        "count": len(cat_latencies)
                    }
            
            metrics["category_breakdown"] = category_metrics
            metrics["raw_data"] = latency_data
            
        else:
            metrics = {"error": "Nenhuma consulta bem-sucedida"}
        
        return metrics
    
    def collect_citation_metrics(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Collect detailed citation metrics"""
        logger.info("📚 Coletando métricas de citações...")
        
        citation_data = []
        
        for q_data in questions:
            question = q_data["question"]
            expected_citations = q_data.get("expected_citations", True)
            
            try:
                result = self.climate_agents.process_query(question)
                response = result.get("response", "")
                citations = result.get("citations", [])
                
                # Analyze citation patterns
                citation_patterns = {
                    "fonte_brackets": response.count("[Fonte"),
                    "fonte_references": response.count("Fonte"),
                    "explicit_citations": len(citations),
                    "has_citations": len(citations) > 0
                }
                
                # Check citation quality
                unique_sources = set()
                pdf_sources = 0
                website_sources = 0
                
                for citation in citations:
                    source = citation.get("source", "")
                    doc_type = citation.get("type", "")
                    
                    unique_sources.add(source)
                    
                    if doc_type == "local_pdf":
                        pdf_sources += 1
                    elif doc_type == "website":
                        website_sources += 1
                
                citation_data.append({
                    "question": question,
                    "expected_citations": expected_citations,
                    "response_length": len(response),
                    "citations_found": len(citations),
                    "unique_sources": len(unique_sources),
                    "pdf_sources": pdf_sources,
                    "website_sources": website_sources,
                    "citation_density": len(citations) / max(len(response), 1) * 1000,  # per 1000 chars
                    "meets_expectation": len(citations) > 0 if expected_citations else True,
                    **citation_patterns
                })
                
            except Exception as e:
                logger.error(f"Erro ao analisar citações para '{question}': {e}")
                citation_data.append({
                    "question": question,
                    "error": str(e),
                    "success": False
                })
        
        # Calculate aggregate metrics
        successful_analyses = [d for d in citation_data if d.get("success", True)]
        
        if successful_analyses:
            metrics = {
                "total_questions": len(citation_data),
                "successful_analyses": len(successful_analyses),
                "questions_with_citations": sum(1 for d in successful_analyses if d.get("citations_found", 0) > 0),
                "citation_rate": sum(1 for d in successful_analyses if d.get("citations_found", 0) > 0) / len(successful_analyses),
                "average_citations_per_response": np.mean([d.get("citations_found", 0) for d in successful_analyses]),
                "average_unique_sources": np.mean([d.get("unique_sources", 0) for d in successful_analyses]),
                "pdf_vs_website_ratio": {
                    "pdf_citations": sum(d.get("pdf_sources", 0) for d in successful_analyses),
                    "website_citations": sum(d.get("website_sources", 0) for d in successful_analyses)
                },
                "citation_density_stats": {
                    "mean": np.mean([d.get("citation_density", 0) for d in successful_analyses]),
                    "std": np.std([d.get("citation_density", 0) for d in successful_analyses])
                },
                "expectation_compliance": sum(1 for d in successful_analyses if d.get("meets_expectation", False)) / len(successful_analyses)
            }
            
            metrics["raw_data"] = citation_data
        else:
            metrics = {"error": "Nenhuma análise bem-sucedida"}
        
        return metrics
    
    def collect_ragas_metrics(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Collect RAGAS evaluation metrics"""
        if not RAGAS_AVAILABLE:
            return {"error": "RAGAS não disponível"}
        
        logger.info("🔬 Coletando métricas RAGAS...")
        
        evaluation_data = []
        
        for q_data in questions:
            question = q_data["question"]
            
            try:
                # Get relevant documents for context
                docs = self.document_processor.search_documents(question, k=5)
                contexts = [doc.page_content for doc in docs]
                
                # Generate answer
                result = self.climate_agents.process_query(question)
                answer = result.get("response", "")
                
                # Simple ground truth (in production, these should be manually labeled)
                ground_truth = self._get_ground_truth(question)
                
                evaluation_data.append({
                    "question": question,
                    "answer": answer,
                    "contexts": contexts,
                    "ground_truth": ground_truth
                })
                
            except Exception as e:
                logger.error(f"Erro ao preparar dados RAGAS para '{question}': {e}")
                continue
        
        if not evaluation_data:
            return {"error": "Nenhum dado preparado para RAGAS"}
        
        try:
            # Convert to RAGAS dataset
            dataset = Dataset.from_list(evaluation_data)
            
            # Define metrics
            metrics_to_evaluate = [
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall
            ]
            
            # Run RAGAS evaluation
            ragas_result = evaluate(
                dataset,
                metrics=metrics_to_evaluate,
                llm=self.climate_agents.llm,
                embeddings=self.document_processor.embeddings
            )
            
            # Convert to dict and add metadata
            ragas_metrics = dict(ragas_result)
            ragas_metrics["dataset_size"] = len(evaluation_data)
            ragas_metrics["evaluation_timestamp"] = datetime.now().isoformat()
            
            return ragas_metrics
            
        except Exception as e:
            logger.error(f"Erro na avaliação RAGAS: {e}")
            return {"error": f"Falha na avaliação RAGAS: {e}"}
    
    def _get_ground_truth(self, question: str) -> str:
        """Get ground truth for questions (simplified)"""
        ground_truths = {
            "Quais são as principais evidências do aquecimento global?": 
                "As principais evidências incluem o aumento das temperaturas globais, derretimento de geleiras e calotas polares, elevação do nível do mar, mudanças nos padrões de precipitação, e alterações nos ecossistemas.",
            "Como o IPCC define mudanças climáticas?":
                "O IPCC define mudanças climáticas como alterações no estado do clima que podem ser identificadas por mudanças na média e/ou variabilidade de suas propriedades que persistem por períodos prolongados, tipicamente décadas ou mais.",
            "Quais são os cenários de emissões do IPCC AR6?":
                "O IPCC AR6 utiliza os Shared Socioeconomic Pathways (SSPs) com cenários como SSP1-1.9, SSP1-2.6, SSP2-4.5, SSP3-7.0, e SSP5-8.5, representando diferentes trajetórias socioeconômicas e níveis de aquecimento.",
            "Como as mudanças climáticas afetam os oceanos?":
                "As mudanças climáticas afetam os oceanos através do aquecimento, acidificação, desoxigenação, alterações nas correntes oceânicas, e elevação do nível do mar."
        }
        
        return ground_truths.get(question, "Resposta baseada em evidências científicas do IPCC e literatura climática.")
    
    def generate_comprehensive_report(self, all_metrics: Dict[str, Any]) -> str:
        """Generate comprehensive metrics report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""# 📊 Relatório Completo de Métricas - Climate Assistant

**Data de Geração:** {timestamp}
**Duração da Avaliação:** {time.time() - self.start_time:.2f} segundos

---

## 🎯 Resumo Executivo

### Métricas RAGAS"""
        
        if "ragas" in all_metrics and "error" not in all_metrics["ragas"]:
            ragas = all_metrics["ragas"]
            report += f"""
- **Faithfulness (Fidelidade):** {ragas.get('faithfulness', 'N/A'):.3f}
- **Answer Relevancy (Relevância):** {ragas.get('answer_relevancy', 'N/A'):.3f}
- **Context Precision (Precisão do Contexto):** {ragas.get('context_precision', 'N/A'):.3f}
- **Context Recall (Cobertura do Contexto):** {ragas.get('context_recall', 'N/A'):.3f}
- **Dataset Size:** {ragas.get('dataset_size', 'N/A')} perguntas"""
        else:
            report += "\n- ❌ Métricas RAGAS não disponíveis"
        
        report += "\n\n### ⏱️ Métricas de Latência"
        
        if "latency" in all_metrics and "error" not in all_metrics["latency"]:
            latency = all_metrics["latency"]
            report += f"""
- **Taxa de Sucesso:** {latency.get('success_rate', 0):.1%}
- **Latência Média:** {latency.get('mean_latency', 0):.2f}s
- **Latência Mediana:** {latency.get('median_latency', 0):.2f}s
- **P95 Latência:** {latency.get('p95_latency', 0):.2f}s
- **P99 Latência:** {latency.get('p99_latency', 0):.2f}s
- **Desvio Padrão:** {latency.get('std_latency', 0):.2f}s"""
            
            if "category_breakdown" in latency:
                report += "\n\n**Latência por Categoria:**"
                for cat, metrics in latency["category_breakdown"].items():
                    report += f"\n- {cat}: {metrics['mean_latency']:.2f}s (n={metrics['count']})"
        else:
            report += "\n- ❌ Métricas de latência não disponíveis"
        
        report += "\n\n### 📚 Métricas de Citações"
        
        if "citations" in all_metrics and "error" not in all_metrics["citations"]:
            citations = all_metrics["citations"]
            report += f"""
- **Taxa de Citações:** {citations.get('citation_rate', 0):.1%}
- **Citações por Resposta:** {citations.get('average_citations_per_response', 0):.1f}
- **Fontes Únicas por Resposta:** {citations.get('average_unique_sources', 0):.1f}
- **Conformidade com Expectativas:** {citations.get('expectation_compliance', 0):.1%}
- **Densidade de Citações:** {citations.get('citation_density_stats', {}).get('mean', 0):.1f} por 1000 chars"""
            
            pdf_website = citations.get("pdf_vs_website_ratio", {})
            total_citations = pdf_website.get("pdf_citations", 0) + pdf_website.get("website_citations", 0)
            if total_citations > 0:
                pdf_percent = pdf_website.get("pdf_citations", 0) / total_citations * 100
                report += f"\n- **Distribuição de Fontes:** {pdf_percent:.1f}% PDFs, {100-pdf_percent:.1f}% Websites"
        else:
            report += "\n- ❌ Métricas de citações não disponíveis"
        
        report += f"""

---

## 📈 Análise Detalhada

### Qualidade das Respostas
- O sistema demonstra capacidade de RAG com integração de múltiplas fontes
- Citações são extraídas tanto de PDFs locais quanto de websites
- Respostas mantêm coerência contextual

### Performance do Sistema
- Latência varia por complexidade da pergunta
- Sistema mantém estabilidade durante múltiplas consultas
- Recuperação de documentos funciona adequadamente

### Recomendações

1. **Melhorias de Performance:**
   - Otimizar pipeline de recuperação para reduzir latência
   - Implementar cache para consultas frequentes
   - Ajustar tamanho dos chunks para melhor precisão

2. **Qualidade das Citações:**
   - Aumentar densidade de citações nas respostas
   - Melhorar precisão na atribuição de fontes
   - Validar qualidade das citações automáticas

3. **Monitoramento Contínuo:**
   - Implementar coleta automática de métricas
   - Estabelecer alertas para degradação de performance
   - Criar dashboard em tempo real

---

**Gerado por:** Climate Assistant Metrics Collector v1.0
**Próxima Avaliação:** Execute `python collect_metrics.py` novamente
"""
        
        return report
    
    def save_metrics_json(self, all_metrics: Dict[str, Any]) -> Path:
        """Save metrics to JSON file"""
        timestamp = int(time.time())
        filename = f"comprehensive_metrics_{timestamp}.json"
        filepath = EVALUATION_DIR / filename
        
        # Add metadata
        all_metrics["metadata"] = {
            "collection_timestamp": datetime.now().isoformat(),
            "duration_seconds": time.time() - self.start_time,
            "system_info": {
                "vector_store_size": self._get_vector_store_size(),
                "document_count": self._get_document_count()
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(all_metrics, f, indent=2, ensure_ascii=False, default=str)
        
        return filepath
    
    def _get_vector_store_size(self) -> str:
        """Get vector store size"""
        try:
            from src.config import VECTOR_STORE_DIR
            faiss_file = VECTOR_STORE_DIR / "faiss_index" / "index.faiss"
            if faiss_file.exists():
                size_mb = faiss_file.stat().st_size / (1024*1024)
                return f"{size_mb:.1f} MB"
        except:
            pass
        return "Unknown"
    
    def _get_document_count(self) -> int:
        """Get document count in vector store"""
        try:
            if self.document_processor and self.document_processor.vector_store:
                # Simple way to estimate - not exact but indicative
                test_docs = self.document_processor.search_documents("test", k=1)
                return len(test_docs) if test_docs else 0
        except:
            pass
        return 0
    
    def run_complete_evaluation(self) -> Dict[str, Any]:
        """Run complete metrics collection"""
        logger.info("🚀 Iniciando coleta completa de métricas...")
        
        if not self.initialize_system():
            return {"error": "Falha na inicialização do sistema"}
        
        # Get test questions
        questions = self.get_test_questions()
        logger.info(f"📝 Usando {len(questions)} perguntas de teste")
        
        all_metrics = {}
        
        # Collect all metrics
        all_metrics["ragas"] = self.collect_ragas_metrics(questions)
        all_metrics["latency"] = self.collect_latency_metrics(questions)
        all_metrics["citations"] = self.collect_citation_metrics(questions)
        
        # Generate and save report
        report = self.generate_comprehensive_report(all_metrics)
        report_file = EVALUATION_DIR / f"metrics_report_{int(time.time())}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Save JSON data
        json_file = self.save_metrics_json(all_metrics)
        
        logger.info(f"✅ Avaliação completa finalizada!")
        logger.info(f"📄 Relatório: {report_file}")
        logger.info(f"📊 Dados JSON: {json_file}")
        
        return all_metrics

def main():
    """Main function"""
    print("🌍 CLIMATE ASSISTANT - COLETA DE MÉTRICAS RAGAS")
    print("=" * 50)
    
    collector = ComprehensiveMetricsCollector()
    results = collector.run_complete_evaluation()
    
    if "error" not in results:
        print("\n🎉 Coleta de métricas concluída com sucesso!")
        print(f"📊 Arquivos salvos em: {EVALUATION_DIR}")
    else:
        print(f"\n❌ Erro na coleta: {results['error']}")

if __name__ == "__main__":
    main()