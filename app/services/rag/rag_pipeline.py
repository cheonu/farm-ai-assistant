class RAGPipeline:
    def __init__(self, retriever):
        self.retriever = retriever
    
    def run(self, question):
        context = self.retriever.retrieve(question)
        # send context + question to LLM
        return context
