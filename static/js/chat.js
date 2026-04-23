let ws = null;
let currentSessionId = localStorage.getItem('session_id') || generateSessionId();
let isGenerating = false;

document.getElementById('session-id').textContent = currentSessionId;

function generateSessionId() {
    const id = 'user_' + Date.now();
    localStorage.setItem('session_id', id);
    return id;
}

function newChat() {
    currentSessionId = generateSessionId();
    document.getElementById('session-id').textContent = currentSessionId;
    document.getElementById('chat-messages').innerHTML = '';
    addMessage('assistant', '你好，请问有什么可以帮助你的？');
    updateActiveHistoryItem();
    connectWebSocket();
}

function connectWebSocket() {
    if (ws) {
        ws.close();
    }
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${window.location.host}/ws/chat/${currentSessionId}`);

    ws.onopen = () => {
        console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.chunk !== undefined) {
            appendToLastMessage(data.chunk);
        } else if (data.done) {
            finishGeneration();
            loadHistorySessions(); // 刷新历史列表
        } else if (data.error) {
            appendToLastMessage('\n[错误: ' + data.error + ']');
            finishGeneration();
        }
    };

    ws.onclose = () => {
        console.log('WebSocket disconnected');
    };

    ws.onerror = (err) => {
        console.error('WebSocket error:', err);
    };
}

function finishGeneration() {
    isGenerating = false;
    document.getElementById('send-btn').disabled = false;
    document.getElementById('user-input').disabled = false;
    document.getElementById('user-input').focus();
}

function addMessage(role, content, isLoading = false) {
    const container = document.getElementById('chat-messages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🤖';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    if (isLoading) {
        contentDiv.innerHTML = '<div class="loading-dots"><span></span><span></span><span></span></div>';
    } else {
        contentDiv.textContent = content;
    }

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(contentDiv);
    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}

function appendToLastMessage(text) {
    const container = document.getElementById('chat-messages');
    const lastMsg = container.lastElementChild;
    if (lastMsg && lastMsg.classList.contains('assistant')) {
        const contentDiv = lastMsg.querySelector('.message-content');
        // 首次收到内容，移除 loading 动画
        if (contentDiv.querySelector('.loading-dots')) {
            contentDiv.textContent = text;
        } else {
            contentDiv.textContent += text;
        }
        container.scrollTop = container.scrollHeight;
    }
}

function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    if (!message || isGenerating) return;

    if (!ws || ws.readyState !== WebSocket.OPEN) {
        alert('连接断开，请刷新页面重试');
        return;
    }

    addMessage('user', message);
    addMessage('assistant', '', true);

    input.value = '';
    input.style.height = 'auto';
    isGenerating = true;
    document.getElementById('send-btn').disabled = true;
    input.disabled = true;

    ws.send(JSON.stringify({ message: message }));
}

async function loadHistorySessions() {
    try {
        const res = await fetch('/api/sessions');
        const data = await res.json();
        renderHistoryList(data.sessions || []);
    } catch (e) {
        console.error('加载历史会话失败:', e);
    }
}

function renderHistoryList(sessions) {
    const container = document.getElementById('history-items');
    container.innerHTML = '';
    sessions.forEach(sessionId => {
        const item = document.createElement('div');
        item.className = 'history-item' + (sessionId === currentSessionId ? ' active' : '');
        item.textContent = sessionId;
        item.title = sessionId;
        item.onclick = () => switchSession(sessionId);
        container.appendChild(item);
    });
}

function updateActiveHistoryItem() {
    document.querySelectorAll('.history-item').forEach(el => {
        el.classList.toggle('active', el.textContent === currentSessionId);
    });
}

async function switchSession(sessionId) {
    currentSessionId = sessionId;
    localStorage.setItem('session_id', sessionId);
    document.getElementById('session-id').textContent = sessionId;
    updateActiveHistoryItem();

    // 清空消息区并加载历史
    document.getElementById('chat-messages').innerHTML = '';
    await loadSessionHistory(sessionId);

    // 重连 WebSocket
    connectWebSocket();
}

async function loadSessionHistory(sessionId) {
    try {
        const res = await fetch(`/api/history/${sessionId}`);
        const data = await res.json();
        if (data.messages && data.messages.length > 0) {
            data.messages.forEach(msg => {
                addMessage(msg.type, msg.content);
            });
        } else {
            addMessage('assistant', '你好，请问有什么可以帮助你的？');
        }
    } catch (e) {
        console.error('加载会话历史失败:', e);
        addMessage('assistant', '你好，请问有什么可以帮助你的？');
    }
}

document.getElementById('user-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

document.getElementById('user-input').addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
});

// 初始化
loadHistorySessions();
connectWebSocket();

// 如果有当前会话的历史记录，加载它；否则显示欢迎语
(async function init() {
    const res = await fetch(`/api/history/${currentSessionId}`);
    const data = await res.json();
    if (data.messages && data.messages.length > 0) {
        data.messages.forEach(msg => {
            addMessage(msg.type, msg.content);
        });
    } else {
        addMessage('assistant', '你好，请问有什么可以帮助你的？');
    }
})();
