
from service.evaluation import evaluator


def run_evaluation():
    
    test_queries = [
        "Product: Web Portal\n\nCategory: Account Suspension\n\nIssue Description: User account was suspended due to suspicious activity",
        "Product: Mobile App\n\nCategory: Performance Issue\n\nIssue Description: App is slow and crashes frequently",
        "Product: Web Portal\n\nCategory: Login Issue\n\nIssue Description: Cannot login with email and password",
    ]
    
    print("Starting Retrieval Evaluation...")
    
    for i, query in enumerate(test_queries, 1):
        result = evaluator.measure_retrieval_time(query)
        print(f"Query {i}: {result['total_time_ms']} ms, Avg Score: {result['relevance_scores'].get('avg_relevance', 'N/A')}")


def evaluate_single_query(query: str):
    result = evaluator.measure_retrieval_time(query)
    
    print(f"Retrieval Time: {result['total_time_ms']} ms")
    if result['relevance_scores']:
        print(f"Avg Relevance: {result['relevance_scores']['avg_relevance']}")
    
    print("\nTop Documents:")
    for i, (doc, score) in enumerate(result['reranked_docs'], 1):
        print(f"{i}. [Score: {score:.4f}] {doc[:80]}...")


if __name__ == "__main__":
    # Run batch evaluation
    run_evaluation()
    
    # Run single query evaluation

    print("Single Query Evaluation:")
    single_query = "Product: Web Portal\n\nCategory: Payment Issue\n\nIssue Description: Payment failed during checkout"
    evaluate_single_query(single_query)
