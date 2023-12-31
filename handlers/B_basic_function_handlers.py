from handlers.A_head_of_handlers import *
from callbacks.basic_callbacks import *
from callbacks.referral_callbacks import *

# Хендлер старта
@dp.message_handler(commands=["start"])
async def start_func(message: types.Message):
    conn, cursor = db_connect()

    status = cursor.execute(f"SELECT count(*) FROM black_list WHERE id='{message.from_user.id}'").fetchone()[0]
    if status == 1:
        cursor.close()
        await message.delete()
        return
    
    # Проверка на существования человека в бд в таблице referral; если его нет, то он добавляется
    get_ref = cursor.execute(f'SELECT count(*) FROM referral WHERE id = {message.from_user.id}').fetchone()[0]
    if get_ref == 0:
        cursor.execute(f'INSERT INTO referral VALUES("{message.from_user.id}","off",0,{os.environ["Sale"]},{os.environ["Salary"]},0,0)')
        conn.commit()

    if trader_validate(message.from_user.id):
        traders = cursor.execute('SELECT trader_id, api_key FROM traders;').fetchall()
        idx = [*map(lambda x: x[0], traders)].index(message.from_user.id)
        if traders[idx][1] is None or traders[idx][1] == '':
            await bot.send_message(chat_id=message.from_user.id,
                                text="Добро пожаловать! Вы были внесены в список <b>квалифицированных трейдеров</b> на ProofReader. Авторизуйтесь для начала работы.",
                                parse_mode="HTML",
                                reply_markup=kb_unreg)
            cursor.execute(f'UPDATE traders SET name = "{message.from_user.first_name} {message.from_user.last_name} - @{message.from_user.username}" WHERE trader_id = {message.from_user.id}')
        else:
            await bot.send_message(chat_id=message.from_user.id,
                                text="Добро пожаловать! Вы были внесены в список <b>квалифицированных трейдеров</b> на ProofReader.",
                                parse_mode="HTML",
                                reply_markup=kb_trader)
            cursor.execute(f'UPDATE traders SET name = "{message.from_user.first_name} {message.from_user.last_name} - @{message.from_user.username}" WHERE trader_id = {message.from_user.id}')
        conn.commit()
    elif paid_validate(message.from_user.id):
        if cursor.execute(f'SELECT api_key FROM users WHERE user_id = {message.from_user.id}').fetchone()[0] not in (None,''):
            await bot.send_message(chat_id=message.from_user.id,
                                text=f"Приветствуем, {message.from_user.username}! В нашем боте вы сможете использовать те же ордера, что и профессиональные трейдеры на Bybit!. "
                                        f"Подробнее ты можешь узнать нажав  "
                                        f"на кнопку \"Описание\"",
                                reply_markup=kb_reg)
        else:
            await bot.send_message(chat_id=message.from_user.id,
                                text=f"Приветствуем, {message.from_user.username}! В нашем боте вы сможете использовать те же ордера, что и профессиональные трейдеры на Bybit!. "
                                        f"Подробнее ты можешь узнать нажав  "
                                        f"на кнопку \"Описание\" \nАвторизуйтесь для начала работы.",
                                reply_markup=kb_unreg)
    else:
        await bot.send_message(chat_id=message.from_user.id,
                            text=f"Приветствуем, {message.from_user.username}! В нашем боте вы сможете использовать те же ордера, что и профессиональные трейдеры на Bybit!. "
                                    f"Подробнее ты можешь узнать нажав  "
                                    f"на кнопку \"Описание\"",
                            reply_markup=kb_free)
        # Подключение к бд
        info = cursor.execute('SELECT * FROM users WHERE user_id=?;', (message.from_user.id, )).fetchone()
        await db_validate(cursor, conn, message, info)

        # Проверка на приглашение по рефералке
        partner = message.text.replace('/start','').strip()
        find_partner = cursor.execute(f'SELECT count(*) FROM referral WHERE id = "{partner}" AND status = "on"').fetchone()[0]

        # айди после старта не пустое, это число, такой айди есть в бд как партнер, партнер не может пригласить сам себя
        if partner != '' and partner.isdigit() and find_partner:
            if partner != str(message.from_user.id):
                cursor.execute(f'INSERT OR REPLACE INTO ref_clients VALUES ("{partner}",{message.from_user.id},"free","","")')
                conn.commit()
            else:
                await bot.send_message(chat_id=message.from_user.id,
                            text=f"Вы не можете пригласить сами себя :3\n\nСкидка не будет учтена",
                            reply_markup=kb_free)

    await message.delete()
    cursor.close()


