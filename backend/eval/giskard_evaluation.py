"""
Giskard evaluation module for the Climate Assistant RAG system
"""
import json
import logging
from typing import List, Dict, Any
from pathlib import Path
import pandas as pd

import giskard
from giskard import Dataset, Model, scan, generate_test_suite, Suite
from giskard.models.function import PredictionFunction

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import EVALUATION_DIR
from ingest.document_processor import DocumentProcessor
from src.agents import ClimateAssistantAgents

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClimateAssistantGiskardEvaluator:
    """Giskard-based evaluation system for the Climate Assistant"""
    
    def __init__(self, document_processor: DocumentProcessor, climate_agents: ClimateAssistantAgents):
        self.document_processor = document_processor
        self.climate_agents = climate_agents
        self.manual_questions = self._load_manual_questions()
    
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
    
    def _create_prediction_function(self):
        """Create a prediction function for Giskard"""
        def predict_answers(df: pd.DataFrame) -> List[str]:
            """Prediction function for Giskard"""
            results = []
            for _, row in df.iterrows():
                question = row['question']
                try:
                    result = self.climate_agents.process_query(question)
                    results.append(result['response'])
                except Exception as e:
                    logger.error(f"Error processing question: {str(e)}")
                    results.append("Error processing question")
            return results
        
        return predict_answers
    
    def create_giskard_dataset(self) -> Dataset:
        """Create Giskard dataset from manual questions"""
        if not self.manual_questions:
            raise ValueError("No manual questions loaded")
        
        # Convert to DataFrame
        df_data = []
        for item in self.manual_questions:
            df_data.append({
                'question': item['question'],
                'ground_truth': item['ground_truth'],
                'question_id': item['question_id'],
                'category': item['category'],
                'difficulty': item['difficulty'],
                'expected_citations': item['expected_citations']
            })
        
        df = pd.DataFrame(df_data)
        
        # Create Giskard dataset
        dataset = Dataset(
            df=df,
            name="Climate Assistant Evaluation Dataset",
            target="ground_truth",
            cat_columns=['category', 'difficulty']
        )
        
        logger.info(f"Created Giskard dataset with {len(df)} samples")
        return dataset
    
    def create_giskard_model(self) -> Model:
        """Create Giskard model from the prediction function"""
        prediction_function = self._create_prediction_function()
        
        model = Model(
            model=prediction_function,
            model_type="text_generation",
            name="Climate Assistant RAG Model",
            description="RAG system with LangGraph agents for climate change questions",
            feature_names=['question']
        )
        
        logger.info("Created Giskard model")
        return model
    
    def run_giskard_scan(self, dataset: Dataset, model: Model) -> Dict[str, Any]:
        """Run Giskard scan to identify potential issues"""
        try:
            logger.info("Running Giskard scan...")
            
            # Run the scan
            scan_results = scan(model, dataset)
            
            # Convert results to dictionary
            results = {
                "scan_summary": {
                    "total_issues": len(scan_results),
                    "critical_issues": len([r for r in scan_results if r.level == "error"]),
                    "warnings": len([r for r in scan_results if r.level == "warning"]),
                    "info": len([r for r in scan_results if r.level == "info"])
                },
                "issues": []
            }
            
            for issue in scan_results:
                results["issues"].append({
                    "type": issue.__class__.__name__,
                    "level": issue.level,
                    "description": str(issue),
                    "metric": getattr(issue, 'metric', None)
                })
            
            logger.info(f"Giskard scan completed. Found {len(scan_results)} issues")
            return results
            
        except Exception as e:
            logger.error(f"Error in Giskard scan: {str(e)}")
            return {"error": str(e)}
    
    def generate_test_suite(self, dataset: Dataset, model: Model) -> Suite:
        """Generate test suite for the model"""
        try:
            logger.info("Generating Giskard test suite...")
            
            # Generate test suite
            test_suite = generate_test_suite(model, dataset)
            
            logger.info(f"Generated test suite with {len(test_suite.tests)} tests")
            return test_suite
            
        except Exception as e:
            logger.error(f"Error generating test suite: {str(e)}")
            return None
    
    def run_comprehensive_giskard_evaluation(self) -> Dict[str, Any]:
        """Run comprehensive Giskard evaluation"""
        logger.info("Starting comprehensive Giskard evaluation...")
        
        try:
            # Create dataset and model
            dataset = self.create_giskard_dataset()
            model = self.create_giskard_model()
            
            # Run scan
            scan_results = self.run_giskard_scan(dataset, model)
            
            # Generate test suite
            test_suite = self.generate_test_suite(dataset, model)
            
            # Run tests if suite was created
            test_results = {}
            if test_suite:
                try:
                    test_results = test_suite.run(model, dataset)
                    logger.info(f"Test suite executed with {len(test_results)} results")
                except Exception as e:
                    logger.error(f"Error running test suite: {str(e)}")
                    test_results = {"error": str(e)}
            
            # Compile results
            results = {
                "evaluation_type": "giskard",
                "dataset_size": len(self.manual_questions),
                "scan_results": scan_results,
                "test_results": test_results,
                "model_info": {
                    "name": model.name,
                    "type": model.model_type,
                    "description": model.description
                }
            }
            
            # Save results
            results_file = EVALUATION_DIR / f"giskard_evaluation_results_{int(time.time())}.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Giskard evaluation completed. Results saved to {results_file}")
            return results
            
        except Exception as e:
            logger.error(f"Error in comprehensive Giskard evaluation: {str(e)}")
            return {"error": str(e)}
    
    def generate_giskard_report(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable Giskard evaluation report"""
        report = f"""
# Relatório de Avaliação Giskard - Climate Assistant RAG System

## Resumo Executivo
- **Tipo de Avaliação**: Giskard AI Quality Scan
- **Tamanho do Dataset**: {results.get('dataset_size', 0)} perguntas
- **Status**: Avaliação Completa

## Resultados do Scan
"""
        
        if 'scan_results' in results and 'scan_summary' in results['scan_results']:
            summary = results['scan_results']['scan_summary']
            report += f"""
- **Total de Problemas**: {summary.get('total_issues', 0)}
- **Problemas Críticos**: {summary.get('critical_issues', 0)}
- **Avisos**: {summary.get('warnings', 0)}
- **Informações**: {summary.get('info', 0)}
"""
        else:
            report += "- Resultados do scan não disponíveis\n"
        
        report += f"""
## Detalhes dos Problemas Encontrados
"""
        
        if 'scan_results' in results and 'issues' in results['scan_results']:
            issues = results['scan_results']['issues']
            for issue in issues[:10]:  # Show first 10 issues
                report += f"""
### {issue.get('type', 'Unknown')} ({issue.get('level', 'unknown')})
- **Descrição**: {issue.get('description', 'No description')}
- **Métrica**: {issue.get('metric', 'N/A')}
"""
        else:
            report += "- Detalhes dos problemas não disponíveis\n"
        
        report += f"""
## Resultados dos Testes
"""
        
        if 'test_results' in results and results['test_results']:
            if 'error' in results['test_results']:
                report += f"- **Erro nos Testes**: {results['test_results']['error']}\n"
            else:
                report += f"- **Testes Executados**: {len(results['test_results'])}\n"
        else:
            report += "- Resultados dos testes não disponíveis\n"
        
        report += f"""
## Recomendações

1. **Qualidade do Modelo**: 
   - Revisar problemas críticos identificados pelo scan
   - Implementar melhorias baseadas nos avisos

2. **Robustez**: 
   - Executar testes regularmente
   - Monitorar performance em produção

3. **Transparência**: 
   - Documentar limitações identificadas
   - Implementar controles de qualidade

## Conclusão

O sistema foi avaliado usando Giskard para identificar potenciais problemas de qualidade,
robustez e transparência. Os resultados devem ser usados para melhorar a confiabilidade
do sistema.
"""
        
        return report

def main():
    """Main function to run Giskard evaluation"""
    import time
    
    try:
        # Initialize components
        document_processor = DocumentProcessor()
        if not document_processor.load_vector_store():
            logger.error("Vector store not found. Please run document processing first.")
            return
        
        climate_agents = ClimateAssistantAgents(document_processor)
        
        # Run Giskard evaluation
        evaluator = ClimateAssistantGiskardEvaluator(document_processor, climate_agents)
        results = evaluator.run_comprehensive_giskard_evaluation()
        
        # Generate and save report
        report = evaluator.generate_giskard_report(results)
        report_file = EVALUATION_DIR / f"giskard_report_{int(time.time())}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Giskard report saved to {report_file}")
        print(report)
        
    except Exception as e:
        logger.error(f"Error in Giskard evaluation: {str(e)}")

if __name__ == "__main__":
    main()

