@echo off
echo ========================================
echo Qwen3-VL 服务启动脚本
echo ========================================
echo.

REM 检查虚拟环境是否存在
if not exist "venv" (
    echo [错误] 虚拟环境不存在，请先运行 install.bat 安装依赖
    pause
    exit /b 1
)

REM 激活虚拟环境
echo [1/4] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 检查 .env 文件是否存在
if not exist ".env" (
    echo [警告] .env 文件不存在，从 .env.example 复制...
    copy .env.example .env
    echo [提示] 请编辑 .env 文件配置模型路径和其他参数
    echo.
)

REM 检查日志目录
if not exist "logs" (
    echo [2/4] 创建日志目录...
    mkdir logs
)

REM 启动服务
echo [3/4] 启动 Qwen3-VL 服务...
echo.
echo ========================================
echo 服务启动中...
echo ========================================
echo.
echo 服务地址: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo 聊天界面: http://localhost:8000/chat
echo.
echo 按 Ctrl+C 停止服务
echo.

python main.py

pause
