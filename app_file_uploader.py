import streamlit
import time  # 导入 time 模块
from knowledge_base import KnowledgeBaseService

streamlit.title("知识库更新服务")

if 'service' not in streamlit.session_state:
  streamlit.session_state['service'] = KnowledgeBaseService()

uploader_file = streamlit.file_uploader(
  "请上传 txt 文件",
  type=['txt'],
  accept_multiple_files=False
)
if uploader_file is not None:
  file_name = uploader_file.name
  file_type = uploader_file.type
  file_size_kb = uploader_file.size/1024     #kb

  if file_size_kb < 1024:
    # 不足 1MB，以 KB 显示
    display_size = f"{file_size_kb:.3f} KB"
  else:
    # 超过 1MB，转换为 MB 显示
    file_size_mb = file_size_kb / 1024
    display_size = f"{file_size_mb:.3f} MB"

  streamlit.subheader(f"文件名：{file_name}")
  streamlit.write(f"格式：{file_type} | 大小：{display_size}")
  
  content = uploader_file.getvalue().decode('utf-8')

  service = streamlit.session_state['service']
  
  with streamlit.spinner("载入知识库中..."):
    time.sleep(1)
    res = service.upload_by_str(data=content,filename=file_name)
    streamlit.write(res)