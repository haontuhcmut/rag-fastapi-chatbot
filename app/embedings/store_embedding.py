from pathlib import Path

from app.embedings.chunks import Chunks
from app.embedings.sentence_embeddings import Embeddings
from app.db_vector.db import get_conn

def store_embeddings(chunks_loader, embedder, db_url):
    conn = get_conn(db_url)
    try:
        with conn.cursor() as cur:
            for chunks in chunks_loader.process_documents():
                for i, chunk in enumerate(chunks):
                    # Generate embedding
                    vector = embedder.encode(chunk)
                    print(f"Chunk {i+1} embedding (first 5 values): {vector[:5]}")

                    # Insert into database
                    cur.execute(
                        "INSERT INTO chunks (content, embedding) VALUES (%s, %s)",
                        (chunk, vector),
                    )
                print(f"Inserted {len(chunks)} chunks into database.")
    except Exception as e:
        print(f"Error storing embeddings: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        # Database URL
        DB_URL = "postgresql://haonguyen:matkhau@localhost:5432/postgres"

        # Initialize chunks and embeddings
        CURRENT_DIR = Path(__file__).resolve().parent
        DOCUMENTS_DIR = CURRENT_DIR.parent.parent / "document"
        file_path = DOCUMENTS_DIR / "data.docx"

        if not file_path.exists():
            raise FileNotFoundError(f"Document not found at {file_path}")

        chunks_loader = Chunks(file_path=str(file_path))
        embedder = Embeddings()

        # Store embeddings in database
        store_embeddings(chunks_loader, embedder, DB_URL)

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")