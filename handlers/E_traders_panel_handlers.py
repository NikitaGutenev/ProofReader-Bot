from handlers.D_paid_function_handlers import *
from callbacks.trader_callbacks import *


class TempStream:
    def __init__(self, id, func):
        self.id = id
        self.func = func

    def create_order_in_object(self, ord, value, mode = False):
            conn, cursor = db_connect()
            print(f"СОЗДАВАЕМЫЙ ОРДЕР: \n {ord} \n")
            text = ""
            if ord[0]["orderType"] == "Market":
                if ord[0]['category'] == "linear":
                    if len(ord) == 3:
                        tp = next((n for n in ord if n['stopOrderType'] == 'TakeProfit'), None)
                        sl = next((n for n in ord if n['stopOrderType'] == 'StopLoss'), None)

                        if ord[value]["takeProfit"] != "":
                            text = f"""РЫНОЧНАЯ ЗАЯВКА
                            
Категория: <b>Дериватив</b>                        
Монета: <b>{ord[value]["symbol"]}</b>
Тип покупки: <b>{ord[value]["side"]}</b>
Количество: <b>{ord[value]["qty"]}</b>
Цена: <b>{ord[value]["avgPrice"]} $</b>
TakeProfit: <b>{ord[value]["takeProfit"]} $</b>
StopLoss: <b>{ord[value]["stopLoss"]} $</b>"""

                        if not mode:
                            current_date = datetime.now().date()
                            current_date = current_date.strftime('%Y-%m-%d')
                            cursor.execute(f"INSERT INTO orders (order_id, tp_order_id, sl_order_id, trade_pair, take_profit, stop_loss, trader_id, user_id,"
                                    f" status, open_price, close_price, close_order_id, profit, qty, date_1, type, type_2) VALUES ('{ord[value]['orderId']}', "
                                    f"'{tp['orderId']}', '{sl['orderId']}' ,"
                                    f"'{ord[value]['symbol']}', '{ord[value]['takeProfit']}', '{ord[value]['stopLoss']}', "
                                    f"'{self.id}', '', 'open', '{ord[value]['avgPrice']}', '', '', '', '{ord[value]['cumExecQty']}', '{current_date}', 'Market', 'derivatives');")
                            conn.commit()
                        else:
                            current_date = datetime.now().date()
                            cursor.execute(f"UPDATE orders SET take_profit = {ord[value]['takeProfit']}, stop_loss = {ord[value]['stopLoss']}, order_id = '{ord[value]['orderId']}', qty = qty + {ord[value]['cumExecQty']}, date_1 = '{current_date}' WHERE trader_id = {self.id} AND trade_pair = '{ord[value]['symbol']}' AND status = 'open'")
                            conn.commit()

                    else:
                        requests.get(f'https://api.telegram.org/bot{os.getenv("TG_TOKEN")}' + \
                                    f'/sendMessage?chat_id={self.id}&text=Вы не установили StopLoss или TakeProfit. Сделка не высветится у пользователей')
                if ord[0]['category'] == 'spot' and ord[0]['orderType'] != 'Filled':
                    print(ord[0]['orderType'])
                    text = f"""РЫНОЧНАЯ ЗАЯВКА

Категория: <b>Спот</b>                       
Монета: <b>{ord[value]["symbol"]}</b>
Тип покупки: <b>{ord[value]["side"]}</b>
Количество монет: <b>{round(float(ord[value]["cumExecQty"]), 2)}</b>"""

                    if not mode:
                        current_date = datetime.now().date()
                        current_date = current_date.strftime('%Y-%m-%d')
                        cursor.execute(f"INSERT INTO orders (order_id, tp_order_id, sl_order_id, trade_pair, take_profit, stop_loss, trader_id, user_id,"
                                f" status, open_price, close_price, close_order_id, profit, qty, date_1, type, type_2, triggeredPrice) VALUES ('{ord[value]['orderId']}', "
                                f"'', '' ,"
                                f"'{ord[value]['symbol']}', '', '', "
                                f"'{self.id}', '', 'open', '{ord[value]['avgPrice']}', '', '', '', '{ord[value]['cumExecQty']}', '{current_date}', 'Market', 'spot', '{ord[value]['triggerPrice']}');")
                        conn.commit()



            elif ord[0]["orderType"] == "Limit":
                if ord[0]['category'] == 'spot' and ord[0]['orderType'] != 'Filled':
                    text = f"""ЛИМИТНАЯ ЗАЯВКА
                    
Категория: <b>Спот</b>
Монета: <b>{ord[value]["symbol"]}</b>
Тип покупки: <b>{ord[value]["side"]}</b>
Колиечество монет: <b>{round(float(ord[value]["cumExecQty"]), 2)}</b>
Цена срабатывания заявки: <b>{ord[value]["price"]}</b>"""
                    if not mode:
                        current_date = datetime.now().date()
                        current_date = current_date.strftime('%Y-%m-%d')
                        cursor.execute(f"INSERT or REPLACE INTO orders (order_id, tp_order_id, sl_order_id, trade_pair, take_profit, stop_loss, trader_id, user_id,"
                                f" status, open_price, close_price, close_order_id, profit, qty, date_1, type, type_2, triggeredPrice) VALUES ('{ord[value]['orderId']}', "
                                f"'', '' ,"
                                f"'{ord[value]['symbol']}', '', '', "
                                f"'{self.id}', '', 'new', '{ord[value]['price']}', '', '', '', '{ord[value]['cumExecQty']}', '{current_date}', 'Limit', 'spot', '{ord[value]['triggerPrice']}');")
                        conn.commit()

                if ord[0]["category"] == "linear":
                    if ord[0]["takeProfit"] != "" and ord[0]["stopLoss"] != "":

                        tmp = cursor.execute(f'SELECT count(*) FROM orders WHERE trader_id = {self.id} and \
                                         (status = "open" or status = "new") and trade_pair = "{ord[0]["symbol"]}" and type = "Limit"').fetchone()[0]
                        if tmp != 0:
                            current_date = datetime.now().date()

                            qty = float(cursor.execute(f'SELECT qty FROM orders WHERE trader_id = {self.id} and trade_pair = "{ord[0]["symbol"]}" \
                                             and (status = "open" or status = "new") and type = "Limit"').fetchone()[0]) + float(ord[0]['cumExecQty'])
                        
                            try:
                                cursor.execute(
                                f"INSERT INTO orders (order_id, tp_order_id, sl_order_id, trade_pair, take_profit, stop_loss, trader_id, user_id,"
                                f" status, open_price, close_price, close_order_id, profit, qty, date_1, type) VALUES ('{ord[0]['orderId']}', "
                                f"'', '' ,"
                                f"'{ord[0]['symbol']}', '{ord[0]['takeProfit']}', '{ord[0]['stopLoss']}', "
                                f"'{self.id}', '', 'new', '{ord[0]['price']}', '', '', '', '{ord[0]['cumExecQty']}', '{current_date}', 'Limit', 'derivatives');")
                            except:
                                tp = next((n for n in ord if n['stopOrderType'] == 'TakeProfit'), None)
                                sl = next((n for n in ord if n['stopOrderType'] == 'StopLoss'), None)
                                cursor.execute(f'UPDATE orders SET tp_order_id = "{tp["orderId"]}", sl_order_id = "{sl["orderId"]}",\
                                           status = "open"')
                            conn.commit()
                            cursor.close()
                            text = f"""ЛИМИТНАЯ ЗАЯВКА

Категория: <b>Дериватив</b>                  
Монета: <b>{ord[0]["symbol"]}</b>
Тип покупки: <b>{ord[0]["side"]}</b>
Количество (всего куплено): <b>{qty}</b>
Цена срабатывания заявки: <b>{ord[0]["price"]} $</b>
TakeProfit: <b>{ord[0]["takeProfit"]} $</b>
StopLoss: <b>{ord[0]["stopLoss"]} $</b>"""
                        
                        else:
                            text = f"""ЛИМИТНАЯ ЗАЯВКА
                        
Категория: <b>Дериватив</b>
Монета: <b>{ord[0]["symbol"]}</b>
Тип покупки: <b>{ord[0]["side"]}</b>
Количество: <b>{ord[0]["cumExecQty"]}</b>
Цена срабатывания заявки: <b>{ord[0]["price"]} $</b>
TakeProfit: <b>{ord[0]["takeProfit"]} $</b>
StopLoss: <b>{ord[0]["stopLoss"]} $</b>"""
                            if not mode:
                                current_date = datetime.now().date()
                                current_date = current_date.strftime('%Y-%m-%d')
                                cursor.execute(
                                f"INSERT INTO orders (order_id, tp_order_id, sl_order_id, trade_pair, take_profit, stop_loss, trader_id, user_id,"
                                f" status, open_price, close_price, close_order_id, profit, qty, date_1, type) VALUES ('{ord[0]['orderId']}', "
                                f"'', '' ,"
                                f"'{ord[0]['symbol']}', '{ord[0]['takeProfit']}', '{ord[0]['stopLoss']}', "
                                f"'{self.id}', '', 'new', '{ord[0]['price']}', '', '', '', '{ord[0]['cumExecQty']}', '{current_date}', 'Limit');")
                                conn.commit()
                                conn.close()
                    else:
                        requests.get(f'https://api.telegram.org/bot{os.getenv("TG_TOKEN")}' + \
                                 f'/sendMessage?chat_id={self.id}&text=Вы не установили StopLoss или TakeProfit. Сделка не высветится у к пользователей.')
                        return
            requests.get(f'https://api.telegram.org/bot{os.getenv("TG_TOKEN")}' + \
                         f'/sendMessage?chat_id={self.id}&text={text}&parse_mode=HTML')


    def handle_message(self, message):
        conn, cursor = db_connect()
        api_key, api_secret, webstream = cursor.execute(f'SELECT api_key,api_secret, webstream FROM traders WHERE trader_id = {self.id}').fetchall()[0]
        flag = True
        session = HTTP(
            testnet=False,
            api_key=decrypt_api(api_key),
            api_secret=decrypt_api(api_secret),
        )
        ord = message["data"]
        print(ord)
        # Индекс элемента списка, заполненного ордера
        value = next((ord.index(n) for n in ord if "orderStatus" in n and n["orderStatus"] == "Filled"), None)
        self.value = value
        self.ord = ord

        # Поиск открытых ордеров (сработанных)
        existence_validate_actual = bool(cursor.execute(f"SELECT count(*) FROM orders WHERE trader_id = '{self.id}' \
                                                        AND trade_pair = '{ord[0]['symbol']}' AND status = 'open'").fetchone()[0])
        
        # Для частичного закрытия
        existence_validate_actual_spot = cursor.execute(f"SELECT count(*) FROM orders WHERE trader_id = '{self.id}' \
                                                        AND trade_pair = '{ord[0]['symbol']}' AND status = 'open' AND qty != '0'").fetchall()[0][0]
        
        # Поиск открытых ордеров (несработанных)
        existence_validate_limit = bool(cursor.execute(f"SELECT count(*) FROM orders WHERE trader_id = '{self.id}' \
                                                       AND trade_pair = '{ord[0]['symbol']}' AND status = 'new'").fetchone()[0])
        
        # Поиск открытых рыночных ордеров (нужно для фильтрации лишних приходящих ордеров в случае закрытия по стоп ордеру)
        find_opens_market = bool(cursor.execute(f'SELECT count(*) FROM orders WHERE trader_id = "{self.id}" AND trade_pair = "{ord[0]["symbol"]}" \
                                        AND status = "open" AND type = "Market"').fetchone()[0])
        # Если есть сам ордер
        if self.value is not None or self.value == None and ord[0]['category'] == 'spot':
            if ord[0]['category'] == 'spot':
                value = 0
            # Если нет открытого ордера этой монеты или этот ордер лимитный и есть новая лимитка -> отслеживание включено
            if (not existence_validate_actual or (existence_validate_limit and ord[0]["orderType"] == "Limit")) or ord[0]['category'] == 'spot' and webstream == 1:
                self.create_order_in_object(ord, value)

            #Если есть открытый ордер этой монеты в споте
            if (existence_validate_actual or existence_validate_limit):
                if ord[0]["orderType"] == "Limit" and ord[0]["orderStatus"] == "Cancelled" or ord[0]["orderType"] == "Market" and ord[0]["orderStatus"] == "Cancelled":
                    cursor.execute(f"UPDATE orders SET status = 'cancel' WHERE order_id = '{ord[0]['orderId']}'")
                    conn.commit()
                    conn.close()
                    text = f'''Вы отменили ордер на покупку 
    
Монета: <b>{ord[0]["symbol"]}</b>
ID ордера: <b>{ord[0]["orderId"]}</b>
Количество: <b>{ord[0]["qty"]}</b>'''

                    requests.get(f'https://api.telegram.org/bot{os.getenv("TG_TOKEN")}' + \
                                 f'/sendMessage?chat_id={self.id}&text={text}&parse_mode=HTML')
                    return

                # Есть ли лимитная заявка на эту монету
                isexist = cursor.execute(
                    f"SELECT order_id FROM orders WHERE status = 'new' AND type = 'Limit' \
                    AND trader_id = '{self.id}' AND trade_pair = '{ord[0]['symbol']}'").fetchall()

                # Если есть рыночные ордера
                if existence_validate_actual:
                    skip_condition = False
                    stop_orders = cursor.execute(f"SELECT tp_order_id, sl_order_id FROM orders WHERE trader_id = '{self.id}' \
                                                 AND trade_pair = '{ord[0]['symbol']}' AND status = 'open' AND type = 'Market'").fetchone()

                    if len(ord) == 2 or ord[0]['category'] == 'spot': # условие для определения и фильтрации не нужных исходящих ордеров.
                        # Было принято такое решение т.к. закрытие по стопам определяется не путем принятия исходящих ордеров, а путем получение их статуса по их id.
                        # При срабатывании стопа, мы получаем сначала один ордер со статусом triggered, на котором в большинстве случаев стоп ордера уже заполнились,
                        # Затем, мы получим два ордера, это будут стоп лосс и тейк профит, проверка идет заново и это вызывает посторный вызов ф-ций, которые не должны
                        # вызываться. Но таким образом, на случай если на момент получения ордера со статусом triggered, наш стоп ордер еще
                        # не был заполнен (вероятно, он был большой), мы закроем и оповестим людей при ФАКТИЧЕСКОМ заполнении (т.к. получим два ордера, которые нам и
                        # говорят о том, что один из стопов был заполнен,а второй деактивен)
                        so_status = ord[value]["orderStatus"]
                        skip_condition = True
                    if ord[0]['category'] != 'spot' and len(ord) == 1:
                        tp_status = session.get_order_history(
                            category="linear",
                            orderId=stop_orders[0])['result']['list'][0]['orderStatus']
                        sl_status = session.get_order_history(
                            category="linear",
                            orderId=stop_orders[1])['result']['list'][0]['orderStatus']

                    # Выдача статусов
                    if not skip_condition:
                        if tp_status == 'Filled' or sl_status == 'Filled':
                            so_status = 'Filled'
                        elif tp_status == 'Deactivated' or sl_status == 'Deactivated':
                            so_status = 'Deactivated'
                        elif tp_status == 'Untriggered' and sl_status == 'Untriggered':
                            so_status = 'Untriggered'

                    # Если ордер продан
                    if so_status == 'Deactivated' or (so_status == "Filled" and ord[0]['category'] == 'spot' and ord[0]['side'] == 'Sell'):
                        if so_status == "Deactivated":
                            close_order = session.get_closed_pnl(
                                category="linear",
                                limit=1,
                            )
                            exit_price = close_order["result"]["list"][0]["avgExitPrice"]
                            profit = str(round(float(close_order["result"]["list"][0]["closedPnl"]), 2))
                            order_id = close_order["result"]["list"][0]["orderId"]
                            cursor.execute(f'''UPDATE orders SET status = "closed",
                                        profit = "{profit}", close_price = "{exit_price}", close_order_id = "{order_id}" WHERE trade_pair = "{ord[0]['symbol']}" AND 
                                        trader_id = "{self.id}" AND status = "open" AND type = "Market" ''')
                        elif so_status == "Filled" and ord[0]['category'] == 'spot' and ord[0]['side'] == 'Sell':
                            if ord[0]["orderType"] == 'Market':
                                ordtype = "Market"
                            elif ord[0]["orderType"] == 'Limit':
                                ordtype = "Limit"
                            if existence_validate_actual_spot == 1:
                                position = "ПОЗИЦИЯ ЗАКРЫТА"
                                exit_price = float(ord[0]["avgPrice"])
                                order_id = ord[0]["orderId"]
                                

                                open_price = cursor.execute(f'''SELECT open_price FROM orders WHERE trade_pair = "{ord[0]['symbol']}" AND 
                                                        trader_id = "{self.id}" AND status = "open" AND type = "{ordtype}"''').fetchone()
                                profit = exit_price * float(ord[0]["cumExecQty"]) - float(open_price[0][0]) * float(ord[0]["cumExecQty"]) - float(ord[0]["cumExecFee"]) * exit_price
                                cursor.execute(f'''UPDATE orders SET status = "closed",
                                        profit = "{profit}", close_price = "{exit_price}", close_order_id = "{order_id}" WHERE trade_pair = "{ord[0]['symbol']}" AND 
                                        trader_id = "{self.id}" AND status = "open" AND type = "{ordtype}" ''')
                               
                                        
                            else:
                                position = "ПОЗИЦИЯ ЧАСТИЧНО ЗАКРЫТА"

                                qty_all = cursor.execute(f'''SELECT qty, order_id FROM orders WHERE trade_pair = "{ord[0]['symbol']}" AND 
                                                        trader_id = "{self.id}" AND status = "open"''').fetchall()
                                qty_summ = 0
                                index = 0
                                open_price = 0
                                profit = 0
                                for i in qty_all:
                                    qty_summ += i[0]
                                    exit_price = float(ord[0]["avgPrice"])
                                    open_price = cursor.execute(f'''SELECT open_price FROM orders WHERE trade_pair = "{ord[0]['symbol']}" AND 
                                                        trader_id = "{self.id}" AND status = "open"''').fetchall()
                                    profit += (exit_price * float(ord[0]["cumExecQty"]) - float(open_price[0][0]) * float(ord[0]["cumExecQty"]) - float(ord[0]["cumExecFee"]) * exit_price)
                                if qty_summ >= float(ord[value]["qty"]):
                                    qty_summ -= float(ord[value]["qty"])
                                    for i in qty_all:
                                        order_id = ord[0]["orderId"]
                                        order_id_1 = i[1]
                                        cursor.execute(f'''UPDATE orders SET status = "closed",
                                            profit = "{profit}", close_price = "{exit_price}", close_order_id = "{order_id}" WHERE trade_pair = "{ord[0]['symbol']}" AND 
                                            trader_id = "{self.id}" AND status = "open" AND order_id = "{order_id_1}"''')
                                        index += 1
                                if qty_summ != 0:
                                    print(index)
                                    order_id = qty_all[index - 1][1]
                                    cursor.execute(f'''UPDATE orders set qty = '{qty_summ}', status = "open", profit = "", close_price = "", close_order_id = ""
                                                    WHERE order_id = "{order_id}"''')
                                    if ordtype == 'Limit':
                                        cursor.execute(f'''UPDATE orders SET status = "closed" WHERE order_id = "{ord[0]["orderId"]}" AND type = "Limit" ''')


                                    
                                    
                            flag = False
                            conn.commit()
                            if ord[0]["category"] == "spot":
                                cat = "Спот"
                            else:
                                cat = "Дериватив"
                            text = f'''{position}

Категория: <b>{cat}</b>
Монета: <b>{ord[value]["symbol"]}</b>
Тип покупки: <b>{ord[value]["side"]}</b>
Количество: <b>{ord[value]["qty"]}</b>
Цена: <b>{exit_price} $</b>
Профит: <b>{round(profit, 2)} $</b>'''

                            requests.get(f'https://api.telegram.org/bot{os.getenv("TG_TOKEN")}' + \
                                            f'/sendMessage?chat_id={self.id}&text={text}&parse_mode=HTML')

                    # Если ордер работает
                    elif so_status == 'Untriggered':
                        requests.get(f'https://api.telegram.org/bot{os.getenv("TG_TOKEN")}' + \
                                        f'/sendMessage?chat_id={self.id}&text=У ваших подписчиков в данный момент есть открытый вами ордер' + \
                                          f'на данной валютной паре. Вероятно, Вы хотите докупить и/или изменить стоп-ордера. Вы хотите отправить им ' + \
                                            f'ТОЛЬКО ЧТО СОЗДАННЫЙ ВАМИ ордер, или не будете?&reply_markup={kb_order}')
                        cursor.close()
                        self.func(self.id)
                        return

                    # Обновление данных при закрытии по стоп-ордеру
                    elif so_status == 'Filled' and ord[0]["category"] != 'spot':
                        if skip_condition:
                            # создаем массив с одним элементом -> исполненным ордером. Это предотвратит поломку кода ниже
                            tmp = []
                            tmp.append(ord[value])
                            ord = tmp.copy()

                        if so_status == tp_status:
                            who = stop_orders[0]
                            text = f'Сработал Take-Profit на монете <b>{ord[0]["symbol"]}</b>. \n'
                            qty = session.get_order_history(
                                                            category="linear",
                                                            orderId=stop_orders[0])['result']['list'][0]['qty']
                        else:
                            who = stop_orders[1]
                            text = f'Сработал Stop-Loss на монете <b>{ord[0]["symbol"]}</b>. \n\n'
                            qty = session.get_order_history(
                                                            category="linear",
                                                            orderId=stop_orders[1])['result']['list'][0]['qty']

                        price = next((n['triggerPrice'] for n in ord if "triggerPrice" in n and n["triggerPrice"] != "0"), None)
                        data = cursor.execute(f"SELECT qty, open_price FROM orders WHERE trade_pair = '{ord[0]['symbol']}' AND trader_id = '{self.id}' \
                                              AND status = 'open' AND type = 'Market' ").fetchone()
                        print(data)
                        profit = round(float(price) * float(data[0]) - float(data[0]) * float(data[1]), 5)
                        cursor.execute(f'''UPDATE orders SET status = "closed",
                                        profit = "{profit}", close_price = "{price}", close_order_id = "{who}" WHERE trade_pair = "{ord[0]['symbol']}" AND 
                                        trader_id = "{self.id}" AND status = "open" AND type = "Market" ''')
                        conn.commit()
                        text += f'''ID стоп ордера: <b>{who}</b>
Профит/убыток: <b>{profit}</b>
Цена закрытия: <b>{price}</b>
Кол-во монет: <b>{qty}</b>'''
                        print('Стоп-ордер успешно сработал')
                        requests.get(f'https://api.telegram.org/bot{os.getenv("TG_TOKEN")}' + \
                                        f'/sendMessage?chat_id={self.id}&text={text}&reply_markup={kb_trader}&parse_mode=HTML')
                        return

                # Если лимитные
                else:
                    for item in isexist:
                        if item[0] == int(ord[0]['orderId']):
                            text = f"Ордер на покупку <b>{ord[0]['symbol']}</b> стал активным. Данная монета была также куплена у всех ваших подписчиков."
                            if ord[0]["category"] != "spot":
                                tp = next((n for n in ord if n['stopOrderType'] == 'TakeProfit'), None)
                                sl = next((n for n in ord if n['stopOrderType'] == 'StopLoss'), None)
                                if tp != sl != None:
                                    cursor.execute(f'''UPDATE orders SET status = "open", tp_order_id = "{tp['orderId']}", sl_order_id = "{sl['orderId']}" WHERE trade_pair = "{ord[0]['symbol']}" AND 
                                                                        trader_id = "{self.id}" AND status = "new" AND type = "Limit" ''')

                            else:
                                cursor.execute(
                                    f'''UPDATE orders SET status = "open", tp_order_id = "none", sl_order_id = "none" WHERE trade_pair = "{ord[0]['symbol']}" AND 
                                                                                                        trader_id = "{self.id}" AND status = "new" AND type = "Limit" ''')
                            conn.commit()
                            cursor.close()
                            requests.get(f'https://api.telegram.org/bot{os.getenv("TG_TOKEN")}' + \
                                         f'/sendMessage?chat_id={self.id}&text={text}&parse_mode=HTML')
                            return

            elif not existence_validate_actual and webstream == 0:
                flag = False
                if ord[0]["orderStatus"] != "Cancelled" and len(ord) != 2:
                    requests.get(f'https://api.telegram.org/bot{os.getenv("TG_TOKEN")}' + \
                                 f'/sendMessage?chat_id={self.id}&text=Ордер не был отправлен вашим подписчикам')

            cursor.close()
            self.func(self.id)

            if flag:
                requests.get(f'https://api.telegram.org/bot{os.getenv("TG_TOKEN")}' + \
                             f'/sendMessage?chat_id={self.id}&text=Отслеживание OFF❌&reply_markup={kb_trader}')
                return
                

            

        # Если только тп и/или сл
        else:
            for obj in ord:
                type = obj["stopOrderType"]
                if type == "StopLoss":
                    cursor.execute(f"UPDATE orders SET stop_loss = '{obj['triggerPrice']}' WHERE sl_order_id = '{obj['orderId']}' and status != 'closed'")
                elif type == "TakeProfit":
                    cursor.execute(f"UPDATE orders SET take_profit = '{obj['triggerPrice']}' WHERE tp_order_Id = '{obj['orderId']}' and status != 'closed'")
            conn.commit()
            cursor.close()
            requests.get(f'https://api.telegram.org/bot{os.getenv("TG_TOKEN")}' + \
                         f'/sendMessage?chat_id={self.id}&text=Стоп ордера были успешно обновлены✅')


