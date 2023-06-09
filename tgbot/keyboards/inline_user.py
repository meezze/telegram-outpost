# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.services.api_sqlite import get_paymentx


# Выбор способов пополнения
def refill_choice_finl():
    keyboard = InlineKeyboardMarkup()

    keyboard.add(InlineKeyboardButton(text="💳 PayPal", callback_data="refill_choice:paypal"))

    return keyboard



# Проверка платежа через PayPal
def refill_bill_finl(send_requests, get_receipt, get_way):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("🌀 Перейти к оплате", url=send_requests)
    ).add(
        InlineKeyboardButton("🔄 Проверить оплату", callback_data=f"Pay:{get_way}:{get_receipt}")
    )

    return keyboard


# Кнопки при открытии самого товара
def products_open_finl(position_id, remover, category_id):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("💰 Купить товар", callback_data=f"buy_item_select:{position_id}")
    ).add(
        InlineKeyboardButton("⬅ Вернуться ↩", callback_data=f"buy_position_return:{remover}:{category_id}")
    )

    return keyboard


# Подтверждение покупки товара
def products_confirm_finl(position_id, get_count):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("✅ Подтвердить", callback_data=f"xbuy_item:yes:{position_id}:{get_count}"),
        InlineKeyboardButton("❌ Отменить", callback_data=f"xbuy_item:not:{position_id}:{get_count}")
    )

    return keyboard


# Ссылка на поддержку
def user_support_finl(user_name):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("💌 Написать в поддержку", url=f"https://t.me/{user_name}"),
    )

    return keyboard
