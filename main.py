from data.imports import *

load_dotenv()

bot = Bot(os.getenv('TG_TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())


# Расшифровка
def decrypt_api(api):
    cipher = Fernet(bytes(os.getenv('CIPHER_KEY')+'=',encoding='utf-8'))
    return cipher.decrypt(api).decode('utf-8')


# Шифровка
def encrypt_api(api):
    cipher = Fernet(bytes(os.getenv('CIPHER_KEY')+'=',encoding='utf-8'))
    return cipher.encrypt(bytes(api,encoding='utf-8'))



# Дата конца подписки
def next_month(today):
    delta = timedelta(days=30)
    return today + delta


# Успещный запуск бота
async def on_startup(_):
    print("Я был запущен")


# Хендлер старта
@dp.message_handler(commands=["start"])
async def start_func(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text=f"Приветствую, {message.from_user.username}! ВСТАВИТЬ ВСТУПЛЕНИЕ. "
                                f"Подробнее ты можешь узнать нажав  "
                                f"на кнопку \"Описание\"",
                           reply_markup=kb_free)
    # Подключение к бд
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    info = cursor.execute('SELECT * FROM users WHERE user_id=?;', (message.from_user.id, )).fetchone()
    # Если нет в бд
    if info is None:
        cursor.execute(f"""INSERT INTO users VALUES ('{message.from_user.id}', '0', '0', 'free', '', '', '');""")
        conn.commit()
    # Если есть в бд
    else:
        cursor.execute("SELECT status, api_key FROM users WHERE user_id = ?", (message.from_user.id,))
        result = cursor.fetchone()
        # Если статус бесплатный
        if result[0] == "free":
            await bot.send_message(chat_id=message.from_user.id,
                                   text="Мы нашли вашу учетную запись в базе данных.",
                                   reply_markup=kb_free)
        # Если статус платный
        elif result[0] == "paid":
            if result[1] == "":
                await bot.send_message(chat_id=message.from_user.id,
                                       text="Мы нашли вашу учетную запись в базе данных.",
                                       reply_markup=kb_unreg)
            else:
                await bot.send_message(chat_id=message.from_user.id,
                                       text="Мы нашли вашу учетную запись в базе данных.",
                                       reply_markup=kb_reg)

    await message.delete()


# Хендлер Описания
@dp.message_handler(Text(equals="Описание"))
async def descr_func(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text=DESCR)


# Хендлер Инструкции
@dp.message_handler(Text(equals="Инструкция"))
async def descr_func(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text=INSTRUCT,
                           parse_mode="HTML",
                           reply_markup=kb_instruct)



# Хендлер Покупки подписки
@dp.message_handler(Text(equals="Оформить подписку"))
async def buy(message: types.Message):
    if (PAYMENTS_TOKEN:=os.getenv('PAYMENTS_TOKEN')).split(":")[1] == "TEST":
        await bot.send_message(message.chat.id,
                               "Тестовый платеж")
    await bot.send_invoice(message.chat.id,
                           title="Подписка на Taber Bot",
                           description="Активация подписки на 1 месяц",
                           provider_token=PAYMENTS_TOKEN,
                           currency="rub",
                           photo_url="https://i.postimg.cc/3RXYBqbV/kandinsky-download-1681585603018.png",
                           photo_width=400,
                           photo_height=300,
                           is_flexible=False,
                           prices=[PRICE],
                           start_parameter="one-month-subscription",
                           payload="tesy-invoice-payload")


@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# Результат после оплаты
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successfull_payment(message: types.Message):
    print("Success")
    payment_info = message.successful_payment.to_python()
    tranzaktion = ""
    for k, v in payment_info.items():
        if k == "telegram_payment_charge_id":
            tranzaktion = v
        print(f"{k} = {v}")
    print('\n')
    await bot.send_message(message.chat.id,
                           f"Платеж на сумму <b>{message.successful_payment.total_amount // 100} "
                           f"{message.successful_payment.currency}</b> прошел успешно. "
                           f"Номер вашей транзакции {tranzaktion}. Приятного пользования!",
                           parse_mode="HTML",
                           reply_markup=kb_unreg
                           )

    # Изменение статуса
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    cursor.execute(f"""Update users set status = "paid", subscribe_start = "{date.today()}", 
                       subscribe_finish = "{next_month(date.today())}" 
                       where user_id = {message.from_user.id}""")
    conn.commit()
    cursor.close()


# Хендлер Возращения в меню
@dp.message_handler(Text(equals="В меню"))
async def menu_func(message: types.Message):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT status, api_key FROM users WHERE user_id = ?", (message.from_user.id,))
    result = cursor.fetchone()
    if result[0] == "free":
        await bot.send_message(chat_id=message.from_user.id,
                               text="Вы вернулись в меню🦩",
                               parse_mode="HTML",
                               reply_markup=kb_free)
    elif result[0] == "paid" and result[1] != "":
        await bot.send_message(chat_id=message.from_user.id,
                               text="Вы вернулись в меню🦩",
                               parse_mode="HTML",
                               reply_markup=kb_reg)
    elif result[0] == "paid" and result[1] == "":
        await bot.send_message(chat_id=message.from_user.id,
                               text="Вы вернулись в меню🦩",
                               parse_mode="HTML",
                               reply_markup=kb_unreg)


# Хендлер Предостережения
@dp.message_handler(Text(equals="❌Предостережения❌"))
async def predostr_func(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text=PREDOSTR,
                           parse_mode="HTML")


# Хендлер Пользование ботом
@dp.message_handler(Text(equals="Как начать пользоваться ботом?"))
async def instruct_func(message: types.Message):
    await bot.send_video(chat_id=message.from_user.id,
                         video=open("imgs/CHANGE_TO_INSTRUCTION.mp4", "rb"),
                         caption="Подробная инструкция")


# !!!ПЛАТНЫЙ ФУНКЦИОНАЛ!!!
# Хендлер Авторизации
@dp.message_handler(Text(equals="Авторизация"))
async def auth_func(message: types.Message):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM users WHERE user_id = ?", (message.from_user.id,))
    result = cursor.fetchone()
    if result[0] == "paid":
        await bot.send_message(chat_id=message.from_user.id,
                               text="Введите ваш <b>api_key</b> и <b>api_secret</b> через пробел: ",
                               parse_mode="HTML")
        await Auth.api.set()
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text="Вы еще не оплатили подписку",
                               parse_mode="HTML")


# Хендлер получения Api
@dp.message_handler(state=Auth.api)
async def set_api(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        proxy['api'] = message.text
        await state.finish()
    s = await state.get_data()

    api_key = encrypt_api(s['api'].partition(' ')[0])
    api_secret = encrypt_api(s['api'].partition(' ')[2])
    try:
        test = HTTP(
            api_key=decrypt_api(api_key),
            api_secret=decrypt_api(api_secret))
        test.get_account_info()
    except exceptions.InvalidRequestError as e:
        await bot.send_message(message.chat.id, 'Api key или Api secret указаны неверно. Повторите попытку', reply_markup=kb_unreg)
        print(e)
        return
    
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    cursor.execute(f"""UPDATE users SET api_secret = "{api_secret}", api_key = "{api_key}"
                            WHERE user_id = {message.from_user.id}""")
    conn.commit()
    cursor.close()
    await bot.send_message(message.chat.id, 'Ваш профиль создан', reply_markup=kb_reg)



# Проверка на полную регистрацию
def api_stock(a):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    return cursor.execute('SELECT api_secret FROM users WHERE user_id=?;', (a,)).fetchone()


# Хендлер Профиля
@dp.message_handler(Text(equals="Профиль"))
async def profile_func(message: types.Message):
    info = api_stock(message.from_user.id)
    if info is not None:
        await message.answer(text="Выберите действие", reply_markup=kb_profile)


# Хендлер Баланса
@dp.message_handler(Text(equals="Баланс"))
async def balance_func(message: types.Message):
    info = api_stock(message.from_user.id)
    if info is not None:
        conn = sqlite3.connect('db/database.db')
        cursor = conn.cursor()
        data = cursor.execute('SELECT api_secret, api_key FROM users WHERE user_id=?;', (message.from_user.id,)).fetchone()
        session = HTTP(
            api_key=decrypt_api(data[1][2:-1]),
            api_secret=decrypt_api(data[0][2:-1])
        )
        
        wallet_balance_data = session.get_wallet_balance(accountType="UNIFIED")["result"]["list"][0]
        coins = wallet_balance_data["coin"]
        total_balance = wallet_balance_data["totalEquity"]
        total_balance_msg = ""

        for obj in coins:
            total_balance_msg += f"<b>{obj['coin']}</b>: <b>{obj['equity']}</b>\n"

        total_balance_msg += f"<b>Общий баланс: {total_balance}</b> $"
        await bot.send_message(chat_id=message.from_user.id,
                               text=total_balance_msg,
                               parse_mode="HTML")


# Хендлер хуйни
@dp.message_handler()
async def unknown_func(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text="Мы не предусмотрели данный запрос. Повторите попытку.")


# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)