# Хендлер Описания
@dp.message_handler(Text(equals="Описание"))
async def descr_func(message: types.Message):
    _, cursor = db_connect()
    status = cursor.execute(f"SELECT status FROM users WHERE user_id='{message.from_user.id}'").fetchone()[0]
    if status != "block":
        await bot.send_message(chat_id=message.from_user.id,
                               text=DESCR, parse_mode="HTML")
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text="Вы присутствуете в черном списке. Доступ запрещен. Обратитесь в тех. поддержку.",
                               parse_mode="HTML")


# хендлер инфо
@dp.message_handler(Text(equals='Информация'))
async def info(message: types.Message):
    _, cursor = db_connect()
    if paid_validate(message.from_user.id):
        await message.answer(text="Выберите действие", parse_mode='html', reply_markup=kb_inform)

    elif trader_validate(message.from_user.id):

        #FIXME: такого уже нет, переделать на проверку из бд

        global stream_websockets
        if stream_websockets[f'stream_{message.from_user.id}']:
            kb = kb_trader2
        else:
            kb = kb_trader
        await message.answer(text=INFO, parse_mode='html', reply_markup=kb)
    else:
        kb = kb_free
        status = cursor.execute(f"SELECT status FROM users WHERE user_id='{message.from_user.id}'").fetchone()[0]
        if status != "block":
            await message.answer(text=INFO, parse_mode='html', reply_markup=kb)


# Хендлер Инструкции
@dp.message_handler(Text(equals="Инструкция"))
async def descr_func(message: types.Message):
    if paid_validate(message.from_user.id):
        await bot.send_message(chat_id=message.from_user.id,
                               text=INSTRUCT,
                               parse_mode="HTML",
                               reply_markup=kb_instruct2)
    else:
        _, cursor = db_connect()
        status = cursor.execute(f"SELECT status FROM users WHERE user_id='{message.from_user.id}'").fetchone()[0]
        if status != "block":
            await bot.send_message(chat_id=message.from_user.id,
                                   text=INSTRUCT,
                                   parse_mode="HTML",
                                   reply_markup=kb_instruct)


# хендлер вывода трейдеров
@dp.message_handler(Text(equals='Наши трейдеры'))
async def toptraders(message: types.Message):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    traders = cursor.execute('SELECT name FROM traders').fetchmany(100)
    res = ''
    print(traders)
    for i in range(0,len(traders)):
        res += f'• <b>{traders[i][0]}</b>\n'
        if traders[i][0] == None and i != 0:
            return
        elif i == 0 and traders[i][0] == None:
            await bot.send_message(chat_id=message.from_user.id,
                                   text = f'База данных трейдеров пуста')
            return
    await bot.send_message(chat_id=message.from_user.id,
                           text=f'Наши трейдеры: \n{res}',
                           parse_mode="HTML")


# Хендлер Покупки подписки
@dp.message_handler(Text(equals="Оформить подписку"))
async def buy(message: types.Message):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    a = cursor.execute(f'SELECT status FROM users WHERE user_id = {message.from_user.id};').fetchone()
    if a != None and a[0] == 'free':
        if os.getenv('PAYMENTS_TOKEN').split(":")[1] == "TEST":
            await bot.send_photo(message.chat.id,
                                photo='https://i.postimg.cc/zBynYjZq/photo-2023-06-18-16-59-44.jpg',
                                caption="Тестовый платеж",
                                reply_markup=paykb)
    else:
        if a == None:
            await bot.send_message(chat_id=message.from_user.id,
                               text='Мы не нашли вас в базе данных пользователей.\n Вы либо не нажали /start, либо вы трейдер))')
        elif a[0] == 'paid':
            await bot.send_message(chat_id=message.from_user.id,
                               text='Вы уже оплатили подписку')
        elif a[0] == 'block':
            await bot.send_message(chat_id=message.from_user.id,
                                text='ВЫ В ЧЕРНОМ СПИСКЕ. ОБРАТИТЕСЬ В ТЕХ. ПОДДЕРЖКУ.')
        else:
            await bot.send_message(chat_id=message.from_user.id,
                               text='Что-то пошло не так...')

    
