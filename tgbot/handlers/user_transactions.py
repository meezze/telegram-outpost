# -*- coding: utf-8 -*-
import requests
import json
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from tgbot.keyboards.inline_user import refill_bill_finl, refill_choice_finl
from tgbot.loader import dp
from tgbot.services.api_sqlite import update_userx, get_refillx, add_refillx, get_userx
from tgbot.utils.const_functions import get_date, get_unix
from tgbot.utils.misc_functions import send_admins

min_input_mdl = 5  # Минимальная сумма пополнения в молдавских леях

PAYPAL_CLIENT_ID = "your_paypal_client_id"
PAYPAL_SECRET = "your_paypal_secret"

# Создание платежа через PayPal с валютой MDL
def create_paypal_payment(amount_mdl):
    url = "https://api-m.sandbox.paypal.com/v2/checkout/orders"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_paypal_access_token()}",
    }

    data = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": "MDL",
                    "value": str(amount_mdl)
                }
            }
        ],
        "application_context": {
            "return_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel"
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 201:
        return response.json()
    else:
        print(f"Error creating PayPal payment: {response.text}")
        return None

# Получение токена доступа PayPal
def get_paypal_access_token():
    url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"

    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US",
    }

    auth = (PAYPAL_CLIENT_ID, PAYPAL_SECRET)

    data = {
        "grant_type": "client_credentials",
    }

    response = requests.post(url, headers=headers, auth=auth, data=data)

    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Error getting PayPal access token: {response.text}")
        return None

async def card_payment(amount_mdl):
    payment = create_paypal_payment(amount_mdl)

    if payment:
        approval_url = next(link["href"] for link in payment["links"] if link["rel"] == "approve")
        return f"Перейдите по ссылке для оплаты: {approval_url}", payment["id"]
    else:
        return "Ошибка создания платежа. Пожалуйста, попробуйте еще раз.", None

# Выбор способа пополнения
@dp.callback_query_handler(text="user_refill", state="*")
async def refill_way(call: CallbackQuery, state: FSMContext):
    get_kb = refill_choice_finl()

    if get_kb is not None:
        await call.message.edit_text("<b>💰 Выберите способ пополнения</b>", reply_markup=get_kb)
    else:
        await call.answer("⛔ Пополнение временно недоступно", True)

# Выбор способа пополнения
@dp.callback_query_handler(text_startswith="refill_choice", state="*")
async def refill_way_choice(call: CallbackQuery, state: FSMContext):
    get_way = call.data.split(":")[1]
    await state.update_data(here_pay_way=get_way)

    await state.set_state("here_pay_amount")
    await call.message.edit_text("<b>💰 Введите сумму пополнения</b>")

# Принятие суммы для пополнения средств через PayPal
@dp.message_handler(state="here_pay_amount")
async def refill_get(message: Message, state: FSMContext):
    if message.text.isdigit():
        cache_message = await message.answer("<b>♻ Подождите, платёж генерируется...</b>")
        pay_amount = int(message.text)
        if min_input_mdl <= pay_amount <= 300000:
            get_way = (await state.get_data())['here_pay_way']
            await state.finish()

            if get_way == "paypal":
                get_message, pay_id = await card_payment(pay_amount)
                await cache_message.edit_text(get_message, reply_markup=refill_bill_finl(None, pay_id, get_way))
        else:
            await cache_message.edit_text(f"<b>❌ Неверная сумма пополнения</b>\n"
                                          f"▶ Cумма не должна быть меньше <code>{min_input_mdl} MDL</code> и больше <code>300 000 MDL</code>\n"
                                          f"💰 Введите сумму для пополнения средств")
    else:
        await message.answer("<b>❌ Данные были введены неверно.</b>\n"
                             "💰 Введите сумму для пополнения средств")

# Функция для проверки платежа через PayPal
async def check_paypal_payment(payment_id):
    url = f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{payment_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_paypal_access_token()}",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        order_data = response.json()
        if order_data["status"] == "COMPLETED":
            pay_amount = float(order_data["purchase_units"][0]["amount"]["value"])
            return "COMPLETED", pay_amount
        else:
            return None, None
    else:
        print(f"Error checking PayPal payment: {response.text}")
        return None, None

async def refill_success(call: CallbackQuery, receipt, amount, get_way):
    get_user = get_userx(user_id=call.from_user.id)
    add_refillx(get_user['user_id'], get_user['user_login'], get_user['user_name'], receipt,
                amount, receipt, get_way, get_date(), get_unix())

    update_userx(call.from_user.id,
                 user_balance=get_user['user_balance'] + amount,
                 user_refill=get_user['user_refill'] + amount)

    await call.message.edit_text(f"<b>💰 Вы пополнили баланс на сумму <code>{amount} MDL</code>. Удачи ❤\n"
                                  f"🧾 Чек: <code>#{receipt}</code></b>")
    await send_admins(
        f"👤 Пользователь: <b>@{get_user['user_login']}</b> | <a href='tg://user?id={get_user['user_id']}'>{get_user['user_name']}</a> | <code>{get_user['user_id']}</code>\n"
        f"💰 Сумма пополнения: <code>{amount} MDL</code>\n"
        f"🧾 Чек: <code>#{receipt}</code>"
    )

# Обработка обратного вызова для проверки PayPal
@dp.callback_query_handler(text_startswith="Pay:PayPal")
async def refill_check_paypal(call: CallbackQuery):
    pay_id = call.data.split(":")[2]
    pay_status, pay_amount = await check_paypal_payment(pay_id)

    if pay_status == "COMPLETED":
        get_refill = get_refillx(refill_receipt=pay_id)
        if get_refill is None:
            await refill_success(call, pay_id, pay_amount, "PayPal")
        else:
            await call.answer("❗ Ваше пополнение уже было зачислено.", True)
    else:
            await call.answer("❗ Платёж не был найден.\n"
                              "⌛ Попробуйте чуть позже.", True, cache_time=5)