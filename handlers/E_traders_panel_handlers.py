from handlers.D_paid_function_handlers import *
from callbacks.trader_callbacks import *


class TempStream:
    def __init__(self, id, func):
        self.id = id
        self.func = func

    def handle_message(self, message):
        ord = message["data"]
        print(ord)
        if len(ord) == 3:
            value = next((ord.index(n) for n in ord if "orderStatus" in n and n["orderStatus"] == "Filled"), None)
            if ord[value]["takeProfit"] != "":
                text = f"""Монета: <b>{ord[value]["symbol"]}</b>
Тип покупки: <b>{ord[value]["side"]}</b> 
Количество: <b>{ord[value]["qty"]}</b>
Цена: <b>{ord[value]["cumExecValue"]} $</b>
TakeProfit: <b>{ord[value]["takeProfit"]} $</b>
StopLoss: <b>{ord[value]["stopLoss"]} $</b>"""
                conn, cursor = db_connect()
                cursor.execute(f"INSERT INTO orders (order_id, trade_pair, take_profit, stop_loss, trader_id, user_id,"
                               f" status, open_price, close_price, profit, qty) VALUES ('{message['id']}', "
                               f"'{ord[value]['symbol']}', '{ord[value]['takeProfit']}', '{ord[value]['stopLoss']}', "
                               f"'{self.id}', '', 'open', '{ord[value]['cumExecValue']}', '', '', '{ord[value]['qty']}');")
                conn.commit()
                cursor.close()
            else:
                price = next((n["cumExecValue"] for n in ord if "cumExecValue" in n and n["cumExecValue"] != "0"), None)
                conn, cursor = db_connect()
                data = cursor.execute(f"SELECT qty, open_price FROM orders WHERE trade_pair = '{ord[value]['symbol']}' AND trader_id = '{self.id}' AND status = 'open'").fetchone()
                profit = round(float(price) * float(data[0]) - float(data[0]) * float(data[1]), 5)
                cursor.execute(f'''UPDATE orders SET status = "closed",
                                profit = "{profit}", close_price = "{price}" WHERE trade_pair = "{ord[value]['symbol']}" AND 
                                trader_id = "{self.id}" AND status = "open"''')
                conn.commit()
                cursor.close()
                text = f"""Монета: <b>{ord[1]["symbol"]}</b>
Тип покупки: <b>{ord[value]["side"]}</b> 
Количество: <b>{ord[value]["qty"]}</b>
Цена: <b>{price} $</b>
Профит: <b>{profit} $</b>"""
            self.func(self.id)
            requests.get(f'https://api.telegram.org/bot{os.getenv("TG_TOKEN")}' + \
                               f'/sendMessage?chat_id={self.id}&text={text}&parse_mode=HTML')
        else:
            requests.get(f'https://api.telegram.org/bot{os.getenv("TG_TOKEN")}' + \
                               f'/sendMessage?chat_id={self.id}&text=Вы не установили StopLoss или TakeProfit. Сделка не высветится у пользователей')
        requests.get(f'https://api.telegram.org/bot{os.getenv("TG_TOKEN")}' + \
                            f'/sendMessage?chat_id={self.id}&text=Отслеживание OFF❌&reply_markup={kb_trader}')
        

def tracking(ws,tmpstream = None, mode = 'off'):
    if mode == 'off':
        ws.exit()
    elif mode == 'on' and isinstance(tmpstream, TempStream):
        ws.order_stream(callback=tmpstream.handle_message)
    else:
        raise Exception('Вы передали какую-то хуйню в функцию tracking')


async def go_stream(id):
    conn, cursor = db_connect()
    api_key, api_secret = cursor.execute(f'SELECT api_key,api_secret FROM traders WHERE trader_id = {id}').fetchall()[0]

    ws = WebSocket(
    testnet=False,
    channel_type="private",
    api_key=decrypt_api(api_key),
    api_secret=decrypt_api(api_secret))

    tmp = TempStream(id, stop_stream)
    tracking(ws, tmp, 'on')
    global stream_websockets
    stream_websockets[f'stream_{id}'] = (ws, tmp)

    await bot.send_message(chat_id=id,
                           text='Отслеживание ON✅',
                           reply_markup=kb_trader2)
    

def stop_stream(id):
    global stream_websockets
    try:
        ws = stream_websockets[f'stream_{id}'][0]
    except:
        return False
    tracking(ws)
    stream_websockets.pop(f'stream_{id}')
    return True


