from sentence_transformers import SentenceTransformer

class EmbeddingModel:
    def __init__(self,model_name):
        self.model = SentenceTransformer(model_name)

    def embed(self, sentences):
        return self.model.encode(sentences)