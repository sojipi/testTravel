# 银发族智能旅行助手启动脚本 (PowerShell版)
# 推荐使用此脚本，支持UTF-8编码

Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "🧳 银发族智能旅行助手启动脚本 (PowerShell版)" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

# 检查Python是否安装
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ 错误：未找到Python，请先安装Python 3.8+" -ForegroundColor Red
    Write-Host "请访问：https://www.python.org/downloads/ 下载安装" -ForegroundColor Yellow
    Read-Host "按回车键退出"
    exit 1
}

# 检查pip是否可用
try {
    $pipVersion = pip --version 2>$null
    Write-Host "✅ pip已安装" -ForegroundColor Green
} catch {
    Write-Host "❌ 错误：未找到pip，请检查Python安装" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# 检查.env文件
if (-not (Test-Path ".env")) {
    Write-Host ""
    Write-Host "⚠️  警告：未找到.env文件" -ForegroundColor Yellow
    Write-Host "请复制.env.example为.env，并填入您的ModelScope Token" -ForegroundColor Yellow
    Write-Host ""

    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env" -Force
        Write-Host "✅ 已创建.env文件，请编辑并填入您的ModelScope Token" -ForegroundColor Green
        Write-Host ""
    }

    Write-Host "请编辑.env文件后重新运行此脚本" -ForegroundColor Yellow
    Write-Host "例如：MODELSCOPE_TOKEN=你的token值" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "按回车键退出"
    exit 1
}

Write-Host "✅ .env文件检查通过" -ForegroundColor Green
Write-Host ""

# 检查虚拟环境
if (-not (Test-Path "venv")) {
    Write-Host "📦 创建虚拟环境..." -ForegroundColor Cyan
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 虚拟环境创建失败" -ForegroundColor Red
        Read-Host "按回车键退出"
        exit 1
    }
    Write-Host "✅ 虚拟环境创建成功" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "✅ 虚拟环境已存在" -ForegroundColor Green
}

Write-Host "📦 安装依赖包..." -ForegroundColor Cyan
& "venv\Scripts\Activate.ps1"
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 依赖包安装失败" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

Write-Host "✅ 依赖包安装完成" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 启动应用..." -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "访问地址：http://localhost:7860" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "按 Ctrl+C 停止应用" -ForegroundColor Yellow
Write-Host ""

python travel_assistant.py

# 如果程序异常退出
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "程序异常退出" -ForegroundColor Red
    Read-Host "按任意键继续"
}
