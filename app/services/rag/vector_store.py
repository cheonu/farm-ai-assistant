import chromadb

class VectorStore:
    def __init__(self, path):
        self.client = chromadb.PersistentClient(path=".chroma")
        self.collection = self.client.create_collection(name="farm_docs")
    
    def add_document(self, ids,documents,embeddings):
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings
        )
    
    def query(self, ids, query_embeddings,n_results=3):
        return self.collection.query(
            query_embeddings=[query_embeddings],
            n_results=n_results
        )

