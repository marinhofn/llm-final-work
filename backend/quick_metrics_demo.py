#!/usr/bin/env python3
"""
Climate Assistant - Demonstração Rápida de Métricas
Teste rápido das principais métricas: faithfulness, answer relevancy, latência, citações
"""
import json
import time
import logging
from datetime import datetime
from pathlib import Path

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import EVALUATION_DIR
from ingest.document_processor import DocumentProcessor
from src.agents import ClimateAssistantAgents

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuickMetricsDemo:
    """Demo rápido de métricas essenciais"""
    
    def __init__(self):
        self.start_time = time.time()
        EVALUATION_DIR.mkdir(parents=True, exist_ok=True)
    
    def quick_test(self):
        """Teste rápido com 3 perguntas"""
        logger.info("🚀 Demo Rápido de Métricas RAGAS")
        
        # Initialize system
        logger.info("🔧 Inicializando sistema...")
        document_processor = DocumentProcessor()
        if not document_processor.load_vector_store():
            logger.error("❌ Vector store não encontrado")
            return
        
        climate_agents = ClimateAssistantAgents(document_processor)
        logger.info("✅ Sistema inicializado")
        
        # Test questions (only 3 for speed)
        test_questions = [
            "Quais são as principais evidências do aquecimento global?",
            "Como o IPCC define mudanças climáticas?", 
            "Quais são os principais gases de efeito estufa?"
        ]
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "questions_tested": len(test_questions),
            "results": []
        }
        
        total_latency = 0
        total_citations = 0
        successful_queries = 0
        
        for i, question in enumerate(test_questions, 1):
            logger.info(f"📝 Pergunta {i}/{len(test_questions)}: {question[:50]}...")
            
            # Measure latency
            start_time = time.time()
            
            try:
                result = climate_agents.process_query(question)
                end_time = time.time()
                
                latency = end_time - start_time
                response = result.get("response", "")
                citations = result.get("citations", [])
                
                # Collect metrics
                total_latency += latency
                total_citations += len(citations)
                successful_queries += 1
                
                # Simple quality assessment
                has_citations = len(citations) > 0
                response_length = len(response)
                citation_quality = "Boa" if has_citations and response_length > 100 else "Regular"
                
                # Check source types
                pdf_sources = sum(1 for c in citations if c.get("type") == "local_pdf")
                website_sources = sum(1 for c in citations if c.get("type") == "website")
                
                result_metrics = {
                    "question": question,
                    "latency_seconds": latency,
                    "response_length": response_length,
                    "citations_count": len(citations),
                    "has_citations": has_citations,
                    "pdf_citations": pdf_sources,
                    "website_citations": website_sources,
                    "citation_quality": citation_quality,
                    "success": True
                }
                
                metrics["results"].append(result_metrics)
                
                # Show immediate feedback
                print(f"  ⏱️ Latência: {latency:.2f}s")
                print(f"  📚 Citações: {len(citations)} ({'✅' if has_citations else '❌'})")
                print(f"  📄 Fontes: {pdf_sources} PDFs, {website_sources} Websites")
                print(f"  📝 Resposta: {response_length} caracteres")
                print()
                
            except Exception as e:
                logger.error(f"❌ Erro na pergunta {i}: {e}")
                metrics["results"].append({
                    "question": question,
                    "error": str(e),
                    "success": False
                })
        
        # Calculate summary metrics
        if successful_queries > 0:
            avg_latency = total_latency / successful_queries
            avg_citations = total_citations / successful_queries
            citation_rate = sum(1 for r in metrics["results"] if r.get("has_citations")) / successful_queries
            
            summary = {
                "total_queries": len(test_questions),
                "successful_queries": successful_queries,
                "success_rate": successful_queries / len(test_questions),
                "average_latency": avg_latency,
                "average_citations_per_response": avg_citations,
                "citation_rate": citation_rate,
                "total_pdf_citations": sum(r.get("pdf_citations", 0) for r in metrics["results"]),
                "total_website_citations": sum(r.get("website_citations", 0) for r in metrics["results"])
            }
            
            metrics["summary"] = summary
            
            # Display summary
            print("=" * 50)
            print("📊 RESUMO DAS MÉTRICAS COLETADAS")
            print("=" * 50)
            print(f"✅ Taxa de Sucesso: {summary['success_rate']:.1%}")
            print(f"⏱️ Latência Média: {summary['average_latency']:.2f}s")
            print(f"📚 Citações por Resposta: {summary['average_citations_per_response']:.1f}")
            print(f"🔗 Taxa de Citações: {summary['citation_rate']:.1%}")
            print(f"📄 Distribuição: {summary['total_pdf_citations']} PDFs, {summary['total_website_citations']} Websites")
            
            # Simulate RAGAS-like quality scores
            print("\n🔬 MÉTRICAS ESTIMADAS (simuladas):")
            faithfulness = min(0.95, 0.7 + (summary['citation_rate'] * 0.3))
            answer_relevancy = min(0.90, 0.6 + (summary['success_rate'] * 0.3))
            
            print(f"📋 Faithfulness (Fidelidade): {faithfulness:.3f}")
            print(f"🎯 Answer Relevancy (Relevância): {answer_relevancy:.3f}")
            print(f"📊 Context Precision: {summary['citation_rate']:.3f}")
            
            metrics["simulated_ragas"] = {
                "faithfulness": faithfulness,
                "answer_relevancy": answer_relevancy,
                "context_precision": summary['citation_rate']
            }
        
        # Save results
        timestamp = int(time.time())
        results_file = EVALUATION_DIR / f"quick_metrics_demo_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Resultados salvos em: {results_file}")
        print(f"⏱️ Tempo total: {time.time() - self.start_time:.1f}s")
        
        return metrics

def main():
    """Main function"""
    print("🌍 CLIMATE ASSISTANT - DEMO RÁPIDO DE MÉTRICAS")
    print("📋 Testando: Latência, Citações, Qualidade das Respostas")
    print("⚡ Modo rápido: 3 perguntas apenas")
    print()
    
    demo = QuickMetricsDemo()
    results = demo.quick_test()
    
    if results and "summary" in results:
        print("\n🎉 Demo concluído com sucesso!")
        print("\n💡 Para avaliação completa:")
        print("   python basic_metrics.py    # Métricas básicas completas")
        print("   python setup_metrics.py    # Instalar RAGAS")
        print("   python collect_metrics.py  # Métricas RAGAS completas")
    else:
        print("\n❌ Demo falhou. Verifique se o sistema está funcionando.")

if __name__ == "__main__":
    main()