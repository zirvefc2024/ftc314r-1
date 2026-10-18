# Бот расписания группы 314R1

Поддержка русского и азербайджанского языков.  
Расписание, уведомления, материалы, ответы на опаздания.

## Быстрый старт (локально)

1. Склонируй или скачай проект.
2. Создай файл `.env` на основе `.env.example`:
   ```bash
   cp .env.example .env
   ```
3. Открой `.env` и вставь свои данные:
   ```env
   BOT_TOKEN=твой_токен_от_BotFather
   CREATOR_ID=твой_telegram_id
   ```
4. Установи зависимости:
   ```bash
   pip install -r requirements.txt
   ```
5. Запусти:
   ```bash
   python bot.py
   ```

## Как получить токен и ID

- Токен: напиши [@BotFather](https://t.me/BotFather) → `/newbot`
- Свой ID: напиши [@userinfobot](https://t.me/userinfobot)

## Загрузка на GitHub

1. Создай репозиторий на GitHub (лучше приватный).
2. В папке проекта:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/ТВОЙ_НИК/название.git
   git push -u origin main
   ```
3. Файл `.env` **не попадёт** в репозиторий (он в `.gitignore`).

## Деплой (хостинг)

Рекомендуемые варианты:

- **Amvera** — удобно, есть постоянный диск
- **Railway** — простой деплой с GitHub
- **VPS** (Oracle Always Free и др.)

### Важно при деплое

- Задай переменные `BOT_TOKEN` и `CREATOR_ID` в панели хостинга (Environment Variables).
- Подключи **постоянный диск (volume)** и укажи, чтобы база `schedule_bot.db` лежала на нём.
- Иначе при перезапуске пропадут пользователи и материалы.

## Команды для администратора

- `/approve 123456789` — одобрить пользователя
- `/setstarosta 123456789` — назначить старосту

## Структура

- `bot.py` — основной файл
- `.env.example` — пример настроек
- `config.py` — предметы и дата старта
- `data/schedule.py` — расписание
- `locales/strings.py` — тексты RU/AZ
- `utils/` — база, погода, логика

## Дата отсчёта недель

15 сентября 2026 года = верхняя неделя (üst həftə).
