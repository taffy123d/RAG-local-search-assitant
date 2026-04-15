import os
from dotenv import load_dotenv
load_dotenv()

from vector_stores import VectorStoreService
from langchain_community.embeddings import DashScopeEmbeddings
import config_data as config
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnablePassthrough,RunnableLambda
from langchain_core.documents import Document  
from langchain_core.output_parsers import StrOutputParser

from langchain_core.runnables import RunnableWithMessageHistory
from operator import itemgetter

# import langchain
# langchain.debug = True

from file_history_store import FileChatMessageHistory

def get_history(session_id):
  return FileChatMessageHistory(session_id,config.file_chat_history)

from sqlite_history_store import SQLiteChatMessageHistory
def get_db_history(session_id:str) -> SQLiteChatMessageHistory:
  return SQLiteChatMessageHistory(
    session_id=session_id,
    db_path=config.sqlite_chat_history
  )

class RagService(object):
  def __init__(self):
    self.vector_service = VectorStoreService(config.embedding_model_name)
    self.prompt_template = ChatPromptTemplate.from_messages([
      ('system','以我提供的已知参考资料为主，简洁专业的回答用户问题。参考资料\n{context}'),
      MessagesPlaceholder('history'),
      ('human','{usrInput}')
    ])
    self.chat_model = init_chat_model(config.chat_model_name)
    self.chain = self.__get_chain()

  def __get_chain(self):
    retriever = self.vector_service.get_retriever()
    
    def get_str_re(docs:list[Document]) -> str:
      if not docs:
        return '无相关参考资料'
      res = '[\n'
      i = 1
      for doc in docs:
        res = res+f'{i}: {doc.page_content}\n'
        i+=1
      res += ']'  
      return res
    
    chain = (
        RunnablePassthrough.assign(   #assign 只能处理字典类型的输入,输出新增一个'context'的键值对
            context = (lambda x: x["usrInput"]) | retriever | get_str_re          #注意括号
        )
        | self.prompt_template
        | self.chat_model
        | StrOutputParser()
    )

    #RunnableWithMessageHistory :
    #接受输入<dict>，输出在原输入<dict>的基础上新增键值对'history'(history_messages_key)
    conversation_chain = RunnableWithMessageHistory(
      chain,
      get_session_history=get_db_history,
      input_messages_key='usrInput',
      history_messages_key='history'
    )

    return conversation_chain

#调用演示
if __name__ == '__main__':

  s1ession_id = 'user_001'
  session_config = {
    'configurable':{
      'session_id':s1ession_id
    }
  }

  text = '身高170cm尺码推荐'

  res = RagService().chain.invoke(
    {'usrInput':text},
    session_config
    )
  print(res)
  pass