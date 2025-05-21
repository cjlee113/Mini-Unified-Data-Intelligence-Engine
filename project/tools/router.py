from project.retrievers.sql import SQLRetriever
from project.retrievers.vector import VectorRetriever

class Router:
    def __init__(self, sql_retriever, vector_retriever):
        self.sql_retriever = sql_retriever
        self.vector_retriever = vector_retriever

    def search(self, query, top_k=3):
        structured = self.sql_retriever.search(query, top_k=top_k)
        semantic = self.vector_retriever.search(query, top_k=top_k)
        return {
            "structured": structured,
            "semantic": semantic
        } 