@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    conn, cursor = db_connect()
    check_ref = cursor.execute(f'SELECT EXISTS(SELECT * FROM ref_clients WHERE client_id = "{pre_checkout_q["from"]["id"]}" LIMIT 1)').fetchone()[0]
    if check_ref:
        partner = cursor.execute(f'SELECT id FROM ref_clients WHERE client_id = "{pre_checkout_q["from"]["id"]}" LIMIT 1').fetchone()
        if partner != None:
            data = cursor.execute(f'SELECT sale, status FROM referral WHERE id = "{partner[0]}" LIMIT 1').fetchone()
            if data[1] == 'on':
                cursor.execute(f'UPDATE ref_clients SET for_bug = "{data[0]}"')
                conn.commit()
                cursor.close()
                await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)
                return
        await bot.send_message(chat_id=pre_checkout_q["from"]["id"],
                                text='Приносим свои извинения. Тот,кто вас пригласил был только что заблокирован.\n\n'+ \
                                'Деньги не были списаны.\nК сожалению, скидка от партнёра больше недействительна. Вы можете перейти по другой партнерской'+\
                                'ссылке,чтобы получить скидку',
                                reply_markup=kb_free)
    else:
        cursor.close()
        await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# Результат после оплаты
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successfull_payment(message: types.Message):
    print("Success")
    payment_info = message.successful_payment.to_python()
    tranzaktion = ""
    # Цены
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
    # Изменение статуса и количества подписанных
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    date_start = date.today()
    current_time = datetime.now().time()

    def add_months(sourcedate, months):
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month // 12
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year,month)[1])
        return date(year, month, day)
    
    with open('db/prices.csv',encoding='utf-8') as data:
        read_file = csv.reader(data,delimiter=';')
        for i in read_file:
            prices = list(map(int,i))

    total = message.successful_payment.total_amount // 100

    #Проверка тотал на скидку. Нужно для того, чтобы если человек купил со скидкой, а партнер уже в чс или не партнер
    # то наш клиент все таки получил подписку
    happy_discount = False
    if total not in prices:
        happy_discount = True

    #Проверка на рефералку
    check_ref = cursor.execute(f'SELECT count(*) FROM ref_clients WHERE client_id = "{message.from_user.id}" LIMIT 1').fetchone()[0]

        # Работа с рефералкой
    if check_ref or happy_discount:
        if not happy_discount:
            # Обновление статуса в ref_clients
            edit_status_ref(message.from_user.id, 'paid', cursor)

            # Запись первой оплаты по рефералке. Если это повторная оплата, то дата не изменится.
            # Мы храним только 1-ю дату т.к. на 22.08.2023 в ref_clinets у нас может быт только 1 строчка с клиентом,
            # а смотреть остальные даты покупок мы можем в purchase_history
            check_date = cursor.execute(f'SELECT date FROM ref_clients WHERE client_id = "{message.from_user.id}"').fetchone()[0]
            if check_date == "":
                time = datetime.now()
                cursor.execute(f'UPDATE ref_clients SET date = "{time}" WHERE client_id = "{message.from_user.id}"')

            partner = cursor.execute(f'SELECT id FROM ref_clients WHERE client_id = "{message.from_user.id}" LIMIT 1').fetchone()[0]

            # Достаем данные о скидке и профите с покупки
            sal = cursor.execute(f'SELECT sale, salary FROM referral WHERE \
                                    id = "{partner}" LIMIT 1').fetchone()

            # Определяем, на какой период была куплена подписка c рефералкой
            total = message.successful_payment.total_amount / (100 * (1 - sal[0]/100))
            print(total)

            # Добавление профита партнеру в бд
            profit = total * sal[1] / 100
            cursor.execute(f'UPDATE referral SET profit = profit + {profit} WHERE id = "{partner}"')

            # Добавляем клиента в копилку
            cursor.execute(f'UPDATE referral SET count_clinents = count_clinents + 1 WHERE id = "{partner}"')
        else:
            sale = cursor.execute(f'SELECT for_bug FROM ref_clients WHERE client_id = "{message.from_user.id}" LIMIT 1').fetchone()[0]
            total = message.successful_payment.total_amount / (100 * (1 - sale/100))
            cursor.execute(f'DELETE FROM ref_clients WHERE client_id = "{message.from_user.id}"')
            
    if total == prices[0]:
        date1 = "week"
        date_fininsh = date_start + timedelta(days=7)
    elif total == prices[1]:
        date1 = "month"
        days = calendar.monthrange(date_start.year, date_start.month)[1]
        date_fininsh = date_start + timedelta(days=days)
    elif total == prices[2]:
        date1 = "3_month"
        date_fininsh = add_months(date_start, 3)
    elif total == prices[3]:
        date1 = "6_month"
        date_fininsh = add_months(date_start, 6)
    elif total == prices[4]:
        date1 = "year"
        date_fininsh = str(add_months(date_start, 12))

    cursor.execute(f"""UPDATE users SET subscriptions = "{date1}" WHERE user_id = {message.from_user.id}""")
    cursor.execute(f"""INSERT INTO purchase_history VALUES ('{date_start}', '{current_time}', 
                   '{message.from_user.id}', '{date1}', '{message.successful_payment.total_amount / 100}', '{tranzaktion}')""")
    cursor.execute(f"""Update users set status = "paid", subscribe_start = "{date_start}", 
                       subscribe_finish = "{date_fininsh}", 
                       [transaction] = "{tranzaktion}" 
                       where user_id = {message.from_user.id};""")

    conn.commit()
    cursor.close()


