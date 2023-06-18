from aiogram import types

DESCR = """<b>Наш софт обеспечивает стабильный доход засчет работы профессиональных трейдеров на криптобирже Bybit.</b>

<b> - Как пользователь взаимодействует с выбранным трейдером?</b>
Наш бот получает ордера от профессионального трейдера, после чего с минимальной задержкой реализовывает их на вашем аккаунте.

<b> - С помощью чего мы гарантируем безопасность ваших API ключей?</b>
Все ключи до попадания в базу данных шифруются, что обеспечивает безопасность.
Каждую неделю ключ шифрования менятеся, из-за чего возможность его подобрать исчезает."""

INSTRUCT = """Мы подготовили для вас инструкцию, чтобы вы смогли пользоваться ботом легко и комфортно
<b>Шаг 1.</b> Создать API ключ на Bybit.
<u>Настоятельно рекомендуем прочитать "Предостережения</u>".
"""

PREDOSTR = """<b>•Ключи API, не привязанные к IP-адресам, действительны в течение трёх (3) месяцев. 
•Ключи с привязкой к IP-адресам действуют бессрочно. 
•После смены пароля ваш секретный ключ API выйдет из строя через 7 дней.
•В целях безопасности API-ключ будет отображен только 1 раз. 
•После закрытия окна API будет недоступен. 
•Сохраните ключ в безопасном месте. 
•В целях безопасности, пожалуйста, не передавайте свой ключ непроверенным сторонним контактам.</b>"""

PRICE1 = types.LabeledPrice(label="Подписка на неделю", amount=1000 * 100)
PRICE2 = types.LabeledPrice(label="Подписка на месяц", amount=10000 * 2)
PRICE3 = types.LabeledPrice(label="Подписка на 3 месяца", amount=10000 * 3)
PRICE4 = types.LabeledPrice(label="Подписка на 6 месяцев", amount=10000 * 4)
PRICE5 = types.LabeledPrice(label="Подписка на 1 год", amount=10000 * 7)