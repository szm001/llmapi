# Qwen3-VL 大模型服务系统

基于 Qwen3-VL-4B-Instruct 模型的 FastAPI 推理服务，支持文本和图像输入的多模态推理。

## 功能特性

- RESTful API 接口，支持文本和图像推理
- 交互式 Web 聊天界面
- 请求参数验证和错误处理
- API 密钥身份验证
- 请求限流保护
- 自动生成 OpenAPI 文档
- 完整的日志记录
- 响应式设计，适配各种设备

## 项目结构

```
llmapi/
├── main.py                 # FastAPI 主应用
├── models.py               # Pydantic 数据模型
├── config.py               # 配置管理
├── model_service.py        # 模型推理服务
├── logger_config.py        # 日志配置
├── requirements.txt        # Python 依赖
├── .env.example           # 环境变量示例
├── .gitignore             # Git 忽略文件
├── logs/                  # 日志目录（自动创建）
└── README.md              # 本文档
```

## 系统要求

- Python 3.8+
- CUDA 11.8+ (GPU 加速)
- 至少 8GB GPU 显存
- 16GB+ 系统内存

## 安装步骤

### 1. 克隆或下载项目

```bash
cd d:\project\llmapi
```

### 2. 创建虚拟环境（推荐）

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
copy .env.example .env
```

编辑 `.env` 文件：

```env
MODEL_PATH=D:/llm/Qwen/Qwen3-VL-4B-Instruct
DEVICE=cuda:0
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
API_KEY=your_api_key_here
RATE_LIMIT=10
```

**配置说明：**

- `MODEL_PATH`: Qwen3-VL 模型的本地路径
- `DEVICE`: 使用的设备（cuda:0, cpu 等）
- `HOST`: 服务监听地址
- `PORT`: 服务端口
- `LOG_LEVEL`: 日志级别（DEBUG, INFO, WARNING, ERROR）
- `API_KEY`: API 密钥（留空则不需要验证）
- `RATE_LIMIT`: 每分钟请求限制次数

## 运行服务

### 开发模式

```bash
python main.py
```

### 生产模式（使用 uvicorn）

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
```

### 使用 systemd 管理（Linux）

创建服务文件 `/etc/systemd/system/qwen3vl.service`：

```ini
[Unit]
Description=Qwen3-VL API Service
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/llmapi
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl enable qwen3vl
sudo systemctl start qwen3vl
```

## API 文档

服务启动后，访问以下地址查看 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

### 1. 健康检查

**GET** `/health`

返回服务状态信息。

**响应示例：**

```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cuda:0",
  "timestamp": "2024-01-19T10:00:00"
}
```

### 2. 聊天接口

**POST** `/api/chat`

发送聊天请求，支持文本和图像输入。

**请求头：**

```
Content-Type: application/json
X-API-Key: your_api_key_here (如果配置了)
```

**请求体：**

```json
{
  "prompt": "请描述这张图片",
  "image_url": "https://example.com/image.jpg",
  "max_new_tokens": 128,
  "temperature": 0.7,
  "top_p": 0.95
}
```

**参数说明：**

- `prompt` (必填): 用户输入的文本提示
- `image_url` (可选): 图片 URL 地址
- `max_new_tokens` (可选): 最大生成 token 数，默认 128
- `temperature` (可选): 温度参数，默认 0.7
- `top_p` (可选): top_p 采样参数，默认 0.95

**响应示例：**

```json
{
  "success": true,
  "response": "这是一张美丽的风景照片，展示了蓝天白云下的山脉...",
  "error": null
}
```

### 3. 聊天历史接口

**POST** `/api/chat/history`

支持多轮对话的聊天接口。

**请求体：**

```json
{
  "messages": [
    {
      "role": "user",
      "content": "你好"
    },
    {
      "role": "assistant",
      "content": "你好！有什么我可以帮助你的吗？"
    },
    {
      "role": "user",
      "content": "IMAGE:https://example.com/image.jpg 请描述这张图片"
    }
  ],
  "max_new_tokens": 128,
  "temperature": 0.7,
  "top_p": 0.95
}
```

## Web 界面

