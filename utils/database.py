"""
База данных (SQLite + aiosqlite)
Пользователи, язык, материалы, ответы на уведомления
"""

import os
import aiosqlite
from datetime import datetime

# Сохраняем базу в постоянное хранилище Amvera (/data)
DB_PATH = "/data/schedule_bot.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                lang TEXT DEFAULT 'ru',
                approved INTEGER DEFAULT 0,
                role TEXT DEFAULT 'student',  -- student / starosta / creator
                created_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT,
                type TEXT,          -- hw / note / file
                title TEXT,
                text TEXT,
                file_id TEXT,
                file_type TEXT,
                deadline TEXT,
                added_by INTEGER,
                created_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                lesson_key TEXT,    -- дата+время+предмет
                response TEXT,      -- late / absent
                created_at TEXT,
                UNIQUE(user_id, lesson_key)
            )
        """)
        await db.commit()


async def add_or_update_user(user_id: int, username: str, full_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (user_id, username, full_name, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                full_name = excluded.full_name
        """, (user_id, username or "", full_name or "", datetime.now().isoformat()))
        await db.commit()


async def set_language(user_id: int, lang: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET lang = ? WHERE user_id = ?", (lang, user_id))
        await db.commit()


async def get_user_lang(user_id: int) -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else "ru"


async def is_approved(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT approved FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            return bool(row and row[0])


async def approve_user(user_id: int, role: str = "student"):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET approved = 1, role = ? WHERE user_id = ?",
            (role, user_id)
        )
        await db.commit()


async def get_approved_users():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM users WHERE approved = 1") as cur:
            return [row[0] async for row in cur]


async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT user_id, username, full_name, role, approved FROM users ORDER BY created_at"
        ) as cur:
            return await cur.fetchall()


async def delete_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        await db.execute("DELETE FROM responses WHERE user_id = ?", (user_id,))
        await db.commit()


async def is_admin(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT role FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            return row and row[0] in ("creator", "starosta")


async def add_material(subject: str, mtype: str, title: str, text: str, file_id: str, file_type: str, deadline: str, added_by: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO materials (subject, type, title, text, file_id, file_type, deadline, added_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (subject, mtype, title, text, file_id, file_type, deadline, added_by, datetime.now().isoformat()))
        await db.commit()


async def get_materials(subject: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT type, title, text, file_id, file_type, deadline FROM materials WHERE subject = ? ORDER BY created_at DESC",
            (subject,)
        ) as cur:
            return await cur.fetchall()


async def save_response(user_id: int, lesson_key: str, response: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO responses (user_id, lesson_key, response, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, lesson_key) DO UPDATE SET
                response = excluded.response,
                created_at = excluded.created_at
        """, (user_id, lesson_key, response, datetime.now().isoformat()))
        await db.commit()


async def get_responses(lesson_key: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT u.full_name, u.username, r.response
            FROM responses r
            JOIN users u ON u.user_id = r.user_id
            WHERE r.lesson_key = ?
        """, (lesson_key,)) as cur:
            return await cur.fetchall()

# fix