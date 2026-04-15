import sqlite3
import json
from typing import List
from langchain_core.messages import (
    message_to_dict,
    messages_from_dict,
    BaseMessage
)
from langchain_core.chat_history import BaseChatMessageHistory


class SQLiteChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id: str, db_path: str = "chat_memory.db"):
        """
        初始化 SQLite 聊天历史记录
        :param session_id: 会话 ID (区分不同用户/对话)
        :param db_path: SQLite 数据库文件路径 (默认 chat_memory.db)
        """
        self.session_id = session_id
        self.db_path = db_path
        
        # 1. 连接数据库 (check_same_thread=False 允许在多线程中使用)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        
        # 2. 自动创建表
        self._create_table_if_not_exists()

    def _create_table_if_not_exists(self) -> None:
        """创建数据库表结构"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            message_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        # 给 session_id 加索引，大幅提升查询速度
        create_index_sql = """
        CREATE INDEX IF NOT EXISTS idx_session_id ON chat_history (session_id);
        """
        
        self.conn.execute(create_table_sql)
        self.conn.execute(create_index_sql)
        self.conn.commit()

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """添加新消息到数据库"""
        insert_sql = """
        INSERT INTO chat_history (session_id, message_json)
        VALUES (?, ?);
        """
        
        # 批量插入消息
        for msg in messages:
            msg_dict = message_to_dict(msg)
            # 保存为 JSON 字符串，ensure_ascii=False 保证中文可读
            msg_json = json.dumps(msg_dict, ensure_ascii=False, indent=2)
            self.conn.execute(insert_sql, (self.session_id, msg_json))
        
        self.conn.commit()

    @property
    def messages(self) -> List[BaseMessage]:
        """从数据库读取所有历史消息"""
        select_sql = """
        SELECT message_json FROM chat_history
        WHERE session_id = ?
        ORDER BY id ASC;
        """
        
        cursor = self.conn.execute(select_sql, (self.session_id,))
        rows = cursor.fetchall()
        
        # 将 JSON 字符串还原为 LangChain Message 对象
        messages_data = [json.loads(row[0]) for row in rows]
        return messages_from_dict(messages_data)

    def clear(self) -> None:
        """清空当前会话的所有历史记录"""
        delete_sql = "DELETE FROM chat_history WHERE session_id = ?;"
        self.conn.execute(delete_sql, (self.session_id,))
        self.conn.commit()

    def close(self) -> None:
        """(可选) 手动关闭数据库连接"""
        self.conn.close()

if __name__ == '__main__':
    print('111')