#!/bin/bash
# Скрипт для синхронизации файлов с VDS (Linux/Mac)
# Использование: ./sync_to_vds.sh

# ===== НАСТРОЙКИ =====
VDS_USER="your_username"      # ЗАМЕНИТЕ на ваше имя пользователя на VDS
VDS_IP="your-vds-ip"           # ЗАМЕНИТЕ на IP вашего VDS
VDS_PATH="/home/user/zimamos"  # ЗАМЕНИТЕ на путь к проекту на VDS

# ===== ФАЙЛЫ ДЛЯ СИНХРОНИЗАЦИИ =====
FILES=(
    "bot.py"
    "database.py"
    "game_data.py"
    "tasks_handler.py"
    "config.py"
    "logger.py"
    "requirements.txt"
    "deploy.sh"
    "update.sh"
    "monitor.sh"
)

echo "🔄 Синхронизация с VDS ($VDS_USER@$VDS_IP)..."

# Копирование файлов
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   → $file"
        scp "$file" "${VDS_USER}@${VDS_IP}:${VDS_PATH}/"
        if [ $? -eq 0 ]; then
            echo "   ✅ $file"
        else
            echo "   ❌ Ошибка при копировании $file"
        fi
    else
        echo "   ⚠️  Файл $file не найден"
    fi
done

echo ""
echo "✅ Синхронизация завершена!"
echo ""
echo "📡 Следующие шаги на VDS:"
echo "   1. Подключитесь: ssh $VDS_USER@$VDS_IP"
echo "   2. Перейдите: cd $VDS_PATH"
echo "   3. Обновите: ./update.sh"
echo ""

