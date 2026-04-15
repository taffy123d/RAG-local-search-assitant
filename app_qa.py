import streamlit
from rag import RagService
from config_data import session_config

streamlit.title('智能客服')
streamlit.divider()

if 'rag' not in streamlit.session_state:
  streamlit.session_state['rag'] = RagService() 
  pass

if 'message' not in streamlit.session_state:
  streamlit.session_state['message'] = [{'role':'assistant','content':'你好，请问有什么可以帮助你的？'}]

prompt = streamlit.chat_input()

for msg in streamlit.session_state['message']:
  streamlit.chat_message(msg['role']).write(msg['content'])
  

if prompt:
  streamlit.chat_message('user').write(prompt)
  
  streamlit.session_state['message'].append({'role':'user','content':prompt})


  with streamlit.spinner('思考中...'):
    ragchat = streamlit.session_state['rag']
    
    response = ragchat.chain.stream({'usrInput':prompt},session_config)

    res_str = streamlit.chat_message('assistant').write_stream(response)

    streamlit.session_state['message'].append({'role':'assistant','content':res_str})



