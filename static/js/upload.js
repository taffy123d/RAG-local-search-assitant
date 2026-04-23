const fileInput = document.getElementById('file-input');
const fileInfo = document.getElementById('file-info');
const fileName = document.getElementById('file-name');
const fileSize = document.getElementById('file-size');
const uploadArea = document.getElementById('upload-area');
const resultDiv = document.getElementById('upload-result');

let selectedFile = null;

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        selectedFile = e.target.files[0];
        showFileInfo(selectedFile);
    }
});

function showFileInfo(file) {
    fileName.textContent = file.name;
    const size = file.size < 1024 * 1024
        ? (file.size / 1024).toFixed(2) + ' KB'
        : (file.size / (1024 * 1024)).toFixed(2) + ' MB';
    fileSize.textContent = size;
    fileInfo.style.display = 'block';
    resultDiv.style.display = 'none';
    resultDiv.className = 'upload-result';
}

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
        selectedFile = e.dataTransfer.files[0];
        if (!selectedFile.name.endsWith('.txt')) {
            showResult('仅支持 .txt 文件', 'error');
            return;
        }
        showFileInfo(selectedFile);
    }
});

async function uploadFile() {
    if (!selectedFile) return;

    const btn = document.querySelector('.upload-btn');
    const originalText = btn.textContent;
    btn.innerHTML = '<span class="spinner"></span>上传中...';
    btn.disabled = true;

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (response.ok) {
            showResult(data.result, 'success');
        } else {
            showResult(data.detail || '上传失败', 'error');
        }
    } catch (err) {
        showResult('网络错误: ' + err.message, 'error');
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

function showResult(msg, type) {
    resultDiv.textContent = msg;
    resultDiv.className = 'upload-result ' + type;
    resultDiv.style.display = 'block';
}
