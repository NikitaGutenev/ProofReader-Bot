from handlers.A_head_of_handlers import *



@dp.callback_query_handler(lambda d: d.data[0] == 'D')
async def paid_callback(callback: types.CallbackQuery):
    callback.data = callback.data[1:]
    match callback.data:
        case 'edit_api':
            if paid_validate(callback.from_user.id):
                conn, cursor = db_connect()
                cursor.execute("SELECT status FROM users WHERE user_id = ?", (callback.from_user.id,))
                result = cursor.fetchone()
                if result[0] == "paid":
                    await bot.send_message(chat_id=callback.from_user.id,
                                        text="Введите ваш <b>api_key</b> и <b>api_secret</b> через пробел: ",
                                        parse_mode="HTML")
                    await EditApi.api.set()
                else:
                    await bot.send_message(chat_id=callback.from_user.id,
                                        text="Вы еще не оплатили подписку",
                                        parse_mode="HTML")
            else: 
                await bot.send_message(chat_id=callback.from_user.id,
                                text="Мы не предусмотрели данный запрос. Повторите попытку.")
                

@dp.message_handler(state=EditApi.api)
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
    except:
        await bot.send_message(message.chat.id, 'Api key или Api secret указаны неверно. Повторите попытку', reply_markup=kb_reg)
        return
    
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    cursor.execute(f"""UPDATE users SET api_secret = "{api_secret}", api_key = "{api_key}"
                            WHERE user_id = {message.from_user.id}""")
    conn.commit()
    cursor.close()
    await bot.send_message(message.chat.id, 'Ваши API изменены', reply_markup=kb_reg)