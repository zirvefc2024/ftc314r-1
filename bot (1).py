"""
Полный бот расписания 314R1
- Языки: RU / AZ
- Одобрение пользователей
- Расписание (верхняя/нижняя неделя)
- Вечерние уведомления + погода
- Уведомления за 5 минут
- Материалы (задания/конспекты/файлы) — только админ + староста
- Ответы «опаздываю / не буду» + просмотр
"""

import asyncio
import logging
from datetime import timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from locales.strings import t
from utils.database import (
    init_db, add_or_update_user, set_language, get_user_lang,
    is_approved, approve_user, get_approved_users, is_admin,
    add_material, get_materials, save_response, get_responses,
    get_all_users, delete_user,
)
from utils.schedule_utils import (
    format_day_schedule, get_tomorrow, get_week_type,
    get_schedule_for_date, format_week, get_baku_today,
)
from utils.weather import get_tomorrow_weather
from data.schedule import SCHEDULE
from config import SUBJECTS

import os
from dotenv import load_dotenv

load_dotenv()

# ====================== НАСТРОЙКИ ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CREATOR_ID = int(os.getenv("CREATOR_ID", "0"))
STAROSTA_IDS = []  # можно оставить пустым или читать из env при необходимости

if not BOT_TOKEN or CREATOR_ID == 0:
    raise ValueError("Заполни BOT_TOKEN и CREATOR_ID в файле .env")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class AddMaterial(StatesGroup):
    subject = State()
    mtype = State()
    title = State()
    text = State()
    file = State()


# ====================== ВСПОМОГАТЕЛЬНЫЕ ======================

def lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="Azərbaycan", callback_data="lang_az")],
    ])


def main_menu(lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("btn_schedule", lang))],
            [KeyboardButton(text=t("btn_subjects", lang))],
        ],
        resize_keyboard=True,
    )


def schedule_menu(lang: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("btn_today", lang), callback_data="sch_today"),
            InlineKeyboardButton(text=t("btn_tomorrow", lang), callback_data="sch_tomorrow"),
        ],
        [
            InlineKeyboardButton(text=t("btn_this_week", lang), callback_data="sch_this"),
            InlineKeyboardButton(text=t("btn_next_week", lang), callback_data="sch_next"),
        ],
    ])


def subjects_keyboard(lang: str):
    buttons = []
    for i, subj in enumerate(SUBJECTS):
        buttons.append([InlineKeyboardButton(text=subj, callback_data=f"subj_{i}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def response_keyboard(lesson_key: str, lang: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_late", lang), callback_data=f"resp_late_{lesson_key}")],
        [InlineKeyboardButton(text=t("btn_absent", lang), callback_data=f"resp_absent_{lesson_key}")],
        [InlineKeyboardButton(text=t("btn_responses", lang), callback_data=f"view_resp_{lesson_key}")],
    ])


# ====================== ХЕНДЛЕРЫ ======================

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await add_or_update_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name,
    )
    await message.answer(t("choose_lang"), reply_markup=lang_keyboard())