@dp.message_handler(Text(equals='Ключи'))
async def keys(message: types.Message):
    if trader_validate(message.from_user.id):
        await bot.send_message(chat_id=message.from_user.id,
                               text="Выберите действие",
                               reply_markup=kb_keys)
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text="Мы не предусмотрели данный запрос. Повторите попытку.")


@dp.message_handler(Text(equals='Вернуться'))
async def back(message: types.Message):
    if trader_validate(message.from_user.id):
        global stream_websockets
        if f'stream_{message.from_user.id}' in stream_websockets:
            await bot.send_message(chat_id=message.from_user.id,
                                text="Вы вернулись в меню",
                                reply_markup=kb_trader2)
        else:
            await bot.send_message(chat_id=message.from_user.id,
                                text="Вы вернулись в меню",
                                reply_markup=kb_trader)
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text="Мы не предусмотрели данный запрос. Повторите попытку.")


@dp.message_handler(Text(equals='Создать ключ'))
async def new_key(message: types.Message):
    if trader_validate(message.from_user.id):
        letters = string.ascii_lowercase
        key = ''.join(random.choice(letters) for i in range(8))

        with open('cache/keys.txt', 'w') as file:
            file.write(key)

        conn, cursor = db_connect()
        cursor.execute(f"INSERT INTO trader_keys (trader_id, key) VALUES ('{message.from_user.id}', '{key}');")
        conn.commit()
        cursor.close()

        await bot.send_message(chat_id=message.from_user.id,
                               text="Выберите количество активаций.",
                               reply_markup=ikb_quantity)
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text="Мы не предусмотрели данный запрос. Повторите попытку.")


@dp.message_handler(Text(equals='Удалить ключ'))
async def new_key(message: types.Message):
    if trader_validate(message.from_user.id):
        await bot.send_message(chat_id=message.from_user.id,
                               text="Введите ключ, который необходимо удалить")
        await Key_Delete.key.set()
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text="Мы не предусмотрели данный запрос. Повторите попытку.")


@dp.message_handler(Text(equals='Вывод всех ключей'))
async def view_keys(message: types.Message):
    if trader_validate(message.from_user.id):
        conn, cursor = db_connect()
        text = "🗝 <b>КЛЮЧ</b> | <em>ДАТА</em> | <u>КОЛ-ВО АКТИВАЦИЙ</u> \n\n"
        data = cursor.execute(
            f"SELECT key, duration, quantity, quantity_tek FROM trader_keys WHERE trader_id = {message.from_user.id}").fetchall()
        for obj in data:
            text += f"<b>{data.index(obj) + 1}. {obj[0]}</b> | <em>{obj[1]}</em> | <u>{obj[3]}/{obj[2]}</u>\n"
        await bot.send_message(chat_id=message.from_user.id,
                               text=text,
                               parse_mode="HTML")
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text="Мы не предусмотрели данный запрос. Повторите попытку.")


@dp.message_handler(Text(equals='Статистика Профиля'))
async def prof_stat(message: types.Message):
    if trader_validate(message.from_user.id):
        await bot.send_video(chat_id=message.from_user.id,
                             video='https://c.mql5.com/1/78/open-uri20150119-12-2b4861__1.gif',
                             caption='Статистика Профиля',
                             reply_markup=ikb_trader_stat)
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text="Мы не предусмотрели данный запрос. Повторите попытку.")


@dp.message_handler(Text(equals='Помощь'))
async def trader_help(message: types.Message):
    if trader_validate(message.from_user.id):
        await bot.send_message(chat_id=message.from_user.id,
                               text=TRADER_HELP,
                               parse_mode='html',
                               reply_markup=kb_trader)
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text="Мы не предусмотрели данный запрос. Повторите попытку.")


@dp.message_handler(Text(equals='Вкл отслеживание'))
async def trader_help(message: types.Message):
    if trader_validate(message.from_user.id):
        await go_stream(message.from_user.id)
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text="Мы не предусмотрели данный запрос. Повторите попытку.")


@dp.message_handler(Text(equals='Выкл отслеживание'))
async def trader_help(message: types.Message):
    if trader_validate(message.from_user.id):
        if stop_stream(message.from_user.id):
            await bot.send_message(chat_id=message.from_user.id,
                           text='Отслеживание OFF❌',
                           reply_markup=kb_trader)
        else:
            await bot.send_message(chat_id=message.from_user.id,
                           text='Отслеживание и так выключено',
                           reply_markup=kb_trader)
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text="Мы не предусмотрели данный запрос. Повторите попытку.")
    