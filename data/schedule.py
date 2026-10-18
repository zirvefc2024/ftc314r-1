"""
Расписание группы 314R1
ÜST HƏFTƏ — верхняя неделя
ALT HƏFTƏ — нижняя неделя
Старт: 15.09.2026 — верхняя неделя
"""

SCHEDULE = {
    "upper": {  # ÜST HƏFTƏ
        0: [  # Понедельник (0 = Monday)
            {"time": "09:50–11:25", "subject": "Fiziki tərbiyənin təşkili və idarə olunması", "type": "seminar", "room": "406", "teacher": "Şadlinskaya Gülmirə Maqsud"},
            {"time": "11:40–13:15", "subject": "Sahibkarlığın əsasları və biznesə giriş", "type": "mühazirə", "room": "330", "teacher": "İsrafilov Vəli Vəliyullah"},
        ],
        1: [  # Вторник
            {"time": "08:00–09:35", "subject": "Hərbi qanunvericiliyin əsasları", "type": "seminar", "room": "330", "teacher": "Bağırov Sədyar Abusalat"},
            {"time": "09:50–11:25", "subject": "Hərbi qanunvericiliyin əsasları", "type": "mühazirə", "room": "S-3", "teacher": "Bağırov Sədyar Abusalat"},
            {"time": "11:40–13:15", "subject": "Mülki müdafiə və ilkin tibbi yardım-2", "type": "mühazirə", "room": "301", "teacher": "Babayev Mehman Əli"},
        ],
        2: [  # Среда
            {"time": "09:50–11:25", "subject": "Fiziki tərbiyənin nəzəriyyəsi və tədrisi metodikası-2", "type": "mühazirə", "room": "302", "teacher": "Məmmədova Elnarə Xeyrəddin"},
            {"time": "11:40–13:15", "subject": "Fiziki tərbiyənin nəzəriyyəsi və tədrisi metodikası-2", "type": "seminar", "room": "429", "teacher": "Məmmədova Elnarə Xeyrəddin"},
        ],
        3: [  # Четверг
            {"time": "08:00–09:35", "subject": "Gənclərin çağırışaqədər hazırlığının nəzəriyyəsi və tədrisi metodikası", "type": "mühazirə", "room": "408", "teacher": "Şirinov Mübariz Şikar"},
            {"time": "09:50–11:25", "subject": "Fiziki tərbiyənin təşkili və idarə olunması", "type": "mühazirə", "room": "330", "teacher": "İsrafilov Vəli Vəliyullah"},
            {"time": "11:40–13:15", "subject": "Gənclərin çağırışaqədər hazırlığının nəzəriyyəsi və tədrisi metodikası-1", "type": "seminar", "room": "437", "teacher": "Şirinov Mübariz Şikar"},
        ],
        4: [  # Пятница
            {"time": "08:00–09:35", "subject": "Sahibkarlığın əsasları və biznesə giriş", "type": "seminar", "room": "435", "teacher": "İsrafilov Vəli Vəliyullah"},
        ],
    },
    "lower": {  # ALT HƏFTƏ
        0: [  # Понедельник
            {"time": "09:50–11:25", "subject": "Fiziki tərbiyənin təşkili və idarə olunması", "type": "seminar", "room": "406", "teacher": "Şadlinskaya Gülmirə Maqsud"},
        ],
        1: [  # Вторник
            {"time": "08:00–09:35", "subject": "Hərbi qanunvericiliyin əsasları", "type": "seminar", "room": "330", "teacher": "Bağırov Sədyar Abusalat"},
            {"time": "09:50–11:25", "subject": "Hərbi qanunvericiliyin əsasları", "type": "mühazirə", "room": "S-3", "teacher": "Bağırov Sədyar Abusalat"},
            {"time": "11:40–13:15", "subject": "Mülki müdafiə və ilkin tibbi yardım-2", "type": "praktiki məşğələ", "room": "Q-1 / V-1", "teacher": "Babayev Mehman Əli / Xudiyeva Gülrosxar Xalid", "note": "314R1-1 / 314R1-2"},
        ],
        2: [  # Среда
            {"time": "08:00–09:35", "subject": "Sosiologiya", "type": "seminar", "room": "330", "teacher": "Babayev Sənan Əlibala"},
            {"time": "09:50–11:25", "subject": "Fiziki tərbiyənin nəzəriyyəsi və tədrisi metodikası-2", "type": "mühazirə", "room": "302", "teacher": "Məmmədova Elnarə Xeyrəddin"},
            {"time": "11:40–13:15", "subject": "Fiziki tərbiyənin nəzəriyyəsi və tədrisi metodikası-2", "type": "seminar", "room": "429", "teacher": "Məmmədova Elnarə Xeyrəddin"},
        ],
        3: [  # Четверг — как в верхней
            {"time": "08:00–09:35", "subject": "Gənclərin çağırışaqədər hazırlığının nəzəriyyəsi və tədrisi metodikası", "type": "mühazirə", "room": "408", "teacher": "Şirinov Mübariz Şikar"},
            {"time": "09:50–11:25", "subject": "Fiziki tərbiyənin təşkili və idarə olunması", "type": "mühazirə", "room": "330", "teacher": "İsrafilov Vəli Vəliyullah"},
            {"time": "11:40–13:15", "subject": "Gənclərin çağırışaqədər hazırlığının nəzəriyyəsi və tədrisi metodikası-1", "type": "seminar", "room": "437", "teacher": "Şirinov Mübariz Şikar"},
        ],
        4: [  # Пятница
            {"time": "08:00–09:35", "subject": "Sosiologiya", "type": "mühazirə", "room": "413", "teacher": "Babayev Sənan Əlibala"},
        ],
    },
}

DAY_NAMES = {
    0: "Понедельник / Bazar ertəsi",
    1: "Вторник / Çərşənbə axşamı",
    2: "Среда / Çərşənbə",
    3: "Четверг / Cümə axşamı",
    4: "Пятница / Cümə",
}
