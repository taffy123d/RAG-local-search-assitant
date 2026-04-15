from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings



import config_data as config

class VectorStoreService(object):
  def __init__(self,embedding):

    self.embedding = DashScopeEmbeddings(model=config.embedding_model_name)

    self.vector_store = Chroma(
      collection_name=config.collection_name,
      embedding_function=self.embedding,
      persist_directory=config.persist_directory
    )
    
  def get_retriever(self):
    return self.vector_store.as_retriever(search_kwargs={'k':config.search_kwargs})

