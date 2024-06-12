import aiosqlite
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
from config import API_TOKEN
from data import quiz_data


# Зададим имя базы данных
DB_NAME2 = 'quiz_bot2.db'

async def create_table():
    async with aiosqlite.connect(DB_NAME2) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state5 (
                            user_id INTEGER PRIMARY KEY, 
                            question_index INTEGER,
                            stat_query INTEGER DEFAULT 0,
                            first_name STRING)''')
        await db.commit()

async def get_quiz_index(user_id):
    async with aiosqlite.connect(DB_NAME2) as db:
        async with db.execute('SELECT question_index FROM quiz_state5 WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0


async def get_statistics(user_id):
    async with aiosqlite.connect(DB_NAME2) as db:
        async with db.execute('SELECT stat_query FROM quiz_state5 WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def update_quiz_index(user_id, index,first_name):
    async with aiosqlite.connect(DB_NAME2) as db:
        async with db.execute('INSERT OR IGNORE INTO quiz_state5 (user_id, question_index, stat_query, first_name) VALUES (?, ?, ?, ?)', (user_id, index, 0,first_name)):
            pass
        await db.execute('UPDATE quiz_state5 SET question_index = ? WHERE user_id = ?', (index, user_id))
        await db.commit()

async def update_statistics(user_id, point, first_name):
    async with aiosqlite.connect(DB_NAME2) as db:
        async with db.execute('INSERT OR IGNORE INTO quiz_state5 (user_id, question_index, stat_query, first_name) VALUES (?, ?, ?,?)', (user_id, 0, 0,first_name)):
            pass
        await db.execute('UPDATE quiz_state5 SET stat_query = ? WHERE user_id = ?', (point, user_id))
        await db.commit()

async def get_table_rows():
    async with aiosqlite.connect(DB_NAME2) as db:
        async with db.execute('SELECT * FROM quiz_state5') as cursor:
            rows = await cursor.fetchall()
            return rows