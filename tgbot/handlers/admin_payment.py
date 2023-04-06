# - *- coding: utf- 8 - *-
import asyncio

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from tgbot.keyboards.inline_admin import payment_choice_finl
from tgbot.loader import dp
from tgbot.services.api_qiwi import QiwiAPI
from tgbot.services.api_sqlite import update_paymentx, get_paymentx
from tgbot.utils.misc.bot_filters import IsAdmin


###################################################################################
############################# ВЫБОР СПОСОБА ПОПОЛНЕНИЯ ############################
# Открытие способов пополнения
@dp.message_handler(IsAdmin(), text="🖲 Способы пополнения", state="*")
async def payment_systems(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>🖲 Выберите способ пополнения</b>", reply_markup=payment_choice_finl())


# Включение/выключение самих способов пополнения
@dp.callback_query_handler(IsAdmin(), text_startswith="change_payment:")
async def payment_systems_edit(call: CallbackQuery):
    way_pay = call.data.split(":")[1]
    way_status = call.data.split(":")[2]

#     get_payment = get_paymentx()

