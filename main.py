import json
import asyncio
import sqlite3
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import config_data as config
from rag import RagService
from knowledge_base import KnowledgeBaseService
from sqlite_history_store import SQLiteChatMessageHistory

app = FastAPI(title="RAG 智能客服系统")

rag_service = RagService()
kb_service = KnowledgeBaseService()


@app.websocket("/ws/chat/{session_id}")
async def chat_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            user_input = msg.get("message", "")

            session_conf = {"configurable": {"session_id": session_id}}

            def stream_response():
                return rag_service.chain.stream({"usrInput": user_input}, session_conf)

            loop = asyncio.get_event_loop()
            iterator = await loop.run_in_executor(None, stream_response)

            for chunk in iterator:
                await websocket.send_text(json.dumps({"chunk": chunk}))

            await websocket.send_text(json.dumps({"done": True}))
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({"error": str(e)}))
        except Exception:
            pass


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="仅支持 txt 文件")

    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="文件编码错误，请使用 UTF-8 编码")

    def do_upload():
        return kb_service.upload_by_str(data=text, filename=file.filename)

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, do_upload)

    return {"result": result}


@app.get("/api/sessions")
async def get_sessions():
    conn = sqlite3.connect(config.sqlite_chat_history, check_same_thread=False)
    cursor = conn.execute(
        "SELECT session_id FROM (SELECT session_id, MAX(id) as max_id FROM chat_history GROUP BY session_id) ORDER BY max_id DESC"
    )
    sessions = [row[0] for row in cursor.fetchall()]
    conn.close()
    return {"sessions": sessions}


@app.get("/api/history/{session_id}")
async def get_history(session_id: str):
    history = SQLiteChatMessageHistory(session_id, config.sqlite_chat_history)
    messages = []
    for msg in history.messages:
        msg_type = (
            "user"
            if msg.type == "human"
            else "assistant" if msg.type == "ai" else msg.type
        )
        messages.append({"type": msg_type, "content": msg.content})
    history.close()
    return {"session_id": session_id, "messages": messages}


@app.delete("/api/history/{session_id}")
async def clear_history(session_id: str):
    history = SQLiteChatMessageHistory(session_id, config.sqlite_chat_history)
    history.clear()
    history.close()
    return {"result": "历史记录已清空"}


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.get("/upload")
async def upload_page():
    return FileResponse("static/upload.html")