@dp.callback_query(F.data.startswith("lang_"))
async def set_lang(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    await set_language(callback.from_user.id, lang)
    # Автоматическое одобрение
    await approve_user(callback.from_user.id, role="student")
    await callback.message.edit_text(t("lang_set", lang))
    await callback.message.answer(t("welcome", lang), reply_markup=main_menu(lang))
    # Уведомляем создателя о новом пользователе
    try:
        await bot.send_message(
            CREATOR_ID,
            f"Новый пользователь (автоодобрен): {callback.from_user.full_name} (@{callback.from_user.username})\n"
            f"ID: {callback.from_user.id}"
        )
    except Exception:
        pass


@dp.message(F.text.in_([t("btn_schedule", "ru"), t("btn_schedule", "az")]))
async def show_schedule_menu(message: Message):
    if not await is_approved(message.from_user.id):
        lang = await get_user_lang(message.from_user.id)
        await message.answer(t("not_approved", lang))
        return
    lang = await get_user_lang(message.from_user.id)
    await message.answer(t("btn_schedule", lang), reply_markup=schedule_menu(lang))


@dp.callback_query(F.data.startswith("sch_"))
async def schedule_callback(callback: CallbackQuery):
    if not await is_approved(callback.from_user.id):
        return
    lang = await get_user_lang(callback.from_user.id)
    action = callback.data.split("_")[1]

    if action == "today":
        text = format_day_schedule(get_baku_today(), lang)
    elif action == "tomorrow":
        text = format_day_schedule(get_tomorrow(), lang)
        weather = await get_tomorrow_weather()
        text += f"\n\n🌤 {t('weather', lang)}: {weather}"
    elif action == "this":
        text = await format_week(get_baku_today(), lang)
    elif action == "next":
        text = await format_week(get_baku_today() + timedelta(days=7), lang)
    else:
        text = "—"

    await callback.message.answer(text)
    await callback.answer()


@dp.message(F.text.in_([t("btn_subjects", "ru"), t("btn_subjects", "az")]))
async def show_subjects(message: Message):
    if not await is_approved(message.from_user.id):
        return
    lang = await get_user_lang(message.from_user.id)
    await message.answer("Выберите предмет:", reply_markup=subjects_keyboard(lang))


@dp.callback_query(F.data.startswith("subj_"))
async def show_subject_materials(callback: CallbackQuery):
    if not await is_approved(callback.from_user.id):
        return
    idx = int(callback.data.split("_")[1])
    subject = SUBJECTS[idx]
    materials = await get_materials(subject)
    lang = await get_user_lang(callback.from_user.id)

    if not materials:
        await callback.message.answer(f"{subject}\n\nПока нет материалов.")
    else:
        text = f"📚 {subject}\n\n"
        for m in materials:
            mtype, title, txt, file_id, file_type, deadline = m
            text += f"• [{mtype.upper()}] {title or ''}\n{txt or ''}\n"
            if deadline:
                text += f"Дедлайн: {deadline}\n"
            text += "\n"
        await callback.message.answer(text)

        # Отправляем файлы отдельно
        for m in materials:
            _, _, _, file_id, file_type, _ = m
            if file_id:
                if file_type == "photo":
                    await callback.message.answer_photo(file_id)
                else:
                    await callback.message.answer_document(file_id)

    # Кнопки для админов
    if await is_admin(callback.from_user.id):
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t("add_hw", lang), callback_data=f"add_hw_{idx}")],
            [InlineKeyboardButton(text=t("add_note", lang), callback_data=f"add_note_{idx}")],
        ])
        await callback.message.answer("Действия:", reply_markup=kb)

    await callback.answer()


# ====================== ДОБАВЛЕНИЕ МАТЕРИАЛОВ (FSM) ======================

