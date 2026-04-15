import os , json

from langchain_core.messages import message_to_dict , messages_from_dict ,BaseMessage
from langchain_core.chat_history import BaseChatMessageHistory



class FileChatMessageHistory(BaseChatMessageHistory):
  def __init__(self,session_id,storage_path):
    self.session_id = session_id
    self.storage_path = storage_path
    #完整文件路径
    self.file_path = os.path.join(self.storage_path,self.session_id)
    os.makedirs(os.path.dirname(self.file_path) , exist_ok=True)  
    
  def add_messages(self, now_msg : list[BaseMessage]) -> None:
    # all_messages = self.messages
    all_messages = list(self.messages)
    all_messages.extend(now_msg) # 融合
    #BaseMessage->json 以字符串写入
    new_messages = []
    for msg in all_messages:
      temp = message_to_dict(msg) 
      new_messages.append(temp)
    with open(self.file_path,'w',encoding='utf-8') as file:
      json.dump(new_messages,file, ensure_ascii=False, indent=2)
    
  @property
  def messages(self) -> list[BaseMessage]:
    try:
      with open(self.file_path, 'r', encoding='utf-8') as file:
        content = file.read().strip() 
                # 空文件直接返回空列表（修复核心！）
        if not content:
                    return []            
        messages_data = json.loads(content)
        return messages_from_dict(messages_data)
    except FileNotFoundError:
      return []
        # 捕获 JSON 错误，坏文件就重置
    except json.JSONDecodeError:
      return []

  def clear(self) -> None:
    with open(self.file_path,'w',encoding='utf-8') as file:
      json.dump([], file, ensure_ascii=False, indent=2)