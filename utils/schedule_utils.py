"""
Основные утилиты: определение типа недели, форматирование расписания
"""

from datetime import date, datetime, timedelta
from data.schedule import SCHEDULE, DAY_NAMES
from config import START_DATE


def get_week_type(target_date: date = None) -> str:
    """
    Возвращает 'upper' или 'lower'.
    15.09.2026 (вторник) — верхняя неделя.
    Считаем от понедельника той же недели (14.09.2026).
    """
    if target_date is None:
        target_date = date.today()

    start = datetime.strptime(START_DATE, "%Y-%m-%d").date()
    # Находим понедельник недели, в которую попал START_DATE
    start_monday = start - timedelta(days=start.weekday())

    # Считаем полные недели от этого понедельника
    delta_days = (target_date - start_monday).days
    weeks = delta_days // 7
    return "upper" if weeks % 2 == 0 else "lower"


def get_schedule_for_date(target_date: date) -> list:
    """Возвращает список пар на дату."""
    weekday = target_date.weekday()  # 0 = Monday
    if weekday > 4:  # выходные
        return []

    week_type = get_week_type(target_date)
    return SCHEDULE.get(week_type, {}).get(weekday, [])


def format_day_schedule(target_date: date, lang: str = "ru") -> str:
    """Форматирует расписание на день."""
    from locales.strings import t
    lessons = get_schedule_for_date(target_date)
    day_name = DAY_NAMES.get(target_date.weekday(), "—")
    week_type = get_week_type(target_date)
    week_label = t("week_upper", lang) if week_type == "upper" else t("week_lower", lang)

    if not lessons:
        return f"📅 {day_name}\n{week_label}\n\n{t('no_lessons', lang)}"

    lines = [f"📅 {day_name} — {week_label}\n"]
    for les in lessons:
        note = f" ({les.get('note', '')})" if les.get("note") else ""
        lines.append(
            f"🕒 {les['time']}\n"
            f"   {les['subject']} ({les['type']})\n"
            f"   👨‍🏫 {les['teacher']}\n"
            f"   🚪 {les['room']}{note}"
        )
    return "\n\n".join(lines)


async def format_week(start_date: date, lang: str = "ru") -> str:
    """Форматирует неделю начиная с понедельника."""
    from locales.strings import t
    # Находим понедельник этой недели
    monday = start_date - timedelta(days=start_date.weekday())
    week_type = get_week_type(monday)
    week_label = t("week_upper", lang) if week_type == "upper" else t("week_lower", lang)

    text = f"📆 Неделя с {monday.strftime('%d.%m')} — {week_label}\n\n"
    for i in range(5):
        d = monday + timedelta(days=i)
        day_text = format_day_schedule(d, lang)
        text += day_text + "\n\n" + "—" * 20 + "\n\n"
    return text.strip()


def get_tomorrow() -> date:
    return date.today() + timedelta(days=1)
