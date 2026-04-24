from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from contextlib import asynccontextmanager
from typing import Optional
import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta

from models import ChatRequest, ChatResponse, ChatHistoryRequest, ChatMessage
from model_service import ModelService
from config import config
from logger_config import setup_logging

logger = setup_logging(config.LOG_LEVEL)

rate_limit_store = defaultdict(list)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("启动服务...")
    try:
        model_service = ModelService()
        logger.info(f"模型服务初始化成功，设备: {model_service.get_device()}")
    except Exception as e:
        logger.error(f"模型服务初始化失败: {e}")
        raise
    
    yield
    
    logger.info("关闭服务...")


app = FastAPI(
    title="V-FLO大模型平台",
    description="基于 Qwen3-VL-4B-Instruct 模型的推理服务，支持文本和图像输入",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def verify_api_key(api_key: Optional[str] = Depends(api_key_header)):
    if config.API_KEY is not None and api_key != config.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的API密钥"
        )
    return api_key


async def rate_limit(request: Request):
    client_ip = request.client.host
    current_time = time.time()
    
    rate_limit_store[client_ip] = [
        timestamp for timestamp in rate_limit_store[client_ip]
        if current_time - timestamp < 60
    ]
    
    if len(rate_limit_store[client_ip]) >= config.RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"请求过于频繁，每分钟最多{config.RATE_LIMIT}次请求"
        )
    
    rate_limit_store[client_ip].append(current_time)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"请求验证失败: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "error": "请求参数验证失败", "details": exc.errors()}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "error": "服务器内部错误"}
    )


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Qwen3-VL 大模型服务</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
            }
            .info {
                margin: 20px 0;
                padding: 15px;
                background-color: #e7f3ff;
                border-left: 4px solid #2196F3;
            }
            .links {
                margin: 20px 0;
            }
            .links a {
                display: block;
                padding: 10px;
                margin: 5px 0;
                background-color: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                text-align: center;
            }
            .links a:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Qwen3-VL 大模型服务</h1>
            <div class="info">
                <p><strong>欢迎使用 Qwen3-VL 大模型推理服务！</strong></p>
                <p>本服务基于 Qwen3-VL-4B-Instruct 模型，支持文本和图像输入的多模态推理。</p>
            </div>
            <div class="links">
                <a href="/chat">📝 进入聊天演示页面</a>
                <a href="/docs">📚 查看 API 文档</a>
                <a href="/health">💚 健康检查</a>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/health")
async def health_check():
    model_service = ModelService()
    return {
        "status": "healthy",
        "model_loaded": model_service.is_loaded(),
        "device": model_service.get_device(),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    http_request: Request,
    api_key: Optional[str] = Depends(verify_api_key)
):
    await rate_limit(http_request)
    
    try:
        model_service = ModelService()
        response = model_service.generate_response(
            prompt=request.prompt,
            image_url=request.image_url,
            max_new_tokens=request.max_new_tokens,
            temperature=request.temperature,
            top_p=request.top_p
        )
        
        return ChatResponse(success=True, response=response)
        
    except Exception as e:
        logger.error(f"聊天请求处理失败: {e}")
        return ChatResponse(success=False, response="", error=str(e))


@app.post("/api/chat/history", response_model=ChatResponse)
async def chat_with_history(
    request: ChatHistoryRequest,
    http_request: Request,
    api_key: Optional[str] = Depends(verify_api_key)
):
    await rate_limit(http_request)
    
    try:
        model_service = ModelService()
        
        last_message = request.messages[-1] if request.messages else None
        if not last_message or last_message.role != "user":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="最后一条消息必须是用户消息"
            )
        
        image_url = None
        if last_message.content.startswith("IMAGE:"):
            parts = last_message.content.split(":", 2)
            if len(parts) >= 2:
                image_url = parts[1].strip()
                prompt = parts[2] if len(parts) > 2 else ""
            else:
                prompt = ""
        else:
            prompt = last_message.content
        
        response = model_service.generate_response(
            prompt=prompt,
            image_url=image_url,
            max_new_tokens=request.max_new_tokens,
            temperature=request.temperature,
            top_p=request.top_p
        )
        
        return ChatResponse(success=True, response=response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"聊天历史请求处理失败: {e}")
        return ChatResponse(success=False, response="", error=str(e))


