from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# КНОПКИ И ДЛЯ ПЛАТНОГО ЮЗЕРА И ДЛЯ ТРЕЙДЕРА
b_edit_api = KeyboardButton('Редактировать API')

# Бесплатная Клавиатура
kb_free = ReplyKeyboardMarkup(resize_keyboard=True)
b1 = KeyboardButton("Описание")
b2 = KeyboardButton('Наши Трейдеры')
b3 = KeyboardButton("Инструкция")
b4 = KeyboardButton("Оформить подписку")
b5 = KeyboardButton('Info')
kb_free.add(b1,b3).add(b2,b5).add(b4)

# Платная Клавиатура (Незареганный аккаунт)
kb_unreg = ReplyKeyboardMarkup(resize_keyboard=True)
b_unreg1 = KeyboardButton("Авторизация")
kb_unreg.add(b_unreg1).add(b3)

# Платная Клавиатура (Зареганный аккаунт)
kb_reg = ReplyKeyboardMarkup(resize_keyboard=True)
b_p1 = KeyboardButton("Профиль")
b_p2 = KeyboardButton("Настройки бота")
b_p4 = KeyboardButton("Начать торговлю")
b_edit_api = KeyboardButton('Редактировать API')
kb_reg.add(b_p1,b_p2,b_p4).add(b2,b5).add(b_edit_api)

# Клавиатура профиля
kb_profile = ReplyKeyboardMarkup(resize_keyboard=True)
prof_b1 = KeyboardButton("Баланс")
prof_b2 = KeyboardButton("Назад")
kb_profile.add(prof_b1).add(prof_b2)

# Клавиатура инструкции
kb_instruct = ReplyKeyboardMarkup(resize_keyboard=True)
b_ins1 = KeyboardButton("Как создать API ключ?")
b_ins2 = KeyboardButton("❌Предостережения❌")
kb_instruct.add(b_ins1).add(b_ins2).add(prof_b2)

# Клавиатура админ панели
kb_admin = ReplyKeyboardMarkup(resize_keyboard=True)
adb1 = KeyboardButton('Статистика')
adb2 = KeyboardButton('Цены')
adb3 = KeyboardButton('Черный список')
adb4 = KeyboardButton('Вывод данных о клиенте')
adb5 = KeyboardButton('Выдать статус')
adb6 = KeyboardButton('Перешифровка')
kb_admin.add(adb1, adb2).add(adb3, adb4).add(adb5, adb6)

# Клавиатура черного списка
kb_black_list = ReplyKeyboardMarkup(resize_keyboard=True)
bl_btn1 = KeyboardButton('Посмотреть заблокированных')
bl_btn2 = KeyboardButton('Добавить в чс')
bl_btn3 = KeyboardButton('Удалить из чс')
bl_btn4 = KeyboardButton('Назад в админку')
kb_black_list.add(bl_btn1).add(bl_btn2, bl_btn3).add(bl_btn4)

# Клавиатура трейдера
trade1 = KeyboardButton('Статистика Профиля')
trade2 = KeyboardButton('Ключи')
trade3 = KeyboardButton('Помощь')
trade4 = KeyboardButton('Вкл отслеживание')
trade5 = KeyboardButton('Выкл отслеживание')
kb_trader = ReplyKeyboardMarkup(resize_keyboard=True)
kb_trader.add(trade1, trade2).add(trade3, b_edit_api).add(trade4)
kb_trader2 = ReplyKeyboardMarkup(resize_keyboard=True)
kb_trader2.add(trade1, trade2).add(trade3, b_edit_api).add(trade5)


# Клавиатура ключей
kb_keys = ReplyKeyboardMarkup(resize_keyboard=True)
key1 = KeyboardButton('Создать ключ')
key2 = KeyboardButton('Удалить ключ')
key3 = KeyboardButton('Вывод всех ключей')
key4 = KeyboardButton('Вернуться')
kb_keys.add(key1, key2).add(key3).add(key4)

