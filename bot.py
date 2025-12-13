"""Основной файл Telegram-бота 'Московская зимняя ярмарка'"""

import asyncio
import json
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import BadRequest, NetworkError, TimedOut, RetryAfter
from config import get_bot_token
import database
import game_data
import tasks_handler

# Импортируем систему логирования
try:
    from logger import logger, log_error, log_info, log_warning
    LOGGING_ENABLED = True
except ImportError:
    # Если logger.py не найден, используем простой print
    LOGGING_ENABLED = False
    def log_error(error, context=""):
        print(f"ERROR in {context}: {type(error).__name__}: {str(error)}", file=sys.stderr)
    def log_info(message, data=None):
        print(f"INFO: {message} {data if data else ''}")
    def log_warning(message, data=None):
        print(f"WARNING: {message} {data if data else ''}")

# Инициализация базы данных и загрузка данных
async def init():
    await database.init_db()
    await game_data.load_game_data()

# Вспомогательные функции для визуализации
def create_progress_bar(current: int, total: int, length: int = 10) -> str:
    """Создать визуальный прогресс-бар"""
    filled = int((current / total) * length) if total > 0 else 0
    filled = min(filled, length)
    bar = "█" * filled + "░" * (length - filled)
    percent = int((current / total) * 100) if total > 0 else 0
    return f"{bar} {percent}%"

def get_emoji_animation(step: int) -> str:
    """Получить анимированный эмодзи для эффектов"""
    animations = {
        "sparkles": ["✨", "⭐", "💫", "✨"],
        "coins": ["🍊", "💰", "💎", "🍊"],
        "success": ["✅", "🎉", "🌟", "✅"],
        "loading": ["⏳", "⏰", "⏳", "⏰"]
    }
    # Простая анимация через шаги
    return animations.get("sparkles", ["✨"])[step % len(animations.get("sparkles", ["✨"]))]

