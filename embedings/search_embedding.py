import numpy as np
from embedings.sentence_embeddings import Embeddings
from app.db_vector.db import get_conn


text = "có bao nhiêu phòng thí nghiệm"
db_url = "postgresql://haonguyen:matkhau@localhost:5432/postgres"

conn = get_conn(db_url)


embedder = Embeddings()
embedding = embedder.encode(text)

# retrieve document
result = conn.execute(
    'SELECT content FROM document ORDER BY embedding <-> %s LIMIT 3',
    (np.array(embedding),)
).fetchall()

context = '\n\n'.join([row[0] for row in result])
print(context)