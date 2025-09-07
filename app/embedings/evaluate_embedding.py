from app.embedings.chunks import Chunks
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
from app.embedings.sentence_embeddings import Embeddings
from app.db_vector.db import get_conn
import numpy as np

def semantic_search(query: str, _chunks_loader: Chunks, embedder: Embeddings, db_url: str, top_k: int = 5):
    # Generate query embedding
    embedding = embedder.encode(query)
    if len(embedding) != 384:
        print(f"Error: Query embedding has incorrect dimension: {len(embedding)}")
        return []

    # Query database
    conn = get_conn(db_url)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT content, embedding <=> %s AS distance FROM chunks ORDER BY distance LIMIT %s",
                (np.array(embedding), top_k)
            )
            results = cur.fetchall()
            if not results:
                print("No results found in database. Check if 'chunks' table is populated.")
                return []
            # Format results as similarity (1 - distance)
            formatted_results = [
                {"text": content, "score": 1 - distance} for content, distance in results
            ]
            return formatted_results
    except Exception as e:
        print(f"Error during semantic search: {e}")
        return []
    finally:
        conn.close()

def evaluate_embeddings(embedder: Embeddings):
    # Test sentences in Vietnamese (similar and dissimilar pairs)
    test_sentences = [
        "Tôi muốn gửi mẫu đến trung tâm 3 để phân tích.",  # Similar to query
        "Trung tâm 3 cung cấp dịch vụ phân tích mẫu chất lượng cao.",  # Similar
        "Thời tiết hôm nay rất đẹp và nắng ấm.",  # Dissimilar
    ]
    embeddings = embedder.encode(test_sentences)

    # Compute cosine similarities
    sim_1_2 = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    sim_1_3 = cosine_similarity([embeddings[0]], [embeddings[2]])[0][0]

    print(f"Similarity (Similar sentences, should be high): {sim_1_2:.4f}")
    print(f"Similarity (Dissimilar sentences, should be low): {sim_1_3:.4f}")

    # Simple evaluation
    if sim_1_2 > sim_1_3:
        print("Embedding evaluation: PASS (similar sentences have higher similarity)")
    else:
        print(
            "Embedding evaluation: FAIL (dissimilar sentences have higher similarity)"
        )


def evaluate_semantic_search(chunks_loader: Chunks, embedder: Embeddings, db_url: str):
    # Test queries with expected relevant content
    test_cases = [
        {
            "query": "Tôi muốn thực hiện thanh toán",
            "expected_content_contains": ["tại các điểm giao dịch của QUATEST3", "118000004544"],
        },
        {
            "query": "Máy học và trí tuệ nhân tạo",
            "expected_content_contains": ["máy học", "trí tuệ nhân tạo"],
        },
    ]

    for test in test_cases:
        query = test["query"]
        expected = test["expected_content_contains"]
        results = semantic_search(query, chunks_loader, embedder, db_url, top_k=3)

        print(f"\nEvaluating query: {query}")
        if not results:
            print("No results returned. Check database or query.")
            continue

        # Check if results contain expected terms
        relevant_results = 0
        for result in results:
            if any(term.lower() in result["text"].lower() for term in expected):
                relevant_results += 1
                print(
                    f"Relevant result: {result['text'][:100]}... (Score: {result['score']:.4f})"
                )

        precision = relevant_results / len(results) if results else 0
        print(f"Precision@3: {precision:.4f}")

if __name__ == "__main__":
    try:
        # Initialize
        CURRENT_DIR = Path(__file__).resolve().parent
        DOCUMENTS_DIR = CURRENT_DIR.parent.parent / "document"
        file_path = DOCUMENTS_DIR / "data.docx"
        db_url = "postgresql://haonguyen:matkhau@localhost:5432/postgres"

        if not file_path.exists():
            raise FileNotFoundError(f"Document not found at {file_path}")

        chunks_loader = Chunks(file_path=str(file_path))
        embedder = Embeddings()

        # Evaluate embeddings
        print("\nEvaluating embedding quality:")
        evaluate_embeddings(embedder)

        # Evaluate semantic search
        print("\nEvaluating semantic search performance:")
        evaluate_semantic_search(chunks_loader, embedder, db_url)

        # Perform semantic search
        query = "Tôi muốn gửi mẫu đến trung tâm 3"
        results = semantic_search(query, chunks_loader, embedder, db_url, top_k=3)

        # Print results
        print(f"\nQuery: {query}")
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Text: {result['text'][:100]}...")
            print(f"Similarity Score: {result['score']:.4f}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")