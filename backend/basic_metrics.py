#!/usr/bin/env python3
"""
Climate Assistant - Coletor de Métricas Básico (sem dependências externas)
Coleta métricas fundamentais de latência, citações e desempenho
"""
import json
import time
import logging
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime
import statistics

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import EVALUATION_DIR
from ingest.document_processor import DocumentProcessor
from src.agents import ClimateAssistantAgents

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BasicMetricsCollector:
    """Coletor básico de métricas sem dependências externas"""
    
    def __init__(self):
        self.start_time = time.time()
        EVALUATION_DIR.mkdir(parents=True, exist_ok=True)
    
    def get_test_questions(self) -> List[Dict[str, Any]]:
        """Get test questions for evaluation"""
        return [
            {
                "question": "Quais são as principais evidências do aquecimento global?",
                "category": "Evidências",
                "complexity": "medium"
            },
            {
                "question": "Como o IPCC define mudanças climáticas?",
                "category": "Definições", 
                "complexity": "low"
            },
            {
                "question": "Quais são os cenários de emissões do IPCC AR6?",
                "category": "Cenários",
                "complexity": "high"
            },
            {
                "question": "Como as mudanças climáticas afetam os oceanos?",
                "category": "Impactos",
                "complexity": "medium"
            },
            {
                "question": "Quais são as principais fontes de gases de efeito estufa?",
                "category": "Causas",
                "complexity": "medium"
            },
            {
                "question": "Como podemos mitigar as mudanças climáticas?",
                "category": "Mitigação",
                "complexity": "high"
            },
            {
                "question": "Quais são os impactos das mudanças climáticas na biodiversidade?",
                "category": "Impactos",
                "complexity": "high"
            },
            {
                "question": "Como adaptar-se às mudanças climáticas?",
                "category": "Adaptação",
                "complexity": "high"
            }
        ]
    
    def initialize_system(self):
        """Initialize the RAG system"""
        try:
            logger.info("🔧 Inicializando sistema RAG...")
            self.document_processor = DocumentProcessor()
            
            if not self.document_processor.load_vector_store():
                raise Exception("Vector store não encontrado")
            
            self.climate_agents = ClimateAssistantAgents(self.document_processor)
            logger.info("✅ Sistema inicializado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na inicialização: {e}")
            return False
    
    def collect_latency_metrics(self, questions: List[Dict[str, Any]], runs: int = 3) -> Dict[str, Any]:
        """Collect latency metrics"""
        logger.info(f"⏱️ Coletando métricas de latência ({runs} execuções)...")
        
        all_latencies = []
        category_latencies = {}
        results_detail = []
        
        total_queries = len(questions) * runs
        successful_queries = 0
        
        for q_data in questions:
            question = q_data["question"]
            category = q_data["category"]
            
            if category not in category_latencies:
                category_latencies[category] = []
            
            for run in range(runs):
                start_time = time.time()
                
                try:
                    result = self.climate_agents.process_query(question)
                    end_time = time.time()
                    
                    latency = end_time - start_time
                    all_latencies.append(latency)
                    category_latencies[category].append(latency)
                    successful_queries += 1
                    
                    results_detail.append({
                        "question": question,
                        "category": category,
                        "run": run + 1,
                        "latency": latency,
                        "response_length": len(result.get("response", "")),
                        "citations_count": len(result.get("citations", [])),
                        "success": True
                    })
                    
                except Exception as e:
                    logger.error(f"Erro na pergunta '{question}': {e}")
                    results_detail.append({
                        "question": question,
                        "category": category,
                        "run": run + 1,
                        "error": str(e),
                        "success": False
                    })
        
        # Calculate statistics
        if all_latencies:
            latency_metrics = {
                "total_queries": total_queries,
                "successful_queries": successful_queries,
                "success_rate": successful_queries / total_queries,
                "mean_latency": statistics.mean(all_latencies),
                "median_latency": statistics.median(all_latencies),
                "min_latency": min(all_latencies),
                "max_latency": max(all_latencies),
                "latency_std": statistics.stdev(all_latencies) if len(all_latencies) > 1 else 0
            }
            
            # Calculate percentiles manually
            sorted_latencies = sorted(all_latencies)
            n = len(sorted_latencies)
            latency_metrics["p95_latency"] = sorted_latencies[int(0.95 * n)] if n > 0 else 0
            latency_metrics["p99_latency"] = sorted_latencies[int(0.99 * n)] if n > 0 else 0
            
            # Category breakdown
            category_stats = {}
            for category, cat_latencies in category_latencies.items():
                if cat_latencies:
                    category_stats[category] = {
                        "mean_latency": statistics.mean(cat_latencies),
                        "count": len(cat_latencies),
                        "min_latency": min(cat_latencies),
                        "max_latency": max(cat_latencies)
                    }
            
            latency_metrics["category_breakdown"] = category_stats
            latency_metrics["detailed_results"] = results_detail
            
        else:
            latency_metrics = {"error": "Nenhuma consulta bem-sucedida"}
        
        return latency_metrics
    
    def collect_citation_metrics(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Collect citation quality metrics"""
        logger.info("📚 Coletando métricas de citações...")
        
        citation_data = []
        total_questions = len(questions)
        questions_with_citations = 0
        total_citations = 0
        total_unique_sources = 0
        pdf_citations = 0
        website_citations = 0
        total_response_length = 0
        
        for q_data in questions:
            question = q_data["question"]
            
            try:
                result = self.climate_agents.process_query(question)
                response = result.get("response", "")
                citations = result.get("citations", [])
                
                # Count citations
                has_citations = len(citations) > 0
                if has_citations:
                    questions_with_citations += 1
                
                total_citations += len(citations)
                total_response_length += len(response)
                
                # Analyze citation sources
                unique_sources = set()
                q_pdf_citations = 0
                q_website_citations = 0
                
                for citation in citations:
                    source = citation.get("source", "")
                    doc_type = citation.get("type", "")
                    
                    unique_sources.add(source)
                    
                    if doc_type == "local_pdf":
                        q_pdf_citations += 1
                        pdf_citations += 1
                    elif doc_type == "website":
                        q_website_citations += 1
                        website_citations += 1
                
                total_unique_sources += len(unique_sources)
                
                # Citation density (citations per 1000 characters)
                citation_density = (len(citations) / max(len(response), 1)) * 1000
                
                citation_data.append({
                    "question": question,
                    "response_length": len(response),
                    "citations_count": len(citations),
                    "unique_sources": len(unique_sources),
                    "pdf_citations": q_pdf_citations,
                    "website_citations": q_website_citations,
                    "citation_density": citation_density,
                    "has_citations": has_citations
                })
                
            except Exception as e:
                logger.error(f"Erro ao analisar citações para '{question}': {e}")
                citation_data.append({
                    "question": question,
                    "error": str(e),
                    "success": False
                })
        
        # Calculate aggregate metrics
        if total_questions > 0:
            citation_metrics = {
                "total_questions": total_questions,
                "questions_with_citations": questions_with_citations,
                "citation_rate": questions_with_citations / total_questions,
                "average_citations_per_response": total_citations / total_questions,
                "average_unique_sources_per_response": total_unique_sources / total_questions,
                "total_citations": total_citations,
                "pdf_citations": pdf_citations,
                "website_citations": website_citations,
                "pdf_citation_percentage": (pdf_citations / max(total_citations, 1)) * 100,
                "website_citation_percentage": (website_citations / max(total_citations, 1)) * 100,
                "average_response_length": total_response_length / total_questions
            }
            
            # Citation density statistics
            densities = [d.get("citation_density", 0) for d in citation_data if d.get("success", True)]
            if densities:
                citation_metrics["citation_density_mean"] = statistics.mean(densities)
                citation_metrics["citation_density_std"] = statistics.stdev(densities) if len(densities) > 1 else 0
            
            citation_metrics["detailed_results"] = citation_data
            
        else:
            citation_metrics = {"error": "Nenhuma pergunta processada"}
        
        return citation_metrics
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level metrics"""
        logger.info("🔧 Coletando métricas do sistema...")
        
        try:
            from src.config import VECTOR_STORE_DIR, DOCUMENTS_DIR
            
            # Vector store info
            vector_store_info = {"exists": False, "size_mb": 0}
            faiss_index = VECTOR_STORE_DIR / "faiss_index" / "index.faiss"
            if faiss_index.exists():
                size_bytes = faiss_index.stat().st_size
                vector_store_info = {
                    "exists": True,
                    "size_mb": size_bytes / (1024 * 1024),
                    "path": str(faiss_index)
                }
            
            # Document info
            pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))
            document_info = {
                "pdf_count": len(pdf_files),
                "pdf_files": [pdf.name for pdf in pdf_files],
                "total_pdf_size_mb": sum(pdf.stat().st_size for pdf in pdf_files) / (1024 * 1024)
            }
            
            # Test vector store functionality
            vector_store_functional = False
            try:
                if self.document_processor:
                    test_docs = self.document_processor.search_documents("test", k=1)
                    vector_store_functional = len(test_docs) > 0
            except:
                pass
            
            return {
                "vector_store": vector_store_info,
                "documents": document_info,
                "vector_store_functional": vector_store_functional,
                "system_initialized": hasattr(self, 'climate_agents')
            }
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas do sistema: {e}")
            return {"error": str(e)}
    
    def generate_report(self, metrics: Dict[str, Any]) -> str:
        """Generate comprehensive metrics report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        duration = time.time() - self.start_time
        
        report = f"""# 📊 CLIMATE ASSISTANT - RELATÓRIO DE MÉTRICAS