@dp.callback_query(F.data.startswith("add_hw_"))
async def start_add_hw(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    idx = int(callback.data.split("_")[-1])
    subject = SUBJECTS[idx]
    await state.update_data(subject=subject, mtype="hw")
    await state.set_state(AddMaterial.title)
    await callback.message.answer(f"Предмет: {subject}\n\nВведите название задания (или /skip):")
    await callback.answer()


@dp.callback_query(F.data.startswith("add_note_"))
async def start_add_note(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    idx = int(callback.data.split("_")[-1])
    subject = SUBJECTS[idx]
    await state.update_data(subject=subject, mtype="note")
    await state.set_state(AddMaterial.title)
    await callback.message.answer(f"Предмет: {subject}\n\nВведите название конспекта (или /skip):")
    await callback.answer()


@dp.message(AddMaterial.title)
async def process_title(message: Message, state: FSMContext):
    title = None if message.text == "/skip" else message.text
    await state.update_data(title=title)
    data = await state.get_data()
    if data["mtype"] == "hw":
        await state.set_state(AddMaterial.text)
        await message.answer("Введите текст задания (или /skip):")
    else:
        await state.set_state(AddMaterial.text)
        await message.answer("Введите текст конспекта (или /skip):")


@dp.message(AddMaterial.text)
async def process_text(message: Message, state: FSMContext):
    text = None if message.text == "/skip" else message.text
    await state.update_data(text=text)
    await state.set_state(AddMaterial.file)
    await message.answer(
        "Пришлите файл или фото (или /skip если без файла).\n"
        "Для задания можно также указать дедлайн в формате ДД.ММ.ГГГГ после файла."
    )


async def notify_new_material(subject: str, mtype: str, title: str):
    """Отправляет уведомление всем одобренным пользователям о новом материале."""
    users = await get_approved_users()
    mtype_label = "Задание" if mtype == "hw" else "Конспект"
    title_text = title or "Без названия"

    for uid in users:
        try:
            lang = await get_user_lang(uid)
            # Простая локализация типа
            if lang == "az":
                mtype_label_local = "Tapşırıq" if mtype == "hw" else "Konspekt"
            else:
                mtype_label_local = mtype_label

            text = (
                f"{t('new_material', lang)}\n\n"
                f"{t('new_material_body', lang).format(subject=subject, mtype=mtype_label_local, title=title_text)}"
            )
            await bot.send_message(uid, text)
        except Exception as e:
            logging.error(f"New material notify error {uid}: {e}")


@dp.message(AddMaterial.file, F.document | F.photo)
async def process_file(message: Message, state: FSMContext):
    data = await state.get_data()
    file_id = None
    file_type = None
    if message.document:
        file_id = message.document.file_id
        file_type = "document"
    elif message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"

    deadline = None
    await add_material(
        subject=data["subject"],
        mtype=data["mtype"],
        title=data.get("title"),
        text=data.get("text"),
        file_id=file_id,
        file_type=file_type,
        deadline=deadline,
        added_by=message.from_user.id,
    )
    await state.clear()
    await message.answer("✅ Материал успешно добавлен!")

    # Уведомляем всех
    await notify_new_material(data["subject"], data["mtype"], data.get("title"))


@dp.message(AddMaterial.file, F.text == "/skip")
async def process_skip_file(message: Message, state: FSMContext):
    data = await state.get_data()
    await add_material(
        subject=data["subject"],
        mtype=data["mtype"],
        title=data.get("title"),
        text=data.get("text"),
        file_id=None,
        file_type=None,
        deadline=None,
        added_by=message.from_user.id,
    )
    await state.clear()
    await message.answer("✅ Материал успешно добавлен (без файла)!")

    # Уведомляем всех
    await notify_new_material(data["subject"], data["mtype"], data.get("title"))


@dp.message(Command("cancel"))
async def cancel_fsm(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено.")


# ====================== ДОПОЛНИТЕЛЬНЫЕ КОМАНДЫ ======================

@dp.message(Command("setstarosta"))
async def set_starosta(message: Message):
    if message.from_user.id != CREATOR_ID:
        return
    try:
        uid = int(message.text.split()[1])
        await approve_user(uid, role="starosta")
        await message.answer(f"Пользователь {uid} назначен старостой.")
        try:
            await bot.send_message(uid, "Вас назначили старостой. Теперь вы можете добавлять материалы.")
        except Exception:
            pass
    except Exception:
        await message.answer("Использование: /setstarosta <user_id>")


@dp.message(Command("users"))
async def list_users(message: Message):
    if message.from_user.id != CREATOR_ID:
        return
    users = await get_all_users()
    if not users:
        await message.answer("Пользователей пока нет.")
        return
    text = "👥 Пользователи:\n\n"
    for uid, username, full_name, role, approved in users:
        name = full_name or username or "—"
        text += f"• {name} | ID: {uid} | роль: {role}\n"
    await message.answer(text)


@dp.message(Command("delete"))
async def cmd_delete(message: Message):
    if message.from_user.id != CREATOR_ID:
        return
    try:
        uid = int(message.text.split()[1])
        if uid == CREATOR_ID:
            await message.answer("Нельзя удалить создателя.")
            return
        await delete_user(uid)
        await message.answer(f"Пользователь {uid} удалён.")
    except Exception:
        await message.answer("Использование: /delete <user_id>")



@dp.callback_query(F.data.startswith("resp_"))
async def handle_response(callback: CallbackQuery):
    if not await is_approved(callback.from_user.id):
        return
    parts = callback.data.split("_", 2)
    resp_type = parts[1]          # late / absent
    lesson_key = parts[2]
    await save_response(callback.from_user.id, lesson_key, resp_type)
    lang = await get_user_lang(callback.from_user.id)
    await callback.answer(t("response_saved", lang), show_alert=True)


@dp.callback_query(F.data.startswith("view_resp_"))
async def view_responses(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("Только для старосты и администратора", show_alert=True)
        return
    lesson_key = callback.data.replace("view_resp_", "")
    rows = await get_responses(lesson_key)
    lang = await get_user_lang(callback.from_user.id)

    if not rows:
        await callback.message.answer(t("no_responses", lang))
        return

    late = []
    absent = []
    for full_name, username, resp in rows:
        name = full_name or username or "—"
        if resp == "late":
            late.append(name)
        elif resp == "absent":
            absent.append(name)

    text = f"📋 Ответы:\n\n"
    text += f"⏰ {t('late_list', lang)} ({len(late)}):\n" + "\n".join(f"• {n}" for n in late) + "\n\n"
    text += f"❌ {t('absent_list', lang)} ({len(absent)}):\n" + "\n".join(f"• {n}" for n in absent)
    await callback.message.answer(text)
    await callback.answer()


# ====================== ЗАПУСК ======================

async def main():
    await init_db()
    # Автоматически делаем создателя админом
    await add_or_update_user(CREATOR_ID, "", "Creator")
    await approve_user(CREATOR_ID, role="creator")

    logging.info("Бот успешно запущен (без автоматических уведомлений)")
    try:
        await bot.send_message(
            CREATOR_ID,
            "✅ Бот запущен.\n"
            "Автоуведомления отключены.\n"
            "Пользователи одобряются автоматически.\n"
            "Команды: /users /setstarosta /delete"
        )
    except Exception:
        logging.warning("Не удалось отправить сообщение создателю о запуске")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