@app.get("/chat", response_class=HTMLResponse)
async def chat_page():
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Qwen3-VL 聊天演示</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
                display: flex;
                flex-direction: column;
                height: calc(100vh - 40px);
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                text-align: center;
            }
            .header h1 {
                font-size: 24px;
                margin-bottom: 5px;
            }
            .header p {
                font-size: 14px;
                opacity: 0.9;
            }
            .chat-container {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background: #f8f9fa;
            }
            .message {
                margin-bottom: 20px;
                display: flex;
                align-items: flex-start;
            }
            .message.user {
                justify-content: flex-end;
            }
            .message.assistant {
                justify-content: flex-start;
            }
            .message-content {
                max-width: 70%;
                padding: 15px 20px;
                border-radius: 15px;
                word-wrap: break-word;
            }
            .message.user .message-content {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-bottom-right-radius: 5px;
            }
            .message.assistant .message-content {
                background: white;
                color: #333;
                border: 1px solid #e0e0e0;
                border-bottom-left-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .message-image {
                max-width: 300px;
                max-height: 300px;
                border-radius: 10px;
                margin-top: 10px;
                display: block;
            }
            .input-container {
                padding: 20px;
                background: white;
                border-top: 1px solid #e0e0e0;
            }
            .image-preview {
                display: none;
                margin-bottom: 10px;
                position: relative;
            }
            .image-preview.active {
                display: block;
            }
            .image-preview img {
                max-width: 200px;
                max-height: 200px;
                border-radius: 10px;
                border: 2px solid #667eea;
            }
            .image-preview button {
                position: absolute;
                top: 5px;
                right: 5px;
                background: #ff4757;
                color: white;
                border: none;
                border-radius: 50%;
                width: 25px;
                height: 25px;
                cursor: pointer;
                font-size: 14px;
            }
            .input-row {
                display: flex;
                gap: 10px;
            }
            .input-wrapper {
                flex: 1;
                position: relative;
            }
            textarea {
                width: 100%;
                min-height: 60px;
                max-height: 150px;
                padding: 15px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                resize: none;
                font-size: 14px;
                font-family: inherit;
                transition: border-color 0.3s;
            }
            textarea:focus {
                outline: none;
                border-color: #667eea;
            }
            .button-group {
                display: flex;
                gap: 10px;
            }
            button {
                padding: 12px 24px;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
            }
            .btn-send {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .btn-send:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            .btn-send:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            .btn-image {
                background: #f8f9fa;
                color: #667eea;
                border: 2px solid #667eea;
            }
            .btn-image:hover {
                background: #667eea;
                color: white;
            }
            .btn-clear {
                background: #f8f9fa;
                color: #ff4757;
                border: 2px solid #ff4757;
            }
            .btn-clear:hover {
                background: #ff4757;
                color: white;
            }
            .loading {
                display: none;
                text-align: center;
                padding: 20px;
            }
            .loading.active {
                display: block;
            }
            .spinner {
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 10px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .error {
                display: none;
                background: #ffebee;
                color: #c62828;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                border-left: 4px solid #c62828;
            }
            .error.active {
                display: block;
            }
            @media (max-width: 768px) {
                .container {
                    height: calc(100vh - 20px);
                    border-radius: 0;
                }
                .message-content {
                    max-width: 85%;
                }
                .button-group {
                    flex-wrap: wrap;
                }
                button {
                    flex: 1;
                    min-width: 80px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Qwen3-VL 智能助手</h1>
                <p>支持文本对话和图像理解的多模态AI助手</p>
            </div>
            
            <div class="chat-container" id="chatContainer">
                <div class="message assistant">
                    <div class="message-content">
                        你好！我是 Qwen3-VL 智能助手，我可以帮你理解图片内容或回答各种问题。请上传图片或输入问题开始对话吧！
                    </div>
                </div>
            </div>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>正在思考中...</p>
            </div>
            
            <div class="error" id="error"></div>
            
            <div class="input-container">
                <div class="image-preview" id="imagePreview">
                    <button onclick="removeImage()">×</button>
                    <img id="previewImg" src="" alt="预览">
                </div>
                
                <div class="input-row">
                    <div class="input-wrapper">
                        <textarea 
                            id="messageInput" 
                            placeholder="输入你的问题或描述..."
                            rows="1"
                        ></textarea>
                    </div>
                    <div class="button-group">
                        <button class="btn-image" onclick="document.getElementById('imageInput').click()">
                            📷 图片
                        </button>
                        <button class="btn-clear" onclick="clearChat()">
                            🗑️ 清空
                        </button>
                        <button class="btn-send" id="sendBtn" onclick="sendMessage()">
                            发送
                        </button>
                    </div>
                </div>
                <input type="file" id="imageInput" accept="image/*" style="display: none;" onchange="handleImageUpload(event)">
            </div>
        </div>
        
        <script>
            let selectedImage = null;
            const chatContainer = document.getElementById('chatContainer');
            const messageInput = document.getElementById('messageInput');
            const sendBtn = document.getElementById('sendBtn');
            const loading = document.getElementById('loading');
            const error = document.getElementById('error');
            const imagePreview = document.getElementById('imagePreview');
            const previewImg = document.getElementById('previewImg');
            
            messageInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });
            
            function handleImageUpload(event) {
                const file = event.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        selectedImage = e.target.result;
                        previewImg.src = selectedImage;
                        imagePreview.classList.add('active');
                    };
                    reader.readAsDataURL(file);
                }
            }
            
            function removeImage() {
                selectedImage = null;
                imagePreview.classList.remove('active');
                document.getElementById('imageInput').value = '';
            }
            
            function addMessage(role, content, imageUrl = null) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${role}`;
                
                let html = `<div class="message-content">${escapeHtml(content)}`;
                if (imageUrl) {
                    html += `<img src="${imageUrl}" class="message-image" alt="上传的图片">`;
                }
                html += `</div>`;
                
                messageDiv.innerHTML = html;
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
            
            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
            
            function showError(message) {
                error.textContent = message;
                error.classList.add('active');
                setTimeout(() => error.classList.remove('active'), 5000);
            }
            
            function clearChat() {
                chatContainer.innerHTML = `
                    <div class="message assistant">
                        <div class="message-content">
                            你好！我是 Qwen3-VL 智能助手，我可以帮你理解图片内容或回答各种问题。请上传图片或输入问题开始对话吧！
                        </div>
                    </div>
                `;
                removeImage();
                messageInput.value = '';
            }
            
            async function sendMessage() {
                const message = messageInput.value.trim();
                if (!message && !selectedImage) {
                    showError('请输入消息或上传图片');
                    return;
                }
                
                sendBtn.disabled = true;
                loading.classList.add('active');
                error.classList.remove('active');
                
                addMessage('user', message, selectedImage);
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            prompt: message || '请描述这张图片',
                            image_url: selectedImage,
                            max_new_tokens: 128,
                            temperature: 0.7,
                            top_p: 0.95
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        addMessage('assistant', data.response);
                    } else {
                        showError(data.error || '请求失败');
                    }
                } catch (err) {
                    showError('网络错误，请稍后重试');
                    console.error(err);
                }
                
                loading.classList.remove('active');
                sendBtn.disabled = false;
                messageInput.value = '';
                removeImage();
            }
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)
