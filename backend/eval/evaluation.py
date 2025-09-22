"""
Evaluation system for the Climate Assistant RAG system
"""
import json
import time
import logging
from typing import List, Dict, Any, Tuple
from pathlib import Path
import pandas as pd
import numpy as np

from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)
from datasets import Dataset

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import EVALUATION_DIR, EVALUATION_QUESTIONS
from ingest.document_processor import DocumentProcessor
from src.agents import ClimateAssistantAgents

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClimateAssistantEvaluator:
    """Evaluation system for the Climate Assistant"""
    
    def __init__(self, document_processor: DocumentProcessor, climate_agents: ClimateAssistantAgents):
        self.document_processor = document_processor
        self.climate_agents = climate_agents
        self.evaluation_results = []
    
    def create_evaluation_dataset(self) -> List[Dict[str, Any]]:
        """Create evaluation dataset with questions and expected answers"""
        
        # Try to load manually labeled questions first
        manual_questions = self._load_manual_questions()
        
        if manual_questions:
            logger.info(f"Loaded {len(manual_questions)} manually labeled questions")
            all_questions = [q['question'] for q in manual_questions]
            manual_ground_truths = {q['question']: q['ground_truth'] for q in manual_questions}
        else:
            # Fallback to config questions
            logger.info("Using questions from config as fallback")
            base_questions = EVALUATION_QUESTIONS
            
            # Additional questions for comprehensive evaluation
            additional_questions = [
                "Quais são os principais gases de efeito estufa?",
                "Como o aquecimento global afeta os padrões de chuva?",
                "Quais são as evidências do derretimento das calotas polares?",
                "Como as mudanças climáticas afetam a agricultura?",
                "Quais são os cenários de temperatura do IPCC para 2100?",
                "Como o oceano absorve CO2 da atmosfera?",
                "Quais são os impactos das mudanças climáticas na saúde humana?",
                "Como podemos adaptar as cidades às mudanças climáticas?",
                "Quais são os principais sumidouros de carbono?",
                "Como as mudanças climáticas afetam a biodiversidade marinha?"
            ]
            
            all_questions = base_questions + additional_questions
            manual_ground_truths = {}
        
        evaluation_data = []
        
        for i, question in enumerate(all_questions):
            # Get relevant documents for context
            try:
                docs = self.document_processor.search_documents(question, k=3)
                context = [doc.page_content for doc in docs]
                
                # Generate answer using the agent system
                result = self.climate_agents.process_query(question)
                
                evaluation_data.append({
                    "question": question,
                    "answer": result["response"],
                    "contexts": context,
                    "ground_truth": manual_ground_truths.get(question, self._get_ground_truth(question)),
                    "question_id": f"q_{i+1}"
                })
                
            except Exception as e:
                logger.error(f"Error processing question {question}: {str(e)}")
                continue
        
        return evaluation_data
    
    def _load_manual_questions(self) -> List[Dict[str, Any]]:
        """Load manually labeled questions from JSON file"""
        questions_file = EVALUATION_DIR / "manual_questions.json"
        
        if not questions_file.exists():
            logger.warning(f"Manual questions file not found: {questions_file}")
            return []
        
        try:
            with open(questions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('evaluation_dataset', [])
        except Exception as e:
            logger.error(f"Error loading manual questions: {str(e)}")
            return []
    
    def _get_ground_truth(self, question: str) -> str:
        """Get ground truth answer (placeholder - in real scenario, these would be manually labeled)"""
        # This is a simplified version. In a real scenario, you would have
        # manually labeled ground truth answers
        ground_truths = {
            "Quais são as principais evidências do aquecimento global?": 
                "As principais evidências incluem aumento da temperatura global, derretimento de gelo, elevação do nível do mar, e mudanças nos padrões climáticos.",
            "Como o IPCC define mudanças climáticas?":
                "O IPCC define mudanças climáticas como mudanças no estado do clima que persistem por longos períodos, tipicamente décadas ou mais.",
            "Quais são os impactos das mudanças climáticas na biodiversidade?":
                "Os impactos incluem extinção de espécies, mudanças nos habitats, alterações nos ciclos de vida, e perda de diversidade genética."
        }
        
        return ground_truths.get(question, "Resposta baseada em evidências científicas do IPCC e outras fontes climáticas.")
    
    def evaluate_with_ragas(self, evaluation_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Evaluate using RAGAS metrics"""
        try:
            # Convert to RAGAS format
            dataset = Dataset.from_list(evaluation_data)
            
            # Define metrics
            metrics = [
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall
            ]
            
            # Run evaluation
            logger.info("Running RAGAS evaluation...")
            result = evaluate(
                dataset,
                metrics=metrics,
                llm=self.climate_agents.llm,
                embeddings=self.document_processor.embeddings
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in RAGAS evaluation: {str(e)}")
            return {}
    
    def evaluate_latency(self, questions: List[str], num_runs: int = 3) -> Dict[str, float]:
        """Evaluate system latency"""
        latencies = []
        
        for question in questions:
            question_latencies = []
            
            for _ in range(num_runs):
                start_time = time.time()
                try:
                    result = self.climate_agents.process_query(question)
                    end_time = time.time()
                    latency = end_time - start_time
                    question_latencies.append(latency)
                except Exception as e:
                    logger.error(f"Error in latency test: {str(e)}")
                    continue
            
            if question_latencies:
                latencies.extend(question_latencies)
        
        if latencies:
            return {
                "mean_latency": np.mean(latencies),
                "median_latency": np.median(latencies),
                "std_latency": np.std(latencies),
                "min_latency": np.min(latencies),
                "max_latency": np.max(latencies)
            }
        else:
            return {}
    
    def evaluate_citation_quality(self, evaluation_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Evaluate citation quality and presence"""
        citation_metrics = {
            "total_questions": len(evaluation_data),
            "questions_with_citations": 0,
            "average_citations_per_answer": 0,
            "citation_accuracy": 0.0
        }
        
        total_citations = 0
        accurate_citations = 0
        
        for item in evaluation_data:
            answer = item["answer"]
            
            # Check if answer contains citations (look for [Fonte X] pattern)
            if "[Fonte" in answer or "Fonte" in answer:
                citation_metrics["questions_with_citations"] += 1
                
                # Count citations
                citation_count = answer.count("[Fonte")
                total_citations += citation_count
                
                # Simple accuracy check (if citations are present and answer is not empty)
                if len(answer.strip()) > 50:  # Non-empty answer
                    accurate_citations += 1
        
        if citation_metrics["total_questions"] > 0:
            citation_metrics["questions_with_citations"] = (
                citation_metrics["questions_with_citations"] / citation_metrics["total_questions"]
            )
            citation_metrics["average_citations_per_answer"] = (
                total_citations / citation_metrics["total_questions"]
            )
            citation_metrics["citation_accuracy"] = (
                accurate_citations / citation_metrics["total_questions"]
            )
        
        return citation_metrics
    
    def run_comprehensive_evaluation(self) -> Dict[str, Any]:
        """Run comprehensive evaluation of the system"""
        logger.info("Starting comprehensive evaluation...")
        
        # Create evaluation dataset
        evaluation_data = self.create_evaluation_dataset()
        logger.info(f"Created evaluation dataset with {len(evaluation_data)} questions")
        
        # Run RAGAS evaluation
        ragas_results = self.evaluate_with_ragas(evaluation_data)
        
        # Evaluate latency
        questions = [item["question"] for item in evaluation_data]
        latency_results = self.evaluate_latency(questions)
        
        # Evaluate citation quality
        citation_results = self.evaluate_citation_quality(evaluation_data)
        
        # Compile results
        results = {
            "evaluation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "dataset_size": len(evaluation_data),
            "ragas_metrics": ragas_results,
            "latency_metrics": latency_results,
            "citation_metrics": citation_results,
            "evaluation_data": evaluation_data
        }
        
        # Save results
        results_file = EVALUATION_DIR / f"evaluation_results_{int(time.time())}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Evaluation completed. Results saved to {results_file}")
        return results
    
    def generate_evaluation_report(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable evaluation report"""
        report = f"""
# Relatório de Avaliação - Climate Assistant RAG System

## Resumo Executivo
- **Data da Avaliação**: {results['evaluation_timestamp']}
- **Tamanho do Dataset**: {results['dataset_size']} perguntas
- **Status**: Avaliação Completa

## Métricas RAGAS
"""
        
        if results.get('ragas_metrics'):
            for metric, value in results['ragas_metrics'].items():
                report += f"- **{metric}**: {value:.3f}\n"
        else:
            report += "- Métricas RAGAS não disponíveis\n"
        
        report += f"""
## Métricas de Latência
"""
        
        if results.get('latency_metrics'):
            latency = results['latency_metrics']
            report += f"- **Latência Média**: {latency.get('mean_latency', 0):.2f}s\n"
            report += f"- **Latência Mediana**: {latency.get('median_latency', 0):.2f}s\n"
            report += f"- **Desvio Padrão**: {latency.get('std_latency', 0):.2f}s\n"
        else:
            report += "- Métricas de latência não disponíveis\n"
        
        report += f"""
## Métricas de Citação
"""
        
        if results.get('citation_metrics'):
            citation = results['citation_metrics']
            report += f"- **Perguntas com Citações**: {citation.get('questions_with_citations', 0):.1%}\n"
            report += f"- **Citações Médias por Resposta**: {citation.get('average_citations_per_answer', 0):.1f}\n"
            report += f"- **Precisão das Citações**: {citation.get('citation_accuracy', 0):.1%}\n"
        else:
            report += "- Métricas de citação não disponíveis\n"
        
        report += f"""
## Recomendações

1. **Melhorias de Performance**: 
   - Otimizar latência para respostas mais rápidas
   - Melhorar precisão das citações

2. **Qualidade das Respostas**:
   - Aumentar cobertura de citações
   - Melhorar relevância contextual

3. **Monitoramento Contínuo**:
   - Implementar avaliação automática
   - Monitorar métricas em produção

## Conclusão

O sistema demonstra funcionalidade básica de RAG com agentes, mas requer melhorias
em precisão e latência para uso em produção.
"""
        
        return report

def main():
    """Main function to run evaluation"""
    try:
        # Initialize components
        document_processor = DocumentProcessor()
        if not document_processor.load_vector_store():
            logger.error("Vector store not found. Please run document processing first.")
            return
        
        climate_agents = ClimateAssistantAgents(document_processor)
        
        # Run evaluation
        evaluator = ClimateAssistantEvaluator(document_processor, climate_agents)
        results = evaluator.run_comprehensive_evaluation()
        
        # Generate and save report
        report = evaluator.generate_evaluation_report(results)
        report_file = EVALUATION_DIR / f"evaluation_report_{int(time.time())}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Evaluation report saved to {report_file}")
        print(report)
        
    except Exception as e:
        logger.error(f"Error in evaluation: {str(e)}")

if __name__ == "__main__":
    main()