def tracking(id, conn, cursor, mode='off'):
    if mode == 'off':
        cursor.execute(f"UPDATE traders SET webstream = '0' WHERE trader_id = {id};")
    elif mode == 'on':
        cursor.execute(f"UPDATE traders SET webstream = '1' WHERE trader_id = {id};")
    conn.commit()
    cursor.close()


async def go_stream(id):
    conn, cursor = db_connect()
    api_key, api_secret = cursor.execute(f'SELECT api_key,api_secret FROM traders WHERE trader_id = {id}').fetchall()[0]
    ws = WebSocket(
    testnet=False,
    channel_type="private",
    api_key=decrypt_api(api_key),
    api_secret=decrypt_api(api_secret))

    tmp = TempStream(id, stop_stream)
    tracking(id, conn, cursor, 'off')
    ws.order_stream(callback=tmp.handle_message)
    global stream_websockets
    stream_websockets[f'stream_{id}'] = (ws, tmp)

    
def stop_stream(id):
    conn, cursor = db_connect()
    tracking(id, conn, cursor)
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
        _, cursor = db_connect()
        a = cursor.execute(f'SELECT webstream FROM traders WHERE trader_id = "{message.from_user.id}"').fetchone()[0]
        if a == 1:
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
async def del_key(message: types.Message):
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
        kb_trader = true_kb(message.from_user.id)
        await bot.send_message(chat_id=message.from_user.id,
                               text=TRADER_HELP,
                               parse_mode='html',
                               reply_markup=kb_trader)
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text="Мы не предусмотрели данный запрос. Повторите попытку.")


@dp.message_handler(Text(equals='Вкл отслеживание'))
async def trader_on(message: types.Message):
    if trader_validate(message.from_user.id):
        if f'stream_{message.from_user.id}' not in stream_websockets:
            await go_stream(message.from_user.id)
        conn, cursor = db_connect()
        tracking(message.from_user.id, conn, cursor, mode="on")
        await bot.send_message(chat_id=message.from_user.id,
                               text="Отслеживание ON✅",
                               reply_markup=kb_trader2)
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text="Мы не предусмотрели данный запрос. Повторите попытку.")


@dp.message_handler(Text(equals='Выкл отслеживание'))
async def trader_off(message: types.Message):
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