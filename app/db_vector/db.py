from pgvector.psycopg import register_vector
import psycopg


def get_conn(url):
    conn = psycopg.connect(url, autocommit=True)
    register_vector(conn)
    return conn


def init_db(url):
    conn = get_conn(url)
    try:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute("DROP TABLE IF EXISTS chunks")
            cur.execute(
                "CREATE TABLE chunks (id bigserial PRIMARY KEY, content text, embedding vector(384))"
            )
            print("Database initialized successfully.")
    except Exception as e:
        print("Error initializing database:", e)
    finally:
        conn.close()


if __name__ == "__main__":
    init_db(url = "postgresql://haonguyen:matkhau@localhost:5432/postgres")
