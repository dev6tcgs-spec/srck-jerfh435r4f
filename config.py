import os

# Безопасный импорт dotenv
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except ImportError:
    # dotenv не установлен, но это не критично - можно использовать переменные окружения напрямую
    pass

# Токен бота (получите у @BotFather)
# Не проверяем при импорте, проверка будет при запуске через get_bot_token()
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

def get_bot_token():
    """Получить токен бота с проверкой"""
    token = os.getenv("BOT_TOKEN", "")
    if not token:
        raise ValueError(
            "BOT_TOKEN не установлен!\n"
            "Создайте файл .env в корне проекта и добавьте:\n"
            "BOT_TOKEN=ваш_токен_здесь"
        )
    return token

# Путь к базе данных
DATABASE_PATH = "winter_fair.db"

# Стартовый капитал
STARTING_COINS = 50

