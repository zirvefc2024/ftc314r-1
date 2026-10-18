"""
Получение погоды для Баку (Гянджлик / Idman Akademiya)
Используем бесплатный Open-Meteo API (без ключа)
"""

import aiohttp
from datetime import datetime, timedelta
from config import WEATHER_LAT, WEATHER_LON, WEATHER_TIMEZONE


async def get_tomorrow_weather() -> str:
    """
    Возвращает строку вида:
    «Завтра +18°, ясно» или «Завтра +12°, дождь, возьмите зонт»
    """
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": WEATHER_LAT,
        "longitude": WEATHER_LON,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
        "timezone": WEATHER_TIMEZONE,
        "forecast_days": 2,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status != 200:
                    return "Погода: не удалось получить данные"
                data = await resp.json()

        daily = data.get("daily", {})
        dates = daily.get("time", [])
        if tomorrow not in dates:
            return "Погода: данные на завтра недоступны"

        idx = dates.index(tomorrow)
        tmax = daily["temperature_2m_max"][idx]
        tmin = daily["temperature_2m_min"][idx]
        precip = daily.get("precipitation_sum", [0])[idx] or 0
        code = daily.get("weathercode", [0])[idx]

        # Простая интерпретация weathercode (Open-Meteo)
        if code in (61, 63, 65, 80, 81, 82, 95):  # дождь / ливень / гроза
            weather_desc = "дождь"
            advice = ", возьмите зонт"
        elif code in (51, 53, 55):  # морось
            weather_desc = "морось"
            advice = ", возьмите зонт"
        elif code in (71, 73, 75, 85, 86):  # снег
            weather_desc = "снег"
            advice = ""
        elif code in (1, 2, 3):  # облачно
            weather_desc = "облачно"
            advice = ""
        else:
            weather_desc = "ясно / малооблачно"
            advice = ""

        temp_str = f"+{round(tmax)}°" if tmax >= 0 else f"{round(tmax)}°"
        return f"Завтра {temp_str} (мин {round(tmin)}°), {weather_desc}{advice}"

    except Exception as e:
        return f"Погода: ошибка ({type(e).__name__})"
