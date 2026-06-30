# ==================== Ollama 测试脚本 (PowerShell) ====================

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "  Ollama 连接测试" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

# ========== 测试 1: 检查 Ollama 版本 ==========
Write-Host "[1/4] 检查 Ollama 服务..." -ForegroundColor Cyan
try {
    $version = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/version" -Method Get -ErrorAction Stop
    Write-Host "  ✓ Ollama 运行正常 (版本: $($version.version))" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Ollama 未运行或无法连接" -ForegroundColor Red
    Write-Host "    请在新终端运行: ollama serve" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# ========== 测试 2: 列出模型 ==========
Write-Host "[2/4] 检查可用模型..." -ForegroundColor Cyan
$models = ollama list
Write-Host $models
Write-Host ""

# ========== 测试 3: 测试生成 ==========
Write-Host "[3/4] 测试模型生成 (qwen2.5:3b)..." -ForegroundColor Cyan
try {
    $body = @{
        model = "qwen2.5:3b"
        prompt = "用一句话介绍你自己"
        stream = $false
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/generate" -Method Post -Body $body -ContentType "application/json" -ErrorAction Stop
    Write-Host "  ✓ 模型响应成功" -ForegroundColor Green
    Write-Host "  回复: $($response.response)" -ForegroundColor White
} catch {
    Write-Host "  ✗ 模型生成失败: $_" -ForegroundColor Red
}

Write-Host ""

# ========== 测试 4: 检查 Flask 健康状态 ==========
Write-Host "[4/4] 检查 Flask 后端连接..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/health" -Method Get -ErrorAction Stop
    
    Write-Host "  状态: $($health.status)" -ForegroundColor $(if ($health.status -eq "healthy") { "Green" } else { "Yellow" })
    Write-Host "  数据库: $($health.services.database.status)" -ForegroundColor $(if ($health.services.database.status -eq "up") { "Green" } else { "Red" })
    Write-Host "  FAISS: $($health.services.faiss.status) (向量数: $($health.services.faiss.total_vectors))" -ForegroundColor $(if ($health.services.faiss.status -eq "up") { "Green" } else { "Red" })
    Write-Host "  Ollama: $($health.services.ollama.status)" -ForegroundColor $(if ($health.services.ollama.status -eq "up") { "Green" } else { "Red" })
    
    if ($health.services.ollama.status -eq "up") {
        Write-Host "    模型: $($health.services.ollama.model)" -ForegroundColor Gray
        Write-Host "    地址: $($health.services.ollama.host)" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ✗ Flask 后端未运行或无法连接" -ForegroundColor Red
    Write-Host "    请确保已运行: python app.py" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "  测试完成" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan

