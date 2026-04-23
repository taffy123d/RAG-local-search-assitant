# RAG 智能客服系统

一个基于 **RAG（Retrieval-Augmented Generation，检索增强生成）** 的智能客服问答系统。支持通过上传 TXT 文档构建知识库，并结合大语言模型实现带有多轮对话记忆的智能问答。

---

## ✨ 功能特性

- **📚 知识库管理**：上传 TXT 文本文件，自动分割、去重并向量化存储到 Chroma 向量库
- **💬 智能问答**：基于用户问题检索相关知识，结合大语言模型生成专业、简洁的回答
- **🧠 多轮对话**：支持 SQLite 持久化的对话历史记忆
- **🔄 历史会话**：侧边栏展示所有历史会话，点击即可切换并继续对话
- **⚡ 流式输出**：AI 回答实时逐字显示，带有加载动画

---

## 🛠 技术栈

| 层级 | 技术 |
|------|------|
| **后端框架** | [FastAPI](https://fastapi.tiangolo.com/) |
| **前端界面** | 原生 HTML / CSS / JavaScript |
| **实时通信** | WebSocket |
| **RAG 框架** | [LangChain](https://www.langchain.com/) |
| **向量数据库** | [Chroma](https://www.trychroma.com/) |
| **Embedding 模型** | [DashScope](https://help.aliyun.com/zh/dashscope/) `text-embedding-v4` |
| **大语言模型** | [DeepSeek](https://www.deepseek.com/) `deepseek-reasoner` |
| **对话历史存储** | SQLite |
| **Python 版本** | >= 3.13 |
| **包管理** | [uv](https://docs.astral.sh/uv/) |

---

## 📁 项目结构

```
.
├── main.py                   # FastAPI 后端入口（API + WebSocket + 静态文件）
├── rag.py                    # RAG 核心服务（检索 + LLM + 对话链）
├── knowledge_base.py         # 知识库服务（文本分割、去重、向量存储）
├── vector_stores.py          # Chroma 向量库封装
├── config_data.py            # 项目配置文件
├── sqlite_history_store.py   # SQLite 对话历史存储
├── file_history_store.py     # 文件形式对话历史存储（备用）
├── pyproject.toml            # 依赖与项目元数据
├── static/                   # 前端静态资源
│   ├── index.html            # 智能客服问答页
│   ├── upload.html           # 知识库上传页
│   ├── css/style.css         # 共享样式
│   ├── js/chat.js            # 问答页逻辑
│   └── js/upload.js          # 上传页逻辑
├── chroma_db/                # Chroma 向量数据库持久化目录
├── chat_history/             # 对话历史存储目录
└── data/                     # 可放置待上传的原始数据文件
```

---

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/taffy123d/RAG-local-search-assitant
cd <项目目录>
```

### 2. 安装依赖

本项目使用 `uv` 进行包管理，若未安装 uv，请先安装：

```bash
# Windows
pip install uv
```

然后安装项目依赖：

```bash
uv sync
```

### 3. 配置环境变量

在项目根目录创建 `.env` 文件，填入你的 API Key：

```env
DASHSCOPE_API_KEY=your_dashscope_api_key_here

DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

> 💡 **获取 API Key**
> - DashScope API Key：[阿里云百炼控制台](https://bailian.console.aliyun.com/)
> - DeepSeek API Key：[DeepSeek 开放平台](https://platform.deepseek.com/)

### 4. 启动应用

```bash
uv run uvicorn main:app --reload --port 8000
```

服务启动后，在浏览器打开：

- **智能客服问答页**：`http://localhost:8000/`
- **知识库上传页**：`http://localhost:8000/upload`

---

## 📖 使用说明

### 上传知识库

1. 打开 `http://localhost:8000/upload`
2. 点击选择或拖拽 `.txt` 格式的文本文件到上传区域
3. 系统会自动：
   - 计算 MD5 进行去重（避免重复上传相同内容）
   - 按配置的分块策略分割文本
   - 调用 Embedding 模型生成向量
   - 存入 Chroma 向量库

### 智能问答

1. 打开 `http://localhost:8000/`
2. 在底部输入框输入问题，按 **Enter** 发送（**Shift + Enter** 换行）
3. 系统会：
   - 从 Chroma 中检索与问题最相关的知识片段
   - 将检索结果作为上下文注入 Prompt
   - 调用 DeepSeek 大模型生成回答
   - 自动维护多轮对话历史

### 切换历史会话

- 左侧边栏「历史会话」区域会列出所有有聊天记录的会话
- 点击任意会话即可切换，自动加载该会话的全部历史消息
- 点击「新建会话」可开始一个全新的对话

---

## 🔌 后端 API

| 方法 | 路径 | 说明 |
|------|------|------|
| `WebSocket` | `/ws/chat/{session_id}` | 流式问答 |
| `POST` | `/api/upload` | 上传 TXT 文件到知识库 |
| `GET` | `/api/sessions` | 获取所有历史会话列表 |
| `GET` | `/api/history/{session_id}` | 获取指定会话的历史消息 |
| `DELETE` | `/api/history/{session_id}` | 清空指定会话的历史记录 |

---

## ⚙️ 核心配置

配置项位于 `config_data.py`，可根据需要调整：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `collection_name` | `rag` | Chroma 集合名称 |
| `persist_directory` | `./chroma_db` | 向量库持久化目录 |
| `chunk_size` | `1000` | 文本分块大小 |
| `chunk_overlap` | `100` | 分块重叠长度 |
| `embedding_model_name` | `text-embedding-v4` | DashScope Embedding 模型 |
| `chat_model_name` | `deepseek-reasoner` | 对话大模型名称 |
| `search_kwargs` | `1` | 检索返回的文档片段数量 |
