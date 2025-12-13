"""Обработчики заданий разных типов"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import random
import asyncio
import database

# Хранилище состояний заданий (в продакшене лучше использовать Redis)
task_states = {}

def ensure_task_state(state_key: str, pavilion_id: int, task_id: int):
    """Убедиться, что состояние задания создано и инициализировано"""
    if state_key not in task_states:
        task_states[state_key] = {
            "step": 1,
            "pavilion_id": pavilion_id,
            "task_id": task_id,
            "start_time": None,
            "ready": False
        }
    return task_states[state_key]

async def start_reaction_task(query, pavilion_id: int, task_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Запуск задания типа 'reaction' (реакция на время)"""
    task = await database.get_task(task_id)
    pav = await database.get_pavilion(pavilion_id)
    
    # Сохраняем состояние
    state_key = f"{query.from_user.id}:{task_id}"
    task_states[state_key] = {
        "step": 1,
        "pavilion_id": pavilion_id,
        "task_id": task_id,
        "start_time": None
    }
    
    # Генерируем параметры задания
    if task_id == 3:  # Проверить термометр
        await show_thermometer_task(query, context)
    elif task_id == 6:  # Пробить чек
        await show_cash_register_task(query, context)
    elif task_id == 16:  # Сделать эспрессо
        await show_espresso_task(query, context)
    elif task_id == 17:  # Налить какао
        await show_cocoa_task(query, context)
    elif task_id == 18:  # Прогреть вафельный рожок
        await show_waffle_task(query, context)
    elif task_id == 20:  # Взбить молоко
        await show_milk_task(query, context)
    elif task_id == 23:  # Проверить гирлянду
        await show_garland_task(query, context)
    elif task_id == 27:  # Проверить снежный шар
        await show_snowball_task(query, context)
    elif task_id == 30:  # Отмерить 500г
        await show_scale_task(query, context)
    elif task_id == 33:  # Достать из духовки
        await show_oven_task(query, context)
    elif task_id == 38:  # Заварить имбирный чай
        await show_tea_heating_task(query, context)
    elif task_id == 40:  # Дождаться кипения
        await show_boiling_task(query, context)
    elif task_id == 43:  # Проверить заварку
        await show_brew_task(query, context)
    elif task_id == 10:  # Проверить ткань
        await show_fabric_task(query, context)
    elif task_id == 12:  # Упаковать в пакет
        await show_pack_bag_task(query, context)
    elif task_id == 21:  # Вставить трубочку
        await show_straw_task(query, context)
    elif task_id == 35:  # Завязать ленту
        await show_tie_ribbon_task(query, context)
    elif task_id == 37:  # Закрыть коробку
        await show_close_box_task(query, context)
    elif task_id == 51:  # Добавить веточку
        await show_add_branch_task(query, context)
    elif task_id == 52:  # Отрезать ленту
        await show_cut_ribbon_task(query, context)
    elif task_id == 55:  # Остановить конвейер
        await show_stop_conveyor_task(query, context)
    elif task_id == 56:  # Посыпать снегом
        await show_sprinkle_snow_task(query, context)
    elif task_id == 58:  # Отмерить ленту
        await show_measure_ribbon_task(query, context)
    else:
        # Универсальный обработчик
        await show_generic_reaction_task(query, task, context)