def format_coins(amount: int) -> str:
    """Форматировать количество мандаринок"""
    if amount >= 1000:
        return f"{amount/1000:.1f}K🍊"
    return f"{amount}🍊"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    try:
        if not update.message:
            return
        
        user_id = update.effective_user.id
        log_info(f"User {user_id} started bot")
        await database.get_user(user_id)  # Создаем пользователя если его нет
        
        text = """🎄✨ *Добро пожаловать на Московскую зимнюю ярмарку!* ✨🎄

━━━━━━━━━━━━━━━━━━━━

🌟 Ты — организатор самой волшебной ярмарки Москвы!

✨ *Что тебя ждёт:*
   🎪 Открывай павильоны
   👥 Обслуживай гостей
   💰 Зарабатывай мандаринки
   📚 Узнавай интересные факты о Москве

━━━━━━━━━━━━━━━━━━━━

💰 *Твой стартовый капитал:* 🍊 50 мандаринок

━━━━━━━━━━━━━━━━━━━━

✨ *Готов начать?*"""
        
        keyboard = [[InlineKeyboardButton("🎪 Открыть ярмарку", callback_data="menu")]]
        
        await update.message.reply_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    except BadRequest as e:
        # Если Markdown не работает, пробуем без него
        log_warning(f"Markdown error in start_command, trying without", {"error": str(e)})
        try:
            await update.message.reply_text(
                text=text.replace('*', '').replace('_', ''),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e2:
            log_error(e2, "start_command fallback")
    except Exception as e:
        log_error(e, "start_command")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик всех inline-кнопок"""
    try:
        query = update.callback_query
        if not query:
            return
        
        await query.answer()
        
        if not query.data:
            return
        
        data = query.data.split(":")
        if not data or len(data) == 0:
            return
        
        action = data[0]
        log_info(f"Button action: {action}", {"user_id": query.from_user.id, "data": query.data})
        
        # ГЛАВНОЕ МЕНЮ
        if action == "menu":
            user_id = query.from_user.id
            user_coins = await database.get_user_coins(user_id)
            open_pavilions = await database.get_open_pavilions(user_id)
            if 1 not in open_pavilions:  # Автоматически открываем первый павильон
                await database.open_pavilion(user_id, 1)
                open_pavilions = await database.get_open_pavilions(user_id)
            open_count = len(open_pavilions)
            
            collected_facts = await database.get_collected_facts(user_id)
            facts_count = len(collected_facts)
            
            # Прогресс-бары
            pavilions_progress = create_progress_bar(open_count, 7)
            facts_progress = create_progress_bar(facts_count, 75)
            
            text = f"""🎄✨ *Московская зимняя ярмарка* ✨🎄

💰 *Твой капитал:* {format_coins(user_coins)}

━━━━━━━━━━━━━━━━━━━━

🎪 *Павильоны:* {open_count}/7
{pavilions_progress}

📚 *Факты:* {facts_count}/75
{facts_progress}

━━━━━━━━━━━━━━━━━━━━

✨ *Что дальше?*"""
            
            keyboard = [
                [InlineKeyboardButton("🗺 Карта ярмарки", callback_data="map")],
                [InlineKeyboardButton("📖 Моя коллекция", callback_data="collection")]
            ]
            
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        
        # КАРТА ЯРМАРКИ
        elif action == "map":
            user_id = query.from_user.id
            user_coins = await database.get_user_coins(user_id)
            pavilions = await database.get_all_pavilions()
            user_pavilions = await database.get_open_pavilions(user_id)
            
            text = f"""🗺 *Карта Московской зимней ярмарки* 🗺

❄️ Снег падает на огоньки павильонов...
☕ Пахнет глинтвейном и мандаринами...
🎄 В воздухе витает предновогоднее волшебство...

━━━━━━━━━━━━━━━━━━━━

💰 *У тебя:* {format_coins(user_coins)}

━━━━━━━━━━━━━━━━━━━━

📍 *Выбери павильон:*"""
            
            keyboard = []
            for pav in pavilions:
                if pav['id'] in user_pavilions:
                    btn = InlineKeyboardButton(
                        f"✅ {pav['emoji']} {pav['name']}",
                        callback_data=f"pav_enter:{pav['id']}"
                    )
                else:
                    btn = InlineKeyboardButton(
                        f"🔒 {pav['emoji']} {pav['name']} · {pav['price']}🍊",
                        callback_data=f"pav_view:{pav['id']}"
                    )
                keyboard.append([btn])
            
            keyboard.append([InlineKeyboardButton("⬅️ В меню", callback_data="menu")])
            
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        
        # ПРОСМОТР ЗАКРЫТОГО ПАВИЛЬОНА
        elif action == "pav_view":
            pav_id = int(data[1])
            pav = await database.get_pavilion(pav_id)
            user_id = query.from_user.id
            user_coins = await database.get_user_coins(user_id)
            
            text = f"""{pav['emoji']} *{pav['name']}*

{pav['description']}

💫 *{pav['atmosphere']}*

━━━━━━━━━━━━━━━━━━━━

💰 *Стоимость:* {format_coins(pav['price'])}
🍊 *У тебя:* {format_coins(user_coins)}"""
            
            keyboard = []
            
            if user_coins >= pav['price']:
                text += "\n\n━━━━━━━━━━━━━━━━━━━━\n\n✅ *Можно открыть!*"
                keyboard.append([
                    InlineKeyboardButton(
                        f"✅ Открыть за {format_coins(pav['price'])}",
                        callback_data=f"pav_buy:{pav_id}"
                    )
                ])
            else:
                needed = pav['price'] - user_coins
                text += f"\n\n━━━━━━━━━━━━━━━━━━━━\n\n❌ *Не хватает:* {format_coins(needed)}\n\n💡 Выполняй задания, чтобы заработать!"
            
            keyboard.append([InlineKeyboardButton("⬅️ Назад на карту", callback_data="map")])
            
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        
        # ПОКУПКА ПАВИЛЬОНА
        elif action == "pav_buy":
            if len(data) < 2:
                await query.answer("❌ Ошибка данных", show_alert=True)
                return
            try:
                pav_id = int(data[1])
            except (ValueError, IndexError):
                await query.answer("❌ Ошибка данных", show_alert=True)
                return
            pav = await database.get_pavilion(pav_id)
            if not pav:
                await query.answer("❌ Павильон не найден", show_alert=True)
                return
            user_id = query.from_user.id
            
            user_coins = await database.get_user_coins(user_id)
            if user_coins < pav['price']:
                await query.answer("❌ Недостаточно мандаринок!", show_alert=True)
                return
            
            # Списываем монеты и открываем павильон
            await database.subtract_coins(user_id, pav['price'])
            await database.open_pavilion(user_id, pav_id)
            
            new_coins = await database.get_user_coins(user_id)
            
            text = f"""🎉✨ *ПАВИЛЬОН ОТКРЫТ!* ✨🎉

{pav['emoji']} *{pav['name']}*

━━━━━━━━━━━━━━━━━━━━

🎊 Поздравляем! Теперь ты можешь:
   👥 Обслуживать гостей
   💰 Зарабатывать мандаринки
   📚 Собирать интересные факты

━━━━━━━━━━━━━━━━━━━━

💰 *Осталось:* {format_coins(new_coins)}"""
            
            keyboard = [
                [InlineKeyboardButton(f"{pav['emoji']} Войти в павильон", callback_data=f"pav_enter:{pav_id}")],
                [InlineKeyboardButton("🗺 На карту", callback_data="map")]
            ]
            
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        
        # ВХОД В ПАВИЛЬОН
        elif action == "pav_enter":
            if len(data) < 2:
                await query.answer("❌ Ошибка данных", show_alert=True)
                return
            try:
                pav_id = int(data[1])
            except (ValueError, IndexError):
                await query.answer("❌ Ошибка данных", show_alert=True)
                return
            pav = await database.get_pavilion(pav_id)
            if not pav:
                await query.answer("❌ Павильон не найден", show_alert=True)
                return
            tasks = await database.get_pavilion_tasks(pav_id)
            user_id = query.from_user.id
            user_coins = await database.get_user_coins(user_id)
            
            text = f"""{pav['emoji']} *{pav['name']}*
📍 {pav['location']}

━━━━━━━━━━━━━━━━━━━━

💫 *{pav['atmosphere']}*

{pav['description']}

━━━━━━━━━━━━━━━━━━━━

💰 *Награда:* +{format_coins(pav['reward'])} за задание
🍊 *У тебя:* {format_coins(user_coins)}

━━━━━━━━━━━━━━━━━━━━

✨ *Чем займёшься?*"""
            
            keyboard = []
            for task in tasks:
                keyboard.append([
                    InlineKeyboardButton(
                        f"{task['emoji']} {task['name']}",
                        callback_data=f"task_start:{pav_id}:{task['id']}"
                    )
                ])
            
            keyboard.append([InlineKeyboardButton("⬅️ На карту ярмарки", callback_data="map")])
            
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        
        # НАЧАЛО ЗАДАНИЯ
        elif action == "task_start":
            if len(data) < 3:
                await query.answer("❌ Ошибка данных", show_alert=True)
                return
            try:
                pav_id = int(data[1])
                task_id = int(data[2])
            except (ValueError, IndexError) as e:
                log_error(e, f"task_start int conversion")
                await query.answer("❌ Ошибка данных", show_alert=True)
                return
            
            task = await database.get_task(task_id)
            
            if not task:
                log_warning(f"Task not found", {"task_id": task_id})
                await query.answer("❌ Задание не найдено", show_alert=True)
                return
            
            if task['type'] == 'reaction':
                await tasks_handler.start_reaction_task(query, pav_id, task_id, context)
            elif task['type'] == 'choice':
                await tasks_handler.start_choice_task(query, pav_id, task_id, context)
            elif task['type'] == 'sequence':
                await tasks_handler.start_sequence_task(query, pav_id, task_id, context)
        
        # РЕАКЦИЯ НА ЗАДАНИЕ - ожидание
        elif action == "task_reaction_wait":
            if len(data) < 2:
                return
            try:
                task_id = int(data[1])
            except (ValueError, IndexError):
                return
            await query.answer("⏳ Подожди...", show_alert=False)
        
        # РЕАКЦИЯ НА ЗАДАНИЕ - нажатие
        elif action == "task_reaction_hit":
            task_id = int(data[1])
            state_key = f"{query.from_user.id}:{task_id}"
            
            # Проверяем состояние задания
            if state_key not in tasks_handler.task_states:
                await query.answer("❌ Задание не найдено. Начните заново.", show_alert=True)
                return
            
            if tasks_handler.task_states[state_key].get("ready"):
                # Успех! Показываем анимацию
                await query.answer("🎉 Отлично! Идеальный момент!", show_alert=False)
                # Небольшая задержка для эффекта
                await asyncio.sleep(0.3)
                await complete_task(query, task_id)
            else:
                # Провал - слишком рано или поздно
                pav_id = tasks_handler.task_states[state_key].get("pavilion_id", 1)
                task = await database.get_task(task_id)
                task_name = task['name'] if task else "задание"
                
                await query.answer("⏰ Не тот момент! Попробуй ещё раз.", show_alert=True)
                # Возвращаем в павильон с более понятным сообщением
                await query.edit_message_text(
                    text=f"""❌ *Время не то*

⏰ Слишком рано или поздно
👀 Следи внимательнее за сигналом

🎯 *Попробуй снова*""",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔄 Попробовать снова", callback_data=f"task_start:{pav_id}:{task_id}"),
                        InlineKeyboardButton("⬅️ Назад в павильон", callback_data=f"pav_enter:{pav_id}")
                    ]]),
                    parse_mode='Markdown'
                )
        
        # ВЫБОР В ЗАДАНИИ
        elif action == "task_choice":
            if len(data) < 2:
                await query.answer("❌ Ошибка данных", show_alert=True)
                return
            task_id = int(data[1])
            choice = data[2] if len(data) > 2 else ""
            
            state_key = f"{query.from_user.id}:{task_id}"
            task = await database.get_task(task_id)
            pav_id = tasks_handler.task_states.get(state_key, {}).get("pavilion_id", 1)
            
            # Обработка специфичных заданий
            if task_id == 1:  # Подобрать варежки
                if choice == "red":
                    await query.answer("✅ Идеально! Клиент доволен!", show_alert=False)
                    await asyncio.sleep(0.3)
                    await complete_task(query, task_id)
                else:
                    await query.answer("❌ Не тот цвет! Клиент просил красные. Попробуй ещё раз.", show_alert=True)
            
            elif task_id == 4:  # Найти нужный размер
                if choice == "M":
                    await query.answer("✅ Отлично! Размер M - именно то, что нужно!", show_alert=False)
                    await asyncio.sleep(0.3)
                    await complete_task(query, task_id)
                else:
                    await query.answer(f"❌ Не тот размер! Клиент просил размер M, а ты выбрал {choice}. Попробуй ещё раз.", show_alert=True)
            
            elif task_id == 15:  # Собрать порцию мороженого - шаг 1 (choice) переходит в sequence
                if state_key not in tasks_handler.task_states:
                    tasks_handler.task_states[state_key] = {"step": 1, "pavilion_id": pav_id, "task_id": task_id, "choices": [choice]}
                else:
                    tasks_handler.task_states[state_key]["choices"].append(choice)
                # Переходим к следующему шагу (sequence)
                await tasks_handler.show_icecream_sequence_continue(query, 1)
            
            elif task_id == 19:  # Добавить топпинг
                await complete_task(query, task_id)
            
            elif task_id == 22:  # Повесить шары
                await complete_task(query, task_id)
            
            elif task_id == 24:  # Упаковать свечи
                await complete_task(query, task_id)
            
            elif task_id == 29:  # Сложить пряники
                await complete_task(query, task_id)
            
            elif task_id == 31:  # Добавить варенье
                await complete_task(query, task_id)
            
            elif task_id == 32:  # Украсить пряник
                await complete_task(query, task_id)
            
            elif task_id == 36:  # Заварить чай
                await complete_task(query, task_id)
            
            elif task_id == 44:  # Собрать чайную пару
                await complete_task(query, task_id)
            
            elif task_id == 45:  # Выбрать варенье
                await complete_task(query, task_id)
            
            elif task_id == 46:  # Найти редкий сорт
                if choice == "found":
                    await complete_task(query, task_id)
                else:
                    await query.answer("Продолжай искать...", show_alert=False)
            
            elif task_id == 48:  # Завернуть бумагу
                await complete_task(query, task_id)
            
            elif task_id == 50:  # Написать пожелание
                await complete_task(query, task_id)
            
            elif task_id == 54:  # Украсить декором
                if state_key not in tasks_handler.task_states:
                    tasks_handler.task_states[state_key] = {"choices": []}
                if choice != "done":
                    tasks_handler.task_states[state_key]["choices"].append(choice)
                    await tasks_handler.show_decor_choice(query)
                else:
                    if len(tasks_handler.task_states[state_key]["choices"]) == 2:
                        await complete_task(query, task_id)
                    else:
                        await query.answer("Нужно выбрать 2 элемента!", show_alert=True)
            
            elif task_id == 57:  # Выбрать открытку
                await complete_task(query, task_id)
            
            elif task_id == 59:  # Финальный штрих
                await complete_task(query, task_id)
            
            elif task_id == 7:  # Листать свитера
                if choice == "found":
                    await complete_task(query, task_id)
                else:
                    await query.answer("Продолжай искать...", show_alert=False)
            
            elif task_id == 8:  # Выбрать размер
                if choice == "M":
                    await complete_task(query, task_id)
                else:
                    await query.answer("❌ Не тот размер!", show_alert=True)
            
            elif task_id == 9:  # Примерить шапку
                await complete_task(query, task_id)
            
            elif task_id == 14:  # Выбрать цветовую гамму
                if state_key not in tasks_handler.task_states:
                    tasks_handler.task_states[state_key] = {"choices": []}
                if choice != "done":
                    tasks_handler.task_states[state_key]["choices"].append(choice)
                    await tasks_handler.show_color_scheme_choice(query)
                else:
                    if len(tasks_handler.task_states[state_key]["choices"]) == 3:
                        await complete_task(query, task_id)
                    else:
                        await query.answer("Нужно выбрать 3 вещи!", show_alert=True)
            
            else:
                await complete_task(query, task_id)
        
        # ПОСЛЕДОВАТЕЛЬНОСТЬ В ЗАДАНИИ
        elif action == "task_sequence":
            if len(data) < 3:
                await query.answer("❌ Ошибка данных", show_alert=True)
                return
            task_id = int(data[1])
            step = int(data[2])
            choice = data[3] if len(data) > 3 else ""
            
            state_key = f"{query.from_user.id}:{task_id}"
            task = await database.get_task(task_id)
            pav_id = tasks_handler.task_states.get(state_key, {}).get("pavilion_id", 1)
            
            # Обработка специфичных последовательностей
            if task_id == 2:  # Собрать набор для катания
                if step == 3:
                    await complete_task(query, task_id)
                else:
                    await tasks_handler.show_skating_set_sequence(query, step + 1)
            
            elif task_id == 5:  # Добавить грелки
                if step == 2:
                    await complete_task(query, task_id)
                else:
                    await tasks_handler.show_handwarmers_sequence(query, step + 1)
            
            elif task_id == 11:  # Собрать образ
                if step == 3:
                    await complete_task(query, task_id)
                else:
                    await tasks_handler.show_outfit_sequence(query, step + 1)
            
            elif task_id == 13:  # Подобрать аксессуары
                if step == 2:
                    await complete_task(query, task_id)
                else:
                    await tasks_handler.show_accessories_sequence(query, step + 1)
            
            elif task_id == 15:  # Собрать порцию мороженого - продолжение (после выбора топпинга)
                # Завершаем задание
                await complete_task(query, task_id)
            
            elif task_id == 25:  # Размотать гирлянду
                if state_key not in tasks_handler.task_states:
                    tasks_handler.task_states[state_key] = {"count": 0}
                if choice == "unwind":
                    tasks_handler.task_states[state_key]["count"] += 1
                    await tasks_handler.show_garland_unwind_sequence(query, 1)
                elif choice == "done":
                    await complete_task(query, task_id)
            
            elif task_id == 26:  # Наполнить вазу
                if state_key not in tasks_handler.task_states:
                    tasks_handler.task_states[state_key] = {"count": 0}
                if choice == "add":
                    tasks_handler.task_states[state_key]["count"] += 1
                    await tasks_handler.show_mandarin_vase_sequence(query, 1)
                elif choice == "done":
                    await complete_task(query, task_id)
            
            elif task_id == 28:  # Зажечь свечи
                if state_key not in tasks_handler.task_states:
                    tasks_handler.task_states[state_key] = {"count": 0}
                if choice == "light":
                    tasks_handler.task_states[state_key]["count"] += 1
                    await tasks_handler.show_candles_light_sequence(query, 1)
                elif choice == "done":
                    await complete_task(query, task_id)
            
            elif task_id == 34:  # Собрать микс конфет
                if state_key not in tasks_handler.task_states:
                    tasks_handler.task_states[state_key] = {"red": 0, "blue": 0, "green": 0, "yellow": 0}
                if choice in ["red", "blue", "green", "yellow"]:
                    tasks_handler.task_states[state_key][choice] += 1
                    await tasks_handler.show_candy_mix_sequence(query, 1)
                elif choice == "done":
                    await complete_task(query, task_id)
            
            elif task_id == 39:  # Собрать набор "Москва"
                if step == 3:
                    await complete_task(query, task_id)
                else:
                    await tasks_handler.show_moscow_set_sequence(query, step + 1)
            
            elif task_id == 41:  # Разлить по чашкам
                if state_key not in tasks_handler.task_states:
                    tasks_handler.task_states[state_key] = {"count": 0}
                if choice == "pour":
                    tasks_handler.task_states[state_key]["count"] += 1
                    await tasks_handler.show_tea_pour_sequence(query, 1)
                elif choice == "done":
                    await complete_task(query, task_id)
            
            elif task_id == 42:  # Помешать сахар
                if state_key not in tasks_handler.task_states:
                    tasks_handler.task_states[state_key] = {"count": 0}
                if choice == "stir":
                    tasks_handler.task_states[state_key]["count"] += 1
                    await tasks_handler.show_sugar_stir_sequence(query, 1)
                elif choice == "done":
                    await complete_task(query, task_id)
            
            elif task_id == 47:  # Упаковать подарок
                if step == 5:
                    await complete_task(query, task_id)
                else:
                    await tasks_handler.show_gift_wrap_sequence(query, step + 1)
            
            elif task_id == 53:  # Разгладить складки
                if state_key not in tasks_handler.task_states:
                    tasks_handler.task_states[state_key] = {"count": 0}
                if choice == "smooth":
                    tasks_handler.task_states[state_key]["count"] += 1
                    await tasks_handler.show_smooth_folds_sequence(query, 1)
                elif choice == "done":
                    await complete_task(query, task_id)
            
            else:
                await complete_task(query, task_id)
        
        # ОТМЕНА ЗАДАНИЯ
        elif action == "task_cancel":
            if len(data) < 2:
                await query.answer("❌ Ошибка данных", show_alert=True)
                return
            task_id = int(data[1])
            state_key = f"{query.from_user.id}:{task_id}"
            pav_id = tasks_handler.task_states.get(state_key, {}).get("pavilion_id", 1)
            
            # Удаляем состояние
            if state_key in tasks_handler.task_states:
                del tasks_handler.task_states[state_key]
            
            # Возвращаем в павильон
            await query.edit_message_text(
                text="❌ Задание отменено",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("⬅️ Назад в павильон", callback_data=f"pav_enter:{pav_id}")
                ]])
            )
        
        # ЗАВЕРШЕНИЕ ЗАДАНИЯ
        elif action == "task_done":
            task_id = int(data[1])
            await complete_task(query, task_id)
        
        # ПОКАЗ ФАКТА
        elif action == "fact":
            if len(data) < 3:
                await query.answer("❌ Ошибка данных", show_alert=True)
                return
            pav_id = int(data[1])
            task_id = int(data[2])
            
            task = await database.get_task(task_id)
            fact = await database.get_fact(task['fact_id'])
            user_id = query.from_user.id
            
            # Сохраняем факт в коллекцию
            await database.add_fact_to_collection(user_id, fact['id'])
            
            user_coins = await database.get_user_coins(user_id)
            
            text = f"""❄️✨ *Интересный факт* ✨❄️

━━━━━━━━━━━━━━━━━━━━

💡 *"{fact['text']}"*

━━━━━━━━━━━━━━━━━━━━

✅ Факт сохранён в коллекцию! 📚

💰 *У тебя:* {format_coins(user_coins)}"""
            
            keyboard = [
                [InlineKeyboardButton("➡️ Ещё задание", callback_data=f"pav_enter:{pav_id}")],
                [InlineKeyboardButton("🗺 На карту", callback_data="map")]
            ]
            
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        
        # КОЛЛЕКЦИЯ
        elif action == "collection":
            user_id = query.from_user.id
            collected_facts = await database.get_collected_facts(user_id)
            facts_count = len(collected_facts)
            user_coins = await database.get_user_coins(user_id)
            
            facts_progress = create_progress_bar(facts_count, 75)
            
            text = f"""📖✨ *Моя коллекция* ✨📖

━━━━━━━━━━━━━━━━━━━━

📚 *Фактов собрано:* {facts_count}/75
{facts_progress}

💰 *Всего заработано:* {format_coins(user_coins)}

━━━━━━━━━━━━━━━━━━━━

✨ *Что посмотрим?*"""
            
            keyboard = [
                [InlineKeyboardButton("📚 Факты по павильонам", callback_data="facts_menu")],
                [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
                [InlineKeyboardButton("⬅️ В меню", callback_data="menu")]
            ]
            
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        
        # МЕНЮ ФАКТОВ
        elif action == "facts_menu":
            user_id = query.from_user.id
            collected_facts = await database.get_collected_facts(user_id)
            pavilions = await database.get_all_pavilions()
            
            text = """📚✨ *Собранные факты* ✨📚

━━━━━━━━━━━━━━━━━━━━

📍 *Выбери павильон:*"""
            
            keyboard = []
            for pav in pavilions:
                pav_facts = await database.get_pavilion_facts(pav['id'])
                collected_pav_facts = [f for f in collected_facts if any(pf['id'] == f for pf in pav_facts)]
                count = len(collected_pav_facts)
                total = len(pav_facts)
                
                status = "✅" if count == total else ""
                keyboard.append([
                    InlineKeyboardButton(
                        f"{status} {pav['emoji']} {pav['name']} · {count}/{total}",
                        callback_data=f"facts_pav:{pav['id']}"
                    )
                ])
            
            keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="collection")])
            
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        
        # ФАКТЫ ПАВИЛЬОНА
        elif action == "facts_pav":
            if len(data) < 2:
                await query.answer("❌ Ошибка данных", show_alert=True)
                return
            pav_id = int(data[1])
            pav = await database.get_pavilion(pav_id)
            user_id = query.from_user.id
            collected_facts = await database.get_collected_facts(user_id)
            pav_facts = await database.get_pavilion_facts(pav_id)
            
            collected_pav_facts = [pf for pf in pav_facts if pf['id'] in collected_facts]
            count = len(collected_pav_facts)
            total = len(pav_facts)
            
            facts_progress = create_progress_bar(count, total)
            
            if count == 0:
                text = f"""📚 *Факты:* {pav['emoji']} {pav['name']}

━━━━━━━━━━━━━━━━━━━━

📊 *Собрано:* {count}/{total}
{facts_progress}

━━━━━━━━━━━━━━━━━━━━

💡 Пока нет собранных фактов.
✨ Выполняй задания в этом павильоне!"""
            else:
                text = f"""📚 *Факты:* {pav['emoji']} {pav['name']}

━━━━━━━━━━━━━━━━━━━━

📊 *Собрано:* {count}/{total} {'✅' if count == total else '📝'}
{facts_progress}

━━━━━━━━━━━━━━━━━━━━

"""
                for i, fact in enumerate(collected_pav_facts, 1):
                    text += f"💡 *Факт {i}:*\n\"{fact['text']}\"\n\n"
                    if i < len(collected_pav_facts):
                        text += "━━━━━━━━━━━━━━━━━━━━\n\n"
            
            keyboard = [[InlineKeyboardButton("⬅️ К павильонам", callback_data="facts_menu")]]
            
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        
        # СТАТИСТИКА
        elif action == "stats":
            user_id = query.from_user.id
            stats = await database.get_user_stats(user_id)
            open_pavilions = await database.get_open_pavilions(user_id)
            
            pavilions_progress = create_progress_bar(stats['pavilions_open'], 7)
            facts_progress = create_progress_bar(stats['facts_collected'], 75)
            
            text = f"""📊✨ *Твоя статистика* ✨📊

━━━━━━━━━━━━━━━━━━━━

💰 *Всего заработано:* {format_coins(stats['coins_earned'])}
👥 *Посетителей обслужено:* {stats['guests_served']}

━━━━━━━━━━━━━━━━━━━━

🎪 *Павильонов открыто:* {stats['pavilions_open']}/7
{pavilions_progress}

📚 *Фактов собрано:* {stats['facts_collected']}/75
{facts_progress}

━━━━━━━━━━━━━━━━━━━━

🔥 *Заданий выполнено:* {stats['tasks_completed']}"""
            
            keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="collection")]]
            
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
    except BadRequest as e:
        # Ошибка редактирования сообщения (например, сообщение не изменилось)
        log_error(e, f"button_handler BadRequest action={action}")
        try:
            await query.answer("⚠️ Сообщение уже обновлено", show_alert=False)
        except:
            pass
    except RetryAfter as e:
        # Превышен лимит запросов
        log_error(e, f"button_handler RetryAfter action={action}")
        try:
            await query.answer(f"⏳ Слишком много запросов. Подожди {e.retry_after} сек.", show_alert=True)
        except:
            pass
    except (NetworkError, TimedOut) as e:
        # Проблемы с сетью
        log_error(e, f"button_handler NetworkError action={action}")
        try:
            await query.answer("🌐 Проблемы с сетью. Попробуй позже.", show_alert=True)
        except:
            pass
    except Exception as e:
        # Другие ошибки
        log_error(e, f"button_handler action={action}")
        try:
            await query.answer("❌ Произошла ошибка. Попробуйте позже.", show_alert=True)
        except:
            pass

async def complete_task(query, task_id: int):
    """Завершение задания и начисление награды"""
    task = await database.get_task(task_id)
    if not task:
        log_warning(f"Task not found in complete_task", {"task_id": task_id})
        await query.answer("❌ Задание не найдено", show_alert=True)
        return
    
    pav = await database.get_pavilion(task['pavilion_id'])
    if not pav:
        log_warning(f"Pavilion not found in complete_task", {"pavilion_id": task.get('pavilion_id')})
        await query.answer("❌ Павильон не найден", show_alert=True)
        return
    
    user_id = query.from_user.id
    
    # Начисляем награду
    await database.add_coins(user_id, pav['reward'])
    await database.increment_tasks_completed(user_id)
    await database.increment_guests_served(user_id)
    
    new_coins = await database.get_user_coins(user_id)
    
    # Сообщения успеха для разных заданий
    success_messages = {
        1: "Варежки подобраны идеально! Клиент доволен! 😊",
        2: "Набор для катания собран! Готов к зимним развлечениям! ⛸️",
        3: "Температура комфортная! Посетитель счастлив! 😊",
        15: "Пломбир с топпингом в хрустящем вафельном рожке готов! Девочка счастлива! 🍦✨",
        47: "Подарок выглядит как произведение искусства! Молодой человек в восторге! 🎁✨",
        38: "Чай заварен как надо — ароматный, согревающий, с легкой остротой имбиря. Посетитель доволен! 😊"
    }
    
    success_msg = success_messages.get(task_id, f"✅ Отлично! {task['name']} выполнено!")
    
    # Анимация успеха
    success_emojis = ["🎉", "✨", "🌟", "💫", "⭐"]
    success_emoji = success_emojis[task_id % len(success_emojis)]
    
    text = f"""{success_emoji} *{success_msg}* {success_emoji}

━━━━━━━━━━━━━━━━━━━━

💰 *Награда:* +{format_coins(pav['reward'])}
🍊 *Всего:* {format_coins(new_coins)}

━━━━━━━━━━━━━━━━━━━━

📚 *Хочешь узнать интересный факт?*"""
    
    keyboard = [[InlineKeyboardButton("📚 Узнать факт", callback_data=f"fact:{pav['id']}:{task_id}")]]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    log_info(f"Task completed", {"user_id": user_id, "task_id": task_id, "reward": pav['reward']})
    
    # Удаляем состояние задания
    state_key = f"{user_id}:{task_id}"
    if state_key in tasks_handler.task_states:
        del tasks_handler.task_states[state_key]

def main():
    """Запуск бота"""
    try:
        log_info("=" * 50)
        log_info("🎄 Бот 'Московская зимняя ярмарка' запускается...")
        
        # Инициализация
        log_info("Инициализация базы данных...")
        asyncio.run(init())
        log_info("База данных инициализирована")
        
        # Создание приложения
        log_info("Создание приложения...")
        bot_token = get_bot_token()  # Проверка токена при запуске
        application = Application.builder().token(bot_token).build()
        
        # Регистрация обработчиков
        # Порядок важен: более специфичные обработчики должны быть первыми
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(CommandHandler("start", start_command))
        
        # Запуск бота
        from datetime import datetime
        log_info("🎄 Бот 'Московская зимняя ярмарка' запущен!")
        log_info("📡 Ожидание обновлений...")
        print("🎄 Бот 'Московская зимняя ярмарка' запущен!")
        print("📡 Ожидание обновлений...")
        print(f"📝 Логи: logs/bot_{datetime.now().strftime('%Y-%m-%d')}.log")
        
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True  # Игнорируем старые обновления при перезапуске
        )
    except KeyboardInterrupt:
        log_info("Бот остановлен пользователем")
        print("\n⏹ Бот остановлен")
    except Exception as e:
        log_error(e, "main")
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

