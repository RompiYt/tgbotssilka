import logging
import asyncio
from os import getenv
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, PreCheckoutQuery, ContentType
from aiogram.utils.keyboard import InlineKeyboardBuilder

load_dotenv()

TOKEN = getenv("BOT_TOKEN")
PRIVATE_LINK = "https://t.me/+e4D7AQ8qlhk5MGY5"
SUPPORT_LINK = "http://t.me/anonaskbot?start=kbhhd3q"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Main Menu
def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💎 Купить подписку", callback_data="buy_subscription"))
    builder.row(InlineKeyboardButton(text="💌 Написать мне", url=SUPPORT_LINK))
    return builder.as_markup()

def get_subscription_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Месяц - 100 звёзд", callback_data="sub_month_stars"))
    builder.row(InlineKeyboardButton(text="Навсегда - 500 звёзд", callback_data="sub_forever_stars"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu"))
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "приветик) здесь ты можешь купить мой приватик и получить ссылку",
        reply_markup=get_main_menu()
    )

@dp.callback_query(F.data == "main_menu")
async def process_main_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "приветик) здесь ты можешь купить мой приватик и получить ссылку",
        reply_markup=get_main_menu()
    )

@dp.callback_query(F.data == "buy_subscription")
async def process_buy_subscription(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Выберите подходящий тариф:",
        reply_markup=get_subscription_menu()
    )

@dp.callback_query(F.data.startswith("sub_"))
async def process_sub_choice(callback: types.CallbackQuery):
    choice = callback.data.split("_")[1:]
    plan = choice[0]
    currency = choice[1]

    prices = {
        "month": 100,
        "forever": 250
    }
    amount = prices[plan]
    title = f"Подписка ({'Месяц' if plan == 'month' else 'Навсегда'})"
    description = (
        f"✨ Доступ к приватному каналу "
        f"на {'месяц' if plan == 'month' else 'неограниченный срок'}.\n\n"
        f"⭐ Нет Telegram Stars?\n"
        f"Инструкция по покупке и пополнению:\n"
        f"https://habr.com/ru/amp/publications/957984/"
    )
        
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=title,
        description=description,
        payload=f"stars_{plan}",
        provider_token="", # Empty for Stars
        currency="XTR",
        prices=[LabeledPrice(label="Звёзды", amount=amount)]
    )
    await callback.answer()

@dp.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    await message.answer(
        f"Оплата прошла успешно! 🎉\nВот твоя ссылка на вход: {PRIVATE_LINK}"
    )

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
