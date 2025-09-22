#!/usr/bin/env python3
"""
Comprehensive evaluation script for the Climate Assistant RAG System
Runs both RAGAS and Giskard evaluations
"""
import sys
import os
import time
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.config import EVALUATION_DIR
from ingest.document_processor import DocumentProcessor
from src.agents import ClimateAssistantAgents
from eval.evaluation import ClimateAssistantEvaluator
from eval.giskard_evaluation import ClimateAssistantGiskardEvaluator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_ragas_evaluation(document_processor, climate_agents):
    """Run RAGAS evaluation"""
    logger.info("=" * 60)
    logger.info("RUNNING RAGAS EVALUATION")
    logger.info("=" * 60)
    
    try:
        evaluator = ClimateAssistantEvaluator(document_processor, climate_agents)
        results = evaluator.run_comprehensive_evaluation()
        
        # Generate and save report
        report = evaluator.generate_evaluation_report(results)
        report_file = EVALUATION_DIR / f"ragas_report_{int(time.time())}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"RAGAS evaluation completed. Report saved to {report_file}")
        return results
        
    except Exception as e:
        logger.error(f"Error in RAGAS evaluation: {str(e)}")
        return None

def run_giskard_evaluation(document_processor, climate_agents):
    """Run Giskard evaluation"""
    logger.info("=" * 60)
    logger.info("RUNNING GISKARD EVALUATION")
    logger.info("=" * 60)
    
    try:
        evaluator = ClimateAssistantGiskardEvaluator(document_processor, climate_agents)
        results = evaluator.run_comprehensive_giskard_evaluation()
        
        # Generate and save report
        report = evaluator.generate_giskard_report(results)
        report_file = EVALUATION_DIR / f"giskard_report_{int(time.time())}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Giskard evaluation completed. Report saved to {report_file}")
        return results
        
    except Exception as e:
        logger.error(f"Error in Giskard evaluation: {str(e)}")
        return None

def generate_summary_report(ragas_results, giskard_results):
    """Generate a summary report combining both evaluations"""
    logger.info("=" * 60)
    logger.info("GENERATING SUMMARY REPORT")
    logger.info("=" * 60)
    
    summary = f"""
# Relatório de Avaliação Completa - Climate Assistant RAG System

## Resumo Executivo
- **Data da Avaliação**: {time.strftime("%Y-%m-%d %H:%M:%S")}
- **Avaliações Executadas**: RAGAS + Giskard
- **Status**: Avaliação Completa

## Resultados RAGAS
"""
    
    if ragas_results:
        summary += f"""
- **Dataset**: {ragas_results.get('dataset_size', 0)} perguntas
- **Métricas de Qualidade**:"""
        
        if 'ragas_metrics' in ragas_results and ragas_results['ragas_metrics']:
            for metric, value in ragas_results['ragas_metrics'].items():
                summary += f"\n  - **{metric}**: {value:.3f}"
        else:
            summary += "\n  - Métricas RAGAS não disponíveis"
        
        summary += f"""
- **Latência Média**: {ragas_results.get('latency_metrics', {}).get('mean_latency', 0):.2f}s
- **Citações**: {ragas_results.get('citation_metrics', {}).get('questions_with_citations', 0):.1%} das respostas
"""
    else:
        summary += "\n- **Status**: RAGAS evaluation failed\n"
    
    summary += f"""
## Resultados Giskard
"""
    
    if giskard_results and 'error' not in giskard_results:
        summary += f"""
- **Dataset**: {giskard_results.get('dataset_size', 0)} perguntas
- **Problemas Identificados**:"""
        
        if 'scan_results' in giskard_results and 'scan_summary' in giskard_results['scan_results']:
            scan_summary = giskard_results['scan_results']['scan_summary']
            summary += f"""
  - **Total**: {scan_summary.get('total_issues', 0)}
  - **Críticos**: {scan_summary.get('critical_issues', 0)}
  - **Avisos**: {scan_summary.get('warnings', 0)}
  - **Info**: {scan_summary.get('info', 0)}"""
        else:
            summary += "\n  - Detalhes do scan não disponíveis"
    else:
        summary += "\n- **Status**: Giskard evaluation failed\n"
    
    summary += f"""

## Recomendações Gerais

### Qualidade das Respostas
1. **Faithfulness**: Melhorar fidelidade às fontes
2. **Relevância**: Aumentar relevância das respostas
3. **Citações**: Garantir presença de citações em todas as respostas

### Robustez do Sistema
1. **Problemas Críticos**: Resolver problemas identificados pelo Giskard
2. **Testes**: Implementar testes automatizados regulares
3. **Monitoramento**: Estabelecer monitoramento contínuo

### Performance
1. **Latência**: Otimizar tempo de resposta
2. **Throughput**: Melhorar capacidade de processamento
3. **Escalabilidade**: Preparar para maior volume de consultas

## Conclusão

O sistema Climate Assistant RAG demonstra funcionalidade básica com agentes LangGraph,
mas requer melhorias em qualidade, robustez e performance para uso em produção.
As avaliações RAGAS e Giskard fornecem métricas objetivas para guiar essas melhorias.

### Próximos Passos
1. Implementar melhorias baseadas nos resultados
2. Estabelecer pipeline de avaliação contínua
3. Monitorar métricas em ambiente de produção
4. Expandir dataset de avaliação com mais perguntas rotuladas

---
*Relatório gerado automaticamente em {time.strftime("%Y-%m-%d %H:%M:%S")}*
"""
    
    # Save summary report
    summary_file = EVALUATION_DIR / f"comprehensive_evaluation_summary_{int(time.time())}.md"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    logger.info(f"Summary report saved to {summary_file}")
    return summary

def main():
    """Main function to run comprehensive evaluation"""
    logger.info("🌍 Climate Assistant RAG System - Comprehensive Evaluation")
    logger.info("=" * 80)
    
    try:
        # Initialize components
        logger.info("Initializing system components...")
        document_processor = DocumentProcessor()
        if not document_processor.load_vector_store():
            logger.error("Vector store not found. Please run document processing first.")
            logger.info("Run: python -m ingest.document_processor")
            return False
        
        climate_agents = ClimateAssistantAgents(document_processor)
        logger.info("System components initialized successfully!")
        
        # Run RAGAS evaluation
        ragas_results = run_ragas_evaluation(document_processor, climate_agents)
        
        # Run Giskard evaluation
        giskard_results = run_giskard_evaluation(document_processor, climate_agents)
        
        # Generate summary report
        summary = generate_summary_report(ragas_results, giskard_results)
        
        # Print summary to console
        print("\n" + "=" * 80)
        print("EVALUATION COMPLETE - SUMMARY")
        print("=" * 80)
        print(summary)
        
        logger.info("Comprehensive evaluation completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error in comprehensive evaluation: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

