import time
from typing import List, Tuple, Dict
from service.hybridsearch import hybrid_search, reranke_context


class RetrievalEvaluator:
    """Simple evaluation metrics for retrieval system"""
    
    def measure_retrieval_time(self, query: str, top_k: int = 5) -> Dict:
        """Measure time taken for retrieval and reranking"""
        start_time = time.time()
        
        retrieved_docs = hybrid_search(query, top_k=top_k)
        reranked_docs = reranke_context(query, retrieved_docs, top_k=3)
        
        total_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Calculate metrics
        relevance_scores = {}
        if reranked_docs:
            scores = [doc[1] for doc in reranked_docs]
            relevance_scores = {
                'avg_relevance': round(sum(scores) / len(scores), 4),
                'max_relevance': round(max(scores), 4),
                'min_relevance': round(min(scores), 4)
            }
        
        return {
            'reranked_docs': reranked_docs,
            'total_time_ms': round(total_time, 2),
            'relevance_scores': relevance_scores
        }
    
    def reset(self):
        """Reset evaluator"""
        pass


evaluator = RetrievalEvaluator()
