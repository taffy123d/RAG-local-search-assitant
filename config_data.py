#md5_tool
md5_path = './md5.text'

#Chroma
collection_name='rag'     #表名
persist_directory = './chroma_db'

#RecursiveCharacterTextSplitter
chunk_size = 1000
chunk_overlap = 100
separators = ["\n\n","\n","。","！","？",".","!","?"," ",""]
max_split_char_number = 1000 #文本分割阈值

#retriever
search_kwargs = 1

embedding_model_name = 'text-embedding-v4'
chat_model_name = 'deepseek-reasoner'

file_chat_history = './chat_history'
sqlite_chat_history = './chat_history/chat_history.db'

session_config = {
    'configurable':{
      'session_id':'user_001'
    }
  }