@echo off
echo ========================================
echo Qwen3-VL 服务安装脚本
echo ========================================
echo.

REM 检查 Python 版本
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [1/5] 检查 Python 版本...
python --version

REM 创建虚拟环境
echo.
echo [2/5] 创建虚拟环境...
python -m venv venv
if errorlevel 1 (
    echo [错误] 创建虚拟环境失败
    pause
    exit /b 1
)

REM 激活虚拟环境
echo.
echo [3/5] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 升级 pip
echo.
echo [4/5] 升级 pip...
python -m pip install --upgrade pip

REM 安装依赖
echo.
echo [5/5] 安装项目依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 安装依赖失败
    pause
    exit /b 1
)

REM 创建配置文件
if not exist ".env" (
    echo.
    echo [配置] 创建 .env 配置文件...
    copy .env.example .env
    echo.
    echo [提示] 请编辑 .env 文件，配置以下参数：
    echo   - MODEL_PATH: 模型文件路径
    echo   - DEVICE: 设备类型 (cuda:0 或 cpu)
    echo   - API_KEY: API 密钥（可选）
    echo.
)

REM 创建日志目录
if not exist "logs" (
    echo [配置] 创建日志目录...
    mkdir logs
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 下一步：
echo 1. 编辑 .env 文件配置模型路径
echo 2. 运行 start.bat 启动服务
echo.
pause
