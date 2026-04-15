import os
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
import config_data as config
import hashlib
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

def check_md5(md5_str:str):
  if not os.path.exists(config.md5_path):
    open(config.md5_path,'w',encoding='utf-8').close
    return False
  else:
    for line in open(config.md5_path,'r',encoding='utf-8').readlines():
      line = line.strip()
      if line == md5_str:
        return True
    return False

def save_md5(md5_str:str): 
  with open(config.md5_path,'a',encoding='utf-8') as file:
    file.write(md5_str + '\n')

def get_str_md5(input_str:str,encoding='utf-8'): #字符串转MD5
  str_bytes = input_str.encode(encoding=encoding)
  md5_obj = hashlib.md5()
  md5_obj.update(str_bytes)
  md5_hex = md5_obj.hexdigest()
  return md5_hex

class KnowledgeBaseService(object):

  def __init__(self):
    os.makedirs(config.persist_directory,exist_ok=True) #文件夹不存在则创建
    self.chroma = Chroma(
      collection_name=config.collection_name,   #表头名
      embedding_function=DashScopeEmbeddings(model=config.embedding_model_name),
      persist_directory=config.persist_directory #数据库存放文件夹目录
    )  #chroma向量库对象
    self.spliter = RecursiveCharacterTextSplitter(
      chunk_size = config.chunk_size,
      chunk_overlap = config.chunk_overlap,
      separators = config.separators,
      length_function = len
    ) #文本分割器

  def upload_by_str(self,data:str,filename,operator=""):  #将传入字符串向量化，存入数据库
    md5_hex = get_str_md5(data)
    if check_md5(md5_hex):
      return "[跳过]内容已在知识库中"
    
    if len(data)>config.max_split_char_number:
      knowledge_chunks = self.spliter.split_text(data)
    else:
      knowledge_chunks = [data]

    metadata = {
      'source':filename,
      "create_time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      "operator":operator
    }

    self.chroma.add_texts(
      knowledge_chunks,
      metadatas=[metadata for _ in knowledge_chunks]
    )

    save_md5(md5_hex)
    return "[成功]内容已成功载入向量库"

if __name__ == '__main__':

  pass