async def show_thermometer_task(query, context: ContextTypes.DEFAULT_TYPE):
    """Задание: Проверить термометр"""
    text = """🌡 *Проверить термометр*

❄️ В павильоне прохладно
🌡️ Термометр на стене показывает температуру
🔥 Отопление работает, температура медленно поднимается

Дождись комфортной температуры (22°C).

🌡️ *15°C...* ❄️"""
    
    keyboard = [[InlineKeyboardButton("⏳ Подождать...", callback_data=f"task_reaction_wait:3")]]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    # Запускаем таймер
    state_key = f"{query.from_user.id}:3"
    state = ensure_task_state(state_key, 1, 3)
    state["start_time"] = asyncio.get_event_loop().time()
    state["ready"] = False  # Сбрасываем ready
    
    # Через 2 секунды обновляем
    await asyncio.sleep(2)
    if state_key in task_states and not task_states[state_key].get("ready", False):
        text = """🌡 *Проверить термометр*

🔥 Теплее становится...
🌡️ *25°C...*

⏳ Ждем идеальной температуры..."""
        
        keyboard = [[InlineKeyboardButton("⏳ Ещё рано...", callback_data=f"task_reaction_wait:3")]]
        
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            pass
        
        # Ещё через 2 секунды - момент нажатия
        await asyncio.sleep(2)
        if state_key in task_states:
            text = """🌡 *Проверить термометр*

✨ Идеальная температура!
🌡️ *22°C* ✅

⚡ *СЕЙЧАС!*"""
            
            keyboard = [
                [InlineKeyboardButton("✅ НАЖАТЬ!", callback_data=f"task_reaction_hit:3")],
                [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:3")]
            ]
            
            try:
                await query.edit_message_text(
                    text=text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                if state_key in task_states:
                    task_states[state_key]["ready"] = True
            except:
                pass

async def show_tea_heating_task(query, context: ContextTypes.DEFAULT_TYPE):
    """Задание: Заварить имбирный чай"""
    text = """🫖 Заварить имбирный чай

Посетитель заказал согревающий имбирный чай. Нужно нагреть воду до идеальной температуры!

Следи за термометром! 🌡️

━━━━━━━━━━━━━━━━

Температура: 25°C..."""
    
    keyboard = [[InlineKeyboardButton("⏳ Подождать...", callback_data=f"task_reaction_wait:38")]]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    state_key = f"{query.from_user.id}:38"
    state = ensure_task_state(state_key, 6, 38)
    state["start_time"] = asyncio.get_event_loop().time()
    state["ready"] = False
    
    await asyncio.sleep(2)
    if state_key in task_states:
        text = """🫖 Заварить имбирный чай

Температура: 55°C..."""
        
        keyboard = [[InlineKeyboardButton("⏳ Ещё рано...", callback_data=f"task_reaction_wait:38")]]
        
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            pass
        
        await asyncio.sleep(2)
        if state_key in task_states:
            text = """🫖 Заварить имбирный чай

Температура: 88°C... 🔥

⚡ СЕЙЧАС!"""
            
            keyboard = [
                [InlineKeyboardButton("🔥 НАЖАТЬ!", callback_data=f"task_reaction_hit:38")],
                [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:38")]
            ]
            
            try:
                await query.edit_message_text(
                    text=text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                if state_key in task_states:
                    task_states[state_key]["ready"] = True
            except:
                pass

async def show_cash_register_task(query, context: ContextTypes.DEFAULT_TYPE):
    """Задание: Пробить чек"""
    text = """📦 Пробить чек

На кассе нужно пробить чек на сумму 1000₽.

Следи за суммой! 💰

━━━━━━━━━━━━━━━━

Сумма: 250₽..."""
    
    keyboard = [[InlineKeyboardButton("⏳ Подождать...", callback_data=f"task_reaction_wait:6")]]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    state_key = f"{query.from_user.id}:6"
    state = ensure_task_state(state_key, 1, 6)
    state["start_time"] = asyncio.get_event_loop().time()
    state["ready"] = False
    
    await asyncio.sleep(1.5)
    if state_key in task_states:
        text = """📦 Пробить чек

Сумма: 650₽..."""
        
        keyboard = [[InlineKeyboardButton("⏳ Ещё рано...", callback_data=f"task_reaction_wait:6")]]
        
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            pass
        
        await asyncio.sleep(1.5)
        if state_key in task_states:
            text = """📦 Пробить чек

Сумма: 1000₽... ✅

⚡ СЕЙЧАС!"""
            
            keyboard = [
                [InlineKeyboardButton("✅ НАЖАТЬ!", callback_data=f"task_reaction_hit:6")],
                [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:6")]
            ]
            
            try:
                await query.edit_message_text(
                    text=text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                if state_key in task_states:
                    task_states[state_key]["ready"] = True
            except:
                pass

async def show_espresso_task(query, context: ContextTypes.DEFAULT_TYPE):
    """Задание: Сделать эспрессо"""
    text = """☕️ Сделать эспрессо

Кофе-машина готовит эспрессо. Следи за индикатором!

━━━━━━━━━━━━━━━━

Индикатор: ⚪️ Готовится..."""
    
    keyboard = [[InlineKeyboardButton("⏳ Подождать...", callback_data=f"task_reaction_wait:16")]]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    state_key = f"{query.from_user.id}:16"
    state = ensure_task_state(state_key, 3, 16)
    state["start_time"] = asyncio.get_event_loop().time()
    state["ready"] = False
    
    await asyncio.sleep(2)
    if state_key in task_states:
        text = """☕️ Сделать эспрессо

Индикатор: 🟡 Почти готово..."""
        
        keyboard = [[InlineKeyboardButton("⏳ Ещё рано...", callback_data=f"task_reaction_wait:16")]]
        
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            pass
        
        await asyncio.sleep(2)
        if state_key in task_states:
            text = """☕️ Сделать эспрессо

Индикатор: 🟢 ГОТОВО! ✅

⚡ СЕЙЧАС!"""
            
            keyboard = [
                [InlineKeyboardButton("☕️ НАЖАТЬ!", callback_data=f"task_reaction_hit:16")],
                [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:16")]
            ]
            
            try:
                await query.edit_message_text(
                    text=text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                if state_key in task_states:
                    task_states[state_key]["ready"] = True
            except:
                pass

async def show_cocoa_task(query, context: ContextTypes.DEFAULT_TYPE):
    """Задание: Налить какао"""
    text = """🍫 Налить какао

Подставь стакан под кран и нажми в нужный момент!

━━━━━━━━━━━━━━━━

Стакан: Пусто..."""
    
    keyboard = [[InlineKeyboardButton("⏳ Подождать...", callback_data=f"task_reaction_wait:17")]]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    state_key = f"{query.from_user.id}:17"
    state = ensure_task_state(state_key, 3, 17)
    state["start_time"] = asyncio.get_event_loop().time()
    state["ready"] = False
    
    await asyncio.sleep(2)
    if state_key in task_states:
        text = """🍫 Налить какао

Стакан: Наполняется..."""
        
        keyboard = [[InlineKeyboardButton("⏳ Ещё рано...", callback_data=f"task_reaction_wait:17")]]
        
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            pass
        
        await asyncio.sleep(2)
        if state_key in task_states:
            text = """🍫 Налить какао

Стакан: Почти полный! ✅

⚡ СЕЙЧАС!"""
            
            keyboard = [
                [InlineKeyboardButton("🍫 НАЖАТЬ!", callback_data=f"task_reaction_hit:17")],
                [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:17")]
            ]
            
            try:
                await query.edit_message_text(
                    text=text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                if state_key in task_states:
                    task_states[state_key]["ready"] = True
            except:
                pass

async def show_waffle_task(query, context: ContextTypes.DEFAULT_TYPE):
    """Задание: Прогреть вафельный рожок"""
    text = """🧇 Прогреть вафельный рожок

Дождись золотистого цвета!

━━━━━━━━━━━━━━━━

Цвет: Светлый..."""
    
    keyboard = [[InlineKeyboardButton("⏳ Подождать...", callback_data=f"task_reaction_wait:18")]]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    state_key = f"{query.from_user.id}:18"
    state = ensure_task_state(state_key, 3, 18)
    state["start_time"] = asyncio.get_event_loop().time()
    state["ready"] = False
    
    await asyncio.sleep(2)
    if state_key in task_states:
        text = """🧇 Прогреть вафельный рожок

Цвет: Желтоватый..."""
        
        keyboard = [[InlineKeyboardButton("⏳ Ещё рано...", callback_data=f"task_reaction_wait:18")]]
        
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            pass
        
        await asyncio.sleep(2)
        if state_key in task_states:
            text = """🧇 Прогреть вафельный рожок

Цвет: Золотистый! ✅

⚡ СЕЙЧАС!"""
            
            keyboard = [
                [InlineKeyboardButton("🧇 НАЖАТЬ!", callback_data=f"task_reaction_hit:18")],
                [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:18")]
            ]
            
            try:
                await query.edit_message_text(
                    text=text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                if state_key in task_states:
                    task_states[state_key]["ready"] = True
            except:
                pass

async def show_milk_task(query, context: ContextTypes.DEFAULT_TYPE):
    """Задание: Взбить молоко"""
    text = """🥛 Взбить молоко

Нажми когда пенка готова!

━━━━━━━━━━━━━━━━

Пенка: Формируется..."""
    
    keyboard = [[InlineKeyboardButton("⏳ Подождать...", callback_data=f"task_reaction_wait:20")]]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    state_key = f"{query.from_user.id}:20"
    state = ensure_task_state(state_key, 3, 20)
    state["start_time"] = asyncio.get_event_loop().time()
    state["ready"] = False
    
    await asyncio.sleep(2)
    if state_key in task_states:
        text = """🥛 Взбить молоко

Пенка: Почти готова..."""
        
        keyboard = [[InlineKeyboardButton("⏳ Ещё рано...", callback_data=f"task_reaction_wait:20")]]
        
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            pass
        
        await asyncio.sleep(2)
        if state_key in task_states:
            text = """🥛 Взбить молоко

Пенка: Готова! ✅

⚡ СЕЙЧАС!"""
            
            keyboard = [
                [InlineKeyboardButton("🥛 НАЖАТЬ!", callback_data=f"task_reaction_hit:20")],
                [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:20")]
            ]
            
            try:
                await query.edit_message_text(
                    text=text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                if state_key in task_states:
                    task_states[state_key]["ready"] = True
            except:
                pass

async def show_garland_task(query, context: ContextTypes.DEFAULT_TYPE):
    """Задание: Проверить гирлянду"""
    text = """💡 Проверить гирлянду

Гирлянда мигает разными цветами. Нажми когда загорится красный!

━━━━━━━━━━━━━━━━

Цвет: Синий..."""
    
    keyboard = [[InlineKeyboardButton("⏳ Подождать...", callback_data=f"task_reaction_wait:23")]]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    state_key = f"{query.from_user.id}:23"
    state = ensure_task_state(state_key, 4, 23)
    state["start_time"] = asyncio.get_event_loop().time()
    state["ready"] = False
    
    await asyncio.sleep(2)
    if state_key in task_states:
        text = """💡 Проверить гирлянду

Цвет: Зеленый..."""
        
        keyboard = [[InlineKeyboardButton("⏳ Ещё рано...", callback_data=f"task_reaction_wait:23")]]
        
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            pass
        
        await asyncio.sleep(2)
        if state_key in task_states:
            text = """💡 Проверить гирлянду

Цвет: 🔴 КРАСНЫЙ! ✅

⚡ СЕЙЧАС!"""
            
            keyboard = [
                [InlineKeyboardButton("💡 НАЖАТЬ!", callback_data=f"task_reaction_hit:23")],
                [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:23")]
            ]
            
            try:
                await query.edit_message_text(
                    text=text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                if state_key in task_states:
                    task_states[state_key]["ready"] = True
            except:
                pass

async def show_snowball_task(query, context: ContextTypes.DEFAULT_TYPE):
    """Задание: Проверить снежный шар"""
    text = """❄️ Проверить снежный шар

Встряхни снежный шар и нажми когда красиво кружится!

━━━━━━━━━━━━━━━━

Снежинки: Оседают..."""
    
    keyboard = [[InlineKeyboardButton("⏳ Подождать...", callback_data=f"task_reaction_wait:27")]]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    state_key = f"{query.from_user.id}:27"
    state = ensure_task_state(state_key, 4, 27)
    state["start_time"] = asyncio.get_event_loop().time()
    state["ready"] = False
    
    await asyncio.sleep(2)
    if state_key in task_states:
        text = """❄️ Проверить снежный шар

Снежинки: Кружатся..."""
        
        keyboard = [[InlineKeyboardButton("⏳ Ещё рано...", callback_data=f"task_reaction_wait:27")]]
        
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            pass
        
        await asyncio.sleep(2)
        if state_key in task_states:
            text = """❄️ Проверить снежный шар

Снежинки: Красиво кружатся! ✨

⚡ СЕЙЧАС!"""
            
            keyboard = [
                [InlineKeyboardButton("❄️ НАЖАТЬ!", callback_data=f"task_reaction_hit:27")],
                [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:27")]
            ]
            
            try:
                await query.edit_message_text(
                    text=text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                if state_key in task_states:
                    task_states[state_key]["ready"] = True
            except:
                pass

async def show_scale_task(query, context: ContextTypes.DEFAULT_TYPE):
    """Задание: Отмерить 500г"""
    text = """⚖️ Отмерить 500г

Нужно отмерить ровно 500 грамм пряников!

━━━━━━━━━━━━━━━━

Вес: 200г..."""
    
    keyboard = [[InlineKeyboardButton("⏳ Подождать...", callback_data=f"task_reaction_wait:30")]]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    state_key = f"{query.from_user.id}:30"
    state = ensure_task_state(state_key, 5, 30)
    state["start_time"] = asyncio.get_event_loop().time()
    state["ready"] = False
    
    await asyncio.sleep(1.5)
    if state_key in task_states:
        text = """⚖️ Отмерить 500г

Вес: 350г..."""
        
        keyboard = [[InlineKeyboardButton("⏳ Ещё рано...", callback_data=f"task_reaction_wait:30")]]
        
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            pass
        
        await asyncio.sleep(1.5)
        if state_key in task_states:
            text = """⚖️ Отмерить 500г

Вес: 500г! ✅

⚡ СЕЙЧАС!"""
            
            keyboard = [
                [InlineKeyboardButton("⚖️ НАЖАТЬ!", callback_data=f"task_reaction_hit:30")],
                [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:30")]
            ]
            
            try:
                await query.edit_message_text(
                    text=text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                if state_key in task_states:
                    task_states[state_key]["ready"] = True
            except:
                pass

async def show_oven_task(query, context: ContextTypes.DEFAULT_TYPE):
    """Задание: Достать из духовки"""
    text = """🔥 Достать из духовки

Пряники пекутся. Нажми когда подрумянятся!

━━━━━━━━━━━━━━━━

Цвет: Светлый..."""
    
    keyboard = [[InlineKeyboardButton("⏳ Подождать...", callback_data=f"task_reaction_wait:33")]]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    state_key = f"{query.from_user.id}:33"
    state = ensure_task_state(state_key, 5, 33)
    state["start_time"] = asyncio.get_event_loop().time()
    state["ready"] = False
    
    await asyncio.sleep(2)
    if state_key in task_states:
        text = """🔥 Достать из духовки

Цвет: Золотистый..."""
        
        keyboard = [[InlineKeyboardButton("⏳ Ещё рано...", callback_data=f"task_reaction_wait:33")]]
        
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            pass
        
        await asyncio.sleep(2)
        if state_key in task_states:
            text = """🔥 Достать из духовки

Цвет: Подрумянились! ✅

⚡ СЕЙЧАС!"""
            
            keyboard = [
                [InlineKeyboardButton("🔥 НАЖАТЬ!", callback_data=f"task_reaction_hit:33")],
                [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:33")]
            ]
            
            try:
                await query.edit_message_text(
                    text=text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                if state_key in task_states:
                    task_states[state_key]["ready"] = True
            except:
                pass

async def show_boiling_task(query, context: ContextTypes.DEFAULT_TYPE):
    """Задание: Дождаться кипения"""
    text = """💨 Дождаться кипения

Самовар нагревается. Нажми когда пойдет пар!

━━━━━━━━━━━━━━━━

Пар: Нет..."""
    
    keyboard = [[InlineKeyboardButton("⏳ Подождать...", callback_data=f"task_reaction_wait:40")]]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    state_key = f"{query.from_user.id}:40"
    state = ensure_task_state(state_key, 6, 40)
    state["start_time"] = asyncio.get_event_loop().time()
    state["ready"] = False
    
    await asyncio.sleep(2)
    if state_key in task_states:
        text = """💨 Дождаться кипения

Пар: Появляется..."""
        
        keyboard = [[InlineKeyboardButton("⏳ Ещё рано...", callback_data=f"task_reaction_wait:40")]]
        
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            pass
        
        await asyncio.sleep(2)
        if state_key in task_states:
            text = """💨 Дождаться кипения

Пар: Идет! 💨

⚡ СЕЙЧАС!"""
            
            keyboard = [
                [InlineKeyboardButton("💨 НАЖАТЬ!", callback_data=f"task_reaction_hit:40")],
                [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:40")]
            ]
            
            try:
                await query.edit_message_text(
                    text=text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                if state_key in task_states:
                    task_states[state_key]["ready"] = True
            except:
                pass

async def show_brew_task(query, context: ContextTypes.DEFAULT_TYPE):
    """Задание: Проверить заварку"""
    text = """⏱ Проверить заварку

Чай заваривается. Нажми через 3 минуты!

━━━━━━━━━━━━━━━━

Время: 1 минута..."""
    
    keyboard = [[InlineKeyboardButton("⏳ Подождать...", callback_data=f"task_reaction_wait:43")]]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    state_key = f"{query.from_user.id}:43"
    state = ensure_task_state(state_key, 6, 43)
    state["start_time"] = asyncio.get_event_loop().time()
    state["ready"] = False
    
    await asyncio.sleep(2)
    if state_key in task_states:
        text = """⏱ Проверить заварку

Время: 2 минуты..."""
        
        keyboard = [[InlineKeyboardButton("⏳ Ещё рано...", callback_data=f"task_reaction_wait:43")]]
        
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            pass
        
        await asyncio.sleep(2)
        if state_key in task_states:
            text = """⏱ Проверить заварку

Время: 3 минуты! ✅

⚡ СЕЙЧАС!"""
            
            keyboard = [
                [InlineKeyboardButton("⏱ НАЖАТЬ!", callback_data=f"task_reaction_hit:43")],
                [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:43")]
            ]
            
            try:
                await query.edit_message_text(
                    text=text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                if state_key in task_states:
                    task_states[state_key]["ready"] = True
            except:
                pass

async def show_fabric_task(query, context: ContextTypes.DEFAULT_TYPE):
    """Задание: Проверить ткань"""
    text = """🖐 Проверить ткань

Клиент хочет потрогать ткань. Нажми когда ткань будет готова!

━━━━━━━━━━━━━━━━

Ткань: Проверяется..."""
    
    keyboard = [[InlineKeyboardButton("⏳ Подождать...", callback_data=f"task_reaction_wait:10")]]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    state_key = f"{query.from_user.id}:10"
    state = ensure_task_state(state_key, 2, 10)
    state["start_time"] = asyncio.get_event_loop().time()
    state["ready"] = False
    
    await asyncio.sleep(2)
    if state_key in task_states:
        text = """🖐 Проверить ткань

Ткань: Мягкая/Теплая/Приятная ✅

⚡ СЕЙЧАС!"""
        
        keyboard = [
            [InlineKeyboardButton("✅ НАЖАТЬ!", callback_data=f"task_reaction_hit:10")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:10")]
        ]
        
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            task_states[state_key]["ready"] = True
        except:
            pass

async def show_pack_bag_task(query, context: ContextTypes.DEFAULT_TYPE):
    """Задание: Упаковать в пакет"""
    text = """🛍 Упаковать в пакет

Упакуй покупку в пакет!

━━━━━━━━━━━━━━━━

Пакет: Готов..."""
    
    keyboard = [[InlineKeyboardButton("⏳ Подождать...", callback_data=f"task_reaction_wait:12")]]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    state_key = f"{query.from_user.id}:12"
    state = ensure_task_state(state_key, 2, 12)
    state["start_time"] = asyncio.get_event_loop().time()
    state["ready"] = False
    
    await asyncio.sleep(2)
    if state_key in task_states:
        text = """🛍 Упаковать в пакет

Пакет: Готов! ✅

⚡ СЕЙЧАС!"""
        
        keyboard = [
            [InlineKeyboardButton("✅ НАЖАТЬ!", callback_data=f"task_reaction_hit:12")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:12")]
        ]
        
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            task_states[state_key]["ready"] = True
        except:
            pass

async def show_straw_task(query, context: ContextTypes.DEFAULT_TYPE):
    """Задание: Вставить трубочку"""
    state_key = f"{query.from_user.id}:21"
    state = ensure_task_state(state_key, 3, 21)
    
    text = """🥤 Вставить трубочку

Добавь трубочку в напиток!

━━━━━━━━━━━━━━━━

Трубочка: Готова..."""
    
    keyboard = [
        [InlineKeyboardButton("🥤 Добавить", callback_data=f"task_reaction_hit:21")],
        [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:21")]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    # Устанавливаем ready сразу, так как это простое задание без таймера
    state["ready"] = True

async def show_tie_ribbon_task(query, context: ContextTypes.DEFAULT_TYPE):
    """Задание: Завязать ленту"""
    text = """🎀 Завязать ленту

Завяжи ленту на коробке!

━━━━━━━━━━━━━━━━

Лента: Готова..."""
    
    keyboard = [[InlineKeyboardButton("⏳ Подождать...", callback_data=f"task_reaction_wait:35")]]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    state_key = f"{query.from_user.id}:35"
    state = ensure_task_state(state_key, 5, 35)
    state["start_time"] = asyncio.get_event_loop().time()
    state["ready"] = False
    
    await asyncio.sleep(2)
    if state_key in task_states:
        text = """🎀 Завязать ленту

Лента: Завязана! ✅

⚡ СЕЙЧАС!"""
        
        keyboard = [
            [InlineKeyboardButton("✅ НАЖАТЬ!", callback_data=f"task_reaction_hit:35")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:35")]
        ]
        
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            task_states[state_key]["ready"] = True
        except:
            pass

async def show_close_box_task(query, context: ContextTypes.DEFAULT_TYPE):
    """Задание: Закрыть коробку"""
    text = """📦 Закрыть коробку

Закрой коробку когда всё внутри!

━━━━━━━━━━━━━━━━

Коробка: Готова..."""
    
    keyboard = [[InlineKeyboardButton("⏳ Подождать...", callback_data=f"task_reaction_wait:37")]]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    state_key = f"{query.from_user.id}:37"
    state = ensure_task_state(state_key, 5, 37)
    state["start_time"] = asyncio.get_event_loop().time()
    state["ready"] = False
    
    await asyncio.sleep(2)
    if state_key in task_states:
        text = """📦 Закрыть коробку

Коробка: Всё внутри! ✅

⚡ СЕЙЧАС!"""
        
        keyboard = [
            [InlineKeyboardButton("✅ НАЖАТЬ!", callback_data=f"task_reaction_hit:37")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:37")]
        ]
        
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            task_states[state_key]["ready"] = True
        except:
            pass

async def show_add_branch_task(query, context: ContextTypes.DEFAULT_TYPE):
    """Задание: Добавить веточку"""
    state_key = f"{query.from_user.id}:51"
    state = ensure_task_state(state_key, 7, 51)
    
    text = """🌲 Добавить веточку

Добавь еловую веточку к подарку!

━━━━━━━━━━━━━━━━

Веточка: Готова..."""
    
    keyboard = [
        [InlineKeyboardButton("🌲 Добавить", callback_data=f"task_reaction_hit:51")],
        [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:51")]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    # Устанавливаем ready сразу, так как это простое задание без таймера
    state["ready"] = True

async def show_cut_ribbon_task(query, context: ContextTypes.DEFAULT_TYPE):
    """Задание: Отрезать ленту"""
    text = """✂️ Отрезать ленту

Отрежь ленту в нужный момент!

━━━━━━━━━━━━━━━━

Лента: Натягивается..."""
    
    keyboard = [[InlineKeyboardButton("⏳ Подождать...", callback_data=f"task_reaction_wait:52")]]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    state_key = f"{query.from_user.id}:52"
    state = ensure_task_state(state_key, 7, 52)
    state["start_time"] = asyncio.get_event_loop().time()
    state["ready"] = False
    
    await asyncio.sleep(2)
    if state_key in task_states:
        text = """✂️ Отрезать ленту

Лента: Натянута! ✅

⚡ СЕЙЧАС!"""
        
        keyboard = [
            [InlineKeyboardButton("✂️ НАЖАТЬ!", callback_data=f"task_reaction_hit:52")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:52")]
        ]
        
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            task_states[state_key]["ready"] = True
        except:
            pass

async def show_stop_conveyor_task(query, context: ContextTypes.DEFAULT_TYPE):
    """Задание: Остановить конвейер"""
    text = """⏸ Остановить конвейер

Останови конвейер когда подарок на месте!

━━━━━━━━━━━━━━━━

Конвейер: Движется..."""
    
    keyboard = [[InlineKeyboardButton("⏳ Подождать...", callback_data=f"task_reaction_wait:55")]]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    state_key = f"{query.from_user.id}:55"
    state = ensure_task_state(state_key, 7, 55)
    state["start_time"] = asyncio.get_event_loop().time()
    state["ready"] = False
    
    await asyncio.sleep(2)
    if state_key in task_states:
        text = """⏸ Остановить конвейер

Подарок: На месте! ✅

⚡ СЕЙЧАС!"""
        
        keyboard = [
            [InlineKeyboardButton("⏸ НАЖАТЬ!", callback_data=f"task_reaction_hit:55")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:55")]
        ]
        
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            task_states[state_key]["ready"] = True
        except:
            pass

async def show_sprinkle_snow_task(query, context: ContextTypes.DEFAULT_TYPE):
    """Задание: Посыпать снегом"""
    state_key = f"{query.from_user.id}:56"
    state = ensure_task_state(state_key, 7, 56)
    
    text = """❄️ Посыпать снегом

Посыпь подарок искусственным снегом!

━━━━━━━━━━━━━━━━

Снег: Готов..."""
    
    keyboard = [
        [InlineKeyboardButton("❄️ Посыпать", callback_data=f"task_reaction_hit:56")],
        [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:56")]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    # Устанавливаем ready сразу, так как это простое задание без таймера
    state["ready"] = True

async def show_measure_ribbon_task(query, context: ContextTypes.DEFAULT_TYPE):
    """Задание: Отмерить ленту"""
    text = """📏 Отмерить ленту

Отмерь 50 см ленты!

━━━━━━━━━━━━━━━━

Длина: 20см..."""
    
    keyboard = [[InlineKeyboardButton("⏳ Подождать...", callback_data=f"task_reaction_wait:58")]]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    state_key = f"{query.from_user.id}:58"
    state = ensure_task_state(state_key, 7, 58)
    state["start_time"] = asyncio.get_event_loop().time()
    state["ready"] = False
    
    await asyncio.sleep(1.5)
    if state_key in task_states:
        text = """📏 Отмерить ленту

Длина: 35см..."""
        
        keyboard = [[InlineKeyboardButton("⏳ Ещё рано...", callback_data=f"task_reaction_wait:58")]]
        
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            pass
        
        await asyncio.sleep(1.5)
        if state_key in task_states:
            text = """📏 Отмерить ленту

Длина: 50см! ✅

⚡ СЕЙЧАС!"""
            
            keyboard = [
                [InlineKeyboardButton("📏 НАЖАТЬ!", callback_data=f"task_reaction_hit:58")],
                [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:58")]
            ]
            
            try:
                await query.edit_message_text(
                    text=text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                if state_key in task_states:
                    task_states[state_key]["ready"] = True
            except:
                pass

async def show_generic_reaction_task(query, task, context: ContextTypes.DEFAULT_TYPE):
    """Универсальный обработчик реакций"""
    text = f"""{task['emoji']} *{task['name']}*

⏳ Следи за процессом...

🎯 *Нажми в нужный момент*"""
    
    keyboard = [
        [InlineKeyboardButton("✅ НАЖАТЬ!", callback_data=f"task_reaction_hit:{task['id']}")],
        [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:{task['id']}")]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def start_choice_task(query, pavilion_id: int, task_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Запуск задания типа 'choice' (выбор из вариантов)"""
    task = await database.get_task(task_id)
    
    state_key = f"{query.from_user.id}:{task_id}"
    task_states[state_key] = {
        "step": 1,
        "pavilion_id": pavilion_id,
        "task_id": task_id,
        "choices": []
    }
    
    # Специфичные задания
    if task_id == 1:  # Подобрать варежки
        await show_gloves_choice(query)
    elif task_id == 4:  # Найти нужный размер
        await show_size_choice(query)
    elif task_id == 7:  # Листать свитера
        await show_sweaters_choice(query)
    elif task_id == 8:  # Выбрать размер
        await show_clothing_size_choice(query)
    elif task_id == 9:  # Примерить шапку
        await show_hat_choice(query)
    elif task_id == 14:  # Выбрать цветовую гамму
        await show_color_scheme_choice(query)
    elif task_id == 15:  # Собрать порцию мороженого (начинается с choice, переходит в sequence)
        await show_icecream_choice(query)
    elif task_id == 19:  # Добавить топпинг
        await show_topping_choice(query)
    elif task_id == 22:  # Повесить шары
        await show_balls_choice(query)
    elif task_id == 24:  # Упаковать свечи
        await show_candles_choice(query)
    elif task_id == 29:  # Сложить пряники
        await show_cookies_choice(query)
    elif task_id == 31:  # Добавить варенье
        await show_jam_choice(query)
    elif task_id == 32:  # Украсить пряник
        await show_cookie_decor_choice(query)
    elif task_id == 36:  # Заварить чай
        await show_tea_type_choice(query)
    elif task_id == 44:  # Собрать чайную пару
        await show_tea_set_choice(query)
    elif task_id == 45:  # Выбрать варенье
        await show_tea_jam_choice(query)
    elif task_id == 46:  # Найти редкий сорт
        await show_rare_tea_choice(query)
    elif task_id == 48:  # Завернуть бумагу
        await show_wrap_paper_choice(query)
    elif task_id == 50:  # Написать пожелание
        await show_wish_choice(query)
    elif task_id == 54:  # Украсить декором
        await show_decor_choice(query)
    elif task_id == 57:  # Выбрать открытку
        await show_card_choice(query)
    elif task_id == 59:  # Финальный штрих
        await show_final_touch_choice(query)
    else:
        await show_generic_choice_task(query, task)

async def show_gloves_choice(query):
    """Подобрать варежки"""
    text = """🧤 *Подобрать варежки*

❄️ Снег падает за окном павильона...
🕯️ Теплый свет ламп освещает полки с варежками

На полке разложены варежки разных цветов.
Клиент указывает на красные — нужно найти подходящие.

🎯 *Выбери цвет:*"""
    
    keyboard = [
        [
            InlineKeyboardButton("🤍 Белые", callback_data=f"task_choice:1:white"),
            InlineKeyboardButton("🔴 Красные", callback_data=f"task_choice:1:red")
        ],
        [
            InlineKeyboardButton("🔵 Синие", callback_data=f"task_choice:1:blue"),
            InlineKeyboardButton("⚫️ Черные", callback_data=f"task_choice:1:black")
        ],
        [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:1")]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_size_choice(query):
    """Найти нужный размер"""
    text = """🧣 *Найти нужный размер*

🌨️ За окном метель, в павильоне тепло и уютно
📦 На полке аккуратно разложены шарфы с бирками

Нужен размер M — средний, самый популярный.

🎯 *Выбери размер:*"""
    
    keyboard = [
        [
            InlineKeyboardButton("S", callback_data=f"task_choice:4:S"),
            InlineKeyboardButton("M", callback_data=f"task_choice:4:M")
        ],
        [
            InlineKeyboardButton("L", callback_data=f"task_choice:4:L"),
            InlineKeyboardButton("XL", callback_data=f"task_choice:4:XL")
        ],
        [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:4")]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_icecream_choice(query):
    """Собрать порцию мороженого - шаг 1"""
    text = """🍦 *Собрать порцию мороженого*

🧊 Холодный воздух из витрины с мороженым
🍦 Вафельные рожки лежат стопкой
✨ Блестит мороженое в металлических контейнерах

Выбери сорт для порции в рожке.

🎯 *Сорт:*"""
    
    keyboard = [
        [
            InlineKeyboardButton("🤍 Пломбир", callback_data=f"task_choice:15:vanilla"),
            InlineKeyboardButton("🍫 Шоколадное", callback_data=f"task_choice:15:chocolate")
        ],
        [
            InlineKeyboardButton("🌰 Фисташковое", callback_data=f"task_choice:15:pistachio"),
            InlineKeyboardButton("🍓 Клубничное", callback_data=f"task_choice:15:strawberry")
        ],
        [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:15")]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_topping_choice(query):
    """Добавить топпинг"""
    text = """🍨 Добавить топпинг

Выбери топпинг для мороженого!"""
    
    keyboard = [
        [
            InlineKeyboardButton("🍫 Шоколадная крошка", callback_data=f"task_choice:19:chocolate"),
            InlineKeyboardButton("🍮 Карамель", callback_data=f"task_choice:19:caramel")
        ],
        [
            InlineKeyboardButton("🫐 Свежие ягоды", callback_data=f"task_choice:19:berries"),
            InlineKeyboardButton("🥜 Орешки", callback_data=f"task_choice:19:nuts")
        ],
        [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:19")]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_balls_choice(query):
    """Повесить шары"""
    text = """🎄 Повесить шары

Выбери цвет елочного шара!"""
    
    keyboard = [
        [
            InlineKeyboardButton("🔴 Красный", callback_data=f"task_choice:22:red"),
            InlineKeyboardButton("🟡 Золотой", callback_data=f"task_choice:22:gold")
        ],
        [
            InlineKeyboardButton("⚪️ Серебряный", callback_data=f"task_choice:22:silver"),
            InlineKeyboardButton("🔵 Синий", callback_data=f"task_choice:22:blue")
        ],
        [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:22")]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_candles_choice(query):
    """Упаковать свечи"""
    text = """🕯 Упаковать свечи

Выбери набор свечей!"""
    
    keyboard = [
        [
            InlineKeyboardButton("3 свечи", callback_data=f"task_choice:24:3"),
            InlineKeyboardButton("5 свечей", callback_data=f"task_choice:24:5")
        ],
        [
            InlineKeyboardButton("7 свечей", callback_data=f"task_choice:24:7"),
            InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:24")
        ]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_cookies_choice(query):
    """Сложить пряники"""
    text = """🍪 Сложить пряники

Выбери форму пряников!"""
    
    keyboard = [
        [
            InlineKeyboardButton("⭐ Звездочки", callback_data=f"task_choice:29:star"),
            InlineKeyboardButton("🎄 Елочки", callback_data=f"task_choice:29:tree")
        ],
        [
            InlineKeyboardButton("❄️ Снежинки", callback_data=f"task_choice:29:snowflake"),
            InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:29")
        ]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_jam_choice(query):
    """Добавить варенье"""
    text = """🫙 Добавить варенье

Выбери варенье!"""
    
    keyboard = [
        [
            InlineKeyboardButton("🫐 Малина", callback_data=f"task_choice:31:raspberry"),
            InlineKeyboardButton("🟠 Облепиха", callback_data=f"task_choice:31:sea_buckthorn")
        ],
        [
            InlineKeyboardButton("🔴 Брусника", callback_data=f"task_choice:31:cranberry"),
            InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:31")
        ]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_cookie_decor_choice(query):
    """Украсить пряник"""
    text = """🎨 Украсить пряник

Выбери узор!"""
    
    keyboard = [
        [
            InlineKeyboardButton("❄️ Снежинка", callback_data=f"task_choice:32:snowflake"),
            InlineKeyboardButton("🎄 Елочка", callback_data=f"task_choice:32:tree")
        ],
        [
            InlineKeyboardButton("⭐ Звезда", callback_data=f"task_choice:32:star"),
            InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:32")
        ]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_tea_type_choice(query):
    """Заварить чай"""
    text = """☕️ Заварить чай

Выбери сорт чая!"""
    
    keyboard = [
        [
            InlineKeyboardButton("⚫️ Черный", callback_data=f"task_choice:36:black"),
            InlineKeyboardButton("🟢 Зеленый", callback_data=f"task_choice:36:green")
        ],
        [
            InlineKeyboardButton("🌿 Травяной", callback_data=f"task_choice:36:herbal"),
            InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:36")
        ]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_tea_set_choice(query):
    """Собрать чайную пару"""
    text = """🍵 Собрать чайную пару

Выбери чайную пару!"""
    
    keyboard = [
        [
            InlineKeyboardButton("🔵 Гжель", callback_data=f"task_choice:44:gzel"),
            InlineKeyboardButton("🔴 Красная", callback_data=f"task_choice:44:red")
        ],
        [
            InlineKeyboardButton("⚪️ Белая", callback_data=f"task_choice:44:white"),
            InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:44")
        ]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_tea_jam_choice(query):
    """Выбрать варенье для чая"""
    text = """🫙 Выбрать варенье

Выбери варенье!"""
    
    keyboard = [
        [
            InlineKeyboardButton("🫐 Малина", callback_data=f"task_choice:45:raspberry"),
            InlineKeyboardButton("🟠 Облепиха", callback_data=f"task_choice:45:sea_buckthorn")
        ],
        [
            InlineKeyboardButton("🔴 Брусника", callback_data=f"task_choice:45:cranberry"),
            InlineKeyboardButton("🍒 Вишня", callback_data=f"task_choice:45:cherry")
        ],
        [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:45")]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_rare_tea_choice(query):
    """Найти редкий сорт"""
    text = """🔍 *Найти редкий сорт*

🫖 Полки уставлены банками с чаем
📜 Этикетки с названиями: "Классический", "Иван-чай", "Смородиновый"...
🔎 Нужно найти "Московский вечер" — редкий сорт

Листай полку и ищи нужную банку.

🎯 *Поиск:*"""
    
    keyboard = [
        [
            InlineKeyboardButton("⬅️ Назад", callback_data=f"task_choice:46:prev"),
            InlineKeyboardButton("➡️ Вперед", callback_data=f"task_choice:46:next")
        ],
        [
            InlineKeyboardButton("✅ Это он!", callback_data=f"task_choice:46:found"),
            InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:46")
        ]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_wrap_paper_choice(query):
    """Завернуть бумагу"""
    text = """🎀 Завернуть бумагу

Выбери упаковочную бумагу!"""
    
    keyboard = [
        [
            InlineKeyboardButton("🟡 Золотая", callback_data=f"task_choice:48:gold"),
            InlineKeyboardButton("🎄 Скандинавская", callback_data=f"task_choice:48:scandinavian")
        ],
        [
            InlineKeyboardButton("🔴 Красная", callback_data=f"task_choice:48:red"),
            InlineKeyboardButton("⚪️ Белая", callback_data=f"task_choice:48:white")
        ],
        [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:48")]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_wish_choice(query):
    """Написать пожелание"""
    text = """🏷 Написать пожелание

Выбери пожелание для открытки!"""
    
    keyboard = [
        [
            InlineKeyboardButton("🎄 С Новым Годом", callback_data=f"task_choice:50:newyear"),
            InlineKeyboardButton("❤️ С любовью", callback_data=f"task_choice:50:love")
        ],
        [
            InlineKeyboardButton("🎉 Поздравляю", callback_data=f"task_choice:50:congrats"),
            InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:50")
        ]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_decor_choice(query):
    """Украсить декором"""
    text = """🎨 *Украсить декором*

🎁 Подарок лежит на столе
✨ Коробка с декоративными элементами: шишки, бусины, колокольчики, звезды
🌟 Нужно выбрать 2 элемента для финального штриха

Выбери 2 декоративных элемента.

🎯 *Декор (2 элемента):*"""
    
    state_key = f"{query.from_user.id}:54"
    if state_key not in task_states:
        task_states[state_key] = {"choices": []}
    
    selected = task_states[state_key].get("choices", [])
    
    if len(selected) < 2:
        text += f"\n\nВыбрано: {len(selected)}/2"
        keyboard = [
            [
                InlineKeyboardButton("🌲 Шишка", callback_data=f"task_choice:54:cone"),
                InlineKeyboardButton("🔵 Бусина", callback_data=f"task_choice:54:bead")
            ],
            [
                InlineKeyboardButton("🔔 Колокольчик", callback_data=f"task_choice:54:bell"),
                InlineKeyboardButton("⭐ Звезда", callback_data=f"task_choice:54:star")
            ],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:54")]
        ]
    else:
        text += "\n\n✅ Выбрано 2 элемента!"
        keyboard = [
            [InlineKeyboardButton("✅ Готово", callback_data=f"task_choice:54:done")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:54")]
        ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_card_choice(query):
    """Выбрать открытку"""
    text = """💌 Выбрать открытку

Выбери дизайн открытки!"""
    
    keyboard = [
        [
            InlineKeyboardButton("🎄 Новогодняя", callback_data=f"task_choice:57:newyear"),
            InlineKeyboardButton("❄️ Зимняя", callback_data=f"task_choice:57:winter")
        ],
        [
            InlineKeyboardButton("🎁 Подарочная", callback_data=f"task_choice:57:gift"),
            InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:57")
        ]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_final_touch_choice(query):
    """Финальный штрих"""
    text = """🎁 Финальный штрих

Добавь последний штрих к подарку!"""
    
    keyboard = [
        [
            InlineKeyboardButton("🌸 Цветок", callback_data=f"task_choice:59:flower"),
            InlineKeyboardButton("🔔 Бубенчик", callback_data=f"task_choice:59:bell")
        ],
        [
            InlineKeyboardButton("✨ Без декора", callback_data=f"task_choice:59:none"),
            InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:59")
        ]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_sweaters_choice(query):
    """Листать свитера"""
    text = """🧥 *Листать свитера*

🎨 На вешалке висят свитера разных цветов и узоров
🦌 Нужен синий с оленями — классический зимний узор
👀 Листай вешалку и ищи нужный

🎯 *Поиск:*"""
    
    keyboard = [
        [
            InlineKeyboardButton("⬅️ Назад", callback_data=f"task_choice:7:prev"),
            InlineKeyboardButton("➡️ Вперед", callback_data=f"task_choice:7:next")
        ],
        [
            InlineKeyboardButton("✅ Это он!", callback_data=f"task_choice:7:found"),
            InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:7")
        ]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_clothing_size_choice(query):
    """Выбрать размер одежды"""
    text = """👕 Выбрать размер

Клиент говорит: рост 175см

Выбери размер!"""
    
    keyboard = [
        [
            InlineKeyboardButton("S (160-165)", callback_data=f"task_choice:8:S"),
            InlineKeyboardButton("M (170-175)", callback_data=f"task_choice:8:M")
        ],
        [
            InlineKeyboardButton("L (180-185)", callback_data=f"task_choice:8:L"),
            InlineKeyboardButton("XL (190+)", callback_data=f"task_choice:8:XL")
        ],
        [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:8")]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_hat_choice(query):
    """Примерить шапку"""
    text = """🧢 Примерить шапку

Выбери модель шапки!"""
    
    keyboard = [
        [
            InlineKeyboardButton("🧢 С помпоном", callback_data=f"task_choice:9:pompon"),
            InlineKeyboardButton("🎩 Классическая", callback_data=f"task_choice:9:classic")
        ],
        [
            InlineKeyboardButton("🎨 Дизайнерская", callback_data=f"task_choice:9:designer"),
            InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:9")
        ]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_color_scheme_choice(query):
    """Выбрать цветовую гамму"""
    text = """🎨 *Выбрать цветовую гамму*

🎭 Зеркала отражают мягкий свет
🧵 На манекенах — серые тона, от светлого до угольного
✨ Нужно собрать комплект: 3 вещи в серой гамме

Выбери 3 предмета, которые сочетаются.

🎯 *Выбери 3 вещи:*"""
    
    state_key = f"{query.from_user.id}:14"
    if state_key not in task_states:
        task_states[state_key] = {"choices": []}
    
    selected = task_states[state_key].get("choices", [])
    
    if len(selected) < 3:
        text += f"\n\nВыбрано: {len(selected)}/3"
        keyboard = [
            [
                InlineKeyboardButton("⚪️ Серый свитер", callback_data=f"task_choice:14:gray_sweater"),
                InlineKeyboardButton("⚫️ Темно-серый шарф", callback_data=f"task_choice:14:gray_scarf")
            ],
            [
                InlineKeyboardButton("🔘 Серые перчатки", callback_data=f"task_choice:14:gray_gloves"),
                InlineKeyboardButton("⚪️ Светло-серый", callback_data=f"task_choice:14:light_gray")
            ],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:14")]
        ]
    else:
        text += "\n\n✅ Выбрано 3 вещи!"
        keyboard = [
            [InlineKeyboardButton("✅ Готово", callback_data=f"task_choice:14:done")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:14")]
        ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_generic_choice_task(query, task):
    """Универсальный обработчик выбора"""
    text = f"""{task['emoji']} *{task['name']}*

🎯 *Выбери вариант:*"""
    
    keyboard = [
        [
            InlineKeyboardButton("Вариант 1", callback_data=f"task_choice:{task['id']}:1"),
            InlineKeyboardButton("Вариант 2", callback_data=f"task_choice:{task['id']}:2")
        ],
        [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:{task['id']}")]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def start_sequence_task(query, pavilion_id: int, task_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Запуск задания типа 'sequence' (многошаговый процесс)"""
    task = await database.get_task(task_id)
    
    state_key = f"{query.from_user.id}:{task_id}"
    task_states[state_key] = {
        "step": 1,
        "pavilion_id": pavilion_id,
        "task_id": task_id,
        "choices": []
    }
    
    # Специфичные задания
    if task_id == 2:  # Собрать набор для катания
        await show_skating_set_sequence(query, 1)
    elif task_id == 5:  # Добавить грелки
        await show_handwarmers_sequence(query, 1)
    elif task_id == 11:  # Собрать образ
        await show_outfit_sequence(query, 1)
    elif task_id == 13:  # Подобрать аксессуары
        await show_accessories_sequence(query, 1)
    elif task_id == 15:  # Собрать порцию мороженого (продолжение)
        await show_icecream_sequence_continue(query, 1)
    elif task_id == 25:  # Размотать гирлянду
        await show_garland_unwind_sequence(query, 1)
    elif task_id == 26:  # Наполнить вазу
        await show_mandarin_vase_sequence(query, 1)
    elif task_id == 28:  # Зажечь свечи
        await show_candles_light_sequence(query, 1)
    elif task_id == 34:  # Собрать микс конфет
        await show_candy_mix_sequence(query, 1)
    elif task_id == 39:  # Собрать набор "Москва"
        await show_moscow_set_sequence(query, 1)
    elif task_id == 41:  # Разлить по чашкам
        await show_tea_pour_sequence(query, 1)
    elif task_id == 42:  # Помешать сахар
        await show_sugar_stir_sequence(query, 1)
    elif task_id == 47:  # Упаковать подарок
        await show_gift_wrap_sequence(query, 1)
    elif task_id == 53:  # Разгладить складки
        await show_smooth_folds_sequence(query, 1)
    else:
        await show_generic_sequence_task(query, task, 1)

async def show_skating_set_sequence(query, step: int):
    """Собрать набор для катания"""
    if step == 1:
        text = """🎒 Собрать набор для катания

Выбери шапку!"""
        
        keyboard = [
            [
                InlineKeyboardButton("🧢 Шапка-ушанка", callback_data=f"task_sequence:2:1:hat"),
                InlineKeyboardButton("🎩 Шерстяная", callback_data=f"task_sequence:2:1:wool_hat")
            ],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:2")]
        ]
    elif step == 2:
        text = """✅ Шапка выбрана

*Шаг 2/3:* Выбери шарф

🎯 *Шарф:*"""
        
        keyboard = [
            [
                InlineKeyboardButton("🧣 Шерстяной", callback_data=f"task_sequence:2:2:scarf"),
                InlineKeyboardButton("🧣 Теплый", callback_data=f"task_sequence:2:2:warm_scarf")
            ],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:2")]
        ]
    elif step == 3:
        text = """✅ Шарф выбран

*Шаг 3/3:* Выбери варежки

🎯 *Варежки:*"""
        
        keyboard = [
            [
                InlineKeyboardButton("🧤 Теплые", callback_data=f"task_sequence:2:3:gloves"),
                InlineKeyboardButton("🧤 Шерстяные", callback_data=f"task_sequence:2:3:wool_gloves")
            ],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:2")]
        ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_handwarmers_sequence(query, step: int):
    """Добавить грелки"""
    if step == 1:
        text = """🔥 Добавить грелки

Добавь грелки в карманы!

━━━━━━━━━━━━━━━━

ШАГ 1/2: Первая грелка"""
        
        keyboard = [
            [InlineKeyboardButton("🔥 Добавить", callback_data=f"task_sequence:5:1:add")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:5")]
        ]
    elif step == 2:
        text = """✅ Первая грелка добавлена!

━━━━━━━━━━━━━━━━

ШАГ 2/2: Вторая грелка"""
        
        keyboard = [
            [InlineKeyboardButton("🔥 Добавить", callback_data=f"task_sequence:5:2:add")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:5")]
        ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_outfit_sequence(query, step: int):
    """Собрать образ"""
    if step == 1:
        text = """🪞 Собрать образ

Выбери свитер!"""
        
        keyboard = [
            [
                InlineKeyboardButton("🧥 С оленями", callback_data=f"task_sequence:11:1:sweater"),
                InlineKeyboardButton("🧥 Классический", callback_data=f"task_sequence:11:1:classic")
            ],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:11")]
        ]
    elif step == 2:
        text = """✅ Свитер выбран!

━━━━━━━━━━━━━━━━

ШАГ 2/3: Выбери шапку"""
        
        keyboard = [
            [
                InlineKeyboardButton("🧢 С помпоном", callback_data=f"task_sequence:11:2:hat"),
                InlineKeyboardButton("🧢 Классическая", callback_data=f"task_sequence:11:2:classic")
            ],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:11")]
        ]
    elif step == 3:
        text = """✅ Шапка выбрана!

━━━━━━━━━━━━━━━━

ШАГ 3/3: Выбери шарф"""
        
        keyboard = [
            [
                InlineKeyboardButton("🧣 Шерстяной", callback_data=f"task_sequence:11:3:scarf"),
                InlineKeyboardButton("🧣 Теплый", callback_data=f"task_sequence:11:3:warm")
            ],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:11")]
        ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_accessories_sequence(query, step: int):
    """Подобрать аксессуары"""
    if step == 1:
        text = """👔 Подобрать аксессуары

К пальто выбери шарф!"""
        
        keyboard = [
            [
                InlineKeyboardButton("🧣 Шерстяной", callback_data=f"task_sequence:13:1:scarf"),
                InlineKeyboardButton("🧣 Шелковый", callback_data=f"task_sequence:13:1:silk")
            ],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:13")]
        ]
    elif step == 2:
        text = """✅ Шарф выбран!

━━━━━━━━━━━━━━━━

ШАГ 2/2: Выбери перчатки"""
        
        keyboard = [
            [
                InlineKeyboardButton("🧤 Кожаные", callback_data=f"task_sequence:13:2:gloves"),
                InlineKeyboardButton("🧤 Шерстяные", callback_data=f"task_sequence:13:2:wool")
            ],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:13")]
        ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_icecream_sequence_continue(query, step: int):
    """Собрать порцию мороженого - продолжение"""
    if step == 1:
        text = """✅ Пломбир выбран

🍦 Мороженое в рожке
✨ *Шаг 2/2:* Выбери топпинг

🎯 *Топпинг:*"""
        
        keyboard = [
            [
                InlineKeyboardButton("🍫 Шоколадная крошка", callback_data=f"task_sequence:15:1:chocolate"),
                InlineKeyboardButton("🍮 Карамель", callback_data=f"task_sequence:15:1:caramel")
            ],
            [
                InlineKeyboardButton("🫐 Свежие ягоды", callback_data=f"task_sequence:15:1:berries"),
                InlineKeyboardButton("🥜 Орешки", callback_data=f"task_sequence:15:1:nuts")
            ],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:15")]
        ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_garland_unwind_sequence(query, step: int):
    """Размотать гирлянду"""
    state_key = f"{query.from_user.id}:25"
    if state_key not in task_states:
        task_states[state_key] = {"count": 0}
    
    count = task_states[state_key].get("count", 0)
    
    if count < 5:
        text = f"""🎀 Размотать гирлянду

Разматывай гирлянду!

━━━━━━━━━━━━━━━━

Размотано: {count}/5"""
        
        keyboard = [
            [InlineKeyboardButton("🎀 Разматывать", callback_data=f"task_sequence:25:1:unwind")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:25")]
        ]
    else:
        text = """✅ Гирлянда размотана!

Готово!"""
        
        keyboard = [
            [InlineKeyboardButton("✅ Готово", callback_data=f"task_sequence:25:2:done")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:25")]
        ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_mandarin_vase_sequence(query, step: int):
    """Наполнить вазу"""
    state_key = f"{query.from_user.id}:26"
    if state_key not in task_states:
        task_states[state_key] = {"count": 0}
    
    count = task_states[state_key].get("count", 0)
    
    if count < 7:
        text = f"""🍊 Наполнить вазу

Добавляй мандарины в вазу!

━━━━━━━━━━━━━━━━

Добавлено: {count}/7"""
        
        keyboard = [
            [InlineKeyboardButton("🍊 Добавить мандарин", callback_data=f"task_sequence:26:1:add")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:26")]
        ]
    else:
        text = """✅ Ваза наполнена!

Готово!"""
        
        keyboard = [
            [InlineKeyboardButton("✅ Готово", callback_data=f"task_sequence:26:2:done")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:26")]
        ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_candles_light_sequence(query, step: int):
    """Зажечь свечи"""
    state_key = f"{query.from_user.id}:28"
    if state_key not in task_states:
        task_states[state_key] = {"count": 0}
    
    count = task_states[state_key].get("count", 0)
    
    if count < 5:
        text = f"""🔥 Зажечь свечи

Зажигай свечи по порядку!

━━━━━━━━━━━━━━━━

Зажжено: {count}/5"""
        
        keyboard = [
            [InlineKeyboardButton("🔥 Зажечь свечу", callback_data=f"task_sequence:28:1:light")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:28")]
        ]
    else:
        text = """✅ Все свечи зажжены!

Готово!"""
        
        keyboard = [
            [InlineKeyboardButton("✅ Готово", callback_data=f"task_sequence:28:2:done")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:28")]
        ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_candy_mix_sequence(query, step: int):
    """Собрать микс конфет"""
    state_key = f"{query.from_user.id}:34"
    if state_key not in task_states:
        task_states[state_key] = {"red": 0, "blue": 0, "green": 0, "yellow": 0}
    
    state = task_states[state_key]
    total = state["red"] + state["blue"] + state["green"] + state["yellow"]
    
    if total < 8:  # По 2 каждого цвета
        text = f"""🍬 Собрать микс конфет

По 2 каждого цвета!

━━━━━━━━━━━━━━━━

🔴 Красные: {state['red']}/2
🔵 Синие: {state['blue']}/2
🟢 Зеленые: {state['green']}/2
🟡 Желтые: {state['yellow']}/2"""
        
        keyboard = [
            [
                InlineKeyboardButton("🔴 Красная", callback_data=f"task_sequence:34:1:red"),
                InlineKeyboardButton("🔵 Синяя", callback_data=f"task_sequence:34:1:blue")
            ],
            [
                InlineKeyboardButton("🟢 Зеленая", callback_data=f"task_sequence:34:1:green"),
                InlineKeyboardButton("🟡 Желтая", callback_data=f"task_sequence:34:1:yellow")
            ],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:34")]
        ]
    else:
        text = """✅ Микс собран!

Готово!"""
        
        keyboard = [
            [InlineKeyboardButton("✅ Готово", callback_data=f"task_sequence:34:2:done")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:34")]
        ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_moscow_set_sequence(query, step: int):
    """Собрать набор 'Москва'"""
    if step == 1:
        text = """📦 Собрать набор "Москва"

Выбери чай!"""
        
        keyboard = [
            [
                InlineKeyboardButton("🫖 Московский", callback_data=f"task_sequence:39:1:tea"),
                InlineKeyboardButton("🫖 Классический", callback_data=f"task_sequence:39:1:classic")
            ],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:39")]
        ]
    elif step == 2:
        text = """✅ Чай выбран!

━━━━━━━━━━━━━━━━

ШАГ 2/3: Выбери сервиз"""
        
        keyboard = [
            [
                InlineKeyboardButton("🍵 Гжель", callback_data=f"task_sequence:39:2:set"),
                InlineKeyboardButton("🍵 Классический", callback_data=f"task_sequence:39:2:classic")
            ],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:39")]
        ]
    elif step == 3:
        text = """✅ Сервиз выбран!

━━━━━━━━━━━━━━━━

ШАГ 3/3: Выбери варенье"""
        
        keyboard = [
            [
                InlineKeyboardButton("🫙 Малина", callback_data=f"task_sequence:39:3:raspberry"),
                InlineKeyboardButton("🫙 Облепиха", callback_data=f"task_sequence:39:3:sea_buckthorn")
            ],
            [
                InlineKeyboardButton("🫙 Брусника", callback_data=f"task_sequence:39:3:cranberry"),
                InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:39")
            ]
        ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_tea_pour_sequence(query, step: int):
    """Разлить по чашкам"""
    state_key = f"{query.from_user.id}:41"
    if state_key not in task_states:
        task_states[state_key] = {"count": 0}
    
    count = task_states[state_key].get("count", 0)
    
    if count < 4:
        text = f"""☕️ Разлить по чашкам

Разливай чай гостям!

━━━━━━━━━━━━━━━━

Разлито: {count}/4"""
        
        keyboard = [
            [InlineKeyboardButton("☕️ Разлить", callback_data=f"task_sequence:41:1:pour")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:41")]
        ]
    else:
        text = """✅ Все чашки наполнены!

Готово!"""
        
        keyboard = [
            [InlineKeyboardButton("✅ Готово", callback_data=f"task_sequence:41:2:done")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:41")]
        ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_sugar_stir_sequence(query, step: int):
    """Помешать сахар"""
    state_key = f"{query.from_user.id}:42"
    if state_key not in task_states:
        task_states[state_key] = {"count": 0}
    
    count = task_states[state_key].get("count", 0)
    
    if count < 3:
        text = f"""🥄 Помешать сахар

Делай круговые движения!

━━━━━━━━━━━━━━━━

Движений: {count}/3"""
        
        keyboard = [
            [InlineKeyboardButton("🥄 Помешать", callback_data=f"task_sequence:42:1:stir")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:42")]
        ]
    else:
        text = """✅ Сахар размешан!

Готово!"""
        
        keyboard = [
            [InlineKeyboardButton("✅ Готово", callback_data=f"task_sequence:42:2:done")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:42")]
        ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_gift_wrap_sequence(query, step: int):
    """Упаковать подарок"""
    if step == 1:
        text = """🎁 Упаковать подарок для мамы

Молодой человек выбрал набор свечей. Нужно красиво упаковать!

━━━━━━━━━━━━━━━━

ШАГ 1/5: Положи подарок на конвейер"""
        
        keyboard = [
            [InlineKeyboardButton("📦 Положить", callback_data=f"task_sequence:47:1:place")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:47")]
        ]
    elif step == 2:
        text = """✅ Подарок на конвейере!

━━━━━━━━━━━━━━━━

ШАГ 2/5: Выбери упаковочную бумагу"""
        
        keyboard = [
            [
                InlineKeyboardButton("🟡 Золотая", callback_data=f"task_sequence:47:2:gold"),
                InlineKeyboardButton("🎄 Скандинавская", callback_data=f"task_sequence:47:2:scandinavian")
            ],
            [
                InlineKeyboardButton("🔴 Красная", callback_data=f"task_sequence:47:2:red"),
                InlineKeyboardButton("⚪️ Белая", callback_data=f"task_sequence:47:2:white")
            ],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:47")]
        ]
    elif step == 3:
        text = """✅ Элегантный выбор!

━━━━━━━━━━━━━━━━

ШАГ 3/5: Заверни бумагу"""
        
        keyboard = [
            [InlineKeyboardButton("🎀 Завернуть", callback_data=f"task_sequence:47:3:wrap")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:47")]
        ]
    elif step == 4:
        text = """✅ Аккуратно!

━━━━━━━━━━━━━━━━

ШАГ 4/5: Завяжи бант"""
        
        keyboard = [
            [
                InlineKeyboardButton("🎀 Красная лента", callback_data=f"task_sequence:47:4:red"),
                InlineKeyboardButton("🤍 Белая лента", callback_data=f"task_sequence:47:4:white")
            ],
            [
                InlineKeyboardButton("💛 Золотая лента", callback_data=f"task_sequence:47:4:gold"),
                InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:47")
            ]
        ]
    elif step == 5:
        text = """✅ Красиво!

━━━━━━━━━━━━━━━━

ШАГ 5/5: Последний штрих — декор"""
        
        keyboard = [
            [
                InlineKeyboardButton("🌲 Еловая веточка", callback_data=f"task_sequence:47:5:branch"),
                InlineKeyboardButton("🔔 Колокольчик", callback_data=f"task_sequence:47:5:bell")
            ],
            [
                InlineKeyboardButton("❄️ Снежинка", callback_data=f"task_sequence:47:5:snowflake"),
                InlineKeyboardButton("✨ Без декора", callback_data=f"task_sequence:47:5:none")
            ],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:47")]
        ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_smooth_folds_sequence(query, step: int):
    """Разгладить складки"""
    state_key = f"{query.from_user.id}:53"
    if state_key not in task_states:
        task_states[state_key] = {"count": 0}
    
    count = task_states[state_key].get("count", 0)
    
    if count < 3:
        text = f"""👋 Разгладить складки

Проводи рукой по складкам!

━━━━━━━━━━━━━━━━

Проведено: {count}/3"""
        
        keyboard = [
            [InlineKeyboardButton("👋 Разгладить", callback_data=f"task_sequence:53:1:smooth")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:53")]
        ]
    else:
        text = """✅ Складки разглажены!

Готово!"""
        
        keyboard = [
            [InlineKeyboardButton("✅ Готово", callback_data=f"task_sequence:53:2:done")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:53")]
        ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_generic_sequence_task(query, task, step: int):
    """Универсальный обработчик последовательностей"""
    text = f"""{task['emoji']} {task['name']}

Шаг {step}"""
    
    keyboard = [
        [InlineKeyboardButton("✅ Продолжить", callback_data=f"task_sequence:{task['id']}:{step}:next")],
        [InlineKeyboardButton("❌ Отменить", callback_data=f"task_cancel:{task['id']}")]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