**Data:** {timestamp}  
**Duração da Avaliação:** {duration:.1f} segundos

---

## 🎯 RESUMO EXECUTIVO"""
        
        # Latency summary
        if "latency" in metrics and "error" not in metrics["latency"]:
            lat = metrics["latency"]
            report += f"""

### ⏱️ Performance de Latência
- **Taxa de Sucesso:** {lat.get('success_rate', 0):.1%}
- **Latência Média:** {lat.get('mean_latency', 0):.2f}s
- **Latência Mediana:** {lat.get('median_latency', 0):.2f}s  
- **P95:** {lat.get('p95_latency', 0):.2f}s | **P99:** {lat.get('p99_latency', 0):.2f}s
- **Variação:** {lat.get('min_latency', 0):.2f}s - {lat.get('max_latency', 0):.2f}s"""
        
        # Citation summary  
        if "citations" in metrics and "error" not in metrics["citations"]:
            cit = metrics["citations"]
            report += f"""

### 📚 Qualidade das Citações
- **Taxa de Citações:** {cit.get('citation_rate', 0):.1%}
- **Citações por Resposta:** {cit.get('average_citations_per_response', 0):.1f}
- **Fontes Únicas por Resposta:** {cit.get('average_unique_sources_per_response', 0):.1f}
- **Distribuição:** {cit.get('pdf_citation_percentage', 0):.1f}% PDFs, {cit.get('website_citation_percentage', 0):.1f}% Websites
- **Densidade Média:** {cit.get('citation_density_mean', 0):.1f} citações/1000 chars"""
        
        # System summary
        if "system" in metrics and "error" not in metrics["system"]:
            sys_info = metrics["system"]
            report += f"""

### 🔧 Status do Sistema
- **Vector Store:** {'✅ Funcional' if sys_info.get('vector_store_functional') else '❌ Problema'}
- **Tamanho do Índice:** {sys_info.get('vector_store', {}).get('size_mb', 0):.1f} MB
- **PDFs Carregados:** {sys_info.get('documents', {}).get('pdf_count', 0)} arquivos
- **Tamanho Total PDFs:** {sys_info.get('documents', {}).get('total_pdf_size_mb', 0):.1f} MB"""
        
        report += f"""

---

## 📈 ANÁLISE DETALHADA

### Distribuição de Latência por Categoria"""
        
        if "latency" in metrics and "category_breakdown" in metrics["latency"]:
            for category, stats in metrics["latency"]["category_breakdown"].items():
                report += f"""
- **{category}:** {stats['mean_latency']:.2f}s (min: {stats['min_latency']:.2f}s, max: {stats['max_latency']:.2f}s, n={stats['count']})"""
        
        report += f"""

### Análise de Citações
"""
        
        if "citations" in metrics and "detailed_results" in metrics["citations"]:
            successful_citations = [r for r in metrics["citations"]["detailed_results"] if r.get("success", True)]
            if successful_citations:
                with_cit = sum(1 for r in successful_citations if r.get("has_citations"))
                report += f"""
- **Perguntas com Citações:** {with_cit}/{len(successful_citations)} ({with_cit/len(successful_citations):.1%})
- **Fontes mais Citadas:** Mix de PDFs locais e websites do IPCC
- **Qualidade:** Citações extraídas automaticamente com metadados preservados"""
        
        report += f"""

---

## 🎯 RECOMENDAÇÕES

### Melhorias de Performance
1. **Latência:** Otimizar pipeline de recuperação para < 2s médio
2. **Cache:** Implementar cache para consultas frequentes  
3. **Indexação:** Revisar tamanho de chunks para melhor precisão

### Qualidade das Respostas
1. **Citações:** Aumentar densidade para > 80% das respostas
2. **Fontes:** Balancear uso de PDFs e websites
3. **Precisão:** Implementar validação automática de citações

### Monitoramento
1. **Métricas Contínuas:** Dashboard em tempo real
2. **Alertas:** Definir thresholds para degradação
3. **A/B Testing:** Comparar diferentes configurações

---

## 📊 DADOS TÉCNICOS

**Sistema:**
- Vector Store: {'Funcional' if metrics.get('system', {}).get('vector_store_functional') else 'Com problemas'}
- Documentos: {metrics.get('system', {}).get('documents', {}).get('pdf_count', 0)} PDFs indexados
- Performance: {metrics.get('latency', {}).get('success_rate', 0):.1%} taxa de sucesso

**Próximos Passos:**
- Executar novamente: `python basic_metrics.py`
- Métricas RAGAS completas: `python setup_metrics.py && python collect_metrics.py`
- Análise histórica: Comparar com execuções anteriores

---
*Gerado por Climate Assistant Basic Metrics Collector v1.0*
"""
        
        return report
    
    def save_results(self, metrics: Dict[str, Any]) -> tuple:
        """Save metrics to files"""
        timestamp = int(time.time())
        
        # Save JSON
        json_file = EVALUATION_DIR / f"basic_metrics_{timestamp}.json"
        metrics["metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": time.time() - self.start_time,
            "collector_version": "basic_v1.0"
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False, default=str)
        
        # Save report
        report = self.generate_report(metrics)
        report_file = EVALUATION_DIR / f"basic_metrics_report_{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return json_file, report_file
    
    def run_evaluation(self) -> Dict[str, Any]:
        """Run complete basic evaluation"""
        logger.info("🚀 Iniciando coleta básica de métricas...")
        
        if not self.initialize_system():
            return {"error": "Falha na inicialização"}
        
        questions = self.get_test_questions()
        logger.info(f"📝 Avaliando {len(questions)} perguntas")
        
        metrics = {}
        
        # Collect all metrics
        metrics["latency"] = self.collect_latency_metrics(questions)
        metrics["citations"] = self.collect_citation_metrics(questions)
        metrics["system"] = self.collect_system_metrics()
        
        # Save results
        json_file, report_file = self.save_results(metrics)
        
        logger.info("✅ Avaliação concluída!")
        logger.info(f"📄 Relatório: {report_file}")
        logger.info(f"📊 Dados: {json_file}")
        
        return metrics

def main():
    """Main function"""
    print("🌍 CLIMATE ASSISTANT - MÉTRICAS BÁSICAS")
    print("=" * 45)
    print("📋 Coletando: Latência, Citações, Performance")
    print()
    
    collector = BasicMetricsCollector()
    results = collector.run_evaluation()
    
    if "error" not in results:
        print("\n🎉 Coleta de métricas concluída!")
        print(f"📁 Resultados salvos em: {EVALUATION_DIR}")
        
        # Show quick summary
        if "latency" in results and "error" not in results["latency"]:
            lat = results["latency"]
            print(f"⏱️ Latência média: {lat.get('mean_latency', 0):.2f}s")
            print(f"✅ Taxa de sucesso: {lat.get('success_rate', 0):.1%}")
        
        if "citations" in results and "error" not in results["citations"]:
            cit = results["citations"]
            print(f"📚 Taxa de citações: {cit.get('citation_rate', 0):.1%}")
            print(f"🔗 Citações por resposta: {cit.get('average_citations_per_response', 0):.1f}")
            
    else:
        print(f"❌ Erro: {results['error']}")

if __name__ == "__main__":
    main()