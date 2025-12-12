import aiosqlite
from config import DATABASE_PATH

async def init_db():
    """Инициализация базы данных"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Таблица пользователей
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                coins INTEGER DEFAULT 50,
                pavilions_open TEXT DEFAULT '[]',
                facts_collected TEXT DEFAULT '[]',
                tasks_completed INTEGER DEFAULT 0,
                guests_served INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица павильонов (справочная)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS pavilions (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                emoji TEXT NOT NULL,
                location TEXT NOT NULL,
                price INTEGER NOT NULL,
                reward INTEGER NOT NULL,
                description TEXT NOT NULL,
                atmosphere TEXT NOT NULL,
                tasks_count INTEGER NOT NULL
            )
        """)
        
        # Таблица заданий (справочная)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                pavilion_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                emoji TEXT NOT NULL,
                type TEXT NOT NULL,
                reward INTEGER NOT NULL,
                fact_id INTEGER,
                FOREIGN KEY (pavilion_id) REFERENCES pavilions(id)
            )
        """)
        
        # Таблица фактов (справочная)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY,
                pavilion_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                FOREIGN KEY (pavilion_id) REFERENCES pavilions(id)
            )
        """)
        
        await db.commit()

async def get_user(user_id: int):
    """Получить пользователя или создать нового"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        )
        user = await cursor.fetchone()
        
        if not user:
            await db.execute(
                "INSERT INTO users (user_id, coins) VALUES (?, ?)",
                (user_id, 50)
            )
            await db.commit()
            cursor = await db.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,)
            )
            user = await cursor.fetchone()
        
        return dict(user)

async def get_user_coins(user_id: int) -> int:
    """Получить количество мандаринок пользователя"""
    user = await get_user(user_id)
    return user['coins']

async def add_coins(user_id: int, amount: int):
    """Добавить мандаринки"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE users SET coins = coins + ? WHERE user_id = ?",
            (amount, user_id)
        )
        await db.commit()

async def subtract_coins(user_id: int, amount: int):
    """Списать мандаринки"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE users SET coins = coins - ? WHERE user_id = ?",
            (amount, user_id)
        )
        await db.commit()

async def get_open_pavilions(user_id: int) -> list:
    """Получить список открытых павильонов"""
    import json
    user = await get_user(user_id)
    try:
        return json.loads(user['pavilions_open'])
    except (json.JSONDecodeError, TypeError):
        return []

async def open_pavilion(user_id: int, pavilion_id: int):
    """Открыть павильон"""
    import json
    async with aiosqlite.connect(DATABASE_PATH) as db:
        user = await get_user(user_id)
        try:
            pavilions = json.loads(user['pavilions_open'])
        except (json.JSONDecodeError, TypeError):
            pavilions = []
        if pavilion_id not in pavilions:
            pavilions.append(pavilion_id)
            await db.execute(
                "UPDATE users SET pavilions_open = ? WHERE user_id = ?",
                (json.dumps(pavilions), user_id)
            )
            await db.commit()

async def get_collected_facts(user_id: int) -> list:
    """Получить список собранных фактов"""
    import json
    user = await get_user(user_id)
    try:
        return json.loads(user['facts_collected'])
    except (json.JSONDecodeError, TypeError):
        return []

async def add_fact_to_collection(user_id: int, fact_id: int):
    """Добавить факт в коллекцию"""
    import json
    async with aiosqlite.connect(DATABASE_PATH) as db:
        user = await get_user(user_id)
        try:
            facts = json.loads(user['facts_collected'])
        except (json.JSONDecodeError, TypeError):
            facts = []
        if fact_id not in facts:
            facts.append(fact_id)
            await db.execute(
                "UPDATE users SET facts_collected = ? WHERE user_id = ?",
                (json.dumps(facts), user_id)
            )
            await db.commit()

async def increment_tasks_completed(user_id: int):
    """Увеличить счетчик выполненных заданий"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE users SET tasks_completed = tasks_completed + 1 WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()

async def increment_guests_served(user_id: int):
    """Увеличить счетчик обслуженных гостей"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE users SET guests_served = guests_served + 1 WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()

async def get_all_pavilions():
    """Получить все павильоны"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM pavilions ORDER BY id")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def get_pavilion(pavilion_id: int):
    """Получить павильон по ID"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM pavilions WHERE id = ?", (pavilion_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

async def get_pavilion_tasks(pavilion_id: int):
    """Получить задания павильона"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM tasks WHERE pavilion_id = ? ORDER BY id",
            (pavilion_id,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def get_task(task_id: int):
    """Получить задание по ID"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

async def get_fact(fact_id: int):
    """Получить факт по ID"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM facts WHERE id = ?", (fact_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

async def get_pavilion_facts(pavilion_id: int):
    """Получить факты павильона"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM facts WHERE pavilion_id = ? ORDER BY id",
            (pavilion_id,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def get_user_stats(user_id: int):
    """Получить статистику пользователя"""
    user = await get_user(user_id)
    return {
        'coins_earned': user['coins'],
        'guests_served': user['guests_served'],
        'pavilions_open': len(await get_open_pavilions(user_id)),
        'facts_collected': len(await get_collected_facts(user_id)),
        'tasks_completed': user['tasks_completed']
    }

