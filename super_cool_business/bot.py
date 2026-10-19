import asyncio
import json
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

# 1. Вставьте сюда токен вашего бота от @BotFather
BOT_TOKEN = "8710309080:AAHPQUP1aS6GLCrImRSLxHHLq--pfq58ATs"

# 2. Вставьте сюда HTTPS-ссылку на ваш index.html (например, с GitHub Pages)
WEBAPP_URL = "https://ВАШ_ЛОГИН.github.io/teleshop/"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Создаем кнопку в нижней клавиатуре (ReplyKeyboard), которая открывает WebApp
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🛍 Открыть магазин (WebApp)",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ],
            [
                KeyboardButton(text="🚀 Создать свой магазин (Тарифы)"),
                KeyboardButton(text="ℹ️ О платформе TeleShop")
            ]
        ],
        resize_keyboard=True
    )

    await message.answer(
        f"Привет, <b>{message.from_user.first_name}</b>! 👋\n\n"
        "Добро пожаловать в демонстрационный бот платформы <b>«TeleShop Builder»</b>.\n\n"
        "👇 Нажмите на кнопку <b>«🛍 Открыть магазин (WebApp)»</b> внизу экрана, чтобы:\n"
        "1️⃣ Протестировать витрину глазами покупателя и оформить заказ.\n"
        "2️⃣ Переключиться во вкладку <b>«⚙️ Конструктор»</b> и добавить свой товар за 10 секунд!",
        parse_mode="HTML",
        reply_markup=kb
    )


@dp.message(F.text == "🚀 Создать свой магазин (Тарифы)")
async def show_tariffs(message: types.Message):
    text = (
        "💼 <b>Тарифы конструктора «TeleShop Builder»:</b>\n\n"
        "🟢 <b>Тариф «Старт» — 0 ₽/мес</b>\n"
        "• До 10 товаров в каталоге\n"
        "• Прием заказов в Telegram\n\n"
        "🔵 <b>Тариф «Бизнес» — 1 990 ₽/мес</b>\n"
        "• До 1 000 товаров + импорт из Excel\n"
        "• Онлайн-оплата (СБП, ЮKassa) и доставка СДЭК\n"
        "• Триггерные рассылки по базе\n\n"
        "🟣 <b>Тариф «PRO» — 3 490 ₽/мес</b>\n"
        "• Безлимит товаров + синхронизация с МойСклад и 1С\n"
        "• Реферальная программа и кастомный дизайн"
    )
    await message.answer(text, parse_mode="HTML")


@dp.message(F.text == "ℹ️ О платформе TeleShop")
async def about_platform(message: types.Message):
    await message.answer(
        "<b>TeleShop Builder</b> — это No-Code платформа для запуска интернет-магазина "
        "внутри Telegram за 15 минут без программистов и комиссий маркетплейсов.\n\n"
        "Разработано командой проекта ДГТУ (5 человек).",
        parse_mode="HTML"
    )


# Обработчик данных заказа, пришедших из окна WebApp
@dp.message(F.web_app_data)
async def handle_webapp_order(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
    except Exception:
        await message.answer("Ошибка при чтении данных заказа.")
        return

    store_name = data.get("store", "Магазин")
    items = data.get("items", [])
    total = data.get("total", 0)
    phone = data.get("phone", "Не указан")
    delivery = data.get("delivery", "Не выбрана")
    address = data.get("address", "Не указан")

    # Формируем список позиций чека
    items_text = ""
    for idx, item in enumerate(items, 1):
        line_sum = item["price"] * item["qty"]
        items_text += f"{idx}. {item['name']} — {item['qty']} шт. × {item['price']} ₽ = <b>{line_sum} ₽</b>\n"

    receipt = (
        f"✅ <b>Новый заказ в магазине «{store_name}»!</b>\n"
        f"🧾 Номер заказа: <code>#TS-{message.message_id}</code>\n"
        f"👤 Покупатель: @{message.from_user.username or message.from_user.first_name}\n"
        f"📞 Телефон: <code>{phone}</code>\n"
        f"🚚 Доставка: {delivery}\n"
        f"📍 Адрес: {address}\n\n"
        f"🛒 <b>Состав заказа:</b>\n{items_text}\n"
        f"💳 <b>ИТОГО К ОПЛАТЕ: {total} ₽</b>\n\n"
        f"<i>Статус: Ожидает онлайн-оплаты (СБП / ЮKassa)</i>"
    )

    # Кнопка имитации быстрой оплаты СБП для презентации
    pay_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"💠 Оплатить {total} ₽ через СБП", callback_data=f"pay_{total}")]
        ]
    )

    await message.answer(receipt, parse_mode="HTML", reply_markup=pay_kb)


@dp.callback_query(F.data.startswith("pay_"))
async def simulate_payment(callback: types.CallbackQuery):
    amount = callback.data.split("_")[1]
    await callback.message.edit_text(
        callback.message.html_text + f"\n\n🟢 <b>ОПЛАЧЕНО ({amount} ₽ через СБП). Заказ передан в сборку!</b>",
        parse_mode="HTML"
    )
    await callback.answer("Оплата прошла успешно!", show_alert=True)


async def main():
    print("Бот TeleShop Builder успешно запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())