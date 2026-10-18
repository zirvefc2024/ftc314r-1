"""
Основной файл бота (скелет)
aiogram 3 + APScheduler
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from utils.schedule_utils import format_day_schedule, get_tomorrow, get_week_type
from utils.weather import get_tomorrow_weather

# === НАСТРОЙКИ ===
BOT_TOKEN = "ВАШ_ТОКЕН_ОТ_BOTFATHER"
ADMIN_IDS = [123456789]  # твой Telegram ID и старосты

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler(timezone="Asia/Baku")


# ==================== КОМАНДЫ ====================

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я бот расписания группы 314R1.\n"
        "Доступ только после одобрения.\n"
        "Команды:\n"
        "/today — сегодня\n"
        "/tomorrow — завтра\n"
        "/week — эта неделя"
    )


@dp.message(Command("tomorrow"))
async def cmd_tomorrow(message: Message):
    tomorrow = get_tomorrow()
    text = format_day_schedule(tomorrow)
    weather = await get_tomorrow_weather()
    await message.answer(f"{text}\n\n🌤 {weather}")


@dp.message(Command("today"))
async def cmd_today(message: Message):
    from datetime import date
    text = format_day_schedule(date.today())
    await message.answer(text)


# ==================== ЕЖЕВЕЧЕРНЕЕ УВЕДОМЛЕНИЕ ====================

async def send_evening_notification():
    """Рассылает расписание на завтра + погоду всем одобренным."""
    tomorrow = get_tomorrow()
    schedule_text = format_day_schedule(tomorrow)
    weather = await get_tomorrow_weather()

    full_text = f"{schedule_text}\n\n🌤 {weather}"

    # TODO: получить список одобренных user_id из базы
    # Пока пример:
    # for user_id in get_approved_users():
    #     try:
    #         await bot.send_message(user_id, full_text)
    #     except Exception:
    #         pass

    # Для теста — отправить админам
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, full_text)
        except Exception as e:
            logging.error(f"Не удалось отправить админу {admin_id}: {e}")


def setup_scheduler():
    # Каждый день в 20:30 по Баку
    scheduler.add_job(
        send_evening_notification,
        CronTrigger(hour=20, minute=30, timezone="Asia/Baku"),
        id="evening_schedule",
        replace_existing=True,
    )
    scheduler.start()
    logging.info("Планировщик запущен (вечернее уведомление в 20:30)")


# ==================== ЗАПУСК ====================

async def main():
    setup_scheduler()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
