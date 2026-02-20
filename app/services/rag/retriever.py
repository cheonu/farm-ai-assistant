class Retriever:
    def __init__(self, embedder, vector_store):
        self.embedder = embedder
        self.vector_store = vector_store

    def retrieve (self, query):
      query_embeddings = self.embedder.embed([query])[0]
      results = self.vector_store.query(query_embeddings)
      return results