访问 http://localhost:8000/chat 打开聊天演示页面。

**功能特性：**

- 文本输入和对话
- 图片上传和预览
- 实时消息显示
- 对话历史记录
- 清空对话功能
- 响应式设计

## 使用示例

### Python 客户端示例

```python
import requests

API_URL = "http://localhost:8000/api/chat"
API_KEY = "your_api_key_here"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

data = {
    "prompt": "请描述这张图片",
    "image_url": "https://example.com/image.jpg",
    "max_new_tokens": 128,
    "temperature": 0.7
}

response = requests.post(API_URL, json=data, headers=headers)
result = response.json()

if result["success"]:
    print("AI 回复:", result["response"])
else:
    print("错误:", result["error"])
```

### cURL 示例

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "prompt": "你好",
    "max_new_tokens": 128
  }'
```

### JavaScript 客户端示例

```javascript
async function chatWithAI(prompt, imageUrl = null) {
  const response = await fetch('http://localhost:8000/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'your_api_key_here'
    },
    body: JSON.stringify({
      prompt: prompt,
      image_url: imageUrl,
      max_new_tokens: 128,
      temperature: 0.7
    })
  });
  
  const result = await response.json();
  
  if (result.success) {
    console.log('AI 回复:', result.response);
  } else {
    console.error('错误:', result.error);
  }
}

chatWithAI('你好');
```

## 日志管理

日志文件存储在 `logs/` 目录：

- `app_YYYYMMDD.log`: 应用日志
- `error_YYYYMMDD.log`: 错误日志

日志文件自动轮转，单个文件最大 10MB，保留 5 个备份。

## 性能优化

### 1. 模型加载优化

模型在服务启动时加载，使用 `device_map="auto"` 自动分配设备。

### 2. 请求处理

- 使用异步处理提高并发性能
- 请求限流防止过载
- GPU 内存复用

### 3. 生成参数调优

根据应用场景调整生成参数：

- `max_new_tokens`: 控制输出长度
- `temperature`: 控制随机性（越高越随机）
- `top_p`: 控制采样范围

## 故障排查

### 1. 模型加载失败

**问题：** 模型路径错误或模型文件损坏

**解决：**
- 检查 `MODEL_PATH` 配置是否正确
- 确认模型文件完整性
- 查看日志获取详细错误信息

### 2. CUDA 内存不足

**问题：** GPU 显存不足

**解决：**
- 减小 `max_new_tokens` 参数
- 使用 CPU 模式（设置 `DEVICE=cpu`）
- 关闭其他占用 GPU 的程序

### 3. 请求超时

**问题：** 推理时间过长

**解决：**
- 减小 `max_new_tokens` 参数
- 增加 `temperature` 参数提高响应速度
- 检查 GPU 利用率

### 4. API 密钥错误

**问题：** 返回 401 错误

**解决：**
- 检查请求头中的 `X-API-Key` 是否正确
- 确认 `.env` 文件中的 `API_KEY` 配置

## 安全建议

1. **生产环境配置：**
   - 设置强密码作为 API_KEY
   - 使用 HTTPS 加密传输
   - 配置防火墙规则
   - 限制访问 IP 地址

2. **请求限流：**
   - 根据服务器性能调整 `RATE_LIMIT`
   - 考虑使用 Redis 实现分布式限流

3. **日志安全：**
   - 定期清理旧日志文件
   - 避免在日志中记录敏感信息

## 监控和维护

### 1. 健康检查

定期调用 `/health` 端点检查服务状态。

### 2. 日志监控

监控日志文件中的错误和警告信息。

### 3. 性能监控

监控以下指标：
- GPU 利用率
- 内存使用情况
- 请求响应时间
- 错误率

## 技术栈

- **后端框架:** FastAPI
- **模型:** Qwen3-VL-4B-Instruct
- **深度学习框架:** PyTorch
- **Web 服务器:** Uvicorn
- **数据验证:** Pydantic

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件

## 更新日志

### v1.0.0 (2024-01-19)

- 初始版本发布
- 支持文本和图像推理
- 提供 RESTful API
- 提供 Web 聊天界面
- 实现请求限流和身份验证
