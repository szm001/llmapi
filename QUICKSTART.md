# Qwen3-VL 服务快速开始指南

本指南将帮助你在 5 分钟内启动并运行 Qwen3-VL 大模型服务。

## 前置条件检查

在开始之前，请确保你已经：

1. ✅ 安装了 Python 3.8 或更高版本
2. ✅ 安装了 CUDA 11.8+（如果使用 GPU）
3. ✅ 下载了 Qwen3-VL-4B-Instruct 模型文件

## 快速开始（Windows）

### 步骤 1: 安装依赖

双击运行 `install.bat`，或在命令行中执行：

```bash
install.bat
```

这将自动：
- 创建 Python 虚拟环境
- 安装所有必需的依赖包
- 创建配置文件和日志目录

### 步骤 2: 配置服务

编辑 `.env` 文件，设置以下关键参数：

```env
MODEL_PATH=D:/llm/Qwen/Qwen3-VL-4B-Instruct  # 修改为你的模型路径
DEVICE=cuda:0                                  # 使用 GPU，或改为 cpu
HOST=0.0.0.0
PORT=8000
API_KEY=                                      # 留空则不需要 API 密钥
RATE_LIMIT=10
```

### 步骤 3: 启动服务

双击运行 `start.bat`，或在命令行中执行：

```bash
start.bat
```

服务启动后，你会看到：

```
========================================
服务启动中...
========================================

服务地址: http://localhost:8000
API 文档: http://localhost:8000/docs
聊天界面: http://localhost:8000/chat
```

### 步骤 4: 测试服务

#### 方法 1: 使用 Web 界面

在浏览器中打开：http://localhost:8000/chat

#### 方法 2: 使用 API 文档

在浏览器中打开：http://localhost:8000/docs

#### 方法 3: 使用测试脚本

```bash
python test_service.py
```

#### 方法 4: 使用 Python 代码

```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "prompt": "你好，请介绍一下你自己"
    }
)

print(response.json())
```

## 快速开始（Linux/Mac）

### 步骤 1: 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 步骤 2: 配置服务

```bash
# 复制配置文件
cp .env.example .env

# 编辑配置文件
nano .env
```

### 步骤 3: 启动服务

```bash
# 开发模式
python main.py

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 步骤 4: 测试服务

```bash
# 运行测试脚本
python test_service.py
```

## 常见问题

### Q1: 服务启动失败，提示模型路径错误

**解决方法：**
- 检查 `.env` 文件中的 `MODEL_PATH` 是否正确
- 确保模型文件存在于指定路径
- 路径使用正斜杠 `/` 或双反斜杠 `\\`

### Q2: CUDA 内存不足

**解决方法：**
- 检查 GPU 显存是否足够（至少 8GB）
- 关闭其他占用 GPU 的程序
- 或使用 CPU 模式：设置 `DEVICE=cpu`

### Q3: 依赖安装失败

**解决方法：**
```bash
# 升级 pip
pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q4: 端口 8000 被占用

**解决方法：**
- 修改 `.env` 文件中的 `PORT` 为其他端口（如 8001）
- 或关闭占用 8000 端口的程序

### Q5: API 请求返回 401 错误

**解决方法：**
- 检查请求头中是否包含正确的 `X-API-Key`
- 如果不需要 API 密钥，将 `.env` 中的 `API_KEY` 留空

## 下一步

### 1. 查看 API 文档

访问 http://localhost:8000/docs 查看完整的 API 文档和交互式测试界面。

### 2. 运行示例代码

```bash
python examples.py
```

### 3. 阅读完整文档

- [README.md](README.md) - 完整的使用说明
- [DEPLOYMENT.md](DEPLOYMENT.md) - 详细的部署指南

### 4. 集成到你的项目

参考 [examples.py](examples.py) 中的示例代码，将服务集成到你的应用中。

## 性能优化建议

### 1. 调整生成参数

根据你的需求调整以下参数：

- `max_new_tokens`: 控制输出长度（默认 128）
- `temperature`: 控制随机性（默认 0.7）
- `top_p`: 控制采样范围（默认 0.95）

### 2. 使用 GPU 加速

确保：
- CUDA 驱动已正确安装
- `DEVICE=cuda:0` 已配置
- GPU 有足够的显存

### 3. 请求批处理

对于大量请求，考虑实现批处理以提高吞吐量。

## 安全建议

### 1. 设置 API 密钥

在生产环境中，设置强密码作为 API_KEY：

```bash
# 生成随机密钥
openssl rand -base64 32
```

### 2. 使用 HTTPS

在生产环境中，配置 Nginx 反向代理并启用 HTTPS。

### 3. 限制访问

使用防火墙规则限制访问 IP 地址。

## 获取帮助

如果遇到问题：

1. 查看 `logs/` 目录中的日志文件
2. 运行 `python test_service.py` 诊断问题
3. 参考 [README.md](README.md) 中的故障排查部分
4. 提交 Issue 报告问题

## 快速命令参考

```bash
# 安装依赖
install.bat  # Windows
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt  # Linux/Mac

# 启动服务
start.bat  # Windows
python main.py  # Linux/Mac

# 测试服务
python test_service.py

# 运行示例
python examples.py

# 查看日志
type logs\app_*.log  # Windows
tail -f logs/app_*.log  # Linux/Mac
```

## 祝你使用愉快！🎉

如果这个服务对你有帮助，请考虑给项目点个 Star！
