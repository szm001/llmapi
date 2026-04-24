# Qwen3-VL 服务部署指南

本文档提供详细的部署说明，帮助你在不同环境中部署 Qwen3-VL 大模型服务。

## 目录

1. [本地部署](#本地部署)
2. [Docker 部署](#docker-部署)
3. [生产环境部署](#生产环境部署)
4. [性能优化](#性能优化)
5. [监控和维护](#监控和维护)

## 本地部署

### 前置条件

1. **硬件要求：**
   - GPU: NVIDIA GPU (至少 8GB 显存)
   - 内存: 16GB+
   - 存储: 50GB+ 可用空间

2. **软件要求：**
   - Python 3.8+
   - CUDA 11.8+
   - cuDNN 8.6+

### 部署步骤

#### 1. 安装 CUDA 和 cuDNN

**Windows:**
```bash
# 下载并安装 CUDA Toolkit 11.8
# https://developer.nvidia.com/cuda-downloads

# 下载并安装 cuDNN
# https://developer.nvidia.com/cudnn
```

**Linux (Ubuntu):**
```bash
# 安装 CUDA
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update
sudo apt-get install cuda-11-8

# 配置环境变量
echo 'export PATH=/usr/local/cuda-11.8/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-11.8/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

#### 2. 下载模型

```bash
# 使用 Hugging Face CLI
pip install huggingface_hub
huggingface-cli download Qwen/Qwen3-VL-4B-Instruct --local-dir D:/llm/Qwen/Qwen3-VL-4B-Instruct

# 或使用 git lfs
git lfs install
git clone https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct D:/llm/Qwen/Qwen3-VL-4B-Instruct
```

#### 3. 安装 Python 依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 4. 配置环境变量

```bash
# 复制配置文件
copy .env.example .env

# 编辑 .env 文件
notepad .env  # Windows
nano .env     # Linux/Mac
```

配置内容：
```env
MODEL_PATH=D:/llm/Qwen/Qwen3-VL-4B-Instruct
DEVICE=cuda:0
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
API_KEY=your_secure_api_key_here
RATE_LIMIT=10
```

#### 5. 启动服务

```bash
# 开发模式
python main.py

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
```

#### 6. 验证部署

```bash
# 检查服务状态
curl http://localhost:8000/health

# 访问 Web 界面
# 浏览器打开: http://localhost:8000/chat
```

## Docker 部署

### 创建 Dockerfile

```dockerfile
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip3 install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY main.py models.py config.py model_service.py logger_config.py .

# 创建日志目录
RUN mkdir -p logs

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  qwen3vl:
    build: .
    container_name: qwen3vl-service
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs
      - D:/llm/Qwen/Qwen3-VL-4B-Instruct:/model
    environment:
      - MODEL_PATH=/model
      - DEVICE=cuda:0
      - HOST=0.0.0.0
      - PORT=8000
      - LOG_LEVEL=INFO
      - API_KEY=your_secure_api_key_here
      - RATE_LIMIT=10
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped
```

### 构建和运行

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 生产环境部署

### 使用 Nginx 反向代理

#### 1. 安装 Nginx

```bash
# Ubuntu/Debian
sudo apt-get install nginx

# CentOS/RHEL
sudo yum install nginx
```

#### 2. 配置 Nginx

创建配置文件 `/etc/nginx/sites-available/qwen3vl`:

```nginx
upstream qwen3vl_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://qwen3vl_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    location /static {
        alias /path/to/static/files;
    }
}
```

启用配置：

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/qwen3vl /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 配置 HTTPS (使用 Let's Encrypt)

```bash
# 安装 Certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 使用 Systemd 管理服务

创建服务文件 `/etc/systemd/system/qwen3vl.service`:

```ini
[Unit]
Description=Qwen3-VL API Service
After=network.target

[Service]
Type=simple
User=your_user
Group=your_group
WorkingDirectory=/path/to/llmapi
Environment="PATH=/path/to/venv/bin"
EnvironmentFile=/path/to/llmapi/.env
ExecStart=/path/to/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 1
Restart=always
RestartSec=10

# 日志配置
StandardOutput=append:/var/log/qwen3vl/service.log
StandardError=append:/var/log/qwen3vl/error.log

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重载 systemd
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable qwen3vl

# 启动服务
sudo systemctl start qwen3vl

# 查看状态
sudo systemctl status qwen3vl

# 查看日志
sudo journalctl -u qwen3vl -f
```

## 性能优化

### 1. GPU 优化

#### 显存优化

修改 `model_service.py` 中的模型加载参数：

```python
self._model = Qwen3VLForConditionalGeneration.from_pretrained(
    config.MODEL_PATH,
    config=self._config,
    torch_dtype=torch.float16,  # 使用 float16 减少显存
    device_map="auto",
    low_cpu_mem_usage=True
)
```

#### 批处理优化

对于批量请求，可以实现批处理接口：

```python
@app.post("/api/chat/batch")
async def batch_chat(requests: List[ChatRequest]):
    # 实现批处理逻辑
    pass
```

### 2. 缓存优化

#### 使用 Redis 缓存

```python
import redis
from functools import lru_cache

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@lru_cache(maxsize=1000)
def get_cached_response(prompt_hash):
    return redis_client.get(prompt_hash)
```

### 3. 并发优化

#### 调整 Worker 数量

```bash
# 根据 GPU 数量调整 workers
uvicorn main:app --workers 2 --host 0.0.0.0 --port 8000
```

#### 使用异步队列

```python
from fastapi import BackgroundTasks
import asyncio

async def process_request(request: ChatRequest):
    # 异步处理请求
    pass
```

### 4. 网络优化

#### 启用 HTTP/2

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --http h11
```

#### 配置 Keep-Alive

```nginx
# Nginx 配置
proxy_http_version 1.1;
proxy_set_header Connection "";
```

## 监控和维护

### 1. 健康检查

创建监控脚本 `monitor.sh`:

```bash
#!/bin/bash

API_URL="http://localhost:8000/health"
ALERT_EMAIL="admin@example.com"

response=$(curl -s -o /dev/null -w "%{http_code}" $API_URL)

if [ $response -ne 200 ]; then
    echo "Service is down! HTTP status: $response"
    # 发送告警邮件
    echo "Qwen3-VL service is down!" | mail -s "Service Alert" $ALERT_EMAIL
    # 重启服务
    sudo systemctl restart qwen3vl
fi
```

添加到 crontab：

```bash
# 每5分钟检查一次
*/5 * * * * /path/to/monitor.sh
```

### 2. 日志管理

#### 日志轮转配置

创建 `/etc/logrotate.d/qwen3vl`:

```
/path/to/llmapi/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 your_user your_group
}
```

### 3. 性能监控

#### 使用 Prometheus + Grafana

安装 Prometheus：

```bash
# 安装 Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvfz prometheus-2.45.0.linux-amd64.tar.gz
cd prometheus-2.45.0.linux-amd64
./prometheus --config.file=prometheus.yml
```

配置 Prometheus (`prometheus.yml`):

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'qwen3vl'
    static_configs:
      - targets: ['localhost:8000']
```

### 4. 备份策略

#### 模型备份

```bash
#!/bin/bash
BACKUP_DIR="/backup/qwen3vl"
MODEL_DIR="/model"
DATE=$(date +%Y%m%d)

# 创建备份
tar -czf $BACKUP_DIR/model_$DATE.tar.gz $MODEL_DIR

# 删除7天前的备份
find $BACKUP_DIR -name "model_*.tar.gz" -mtime +7 -delete
```

## 故障恢复

### 1. 服务崩溃恢复

```bash
# 查看崩溃日志
journalctl -u qwen3vl -n 100

# 重启服务
sudo systemctl restart qwen3vl
```

### 2. GPU 内存泄漏处理

```bash
# 监控 GPU 内存
watch -n 1 nvidia-smi

# 如果内存泄漏，重启服务
sudo systemctl restart qwen3vl
```

### 3. 数据恢复

从备份恢复模型：

```bash
# 解压备份
tar -xzf /backup/qwen3vl/model_20240119.tar.gz -C /tmp

# 恢复模型
cp -r /tmp/model/* /model/
```

## 安全加固

### 1. 防火墙配置

```bash
# Ubuntu UFW
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow from 192.168.1.0/24 to any port 8000
sudo ufw enable
```

### 2. API 密钥管理

```bash
# 生成强密码
openssl rand -base64 32

# 使用环境变量
export API_KEY=$(openssl rand -base64 32)
```

### 3. 限流配置

在 `.env` 中配置：

```env
RATE_LIMIT=10  # 每分钟最多10个请求
```

## 扩展部署

### 多实例部署

使用 Docker Swarm 或 Kubernetes 部署多个实例：

```yaml
# docker-compose.yml
version: '3.8'

services:
  qwen3vl:
    image: qwen3vl:latest
    deploy:
      replicas: 3
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### 负载均衡

使用 HAProxy 或 Nginx 进行负载均衡：

```nginx
upstream qwen3vl_cluster {
    least_conn;
    server 192.168.1.10:8000;
    server 192.168.1.11:8000;
    server 192.168.1.12:8000;
}
```

## 总结

本部署指南涵盖了从本地开发到生产环境的完整部署流程。根据你的实际需求选择合适的部署方式：

- **本地开发**: 直接运行 `python main.py`
- **测试环境**: 使用 Docker 部署
- **生产环境**: 使用 Systemd + Nginx + HTTPS

如有问题，请参考 [README.md](README.md) 或提交 Issue。
