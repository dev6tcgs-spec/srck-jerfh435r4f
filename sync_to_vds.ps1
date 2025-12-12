# Скрипт для синхронизации файлов с VDS
# Использование: .\sync_to_vds.ps1

# ===== НАСТРОЙКИ =====
$VDS_USER = "your_username"      # ЗАМЕНИТЕ на ваше имя пользователя на VDS
$VDS_IP = "your-vds-ip"           # ЗАМЕНИТЕ на IP вашего VDS
$VDS_PATH = "/home/user/zimamos"  # ЗАМЕНИТЕ на путь к проекту на VDS

# ===== ФАЙЛЫ ДЛЯ СИНХРОНИЗАЦИИ =====
$FILES = @(
    "bot.py",
    "database.py",
    "game_data.py",
    "tasks_handler.py",
    "config.py",
    "logger.py",
    "requirements.txt",
    "deploy.sh",
    "update.sh",
    "monitor.sh"
)

Write-Host "🔄 Синхронизация с VDS ($VDS_USER@$VDS_IP)..." -ForegroundColor Cyan
Write-Host ""

# Проверка наличия файлов
$missing = @()
foreach ($file in $FILES) {
    if (-not (Test-Path $file)) {
        $missing += $file
    }
}

if ($missing.Count -gt 0) {
    Write-Host "❌ Файлы не найдены:" -ForegroundColor Red
    $missing | ForEach-Object { Write-Host "   - $_" -ForegroundColor Red }
    exit 1
}

# Копирование файлов
Write-Host "📤 Копирование файлов..." -ForegroundColor Yellow
foreach ($file in $FILES) {
    Write-Host "   → $file" -ForegroundColor Gray
    scp $file "${VDS_USER}@${VDS_IP}:${VDS_PATH}/" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Ошибка при копировании $file" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "✅ Синхронизация завершена!" -ForegroundColor Green
Write-Host ""
Write-Host "📡 Следующие шаги на VDS:" -ForegroundColor Cyan
Write-Host "   1. Подключитесь: ssh $VDS_USER@$VDS_IP" -ForegroundColor White
Write-Host "   2. Перейдите: cd $VDS_PATH" -ForegroundColor White
Write-Host "   3. Обновите: ./update.sh" -ForegroundColor White
Write-Host ""

