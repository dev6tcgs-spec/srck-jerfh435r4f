"""Скрипт для отправки уведомления о технических работах всем пользователям"""

import asyncio
import sys
from telegram import Bot
from telegram.error import TelegramError, RetryAfter, TimedOut
from config import get_bot_token
import database

async def send_maintenance_message():
    """Отправить сообщение о технических работах всем пользователям"""
    
    # Инициализация базы данных
    await database.init_db()
    
    # Получаем токен бота
    bot_token = get_bot_token()
    if not bot_token:
        print("❌ Ошибка: токен бота не найден!")
        return
    
    bot = Bot(token=bot_token)
    
    # Получаем список всех пользователей
    user_ids = await database.get_all_user_ids()
    
    if not user_ids:
        print("ℹ️ Пользователей в базе данных не найдено.")
        return
    
    print(f"📊 Найдено пользователей: {len(user_ids)}")
    print("🚀 Начинаю рассылку...\n")
    
    # Текст сообщения о технических работах
    message_text = """🔧 *Технические работы*

━━━━━━━━━━━━━━━━━━━━

⚙️ Мы проводим технические работы для улучшения бота.

✨ *Что улучшаем:*
• Оптимизация кода
• Улучшение производительности
• Исправление ошибок
• Подготовка новых функций

⏱ *Время работ:* ~10-15 минут

━━━━━━━━━━━━━━━━━━━━

🙏 Спасибо за понимание!

Бот вернется в работу сразу после завершения работ."""
    
    success_count = 0
    error_count = 0
    blocked_count = 0
    
    for i, user_id in enumerate(user_ids, 1):
        try:
            await bot.send_message(
                chat_id=user_id,
                text=message_text,
                parse_mode='Markdown'
            )
            success_count += 1
            print(f"✅ [{i}/{len(user_ids)}] Отправлено пользователю {user_id}")
            
            # Небольшая задержка, чтобы не превысить лимиты API
            await asyncio.sleep(0.05)  # 50ms между сообщениями
            
        except RetryAfter as e:
            # Превышен лимит запросов, ждем
            wait_time = e.retry_after
            print(f"⏳ Лимит запросов. Ждем {wait_time} секунд...")
            await asyncio.sleep(wait_time)
            # Повторяем отправку
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=message_text,
                    parse_mode='Markdown'
                )
                success_count += 1
                print(f"✅ [{i}/{len(user_ids)}] Отправлено пользователю {user_id} (повтор)")
            except Exception as e:
                error_count += 1
                print(f"❌ [{i}/{len(user_ids)}] Ошибка для {user_id}: {e}")
                
        except TelegramError as e:
            error_message = str(e).lower()
            if "blocked" in error_message or "chat not found" in error_message:
                blocked_count += 1
                print(f"🚫 [{i}/{len(user_ids)}] Пользователь {user_id} заблокировал бота")
            else:
                error_count += 1
                print(f"❌ [{i}/{len(user_ids)}] Ошибка для {user_id}: {e}")
                
        except Exception as e:
            error_count += 1
            print(f"❌ [{i}/{len(user_ids)}] Неожиданная ошибка для {user_id}: {e}")
    
    # Итоговая статистика
    print("\n" + "="*50)
    print("📊 ИТОГИ РАССЫЛКИ:")
    print("="*50)
    print(f"✅ Успешно отправлено: {success_count}")
    print(f"❌ Ошибок: {error_count}")
    print(f"🚫 Заблокировано бота: {blocked_count}")
    print(f"📊 Всего пользователей: {len(user_ids)}")
    print("="*50)

if __name__ == "__main__":
    try:
        asyncio.run(send_maintenance_message())
    except KeyboardInterrupt:
        print("\n⚠️ Рассылка прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)