# Хендлер Возращения в меню
@dp.message_handler(Text(equals="Назад"))
async def menu_func(message: types.Message):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT status, api_key FROM users WHERE user_id = ?", (message.from_user.id,))
    result = cursor.fetchone()
    if result is not None:
        if result[0] != "block":
            if result[0] == "free":
                kb = kb_free
            elif result[0] == "paid" and result[1] != "":
                kb = kb_reg
            elif result[0] == "paid" and result[1] == "":
                kb = kb_unreg

            await bot.send_message(chat_id=message.from_user.id,
                                   text="Вы вернулись в меню",
                                   parse_mode="HTML",
                                   reply_markup=kb)
        else:
            await bot.send_message(chat_id=message.from_user.id,
                                   text="Вы присутствуете в черном списке. Доступ запрещен. Обратитесь в тех. поддержку.",
                                   parse_mode="HTML")
    else:
        data = cursor.execute("SELECT api_key, status FROM traders WHERE trader_id = ?", (message.from_user.id,)).fetchone()
        if data[1] != "block":
            if data[0] is not None:
                kb = kb_reg
            else:
                kb = kb_unreg

            await bot.send_message(chat_id=message.from_user.id,
                                   text="Вы вернулись в меню",
                                   parse_mode="HTML",
                                   reply_markup=kb)
        else:
            await bot.send_message(chat_id=message.from_user.id,
                                   text="Вы присутствуете в черном списке. Доступ запрещен. Обратитесь в тех. поддержку.",
                                   parse_mode="HTML")


# Хендлер Предостережения
@dp.message_handler(Text(equals="❌Предостережения❌"))
async def predostr_func(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text=PREDOSTR,
                           parse_mode="HTML")


# Хендлер Пользование ботом
@dp.message_handler(Text(equals="Как создать API ключ?"))
async def instruct_func(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text='Видеоинструкция уже грузится. Пожалуйста, немного подождите...')
    await bot.send_video(chat_id=message.from_user.id,
                         video=open("imgs/instruct.mp4", "rb"),
                         caption="Подробная инструкция")
    

# Рефералки
@dp.message_handler(Text(equals='Партнёрская программа'))
async def ref(message: types.Message):
    conn, cursor = db_connect()
    # проверка на блэк лист
    a = cursor.execute(f'SELECT count(*) FROM black_list WHERE id = {message.from_user.id};').fetchone()[0]
    if a == 0:
        # проверка на сущестование записи в бд
        b = bool(cursor.execute(f'SELECT count(*) FROM referral WHERE id = "{message.from_user.id}"').fetchone()[0])

        if b:
            salary = int(cursor.execute(f'SELECT salary FROM referral WHERE id = {message.from_user.id}').fetchone()[0])
            sale = int(cursor.execute(f'SELECT sale FROM referral WHERE id = {message.from_user.id}').fetchone()[0])
            link = cursor.execute(f'SELECT link FROM referral WHERE id = {message.from_user.id}').fetchone()[0]
            profit = cursor.execute(f'SELECT profit FROM referral WHERE id = {message.from_user.id}').fetchone()[0]
            bank = "*не настроено*"
            ispartner = "on" == cursor.execute(f'SELECT status FROM referral WHERE id = "{message.from_user.id}"').fetchone()[0]

            if ispartner:
                await bot.send_photo(chat_id=message.from_user.id,
                                    photo='https://avatars.mds.yandex.net/i?id=409af83d0551ff3d1939e278fb3a0debe6f6883f-9291097-images-thumbs&n=13',
                                    caption=f'Партнёрская программа ProofReader\n\n\n'
                                        f'Ваша ссылка для партнёрской программы (Click! чтобы скопировать): \n<code><b>{link}</b></code>\n\n'
                                        f'По ней приведенные вами клиенты будут покупать подписку, а часть стоимости придет на ваш счет: \n<b>{bank}</b>\n\n'
                                        f'Ваша прибыль с каждой покупки (скидка не влияет на прибыль) = <b>{salary}%</b>\n\n'
                                        f'Для клиентов по вашей ссылке скидка <b>{sale}%</b>\n\n'
                                        f'Вы заработали с нами: <strong>{profit}₽</strong>',
                                    reply_markup=kb_ref,
                                    parse_mode='html')
            else:
                await bot.send_photo(chat_id=message.from_user.id,
                                    photo='https://avatars.mds.yandex.net/i?id=409af83d0551ff3d1939e278fb3a0debe6f6883f-9291097-images-thumbs&n=13',
                                    caption=f'Вы не являетесь нашим партнёром',
                                    reply_markup=kb_ref_np,
                                    parse_mode='html')
        else:
            await bot.send_message(chat_id=message.from_user.id,
                                   text="Напишите /start и попробуйте снова")
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text='Программа не доступна для пользователей в черном списке. Если вы хотите вывести ваши средства,\
                                 то напишите в Тех. Поддержку')
    cursor.close()